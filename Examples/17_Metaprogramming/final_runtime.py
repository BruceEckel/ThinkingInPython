# final_runtime.py

class A:
    pass

class B(A):
    def __init_subclass__(cls, **kwargs: object) -> None:
        raise TypeError(
            f"{B.__name__} is final; you cannot subclass it")

try:
    class C(B):
        pass
except TypeError as error:
    print(error)
#: B is final; you cannot subclass it
