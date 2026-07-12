# demo_display_object.py
from dataclasses import dataclass
from display import ALL_DUNDERS, display_object

@dataclass
class Fraggle:
    """A small dataclass for the demo."""
    x: int
    y: float = 1.14659
    z: str = "blivet"

    def f(self) -> None: ...
    def g(self, x: int) -> float:
        return 0.001
    def h(self, s: str) -> str:
        return f"h({s})"

display_object(Fraggle)  # Display the class
#: [Attributes]
#:   • y: float = 1.14659 [CV]
#:   • z: str = 'blivet' [CV]
#: [Methods]
#:   • f(self) -> None
#:   • g(self, x: int) -> float
#:   • h(self, s: str) -> str

# Display a specific instance:
display_object(Fraggle(9, 2.3))
#: [Attributes]
#:   • x: int = 9
#:   • y: float = 2.3
#:   • z: str = 'blivet'
#: [Methods]
#:   • f(self) -> None
#:   • g(self, x: int) -> float
#:   • h(self, s: str) -> str

# ALL_DUNDERS also reveals what @dataclass generated:
display_object(Fraggle(9, 2.3), dunder=ALL_DUNDERS)
#: [Attributes]
#:   • __annotations_cache__ = {'x': <class 'int'>, 'y': <cl... [CV]
#:   • __class__ = <attribute '__class__'> [CV]
#:   • __dataclass_fields__ = {'x': Field(name='x',type=<cla... [CV]
#:   • __dataclass_params__ = _DataclassParams(init=True,rep... [CV]
#:   • __dict__ = <attribute '__dict__'> [CV]
#:   • __doc__ = 'A small dataclass for the demo.' [CV]
#:   • __firstlineno__ = 5 [CV]
#:   • __hash__ = None [CV]
#:   • __match_args__ = ('x', 'y', 'z') [CV]
#:   • __module__ = '__main__' [CV]
#:   • __static_attributes__ = () [CV]
#:   • __weakref__ = <attribute '__weakref__'> [CV]
#:   • x: int = 9
#:   • y: float = 2.3
#:   • z: str = 'blivet'
#: [Methods]
#:   • __annotate_func__(format, /)
#:   • __delattr__(self, name, /)
#:   • __dir__(self, /)
#:   • __eq__(self, other)
#:   • __format__(self, format_spec, /)
#:   • __ge__(self, value, /)
#:   • __getattribute__(self, name, /)
#:   • __getstate__(self, /)
#:   • __gt__(self, value, /)
#:   • __init__(self, x: int, y: float = 1.14659, z: str = 'blive...
#:   • __init_subclass__(type, /)
#:   • __le__(self, value, /)
#:   • __lt__(self, value, /)
#:   • __ne__(self, value, /)
#:   • __new__(*args, **kwargs)
#:   • __reduce__(self, /)
#:   • __reduce_ex__(self, protocol, /)
#:   • __replace__(self, /, **changes)
#:   • __repr__(self)
#:   • __setattr__(self, name, value, /)
#:   • __sizeof__(self, /)
#:   • __str__(self, /)
#:   • __subclasshook__(type, object, /)
#:   • f(self) -> None
#:   • g(self, x: int) -> float
#:   • h(self, s: str) -> str
