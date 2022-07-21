# EasyMulti.pyw is the main file which is ran through the .exe.
# The pyw extension also tells windows that it is a GUI based script as opposed to a CLI.
# This file can also be ran as a python script on linux (eg. `python3 EasyMulti.pyw`).

import traceback, os
import tkinter.messagebox as tkMessageBox
from easy_multi_gui import *
from easy_multi_options import get_location, get_options_instance
from logger import Logger


def main():
    try:
        opt_path = get_location()
        options = get_options_instance().try_load_file(opt_path)
        logger = Logger()
        logger.add_callback(print)
        emg = EasyMultiGUI(logger)
        try:
            emg.mainloop()
        except:
            pass
        emg.on_close()
        options.save_file(opt_path)
        if len(threading.enumerate()) > 2:
            print("Threads:", threading.enumerate())
            time.sleep(1)  # Wait in case something else is running...
            print("Force exiting...")
            os._exit(0)
    except:
        error = traceback.format_exc()
        print(error)
        tkMessageBox.showerror(
            "Easy Multi Error", error)


if __name__ == "__main__":
    main()
