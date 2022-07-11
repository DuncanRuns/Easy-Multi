import threading
from logger import Logger
from minecraft_instance import MinecraftInstance, get_all_mc_instances
from easy_multi_options import EasyMultiOptions
from input_util import *

VERSION = "2.0.0-dev"


class EasyMulti:
    def __init__(self, options: EasyMultiOptions, logger: Logger) -> None:
        self._tick_lock = threading.Lock()
        self._mc_instances: List[MinecraftInstance] = []

        self._options = options
        self._logger = logger

    def log(self, line: str) -> None:
        self._logger.log(line, "EasyMulti")

    def _setup_instances(self) -> None:
        self._mc_instances = get_all_mc_instances()

    def tick(self) -> None:
        if self._tick_lock.locked():
            # Cancel tick if already being ran
            return
        with self._tick_lock:
            pass


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")
