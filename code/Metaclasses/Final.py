# Metaclasses/Final.py
# Emulating Java's 'final'

class final(type):
    def __init__(cls, name, bases, namespace):
        for klass in bases:
            if isinstance(klass, final):
                raise TypeError(str(klass.__name__) + " is final")
        super(final, cls).__init__(name, bases, namespace)

class A(object):
    pass

class B(A):
    __metaclass__= final

# Produces compile-time error:
class C(B):
    pass

""" Output:
...
TypeError: B is final
"""
