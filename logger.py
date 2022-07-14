import threading, os, easy_multi_options, time
from typing import Callable, List

_time_started = int(time.time())


class Logger:
    def __init__(self) -> None:
        self._location: str = get_location()
        self._location_latest: str = get_location_latest()
        self._callbacks: List[Callable[[str], None]] = []
        self._log_lock = threading.Lock()
        if os.path.exists(self._location_latest):
            os.remove(self._location_latest)

    def add_callback(self, callback: Callable[[str], None]) -> None:
        self._callbacks.append(callback)

    def log(self, line: str, source: str = None) -> None:
        threading.Thread(target=self._log_thread, args=(line, source)).start()

    def _log_thread(self, line: str, source: str = None) -> None:
        if source:
            line = f"[{source}] {line}"
        with self._log_lock:
            for location in [self._location, self._location_latest]:
                with open(location, "a") as log_file:
                    current_time = time.strftime("%H:%M:%S", time.localtime())
                    log_file.write(f"[{current_time}] {line}\n")
            for callback in self._callbacks:
                callback(line)


class PrintLogger(Logger):
    """Logger which defaults to printing the log rather than outputting to a file.
    """

    def __init__(self) -> None:
        self._callbacks: List[Callable[[str], None]] = []
        self._log_lock = threading.Lock()
        self.add_callback(print)

    def _log_thread(self, line: str, source: str = None) -> None:
        if source:
            line = f"[{source}] {line}"
        with self._log_lock:
            for callback in self._callbacks:
                callback(line)


def get_or_create_folder() -> str:
    fol = os.path.join(easy_multi_options.get_or_create_folder(), "logs")
    if not os.path.isdir(fol):
        os.mkdir(fol)
    return fol


def get_location() -> str:
    return os.path.join(get_or_create_folder(), f"log_{_time_started}.txt")


def get_location_latest() -> str:
    return os.path.join(get_or_create_folder(), "log_latest.txt")


if __name__ == "__main__":
    logger = Logger()
    logger.add_callback(print)
    logger.log("hello mario", "test")
    logger.log("hello", "test")
    time.sleep(1)
    logger.log("luigi", "test")
