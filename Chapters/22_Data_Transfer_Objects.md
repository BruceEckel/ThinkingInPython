# Data Transfer Objects

The *Messenger* or *Data Transfer Object* is a way to pass a clump of information around.
The most typical place for this is in return values from functions,
where tuples or dictionaries often serve.
However, those rely on indexing.
A tuple requires the consumer to keep track of numerical order.
A `dict` requires the clumsier `d["name"]` syntax.

A Messenger is an object with attributes corresponding to the names of the data you pass or return:

```python
# messenger_idiom.py
from typing import Any

class Messenger:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__ = kwargs

m: Any = Messenger(info="Some information", b=["a", "list"])
m.more = 11
print(m.info, m.b, m.more)
#: Some information ['a', 'list'] 11
```

The trick here is assigning the object's `__dict__` to the `dict` that the `**kwargs` argument automatically creates.

You could create a `Messenger` class and put it in a library to import,
but there is no need: the standard library already ships this idiom,
as the next section shows.

Testing confirms the `Messenger` turns keyword arguments into attributes and takes new ones afterward:

```python
# test_messenger_idiom.py
from typing import Any
from messenger_idiom import Messenger

def test_messenger_exposes_kwargs_as_attributes() -> None:
    m: Any = Messenger(info="hi", count=3)
    assert m.info == "hi"
    assert m.count == 3
    m.added = 9  # Attributes can be added afterward, too
    assert m.added == 9
```

## The Standard-Library Versions

Python ships with this idiom.
`types.SimpleNamespace` is a `Messenger`,
with keyword arguments becoming attributes.
When you want the fields named and type-checked,
a `@dataclass` gives you a typed mutable record with a generated `__init__()`,
`__repr__()`, and equality, and a `NamedTuple` gives you a typed immutable one:

```python
# messenger_modern.py
from dataclasses import dataclass
from types import SimpleNamespace
from typing import NamedTuple

# SimpleNamespace is the Messenger idiom, built in:
m = SimpleNamespace(info="Some information", b=["a", "list"])
m.more = 11
print(m.info, m.b, m.more)
#: Some information ['a', 'list'] 11

# A dataclass is the typed, mutable version:
@dataclass
class Point:
    x: float
    y: float

print(Point(1.0, 2.0))
#: Point(x=1.0, y=2.0)

# A NamedTuple is the typed, immutable version:
class Color(NamedTuple):
    r: int
    g: int
    b: int

print(Color(255, 0, 0))
#: Color(r=255, g=0, b=0)
```

Use `SimpleNamespace` for an ad-hoc bag of attributes,
a `@dataclass` for a typed mutable record,
and a `NamedTuple` for a typed immutable one.
Write the hand-rolled `Messenger` only to show how `SimpleNamespace` works underneath.
To make a `@dataclass` guarantee that its values are legal, not merely typed,
see [Data Classes as Types](12_Data_Classes_as_Types.md#a-type-is-a-set-of-values).

This verifies that the `@dataclass` carries fields and value equality,
and the `NamedTuple` is a named record you can still treat as a tuple:

```python
# test_messenger_modern.py
from messenger_modern import Color, Point

def test_dataclass_point_has_fields_and_equality() -> None:
    assert Point(1.0, 2.0).x == 1.0
    assert Point(1.0, 2.0) == Point(1.0, 2.0)
    assert Point(1.0, 2.0) != Point(1.0, 3.0)

def test_namedtuple_color_is_a_named_record() -> None:
    c = Color(255, 0, 0)
    assert c.r == 255
    assert (c.r, c.g, c.b) == tuple(c)
```

`display_object()` shows that a `SimpleNamespace` keeps each keyword argument as an attribute:

```python
# display_namespace.py
from types import SimpleNamespace
from display import display_object

m = SimpleNamespace(info="Some information", b=["a", "list"])
m.more = 11
display_object(m)
#: [Attributes]
#:   • b = ['a', 'list']
#:   • info = 'Some information'
#:   • more = 11
#: [Methods]
#:   None
```

## Exercises

1.  In `messenger_idiom.py`,
    create a second `Messenger` with different keyword arguments and confirm the two instances do not share attributes (unlike a class attribute from [Class Attributes](09_Class_Attributes.md)).
2.  In `messenger_modern.py`, add a third field, `z: float`,
    to the `Point` dataclass,
    and update the `print(Point(1.0, 2.0))` call to pass three arguments.
3.  Add a `NamedTuple` called `Fraction` with fields `numerator: int` and `denominator: int` to `messenger_modern.py`,
    following `Color`'s shape,
    and confirm an instance still unpacks and indexes like a plain tuple.
4.  In `display_namespace.py`,
    add a fourth keyword argument to `m` when it is constructed instead of assigning `m.more` afterward,
    and confirm `display_object()` shows all four attributes,
    sorted alphabetically either way.
