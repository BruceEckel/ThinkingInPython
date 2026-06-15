# Final.py
# Preventing inheritance with __init_subclass__, no metaclass
# required.


class A:
    pass


class B(A):
    # Make B final: any attempt to subclass it fails at class
    # creation.
    def __init_subclass__(cls, **kwargs: object) -> None:
        raise TypeError(
            f"{B.__name__} is final; you cannot subclass it")


print(B.__bases__)

try:
    class C(B):
        pass
except TypeError as error:
    print(error)

""" Output:
(<class '__main__.A'>,)
B is final; you cannot subclass it
"""
