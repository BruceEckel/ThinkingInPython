# finalize_trap.py
import gc
from weakref import finalize, ref

class Leaky:
    def __init__(self, name: str) -> None:
        self.name = name
        finalize(self, self.close).atexit = False

    def close(self) -> None:
        print(self.name, "closed")

class Safe:
    def __init__(self, name: str) -> None:
        self.name = name
        finalize(self, print, name, "closed")

leaky, safe = ref(Leaky("L")), ref(Safe("S"))
#: S closed
gc.collect()
print("Leaky alive:", leaky() is not None)
#: Leaky alive: True
print("Safe alive:", safe() is not None)
#: Safe alive: False
