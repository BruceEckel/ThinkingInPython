# Messenger

The *Messenger* or *Data Transfer Object* is a way to pass a clump of
information around. The most typical place for this is in return values
from functions, where tuples or dictionaries are often used. However,
those rely on indexing; in the case of tuples this requires the consumer
to keep track of numerical order, and in the case of a `dict` you must
use the `d["name"]` syntax which can be slightly less desirable.

A Messenger is simply an object with attributes corresponding to the
names of the data you want to pass around or return:

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

The trick here is that the `__dict__` for the object is just assigned to
the `dict` that is automatically created by the ``kwargs` argument.

Although one could easily create a `Messenger` class and put it into a
library and import it, there are so few lines to describe it that it
usually makes more sense to just define it in-place whenever you need it. It is probably easier for the reader to follow, as well.

## The Standard-Library Versions

You rarely need even those few lines, because Python already ships this idiom.
`types.SimpleNamespace` is exactly a `Messenger`: keyword arguments become
attributes. When you want the fields named and type-checked, a `@dataclass`
gives you a typed mutable record with a generated `__init__`, `repr`, and
equality, and a `NamedTuple` gives you a typed immutable one:

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

Reach for `SimpleNamespace` for an ad-hoc bag of attributes, a `@dataclass` for
a typed mutable record, and a `NamedTuple` for a typed immutable one. Write the
hand-rolled `Messenger` only to show how `SimpleNamespace` works underneath. To
make a `@dataclass` guarantee that its values are legal, not merely typed, see
[Data Classes as Types](05_Data_Classes_as_Types.md).
