# observer.py
# Class support for "observer" pattern.
from typing import Any

from synchronization import *


class Observer:
    def update(self, observable: Any, arg: Any) -> None:
        '''Called when the observed object is
        modified. You call an Observable object's
        notifyObservers method to notify all the
        object's observers of the change.'''
        pass

class Observable(Synchronization):
    def __init__(self) -> None:
        self.obs: list[Observer] = []
        self.changed = 0
        Synchronization.__init__(self)

    def addObserver(self, observer: Observer) -> None:
        if observer not in self.obs:
            self.obs.append(observer)

    def deleteObserver(self, observer: Observer) -> None:
        self.obs.remove(observer)

    def notifyObservers(self, arg: Any = None) -> None:
        '''If 'changed' indicates that this object
        has changed, notify all its observers, then
        call clearChanged(). Each observer has its
        update() called with two arguments: this
        observable object and the generic 'arg'.'''

        self.mutex.acquire()
        try:
            if not self.changed: return
            # Make a local copy in case of synchronous
            # additions of observers:
            localArray = self.obs[:]
            self.clearChanged()
        finally:
            self.mutex.release()
        # Updating is not required to be synchronized:
        for observer in localArray:
            observer.update(self, arg)

    def deleteObservers(self) -> None: self.obs = []
    def setChanged(self) -> None: self.changed = 1
    def clearChanged(self) -> None: self.changed = 0
    def hasChanged(self) -> int: return self.changed
    def countObservers(self) -> int: return len(self.obs)

synchronize(Observable,
  "addObserver deleteObserver deleteObservers " +
  "setChanged clearChanged hasChanged " +
  "countObservers")
