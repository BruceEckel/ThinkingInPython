# final_runtime.py
from exceptions import ignore

class A:
    pass

class B(A):
    def __init_subclass__(cls, **kwargs: object) -> None:
        raise TypeError(
            f"{B.__name__} is final; "
            f"you cannot subclass it")

with ignore(TypeError):
    class C(B):
        pass
#: [TypeError] B is final; you cannot subclass it
