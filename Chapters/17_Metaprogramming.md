# Metaprogramming

Objects are created by other (special) objects.
These special objects are called *classes* and we configure them to produce desired objects.

So, classes are themselves objects.
We can modify objects:

```python
# modify_class.py
from display import display_object

class Foo:
    pass

display_object(Foo)
#: [Attributes]
#:   None
#: [Methods]
#:   None

x = Foo()
display_object(x)
#: [Attributes]
#:   None
#: [Methods]
#:   None

Foo.n = 42  # type: ignore
display_object(Foo)
#: [Attributes]
#:   • n = 42 [CV]
#: [Methods]
#:   None

Foo.m = lambda self: f"{self.n = }"  # type: ignore
display_object(Foo)
#: [Attributes]
#:   • n = 42 [CV]
#: [Methods]
#:   • m(self)

print(x.m())  # type: ignore
#: self.n = 42

display_object(x)
#: [Attributes]
#:   • n = 42 [CV]
#: [Methods]
#:   • m(self)
```

Note that `x` is modified by the changes made to the class *after* `x` was created.
A change to a class affects every object of that class,
even ones already created.

What creates these "class" objects?
Other special objects, called *metaclasses*.
The default metaclass is `type`,
and in the vast majority of cases it does the right thing.
You can customize how Python produces classes by running extra code or injecting members as it builds each class.
That is metaclass programming.

Most of the time you do not need a metaclass.
It is a fascinating tool, and the temptation to use it is strong,
but Python 3 added simpler hooks that cover almost every case a metaclass used to handle:

- `__init_subclass__()` runs at subclass creation.
  It replaces most "do something each time a class is defined" metaclasses.
- `__set_name__()` lets a descriptor learn its attribute name,
  at class-creation time.
- *Class decorators* transform a class after Python builds it.

Use a metaclass only when these cannot do the job.
This chapter shows the simpler tools first,
then metaclasses for situations that still need them.

## Generating Classes with `type`

Since metaclasses create classes, you can call the metaclass yourself.
`type` with one argument gives the type of an existing object.
`type` with three arguments creates a new class.
These arguments are the name, a tuple of base classes,
and a namespace dictionary of fields and methods.
A class definition is shorthand for calling `type`:

```python
# class_via_type.py
class C:
    pass

D = type("D", (), {})  # The same construction, by hand

print(type(C), type(D))
#: <class 'type'> <class 'type'>
# Both inherit object:
print(C.__bases__, D.__bases__)
#: (<class 'object'>,) (<class 'object'>,)
# Both make ordinary instances:
print(isinstance(C(), C), isinstance(D(), D))
#: True True
```

You can add bases, fields, and methods the same way:

```python
# my_list.py
from display import display_object

def howdy(self, you: str) -> None:
    print(f"Howdy, {you}")

MyList = type("MyList", (list,), dict(x=42, howdy=howdy))

display_object(MyList)
#: [Attributes]
#:   • x = 42 [CV]
#: [Methods]
#:   • append(self, object, /)
#:   • clear(self, /)
#:   • copy(self, /)
#:   • count(self, value, /)
#:   • extend(self, iterable, /)
#:   • howdy(self, you: str) -> None
#:   • index(self, value, start=0, stop=9223372036854775807, /)
#:   • insert(self, index, object, /)
#:   • pop(self, index=-1, /)
#:   • remove(self, value, /)
#:   • reverse(self, /)
#:   • sort(self, /, *, key=None, reverse=False)

ml = MyList()
ml.append("Camembert")
print(ml)
#: ['Camembert']
print(ml.x)
#: 42
ml.howdy("John")
#: Howdy, John

print(ml.__class__.__class__)
#: <class 'type'>
```

Because `MyList` inherits `list`, it gets all the methods from `list`.

Printing the class of the class produces the metaclass.

Generating classes programmatically with `type` creates possibilities.
For example, where you might otherwise write many near-identical subclasses by hand,
you can instead generate them dynamically:

```python
# greenhouse.py
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, cast

type EventMaker = Callable[[int, int], Event]
NOT_CREATED: EventMaker = cast(EventMaker, sentinel("NOT_CREATED"))

@dataclass
class Event:
    action: str
    hour: int
    minute: int
    events: ClassVar[list[Event]] = []  # Registry of all Events
    event_makers: ClassVar[dict[str, EventMaker]] = {
        name : NOT_CREATED  # Dict key : value pair
        for name in (
            "ThermostatDay", "ThermostatNight",
            "LightOn", "LightOff",
            "WaterOn", "WaterOff",
            "RingBell",
        )
    }

    def __post_init__(self) -> None:
        Event.events.append(self)

    @classmethod
    def load_schedule(cls, path: Path) -> None:
        lines = [
            line for line in path.read_text().splitlines()
            if line.strip() and not line.startswith("#")
        ]
        for line in lines:
            class_name, hour, minute = (
                line.replace(":", " ").split())
            cls._class_for(class_name)(int(hour), int(minute))

    @classmethod
    def _class_for(cls, class_name: str) -> EventMaker:
        if class_name not in cls.event_makers:
            raise ValueError(f"Unknown event class: {class_name!r}")
        if cls.event_makers[class_name] is NOT_CREATED:
            print(f"Creating {class_name}")
            def init(self: Event, hour: int, minute: int) -> None:
                Event.__init__(self, class_name, hour, minute)
            new_cls = type(class_name, (Event,), {"__init__": init})
            cls.event_makers[class_name] = cast(EventMaker, new_cls)
        return cls.event_makers[class_name]

    @staticmethod
    def run_events() -> None:
        for e in sorted(
                Event.events, key=lambda e: (e.hour, e.minute)):
            print(f"{e.hour}:{e.minute:02d}: {e.action}")

if __name__ == "__main__":
    Event.load_schedule(Path("schedule.txt"))
    Event.run_events()
#: Creating ThermostatNight
#: Creating LightOff
#: Creating WaterOn
#: Creating WaterOff
#: Creating LightOn
#: Creating RingBell
#: Creating ThermostatDay
#: 1:00: LightOn
#: 2:00: LightOff
#: 3:30: WaterOn
#: 4:45: WaterOff
#: 5:00: ThermostatNight
#: 6:00: ThermostatDay
#: 7:00: RingBell
#: 8:00: LightOn
```

Now the end user only needs to write and maintain the file containing the schedule:

```text
# schedule.txt
ThermostatNight 5:00
LightOff 2:00
WaterOn 3:30
WaterOff 4:45
LightOn 1:00
RingBell 7:00
ThermostatDay 6:00
LightOn 8:00
```

`load_schedule()` reads that file, filtering out blank lines and comments,
then builds an `Event` from each surviving line.
`line.replace(":", " ").split()` turns `"WaterOn 3:30"` into three plain strings in one step,
by replacing the colon with a second space before splitting on whitespace.
`_class_for()` gets the class object used to build that `Event`.
The first time an event type is actually needed,
the class is built and registered under its name.

`Event.event_makers` comes pre-populated with the seven legitimate event names,
each paired with the `NOT_CREATED` sentinel as a placeholder.
Populating that dict does not build any classes.
It only reserves the names,
so `_class_for()` has something to check a `class_name` against before building anything.

`_class_for()` calls `Event.__init__(self, ...)` directly instead of `super().__init__(...)`.
`init()` is a nested function, not a method defined inside a `class` statement,
so the compiler never gives it the `__class__` cell that zero-argument `super()` needs.

## Generating Classes with `exec()`

The `type` approach in the previous section builds a class from a name,
a tuple of bases, and a namespace dict.
`exec()` offers a second way:
write the class as an ordinary `class` statement inside an f-string,
then run that string as code.
The generated source reads like a class definition, because it is one:

```python
# commander.py
from collections.abc import Callable
from typing import ClassVar, cast
from exceptions import ignore

class Command:
    KNOWN_COMMANDS: ClassVar[set[str]] = {"Start", "Stop", "Pause"}

    def __init__(self, label: str) -> None:
        self.label = label

    def run(self) -> str:
        return f"Running {self.label}"

    @classmethod
    def make_class(cls, class_name: str) -> Callable[[], Command]:
        if class_name not in cls.KNOWN_COMMANDS:
            raise ValueError(f"Unknown command: {class_name!r}")
        klass = f"""
class {class_name}(Command):
    def __init__(self) -> None:
        super().__init__("{class_name}")
"""
        namespace: dict[str, type[Command]] = {"Command": Command}
        exec(klass, namespace)
        return cast(Callable[[], Command], namespace[class_name])

if __name__ == "__main__":
    for name in ("Start", "Stop", "Pause"):
        command_class = Command.make_class(name)
        print(command_class().run())
    with ignore(ValueError):
        Command.make_class("Reset")
#: Running Start
#: Running Stop
#: Running Pause
#: ValueError("Unknown command: 'Reset'")
```

`make_class()` execs `klass` into a private `namespace` dict,
seeded with `{"Command": Command}` so the generated class's own reference to `Command` resolves.
Nothing is written into the real module namespace
([`globals()`](06_Modules_and_Packages.md), covered when modules are introduced):
`namespace[class_name]` is the only way to reach the class afterward.
The checker only knows `Command`'s own `__init__(self, label)`,
not that the generated subclass replaces it with a no-argument `__init__`,
so `cast(Callable[[], Command], ...)` records the narrower,
actual signature at the one place the class is created,
the same idiom [Generating Classes with `type`](#generating-classes-with-type)
uses for `EventMaker`.

Notice `super().__init__(...)` inside the generated class, working normally.
Unlike `_class_for()`'s `init()`,
defined as a nested function and never given a `__class__` cell,
this `__init__` is a method defined inside a real `class` statement,
even though that statement arrived as a string.
The compiler doesn't distinguish where the source text came from,
only whether the method is textually inside a `class` block.

`exec()` runs its string as Python code with the full power of the language:
imports, file access, network calls, anything.
A string built from untrusted input,
such as a web form or a file another user uploaded,
would hand an attacker that same access.

`Command.KNOWN_COMMANDS` is what keeps `make_class()` safe.
It checks `class_name` before doing anything with it,
and raises `ValueError` for any name that isn't `"Start"`, `"Stop"`,
or `"Pause"`.
An unrecognized name gets rejected, not executed.

That check matters for a sharper reason than just rejecting nonsense.
`klass` splices `class_name` directly into class-definition source text before handing it to `exec()`.
An unvalidated `class_name` containing a newline and a second statement could break out of the intended `class` block and run arbitrary code there,
the same way an unescaped string breaks out of a hand-built SQL query.
`_class_for()`, back in [Generating Classes with `type`](#generating-classes-with-type),
never has this risk:
`type(class_name, (Event,), ...)` always treats `class_name` as a plain string value,
never as source code to parse.
Building a class from a string template and validating what gets spliced into it are two different concerns,
and skipping the second one is exactly how this kind of vulnerability gets shipped.

Treat `exec()` and `eval()` the way you'd treat string-built SQL:
safe on data you already validated,
dangerous on anything reaching the program from outside it unchecked.

## Self-Registration of Subclasses

A common need is for a base class to keep track of its subclasses,
so you can enumerate them.
This is the textbook reason people used to write a metaclass.
In Python 3 it is a few lines with `__init_subclass__()`,
which Python calls automatically for every new subclass:

```python
# init_subclass.py
# Track the "leaf" subclasses (those with no subclasses of their own),
# using __init_subclass__ instead of a metaclass.
from typing import ClassVar

class Color:
    registry: ClassVar[set[type[Color]]] = set()

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Color.registry.add(cls)
        Color.registry -= set(cls.__bases__)  # Keep only the leaves

class Blue(Color):
    pass
class Red(Color):
    pass
class Green(Color):
    pass
print(sorted(c.__name__ for c in Color.registry))
#: ['Blue', 'Green', 'Red']

class PhthaloBlue(Blue):
    pass
class CeruleanBlue(Blue):
    pass
print(sorted(c.__name__ for c in Color.registry))
#: ['CeruleanBlue', 'Green', 'PhthaloBlue', 'Red']

# A second, independent hierarchy keeps its own registry:
class Shape:
    registry: ClassVar[set[type[Shape]]] = set()

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Shape.registry.add(cls)
        Shape.registry -= set(cls.__bases__)

class Round(Shape):
    pass
class Square(Shape):
    pass
class Circle(Round):
    pass
print(sorted(c.__name__ for c in Shape.registry))
#: ['Circle', 'Square']
```

For each new subclass,
`__init_subclass__()` adds it to the registry and removes its base classes,
so only the current leaves remain.
That is why `Blue` is absent from the second `Color` print.
Creating `PhthaloBlue` and `CeruleanBlue` removed their base `Blue`,
leaving those two leaves beside `Green` and `Red`.
For the same reason `Round` is missing from the `Shape` registry.
Creating `Circle`, a subclass of `Round`, removed `Round`,
leaving `Circle` and `Square`.
This involves no metaclass.
`__init_subclass__()` is implicitly a class method.
Its first argument is the new subclass.

Testing checks that each registry holds only its current leaf classes:

```python
# test_init_subclass.py
import init_subclass

def test_leaf_registry_tracks_only_leaves() -> None:
    leaves = {c.__name__ for c in init_subclass.Color.registry}
    assert leaves == {"Red", "Green", "PhthaloBlue", "CeruleanBlue"}

def test_independent_hierarchies_have_separate_registries() -> None:
    shapes = {c.__name__ for c in init_subclass.Shape.registry}
    assert shapes == {"Square", "Circle"}  # Round is no longer a leaf
```

## Learning a Name with `__set_name__()`

Another job that once needed a metaclass is letting an attribute object discover the name to which it belongs.
A *descriptor* with `__set_name__()` gets that name at class creation:

```python
# set_name.py
# A descriptor learns its attribute name at class-creation time.
from typing import Any

class Field:
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name
        self.storage = f"_{name}"

    def __get__(self, obj: Any, owner: type | None = None) -> Any:
        if obj is None:
            return self
        return getattr(obj, self.storage)

    def __set__(self, obj: Any, value: Any) -> None:
        setattr(obj, self.storage, value)

class Point:
    x = Field()
    y = Field()

p = Point()
p.x = 3
p.y = 4
print(p.x, p.y)
#: 3 4
```

The `Field` descriptors do not know their names are `x` and `y` until Python tells them through `__set_name__()`.
This is metaprogramming, but it needs no metaclass.

Testing confirms the descriptor learns its name and stores under it,
and returns itself when accessed on the class:

```python
# test_set_name.py
import set_name

def test_descriptor_learns_its_name() -> None:
    p = set_name.Point()
    p.x = 3
    p.y = 4
    assert (p.x, p.y) == (3, 4)
    assert p.__dict__ == {"_x": 3, "_y": 4}  # Stored under the names

def test_descriptor_on_class_returns_itself() -> None:
    assert isinstance(set_name.Point.x, set_name.Field)
```

## Writing a Metaclass

When the simpler hooks are not enough, write a metaclass.
A metaclass is a subclass of `type`.
You attach it with the `metaclass=` keyword in the class header.
Python then uses your metaclass, instead of `type`, to build the class.

```python
# simple_meta1.py
# Writing a metaclass and applying it with the `metaclass=` keyword.
from typing import Any

class SimpleMeta1(type):
    def __init__(cls, name: str, bases: tuple[type, ...],
                 nmspc: dict[str, Any]) -> None:
        super().__init__(name, bases, nmspc)
        setattr(cls, "uses_metaclass", lambda self: "Yes!")

class Simple1(metaclass=SimpleMeta1):
    def foo(self) -> None: pass

    @staticmethod
    def bar() -> None: pass

simple = Simple1()
print([m for m in dir(simple) if not m.startswith("__")])
#: ['bar', 'foo', 'uses_metaclass']
# A method injected by the metaclass:
print(simple.uses_metaclass())  # type: ignore
#: Yes!
```

By convention the first argument of a metaclass method is `cls` rather than `self`,
except for `__new__()`, which uses `mcl` (metaclass).
The `cls` is the class object under construction.
As with any subclass, call the base-class version first through `super()`.

Metaprogramming and static typing pull against each other.
A type describes a fixed set of attributes and signatures,
but a metaclass changes that structure at runtime,
adding attributes the class never declared and replacing methods like `__new__()`.
The checker cannot follow those changes,
so it reports the dynamic lines as errors.
Three ways quiet it, from narrowest to broadest:
`setattr(cls, "name", value)` adds an attribute through a string the checker does not track;
a localized `# type: ignore` silences one line,
as on `simple.uses_metaclass()` above;
and copying the class into an `Any`-typed name stops attribute checking for everything reached through that name.
The [singleton metaclass](24_Singleton.md#singleton-using-metaclasses)
uses that last form, `klass: Any = cls`,
to add an `instance` attribute and swap `__new__()`.
Prefer the narrowest escape that fits,
because a broad `Any` also hides genuine mistakes.

## `__init__()` versus `__new__()` in a Metaclass

Metaclass examples appear to use `__new__()` and `__init__()` interchangeably.
The difference is timing.
`__new__()` runs *before* the class object exists, so it can change the name,
bases, and namespace that Python will use to build it.
`__init__()` runs *after* the class exists,
so changing those arguments has no effect,
though you can still modify the finished class object:

```python
# new_vs_init.py
from typing import Any
from display import display_object

class Tag:
    pass

class Meta(type):
    def __new__(mcl, name: str, bases: tuple[type, ...],
                nmspc: dict[str, Any]) -> type:
        # Before creation: these changes take effect
        nmspc["added_in_new"] = 42
        bases += (Tag,)
        return super().__new__(mcl, name, bases, nmspc)

    def __init__(cls, name: str, bases: tuple[type, ...],
                 nmspc: dict[str, Any]) -> None:
        super().__init__(name, bases, nmspc)
        # No effect: the class is already built
        nmspc["added_in_init"] = 99
        # Effect: this modifies the finished class
        setattr(cls, "patched_in_init", 3.14)

class Demo(metaclass=Meta):
    pass

display_object(Demo(), dunder=["__new__", "__init__"])
#: [Attributes]
#:   • added_in_new = 42 [CV]
#:   • patched_in_init = 3.14 [CV]
#: [Methods]
#:   • __init__(self, /, *args, **kwargs)
#:   • __new__(*args, **kwargs)

print("has Tag base:", Tag in Demo.__bases__)
#: has Tag base: True
```

Override `__new__()` when you must change `name`, `bases`, or the namespace
(including special members like `__slots__`) before Python builds the class.
Otherwise, prefer `__init__()`, which is simpler.
When the choice does not matter,
pick `__init__()` and reserve `__new__()` for a genuine need.

## Intercepting Instance Creation

A method defined on the metaclass becomes a method of the *class object*,
callable on the class but not on its instances.
These are sometimes called *metamethods*.
One useful metamethod is `__call__()`, which runs when you create an instance.
Overriding it lets a metaclass intercept instance creation,
which is one way to build a [Singleton](24_Singleton.md):

```python
# singleton.py
# Singleton metaclass intercepts instance creation through __call__.
from typing import Any, ClassVar

class Singleton(type):
    _instances: ClassVar[dict[type, Any]] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class ASingleton(metaclass=Singleton):
    pass

class BSingleton(metaclass=Singleton):
    pass

a = ASingleton()
b = ASingleton()
assert a is b

c = BSingleton()
d = BSingleton()
assert c is d
assert a is not c
print(a.__class__.__name__, c.__class__.__name__)
#: ASingleton BSingleton
```

Each class gets its own entry in the `_instances` dictionary,
so the singletons stay independent.

This works, but it is heavier than the problem usually requires.
[Singleton](24_Singleton.md) covers the lighter alternatives,
from a class decorator down to a module.
Choose the lightest tool that solves your problem.

## Making a Class Final

It is sometimes useful to forbid inheritance.
The modern way to say so is the `@final` decorator from `typing`:

```python
# final.py
from typing import final

@final
class B:
    pass

b = B()
print(type(b).__name__)
#: B

# The type checker rejects `class C(B): ...`,
# because it would inherit from a final class.
```

Type checkers such as ty, mypy, and pyright check `@final` statically.
It states the intent and catches a violation before the code runs.
At runtime it only marks the class, setting `__final__ = True`
(as `test_final.py` below confirms); nothing enforces it:
the interpreter still lets `class C(B): pass` run.

If you need the interpreter to refuse subclassing,
`__init_subclass__()` can enforce it at each subclass creation.
Older literature claims this requires a metaclass.
It does not:

```python
# final_runtime.py
# Runtime finality with __init_subclass__, no metaclass required.

class A:
    pass

class B(A):
    # Any attempt to subclass it fails at class creation:
    def __init_subclass__(cls, **kwargs: object) -> None:
        raise TypeError(
            f"{B.__name__} is final; you cannot subclass it")

print(B.__bases__)
#: (<class '__main__.A'>,)

try:
    class C(B):
        pass
except TypeError as error:
    print(error)
#: B is final; you cannot subclass it
```

The check happens at class-creation time, exactly when it must,
and Python builds `B` normally because `A` does not forbid subclassing.
Use the runtime version only when `@final` is not enough, which is rare.

Tests confirm the `@final` marker is present,
the runtime-final class refuses subclassing,
and its non-final base still allows it:

```python
# test_final.py
import final
import final_runtime
import pytest

def test_final_decorator_marks_class() -> None:
    # @final sets __final__ at runtime. Type checkers read it
    assert final.B.__final__ is True  # type: ignore

def test_runtime_final_cannot_be_subclassed() -> None:
    with pytest.raises(TypeError):
        class Sub(final_runtime.B):
            pass

def test_runtime_non_final_base_can_be_subclassed() -> None:
    class Ok(final_runtime.A):
        pass

    assert issubclass(Ok, final_runtime.A)
```

## When You Still Need a Metaclass

After all this, when is a metaclass the right tool?
When you need to change the class object rather than react to its creation:
adding methods *to the class*
(metamethods such as a custom `__iter__()` or `__call__()` on the class, shown above),
replacing the namespace mapping with `__prepare__()` so the class body populates a custom dictionary,
or enforcing an invariant across an entire family of classes through their shared metaclass.
These are real but uncommon.
For everything else, `__init_subclass__()`, `__set_name__()`,
and class decorators are simpler and easier to read.

One caution: a class has a single metaclass.
Multiple inheritance can accidentally combine classes with different metaclasses,
which creates a metaclass conflict you must then resolve.
That is one more reason to avoid metaclasses unless you truly need them.

## The `inspect` Module

Up to now we've been modifying classes.
`type` builds them, and metaclasses and `__init_subclass__()` run code during their creation.
The `inspect` module is the other half of metaprogramming:
reading the structure of live objects.
It answers questions like which members an object has,
what a function's signature is, and what its docstring says,
without you knowing the answers in advance.

`inspect` works on any live object: modules, classes, functions, methods,
and instances.
A few functions cover most needs:

- `inspect.signature(callable)` returns a `Signature` object describing the parameters,
  their annotations, and their defaults.
- `inspect.getdoc(obj)` returns the cleaned-up docstring.
- `inspect.getmembers(obj)` and `inspect.getmembers_static(obj)` return an object's `(name, value)` pairs.
- Predicates such as `inspect.isclass()`, `inspect.isfunction()`,
  and `inspect.ismethod()` classify what you find.

```python
# inspect_tour.py
import inspect

def greet(name: str, loud: bool = False) -> str:
    "Return a greeting."
    text = f"Hello, {name}"
    return text.upper() if loud else text

print(inspect.signature(greet))
#: (name: str, loud: bool = False) -> str
print(inspect.getdoc(greet))
#: Return a greeting.
print(inspect.isfunction(greet), inspect.isclass(greet))
#: True False
print(list(inspect.signature(greet).parameters))
#: ['name', 'loud']
```

`signature()` recovers the full call interface,
annotations and defaults included, as a structured object rather than a string.

Earlier, `new_vs_init.py` called `display_object()` to show the layout of an object.
That tool is a helper used throughout the book,
so it lives at the root of the examples and any chapter can import it:

```python
# shared: display.py
import inspect
from collections.abc import Callable, Sequence
from typing import Final

ALL_DUNDERS = sentinel("ALL_DUNDERS")
REDEFINED_DUNDERS = sentinel("REDEFINED_DUNDERS")
INTERESTING_DUNDERS: Final[tuple[str, ...]] = (
    "__init__", "__repr__", "__eq__", "__hash__",
)

def _annotations(cls: type) -> dict[str, object]:
    # Annotations declared on the class or any of its bases:
    merged: dict[str, object] = {}
    for base in reversed(cls.__mro__):
        merged.update(inspect.get_annotations(base))
    return merged

def _type_name(annotation: object) -> str:
    # A readable name for a type annotation, keeping any [parameters]:
    if isinstance(annotation, type):
        return annotation.__name__
    return str(annotation)

def _redefined(name: str, value: object) -> bool:
    # Restricted to INTERESTING_DUNDERS: every class has __module__,
    # __dict__, and other bookkeeping dunders that always differ from
    # object's, so comparing those would never filter anything out.
    if name not in INTERESTING_DUNDERS:
        return False
    return getattr(object, name, None) is not value

def _show_dunder(
    dunder: Sequence[str] | ALL_DUNDERS | REDEFINED_DUNDERS,
    name: str,
    value: object,
) -> bool:
    if dunder is ALL_DUNDERS:
        return True
    if dunder is REDEFINED_DUNDERS:
        return _redefined(name, value)
    return name in dunder

def _shared(obj: object, name: str) -> bool:
    # A class has no instance-level storage to compare against, so
    # every attribute it shows is class-level storage by construction.
    # For an instance, only a name missing from its own __dict__ is:
    if inspect.isclass(obj):
        return True
    return name not in getattr(obj, "__dict__", {})

def _truncate(text: str, budget: int) -> str:
    # Keep text within budget, marking a cut with an ellipsis:
    if len(text) <= budget:
        return text
    return text[:budget - 3] + "..."

def _format_method(
    name: str, value: Callable[..., object], max_width: int
) -> str:
    try:
        sig = str(inspect.signature(value))
    except (ValueError, TypeError):
        sig = "(...)"
    sig = _truncate(sig, max_width - len(name) - 4)
    return f"  • {name}{sig}"

def _format_attribute(
    obj: object,
    name: str,
    value: object,
    annotations: dict[str, object],
    max_width: int,
) -> str:
    label = name
    if name in annotations:
        label = f"{name}: {_type_name(annotations[name])}"
    tag = " [CV]" if _shared(obj, name) else ""
    budget = max_width - len(label) - len(tag) - 7
    val_str = _truncate(repr(value), budget)
    return f"  • {label} = {val_str}{tag}"

def display_object(
    obj: object,
    dunder: Sequence[str] | ALL_DUNDERS | REDEFINED_DUNDERS = (),
    max_width: int = 65,
    header: bool = False,
    exclude: Sequence[str] = (),
) -> None:
    # For a class, the class itself; for an instance, its class:
    cls = obj if inspect.isclass(obj) else type(obj)
    if header:
        print(f"=== {cls.__name__} ===")
    annotations = _annotations(cls)
    attributes: list[str] = []
    methods: list[str] = []
    # Read members statically, without triggering dynamic descriptors:
    for name, value in inspect.getmembers_static(obj):
        if name in exclude:
            continue
        is_dunder = name.startswith("__") and name.endswith("__")
        if is_dunder and not _show_dunder(dunder, name, value):
            continue  # Skip standard dunder clutter
        if callable(value):
            methods.append(_format_method(name, value, max_width))
        else:
            attributes.append(_format_attribute(
                obj, name, value, annotations, max_width
            ))
    print("[Attributes]")
    print("\n".join(attributes) or "  None")
    print("[Methods]")
    print("\n".join(methods) or "  None")
```

`header=True` prints `=== {ClassName} ===` before the report; the default,
`False`, omits it.
Every call in this book sits directly beneath the code that produced it,
so the class is already visible without a header.
Pass `header=True` when running `display_object()` on its own,
outside a listing like this one,
especially if several calls to different classes run together with nothing else marking where one report ends and the next begins.

`display_object()` walks every member that `inspect.getmembers_static()` returns.
The static variant reads members from the object and its classes directly,
without invoking descriptors, properties, or `__getattr__()`.
Inspecting an object therefore never runs its code or triggers a side effect,
which matters when you point this tool at something unfamiliar.
The tool sorts each member into one of two lists.
Callables become methods,
printed with the signature `inspect.signature()` reports,
or `(...)` when a built-in has no inspectable signature.
Everything else becomes an attribute, printed as `name: type = value`.
The declared type comes from the class annotations,
gathered across the whole inheritance chain with `inspect.get_annotations()`.
An attribute with no annotation, such as one assigned dynamically,
prints as `name = value`.
The value is the member's `repr()`,
truncated to keep the line within `max_width`.
An attribute tagged `[CV]`, for *class variable*,
is not stored in `obj`'s own `__dict__`.
A class has no instance-level storage to compare against:
every attribute `display_object()` shows for a class already lives on that class or a base class,
so all of them carry the tag.
`classvar_dataclass.py`'s `show(D)` tags both `D.x` and `D.s`,
even though `D` declares them directly, because neither belongs to an instance.
For an instance, the tag distinguishes storage borrowed from the class from storage that lives on the object itself,
the way `Stars.rating` did in [Class Attributes](09_Class_Attributes.md#class-attributes-are-not-default-values):
`class_with_defaults.py`'s `show(B())` tags the same two names, `B.x` and `B.s`,
while `display_object(Messenger("foo", 12, 3.14))` tags none,
since `@dataclass` assigns every field straight onto the new instance.
The tag reports this dynamically, from where the value actually lives,
so it applies whether or not the attribute is declared with `typing.ClassVar`.
The display hides standard dunder members by default.
Pass their names in `dunder` to keep specific ones,
as `new_vs_init.py` does to show `__new__` and `__init__`.
Pass the `ALL_DUNDERS` sentinel instead to keep every dunder member,
including the interpreter's own machinery.
`dunder` is typed `Sequence[str] | ALL_DUNDERS | REDEFINED_DUNDERS`,
naming each sentinel value itself rather than the generic `sentinel` class,
so a type checker narrows `dunder` to `Sequence[str]` once both sentinels are ruled out,
and `name in dunder` needs no further guard.
`ALL_DUNDERS` is useful for exploring an unfamiliar object,
but it buries a class's own choices under everything `object` and the interpreter add.
`INTERESTING_DUNDERS` names the four a reader actually customizes when defining a class:
`__init__`, `__repr__`, `__eq__`, and `__hash__`.
Pass it as `dunder` to see those four without the surrounding noise.

A class inherits all four of those from `object` without overriding any of them,
so `INTERESTING_DUNDERS` shows `object`'s generic versions,
which can look like the class defined them itself.
`REDEFINED_DUNDERS` filters harder: among those same four,
it keeps only the ones whose value differs from `object`'s own,
so a class that overrides none of them shows no dunders at all.
`_redefined()` checks membership in `INTERESTING_DUNDERS` before comparing,
deliberately narrowing the comparison to those four.
Every class, even an empty one, has its own `__module__`, `__dict__`,
and a handful of other bookkeeping dunders that never match `object`'s,
so comparing every dunder this way would show that bookkeeping instead of filtering it out.
The comparison uses `is`, not `==`,
since a dunder inherited unchanged from `object` is the same function object,
not merely an equal one.

`exclude` drops specific names regardless of what `dunder` would otherwise show,
and it applies to any member, not just dunders.
`display_object(obj, REDEFINED_DUNDERS, exclude=("__hash__",))` shows whatever `REDEFINED_DUNDERS` finds redefined,
minus `__hash__`, useful when a listing has already made that particular point and repeating it would only add noise.
The check runs first, before the `dunder` logic even sees the name,
so an excluded name never reaches `[Attributes]` or `[Methods]` no matter which mode selected it.

```python
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
```

The first two calls show the same class from two angles.
`display_object(Fraggle)` inspects the class object itself.
It lists `y` and `z`, the fields with defaults.
`x` is declared as `x: int` with no default,
so on the class it is only an annotation, not a bound attribute,
and `getmembers_static()` does not return it.
`display_object(Fraggle(9, 2.3))` inspects an instance,
whose attributes hold its field values, so `x` now appears beside `y` and `z`.
With `header=True`, both calls would print the same header, `=== Fraggle ===`:
for a class `display_object()` reports the class's own name,
and for an instance the name of the instance's class.
The method list is the same either way, because methods live on the class.
The third call passes `ALL_DUNDERS`.
Part of the flood is `@dataclass`'s own doing: `__dataclass_fields__`,
`__match_args__`, `__replace__`, `__hash__` set to `None`,
and the generated `__init__`, `__eq__`,
and `__repr__` that give `Fraggle` a constructor, equality,
and a `repr()` for free.
The rest, from `__class__` to `__static_attributes__`,
is the bookkeeping every class carries.

## Exercises

1.  In `init_subclass.py`,
    add a class `Yellow(Color)` and then `MutedYellow(Yellow)`.
    Predict `Color.registry` after each new class, then confirm.
2.  In `set_name.py`, add a third `Field()` attribute, `z`, to `Point`,
    set `p.z = 9`, and confirm `p.__dict__` now also holds `_z`.
3.  In `singleton.py`, add a third class `CSingleton(metaclass=Singleton)` and confirm `c1 = CSingleton(); c2 = CSingleton(); c1 is c2` is `True`,
    while `c1 is a` (comparing across the different singleton classes)
    is `False`.
4.  In `final_runtime.py`, add a class `D(A)`
    (a second, independent subclass of the non-final `A`)
    and confirm it succeeds, the same way `Ok` does in `test_final.py`.
5.  Using `inspect_tour.py` as a model,
    write a function `describe(func)` that prints a function's name,
    its `inspect.signature()`, and its docstring
    (or `"(no docstring)"` if `inspect.getdoc()` returns `None`),
    then call it on `greet` and on a lambda.
