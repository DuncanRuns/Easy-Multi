import os, re, input_util, clear_util, threading
from window import Window, get_all_mc_windows, get_window_by_dir
from typing import Union, List

_match_view_start = re.compile(
    r"^\[\d\d:\d\d:\d\d\] \[Render thread\/INFO\]: Starting Preview at \(-?\d+.5, \d+.0, -?\d+.5\)$").match
_match_world_load = re.compile(
    r"^\[\d\d:\d\d:\d\d] \[Server thread\/INFO\]: Saving chunks for level .+$").match


class MinecraftInstance:
    def __init__(self, game_dir: str = None, window: Window = None) -> None:
        self._window: Window
        self._game_dir: str
        if game_dir:
            self._game_dir = game_dir
            self._window = window
        elif window:
            self._window = window
            self._game_dir = window.get_mc_dir()
        else:
            raise  # NO GAME DIRECTORY OR WINDOW GIVEN

        self._pause_on_wp: bool = False
        self._pause_on_load: bool = False
        self._use_f3: bool = False

        self._loaded_preview: bool = True
        self._loaded_world: bool = True

        self._leave_preview_key = None
        self._leave_preview_key: int = self._get_leave_preview_key()

        self._tick_lock = threading.Lock()
        self._reset_lock = threading.Lock()
        self._log_lock = threading.Lock()
        self._clear_lock = threading.Lock()

        with open(self.get_log_path(), "rb") as f:
            self._log_progress = len(f.read())

    def _get_leave_preview_key(self) -> Union[int, None]:
        if self._leave_preview_key is not None:
            return self._leave_preview_key
        options_path = os.path.join(self._game_dir, "options.txt")
        try:
            with open(options_path) as f:
                for line in f:
                    args = line.split(":")
                    if args[0] == "key_Leave Preview":
                        args = args[1].split(".")
                        self._leave_preview_key = input_util.vk_key_names[
                            args[2].lower().rstrip()]
                        break
            return self._leave_preview_key
        except:
            pass
        return None

    def reset(self, pause_on_load: bool = True, use_f3: bool = True, clear_worlds: bool = True) -> None:
        with self._reset_lock:
            if self._window is None or not self._window.exists():
                print("NO WINDOW AVAILABLE TO RESET")
                return
            if self._window.is_fullscreen():
                self._window.press_f11()
            self.get_next_log_lines()
            if not self._loaded_world:
                if self._get_leave_preview_key() is not None:
                    self._window.press_key(self._get_leave_preview_key())
                else:
                    print("NO PREVIEW KEY SET IN OPTIONS")
            self._window.press_reset_keys()

            self._pause_on_load = pause_on_load
            self._use_f3 = use_f3

            self._loaded_preview = False
            self._loaded_world = False

            if clear_worlds:
                self.clear_worlds()

    def activate(self, use_fullscreen: bool = False) -> None:
        self.cancel_plans()
        if self._window is not None and self._window.exists():
            self._window.activate()
        if use_fullscreen and not self._window.is_fullscreen():
            self._window.press_f11()
        elif not use_fullscreen and self._window.is_fullscreen():
            self._window.press_f11()

    def cancel_plans(self) -> None:
        self._loaded_preview = True
        self._loaded_world = True

    def tick(self) -> None:
        if self._tick_lock.locked():
            # Cancel tick if already being ran
            return
        with self._tick_lock:
            # Window replacer
            if self._window is None:
                self._window = get_window_by_dir(self._game_dir)
                self._log_progress = 0
            elif not self._window.exists():
                self._window = None
            # Log Reader
            elif (not self._loaded_preview) or (self._pause_on_load and not self._loaded_world):
                self._process_log()

    def _process_log(self) -> None:
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

    def get_window(self) -> Window:
        return self._window

    def __eq__(self, __o: object) -> bool:
        return type(self) == type(__o) and self._game_dir == __o._game_dir


def _get_instance_total(instance: MinecraftInstance):
    total = 0
    nums = [i for i in range(10)]
    for c in instance._game_dir:
        if c in nums:
            total += 11
            total += int(c)
    return total


def get_all_mc_instances() -> List[MinecraftInstance]:
    instances = [MinecraftInstance(window=i) for i in get_all_mc_windows()]
    instances.sort(key=_get_instance_total)
    return instances


if __name__ == "__main__":
    import os
    os.system("python test.py")
