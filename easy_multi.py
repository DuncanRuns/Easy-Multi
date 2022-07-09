import threading
from minecraft_instance import MinecraftInstance, get_all_mc_instances
from easy_multi_options import EasyMultiOptions
from key_util import *


class EasyMulti:
    def __init__(self, options: EasyMultiOptions) -> None:
        self._tick_lock = threading.Lock()

    def tick(self) -> None:
        with self._tick_lock:
            pass
