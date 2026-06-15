# observer.py
# Class support for "observer" pattern.
from typing import Any

from synchronization import Synchronization, synchronize


class Observer:
    def update(self, observable: Any, arg: Any) -> None:
        '''Called when the observed object is
        modified. You call an Observable object's
        notify_observers method to notify all the
        object's observers of the change.'''
        pass

class Observable(Synchronization):
    def __init__(self) -> None:
        self.obs: list[Observer] = []
        self.changed = 0
        Synchronization.__init__(self)

    def add_observer(self, observer: Observer) -> None:
        if observer not in self.obs:
            self.obs.append(observer)

    def delete_observer(self, observer: Observer) -> None:
        self.obs.remove(observer)

    def notify_observers(self, arg: Any = None) -> None:
        '''If 'changed' indicates that this object
        has changed, notify all its observers, then
        call clear_changed(). Each observer has its
        update() called with two arguments: this
        observable object and the generic 'arg'.'''

        self.mutex.acquire()
        try:
            if not self.changed:
                return
            # Make a local copy in case of synchronous
            # additions of observers:
            local_array = self.obs[:]
            self.clear_changed()
        finally:
            self.mutex.release()
        # Updating is not required to be synchronized:
        for observer in local_array:
            observer.update(self, arg)

    def delete_observers(self) -> None: self.obs = []
    def set_changed(self) -> None: self.changed = 1
    def clear_changed(self) -> None: self.changed = 0
    def has_changed(self) -> int: return self.changed
    def count_observers(self) -> int: return len(self.obs)

synchronize(Observable,
  "add_observer delete_observer delete_observers " +
  "set_changed clear_changed has_changed " +
  "count_observers")
