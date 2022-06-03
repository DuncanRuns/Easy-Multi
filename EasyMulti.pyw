# EasyMulti.pyw is the main file which is ran through the .exe.
# The pyw extension also tells windows that it is a GUI based script as opposed to a CLI.
# This file can also be ran as a python script on linux (eg. `python3 EasyMulti.pyw`).

import tkinter.messagebox as tkMessageBox
import traceback
from EasyMultiGUI import *


def main():
    try:
        ema = EasyMultiGUI()
        ema.mainloop()
        clear_and_stop_hotkey_checker()
    except:
        error = traceback.format_exc()
        print(error)
        tkMessageBox.showerror(
            "Easy Multi Error", error)


if __name__ == "__main__":
    main()
