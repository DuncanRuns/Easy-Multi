from genericpath import isfile
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
        self._num = None

        self._pause_on_load: bool = False

        self._loaded_preview: bool = True
        self._loaded_world: bool = True

        self._next_state_check = 0
        self._last_world_clear = 0

        self._time_of_last_activity = 0

        self._create_world_key = None
        self._leave_preview_key = None
        self._mc_version = None

        # 0 = no atum, 1 = old atum (use leave preview), 2 = modern atum (create world key)
        self._atum_level = 2

        self._tick_lock = threading.Lock()
        self._reset_lock = threading.Lock()
        self._log_lock = threading.Lock()
        self._clear_lock = threading.Lock()

        if self in _mc_instance_cache:
            self._log_progress = _mc_instance_cache[_mc_instance_cache.index(
                self)]._log_progress
        else:
            self.jump_log_progress()

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
            if self._name == "Roaming":
                self._name = ".minecraft"

        return self._name

    def is_world_loaded(self) -> bool:
        return self._loaded_world

    def _get_create_world_key(self) -> Union[int, None]:
        if self._create_world_key:
            return self._create_world_key
        self._create_world_key = self._get_key("key_Create New World")
        return self._create_world_key

    def _get_leave_preview_key(self) -> Union[int, None]:
        if self._leave_preview_key:
            return self._leave_preview_key
        self._leave_preview_key = self._get_key("key_Leave Preview")
        return self._leave_preview_key

    def wait_for_all_activity(self) -> None:
        locks = (self._log_lock, self._tick_lock,
                 self._clear_lock, self._reset_lock)

        still_locked = True
        while still_locked:
            time.sleep(0.1)
            still_locked = False
            for lock in locks:
                if lock.locked():
                    still_locked = True
                    break

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

    def reset(self, is_full: bool = False, single_instance: bool = False):
        # is_full does not reference fullscreen, it means "full reset" which considers more things.
        # A non-full reset just sends the reset key and resets plans.
        func = self._full_reset if is_full else self._send_reset
        threading.Thread(target=func, args=(single_instance,)).start()

    def _full_reset(self, single_instance: bool = False) -> None:
        with self._reset_lock:

            if not self.has_window(True):
                self.log("No window opened yet...")
                return

        self._send_reset(single_instance)

    def _send_reset(self, single_instance: bool = False) -> None:
        with self._reset_lock:
            self.log("Resetting...")
            mc_version = self._window.get_mc_version()
            if mc_version[1] < 14:
                self._window.press_reset_keys()
            else:
                if self._atum_level >= 2 and self._get_create_world_key() is not None:
                    self._window.press_key(self._get_create_world_key())
                else:
                    if self._atum_level >= 1 and self._get_leave_preview_key():
                        self._atum_level = 1
                        if not self._loaded_world and self._loaded_preview:
                            self._window.press_key(
                                self._get_leave_preview_key())
                        else:
                            self._window.press_reset_keys()
                    else:
                        self._atum_level = 0

            self._pause_on_load = self._options["pause_on_load"] and not single_instance

            self._loaded_preview = mc_version[1] < 14
            self._loaded_world = False
            time.sleep(0.1)
            self.jump_log_progress()

    def activate(self) -> None:
        with self._reset_lock:
            self.ensure_window_state()

            if self._window is not None and self._window.exists():
                self._window.activate()

            if self._loaded_world:

                # Magic Number :((( Without this, the mouse does not get locked into MC
                time.sleep(0.05)

                self._window.press_esc()
            self._pause_on_load = False

            self.log("Activated")

    def ensure_window_state(self) -> None:
        if self.has_window():
            # Ensure not minimized
            if self._window.is_minimized():
                self.log("Unminimizing...")
                self._window.show()
                time.sleep(0.1)

            # Ensure borderless
            if self._options["use_borderless"] and not self._window.is_borderless():
                self._window.show()
                time.sleep(0.05)
                self._window.go_borderless()
                self._window.move(
                    self._options["screen_location"], self._options["screen_size"])
                time.sleep(0.1)

            # Ensure not borderless
            if not self._options["use_borderless"] and self._window.is_borderless():
                self._window.restore_window()
                self._window.show()

        self._next_state_check = time.time() + 0.5
        if not self.has_window(True):
            self._next_state_check += 2

    def tick(self, is_active: bool = True) -> None:
        if self._tick_lock.locked():
            # Cancel tick if already being run
            return

        with self._tick_lock:
            try:
                if time.time() > self._next_state_check:
                    self.ensure_window_state()
                if self.has_window(True):
                    if self._options["auto_clear_worlds"] and abs(time.time() - self._last_world_clear) > 20:
                        self._last_world_clear = time.time()
                        threading.Thread(target=self.clear_worlds).start()
                    # Log Reader
                    if (not self._loaded_preview) or (not self._loaded_world):
                        self._time_of_last_activity = time.time()
                    if abs(time.time() - self._time_of_last_activity) < 2:
                        self._process_logs(is_active)
            except:
                print("Error during tick, probably a window missing.")

    def _process_logs(self, is_active: bool = True) -> None:
        new_log_lines = self.get_next_log_lines()
        for line in new_log_lines:
            if _match_view_start(line):
                self._loaded_preview = True
                self._loaded_world = False
                if self._options["use_f3"]:
                    self._window.press_f3_esc()
                break
            elif not self._loaded_world and _match_world_load(line):
                self._loaded_world = True
                if self._pause_on_load:
                    if self._options["use_f3"]:
                        self._window.press_f3_esc()
                    else:
                        self._window.press_esc()
                break

    def get_next_log_lines(self) -> List[str]:
        with self._log_lock:
            line_list = []
            if os.path.isfile(self.get_log_path()):
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

    def jump_log_progress(self) -> None:
        with self._log_lock:
            if os.path.isfile(self.get_log_path()):
                with open(self.get_log_path(), "rb") as f:
                    self._log_progress = len(f.read())
            else:
                self._log_progress = 0

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
            if self._window is None or not self._window.exists():
                self._window = get_window_by_dir(self._game_dir)
                if self._num and self._window:
                    self.log("Window found, title set")
                    self._window.set_title(str(self._num))
                self._log_progress = 0
        return self._window is not None

    def update_num(self, num: int) -> bool:
        self._num = num

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


_mc_match = re.compile(
    r"^Minecraft\*? 1\.[1-9]\d*(\.[1-9]\d*)?( .*)?$").match


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
        if instance.has_window():
            if _mc_match(instance.get_window().get_original_title()):
                return instance


def get_instance_from_dir(game_dir: str) -> EMMinecraftInstance:
    with _retreive_lock:
        instance = EMMinecraftInstance(game_dir=game_dir)
        if instance in _mc_instance_cache:
            instance = _mc_instance_cache[_mc_instance_cache.index(instance)]
        else:
            _mc_instance_cache.append(instance)
        return instance


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")
