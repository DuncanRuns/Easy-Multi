import ttkthemes, threading
import tkinter as tk
from tkinter import ttk
from easy_multi import *
from easy_multi_options import EasyMultiOptions
from logger import Logger


class EasyMultiGUI(tk.Tk):
    def __init__(self, options: EasyMultiOptions, logger: Logger):
        tk.Tk.__init__(self)
        self.easy_multi = EasyMulti(options, logger)
        self.after(0, self._loop)

    def _loop(self):
        threading.Thread(target=self.easy_multi.tick).start()
        self.after(50, self._loop)


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")
