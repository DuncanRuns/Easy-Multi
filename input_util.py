# Abstraction layer on top of win32api and uses some stuff from global_hotkeys

import time, global_hotkeys, ctypes, win32api, mc_input_constants
from typing import Callable, List, Union
from global_hotkeys.keycodes import vk_key_names

_user32 = ctypes.WinDLL('user32', use_last_error=True)

MODIFIER_KEYS = ["left_control", "right_control",
                 "left_shift", "right_shift", "left_menu", "right_menu"]
BASIC_MODIFIER_KEYS = ["control", "shift", "alt"]

ALL_SHIFT_KEYS = ["shift", "left_shift", "right_shift"]
ALL_CONTROL_KEYS = ["control", "left_control", "right_control"]
ALL_ALT_KEYS = ["alt", "right_menu", "left_menu"]

_MODIFIER_DICT = {
    "alt": ALL_ALT_KEYS.copy(),
    "control": ALL_CONTROL_KEYS.copy(),
    "shift": ALL_SHIFT_KEYS.copy()
}


# Keyboard module apparently doesn't do so well with numpad stuff, so this is useful for that.
def press_keys_for_time(gh_keys: List[str], wait_time: int = 0.1):
    global _user32
    # Press
    for gh_key in gh_keys:
        _user32.keybd_event(vk_key_names[gh_key], 0, 0, 0)
    # Wait
    time.sleep(wait_time)
    # Release
    for gh_key in gh_keys:
        _user32.keybd_event(vk_key_names[gh_key], 0, 2, 0)


def get_similar_modifiers(key_name: str):
    return _MODIFIER_DICT[key_name]


def _get_nm_keys() -> List[str]:
    nm_keys = []
    for name in vk_key_names.keys():
        if name not in MODIFIER_KEYS and name not in BASIC_MODIFIER_KEYS:
            nm_keys.append(name)
    return nm_keys


NM_KEYS = _get_nm_keys()


def is_pressed(ghk_name: str):
    return win32api.GetAsyncKeyState(vk_key_names[ghk_name]) < 0


def read_hotkey(should_continue_callback: Callable = None) -> List[str]:
    found_key = ""
    while found_key == "" and (should_continue_callback is None or should_continue_callback()):
        time.sleep(0.01)
        for ghk_name in NM_KEYS:
            if is_pressed(ghk_name):
                keylist = []
                for modifier in MODIFIER_KEYS:
                    if is_pressed(modifier):
                        keylist.append(modifier)
                keylist.append(ghk_name)
                return keylist


def format_hotkey(hotkey: List[str]) -> str:
    string = ""
    for i in hotkey:
        if string != "":
            string += " + "
        string += i.replace("_", " ").title()
    return string


def get_invalid_modifiers(hotkey: List[str]) -> List[str]:
    invalid_modifiers = MODIFIER_KEYS.copy()
    for modifier in BASIC_MODIFIER_KEYS:
        if modifier in hotkey:
            for to_remove in get_similar_modifiers(modifier):
                invalid_modifiers.remove(to_remove)
    for modifier in MODIFIER_KEYS:
        if modifier in hotkey:
            if modifier in invalid_modifiers:
                invalid_modifiers.remove(modifier)
    return invalid_modifiers


def are_any_keys_pressed(key_names: List[str]) -> bool:
    for key_name in key_names:
        if is_pressed(key_name):
            return True
    return False


def get_vk_from_minecraft(minecraft_key: str) -> Union[None, int]:
    glfw_key = mc_input_constants.TRANSLATIONS_TO_GLFW[minecraft_key]
    vk_key = mc_input_constants.get_vk_from_glfw(glfw_key)
    if vk_key > 0:
        return vk_key
    return None


def clear_and_stop_hotkey_checker() -> None:
    global_hotkeys.stop_checking_hotkeys()
    global_hotkeys.clear_hotkeys()


def register_hotkey(hotkey: List[str], callback) -> None:
    global_hotkeys.register_hotkeys([
        [hotkey, callback, None]
    ])


def start_hotkey_checker() -> None:
    global_hotkeys.start_checking_hotkeys()


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")
