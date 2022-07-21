# Abstraction layer on top of win32gui and win32process

import re, win32con, win32process, subprocess, win32api, win32gui, os, time
from typing import List, Union, Tuple
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


def can_int(string: str) -> bool:
    try:
        int(string)
        return True
    except:
        return False


_mc_match = re.compile(
    r"^Minecraft\*? 1\.[1-9]\d*(\.[1-9]\d*)?( .*)?$").match


def get_all_mc_hwnds() -> List[int]:
    hwnds = []
    for hwnd in get_all_hwnds():
        title = get_hwnd_title(hwnd)
        if _mc_match(title) or (can_int(title) and get_mc_dir(get_pid_from_hwnd(hwnd))):
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

# LPARAM STUFF
# https://stackoverflow.com/questions/54638741/how-is-the-lparam-of-postmessage-constructed


def virtual_key_to_scan_code(virtual_key: int) -> Tuple[int, bool]:
    scan_code = win32api.MapVirtualKey(virtual_key, 0)
    is_extended = virtual_key in [win32con.VK_RMENU, win32con.VK_RCONTROL, win32con.VK_LEFT,
                                  win32con.VK_UP, win32con.VK_RIGHT, win32con.VK_DOWN,
                                  win32con.VK_PRIOR, win32con.VK_NEXT, win32con.VK_END,
                                  win32con.VK_HOME, win32con.VK_INSERT, win32con.VK_DELETE,
                                  win32con.VK_DIVIDE, win32con.VK_NUMLOCK]
    return (scan_code, is_extended)


def create_lparam(virtual_key: int, repeat_count: int, transition_state: bool, previous_key_state: bool, context_code: bool) -> int:
    scan_code = virtual_key_to_scan_code(virtual_key)
    return (transition_state << 31) | (previous_key_state << 30) | (context_code << 29) | (scan_code[1] << 24) | (scan_code[0] << 16) | (repeat_count)


def create_lparam_key_down(virtual_key: int, repeat_count: int = 1) -> int:
    return create_lparam(virtual_key, repeat_count, False, repeat_count > 1, False)


def create_lparam_key_up(virtual_key: int) -> int:
    return create_lparam(virtual_key, 1, True, True, False)


def send_keydown_to_hwnd(hwnd: int, virtual_key: int, use_post: bool = True) -> None:
    if use_post:
        win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN,
                             virtual_key, create_lparam_key_down(virtual_key))
    else:
        win32gui.SendMessage(hwnd, win32con.WM_KEYDOWN,
                             virtual_key, create_lparam_key_down(virtual_key))


def send_keyup_to_hwnd(hwnd: int, virtual_key: int, use_post: bool = True) -> None:
    if use_post:
        win32gui.PostMessage(hwnd, win32con.WM_KEYUP,
                             virtual_key, create_lparam_key_up(virtual_key))
    else:
        win32gui.SendMessage(hwnd, win32con.WM_KEYUP,
                             virtual_key, create_lparam_key_up(virtual_key))


def send_key_to_hwnd(hwnd: int, virtual_key: int, press_time: float = 0, use_post: bool = True) -> None:
    send_keydown_to_hwnd(hwnd, virtual_key, use_post)
    if press_time > 0:
        time.sleep(press_time)
    send_keyup_to_hwnd(hwnd, virtual_key, use_post)


def set_hwnd_borderless(hwnd: int) -> None:
    style = get_hwnd_style(hwnd)
    style &= ~(win32con.WS_BORDER | win32con.WS_DLGFRAME | win32con.WS_THICKFRAME |
               win32con.WS_MINIMIZEBOX | win32con.WS_MAXIMIZEBOX | win32con.WS_SYSMENU)
    set_hwnd_style(hwnd, style)
    # win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, pos[0], pos[1],
    #                      window_size[0], window_size[1], win32con.SWP_SHOWWINDOW)


def is_hwnd_borderless(hwnd: int) -> bool:
    old_style = get_hwnd_style(hwnd)
    new_style = old_style
    new_style &= ~(win32con.WS_BORDER | win32con.WS_DLGFRAME | win32con.WS_THICKFRAME |
                   win32con.WS_MINIMIZEBOX | win32con.WS_MAXIMIZEBOX | win32con.WS_SYSMENU)
    return new_style == old_style


def undo_hwnd_borderless(hwnd) -> None:
    set_hwnd_style(hwnd, 382664704)


def show_hwnd(hwnd: int) -> None:
    win32gui.ShowWindow(hwnd, 3)


def set_hwnd_title(hwnd: int, text: str) -> None:
    win32gui.SetWindowText(hwnd, text)


def activate_hwnd(hwnd: int) -> None:
    global shell
    shell.SendKeys('%')
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
    try:
        cmd = f"powershell.exe \"$proc = Get-WmiObject Win32_Process -Filter \\\"ProcessId = {str(pid)}\\\";$proc.CommandLine\""
        p = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        response = p.communicate()[0].decode()
        if "--gameDir" in response:
            ind = response.index("--gameDir") + 10
            return take_arg(response, ind).replace("\\", "/")
        elif "Djava.library.path" in response:
            if '"-Djava.library.path' in response:
                ind = response.index('"-Djava.library.path')
            else:
                ind = response.index('-Djava.library.path')
            natives_path = take_arg(response, ind)[20:].replace("\\", "/")
            return os.path.join(os.path.split(natives_path)[0], ".minecraft").replace("\\", "/")
    except:
        return None


def get_pid_from_hwnd(hwnd: int) -> int:
    return win32process.GetWindowThreadProcessId(hwnd)[1]


def is_hwnd_fullscreen(hwnd: int) -> bool:
    style_long = get_hwnd_style(hwnd)
    # Fullscreen style is around 0xffffffffb6000000 or -1241513984
    # Borderless, Maximized, and Regular window style is around 0x0000000016cf0000 or 382664704
    # Whichever the current style is closer to should give if it is fullscreen or not
    return abs(style_long - FULLSCREEN_STYLE) < abs(style_long - REGULAR_STYLE)


def is_hwnd_minimized(hwnd: int) -> bool:
    return win32gui.IsIconic(hwnd)


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")
