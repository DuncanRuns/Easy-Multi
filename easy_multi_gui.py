import ttkthemes, threading, os
import tkinter as tk
from typing import Callable, List
from tkinter import ttk
from easy_multi import EasyMulti, VERSION, InstanceInfo
from easy_multi_options import get_options_instance
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


class OptionsMenu(tk.Toplevel):
    def __init__(self, master) -> None:
        tk.Toplevel.__init__(self, master)
        self.log: Callable[[str, ], None] = master.log
        self.title("Easy Multi Options")
        self.attributes("-topmost", 1)
        self.resizable(0, 0)
        try:
            self.iconbitmap(resource_path("EasyMulti.ico"))
        except:
            pass

        self._options = get_options_instance()

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

        frame = ttk.LabelFrame(self._main_frame, text="Automatic Hiding")
        frame.grid(row=10, column=0, sticky="NEWS", padx=5, pady=5)
        self._init_widgets_hiding(frame)

        frame = ttk.LabelFrame(self._main_frame, text="Hotkeys")
        frame.grid(row=10, column=10, sticky="NEWS", padx=5, pady=5)
        self._init_widgets_hotkeys(frame)

    def _init_widgets_reset(self, frame: ttk.Frame) -> None:
        var = tk.BooleanVar(self)
        self._options.set_option_wrapper("pause_on_load", var)
        ttk.Checkbutton(frame, text="Pause on Load", variable=var).pack(
            padx=5, pady=5, anchor="w")

        var = tk.BooleanVar(self)
        self._options.set_option_wrapper("use_f3", var)
        ttk.Checkbutton(frame, text="Use F3", variable=var).pack(
            padx=5, pady=5, anchor="w")

        var = tk.BooleanVar(self)
        self._options.set_option_wrapper("auto_clear_worlds", var)
        ttk.Checkbutton(frame, text="Auto Clear Worlds",
                        variable=var).pack(padx=5, pady=5, anchor="w")

        clipboard_frame = ttk.Frame(frame)
        clipboard_frame.pack(padx=5, pady=5, anchor="w")

        var = tk.StringVar(self)
        self._options.set_option_wrapper("clipboard_on_reset", var)
        ttk.Label(clipboard_frame, text="Clipboard on Reset:").pack(anchor="w")
        ttk.Entry(clipboard_frame, textvariable=var).pack(anchor="w")

    def _init_widgets_window(self, frame: ttk.Frame) -> None:
        var = tk.BooleanVar(self)
        self._options.set_option_wrapper("use_fullscreen", var)
        ttk.Checkbutton(frame, text="Use Fullscreen (not recommended)", variable=var).pack(
            padx=5, pady=5, anchor="w")

        var = tk.BooleanVar(self)
        self._options.set_option_wrapper("use_borderless", var)
        ttk.Checkbutton(frame, text="Use Borderless", variable=var).pack(
            padx=5, pady=5, anchor="w")

    def _init_widgets_hiding(self, frame: ttk.Frame) -> None:
        var = tk.BooleanVar(self)
        self._options.set_option_wrapper("auto_hide", var)
        ttk.Checkbutton(frame, text="Auto Hide", variable=var).pack(
            padx=5, pady=5, anchor="w")

    def _init_widgets_hotkeys(self, frame: ttk.Frame) -> None:
        pass


class EasyMultiGUI(ttkthemes.ThemedTk):
    def __init__(self, logger: Logger) -> None:
        ttkthemes.ThemedTk.__init__(self, theme="breeze")

        self._options = get_options_instance()
        self._logger = logger

        self._logger.add_callback(self._on_log)
        self._log_var = tk.StringVar(self, value=" \n " * 9)

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

    def _init_widgets(self) -> None:
        self._init_log_widgets(0, 0)
        self._init_control_widgets(0, 1)
        self._instances_display = InstancesDisplay(
            self._main_frame, None)  # TODO: add remove_callback
        self._instances_display.grid(
            row=1, column=0, columnspan=2, padx=5, pady=5, sticky="NEWS")
        self._main_frame.grid_rowconfigure(1, minsize=50)

    def _init_log_widgets(self, row: int, column: int, rowspan: int = 1, columnspan: int = 1) -> None:
        log_frame = ttk.LabelFrame(
            self._main_frame, text="Log", width=410, height=188)
        log_frame.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan,
                       padx=5, pady=5)
        log_frame.grid_propagate(False)
        log_frame.grid_rowconfigure(0, weight=1)
        label = ttk.Label(
            log_frame, textvariable=self._log_var, justify="left", width=57)
        label.grid(row=0, column=0, padx=3, pady=3, sticky="EWS")

    def _init_control_widgets(self, row: int, column: int, rowspan: int = 1, columnspan: int = 1) -> None:
        control_frame = ttk.LabelFrame(self._main_frame, text="Controls")
        control_frame.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan,
                           padx=5, pady=5, sticky="NEWS")

        def gr(widget: tk.Widget, row: int, column: int, rowspan: int = 1, columnspan: int = 1, padx: int = 5, pady: int = 5) -> tk.Widget:  # Grid and return
            widget.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan,
                        padx=padx, pady=pady, sticky="NEWS")
            return widget

        gr(ttk.Button(control_frame, text="Setup Instances",
           command=self._setup_instances), 0, 0)

        gr(ttk.Button(control_frame, text="Options...", command=lambda *x: self._open_options()),
           100, 0)

    def _setup_instances(self) -> None:
        self._easy_multi.setup_instances()
        # TODO: Make instances display

    def _open_options(self) -> None:
        if not (self._options_menu and self._options_menu.winfo_exists()):
            self._options_menu = OptionsMenu(self)
            self.log("Options opened")
        self._options_menu.focus()

    def log(self, line: str) -> None:
        self._logger.log(line, "EasyMulti")

    def _on_log(self, line: str) -> None:
        lines = self._log_var.get().splitlines()
        lines.pop(0)
        lines.append(line)
        out = ""
        for line in lines:
            out += line + "\n"
        self._log_var.set(out.rstrip())


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")
