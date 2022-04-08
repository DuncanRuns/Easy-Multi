# Object oriented abstraction layer on top of hwnd_util

import hwnd_util


class Window:
    def __init__(self, hwnd):
        self._hwnd = hwnd
        self._original_title = hwnd_util.get_hwnd_title(self._hwnd)

    def revert_title(self) -> None:
        self.set_title(self._original_title)

    def set_title(self, title: str) -> None:
        hwnd_util.set_hwnd_title(self._hwnd, title)

    def get_title(self) -> str:
        return hwnd_util.get_hwnd_title(self._hwnd)

    def activate(self) -> None:
        hwnd_util.activate_hwnd(self._hwnd)

    def tiny(self) -> None:
        if self.is_borderless():
            hwnd_util.move_hwnd(self._hwnd, 0, 0, 0, 0)

    def untiny(self, window_size) -> None:
        if self.is_borderless():
            hwnd_util.move_hwnd(
                self._hwnd, 0, 0, window_size[0], window_size[1])

    def is_borderless(self) -> bool:
        return hwnd_util.is_hwnd_borderless(self._hwnd)

    def go_borderless(self, window_size) -> None:
        hwnd_util.set_hwnd_borderless(self._hwnd, window_size)

    def restore_window(self, offset=0):
        hwnd_util.undo_hwnd_borderless(self._hwnd, offset)

    def get_hwnd(self) -> int:
        return self._hwnd

    def __eq__(self, __o: object) -> bool:
        return self._hwnd == __o.get_hwnd()

    def exists(self) -> bool:
        return hwnd_util.get_hwnd_exists(self._hwnd)


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")


def get_all_mc_windows(old_windows=[]) -> list:
    hwnds = hwnd_util.get_all_mc_hwnds([i.get_hwnd() for i in old_windows])
    windows = []
    for hwnd in hwnds:
        window = Window(hwnd)
        windows.append(window)
    return windows


def get_current_window() -> Window:
    return Window(hwnd_util.get_current_hwnd())
