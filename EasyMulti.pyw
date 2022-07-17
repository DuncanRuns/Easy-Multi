# EasyMulti.pyw is the main file which is ran through the .exe.
# The pyw extension also tells windows that it is a GUI based script as opposed to a CLI.
# This file can also be ran as a python script on linux (eg. `python3 EasyMulti.pyw`).

import tkinter.messagebox as tkMessageBox
import traceback
from easy_multi_gui import *
from easy_multi_options import get_location, get_options_instance
from logger import Logger
from input_util import clear_and_stop_hotkey_checker


def main():
    try:
        opt_path = get_location()
        options = get_options_instance().try_load_file(opt_path)
        logger = Logger()
        logger.add_callback(print)
        ema = EasyMultiGUI(logger)
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
