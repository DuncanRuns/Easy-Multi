import threading
from minecraft_instance import MinecraftInstance, get_all_mc_instances
from easy_multi_options import EasyMultiOptions
from input_util import *


class EasyMulti:
    def __init__(self, options: EasyMultiOptions) -> None:
        self._tick_lock = threading.Lock()
        self._setup_instances()

    def _setup_instances(self) -> None:
        self.mc_instances = get_all_mc_instances()

    def tick(self) -> None:
        if self._tick_lock.locked():
            # Cancel tick if already being ran
            return
        with self._tick_lock:
            pass


if __name__ == "__main__":
    import os
    os.system("python EasyMulti.pyw")
