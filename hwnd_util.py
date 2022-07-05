# Abstraction layer on top of win32gui and win32process

import re, win32con, win32process, subprocess, win32gui, os, autoit
from typing import List, Union
from win32com import client

shell = client.Dispatch("WScript.Shell")

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

# Custom Constants
FULLSCREEN_STYLE = -1241513984
REGULAR_STYLE = 382664704

"""
Tested Style Values

Fullscreen: -1241513984
0xffffffffb6000000

Borderless:  369623040
0x0000000016080000

Regular Window: 382664704
0x0000000016cf0000

Maximized Window: 399441920
0x0000000017cf0000
"""


def get_current_hwnd() -> int:
    return win32gui.GetForegroundWindow()


def get_hwnd_title(hwnd: int) -> str:
    return win32gui.GetWindowText(hwnd)


def _win_enum_handler(hwnd: int, hwnd_list: List[str]) -> None:
    hwnd_list.insert(0, hwnd)


def get_all_hwnds() -> List[int]:
    hwnd_list = []
    win32gui.EnumWindows(_win_enum_handler, hwnd_list)
    return hwnd_list


def get_all_mc_hwnds(old_hwnds=[]) -> List[int]:
    hwnds = []
    mc_match = re.compile(
        r"^Minecraft\*? 1\.[1-9]\d*(\.[1-9]\d*)?( .*)?$").match
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


def autoit_send_to_hwnd(hwnd: int, send_text: str) -> None:
    """
    Use AutoIt to reliably send inputs to a window.
    If sending to a Minecraft window while in a different Minecraft window, it will crash Minecraft.
    Uses an AHK style input text, see more: https://www.autoitscript.com/autoit3/docs/functions/Send.htm

    Args:
        hwnd (int): Window ID to send inputs to.
        send_text (str): AutoIt send text.
    """
    autoit.control_send_by_handle(hwnd, hwnd, send_text)


def set_hwnd_borderless(hwnd: int) -> None:
    style = get_hwnd_style(hwnd)
    style &= ~(WS_BORDER | WS_DLGFRAME | WS_THICKFRAME |
               WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU)
    set_hwnd_style(hwnd, style)
    # win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, pos[0], pos[1],
    #                      window_size[0], window_size[1], win32con.SWP_SHOWWINDOW)


def is_hwnd_borderless(hwnd: int) -> bool:
    old_style = get_hwnd_style(hwnd)
    new_style = old_style
    new_style &= ~(WS_BORDER | WS_DLGFRAME | WS_THICKFRAME |
                   WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU)
    return new_style == old_style


def undo_hwnd_borderless(hwnd, offset=0) -> None:
    set_hwnd_style(hwnd, 382664704)
    move_hwnd(hwnd, 60 * offset, 60 * offset, 900, 520)


def set_hwnd_title(hwnd: int, text: str) -> None:
    win32gui.SetWindowText(hwnd, text)


def activate_hwnd(hwnd: int) -> None:
    global shell
    shell.SendKeys('%')
    win32gui.ShowWindow(hwnd, 5)
    win32gui.SetForegroundWindow(hwnd)


def move_hwnd(hwnd: int, x: int, y: int, w: int, h: int):
    win32gui.MoveWindow(hwnd, x, y, w, h, False)


def take_arg(string: str, ind: int) -> str:
    """Takes a single argument or word from a string.

    Args:
        string (str): utf-8 string containing multiple words.
        ind (int): Starting index of argument.

    Returns:
        str: The argument at the specified `index` of `string`.
    """
    sub = string[ind:]
    if sub == "":
        return ""
    while sub[0] == " ":
        sub = sub[1:]
        if sub == "":
            return ""
    if sub[0] == '"':
        scan_ind = 1
        bsc = 0
        while scan_ind < len(sub):
            if sub[scan_ind] == '\\':
                bsc += 1
            elif sub[scan_ind] == '"':
                if bsc % 2 == 0:
                    break
                else:
                    bsc = 0
            else:
                bsc = 0
            scan_ind += 1
        if scan_ind == len(sub):
            raise  # QUOTATION WAS NOT ENDED
        return sub[1:scan_ind].encode('utf-8').decode('unicode_escape')
    else:
        scan_ind = 1
        while scan_ind < len(sub) and scan_ind:
            if sub[scan_ind] == " ":
                break
            scan_ind += 1
        return sub[:scan_ind]


def get_mc_dir(pid: int) -> Union[str, None]:
    # Thanks to the creator of MoveWorlds-v0.3.ahk (probably specnr)
    cmd = f"powershell.exe \"$proc = Get-WmiObject Win32_Process -Filter \\\"ProcessId = {str(pid)}\\\";$proc.CommandLine\""
    p = subprocess.Popen(
        cmd, stdout=subprocess.PIPE)
    response = p.communicate()[0].decode()
    if "--gameDir" in response:
        ind = response.index("--gameDir") + 10
        return take_arg(response, ind).replace("\\", "/")
    elif "\"-Djava.library.path=" in response:
        ind = response.index("\"-Djava.library.path=")
        natives_path = take_arg(response, ind)[20:].replace("\\", "/")
        return os.path.join(os.path.split(natives_path)[0], ".minecraft").replace("\\", "/")


def get_pid_from_hwnd(hwnd: int) -> int:
    return win32process.GetWindowThreadProcessId(hwnd)[1]


def is_hwnd_fullscreen(hwnd: int) -> bool:
    style_long = get_hwnd_style(hwnd)
    # Fullscreen style is around 0xffffffffb6000000 or -1241513984
    # Borderless, Maximized, and Regular window style is around 0x0000000016cf0000 or 382664704
    # Whichever the current style is closer to should give if it is fullscreen or not
    return abs(style_long - FULLSCREEN_STYLE) < abs(style_long - REGULAR_STYLE)


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")
