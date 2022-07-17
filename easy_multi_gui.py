import ttkthemes, threading, os
import tkinter as tk
from tkinter import ttk
from easy_multi import EasyMulti, VERSION
from easy_multi_options import get_options_instance
from logger import Logger


def resource_path(relative_path):
    try:
        from sys import _MEIPASS
        base_path = _MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class InstancesDisplay(ttk.Frame):
    def __init__(self, parent) -> None:
        ttk.Frame.__init__(self, parent)
        self._parent = parent


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
        self.iconbitmap(resource_path("EasyMulti.ico"))
        self.attributes("-topmost", 1)

        self.log("Initializing EasyMulti...")
        self.easy_multi = EasyMulti(logger)

        self.log("Creating widgets...")
        self._main_frame = ttk.Frame(self)
        self._main_frame.pack()
        self._init_widgets()

        self.log("")
        self.log("Welcome to Easy Multi v" + VERSION)
        self.after(50, self._loop)

    def _loop(self) -> None:
        threading.Thread(target=self.easy_multi.tick).start()
        self.after(50, self._loop)

    def _init_widgets(self) -> None:
        self._init_log_widgets(0, 0)
        self._init_control_widgets(0, 1)

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

        gr(ttk.Button(control_frame, text="Setup Instaces",
           command=lambda *x: self.easy_multi.setup_instances()), 0, 0)

        gr(ttk.Button(control_frame, text="hello"),
           1, 0).configure(state="disabled")

    def log(self, line: str) -> None:
        self._logger.log(line, "EasyMultiGUI")

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
