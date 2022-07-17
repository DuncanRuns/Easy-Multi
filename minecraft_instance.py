import os, re, input_util, clear_util, threading, time
from logger import Logger, PrintLogger
from window import Window, get_all_mc_windows, get_current_window, get_window_by_dir
from typing import Tuple, Union, List
from easy_multi_options import get_options_instance

_match_view_start = re.compile(
    r"^\[\d\d:\d\d:\d\d\] \[Render thread\/INFO\]: Starting Preview at \(-?\d+.5, \d+.0, -?\d+.5\)$").match
_match_world_load = re.compile(
    r"^\[\d\d:\d\d:\d\d] \[Server thread\/INFO\]: Saving chunks for level .+$").match

_retreive_lock = threading.Lock()


class EMMinecraftInstance:
    def __init__(self, game_dir: str = None, window: Window = None, logger: Logger = None) -> None:
        self._window: Window
        self._game_dir: str

        self._options = get_options_instance()

        if game_dir:
            self._game_dir = game_dir
            self._window = window if window else get_window_by_dir(game_dir)
        elif window:
            self._window = window
            self._game_dir = window.get_mc_dir()
        else:
            raise  # NO GAME DIRECTORY OR WINDOW GIVEN

        if not logger:
            logger = PrintLogger()
        self._logger = logger

        self._name = None

        self._pause_on_wp: bool = False
        self._pause_on_load: bool = False
        self._use_f3: bool = False

        self._loaded_preview: bool = True
        self._loaded_world: bool = True

        self._create_world_key = None
        self._fullscreen_key = None
        self._mc_version = None

        self._tick_lock = threading.Lock()
        self._reset_lock = threading.Lock()
        self._log_lock = threading.Lock()
        self._clear_lock = threading.Lock()

        if self in _mc_instance_cache:
            self._log_progress = _mc_instance_cache[_mc_instance_cache.index(
                self)]._log_progress
        else:
            with open(self.get_log_path(), "rb") as f:
                self._log_progress = len(f.read())

    def log(self, line: str) -> None:
        self._logger.log(line, self.get_name())

    def set_logger(self, logger: Logger) -> None:
        self._logger = logger

    def get_name(self) -> str:
        self._name = os.path.split(self._game_dir)[
            1].replace("\\", "/").strip("/")

        if self._name == ".minecraft":
            self._name = os.path.split(os.path.split(self._game_dir)[0])[
                1].replace("\\", "/").strip("/")

        return self._name

    def is_world_loaded(self) -> bool:
        return self._loaded_world

    def _get_create_world_key(self) -> Union[int, None]:
        if self._create_world_key:
            return self._create_world_key
        self._create_world_key = self._get_key("key_Create New World")
        return self._create_world_key

    def _get_fullscreen_key(self) -> Union[int, None]:
        if self._fullscreen_key:
            return self._fullscreen_key
        self._fullscreen_key = self._get_key("key_key.fullscreen")
        if not self._fullscreen_key:
            return 0x7A
        return self._fullscreen_key

    def _get_key(self, key: str) -> Union[int, None]:
        options_path = os.path.join(self._game_dir, "options.txt")
        try:
            with open(options_path) as f:
                for line in f:
                    args = line.split(":")
                    if args[0] == key:
                        return input_util.get_vk_from_minecraft(
                            args[1].rstrip())
        except:
            pass

    def _get_mc_version(self) -> Union[Tuple[int, int, int], None]:
        if self._mc_version:
            return self._mc_version
        self._mc_version = self._window.get_mc_version()
        return self._mc_version

    def reset(self, pause_on_load: bool = True, use_f3: bool = True, clear_worlds: bool = True, single_instance: bool = False) -> None:
        with self._reset_lock:
            self.log("Resetting...")
            self.get_next_log_lines()
            if self._window is None or not self._window.exists():
                self.log("No window opened yet...")
                return

            if self._window.is_fullscreen():
                self._window.press_key(self._get_fullscreen_key())

            if self._get_mc_version()[1] < 14:
                self._window.press_reset_keys()
            else:
                if self._get_create_world_key() is not None:
                    self._window.press_key(self._get_create_world_key())
                else:
                    self.log("!!! No create world key is set!!!")

            self._pause_on_load = pause_on_load and not single_instance
            self._use_f3 = use_f3
            self._use_fullscreen = False

            self._loaded_preview = self._get_mc_version()[1] < 14
            self._loaded_world = False

            if clear_worlds:
                threading.Thread(target=self.clear_worlds).start()

    def activate(self, use_fullscreen: bool = False) -> None:
        with self._reset_lock:
            self._use_fullscreen = use_fullscreen

            if self._window is not None and self._window.exists():
                self._window.show()
                self._window.activate()

            if self._pause_on_load and self._loaded_world:
                if use_fullscreen:
                    self._window.press_key(self._get_fullscreen_key())

                # Magic Number :((( Without this, the mouse does not get locked into MC
                time.sleep(0.05)

                self._window.press_esc()
            self._pause_on_load = False

            self.log("Activated")

    def tick(self, window_pos=(0, 0), window_size=(1920, 1080), is_active: bool = True) -> None:
        if self._tick_lock.locked():
            # Cancel tick if already being ran
            return

        with self._tick_lock:
            if self.has_window():

                if self._window.is_minimized():
                    self.log("Unminimizing..")
                    self._window.show()
                    if self._window.is_fullscreen():
                        self._window.press_key(self._get_fullscreen_key())

                # Ensure borderless
                if not self._window.is_borderless():
                    self._window.show()
                    time.sleep(0.05)
                    self._window.go_borderless()
                    self._window.move(window_pos, window_size)

                # Log Reader
                if (not self._loaded_preview) or (not self._loaded_world):
                    self._process_plans(is_active)

    def _process_plans(self, is_active: bool = True) -> None:
        new_log_lines = self.get_next_log_lines()
        if not self._loaded_preview:
            for line in new_log_lines:
                if _match_view_start(line):
                    self._loaded_preview = True
                    self._loaded_world = False
                    if self._use_f3:
                        self._window.press_f3_esc()
                    break
        if not self._loaded_world:
            for line in new_log_lines:
                if _match_world_load(line):
                    self._loaded_world = True
                    if self._pause_on_load:
                        if self._use_f3:
                            self._window.press_f3_esc()
                        else:
                            self._window.press_esc()
                    if is_active and (not self._window.is_fullscreen()) and self._use_fullscreen:
                        self._window.press_key(self._get_fullscreen_key())
                    break

    def get_next_log_lines(self) -> List[str]:
        with self._log_lock:
            line_list = []
            with open(self.get_log_path(), "rb") as f:
                f.seek(self._log_progress, 0)
                f_rbytes = f.read()
                self._log_progress += len(f_rbytes)
            f_text = f_rbytes.decode()
            for line in f_text.splitlines():
                line_list.append(line.rstrip())
            while "" in line_list:
                line_list.remove("")
            return line_list

    def get_log_path(self) -> str:
        return os.path.join(self._game_dir, "logs", "latest.log")

    def get_game_dir(self) -> str:
        return self._game_dir

    def clear_worlds(self) -> int:
        with self._clear_lock:
            try:
                i = clear_util.delete_all_in_minecraft(self._game_dir, 6)
            except:
                i = -1
        return i

    def get_window(self) -> Union[Window, None]:
        return self._window

    def has_window(self, no_update: bool = False) -> bool:
        if not no_update:
            if self._window is None:
                self._window = get_window_by_dir(self._game_dir)
                self._log_progress = 0
            elif not self._window.exists():
                self._window = None
        return self._window is not None

    def __eq__(self, __o: object) -> bool:
        return type(self) == type(__o) and self._game_dir == __o._game_dir


_mc_instance_cache: List[EMMinecraftInstance] = []


def _get_instance_total(instance: EMMinecraftInstance):
    total = 0
    nums = [str(i) for i in range(10)]
    for c in instance.get_game_dir():
        if c in nums:
            total += 11
            total += int(c)
    return total


def sort_instances_list(instances: List[EMMinecraftInstance]) -> None:
    instances.sort(key=_get_instance_total)


def get_all_mc_instances() -> List[EMMinecraftInstance]:
    with _retreive_lock:
        global _mc_instance_cache
        windows = get_all_mc_windows()
        instances = []
        for window in windows:
            instance = EMMinecraftInstance(window.get_mc_dir(), window)
            if instance in _mc_instance_cache:
                instance = _mc_instance_cache[
                    _mc_instance_cache.index(instance)]
            instances.append(instance)
        sort_instances_list(instances)
        _mc_instance_cache = instances.copy()
        return instances


def get_current_mc_instance() -> Union[EMMinecraftInstance, None]:
    with _retreive_lock:
        global _mc_instance_cache
        try:
            window = get_current_window()
            if window.is_minecraft():
                instance = EMMinecraftInstance(window=window)
            else:
                return None
        except:
            return None
        if instance in _mc_instance_cache:
            instance = _mc_instance_cache[_mc_instance_cache.index(instance)]
        else:
            _mc_instance_cache.append(instance)
    mc_match = re.compile(
        r"^Minecraft\*? 1\.[1-9]\d*(\.[1-9]\d*)?( .*)?$").match
    if mc_match(instance.get_window().get_original_title()):
        return instance


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")
