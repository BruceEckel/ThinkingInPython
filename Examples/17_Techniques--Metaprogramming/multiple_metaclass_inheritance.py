# multiple_metaclass_inheritance.py
from exceptions import ignore

class MetaA(type):
    pass

class MetaB(type):
    pass

class A(metaclass=MetaA):
    pass

class B(metaclass=MetaB):
    pass

with ignore(TypeError):
    class C(A, B):  # type: ignore
        pass
#: [TypeError] metaclass conflict: the metaclass of a
#: derived class must be a (non-strict) subclass of the
#: metaclasses of all its bases

class MetaC(MetaA, MetaB):
    pass

class D(A, B, metaclass=MetaC):
    pass

print(type(D).__name__)
#: MetaC
