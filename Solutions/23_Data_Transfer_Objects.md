# Data Transfer Objects: Solutions

## 1. Two `Messenger`s do not share attributes

```python
# exercise_1.py
from typing import Any

class Messenger:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__ = kwargs

m1: Any = Messenger(info="hi", count=3)
m2: Any = Messenger(name="Bob", age=30)
print(m1.info, m1.count)
#: hi 3
print(m2.name, m2.age)
#: Bob 30
print(hasattr(m1, "name"), hasattr(m2, "info"))
#: False False
```

Each `Messenger()` call assigns a fresh `dict` (the one `**kwargs`
built from that call's own arguments) to that instance's `__dict__`.
Every instance gets its own independent dictionary, unlike a class
attribute from [Class Attributes](09_Class_Attributes.md), which is
one object shared by every instance until something shadows it. `m1`
and `m2` share nothing: `m1` has no `name`, and `m2` has no `info`.

## 2. A third field on `Point`

```python
# exercise_2.py
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    z: float

print(Point(1.0, 2.0, 3.0))
#: Point(x=1.0, y=2.0, z=3.0)
```

`@dataclass` reads whatever fields the class body declares and
generates `__init__()` and `__repr__()` to match, so adding `z: float`
automatically extends the constructor to three positional arguments
and the `repr()` to three fields, with no other code to update.

## 3. A `NamedTuple` called `Fraction`

```python
# exercise_3.py
from typing import NamedTuple

class Fraction(NamedTuple):
    numerator: int
    denominator: int

f = Fraction(3, 4)
print(f)
#: Fraction(numerator=3, denominator=4)
print(f[0], f[1])
#: 3 4
num, denom = f
print(num, denom)
#: 3 4
```

`Fraction` behaves exactly like `Color` does: `f.numerator` and
`f.denominator` are readable by name, `f[0]` and `f[1]` still work
because a `NamedTuple` is still a real tuple underneath, and unpacking
with `num, denom = f` works the same way it would for a plain
`(3, 4)` tuple.

## 4. A fourth attribute supplied at construction

`display_object()` is the book's shared inspection helper, kept at the
tree root the same way `Examples/display.py` is, so any solution can
import it:

```python
# display.py
import inspect
from collections.abc import Sequence

def _annotations(cls: type) -> dict[str, object]:
    merged: dict[str, object] = {}
    for base in reversed(cls.__mro__):
        merged.update(inspect.get_annotations(base))
    return merged

def _type_name(annotation: object) -> str:
    if isinstance(annotation, type):
        return annotation.__name__
    return str(annotation)

def display_object(
    obj: object, dunder: Sequence[str] = (), max_width: int = 65
) -> None:
    cls = obj if inspect.isclass(obj) else type(obj)
    print(f"=== {cls.__name__} ===")
    annotations = _annotations(cls)
    attributes: list[str] = []
    methods: list[str] = []
    for name, value in inspect.getmembers_static(obj):
        is_dunder = name.startswith("__") and name.endswith("__")
        if is_dunder and name not in dunder:
            continue
        if callable(value):
            try:
                sig = str(inspect.signature(value))
            except (ValueError, TypeError):
                sig = "(...)"
            methods.append(f"  • {name}{sig}")
        else:
            label = name
            if name in annotations:
                label = f"{name}: {_type_name(annotations[name])}"
            val_str = repr(value)
            budget = max_width - len(label) - 7
            if len(val_str) > budget:
                val_str = val_str[:budget - 3] + "..."
            attributes.append(f"  • {label} = {val_str}")
    print("[Attributes]")
    print("\n".join(attributes) or "  None")
    print("[Methods]")
    print("\n".join(methods) or "  None")
```

```python
# exercise_4.py
from types import SimpleNamespace
from display import display_object

m = SimpleNamespace(info="Some information", b=["a", "list"],
                     more=11, extra="stuff")
display_object(m)
#: === SimpleNamespace ===
#: [Attributes]
#:   • b = ['a', 'list']
#:   • extra = 'stuff'
#:   • info = 'Some information'
#:   • more = 11
#: [Methods]
#:   None
```

`display_object()` shows all four attributes regardless of whether
they were passed as keyword arguments to the constructor or assigned
afterward, as `m.more = 11` did in the original. Both ways add an
entry to the instance's `__dict__`, which is all `display_object()`
reads. The listing is alphabetical either way, since `display_object()`
sorts by iterating `inspect.getmembers_static()`, which returns
members already sorted by name.
