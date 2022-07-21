import threading, traceback, clipboard
from logger import Logger
from minecraft_instance import EMMinecraftInstance, get_all_mc_instances, get_current_mc_instance, get_instance_from_dir
from easy_multi_options import get_options_instance
from input_util import *

VERSION = "2.0.0-dev"


class InstanceInfo:
    def __init__(self, name: str, has_window: bool, world_loaded: bool, game_dir: str) -> None:
        self.name = name
        self.has_window = has_window
        self.world_loaded = world_loaded
        self.game_dir = game_dir


class EasyMulti:
    def __init__(self, logger: Logger) -> None:
        self._tick_lock = threading.Lock()

        self._options = get_options_instance()
        self._logger = logger
        self._has_hidden = False

        self._mc_instances: List[EMMinecraftInstance] = [
            get_instance_from_dir(i) for i in self._options["last_instances"]]
        if len(self._mc_instances) > 0:
            self.set_titles()
        for instance in self._mc_instances:
            instance.set_logger(logger)

        self.update_hotkeys()

        self.log("Initialized")

    def log(self, line: str) -> None:
        self._logger.log(line, "Easy Multi")

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
        self.restore_titles()
        self.log("Redetecting Instances...")
        self._mc_instances = get_all_mc_instances()
        for instance in self._mc_instances:
            instance.set_logger(self._logger)
        self.log(f"Found {len(self._mc_instances)} instance(s)")
        self.set_titles()
        self._options["last_instances"] = [
            i.get_game_dir() for i in self._mc_instances]

    def remove_instance(self, instance_num: int) -> None:
        inst = self._mc_instances.pop(instance_num)
        if inst.has_window():
            inst.get_window().revert_title()
        self.log(f"Removed Instance: {inst.get_name()}")
        self._options["last_instances"] = [
            i.get_game_dir() for i in self._mc_instances]

    def set_titles(self) -> None:
        self.log("Setting titles...")
        i = 0
        for instance in self._mc_instances:
            i += 1
            if instance.has_window():
                instance.get_window().set_title(str(i))

    def restore_titles(self) -> None:
        self.log("Restoring titles...")
        for instance in self._mc_instances:
            if instance.has_window():
                instance.get_window().revert_title()

    def _reset_hotkey_press(self) -> None:
        try:
            current_instance = get_current_mc_instance()
            single_instance = len(self._mc_instances) == 1
            if current_instance and current_instance in self._mc_instances:
                already_reset = False
                if self._options["use_fullscreen"]:
                    already_reset = True
                    current_instance.reset(True, single_instance)
                    time.sleep(0.05)

                if not single_instance:

                    next_ind = self._mc_instances.index(current_instance) + 1
                    if next_ind >= len(self._mc_instances):
                        next_ind = 0
                    next_instance = self._mc_instances[next_ind]
                    if next_instance.has_window(True):
                        self._mc_instances[next_ind].activate()
                    else:
                        self.log(
                            f"Missing window for {next_instance.get_name()}")

                    if self._options["obs_press_hotkey"]:
                        switch_key = str(next_ind + 1)
                        if self._options["obs_use_numpad"]:
                            switch_key = "numpad_" + switch_key
                        if self._options["obs_use_alt"]:
                            switch_key = "alt+" + switch_key
                        press_keys_for_time(switch_key.split("+"), 0.1)

                if not already_reset:
                    current_instance.reset(True, single_instance)

                if self._has_hidden:
                    self._has_hidden = False
                    for inst in self._mc_instances:
                        inst.get_window().move(
                            self._options["screen_location"], self._options["screen_size"])

                press_keys_for_time()

                if self._options["clipboard_on_reset"] != "":
                    clipboard.copy(self._options["clipboard_on_reset"])

        except:
            self.log("Error during reset: " +
                     traceback.format_exc().replace("\n", "\\n"))

    def _hide_hotkey_press(self) -> None:
        if not self._has_hidden:
            try:
                current_instance = get_current_mc_instance()
                if current_instance and current_instance in self._mc_instances:
                    self._has_hidden = True
                    for instance in self._mc_instances:
                        if instance != current_instance and instance.has_window(False):
                            instance.get_window().tiny()
            except Exception:
                self.log("Error during hiding: " +
                         traceback.format_exc().replace("\n", "\\n"))

    def _bg_reset_hotkey_press(self) -> None:
        if not self._has_hidden:
            try:
                current_instance = get_current_mc_instance()
                if current_instance and current_instance in self._mc_instances:
                    for instance in self._mc_instances:
                        if instance != current_instance and instance.has_window(False):
                            instance.reset()
            except Exception:
                self.log("Error during reset: " +
                         traceback.format_exc().replace("\n", "\\n"))

    def get_instance_infos(self) -> List[InstanceInfo]:
        return [
            InstanceInfo(
                instance.get_name(), instance.has_window(
                    True), instance.is_world_loaded(), instance.get_game_dir()
            ) for instance in self._mc_instances
        ]

    def reset_instance(self, instance_num: int) -> None:
        inst = self._mc_instances[instance_num]
        if inst.has_window():
            self._mc_instances[instance_num].reset()

    def activate_instance(self, instance_num: int) -> None:
        inst = self._mc_instances[instance_num]
        if inst.has_window():
            self._mc_instances[instance_num].activate()

    def tick(self) -> None:
        if self._tick_lock.locked():
            # Cancel tick if already being ran
            return
        with self._tick_lock:
            active_instance = get_current_mc_instance()
            if len(self._mc_instances) == 1:
                active_instance = self._mc_instances[0]
            for instance in self._mc_instances:
                instance.tick(instance == active_instance)


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")
