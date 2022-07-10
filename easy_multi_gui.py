import tkinter as tk
from tkinter import ttk
from easy_multi import *
from easy_multi_options import EasyMultiOptions


class EasyMultiGUI(tk.Tk):
    def __init__(self, options: EasyMultiOptions):
        tk.Tk.__init__(self)
        self.em = EasyMulti(options)
