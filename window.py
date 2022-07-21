# Object oriented abstraction layer on top of win_util

import hwnd_util, win32con, threading, time, re
from typing import List, Tuple, Union

_mc_window_cache = []
_retreive_lock = threading.Lock()


class Window:
    def __init__(self, hwnd):
        self._hwnd: int = hwnd
        self._pid: int = hwnd_util.get_pid_from_hwnd(hwnd)
        self._dir: str = None
        self._original_title: str = hwnd_util.get_hwnd_title(self._hwnd)

    def get_original_title(self) -> str:
        mc_match = re.compile(
            r"^Minecraft\*? 1\.[1-9]\d*(\.[1-9]\d*)?( .*)?$").match
        if mc_match(self._original_title):
            return self._original_title
        else:
            new_title = self.get_title()
            if mc_match(new_title):
                self._original_title = new_title
                return new_title
            else:
                return "Minecraft* 1.16.1"

    def revert_title(self) -> None:
        self.set_title(self.get_original_title())

    def is_minecraft(self) -> bool:
        mc_match = re.compile(
            r"^Minecraft\*? 1\.[1-9]\d*(\.[1-9]\d*)?( .*)?$").match
        return mc_match(self.get_original_title())

    def get_mc_version(self) -> Union[Tuple[int, int, int], None]:
        try:
            vstr = self.get_original_title().split()[1]
            v = vstr.split(".")
            if len(v) == 2:
                v.append("0")
            return (int(v[0]), int(v[1]), int(v[2]))
        except:
            return None

    def is_minimized(self) -> bool:
        return hwnd_util.is_hwnd_minimized(self._hwnd)

    def set_title(self, title: str) -> None:
        hwnd_util.set_hwnd_title(self._hwnd, title)

    def get_title(self) -> str:
        return hwnd_util.get_hwnd_title(self._hwnd)

    def activate(self) -> None:
        hwnd_util.activate_hwnd(self._hwnd)

    def show(self) -> None:
        """Like activate but doesn't set to the foreground.
        """
        hwnd_util.show_hwnd(self._hwnd)

    def is_active(self) -> bool:
        return self._hwnd == hwnd_util.get_current_hwnd()

    def tiny(self) -> bool:
        if self.is_borderless():
            hwnd_util.move_hwnd(self._hwnd, 0, 0, 0, 0)
            return True
        return False

    def untiny(self, window_size: List[int]) -> None:
        if self.is_borderless():
            hwnd_util.move_hwnd(
                self._hwnd, 0, 0, window_size[0], window_size[1])

    def is_borderless(self) -> bool:
        return hwnd_util.is_hwnd_borderless(self._hwnd)

    def is_fullscreen(self) -> bool:
        return hwnd_util.is_hwnd_fullscreen(self._hwnd)

    def go_borderless(self) -> None:
        hwnd_util.set_hwnd_borderless(self._hwnd)

    def move(self, pos: List[int], window_size: List[int]) -> None:
        hwnd_util.move_hwnd(self._hwnd, *pos, *window_size)

    def restore_window(self):
        hwnd_util.undo_hwnd_borderless(self._hwnd)

    def get_hwnd(self) -> int:
        return self._hwnd

    def get_mc_dir(self) -> str:
        if self._dir is not None:
            return self._dir
        self._dir = hwnd_util.get_mc_dir(self._pid)
        return self._dir

    def press_f11(self) -> None:
        hwnd_util.send_key_to_hwnd(self._hwnd, win32con.VK_F11)

    def press_reset_keys(self, attempts=2, use_post=True) -> None:
        """
        Runs esc, shift-tab, enter twice on the window.

        press_key(key) with key being equal to Atum's create world key should be used instead.
        """
        v = self.get_mc_version()
        version_major = v[1]
        version_minor = v[2]
        for i in range(attempts):
            hwnd_util.send_key_to_hwnd(
                self._hwnd, win32con.VK_ESCAPE, use_post=use_post)
            if version_major > 12:
                hwnd_util.send_keydown_to_hwnd(
                    self._hwnd, win32con.VK_LSHIFT, use_post=use_post)
                hwnd_util.send_key_to_hwnd(
                    self._hwnd, win32con.VK_TAB, use_post=use_post)
                hwnd_util.send_keyup_to_hwnd(
                    self._hwnd, win32con.VK_LSHIFT, use_post=use_post)
            elif version_major == 8 and version_minor == 9:
                time.sleep(0.07)  # Uh oh magic number
                for i in range(7):  # Run 7 times for anchiale
                    hwnd_util.send_key_to_hwnd(
                        self._hwnd, win32con.VK_TAB, use_post=use_post)
            else:
                time.sleep(0.07)  # Uh oh magic number
                hwnd_util.send_key_to_hwnd(
                    self._hwnd, win32con.VK_TAB, use_post=use_post)
            hwnd_util.send_key_to_hwnd(
                self._hwnd, win32con.VK_RETURN, use_post=use_post)

    def press_esc(self) -> None:
        """
        Runs esc on the window.
        """
        hwnd_util.send_key_to_hwnd(self._hwnd, win32con.VK_ESCAPE)

    def press_f3_esc(self) -> None:
        """
        Runs f3+esc on the window.
        """
        hwnd_util.send_keydown_to_hwnd(self._hwnd, win32con.VK_F3)
        hwnd_util.send_key_to_hwnd(self._hwnd, win32con.VK_ESCAPE)
        hwnd_util.send_keyup_to_hwnd(self._hwnd, win32con.VK_F3)

    def press_key(self, virtual_key: int) -> None:
        hwnd_util.send_key_to_hwnd(self._hwnd, virtual_key)

    def exists(self) -> bool:
        return hwnd_util.get_hwnd_exists(self._hwnd)

    def __eq__(self, __o: object) -> bool:
        return self._hwnd == __o.get_hwnd()


def get_all_mc_windows() -> List[Window]:
    with _retreive_lock:
        global _mc_window_cache
        hwnds = hwnd_util.get_all_mc_hwnds()
        windows = []
        for hwnd in hwnds:
            window = Window(hwnd)
            if window in _mc_window_cache:
                window = _mc_window_cache[_mc_window_cache.index(window)]
            windows.append(window)
        _mc_window_cache = windows.copy()
        return windows


def get_current_window() -> Window:
    with _retreive_lock:
        global _mc_window_cache
        window = Window(hwnd_util.get_current_hwnd())
        if window in _mc_window_cache:
            window = _mc_window_cache[_mc_window_cache.index(window)]
        else:
            _mc_window_cache.append(window)
    return window


def get_window_by_dir(mc_dir: str) -> Union[None, Window]:
    for window in get_all_mc_windows():
        if window.get_mc_dir() == mc_dir:
            return window


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")
