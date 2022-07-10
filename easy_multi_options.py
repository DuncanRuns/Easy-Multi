from basic_options import BasicOptions


class EasyMultiOptions(BasicOptions):
    def set_defaults(self) -> None:
        use_wall = False
        use_fullscreen = False
        monitor_size = [1920, 1080]

        # World Deletion
        auto_clear_worlds = True

        # Instance Hiding
        auto_hide = False
        auto_hide_time = 5

        # Hotkeys
        reset_hotkey = ["u"]
        hide_hotkey = ["p"]
        bg_reset_hotkey = ["["]
