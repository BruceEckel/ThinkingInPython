# modify_class.py
from display import display_object

class Clay:
    pass

display_object(Clay)
#: [Attributes]
#:   None
#: [Methods]
#:   None

x = Clay()
display_object(x)
#: [Attributes]
#:   None
#: [Methods]
#:   None

Clay.n = 42  # type: ignore
display_object(Clay)
#: [Attributes]
#:   • n = 42 [CV]
#: [Methods]
#:   None

Clay.m = lambda self: f"{self.n = }"  # type: ignore
display_object(Clay)
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

print(vars(x))
#: {}
