import threading, traceback, clipboard
from logger import Logger
from minecraft_instance import EMMinecraftInstance, get_all_mc_instances, get_current_mc_instance
from easy_multi_options import get_options_instance
from input_util import *

VERSION = "2.0.0-dev"


class InstanceInfo:
    def __init__(self, name: str, has_window: bool, world_loaded: bool) -> None:
        self.name = name
        self.has_window = has_window
        self.world_loaded = world_loaded


class EasyMulti:
    def __init__(self, logger: Logger) -> None:
        self._tick_lock = threading.Lock()
        self._mc_instances: List[EMMinecraftInstance] = []

        self._options = get_options_instance()
        self._logger = logger

        self.update_hotkeys()

        self.log("Initialized")

    def log(self, line: str) -> None:
        self._logger.log(line, "EasyMulti")

    def update_hotkeys(self) -> None:
        clear_and_stop_hotkey_checker()
        if len(self._options["reset_hotkey"]) > 0:
            register_hotkey(self._options["reset_hotkey"],
                            self._reset_hotkey_press)
        if len(self._options["hide_hotkey"]) > 0:
            register_hotkey(self._options["hide_hotkey"],
                            self._hide_hotkey_press)
        if len(self._options["bg_reset_hotkey"]) > 0:
            register_hotkey(self._options["bg_reset_hotkey"],
                            self._bg_reset_hotkey_press)
        start_hotkey_checker()

    def setup_instances(self) -> None:
        self.log("Redetecting Instances...")
        self._mc_instances = get_all_mc_instances()
        for instance in self._mc_instances:
            instance.set_logger(self._logger)
        self.log(f"Found {len(self._mc_instances)} instance(s)")

    def _reset_hotkey_press(self) -> None:
        current_instance = get_current_mc_instance()
        try:
            if current_instance and current_instance in self._mc_instances:
                already_reset = False
                if self._options["use_fullscreen"]:
                    already_reset = True
                    current_instance.reset(len(self._mc_instances) == 1)
                    time.sleep(0.05)

                next_ind = self._mc_instances.index(current_instance) + 1
                if next_ind >= len(self._mc_instances):
                    next_ind = 0
                next_instance = self._mc_instances[next_ind]
                if next_instance.has_window(True):
                    self._mc_instances[next_ind].activate(
                        self._options["use_fullscreen"])
                else:
                    self.log(f"Missing window for {next_instance.get_name()}")

                if not already_reset:
                    current_instance.reset(len(self._mc_instances) == 1)

                if self._options["clipboard_on_reset"] != "":
                    clipboard.copy(self._options["clipboard_on_reset"])

        except Exception:
            self.log("Error during reset: " +
                     traceback.format_exc().replace("\n", "\\n"))

    def _hide_hotkey_press(self) -> None:
        pass

    def _bg_reset_hotkey_press(self) -> None:
        pass

    def get_instance_infos(self) -> List[InstanceInfo]:
        return [
            InstanceInfo(
                instance.get_name(), instance.has_window(True), instance.is_world_loaded()
            ) for instance in self._mc_instances
        ]

    def tick(self) -> None:
        if self._tick_lock.locked():
            # Cancel tick if already being ran
            return
        with self._tick_lock:
            active_instance = get_current_mc_instance()
            if len(self._mc_instances) == 1:
                active_instance = self._mc_instances[0]
            for instance in self._mc_instances:
                instance.tick(
                    self._options["screen_location"], self._options["screen_size"], instance == active_instance)


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")
