import ttkthemes, threading, os
import tkinter as tk
from tkinter import ttk
from easy_multi import EasyMulti, VERSION
from easy_multi_options import EasyMultiOptions
from logger import Logger


def resource_path(relative_path):
    try:
        from sys import _MEIPASS
        base_path = _MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class EasyMultiGUI(ttkthemes.ThemedTk):
    def __init__(self, options: EasyMultiOptions, logger: Logger) -> None:
        ttkthemes.ThemedTk.__init__(self, theme="breeze")
        self.easy_multi = EasyMulti(options, logger)
        self.title("Easy Multi v" + VERSION)
        self.resizable(0, 0)
        self.iconbitmap(resource_path("EasyMulti.ico"))

        self._options = options
        self._logger = logger

        self._logger.add_callback(self._on_log)
        self._log_var = tk.StringVar(self, value=" \n " * 9)
        self.log("Welcome to Easy Multi v" + VERSION)

        self._main_frame = ttk.Frame(self)
        self._main_frame.pack()
        self._init_widgets()

    def _loop(self) -> None:
        threading.Thread(target=self.easy_multi.tick).start()
        self.after(50, self._loop)

    def _init_widgets(self) -> None:
        self._init_log_widgets()

    def _init_log_widgets(self) -> None:
        log_frame = ttk.LabelFrame(
            self._main_frame, text="Log", width=410, height=188)
        log_frame.grid(row=0, column=1, rowspan=10, padx=5, pady=5)
        log_frame.grid_propagate(False)
        log_frame.grid_rowconfigure(0, weight=1)
        label = ttk.Label(
            log_frame, textvariable=self._log_var, justify="left", width=57)
        label.grid(row=0, column=0, padx=3, pady=3, sticky="EWS")

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
