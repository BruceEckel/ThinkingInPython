# observer.py
from typing import Any

class Observer:
    def update(self, observable: Any, arg: Any, /) -> None:
        "Called when the observed object changes."

class Observable:
    def __init__(self) -> None:
        self.observers: list[Observer] = []
        self.changed = False

    def add_observer(self, observer: Observer) -> None:
        if observer not in self.observers:
            self.observers.append(observer)

    def delete_observer(self, observer: Observer) -> None:
        self.observers.remove(observer)

    def set_changed(self) -> None:
        self.changed = True

    def notify_observers(self, arg: Any = None) -> None:
        if not self.changed:
            return
        self.changed = False
        for observer in list(self.observers):
            observer.update(self, arg)
