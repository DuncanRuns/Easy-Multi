# Abstraction layer on top of win32gui

from win32 import win32gui
import re
import win32con

import win32com.client
shell = win32com.client.Dispatch("WScript.Shell")

# Constants and borderless method thanks to Mr-Technician
# https://github.com/Mr-Technician/BorderlessMinecraft/blob/master/BorderlessMinecraft/DLLInterop.cs

SW_RESTORE = 0x09  # const for restoreWindow
SW_MINIMIZE = 0x06

# sets the necessary constants for setBorderless
GWL_STYLE = -16
WS_BORDER = 0x00800000
WS_THICKFRAME = 0x00040000
WS_MINIMIZEBOX = 0x00020000
WS_MAXIMIZEBOX = 0x00010000
WS_SYSMENU = 0x00800000
WS_DLGFRAME = 0x00400000

SWP_NOZORDER = 0x0004  # const for setPos


def get_current_hwnd() -> int:
    return win32gui.GetForegroundWindow()


def get_hwnd_title(hwnd: int) -> str:
    return win32gui.GetWindowText(hwnd)


def _win_enum_handler(hwnd: int, hwnd_list: list):
    hwnd_list.insert(0,hwnd)


def get_all_hwnds() -> list:
    hwnd_list = []
    win32gui.EnumWindows(_win_enum_handler, hwnd_list)
    return hwnd_list


def get_all_mc_hwnds(old_hwnds=[]) -> list:
    hwnds = []
    mc_match = re.compile("Minecraft\\*? 1\\.[1-9]\\d*\\.[1-9]\\d*.*").match
    for hwnd in get_all_hwnds():
        if hwnd in old_hwnds or mc_match(get_hwnd_title(hwnd)):
            hwnds.append(hwnd)
    return hwnds

def get_hwnd_exists(hwnd: int) -> bool:
    if win32gui.IsWindow(hwnd):
        return True
    return False

def get_hwnd_style(hwnd: int) -> int:
    return win32gui.GetWindowLong(hwnd, GWL_STYLE)


def set_hwnd_style(hwnd: int, style: int) -> None:
    win32gui.SetWindowLong(hwnd, GWL_STYLE, style)


def restore_hwnd(hwnd: int) -> None:
    win32gui.ShowWindow(hwnd, SW_RESTORE)


def set_hwnd_borderless(hwnd: int, window_size=(1920, 1080)) -> None:
    restore_hwnd(hwnd)
    style = get_hwnd_style(hwnd)
    style &= ~(WS_BORDER | WS_DLGFRAME | WS_THICKFRAME |
               WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU)
    set_hwnd_style(hwnd, style)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0,
                          window_size[0], window_size[1], win32con.SWP_SHOWWINDOW)

def is_hwnd_borderless(hwnd: int) -> bool:
    old_style = get_hwnd_style(hwnd)
    new_style = old_style
    new_style &= ~(WS_BORDER | WS_DLGFRAME | WS_THICKFRAME |
               WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU)
    return new_style == old_style
    


def undo_hwnd_borderless(hwnd, offset=0) -> None:
    restore_hwnd(hwnd)
    set_hwnd_style(hwnd, 382664704)
    move_hwnd(hwnd, 60*offset, 60*offset, 900, 520)


def set_hwnd_title(hwnd: int, text: str) -> None:
    win32gui.SetWindowText(hwnd, text)


def activate_hwnd(hwnd: int) -> None:
    global shell
    shell.SendKeys('%')
    win32gui.ShowWindow(hwnd, 5)
    win32gui.SetForegroundWindow(hwnd)


def move_hwnd(hwnd: int, x: int, y: int, w: int, h: int):
    win32gui.MoveWindow(hwnd, x, y, w, h, False)


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")
