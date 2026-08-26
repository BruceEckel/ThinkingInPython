# dunder_modes.py
from dataclasses import dataclass
from display import (
    INTERESTING_DUNDERS,
    REDEFINED_DUNDERS,
    display_object,
)

class Plain:
    pass

@dataclass
class Point:
    x: int
    y: int

display_object(Plain, INTERESTING_DUNDERS)
#: [Attributes]
#:   None
#: [Methods]
#:   • __eq__(self, value, /)
#:   • __hash__(self, /)
#:   • __init__(self, /, *args, **kwargs)
#:   • __repr__(self, /)

display_object(Plain, REDEFINED_DUNDERS)
#: [Attributes]
#:   None
#: [Methods]
#:   None

display_object(Point, REDEFINED_DUNDERS)
#: [Attributes]
#:   • __hash__ = None [CV]
#: [Methods]
#:   • __eq__(self, other)
#:   • __init__(self, x: int, y: int) -> None
#:   • __repr__(self)

display_object(Point, REDEFINED_DUNDERS,
               exclude=("__hash__",))
#: [Attributes]
#:   None
#: [Methods]
#:   • __eq__(self, other)
#:   • __init__(self, x: int, y: int) -> None
#:   • __repr__(self)
