# EasyMulti.pyw is the main file which is run through the .exe.
# The pyw extension also tells windows that it is a GUI based script as opposed to a CLI.
# This file can also be run as a python script on linux (e.g. `python3 EasyMulti.pyw`).

import traceback, os, threading, time
import tkinter.messagebox as tkMessageBox
from easy_multi_gui import EasyMultiGUI
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
        options.save_file(opt_path)
        print("Saved options")
        print("Threads:", threading.enumerate())
        if len(threading.enumerate()) > 1:
            print("Force exiting in 1 second...")
            time.sleep(1)  # Wait in case something else is running...
            print("Force exiting...")
            print("Losing these threads:", threading.enumerate())
            os._exit(0)
    except:
        error = traceback.format_exc()
        print(error)
        tkMessageBox.showerror(
            "Easy Multi Error", error)


if __name__ == "__main__":
    main()
