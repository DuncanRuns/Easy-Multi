from sys import maxsize
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as tkMessageBox
import os
import json
import keyboard
import time
import traceback
import global_hotkeys
import clipboard
import threading
import webbrowser

from window import *
from key_util import *
from instance_util import *

VERSION = "1.3.0"


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
    "window_size": [1920, 1080],
    "instances_folder": None,
    "clear_types": "tttt",
    "auto_clear": False,
    "use_numpad": False,
    "use_alt": True
}

CHECK = "✅"
CROSS = "❎"


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

    # ------ init -----

    def __init__(self):
        super().__init__()

        # TK Window Stuff

        self.title("Easy Multi v"+VERSION)
        self.resizable(0, 0)
        self.iconbitmap(resource_path("EasyMulti.ico"))
        self.protocol("WM_DELETE_WINDOW", self._exit)

        # App Stuff

        self._did_hide = False
        self._windows = []
        self._log_lines = [" " for i in range(20)]
        self._log_var: tk.StringVar = tk.StringVar(
            self, value="")
        self._log_lock = threading.Lock()
        self._running = False
        self._changing_something = False

        # String Vars

        self._total_var: tk.StringVar = tk.StringVar(
            self, value="Current Instances: 0")
        self._reset_dis_var: tk.StringVar = tk.StringVar(self, value="")
        self._hide_dis_var: tk.StringVar = tk.StringVar(self, value="")
        self._window_size_dis_var: tk.StringVar = tk.StringVar(self, value="")
        self._instances_folder_dis_var: tk.StringVar = tk.StringVar(
            self, value="")
        self._clear_types_dis_vars = []
        for i in range(4):
            self._clear_types_dis_vars.append(tk.StringVar(self, value=""))
        self._auto_clear_dis_var = tk.StringVar(self, value="")
        self._use_numpad_dis_var = tk.StringVar(self, value="")
        self._use_alt_dis_var = tk.StringVar(self, value="")

        self._log("Welcome to Easy Multi!\n ")
        self._init_widgets()
        self._options_json = self._load_options_json()
        self._refresh_options()

    def _refresh_options(self) -> None:
        # Hotkeys

        self._setup_hotkeys()

        # Window Size
        self._window_size = self._get_setting(
            self._options_json, "window_size")
        self._window_size_dis_var.set(
            "Window Size:\n"+str(self._window_size[0])+"x"+str(self._window_size[1]))

        # Instances Folder
        self._instances_folder = self._get_setting(
            self._options_json, "instances_folder")
        self._instances_folder_dis_var.set(
            ".................... Currently Unset" if self._instances_folder is None else ".................... "+self._instances_folder)

        # Clear Types
        self._clear_types: str = self._get_setting(
            self._options_json, "clear_types")
        for i, b in enumerate(list(self._clear_types)):
            self._clear_types_dis_vars[i].set(CHECK if b == "t" else CROSS)

        # Auto Clear
        self._auto_clear = self._get_setting(self._options_json, "auto_clear")
        self._auto_clear_dis_var.set(CHECK if self._auto_clear else CROSS)

        # Use numpad
        self._use_numpad = self._get_setting(self._options_json, "use_numpad")
        self._use_numpad_dis_var.set(CHECK if self._use_numpad else CROSS)

        # Use Alt
        self._use_alt = self._get_setting(self._options_json, "use_alt")
        self._use_alt_dis_var.set(CHECK if self._use_alt else CROSS)

        # Save
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

        title_frame = tk.Frame(self)
        title_frame.grid(row=0, column=0, columnspan=5, padx=5, pady=5)

        tk.Label(title_frame, text="Easy Multi v"+VERSION,
                 font="arial 14").grid(row=0, column=0)
        ll = tk.Label(title_frame, text="by Duncan",
                      font="arial 10 underline", foreground="blue")
        ll.grid(row=1, column=0)
        ll.bind("<Button-1>",
                lambda x: webbrowser.open("https://linktr.ee/DuncanRuns"))

        self._init_widgets_control()
        self._init_widgets_options()
        self._init_widgets_log()
        self._init_widgets_worlds()

    def _init_widgets_control(self) -> None:
        control_frame = tk.LabelFrame(self)
        control_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nes")
        tk.Button(control_frame, text="Setup Instances", command=self._setup_button).grid(
            row=0, column=0, padx=5, pady=5, sticky="NESW")
        tk.Button(control_frame, text="Go Borderless", command=self._go_borderless_button).grid(
            row=1, column=0, padx=5, pady=5, sticky="NESW")
        tk.Button(control_frame, text="Restore Windows", command=self._restore_button).grid(
            row=2, column=0, padx=5, pady=5, sticky="NESW")

    def _init_widgets_options(self) -> None:
        options_frame = tk.LabelFrame(self)
        options_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nes")
        tk.Button(options_frame, textvariable=self._reset_dis_var, command=self._set_reset_button).grid(
            row=0, column=0, padx=5, pady=5, sticky="NESW")
        tk.Button(options_frame, textvariable=self._hide_dis_var, command=self._set_hide_button).grid(
            row=1, column=0, padx=5, pady=5, sticky="NESW")
        tk.Button(options_frame, textvariable=self._window_size_dis_var, command=self._set_window_size_button).grid(
            row=2, column=0, padx=5, pady=5, sticky="NESW")
        ttk.Separator(options_frame, orient=tk.HORIZONTAL).grid(
            row=3, column=0, sticky="we", pady=5)

        ss_frame = tk.Frame(options_frame)
        ss_frame.grid(row=4, column=0, padx=5, pady=5)
        tk.Label(ss_frame, text="Scene Switching").grid(
            row=0, column=0, columnspan=2)
        tk.Button(ss_frame, textvariable=self._use_numpad_dis_var,
                  command=self._use_numpad_button).grid(row=1, column=0)
        tk.Label(ss_frame, text="Use Numpad").grid(row=1, column=1, sticky="w")
        tk.Button(ss_frame, textvariable=self._use_alt_dis_var,
                  command=self._use_alt_button).grid(row=2, column=0)
        tk.Label(ss_frame, text="Use Alt").grid(row=2, column=1, sticky="w")

    def _init_widgets_log(self) -> None:
        log_frame = tk.LabelFrame(self)
        log_frame.grid(row=1, column=1, padx=5, pady=5, rowspan=2, sticky="n")
        tk.Label(log_frame, textvariable=self._log_var, anchor=tk.W,
                 justify=tk.LEFT, width=50).grid(row=0, column=0, padx=5, pady=5, columnspan=3)
        ttk.Separator(log_frame, orient=tk.HORIZONTAL).grid(
            row=1, column=0, columnspan=3, pady=3, sticky="we")
        tk.Label(log_frame, textvariable=self._total_var).grid(
            row=2, column=0, padx=5, pady=5, sticky="w")
        tk.Button(log_frame, text="Copy Log", command=self._copy_log_button).grid(
            row=2, column=2, padx=5, pady=5, sticky="e")

    def _init_widgets_worlds(self) -> None:
        worlds_frame = tk.LabelFrame(self)
        worlds_frame.grid(row=1, column=2, padx=5,
                          pady=5, rowspan=2, sticky="n")

        csw_frame = tk.Frame(worlds_frame)
        csw_frame.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        tk.Button(csw_frame, text="Clear Speedrun Worlds",
                  command=self._clear_worlds_button).grid(row=0, column=0)
        info_button = tk.Label(csw_frame, text="?", font="arial 9 underline",
                               foreground="blue")
        info_button.grid(row=0, column=1, padx=3)

        def show_clear_explanation(*args):
            tkMessageBox.showinfo(
                "Easy Multi: World Clearing", "Clearing Speedrun Worlds will clear out all speedrun worlds from all MultiMC instances except for the latest 5 in each instance.\n\n\"Automatically Clear\" will do this every reset.\n\n\"World Types to Clear\" determine which worlds are considered speedrun worlds.")
        info_button.bind("<Button-1>", show_clear_explanation)

        auto_clear_frame = tk.Frame(worlds_frame)
        auto_clear_frame.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        tk.Button(auto_clear_frame, textvariable=self._auto_clear_dis_var, command=self._auto_clear_button).grid(
            row=0, column=0)
        tk.Label(auto_clear_frame, text="Automatically Clear").grid(
            row=0, column=1)

        ttk.Separator(worlds_frame, orient=tk.HORIZONTAL).grid(
            row=45, column=0, pady=5, sticky="we")

        tk.Label(worlds_frame, text="MultiMC Instances Folder:").grid(
            row=50, column=0, padx=5, pady=5, sticky="w")
        path_frame = tk.Frame(worlds_frame)
        path_frame.grid(row=51, column=0, padx=5, pady=0, sticky="w")
        tk.Label(path_frame, textvariable=self._instances_folder_dis_var, anchor=tk.E, width=15,).grid(
            row=1, column=1, padx=5, pady=0, sticky="w")
        tk.Button(path_frame, text="📁", command=self._set_instances_path_button).grid(
            row=1, column=0, pady=0, sticky="w")

        ttk.Separator(worlds_frame, orient=tk.HORIZONTAL).grid(
            row=95, column=0, pady=5, sticky="we")

        tk.Label(worlds_frame, text="World Types to Clear:").grid(
            row=99, column=0, padx=5, sticky="w")

        clear_types_frame = tk.Frame(worlds_frame)
        clear_types_frame.grid(row=100, column=0, padx=5, pady=5, sticky="w")
        clear_type_frames = []
        for i in range(4):
            frame = tk.Frame(clear_types_frame)
            frame.grid(row=i, column=0, sticky="w")
            clear_type_frames.append(frame)
        tk.Button(
            clear_type_frames[0], textvariable=self._clear_types_dis_vars[0], command=lambda *x: self._clear_type_button(0)).grid(row=0, column=0, sticky="w")
        tk.Button(
            clear_type_frames[1], textvariable=self._clear_types_dis_vars[1], command=lambda *x: self._clear_type_button(1)).grid(row=0, column=0, sticky="w")
        tk.Button(
            clear_type_frames[2], textvariable=self._clear_types_dis_vars[2], command=lambda *x: self._clear_type_button(2)).grid(row=0, column=0, sticky="w")
        tk.Button(
            clear_type_frames[3], textvariable=self._clear_types_dis_vars[3], command=lambda *x: self._clear_type_button(3)).grid(row=0, column=0, sticky="w")
        tk.Label(clear_type_frames[0], text="New World (22)").grid(
            row=0, column=1)
        tk.Label(clear_type_frames[1], text="RandomSpeedrun #22").grid(
            row=0, column=1)
        tk.Label(clear_type_frames[2], text="SetSpeedrun #22").grid(
            row=0, column=1)
        tk.Label(clear_type_frames[3], text="Speedrun #22").grid(
            row=0, column=1)

    # ----- exit -----

    def _exit(self, *args) -> None:
        self._abandon_windows()
        self.destroy()

    # ----- buttons -----

    def _use_numpad_button(self, *args) -> None:
        if self._use_numpad and (not self._use_alt):
            ans = tkMessageBox.askyesno(
                "Easy Multi: Are you sure?", "The hotkey used to switch scenes will be \"1\", \"2\", \"3\", etc.\nAre you sure this is what you want?")
            if not ans:
                return
        self._options_json["use_numpad"] = not self._use_numpad
        self._refresh_options()

    def _use_alt_button(self, *args) -> None:
        if self._use_alt and (not self._use_numpad):
            ans = tkMessageBox.askyesno(
                "Easy Multi: Are you sure?", "The hotkey used to switch scenes will be \"1\", \"2\", \"3\", etc.\nAre you sure this is what you want?")
            if not ans:
                return
        self._options_json["use_alt"] = not self._use_alt
        self._refresh_options()

    def _auto_clear_button(self, *args) -> None:
        self._options_json["auto_clear"] = not self._auto_clear
        self._refresh_options()

    def _clear_worlds_button(self, *args) -> None:
        self._clear_worlds()

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

    def _setup_button(self, *args) -> None:
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

    def _copy_log_button(self, *args) -> None:
        clipboard.copy(self._log_var.get().replace("\\n", "\n"))

    def _go_borderless_button(self, *args) -> None:
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

    def _restore_button(self, *args) -> None:
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

    def _set_instances_path_button(self, *args) -> None:
        ans = ask_for_directory(self._instances_folder)
        if ans != "":
            instances_folder = ensure_instances_path(ans)
            if instances_folder is None:
                tkMessageBox.showerror("Easy Multi: Not an instances folder.",
                                       "The selected directory was not an instances folder\nor the folder doesn't contain any instances yet.\nAttempts to located a related instances folder also failed.")
            else:
                self._options_json["instances_folder"] = instances_folder
                self._refresh_options()

    def _clear_type_button(self, ind: int) -> None:
        l = list(self._clear_types)
        l[ind] = "t" if l[ind] == "f" else "f"
        s = ""
        for i in l:
            s += i
        self._options_json["clear_types"] = s
        self._refresh_options()

    # ----- keypress -----

    def _reset_keypress(self) -> None:
        if are_any_keys_pressed(get_invalid_modifiers(self._reset_hotkey)):
            return
        threading.Thread(target=self._run_macro).start()

    def _run_macro(self) -> None:
        try:
            if not self._running:
                self._validate_windows()
                window_to_reset = get_current_window()
                if window_to_reset in self._windows:
                    self._running = True
                    window_to_reset = self._windows[self._windows.index(
                        window_to_reset)]
                    if self._did_hide:
                        for window in self._windows:
                            window.untiny(self._window_size)
                        self._did_hide = False
                    if len(self._windows) == 1:
                        self._run_macro_single(window_to_reset)
                    else:
                        self._run_macro_multi(window_to_reset)
                    self._running = False
                    if self._auto_clear:
                        self._clear_worlds()
        except:
            self._log("Error during reset: \n" +
                      traceback.format_exc().replace("\n", "\\n"))
            self._running = False

    def _run_macro_single(self, window_to_reset: Window) -> None:
        self._log("Resetting (Single)...")
        self._reset_world(window_to_reset)

    def _run_macro_multi(self, window_to_reset: Window) -> None:
        next_window_index = self._windows.index(
            window_to_reset) + 1
        next_window_index = 0 if next_window_index >= len(
            self._windows) else next_window_index
        next_window: Window = self._windows[next_window_index]
        switch_key = str(next_window_index+1)
        if self._use_numpad:
            switch_key = "numpad_"+switch_key
        if self._use_alt:
            switch_key = "alt+"+switch_key

        self._log("Resetting and pressing " +
                  format_hotkey(switch_key.split("+"))+"...")

        self._reset_world(window_to_reset)

        press_keys_for_time(switch_key.split("+"), 0.1)
        next_window.activate()
        time.sleep(0.1)

        keyboard.press_and_release("esc")

    def _reset_world(self, window_to_reset: Window):
        pre19 = False
        try:
            pre19 = int(window_to_reset.get_original_title().split(".")[1]) < 9
        except:
            pass
        keyboard.press_and_release("esc")
        if pre19:
            time.sleep(0.07)  # Uh oh magic number
            keyboard.press_and_release("tab")
        else:
            keyboard.press_and_release("shift+tab")
        keyboard.press_and_release("enter")

    def _hide_keypress(self) -> None:
        try:
            if are_any_keys_pressed(get_invalid_modifiers(self._hide_hotkey)):
                return
            current_window = get_current_window()
            if len(self._windows) > 1 and current_window in self._windows:
                successes = 0
                for window in self._windows:
                    if window != current_window:
                        if window.tiny():
                            successes += 1
                if successes > 0:
                    self._did_hide = True
                    self._log("Hid "+str(successes)+" instances.")
                else:
                    self._log(
                        "No instances were hid (maybe they weren't borderless)")
        except:
            self._log("Error during hiding: \n" +
                      traceback.format_exc().replace("\n", "\\n"))
            self._running = False

    # ----- general -----

    def _clear_worlds(self) -> None:
        if self._instances_folder is None:
            self._log("No instances folder set!")
        else:
            threading.Thread(target=self._clear_worlds_thread).start()

    def _clear_worlds_thread(self) -> None:
        if self._clear_types.count("t") > 0:
            regex_list = []
            for ind, regex in enumerate([NEW_WORLD_RE, RSPEEDRUN_RE, SSPEEDRUN_RE, SPEEDRUN_RE]):
                if self._clear_types[ind] == "t":
                    regex_list.append(regex)
            count = delete_all_worlds(self._instances_folder, regex_list, 5)
            self._log("Cleared "+str(count)+" worlds.")
        else:
            self._log("No clear types set!")

    def _is_app_selected(self) -> bool:
        try:
            return self.focus_displayof() is not None
        except:
            return False

    def _set_windows(self, windows: list) -> None:
        self._total_var.set("Current Instances: "+str(len(windows)))
        self._windows = windows

    def _validate_windows(self) -> None:
        for window in self._windows:
            window: Window
            if not window.exists():
                self._log("One of your instances has closed!")
                self._abandon_windows()
                break

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

    def _log(self, txt: str) -> None:
        with self._log_lock:
            for new_line in [i.rstrip() for i in txt.split("\n")]:
                last_line = self._log_lines[-1]
                if new_line == last_line:
                    self._log_lines[-1] = new_line + " (x2)"
                elif (" (x" in last_line and new_line == last_line[:last_line.index(" (x")]):
                    self._log_lines[-1] = new_line + \
                        " (x" + \
                        str(int(
                            last_line[last_line.index(" (x")+3:-1]) + 1)+")"
                else:
                    while len(self._log_lines) >= 20:
                        self._log_lines.pop(0)
                    self._log_lines.append(" " if new_line == "" else new_line)
            log_txt = ""
            for line in self._log_lines:
                if log_txt != "":
                    log_txt += "\n"
                log_txt += line
            self._log_var.set(log_txt)

    # ----- file management -----

    @ staticmethod
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

    @ staticmethod
    def _save_options_json(options_json: dict) -> None:
        with open("options.json", "w+") as options_file:
            json.dump(options_json, options_file, indent=4)
            options_file.close()

    @ staticmethod
    def _get_setting(options_json: dict, key: str) -> dict:
        return options_json.get(key, DEFAULT_OPTIONS.get(key, None))


def main():
    try:
        ema = EasyMultiApp()
        ema.mainloop()
        global_hotkeys.stop_checking_hotkeys()
    except:
        tkMessageBox.showerror(
            "Easy Multi Error", traceback.format_exc())


if __name__ == "__main__":
    main()
