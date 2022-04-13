# NOTE(wurgo): THE PROGRAM MUST BE RUN WITH SUDO TO USE KEYBOARD LIBRARY!!!!!!!!!!!!!!!!!

import keyboard
from typing import Callable, Union

MODIFIER_KEYS = ["left ctrl", "right ctrl", "left shift", "right shift", "left menu", "right menu"]
BASIC_MODIFIER_KEYS = ["ctrl", "shift", "alt"]

ALL_SHIFT_KEYS = ["shift", "left shift", "right shift"]
ALL_CONTROL_KEYS = ["ctrl", "left ctrl", "right ctrl"]
ALL_ALT_KEYS = ["alt", "right menu", "left menu"]

_MODIFIER_DICT = {
    "alt": ALL_ALT_KEYS.copy(),
    "control": ALL_CONTROL_KEYS.copy(),
    "shift": ALL_SHIFT_KEYS.copy()
}

def press_and_release(keys: Union(str, list)):
    if type(keys) == list:
        for key in keys:
            keyboard.press_and_release(key)
        return
    keyboard.press_and_release(keys)

def get_similar_modifiers(key: str):
    return _MODIFIER_DICT[key]

# NOTE(wurgo): Also works for key combinations (ctrl+b)
def is_pressed(key: str):
    return keyboard.is_pressed(key)

def are_any_keys_pressed(keys: list):
    for key in keys:
        if is_pressed(key):
            return True
    return False

def register_hotkey(hotkey: str, callback: Callable):
    keyboard.add_hotkey(hotkey, callback)

def start_hotkey_checker():
    keyboard.wait()
