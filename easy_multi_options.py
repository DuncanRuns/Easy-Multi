import shutil
from basic_options import BasicOptions
import os


class EasyMultiOptions(BasicOptions):
    def set_defaults(self) -> None:
        self.use_fullscreen = False
        self.pause_on_load = True
        self.use_f3 = True

        self.screen_location = [0, 0]
        self.screen_size = [1920, 1080]

        # World Deletion
        self.auto_clear_worlds = True

        # Instance Hiding
        self.auto_hide = False
        self.auto_hide_time = 5

        # Hotkeys
        self.reset_hotkey = ["u"]
        self.hide_hotkey = ["p"]
        self.bg_reset_hotkey = ["["]


def get_or_create_folder() -> str:
    fol = os.path.join(os.path.expanduser("~"), ".EasyMulti")
    if not os.path.isdir(fol):
        os.mkdir(fol)
    return fol


def get_location() -> str:
    return os.path.join(get_or_create_folder(), "options.json")


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")
