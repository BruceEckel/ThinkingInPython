# exercise_4.py
from typing import ClassVar

class A:
    _final: ClassVar[set[type]] = set()

    def __init_subclass__(cls, final: bool = False,
                          **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        for base in cls.__mro__[1:]:
            if base in A._final:
                raise TypeError(
                    f"{base.__name__} is final;"
                    " you cannot subclass it")
        if final:
            A._final.add(cls)

class B(A, final=True):
    pass

class Open(A):  # A sibling that says nothing
    pass

class Sub(Open):
    pass
print(issubclass(Sub, A))
#: True

try:
    class C(B):
        pass
except TypeError as error:
    print(error)
#: B is final; you cannot subclass it
