# to_synch.py

import threading


class ToSynch:
    def __init__(self) -> None:
        self.mutex = threading.RLock()
        self.val = 1
    def a_synchronized_method(self) -> int:
        self.mutex.acquire()
        try:
            self.val += 1
            return self.val
        finally:
            self.mutex.release()
