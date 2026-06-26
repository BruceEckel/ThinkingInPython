# final_runtime.py
# Runtime finality with __init_subclass__, no metaclass required.

class A:
    pass

class B(A):
    # Any attempt to subclass it fails at class creation:
    def __init_subclass__(cls, **kwargs: object) -> None:
        raise TypeError(
            f"{B.__name__} is final; you cannot subclass it")

print(B.__bases__)
## (<class '__main__.A'>,)

try:
    class C(B):
        pass
except TypeError as error:
    print(error)
## B is final; you cannot subclass it
