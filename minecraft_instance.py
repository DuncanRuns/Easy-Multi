from window import *


class MinecraftInstance:
    def __init__(self, game_dir: str, window: Window = None) -> None:
        self._game_dir = game_dir
        self._window = window

        self._pause_on_wp = False
        self._pause_on_l = False

    def reset(self, pause_on_load: bool = True, use_f3: bool = True) -> None:
        pass

    def tick(self) -> None:
        pass
