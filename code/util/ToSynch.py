# util/ToSynch.py

import threading
class ToSynch:
    def __init__(self):
        self.mutex = threading.RLock()
        self.val = 1
    def aSynchronizedMethod(self):
        self.mutex.acquire()
        try:
            self.val += 1
            return self.val
        finally:
            self.mutex.release()