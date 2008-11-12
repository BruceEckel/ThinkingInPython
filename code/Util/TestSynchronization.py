# Util/TestSynchronization.py
from Synchronization import *

# To use for a method:
class C(Synchronization):
    def __init__(self):
        Synchronization.__init__(self)
        self.data = 1
    def m(self):
        self.data += 1
        return self.data
    m = synchronized(m)
    def f(self): return 47
    def g(self): return 'spam'

# So m is synchronized, f and g are not.
c = C()

# On the class level:
class D(C):
    def __init__(self):
        C.__init__(self)
    # You must override an un-synchronized method
    # in order to synchronize it (just like Java):
    def f(self): C.f(self)

# Synchronize every (defined) method in the class:
synchronize(D)
d = D()
d.f() # Synchronized
d.g() # Not synchronized
d.m() # Synchronized (in the base class)

class E(C):
    def __init__(self):
        C.__init__(self)
    def m(self): C.m(self)
    def g(self): C.g(self)
    def f(self): C.f(self)
# Only synchronizes m and g. Note that m ends up
# being doubly-wrapped in synchronization, which
# doesn't hurt anything but is inefficient:
synchronize(E, 'm g')
e = E()
e.f()
e.g()
e.m()