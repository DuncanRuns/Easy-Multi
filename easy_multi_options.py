import os, screeninfo
from basic_options import BasicOptions


class EasyMultiOptions(BasicOptions):
    def set_defaults(self) -> None:
        # Reset
        self.pause_on_load = True
        self.use_f3 = True
        self.auto_clear_worlds = True
        self.clipboard_on_reset = ""

        # Window
        self.use_borderless = False
        self.screen_location = [0, 0]
        self.screen_size = [1920, 1080]

        for monitor in screeninfo.get_monitors():
            if monitor.is_primary:
                self.screen_location = [monitor.x, monitor.y]
                self.screen_size = [monitor.width, monitor.height]

        # Instance Hiding
        self.auto_hide = False
        self.auto_hide_time = 5

        # Hotkeys
        self.reset_hotkey = ["u"]
        self.hide_hotkey = ["p"]
        self.bg_reset_hotkey = ["["]

        # OBS
        self.obs_press_hotkey = False
        self.obs_use_numpad = True
        self.obs_use_alt = False

        # Hidden
        self.last_instances = []


INSTANCE = EasyMultiOptions()


def get_options_instance() -> EasyMultiOptions:
    return INSTANCE


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
