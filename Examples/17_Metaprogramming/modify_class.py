# modify_class.py
from display import display_object

class Foo:
    pass

display_object(Foo)
#: [Attributes]
#:   None
#: [Methods]
#:   None

x = Foo()

Foo.n = 42  # type: ignore
display_object(Foo)
#: [Attributes]
#:   • n = 42 [CV]
#: [Methods]
#:   None

Foo.m = lambda self: f"{self.n = }"  # type: ignore
display_object(Foo)
#: [Attributes]
#:   • n = 42 [CV]
#: [Methods]
#:   • m(self)

print(x.m())  # type: ignore
#: self.n = 42
