# Abstraction layer on top of win32gui and win32process

import re, win32con, win32process, subprocess, win32gui, os
from typing import List, Union
from win32com import client

shell = client.Dispatch("WScript.Shell")

# Borderless method thanks to Mr-Technician
# https://github.com/Mr-Technician/BorderlessMinecraft/blob/master/BorderlessMinecraft/DLLInterop.cs

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
    return win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)


def set_hwnd_style(hwnd: int, style: int) -> None:
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)


def restore_hwnd(hwnd: int) -> None:
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)


def set_hwnd_borderless(hwnd: int, window_size=(1920, 1080)) -> None:
    restore_hwnd(hwnd)
    style = get_hwnd_style(hwnd)
    style &= ~(win32con.WS_BORDER | win32con.WS_DLGFRAME | win32con.WS_THICKFRAME |
               win32con.WS_MINIMIZEBOX | win32con.WS_MAXIMIZEBOX | win32con.WS_SYSMENU)
    set_hwnd_style(hwnd, style)
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 0, 0,
                          window_size[0], window_size[1], win32con.SWP_SHOWWINDOW)


def is_hwnd_borderless(hwnd: int) -> bool:
    old_style = get_hwnd_style(hwnd)
    new_style = old_style
    new_style &= ~(win32con.WS_BORDER | win32con.WS_DLGFRAME | win32con.WS_THICKFRAME |
                   win32con.WS_MINIMIZEBOX | win32con.WS_MAXIMIZEBOX | win32con.WS_SYSMENU)
    return new_style == old_style


def undo_hwnd_borderless(hwnd, offset=0) -> None:
    restore_hwnd(hwnd)
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
