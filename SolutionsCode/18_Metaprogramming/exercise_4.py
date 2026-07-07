# exercise_4.py
class A:
    pass

class B(A):
    def __init_subclass__(cls, **kwargs: object) -> None:
        raise TypeError(
            f"{B.__name__} is final; you cannot subclass it")

class D(A):
    pass
print(issubclass(D, A))
#: True
