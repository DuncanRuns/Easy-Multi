from sys import maxsize
import tkinter as tk
from tkinter import ttk
import os
import json
import keyboard
import time
import traceback
import global_hotkeys
import clipboard
import threading

from window import *
from global_hotkeys.keycodes import vk_key_names
from win32 import win32api

VERSION = "1.0.2"

modifier_keys = ["left_control", "right_control",
                 "left_shift", "right_shift", "left_menu", "right_menu"]


def read_hotkey(should_continue_call=None) -> list:
    found_key = ""
    name_key_list = vk_key_names.items()
    while found_key == "" and (should_continue_call is None or should_continue_call()):
        time.sleep(0.01)
        for name, vk_value in name_key_list:
            if not (name.endswith("control") or name.endswith("alt") or name.endswith("shift") or name.endswith("menu")):
                if win32api.GetAsyncKeyState(vk_value) < 0:
                    keylist = []
                    for modifier in modifier_keys:
                        if win32api.GetAsyncKeyState(vk_key_names[modifier]) < 0:
                            keylist.append(modifier)
                    keylist.append(name)
                    return keylist


def format_hotkey(hotkey: list) -> str:
    string = ""
    for i in hotkey:
        if string != "":
            string += " + "
        string += i.replace("_", " ").title()
    return string


def resource_path(relative_path):
    try:
        from sys import _MEIPASS
        base_path = _MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


DEFAULT_OPTIONS = {
    "reset_hotkey": ["u"],
    "hide_hotkey": ["p"],
    "window_size": [1920, 1080]
}


class IntEntry(tk.Entry):
    def __init__(self, parent, max=maxsize):
        self.max = max
        self.parent = parent
        vcmd = (self.parent.register(self.validateInt),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        tk.Entry.__init__(self, parent, validate='key', validatecommand=vcmd)

    def validateInt(self, action, index, value_if_allowed,
                    prior_value, text, validation_type, trigger_type, widget_name):
        if value_if_allowed == "":
            return True
        if value_if_allowed:
            try:
                if (len(value_if_allowed) > 1 and value_if_allowed[0] == "0") or (int(value_if_allowed) > self.max):
                    return False
                return True
            except ValueError:
                return False
        else:
            return False


class EasyMultiApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # TK Window Stuff
        self.title("Easy Multi v"+VERSION)
        self.resizable(0, 0)
        self.iconbitmap(resource_path("EasyMulti.ico"))
        self.protocol("WM_DELETE_WINDOW", self._exit)

        # App Stuff
        self._windows = []
        self._log_lines = [" " for i in range(20)]
        self._log_var: tk.StringVar = tk.StringVar(
            self, value="")
        self._total_var: tk.StringVar = tk.StringVar(
            self, value="Current Instances: 0")
        self._reset_dis_var: tk.StringVar = tk.StringVar(self, value="")
        self._hide_dis_var: tk.StringVar = tk.StringVar(self, value="")
        self._window_size_dis_var: tk.StringVar = tk.StringVar(self, value="")
        self._changing_something = False
        self._log("Welcome to Easy Multi!\n")
        self._running = False
        self._init_widgets()
        self._options_json = self._load_options_json()
        self._refresh_options()

    def _exit(self, *args) -> None:
        self._abandon_windows()
        self.destroy()

    @staticmethod
    def _load_options_json() -> None:
        try:
            if not os.path.isfile("options.json"):
                return {}
            with open("options.json", "r") as options_file:
                options_json = json.load(options_file)
                options_file.close()
            return options_json
        except:
            return {}

    @staticmethod
    def _save_options_json(options_json: dict) -> None:
        with open("options.json", "w+") as options_file:
            json.dump(options_json, options_file, indent=4)
            options_file.close()

    @staticmethod
    def _get_setting(options_json: dict, key: str):
        return options_json.get(key, DEFAULT_OPTIONS.get(key, None))

    def _refresh_options(self) -> None:
        self._setup_hotkeys()
        self._window_size = self._get_setting(
            self._options_json, "window_size")
        self._window_size_dis_var.set(
            "Window Size:\n"+str(self._window_size[0])+"x"+str(self._window_size[1]))
        self._save_options_json(self._options_json)

    def _setup_hotkeys(self) -> None:
        global_hotkeys.stop_checking_hotkeys()
        global_hotkeys.clear_hotkeys()
        self._reset_hotkey = self._get_setting(
            self._options_json, "reset_hotkey")
        self._hide_hotkey = self._get_setting(
            self._options_json, "hide_hotkey")
        global_hotkeys.register_hotkeys([
            [self._reset_hotkey, self._reset_keypress, None],
            [self._hide_hotkey, self._hide_keypress, None]
        ])
        self._reset_dis_var.set("Reset:\n"+format_hotkey(self._reset_hotkey))
        self._hide_dis_var.set("Hide:\n"+format_hotkey(self._hide_hotkey))
        global_hotkeys.start_checking_hotkeys()

    def _init_widgets(self) -> None:
        buttons_frame = tk.LabelFrame(self)
        buttons_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nes")
        tk.Button(buttons_frame, text="Setup Instances", command=self._setup_button).grid(
            row=0, column=0, padx=5, pady=5, sticky="NESW")
        tk.Button(buttons_frame, text="Go Borderless", command=self._try_borderless_button).grid(
            row=1, column=0, padx=5, pady=5, sticky="NESW")
        tk.Button(buttons_frame, text="Restore Windows", command=self._restore_button).grid(
            row=2, column=0, padx=5, pady=5, sticky="NESW")

        options_frame = tk.LabelFrame(self)
        options_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nes")
        tk.Button(options_frame, textvariable=self._reset_dis_var, command=self._set_reset_button).grid(
            row=0, column=0, padx=5, pady=5, sticky="NESW")
        tk.Button(options_frame, textvariable=self._hide_dis_var, command=self._set_hide_button).grid(
            row=1, column=0, padx=5, pady=5, sticky="NESW")
        tk.Button(options_frame, textvariable=self._window_size_dis_var, command=self._set_window_size_button).grid(
            row=2, column=0, padx=5, pady=5, sticky="NESW")

        log_frame = tk.LabelFrame(self)
        log_frame.grid(row=0, column=1, padx=5, pady=5, rowspan=2)
        tk.Label(log_frame, textvariable=self._log_var, anchor=tk.W,
                 justify=tk.LEFT, width=50).grid(row=0, column=0, padx=5, pady=5, columnspan=3)
        ttk.Separator(log_frame, orient=tk.HORIZONTAL).grid(
            row=1, column=0, columnspan=3, pady=3, sticky="we")
        tk.Label(log_frame, textvariable=self._total_var).grid(
            row=2, column=0, padx=5, pady=5, sticky="w")
        tk.Button(log_frame, text="Copy Log", command=self.log_button).grid(
            row=2, column=2, padx=5, pady=5, sticky="e")

    def _set_reset_button(self, *args) -> None:
        threading.Thread(target=self._set_reset_thread).start()

    def _set_reset_thread(self) -> None:
        if not self._changing_something:
            global_hotkeys.stop_checking_hotkeys()
            self._log("Setting hotkey, press ESC to cancel.")
            self._changing_something = True
            self._reset_dis_var.set("Reset:\n...")
            hotkey = read_hotkey(self._is_app_selected)
            if not (hotkey is None or hotkey[-1] == "escape"):
                self._options_json["reset_hotkey"] = hotkey
            self._refresh_options()
            self._changing_something = False

    def _set_hide_button(self, *args) -> None:
        threading.Thread(target=self._set_hide_thread).start()

    def _set_hide_thread(self) -> None:
        if not self._changing_something:
            global_hotkeys.stop_checking_hotkeys()
            self._log("Setting hotkey, press ESC to cancel.")
            self._changing_something = True
            self._hide_dis_var.set("Hide:\n...")
            hotkey = read_hotkey(self._is_app_selected)
            if not (hotkey is None or hotkey[-1] == "escape"):
                self._options_json["hide_hotkey"] = hotkey
            self._refresh_options()
            self._changing_something = False

    def _set_window_size_button(self, *args) -> None:
        if not self._changing_something:
            self._changing_something = True
            window_size_tl = tk.Toplevel(self)
            window_size_tl.resizable(0, 0)
            window_size_tl.title("Change Instance Window Size")
            window_size_tl.iconbitmap(resource_path("EasyMulti.ico"))

            def exit_wst():
                self._changing_something = False
                window_size_tl.destroy()

            window_size_tl.protocol("WM_DELETE_WINDOW", exit_wst)

            tk.Label(window_size_tl, text="Enter your desired window size for borderless minecraft instances:").grid(
                row=0, column=0, padx=5, pady=5)

            entry_frame = tk.Frame(window_size_tl)
            entry_frame.grid(row=1, column=0, padx=5, pady=5)

            x_entry = IntEntry(entry_frame, 10000)
            x_entry.config(width=4)
            x_entry.insert(0, str(self._window_size[0]))
            x_entry.grid(row=0, column=0)
            tk.Label(entry_frame, text="x").grid(
                row=0, column=1)
            y_entry = IntEntry(entry_frame, 10000)
            y_entry.config(width=4)
            y_entry.insert(0, str(self._window_size[1]))
            y_entry.grid(row=0, column=2)

            def done():
                try:
                    x = int(x_entry.get())
                except:
                    x = 1920
                try:
                    y = int(y_entry.get())
                except:
                    y = 1080
                self._options_json["window_size"] = [x, y]
                self._refresh_options()
                exit_wst()

            tk.Button(window_size_tl, text=" Ok ", command=done).grid(
                row=100, column=0, padx=5, pady=5)
            window_size_tl.focus()

            def tick():
                window_size_tl.after(50, tick)
                if window_size_tl.focus_displayof() is None:
                    exit_wst()
            window_size_tl.after(50, tick)

    def _reset_keypress(self) -> None:
        threading.Thread(target=self._run_macro).start()

    def _hide_keypress(self) -> None:
        current_window = get_current_window()
        if current_window in self._windows:
            for window in self._windows:
                if window != current_window:
                    window.tiny()

    def _validate_windows(self) -> None:
        for window in self._windows:
            window: Window
            if not window.exists():
                self._log("One of your instances has closed!")
                self._abandon_windows()
                break

    def _is_app_selected(self) -> bool:
        try:
            return self.focus_displayof() is not None
        except:
            return False

    def _set_windows(self, windows: list) -> None:
        self._total_var.set("Current Instances: "+str(len(windows)))
        self._windows = windows

    def _abandon_windows(self) -> None:
        if len(self._windows) > 0:
            self._log("Abandoning current instances...")
            for window in self._windows:
                window: Window
                try:
                    int(window.get_title())
                    window.revert_title()
                except:
                    pass
            self._set_windows([])

    def _run_macro(self) -> None:
        try:
            if not self._running:
                self._running = True
                self._validate_windows()
                window_to_reset = get_current_window()
                if window_to_reset in self._windows:
                    if len(self._windows) == 1:
                        self._run_macro_single(window_to_reset)
                    else:
                        self._run_macro_multi(window_to_reset)
                self._running = False
        except:
            self._log("Error during reset: \n" +
                      traceback.format_exc().replace("\n", "\\n"))
            self._running = False

    def _run_macro_single(self, window_to_reset: Window) -> None:
        self._log("Resetting (Single)...")
        keyboard.press_and_release("esc")
        keyboard.press_and_release("shift+tab")
        keyboard.press_and_release("enter")
        window_to_reset.untiny(self._window_size)

    def _run_macro_multi(self, window_to_reset: Window) -> None:
        self._log("Resetting...")
        next_window_index = self._windows.index(
            window_to_reset) + 1
        next_window_index = 0 if next_window_index >= len(
            self._windows) else next_window_index
        next_window: Window = self._windows[next_window_index]
        keyboard.press_and_release("esc")
        keyboard.press_and_release("shift+tab")
        keyboard.press_and_release("enter")
        keyboard.press("alt+"+str(next_window_index+1))
        time.sleep(0.1)
        keyboard.release("alt+"+str(next_window_index+1))
        next_window.untiny(self._window_size)
        next_window.activate()
        time.sleep(0.1)
        keyboard.press_and_release("esc")

    def _log(self, txt: str) -> None:
        for new_line in [i.rstrip() for i in txt.split("\n")]:
            last_line = self._log_lines[-1]
            if new_line == last_line:
                self._log_lines[-1] = new_line + " (x2)"
            elif (" (x" in last_line and new_line == last_line[:last_line.index(" (x")]):
                self._log_lines[-1] = new_line + \
                    " (x" + \
                    str(int(last_line[last_line.index(" (x")+3:-1]) + 1)+")"
            else:
                while len(self._log_lines) >= 15:
                    self._log_lines.pop(0)
                self._log_lines.append(new_line)
        log_txt = ""
        for line in self._log_lines:
            if log_txt != "":
                log_txt += "\n"
            log_txt += line
        self._log_var.set(log_txt)

    def _setup_button(self) -> None:
        self._log("Running setup...")
        try:
            self._abandon_windows()
            windows = get_all_mc_windows()
            if len(windows) <= 0:
                self._log(
                    "Found no Minecraft instances open.")
            else:
                self._set_windows(windows)
                self._log("Found "+str(len(windows)) +
                          " minecraft instances.")
                i = 0
                for window in windows:
                    i += 1
                    window.set_title(str(i))
        except:
            self._log("Error during setup: \n" +
                      traceback.format_exc().replace("\n", "\\n"))

    def log_button(self) -> None:
        clipboard.copy(self._log_var.get().replace("\\n", "\n"))

    def _try_borderless_button(self) -> None:
        if len(self._windows) == 0:
            self._log("No instances yet, please run setup.")
        else:
            self._log("Setting borderless...")
            try:
                for window in self._windows:
                    window.go_borderless(self._window_size)
            except:
                self._log("Error going borderless:\n" +
                          traceback.format_exc().replace("\n", "\\n"))

    def _restore_button(self) -> None:
        if len(self._windows) == 0:
            self._log("No instances yet, please run setup.")
        else:
            self._log("Restoring windows...")
            try:
                i = 0
                for window in self._windows:
                    i += 1
                    window.restore_window(i)
                    window.activate()
            except:
                self._log("Error on restoring windows:\n" +
                          traceback.format_exc().replace("\n", "\\n"))


def main():
    try:
        ema = EasyMultiApp()
        ema.mainloop()
    except:
        import tkinter.messagebox
        tkinter.messagebox.showerror(
            "Easy Multi Error", traceback.format_exc())


if __name__ == "__main__":
    main()
