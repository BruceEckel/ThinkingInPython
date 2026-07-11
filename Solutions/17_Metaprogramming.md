# Metaprogramming: Solutions

## 1. Tracking leaves through two more generations

```python
# exercise_1.py
from typing import ClassVar

class Color:
    registry: ClassVar[set[type[Color]]] = set()

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Color.registry.add(cls)
        Color.registry -= set(cls.__bases__)

class Blue(Color):
    pass
class Red(Color):
    pass
class Green(Color):
    pass
class PhthaloBlue(Blue):
    pass
class CeruleanBlue(Blue):
    pass

class Yellow(Color):
    pass
print(sorted(c.__name__ for c in Color.registry))
#: ['CeruleanBlue', 'Green', 'PhthaloBlue', 'Red', 'Yellow']

class MutedYellow(Yellow):
    pass
print(sorted(c.__name__ for c in Color.registry))
#: ['CeruleanBlue', 'Green', 'MutedYellow', 'PhthaloBlue', 'Red']
```

Creating `Yellow` adds it to the registry; nothing removes it yet,
since `Color` (its only base) is never in the registry to begin with.
Creating `MutedYellow` adds *it* and removes its base, `Yellow`, the
same pruning `PhthaloBlue` and `CeruleanBlue` did to `Blue` earlier.
`__init_subclass__()` runs for every new subclass, so this addition
and removal happens automatically at each new generation, with no
change to `Color` needed.

## 2. A third `Field` descriptor

```python
# exercise_2.py
from typing import Any

class Field:
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name
        self.storage = "_" + name

    def __get__(self, obj: Any, owner: type | None = None) -> Any:
        if obj is None:
            return self
        return getattr(obj, self.storage)

    def __set__(self, obj: Any, value: Any) -> None:
        setattr(obj, self.storage, value)

class Point:
    x = Field()
    y = Field()
    z = Field()

p = Point()
p.x = 3
p.y = 4
p.z = 9
print(p.x, p.y, p.z)
#: 3 4 9
print(p.__dict__)
#: {'_x': 3, '_y': 4, '_z': 9}
```

`z = Field()` needs no change to the `Field` class itself.
`__set_name__()` runs once per descriptor, at class-creation time, and
Python calls it separately for each of `x`, `y`, and `z`, passing each
one its own attribute name. So `z`'s `Field` instance learns it is
named `"z"` and stores under `"_z"`, independently of the other two.

## 3. A third independent singleton class

```python
# exercise_3.py
from typing import Any, ClassVar

class Singleton(type):
    _instances: ClassVar[dict[type, Any]] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class ASingleton(metaclass=Singleton):
    pass
class CSingleton(metaclass=Singleton):
    pass

a = ASingleton()
c1 = CSingleton()
c2 = CSingleton()
print(c1 is c2)
#: True
print(c1 is a)
#: False
```

`Singleton._instances` is a dictionary keyed by the class itself, so
each class using the `Singleton` metaclass gets its own independent
slot: `ASingleton`'s single instance, `BSingleton`'s single instance
(omitted here, but present in the book), and now `CSingleton`'s.
Calling `CSingleton()` twice returns the same object both times, but
that object is unrelated to `ASingleton`'s instance, since they live
under different keys in the same dictionary.

## 4. A second, unrelated subclass of the non-final base

```python
# exercise_4.py
class A:
    pass

class B(A):
    def __init_subclass__(cls, **kwargs: object) -> None:
        raise TypeError(
            f"{B.__name__} is final; you cannot subclass it")

class D(A):
    pass
print(issubclass(D, A))
#: True
```

`B`'s `__init_subclass__()` only runs when something subclasses `B`
itself; it has no effect on `A`, which declares no such restriction.
`D(A)` is a plain, ordinary subclass of `A`, exactly like `B` was, and
it succeeds the same way `Ok(A)` does in `test_final.py`. Trying to
subclass `B`, on the other hand, still raises, because that
`__init_subclass__()` lives on `B` and runs for any class that
inherits from it.

## 5. A small `inspect`-based `describe()` helper

```python
# exercise_5.py
import inspect

def greet(name: str, loud: bool = False) -> str:
    "Return a greeting."
    text = f"Hello, {name}"
    return text.upper() if loud else text

def describe(func) -> None:
    doc = inspect.getdoc(func)
    sig = inspect.signature(func)
    print(func.__name__, sig, doc or "(no docstring)")

describe(greet)
#: greet (name: str, loud: bool = False) -> str Return a greeting.
describe(lambda x: x * 2)
#: <lambda> (x) (no docstring)
```

`inspect.getdoc()` returns `None` when a callable has no docstring, so
`doc or "(no docstring)"` supplies a fallback message instead of
printing `None`. A `lambda` always has a name, `"<lambda>"`, so
`func.__name__` works uniformly on both a `def`-based function and a
`lambda`, with no special case needed to tell them apart.
