# Abstraction layer on top of win32api and uses some stuff from global_hotkeys

import time
from global_hotkeys.keycodes import vk_key_names
from win32 import win32api

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


def get_similar_modifiers(key_name: str):
    return _MODIFIER_DICT[key_name]


def _get_nm_keys() -> list:
    nm_keys = []
    for name in vk_key_names.keys():
        if name not in MODIFIER_KEYS and name not in BASIC_MODIFIER_KEYS:
            nm_keys.append(name)
    return nm_keys


NM_KEYS = _get_nm_keys()


def is_pressed(ghk_name: str):
    return win32api.GetAsyncKeyState(vk_key_names[ghk_name]) < 0


def read_hotkey(should_continue_call=None) -> list:
    found_key = ""
    while found_key == "" and (should_continue_call is None or should_continue_call()):
        time.sleep(0.01)
        for ghk_name in NM_KEYS:
            if is_pressed(ghk_name):
                keylist = []
                for modifier in MODIFIER_KEYS:
                    if is_pressed(modifier):
                        keylist.append(modifier)
                keylist.append(ghk_name)
                return keylist


def format_hotkey(hotkey: list) -> str:
    string = ""
    for i in hotkey:
        if string != "":
            string += " + "
        string += i.replace("_", " ").title()
    return string


def get_invalid_modifiers(hotkey: list) -> list:
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


def are_any_keys_pressed(key_names: list) -> bool:
    for key_name in key_names:
        if is_pressed(key_name):
            return True
    return False


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")
