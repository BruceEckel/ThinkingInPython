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
Clay.n = 42  # type: ignore
Clay.m = lambda self: f"{self.n = }"  # type: ignore
display_object(x)
#: [Attributes]
#:   • n = 42 [CV]
#: [Methods]
#:   • m(self)
print(x.m())  # type: ignore
#: self.n = 42
print(vars(x))
#: {}
