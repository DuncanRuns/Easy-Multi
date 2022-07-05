# Object oriented abstraction layer on top of win_util

from typing import List
import hwnd_util, win32con


class Window:
    def __init__(self, hwnd):
        self._hwnd: int = hwnd
        self._pid: int = hwnd_util.get_pid_from_hwnd(hwnd)
        self._dir: str = 0
        self._original_title: str = hwnd_util.get_hwnd_title(self._hwnd)

    def get_original_title(self) -> str:
        return self._original_title

    def revert_title(self) -> None:
        self.set_title(self._original_title)

    def set_title(self, title: str) -> None:
        hwnd_util.set_hwnd_title(self._hwnd, title)

    def get_title(self) -> str:
        return hwnd_util.get_hwnd_title(self._hwnd)

    def activate(self) -> None:
        hwnd_util.activate_hwnd(self._hwnd)

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

    def restore_window(self, offset=0):
        hwnd_util.undo_hwnd_borderless(self._hwnd, offset)

    def get_hwnd(self) -> int:
        return self._hwnd

    def get_mc_dir(self) -> str:
        if self._dir != 0:
            return self._dir
        self._dir = hwnd_util.get_mc_dir(self._pid)
        return self._dir

    def remote_reset_keys(self) -> None:
        """
        Runs esc, shift-tab, enter twice on the window.
        """
        hwnd_util.send_key_to_hwnd(self._hwnd, win32con.VK_ESCAPE)
        hwnd_util.send_keydown_to_hwnd(self._hwnd, win32con.VK_LSHIFT)
        hwnd_util.send_key_to_hwnd(self._hwnd, win32con.VK_TAB)
        hwnd_util.send_keyup_to_hwnd(self._hwnd, win32con.VK_LSHIFT)
        hwnd_util.send_key_to_hwnd(self._hwnd, win32con.VK_RETURN, 0)

    def remote_f3_esc(self) -> None:
        """
        Runs f3+esc on the window.
        """
        hwnd_util.autoit_send_to_hwnd(self._hwnd, "{F3 down}{ESC}{F3 up}")
        hwnd_util.send_keydown_to_hwnd(self._hwnd, win32con.VK_F3)
        hwnd_util.send_keyup_to_hwnd(self._hwnd, win32con.VK_F3)

    def exists(self) -> bool:
        return hwnd_util.get_hwnd_exists(self._hwnd)

    def __eq__(self, __o: object) -> bool:
        return self._hwnd == __o.get_hwnd()


def get_all_mc_windows(old_windows=[]) -> List[Window]:
    hwnds = hwnd_util.get_all_mc_hwnds([i.get_hwnd() for i in old_windows])
    windows = []
    for hwnd in hwnds:
        window = Window(hwnd)
        windows.append(window)
    return windows


def get_current_window() -> Window:
    return Window(hwnd_util.get_current_hwnd())


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")
