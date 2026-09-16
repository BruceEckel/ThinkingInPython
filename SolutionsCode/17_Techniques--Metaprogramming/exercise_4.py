# exercise_4.py
from typing import ClassVar
from exceptions import ignore

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

with ignore(TypeError):
    class C(B):
        pass
#: TypeError('B is final; you cannot subclass it')
