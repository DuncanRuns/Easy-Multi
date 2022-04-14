# Object oriented abstraction layer on top of win_util

import win_util

SUPPORTS_BORDERLESS = True


class Window:
    def __init__(self, hwnd):
        self._hwnd = hwnd
        self._original_title = win_util.get_hwnd_title(self._hwnd)

    def get_original_title(self) -> str:
        return self._original_title

    def revert_title(self) -> None:
        self.set_title(self._original_title)

    def set_title(self, title: str) -> None:
        win_util.set_hwnd_title(self._hwnd, title)

    def get_title(self) -> str:
        return win_util.get_hwnd_title(self._hwnd)

    def activate(self) -> None:
        win_util.activate_hwnd(self._hwnd)

    def tiny(self) -> bool:
        if self.is_borderless():
            win_util.move_hwnd(self._hwnd, 0, 0, 0, 0)
            return True
        return False

    def untiny(self, window_size) -> None:
        if self.is_borderless():
            win_util.move_hwnd(
                self._hwnd, 0, 0, window_size[0], window_size[1])

    def is_borderless(self) -> bool:
        return win_util.is_hwnd_borderless(self._hwnd)

    def go_borderless(self, window_size) -> None:
        win_util.set_hwnd_borderless(self._hwnd, window_size)

    def restore_window(self, offset=0):
        win_util.undo_hwnd_borderless(self._hwnd, offset)

    def get_hwnd(self) -> int:
        return self._hwnd

    def __eq__(self, __o: object) -> bool:
        return self._hwnd == __o.get_hwnd()

    def exists(self) -> bool:
        return win_util.get_hwnd_exists(self._hwnd)


def get_all_mc_windows(old_windows=[]) -> list:
    hwnds = win_util.get_all_mc_hwnds([i.get_hwnd() for i in old_windows])
    windows = []
    for hwnd in hwnds:
        window = Window(hwnd)
        windows.append(window)
    return windows


def get_current_window() -> Window:
    return Window(win_util.get_current_hwnd())


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")
