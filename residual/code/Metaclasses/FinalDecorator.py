# Metaclasses/FinalDecorator.py

"""
class final(type):
    def __init__(cls, name, bases, namespace):
        super(final, cls).__init__(name, bases, namespace)
        for klass in bases:
            if isinstance(klass, final):
                raise TypeError(str(klass.__name__) + " is final")
"""
class Final(object): pass

def final(cls):
    cls.__bases__ += (Final,)
    print cls.__bases__
    def __init__(cls, name, bases, namespace):
        super(Final, cls).__init__(name, bases, namespace)
        for klass in bases:
            if isinstance(klass, Final):
                raise TypeError(str(klass.__name__) + " is Final")
    cls.__class__ = Final
    return cls

class A(object): pass

@final
class B(A): pass


# Produces compile-time error:
class C(B):
    pass

""" Output:
...
TypeError: B is final
"""
