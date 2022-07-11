# EasyMulti.pyw is the main file which is ran through the .exe.
# The pyw extension also tells windows that it is a GUI based script as opposed to a CLI.
# This file can also be ran as a python script on linux (eg. `python3 EasyMulti.pyw`).

import tkinter.messagebox as tkMessageBox
import traceback
from easy_multi_gui import *
from easy_multi_options import EasyMultiOptions, get_location
from logger import Logger


def main():
    try:
        opt_path = get_location()
        options = EasyMultiOptions().try_load_file(opt_path)
        ema = EasyMultiGUI(options, Logger())
        ema.mainloop()
        options.save_file(opt_path)
        clear_and_stop_hotkey_checker()
    except:
        error = traceback.format_exc()
        print(error)
        tkMessageBox.showerror(
            "Easy Multi Error", error)


if __name__ == "__main__":
    main()
