# facade.py
class A:
    def __init__(self, x: object) -> None: pass
class B:
    def __init__(self, x: object) -> None: pass
class C:
    def __init__(self, x: object) -> None: pass

# Other classes that aren't exposed by the
# facade go here ...

class Facade:
    @staticmethod
    def make_a(x: object) -> A:
        return A(x)

    @staticmethod
    def make_b(x: object) -> B:
        return B(x)

    @staticmethod
    def make_c(x: object) -> C:
        return C(x)

# The client programmer gets the objects
# by calling the static methods:
a = Facade.make_a(1)
b = Facade.make_b(1)
c = Facade.make_c(1.0)
