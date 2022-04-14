# Abstraction layer on top of the keyboard module

# NOTE(wurgo): THE PROGRAM MUST BE RUN WITH SUDO TO USE KEYBOARD LIBRARY!!!!!!!!!!!!!!!!!
# NOTE(duncan): Please stop shouting

import keyboard, time, threading
from typing import Callable, Union

MODIFIER_KEYS = ["left ctrl", "right ctrl", "left shift",
                 "right shift", "left menu", "right menu"]
BASIC_MODIFIER_KEYS = ["ctrl", "shift", "alt"]

ALL_SHIFT_KEYS = ["shift", "left shift", "right shift"]
ALL_CONTROL_KEYS = ["ctrl", "left ctrl", "right ctrl"]
ALL_ALT_KEYS = ["alt", "right menu", "left menu"]

_MODIFIER_DICT = {
    "alt": ALL_ALT_KEYS.copy(),
    "control": ALL_CONTROL_KEYS.copy(),
    "shift": ALL_SHIFT_KEYS.copy()
}


# Unsure if numpad works here.
def press_keys_for_time(gh_keys: list, wait_time: int = 0.1):
    # Convert gh module names into keyboard module names for the cases used in easy multi.
    keyboard_keys = [key.lower().replace("numpad_", "num ") for key in gh_keys]
    for key in keyboard_keys:
        keyboard.press(key)
    time.sleep(wait_time)
    for key in keyboard_keys:
        keyboard.release(key)


def get_similar_modifiers(key_name: str):
    return _MODIFIER_DICT[key_name]

# Missing some modifier functions here as they go unused for now


def is_pressed(key: str):
    return keyboard.is_pressed(key)


class KeyReader:
    def __init__(self) -> None:
        self._canceled = False
        self._result = None

    def read_hotkey(self, should_continue_callback: Callable = None) -> str:
        threading.Thread(target=self._read_thread).start()

        should_continue = should_continue_callback is None or should_continue_callback()

        while should_continue and self._result is None:
            time.sleep(0.05)
            should_continue = should_continue_callback is None or should_continue_callback()

        if not should_continue:
            self._canceled = True

        return self._result

    def _read_thread(self) -> None:
        result = keyboard.read_hotkey(suppress=False)
        if not self._canceled:
            self._result = result


# Won't return the same thing as the windows version.
# Will be a list of keyboard module's key names instead of global_hotkeys.
# This shouldn't matter though, as the returned list should only be used on other linux modules.
def read_hotkey(should_continue_callback: Callable = None):
    return KeyReader().read_hotkey(should_continue_callback)


def format_hotkey(hotkey: list) -> str:
    string = ""
    for i in hotkey:
        if string != "":
            string += " + "
        string += i.lower().replace("num", "numpad").replace("_", " ").title()
    return string


# Invalid modifiers gives back modifier keys that should not be pressed for a specified hotkey
# (eg. hotkey = ["u"] will return all modifier keys)
# However for linux, since we are  using the keyboard module, we set no invalid keys.
def get_invalid_modifiers(hotkey: list) -> list:
    return []


def are_any_keys_pressed(keys: list):
    for key in keys:
        if is_pressed(key):
            return True
    return False


def clear_and_stop_hotkey_checker() -> None:
    keyboard.clear_all_hotkeys()


def register_hotkey(hotkey: str, callback: Callable):
    keyboard.add_hotkey(hotkey, callback)


def start_hotkey_checker():
    pass  # keyboard module automatically starts on add_hotkey
