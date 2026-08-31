# finalize_trap.py
import gc
from weakref import finalize, ref

class Leaky:
    def __init__(self, name: str) -> None:
        self.name = name
        # ty: missing-slot: typeshed's finalize lists no
        # slot for its writable atexit property:
        finalize(self, self.close).atexit = False  # type: ignore

    def close(self) -> None:
        print(self.name, "closed")

class Safe:
    def __init__(self, name: str) -> None:
        self.name = name
        finalize(self, print, name, "closed")

leaky, safe = ref(Leaky("L")), ref(Safe("S"))
gc.collect()
#: S closed
print(leaky() is None, safe() is None)
#: False True
