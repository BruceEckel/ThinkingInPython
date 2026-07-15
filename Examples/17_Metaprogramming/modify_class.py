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
display_object(x)
#: [Attributes]
#:   None
#: [Methods]
#:   None

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

display_object(x)
#: [Attributes]
#:   • n = 42 [CV]
#: [Methods]
#:   • m(self)
