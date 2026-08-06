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

## 4. Declaring finality with a keyword in the class header

```python
# exercise_4.py
from typing import ClassVar

class A:
    _final: ClassVar[set[type]] = set()

    def __init_subclass__(cls, final: bool = False,
                          **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        for base in cls.__mro__[1:]:
            if base in A._final:
                raise TypeError(
                    f"{base.__name__} is final;"
                    " you cannot subclass it")
        if final:
            A._final.add(cls)

class B(A, final=True):
    pass

class Open(A):  # A sibling that says nothing
    pass

class Sub(Open):
    pass
print(issubclass(Sub, A))
#: True

try:
    class C(B):
        pass
except TypeError as error:
    print(error)
#: B is final; you cannot subclass it
```

The keywords in a class header travel to `__init_subclass__()`, so
`final=True` in `class B(A, final=True):` arrives as a parameter of
the hook that `B`'s creation triggers. Declaring it with a default,
`final: bool = False`, lets every other subclass omit it. The
remaining `**kwargs` go on to `super().__init_subclass__()`, which is
what turns a misspelled keyword into a `TypeError` instead of a silent
no-op.

The chapter's `final_runtime.py` hard-codes the refusal into `B`'s own
`__init_subclass__()`. This version moves the decision into a set that
`A` owns, so the hook has to walk `cls.__mro__` to ask whether any
ancestor declared itself final. `Open` and `Sub` show that the rest of
the hierarchy is unaffected: only the classes named in `A._final`
refuse to be subclassed.

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

## 7. Building a `float` subclass with `type()`

```python
# exercise_7.py
from typing import Any

def describe(self: Any) -> str:
    return f"{self} degrees {self.unit}"

Celsius = type("Celsius", (float,),
               {"unit": "C", "describe": describe})

c = Celsius(21.5)
print(c.describe())
#: 21.5 degrees C
print(type(Celsius) is type)
#: True
print(c + 0.5, isinstance(c, float))
#: 22.0 True
```

The three arguments are the name, the bases, and the namespace, which
is what a `class` statement assembles for you. A function defined at
module level becomes a method by landing in that namespace dict: no
decoration is needed, since a function is a descriptor and binding
happens on lookup.

`type(Celsius)` is `type` because `type()` was called as a
constructor, not subclassed. Nothing here involves a metaclass of your
own. `Celsius` inherits `float`'s arithmetic, so `c + 0.5` works,
though it returns a `float` rather than a `Celsius`: `float.__add__()`
builds its result from `float`, which is the usual reason a numeric
subclass also overrides the operators it wants to keep its own type.

`describe()` annotates `self` as `Any` because the type checker has no
way to know that this loose function will end up on a class carrying a
`unit` attribute. That is the cost of building a class from data
rather than from a `class` statement.

## 8. Moving `bases += (Tag,)` into `__init__()`

The prediction: nothing happens. The base is not added, and no error
is reported either.

```python
# exercise_8.py
from typing import Any

class Tag:
    pass

class Meta(type):
    def __init__(cls, name: str, bases: tuple[type, ...],
                 nmspc: dict[str, Any]) -> None:
        bases += (Tag,)  # Rebinds a local name, nothing else
        super().__init__(name, bases, nmspc)

class Demo(metaclass=Meta):
    pass

print(Demo.__bases__)
#: (<class 'object'>,)
print(Tag in Demo.__bases__)
#: False
```

By the time `__init__()` runs, the class object is finished. `type`
built it inside `__new__()`, using the bases it was given there, and
laid out its `__mro__` from them. The `bases` parameter of `__init__()`
is a tuple that describes what was used, not a control that decides
what will be used, so `bases += (Tag,)` rebinds a local name and
throws it away. Passing the longer tuple on to `type.__init__()`
changes nothing either, since `type.__init__()` only validates its
arguments.

This is the same lesson `added_in_init` teaches in `new_vs_init.py`,
seen from the other side. Anything that decides *what the class is*,
its name, its bases, or the namespace it is built from, has to happen
in `__new__()`. `__init__()` can only modify the object that already
exists, which is why `setattr(cls, ...)` still works there.
