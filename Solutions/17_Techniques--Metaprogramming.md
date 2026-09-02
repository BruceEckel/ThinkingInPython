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

class Gold(Yellow):
    pass
print(sorted(c.__name__ for c in Color.registry))
#: ['CeruleanBlue', 'Gold', 'Green', 'PhthaloBlue', 'Red']
```

Creating `Yellow` adds it to the registry. Nothing removes it yet,
since `Color` (its only base) is never in the registry to begin with.
Creating `Gold` adds *it* and removes its base, `Yellow`, the
same pruning `PhthaloBlue` and `CeruleanBlue` did to `Blue` earlier.
`__init_subclass__()` runs for every new subclass, so each new
generation adds itself and prunes its parent automatically, with no
edit to `Color`.

## 2. A third `Field` descriptor

```python
# exercise_2.py
from typing import Any

class Field:
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name
        self.storage = "_" + name

    def __get__(self, obj: Any,
                owner: type | None = None) -> Any:
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
`__set_name__()` runs once per descriptor, at class-creation time.
Python calls it separately for each of `x`, `y`, and `z`, passing each
one its own attribute name, so `z`'s `Field` instance learns the name
`"z"` and stores under `"_z"`, independently of the other two.

## 3. A third independent singleton class

```python
# exercise_3.py
from typing import Any, ClassVar

class Singleton(type):
    _instances: ClassVar[dict[type, Any]] = {}

    def __call__[T](
            cls: type[T], *args: Any, **kwargs: Any) -> T:
        if cls not in Singleton._instances:
            Singleton._instances[cls] = type.__call__(
                cls, *args, **kwargs)
        return Singleton._instances[cls]

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
Calling `CSingleton()` twice returns the same object both times.
`ASingleton` occupies its own key in that dictionary, so its instance
is a separate object.

The `__call__[T]` signature is the chapter's, and it is worth keeping
here rather than simplifying to `-> Any`. It ties the return type to
`cls`, so `CSingleton()` type-checks as a `CSingleton`, and `ty` still
flags a misspelled attribute on the result. Two details follow from
that annotation. `cls: type[T]` hides the fact that `cls` is a
`Singleton`, so the body writes `type.__call__(cls, ...)`, where a
type checker would reject a zero-argument `super()`. For the same
reason the body reads the cache through the class name,
`Singleton._instances`, rather than through `cls`.

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
the hook that `B`'s creation triggers. Declaring `final` with a
default, `final: bool = False`, lets every other subclass omit it. The
remaining `**kwargs` go on to `super().__init_subclass__()`, which
turns a misspelled keyword into a `TypeError` instead of a silent
no-op.

The chapter's `final_runtime.py` hard-codes the refusal into `B`'s own
`__init_subclass__()`. This version moves the decision into a set that
`A` owns, so the hook has to walk `cls.__mro__` to ask whether any
ancestor declared itself final. `Open` and `Sub` show that the rest of
the hierarchy still subclasses freely: the hook raises a `TypeError`
only for a class whose `__mro__` holds one of the classes in
`A._final`.

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
    print(func.__name__, sig)
    print(" ", doc or "(no docstring)")

describe(greet)
#: greet (name: str, loud: bool = False) -> str
#:   Return a greeting.
describe(lambda x: x * 2)
#: <lambda> (x)
#:   (no docstring)
```

`inspect.getdoc()` returns `None` when a callable has no docstring, so
`doc or "(no docstring)"` supplies a fallback message instead of
printing `None`. A `lambda` always has a name, `"<lambda>"`, so
`func.__name__` works uniformly on both a `def`-based function and a
`lambda`, with no special case needed to tell them apart.

## 6. The static diagnostic beside the runtime `TypeError`

Removing the `# type: ignore` from `metaclass_layout_conflict.py` leaves
the class header unsuppressed, inside the `try` the listing already has:

```python
try:
    class Singleton(type, dict[type, Any]):
        pass
except TypeError as e:
    print(e)
```

`uv run ty check metaclass_layout_conflict.py` then reports:

```text
error[instance-layout-conflict]: Class will raise `TypeError` at runtime
due to incompatible bases
 --> metaclass_layout_conflict.py:5:11
  |
5 |     class Singleton(type, dict[type, Any]):
  |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Bases `type` and `dict`
  |           cannot be combined in multiple inheritance
info: Two classes cannot coexist in a class's MRO if their instances
have incompatible memory layouts
  |
5 |     class Singleton(type, dict[type, Any]):
  |                     ----  --------------- `dict` instances have a
  |                     |                     distinct memory layout
  |                     |                     because of the way `dict`
  |                     |                     is implemented in a C
  |                     |                     extension
  |                     `type` instances have a distinct memory layout
  |                     because of the way `type` is implemented in a C
  |                     extension
```

Running the same file prints
`multiple bases have instance lay-out conflict`.

The diagnostic and the exception describe one collision. `ty`'s summary
line even names the consequence, "Class will raise `TypeError` at
runtime." Its `info` block explains the rule the interpreter enforces
without explaining: `type` and `dict` are both implemented in C, each
with its own instance layout, so no single object can be both. CPython
discovers that conflict while executing the `class` statement and
reports it as the terse "instance lay-out conflict." `ty` reaches the
same conclusion from the class header alone, before anything runs, and
points at both bases to say which pair is at fault.

That is the difference worth taking from this exercise. The runtime
message tells you something collided. The static one tells you which
two things collided and why, at the moment you type the header rather
than the moment the module is first imported. The `# type: ignore` is
in the chapter's version because this listing exists to show the
`TypeError`, and a suppressed diagnostic is the cost of demonstrating a
crash on purpose.

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

The three arguments are the name, the bases, and the namespace, the
same three a `class` statement assembles for you. A function defined
at module level becomes a method by landing in that namespace dict. It
needs no decoration, because a function is a descriptor: the attribute
lookup binds it to the instance.

`type(Celsius)` is `type` because this listing calls `type()` as a
constructor rather than subclassing it. Nothing here involves a
metaclass of your own. `Celsius` inherits `float`'s arithmetic, so
`c + 0.5` works, though the sum is a `float` rather than a `Celsius`:
`float.__add__()` builds its result from `float`, and that is why a
numeric subclass usually overrides every operator whose result it
wants to keep its own type.

`describe()` annotates `self` as `Any` because the type checker cannot
know that this loose function ends up on a class carrying a `unit`
attribute. That is the cost of building a class from data
rather than from a `class` statement.

## 8. Moving `bases += (Tag,)` into `__init__()`

The prediction: nothing happens. `Tag` stays out of `Demo.__bases__`,
and Python raises no error.

```python
# exercise_8.py
from typing import Any

class Tag:
    pass

class Meta(type):
    def __init__(cls, name: str, bases: tuple[type, ...],
                 nmspc: dict[str, Any]) -> None:
        # Rebinds a local name, nothing else
        bases += (Tag,)
        super().__init__(name, bases, nmspc)

class Demo(metaclass=Meta):
    pass

print(Demo.__bases__)
#: (<class 'object'>,)
print(Tag in Demo.__bases__)
#: False
```

By the time `__init__()` runs, the class object is complete. `type`
built it inside `__new__()`, using the bases the class header supplied
there, and laid out its `__mro__` from them. The `bases` parameter of
`__init__()` reports the tuple `__new__()` already used rather than
choosing a new one, so `bases += (Tag,)` rebinds a local name and
throws it away. Passing the longer tuple on to `type.__init__()`
changes nothing either, since `type.__init__()` only validates its
arguments.

`new_vs_init.py` makes the same point from the other side, with its
`added_in_init` key. `__new__()` has to make every decision about
*what the class is*: its name, its bases, and the namespace `type`
builds it from. `__init__()` can only modify the object that already
exists, which is why `setattr(cls, ...)` still works there.

## 9. Removing the `KNOWN_COMMANDS` check

```python
# ch17_exec_injection.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, cast

@dataclass
class Command:
    label: str

    def run(self) -> str:
        return f"Running {self.label}"

    @classmethod
    def make_class(
        cls, class_name: str
    ) -> Callable[[], Command]:
        # The KNOWN_COMMANDS check has been removed:
        klass = f"""
class {class_name}(Command):
    def __init__(self) -> None:
        super().__init__("{class_name}")
"""
        namespace: dict[str, Any] = {"Command": Command}
        exec(klass, namespace)
        return cast(Callable[[], Command],
                    namespace[class_name])

attack = (
    'X(Command):\n'
    '    pass\n'
    'print("injected code ran")\n'
    'Y = """  #'
)
try:
    Command.make_class(attack)
except KeyError:
    print("lookup failed, after the injection ran")
#: injected code ran
#: lookup failed, after the injection ran
```

`print("injected code ran")` is not part of any class body. It runs at
module level inside `exec()`, which is the whole point: a name that
reaches `make_class()` unchecked becomes source code, and source code
can do anything the program can do.

The payload needs a little care, because `make_class()` splices
`class_name` in twice. The first splice supplies the attack lines. The
second lands inside the `super().__init__("...")` string literal, where
a bare newline would be a `SyntaxError` before anything runs. So the
payload's last line opens a triple-quoted string, `Y = """`. That
string swallows the second splice, and the trailing `#` comments out
the `")` left over after it closes. The result compiles, and the
injected `print()` runs while `exec()` is executing the class body.

The `KeyError` afterward is incidental damage, not protection.
`namespace[class_name]` looks for a class named after the whole
payload, which was never defined. The injected statement already ran
before that lookup happened, so failing the lookup rescues nothing.
Restoring the `if class_name not in cls.KNOWN_COMMANDS` check closes
the hole at the only point that works: before `make_class()` builds
the string.

## 10. Keeping the first definition instead of raising an exception

```python
# ch17_keep_first.py
from typing import Any

class KeepFirst(dict[str, Any]):
    def __setitem__(self, key: str, value: Any) -> None:
        if key in self:
            return  # Discard the later definition
        super().__setitem__(key, value)

class First(type):
    @classmethod
    def __prepare__(cls, name: str, bases: tuple[type, ...],
                    **kwargs: Any) -> KeepFirst:
        return KeepFirst()

class Handlers(metaclass=First):
    def on_open(self) -> None:
        print("first on_open")
    def on_open(self) -> None:  # noqa: F811
        print("second on_open")

Handlers().on_open()
#: first on_open
```

`NoDuplicates` raised an exception on a repeated key. `KeepFirst`
returns instead, so Python builds the second `on_open` function, hands
it to `__setitem__()`, and the mapping discards it. The name still
refers to the first function when the body finishes, as
`Handlers().on_open()` proves.

No class decorator can keep the first definition, and neither can
`__init_subclass__()` or `__set_name__()`. All three receive the class
after its body has finished executing, and by then the body has run
`on_open = <second function>` as an ordinary assignment into the
namespace mapping. The first function has no name pointing at it and
no reference anywhere, so no later hook has anything to restore.
`__prepare__()` is the only hook that sees the assignments one at a
time, while they happen, and that is exactly why the chapter calls it
the one with no simpler substitute.
