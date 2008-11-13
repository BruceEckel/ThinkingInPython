# ChangeInterface/Facade.py
class A:
    def __init__(self, x): pass
class B:
    def __init__(self, x): pass
class C:
    def __init__(self, x): pass

# Other classes that aren't exposed by the
# facade go here ...

class Facade:
    def makeA(x): return A(x)
    makeA = staticmethod(makeA)
    def makeB(x): return B(x)
    makeB = staticmethod(makeB)
    def makeC(x): return C(x)
    makeC = staticmethod(makeC)

# The client programmer gets the objects
# by calling the static methods:
a = Facade.makeA(1);
b = Facade.makeB(1);
c = Facade.makeC(1.0);