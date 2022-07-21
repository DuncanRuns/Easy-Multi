import ttkthemes, threading, os, input_util, time
import tkinter as tk
from typing import Callable, List
from tkinter import ttk
from easy_multi import EasyMulti, VERSION, InstanceInfo
from easy_multi_options import get_options_instance, BasicOptions
from logger import Logger


def resource_path(relative_path):
    try:
        from sys import _MEIPASS
        base_path = _MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class InstancesDisplay(ttk.LabelFrame):
    def __init__(self, parent: tk.Widget, remove_callback: Callable[[int], None]) -> None:
        ttk.LabelFrame.__init__(self, parent, text="Instances")
        self._remove_callback = remove_callback

    def update_infos(infos: List[InstanceInfo]) -> None:
        pass


_hotkey_setter_lock = threading.Lock()


class HotkeyWidget(ttk.Frame):
    def __init__(self, master: ttk.Frame, option_name: str, options: BasicOptions, display_name: str, log_func: Callable[[str], None], update_hotkeys_func: Callable[[], None], still_exists_func: Callable[[], bool]) -> None:
        ttk.Frame.__init__(self, master)

        self._hotkey: List[str] = []
        self._em_options = options
        self._option_name = option_name
        self._option_display_name = display_name
        self._hotkey_display = tk.StringVar()
        self._update_key_display()
        self.log = log_func
        self._update_hotkeys = update_hotkeys_func
        self._is_running = still_exists_func

        ttk.Label(self, text=display_name +
                  ":").grid(row=0, column=0, sticky="NW")
        self._button = ttk.Button(
            self, textvariable=self._hotkey_display, command=self._on_button)
        self._button.grid(row=2, column=0, sticky="NW")

    def _update_key_display(self) -> None:
        self._hotkey_display.set(input_util.format_hotkey(
            self._em_options.get_option(self._option_name)))

    def _on_button(self) -> None:
        threading.Thread(target=self._hotkey_set_thread).start()

    def _is_button_focused(self) -> bool:
        focused = self.focus_get()
        if focused and focused == self._button:
            return True
        return False

    def _hotkey_set_thread(self) -> None:
        if _hotkey_setter_lock.locked():
            return
        with _hotkey_setter_lock:
            self._hotkey_display.set("...")
            out = input_util.read_hotkey(self._is_button_focused)
            time.sleep(0.01)
            if self._is_running():
                if out:
                    if out == ["escape"]:
                        self._em_options.set_option(self._option_name, [])
                        self.log(
                            f"Cleared \"{self._option_display_name}\" hotkey")
                        self._update_hotkeys()
                    else:
                        self._em_options.set_option(self._option_name, out)
                        self.log(
                            f"Set \"{self._option_display_name}\" hotkey to {input_util.format_hotkey(out)}")
                        self._update_hotkeys()
                self._update_key_display()


class OptionsMenu(tk.Toplevel):
    def __init__(self, master) -> None:
        tk.Toplevel.__init__(self, master)
        self._master: EasyMultiGUI = master
        self.title("Easy Multi Options")
        self.attributes("-topmost", 1)
        self.resizable(0, 0)
        try:
            self.iconbitmap(resource_path("EasyMulti.ico"))
        except:
            pass

        self._em_options = get_options_instance()
        self.log = self._master.log

        self._main_frame = ttk.Frame(self)
        self._main_frame.grid()
        self._init_widgets()

    def _init_widgets(self) -> None:
        frame = ttk.LabelFrame(self._main_frame, text="Resetting")
        frame.grid(row=0, column=0, sticky="NEWS", padx=5, pady=5)
        self._init_widgets_reset(frame)

        frame = ttk.LabelFrame(self._main_frame, text="Window")
        frame.grid(row=0, column=10, sticky="NEWS", padx=5, pady=5)
        self._init_widgets_window(frame)

        frame = ttk.LabelFrame(self._main_frame, text="Hotkeys")
        frame.grid(row=10, column=0, sticky="NEWS", padx=5, pady=5)
        self._init_widgets_hotkeys(frame)

        frame = ttk.LabelFrame(self._main_frame, text="Automatic Hiding")
        frame.grid(row=10, column=10, sticky="NEWS", padx=5, pady=5)
        self._init_widgets_hiding(frame)

    def _init_widgets_reset(self, frame: ttk.Frame) -> None:
        var = tk.BooleanVar(self)
        self._em_options.set_option_wrapper("pause_on_load", var)
        ttk.Checkbutton(frame, text="Pause on Load", variable=var).pack(
            padx=5, pady=5, anchor="w")

        var = tk.BooleanVar(self)
        self._em_options.set_option_wrapper("use_f3", var)
        ttk.Checkbutton(frame, text="Use F3", variable=var).pack(
            padx=5, pady=5, anchor="w")

        var = tk.BooleanVar(self)
        self._em_options.set_option_wrapper("auto_clear_worlds", var)
        ttk.Checkbutton(frame, text="Auto Clear Worlds",
                        variable=var).pack(padx=5, pady=5, anchor="w")

        clipboard_frame = ttk.Frame(frame)
        clipboard_frame.pack(padx=5, pady=5, anchor="w")

        var = tk.StringVar(self)
        self._em_options.set_option_wrapper("clipboard_on_reset", var)
        ttk.Label(clipboard_frame, text="Clipboard on Reset:").pack(anchor="w")
        ttk.Entry(clipboard_frame, textvariable=var).pack(anchor="w")

    def _init_widgets_window(self, frame: ttk.Frame) -> None:
        var = tk.BooleanVar(self)
        self._em_options.set_option_wrapper("use_fullscreen", var)
        ttk.Checkbutton(frame, text="Use Fullscreen (not recommended)", variable=var).pack(
            padx=5, pady=5, anchor="w")

        var = tk.BooleanVar(self)
        self._em_options.set_option_wrapper("use_borderless", var)
        ttk.Checkbutton(frame, text="Use Borderless", variable=var).pack(
            padx=5, pady=5, anchor="w")

    def _init_widgets_hiding(self, frame: ttk.Frame) -> None:
        var = tk.BooleanVar(self)
        self._em_options.set_option_wrapper("auto_hide", var)
        ttk.Checkbutton(frame, text="Auto Hide", variable=var).pack(
            padx=5, pady=5, anchor="w")

        auto_hide_time_label = ttk.Label(frame)
        auto_hide_time_label.pack(padx=5, pady=5, anchor="w")

        def scroll_callback(event=None) -> None:
            if event:
                delta = event.delta
                if delta > 0:
                    self._em_options["auto_hide_time"] += 1
                elif delta < 0:
                    self._em_options["auto_hide_time"] -= 1
            self._em_options["auto_hide_time"] = max(
                1, min(60, self._em_options["auto_hide_time"]))
            auto_hide_time_label.config(
                text=f"Auto Hide Time: {self._em_options['auto_hide_time']} minutes\n(Hover+scroll to change)")

        scroll_callback()
        auto_hide_time_label.bind("<MouseWheel>", scroll_callback)

    def _init_widgets_hotkeys(self, frame: ttk.Frame) -> None:
        HotkeyWidget(frame, "reset_hotkey", self._em_options, "Reset",
                     self.log, self._master.on_hotkey_change, self._master.is_running).pack(padx=5, pady=5, anchor="w")
        HotkeyWidget(frame, "hide_hotkey", self._em_options, "Hide Other Instances",
                     self.log, self._master.on_hotkey_change, self._master.is_running).pack(padx=5, pady=5, anchor="w")
        HotkeyWidget(frame, "bg_reset_hotkey", self._em_options, "Background Reset",
                     self.log, self._master.on_hotkey_change, self._master.is_running).pack(padx=5, pady=5, anchor="w")


class EasyMultiGUI(ttkthemes.ThemedTk):
    def __init__(self, logger: Logger) -> None:
        self._running = False
        self._closed = False
        ttkthemes.ThemedTk.__init__(self, theme="breeze")

        self._em_options = get_options_instance()
        self._logger = logger

        self._logger.add_callback(self._on_log)
        total_lines = 13
        self._log_var = tk.StringVar(self, value=" \n " * (total_lines - 1))

        self.log("Setting up window...")
        self.title("Easy Multi v" + VERSION)
        self.resizable(0, 0)
        try:
            self.iconbitmap(resource_path("EasyMulti.ico"))
        except:
            pass
        self.attributes("-topmost", 1)

        self.log("Initializing EasyMulti...")
        self._easy_multi = EasyMulti(logger)

        self.log("Creating widgets...")
        self._main_frame = ttk.Frame(self)
        self._main_frame.pack()
        self._init_widgets()

        self._options_menu: tk.Toplevel = None

        self.log("")
        self.log("Welcome to Easy Multi v" + VERSION)
        self.after(50, self._loop)

    def _loop(self) -> None:
        threading.Thread(target=self._easy_multi.tick).start()
        self.after(50, self._loop)

    def mainloop(self) -> None:
        self._running = True
        super().mainloop()
        self._running = False
        self.on_close()

    def on_close(self) -> None:
        self._closed = True
        input_util.clear_and_stop_hotkey_checker()
        self._easy_multi.restore_titles()
        time.sleep(0.1)
        self._logger.wait_for_file_write()
        time.sleep(0.1)

    def is_running(self) -> None:
        return self._running

    def _init_widgets(self) -> None:
        self._init_widgets_log(0, 0)
        self._init_widgets_control(0, 1)
        self._instances_display = InstancesDisplay(
            self._main_frame, None)  # TODO: add remove_callback
        self._instances_display.grid(
            row=1, column=0, columnspan=2, padx=5, pady=5, sticky="NEWS")
        self._main_frame.grid_rowconfigure(1, minsize=50)

    def _init_widgets_log(self, row: int, column: int, rowspan: int = 1, columnspan: int = 1) -> None:
        log_frame = ttk.LabelFrame(
            self._main_frame, text="Log", width=410, height=50)
        log_frame.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan,
                       padx=5, pady=5)
        log_frame.grid_rowconfigure(0, weight=1)
        label = ttk.Label(
            log_frame, textvariable=self._log_var, justify="left", width=57)
        label.grid(row=0, column=0, padx=3, pady=3, sticky="EWS")

    def _init_widgets_control(self, row: int, column: int, rowspan: int = 1, columnspan: int = 1) -> None:
        frame = ttk.LabelFrame(self._main_frame, text="Controls")
        frame.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan,
                   padx=5, pady=5, sticky="NEWS")

        def gr(widget: tk.Widget, row: int, column: int, rowspan: int = 1, columnspan: int = 1, padx: int = 5, pady: int = 5) -> tk.Widget:  # Grid and return
            widget.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan,
                        padx=padx, pady=pady, sticky="NEWS")
            return widget

        gr(ttk.Button(frame, text="Setup Instances",
           command=self._setup_instances), 0, 0)

        gr(ttk.Button(frame, text="Set Titles",
           command=self._easy_multi.set_titles), 1, 0)

        gr(ttk.Button(frame, text="Options...", command=lambda *x: self._open_options()),
           100, 0)

    def _setup_instances(self) -> None:
        self._easy_multi.setup_instances()
        # TODO: Make instances display

    def _open_options(self) -> None:
        if not (self._options_menu and self._options_menu.winfo_exists()):
            self._options_menu = OptionsMenu(self)
            self.log("Options opened")
        self._options_menu.focus()

    def on_hotkey_change(self) -> None:
        self._easy_multi.update_hotkeys()

    def log(self, line: str) -> None:
        self._logger.log(line, "Easy Multi")

    def _on_log(self, from_log: str) -> None:
        if not self._closed:
            lines = [(" " if i == " " else i) for i in [j.strip()
                                                        for j in self._log_var.get().splitlines()]]
            new_lines = [(" " if i == " " else i)
                         for i in [j.strip() for j in from_log.splitlines()]]
            for i in range(len(new_lines)):
                lines.pop(0)
            lines.extend(new_lines)
            out = ""
            for line in lines:
                out += line + "\n"
            self._log_var.set(out.rstrip())


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")
