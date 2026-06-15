# synchronization.py
'''Simple emulation of Java's 'synchronized'
keyword, from Peter Norvig.'''
import threading
from collections.abc import Callable
from typing import Any


def synchronized(method: Callable[..., Any]) -> Callable[..., Any]:
    def f(*args: Any) -> Any:
        self = args[0]
        self.mutex.acquire()
        # print(method.__name__, 'acquired')
        try:
            return method(*args)
        finally:
            self.mutex.release()
            # print(method.__name__, 'released')
    return f

def synchronize(klass: type, names: str | None = None) -> None:
    """Synchronize methods in the given class.
    Only synchronize the methods whose names are
    given, or all methods if names=None."""
    selected = names.split() if names is not None else None
    for (name, val) in list(klass.__dict__.items()):
        if callable(val) and name != '__init__' and \
          (selected is None or name in selected):
            # print("synchronizing", name)
            setattr(klass, name, synchronized(val))

# You can create your own self.mutex, or inherit
# from this class:
class Synchronization:
    def __init__(self) -> None:
        self.mutex = threading.RLock()
