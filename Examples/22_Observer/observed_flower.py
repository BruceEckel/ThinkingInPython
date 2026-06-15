# observed_flower.py
# Demonstration of "observer" pattern.
import sys

sys.path += ['../Util']
from observer import Observable, Observer  # type: ignore


class Flower:
    def __init__(self):
        self.isOpen = 0
        self.openNotifier = Flower.OpenNotifier(self)
        self.closeNotifier= Flower.CloseNotifier(self)
    def open(self): # Opens its petals
        self.isOpen = 1
        self.openNotifier.notify_observers()
        self.closeNotifier.open()
    def close(self): # Closes its petals
        self.isOpen = 0
        self.closeNotifier.notify_observers()
        self.openNotifier.close()
    def closing(self): return self.closeNotifier

    class OpenNotifier(Observable):
        def __init__(self, outer):
            Observable.__init__(self)
            self.outer = outer
            self.alreadyOpen = 0
        def notify_observers(self):
            if self.outer.isOpen and \
            not self.alreadyOpen:
                self.set_changed()
                Observable.notify_observers(self)
                self.alreadyOpen = 1
        def close(self):
            self.alreadyOpen = 0

    class CloseNotifier(Observable):
        def __init__(self, outer):
            Observable.__init__(self)
            self.outer = outer
            self.already_closed = 0
        def notify_observers(self):
            if not self.outer.isOpen and \
            not self.already_closed:
                self.set_changed()
                Observable.notify_observers(self)
                self.already_closed = 1
        def open(self):
            self.already_closed = 0

class Bee:
    def __init__(self, name):
        self.name = name
        self.openObserver = Bee.OpenObserver(self)
        self.closeObserver = Bee.CloseObserver(self)
    # An inner class for observing openings:
    class OpenObserver(Observer):
        def __init__(self, outer):
            self.outer = outer
        def update(self, observable, arg):
            print("Bee " + self.outer.name +
              "'s breakfast time!")
    # Another inner class for closings:
    class CloseObserver(Observer):
        def __init__(self, outer):
            self.outer = outer
        def update(self, observable, arg):
            print("Bee " + self.outer.name +
              "'s bed time!")

class Hummingbird:
    def __init__(self, name):
        self.name = name
        self.openObserver = \
          Hummingbird.OpenObserver(self)
        self.closeObserver = \
          Hummingbird.CloseObserver(self)
    class OpenObserver(Observer):
        def __init__(self, outer):
            self.outer = outer
        def update(self, observable, arg):
            print("Hummingbird " + self.outer.name + \
              "'s breakfast time!")
    class CloseObserver(Observer):
        def __init__(self, outer):
            self.outer = outer
        def update(self, observable, arg):
            print("Hummingbird " + self.outer.name + \
              "'s bed time!")

f = Flower()
ba = Bee("Eric")
bb = Bee("Eric 0.5")
ha = Hummingbird("A")
hb = Hummingbird("B")
f.openNotifier.add_observer(ha.openObserver)
f.openNotifier.add_observer(hb.openObserver)
f.openNotifier.add_observer(ba.openObserver)
f.openNotifier.add_observer(bb.openObserver)
f.closeNotifier.add_observer(ha.closeObserver)
f.closeNotifier.add_observer(hb.closeObserver)
f.closeNotifier.add_observer(ba.closeObserver)
f.closeNotifier.add_observer(bb.closeObserver)
# Hummingbird 2 decides to sleep in:
f.openNotifier.delete_observer(hb.openObserver)
# A change that interests observers:
f.open()
f.open() # It's already open, no change.
# Bee 1 doesn't want to go to bed:
f.closeNotifier.delete_observer(ba.closeObserver)
f.close()
f.close() # It's already closed; no change
f.openNotifier.delete_observers()
f.open()
f.close()
