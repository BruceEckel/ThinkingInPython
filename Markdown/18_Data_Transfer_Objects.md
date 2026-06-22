# Data Transfer Objects

The *Messenger* or *Data Transfer Object* is a way to pass a clump of information around.
The most typical place for this is in return values from functions,
where tuples or dictionaries are often used.
However, those rely on indexing;
in the case of tuples this requires the consumer to keep track of numerical order,
and in the case of a `dict` you must use the `d["name"]` syntax which can be slightly less desirable.

A Messenger is an object with attributes corresponding to the names of the data you want to pass around or return:

```python
# messenger_idiom.py
from typing import Any

class Messenger:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__ = kwargs

m: Any = Messenger(info="some information", b=['a', 'list'])
m.more = 11
print(m.info, m.b, m.more)
```

The trick here is that the `__dict__` for the object is just assigned to the `dict` that is automatically created by the `**kwargs` argument.

You could create a `Messenger` class and put it in a library to import.
But it takes so few lines that defining it in-place, wherever you need it,
usually makes more sense.

## The Standard-Library Versions

You rarely need even those few lines, because Python already ships this idiom.
`types.SimpleNamespace` is exactly a `Messenger`:
keyword arguments become attributes.
When you want the fields named and type-checked,
a `@dataclass` gives you a typed mutable record with a generated `__init__`,
`repr`, and equality, and a `NamedTuple` gives you a typed immutable one:

```python
# messenger_modern.py
# The standard library already provides this idiom and its typed
# cousins.
from dataclasses import dataclass
from types import SimpleNamespace
from typing import NamedTuple

# SimpleNamespace is exactly the Messenger idiom, built in:
m = SimpleNamespace(info="some information", b=["a", "list"])
m.more = 11
print(m.info, m.b, m.more)

# A dataclass is the typed, mutable version:
@dataclass
class Point:
    x: float
    y: float

print(Point(1.0, 2.0))

# A NamedTuple is the typed, immutable version:
class Color(NamedTuple):
    r: int
    g: int
    b: int

print(Color(255, 0, 0).r)
```

Use `SimpleNamespace` for an ad-hoc bag of attributes,
a `@dataclass` for a typed mutable record,
and a `NamedTuple` for a typed immutable one.
Write the hand-rolled `Messenger` only to show how `SimpleNamespace` works underneath.
To make a `@dataclass` guarantee that its values are legal, not merely typed,
see [Data Classes as Types](10_Data_Classes_as_Types.md).

A small test confirms each form behaves as a record:
the hand-rolled `Messenger` turns keyword arguments into attributes (and takes new ones later),
the `@dataclass` carries fields and value equality,
and the `NamedTuple` is a named record you can still treat as a tuple:

```python
# test_messenger.py
from typing import Any
from messenger_idiom import Messenger
from messenger_modern import Color, Point

def test_messenger_exposes_kwargs_as_attributes() -> None:
    m: Any = Messenger(info="hi", count=3)
    assert m.info == "hi"
    assert m.count == 3
    m.added = 9  # Attributes can be added afterward, too
    assert m.added == 9

def test_dataclass_point_has_fields_and_equality() -> None:
    assert Point(1.0, 2.0).x == 1.0
    assert Point(1.0, 2.0) == Point(1.0, 2.0)
    assert Point(1.0, 2.0) != Point(1.0, 3.0)

def test_namedtuple_color_is_a_named_record() -> None:
    c = Color(255, 0, 0)
    assert c.r == 255
    assert (c.r, c.g, c.b) == tuple(c)
```
