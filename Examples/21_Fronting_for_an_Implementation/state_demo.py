# state_demo.py
# Simple demonstration of the State pattern.

class StateD:
    def __init__(self, imp):
        self.__implementation = imp
    def change_imp(self, new_imp):
        self.__implementation = new_imp
    # Delegate calls to the implementation:
    def __getattr__(self, name):
        return getattr(self.__implementation, name)

class Implementation1:
    def f(self):
        print("Fiddle de dum, Fiddle de dee,")
    def g(self):
        print("Eric the half a bee.")
    def h(self):
        print("Ho ho ho, tee hee hee,")

class Implementation2:
    def f(self):
        print("We're Knights of the Round Table.")
    def g(self):
        print("We dance whene'er we're able.")
    def h(self):
        print("We do routines and chorus scenes")

def run(b):
    b.f()
    b.g()
    b.h()
    b.g()

b = StateD(Implementation1())
run(b)
b.change_imp(Implementation2())
run(b)
