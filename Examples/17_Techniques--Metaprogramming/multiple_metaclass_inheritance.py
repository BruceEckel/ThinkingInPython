# multiple_metaclass_inheritance.py
class MetaA(type):
    pass

class MetaB(type):
    pass

class A(metaclass=MetaA):
    pass

class B(metaclass=MetaB):
    pass

try:
    class C(A, B):  # type: ignore
        pass
except TypeError as error:
    print(type(error).__name__)
#: TypeError
