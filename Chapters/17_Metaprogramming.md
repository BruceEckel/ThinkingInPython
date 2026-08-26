# Metaprogramming

Other (special) objects create objects.
These special objects are *classes*,
and you configure them to produce the objects you want.

Classes are also objects, and you can modify objects.
The listings here use `display_object()`,
the inspection helper this chapter builds in [Building `display_object()`](#building-display_object):

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

print(vars(x))
#: {}
```

`x` sees the changes you make to the class *after* `x`'s creation.
The instance does not change;
the last line shows its instance dictionary still empty.
Attribute lookup on an instance falls through to its class,
so a change to a class reaches every object of that class,
even ones already created.

What creates these "class" objects?
Other special objects, called *metaclasses*.
The default metaclass is `type`, and almost always it does the right thing.
You can customize how Python produces classes by running extra code or injecting members as it builds each class.
That is metaclass programming.

You have used metaclasses already, without writing one.
`abc.ABCMeta` builds `abc.ABC`,
and makes a class with an unimplemented abstract method refuse instantiation.
`enum.EnumType` builds each `Enum` subclass,
turning every class-body assignment into a member and making `for c in Color` walk them.
Iterating a class is behavior on the class object,
which is where a metaclass can put it and an ordinary class cannot.

Most of the time you do not need a metaclass.
It is a fascinating tool and tempting to use,
but simpler hooks cover almost every case a metaclass used to handle:

- `__init_subclass__()` runs at subclass creation.
  It replaces most "do something at each class definition" metaclasses.
- `__set_name__()` lets a class attribute learn its own name,
  at class-creation time.
- *Class decorators* transform a class after Python builds it
  ([Decorating Classes](14_Decorators.md#decorating-classes)).

Use a metaclass only when these cannot do the job.
This chapter starts by building classes by hand,
to show what a `class` statement actually does.
Then come the simpler hooks, and metaclasses for the jobs that still need them.
The `inspect` module closes the chapter from the other side,
reading class structure instead of changing it.

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

Generating classes programmatically with `type` pays off when a family of classes differs only by name.
Where you might otherwise write many near-identical subclasses by hand,
you can instead generate them dynamically.
A greenhouse controller runs scheduled events, one class per kind of event,
and a dict comprehension builds all of them:

```python
# eager_event_classes.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import Final, cast

@dataclass
class Event:
    action: str
    hour: int
    minute: int

type EventMaker = Callable[[int, int], Event]
NAMES: Final[tuple[str, ...]] = (
    "ThermostatDay", "ThermostatNight", "LightOn", "LightOff",
    "WaterOn", "WaterOff", "RingBell",
)

def make(name: str) -> EventMaker:
    def init(self: Event, hour: int, minute: int) -> None:
        Event.__init__(self, name, hour, minute)
    new_cls = type(name, (Event,), {"__init__": init})
    return cast(EventMaker, new_cls)

makers = {name: make(name) for name in NAMES}
print(len(makers))
#: 7
print(makers["LightOn"](1, 0))
#: LightOn(action='LightOn', hour=1, minute=0)
```

Each generated class is a real type, not a label.
`LightOn` and `WaterOff` are distinct subclasses of `Event`,
so `isinstance()` tells them apart and you can later give either one behavior of its own.

The checker cannot follow a class built by `type()`,
so it reads `make()`'s result as `Event`,
whose `__init__()` takes three arguments.
`EventMaker` names the two-argument signature the generated classes really have,
and the `cast()` records it at the one place that creates a class.

`make()` exists so that each `init()` closes over its own `name`.
A lambda written inline in the comprehension would close over the comprehension's variable instead,
so every generated class would record the final name, `RingBell`,
as its `action`: the late-binding trap `late_binding.py` demonstrates in [Function Objects](28_Function_Objects.md#command-choosing-the-operation-at-runtime).

`init()` calls `Event.__init__(self, ...)` directly instead of `super().__init__(...)`.
It is a nested function, not a method defined inside a `class` statement,
so the compiler never gives it the `__class__` cell that zero-argument `super()` needs.

The dict comprehension builds all seven classes whether the schedule uses them or not.
Seven is cheap and hundreds would not be,
so the next version delays building each class until the first lookup asks for it,
which costs a `dict` subclass and a placeholder for the classes that do not exist yet:

```python
# greenhouse.py
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, cast

type EventMaker = Callable[[int, int], Event]
NOT_CREATED = sentinel("NOT_CREATED")

class EventMakers(dict[str, EventMaker | NOT_CREATED]):
    def __getitem__(self, class_name: str) -> EventMaker:
        if class_name not in self:
            raise KeyError(f"Unknown event class: {class_name!r}")
        maker = super().__getitem__(class_name)
        if maker is NOT_CREATED:
            print(f"Creating {class_name}")
            # Local function to pass to type constructor:
            def init(self: Event, hour: int, minute: int) -> None:
                Event.__init__(self, class_name, hour, minute)
            new_cls = type(class_name, (Event,), {"__init__": init})
            maker = cast(EventMaker, new_cls)
            self[class_name] = maker
        return maker

@dataclass
class Event:
    action: str
    hour: int
    minute: int
    events: ClassVar[list[Event]] = []  # Registry of all Events
    _event_maker: ClassVar[EventMakers] = EventMakers({
        name : NOT_CREATED  # Dict key : value
        for name in (
            "ThermostatDay", "ThermostatNight",
            "LightOn", "LightOff",
            "WaterOn", "WaterOff",
            "RingBell",
        )
    })

    def __post_init__(self) -> None:
        Event.events.append(self)

    @staticmethod
    def load_schedule(path: Path) -> None:
        lines = [
            line for line in path.read_text().splitlines()
            if line.strip() and not line.startswith("#")
        ]
        for line in lines:
            class_name, hour, minute = (
                line.replace(":", " ").split())
            Event._event_maker[class_name](int(hour), int(minute))

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

Calling `Event(class_name, hour, minute)` directly would print the same schedule,
but every entry would be the same type with its kind reduced to a string.

`EventMakers` subclasses `dict` so the laziness is invisible at the call site.
`Event._event_maker[class_name]` reads as an ordinary lookup,
and the overridden `__getitem__()` decides whether that lookup returns a class or builds one first.
The alternative, a `make_event()` function,
would push that decision into every caller.

`load_schedule()` reads that file, filtering out blank lines and comments,
then builds an `Event` from each resulting line.
`line.replace(":", " ").split()` turns `"WaterOn 3:30"` into three strings in a single step,
replacing the colon with a second space before splitting on whitespace.
`Event._event_maker[class_name]` gets the class object that builds that `Event`.
The first time a lookup asks for an event type,
the maker builds the class and registers it under its name.
An unknown name raises `KeyError`,
which a caller writing `try: ... except KeyError` around a lookup expects.

`Event._event_maker` starts out holding the seven legitimate event names,
each paired with the `NOT_CREATED` sentinel as a placeholder.
Populating that dict does not build any classes.
It only reserves the names,
so `EventMakers.__getitem__()` has something to check a `class_name` against before building anything.
The dict's value type is `EventMaker | NOT_CREATED`,
naming the sentinel value rather than the generic `sentinel` class,
so ruling out one member with `maker is NOT_CREATED` leaves `EventMaker` in the other branch.
[Choosing Which Dunders to Show](#choosing-which-dunders-to-show)
uses the same idiom.

## Generating Classes with `exec()`

The `type` approach in the previous section builds a class from a name,
a tuple of bases, and a namespace dict.
A second way is to write an ordinary `class` statement in an f-string,
then `exec()` that string as code.
That class body, held in `klass` below,
is easier to read and modify than a namespace dict:

```python
# commander.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, ClassVar, cast
from exceptions import ignore

@dataclass
class Command:
    label: str
    KNOWN_COMMANDS: ClassVar[set[str]] = {"Start", "Stop", "Pause"}

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
        namespace: dict[str, Any] = {"Command": Command}
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

`make_class()` execs `klass` into a private `namespace` dict rather than the module's namespace,
which it seeds with `{"Command": Command}` so the generated class can find its base.
The type checker can't see into the string,
so `namespace[class_name]` is just `Any` to it.
`exec()` also drops a `__builtins__` entry into any globals mapping that lacks one,
which is the other reason the values can carry no type more precise than `Any`.
`cast(Callable[[], Command], ...)` records the actual no-argument signature at the one place that creates the class,
the same idiom `greenhouse.py` uses for `EventMaker`.
Unlike `EventMakers`, `make_class()` caches nothing:
calling `make_class("Start")` twice builds two distinct classes.

`__init__`'s definition sits textually inside a `class` block.
The compiler doesn't care that the block arrived as a string.
That is the difference from `greenhouse.py`,
whose `init()` is a nested function rather than a method in a class body,
so it gets no `__class__` cell and cannot use zero-argument `super()`.
Text that reaches the compiler as a class body gets the cell;
a function object handed to `type()` does not.

That string is also the danger.
`exec()` runs its argument with the full power of the language,
and `klass` splices `class_name` directly into source text,
so an unvalidated name containing a newline and a second statement could break out of the `class` block and run anything,
the same way an unescaped value breaks out of a hand-built SQL query.
The `KNOWN_COMMANDS` check closes that hole:
only three fixed names ever reach the template.
`EventMakers` never has this risk,
because `type(class_name, (Event,), ...)` treats `class_name` as a plain string value,
never as source code.
Treat `exec()` and `eval()` like string-built SQL:
safe on values you've already validated,
dangerous on anything that reaches the program from outside, unchecked.

## Self-Registration of Subclasses

Often a base class needs to keep track of its subclasses,
so you can enumerate them.
This is the textbook reason people used to justify a metaclass.
Python calls `__init_subclass__()` automatically for every new subclass,
so a base class can register its own subclasses in a few lines.
This example tracks the "leaf" subclasses
(those with no subclasses of their own),
using `__init_subclass__()` instead of a metaclass:

```python
# init_subclass.py
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
Creating `PhthaloBlue` and `CeruleanBlue` removes their base `Blue`,
leaving those two leaves beside `Green` and `Red`.
For the same reason, `Round` is missing from the `Shape` registry.
Creating `Circle`, a subclass of `Round`, removes `Round`,
leaving `Circle` and `Square`.
None of this needs a metaclass.
`__init_subclass__()` is implicitly a class method.
Its first argument is the new subclass.
It never runs for the class whose body defines it,
only for classes derived from that class,
which is why neither `Color` nor `Shape` appears in its own registry.

The keyword arguments come from the subclass header.
Writing `class Blue(Color, shade="cool"):` delivers `shade="cool"` to `__init_subclass__()`,
so a subclass can configure its own registration.
Passing the rest on with `super().__init_subclass__(**kwargs)` lets a base further up the chain take the keywords it declared,
and makes an unrecognized keyword an error rather than a silent no-op.

Testing shows that each registry holds only its current leaf classes:

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

The mechanism is reliable;
the registries built on it fail in two ways that have nothing to do with `__init_subclass__()`.
[Factory](27_Factory.md#the-pythonic-factory-a-dictionary) covers both:
a class in a module nobody imports never registers,
and keying on `cls.__name__` lets two same-named classes overwrite each other.

## Making a Class Final

Sometimes you need to forbid inheritance.
The modern way to say so is the `typing.final` decorator:

```python
# final.py
from typing import final

@final
class B:
    pass

# class C(B): pass  # ty: cannot inherit from final class "B"
b = B()
print(type(b).__name__)
#: B
```

The type checker rejects the commented line.

Type checkers such as ty, mypy, and pyright check `@final` statically.
At runtime the decorator only marks the class, setting `__final__ = True`
(as `test_final.py` below confirms),
so the interpreter still runs `class C(B): pass`.

If you need the interpreter to refuse subclassing,
older literature claims this requires a metaclass.
It does not; `__init_subclass__()` can enforce it at each subclass creation:

```python
# final_runtime.py

class A:
    pass

class B(A):
    def __init_subclass__(cls, **kwargs: object) -> None:
        raise TypeError(
            f"{B.__name__} is final; you cannot subclass it")

try:
    class C(B):
        pass
except TypeError as error:
    print(error)
#: B is final; you cannot subclass it
```

The check runs at class-creation time.
Python builds `B` normally.
A class's own `__init_subclass__()` never runs for that class,
and the version that does run at `B`'s creation is the one `B` inherits from `A`,
which is `object`'s do-nothing default.
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

## Learning a Name with `__set_name__()`

A *descriptor* is any object whose class defines at least one of `__get__()`,
`__set__()`, or `__delete__()`.
Most descriptors define `__get__()` and add the others as needed.
When a class attribute holds a descriptor,
that descriptor takes over access to the attribute.
Instead of going to the instance's `__dict__`,
a read calls `__get__()` and a write calls `__set__()`.
[Decorators](14_Decorators.md#a-limitation-methods-need-a-descriptor)
already relied on this without naming it.
A function is an object like any other, and its class defines `__get__()`,
which makes every function a descriptor:

```python
# function_is_descriptor.py
from dataclasses import dataclass

@dataclass
class Person:
    name: str

    def greet(self) -> str:
        return f"Hello, {self.name}"

# def created a plain function in the class namespace:
plain = Person.__dict__["greet"]
print(type(plain).__name__, hasattr(plain, "__get__"))
#: function True

# Reading it through an instance triggers __get__(),
# which returns a bound method:
p = Person("Ann")
print(p.greet())
#: Hello, Ann

print(plain.__get__(p, Person)())
#: Hello, Ann
```

The last line performs by hand what `p.greet()` does automatically.
Method binding is not special machinery, just the descriptor protocol at work.

Learning its own name is another job that once needed a metaclass.
In `x = Field()` below, `Field()` runs before the assignment,
so the new instance cannot know it is about to get the name `x`.
Python delivers that name automatically.
When a `class` body finishes executing,
Python calls `__set_name__(owner, name)` on every class attribute that defines it,
not only descriptors,
passing the freshly created class and the name that holds the attribute.
`Field` pairs `__set_name__()` with `__get__()` and `__set__()`,
the descriptor protocol, and uses the delivered name to build its storage key.
A `print()` at the top of each method traces the descriptor's whole life:
naming at class creation, then every read and write:

```python
# set_name.py
from typing import Any

class Field:
    def __set_name__(self, owner: type, name: str) -> None:
        print(f"{name}.__set_name__ on {owner.__name__}")
        self.name = name
        self.storage = f"_{name}"

    def __get__(self, obj: Any, owner: type | None = None) -> Any:
        via = "class" if obj is None else "instance"
        print(f"{self.name}.__get__ via {via}")
        if obj is None:
            return self
        return getattr(obj, self.storage)

    def __set__(self, obj: Any, value: Any) -> None:
        print(f"{self.name}.__set__ = {value}")
        setattr(obj, self.storage, value)

class Point:
    x = Field()
    y = Field()
#: x.__set_name__ on Point
#: y.__set_name__ on Point

p = Point()
p.x = 3
#: x.__set__ = 3
p.y = 4
#: y.__set__ = 4
print(p.x, p.y)
#: x.__get__ via instance
#: y.__get__ via instance
#: 3 4
print(isinstance(Point.x, Field))
#: x.__get__ via class
#: True
```

The first two trace lines appear before any instance exists:
Python calls `__set_name__()` as it finishes executing the `class Point` statement,
once for each `Field`,
handing each one the new class and its own attribute name.
From then on, every read and write routes through the descriptor instead of going to the instance's `__dict__`.
`p.x = 3` prints `x.__set__ = 3` before storing anything.
In `print(p.x, p.y)`, Python evaluates both arguments before calling `print()`,
so both `__get__` lines appear ahead of `3 4`.
The final access, `Point.x`, goes through the class rather than an instance,
so `__get__()` receives `obj=None` and reports `via class`.
That branch returns `self`, the descriptor object,
which is why `isinstance(Point.x, Field)` is `True`.

Each `Field` stores values under `_x` or `_y` in the instance's `__dict__`.
The underscore prefix is not decoration.
A descriptor that defines `__set__()` is a *data descriptor*,
and on every lookup a data descriptor outranks the instance's `__dict__`.
If `__get__()` asks `obj` for plain `"x"`,
that lookup routes back to the descriptor and calls `__get__()` again, forever.
Storing under `"_x"`, a name no descriptor claims, breaks the loop.

A descriptor with only `__get__()` is a *non-data descriptor*,
and the ranking reverses: the instance's `__dict__` wins.
That is why assigning `p.greet = something` shadows the method on that one instance,
while `p.x = 3` cannot shadow `Field`, because `Field` defines `__set__()`.

This is metaprogramming, but it needs no metaclass.

Testing confirms the descriptor learns its name,
stores each value under the storage key built from that name,
and returns itself when you read it through the class:

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

A metaclass is a subclass of `type`,
and you write one when the simpler hooks are not enough.
You attach it with the `metaclass=` keyword in the class header.
Python then uses your metaclass, instead of `type`, to build the class.

```python
# simple_meta.py
from typing import Any
from display import display_object

class SimpleMeta(type):
    def __init__(cls, name: str, bases: tuple[type, ...],
                 nmspc: dict[str, Any]) -> None:
        super().__init__(name, bases, nmspc)
        setattr(cls, "uses_metaclass", lambda self: "Yes!")

class Simple(metaclass=SimpleMeta):
    def foo(self) -> None: pass

    @staticmethod
    def bar() -> None: pass

display_object(Simple)
#: [Attributes]
#:   None
#: [Methods]
#:   • bar() -> None
#:   • foo(self) -> None
#:   • uses_metaclass(self)
print(Simple().uses_metaclass())  # type: ignore
#: Yes!
```

`SimpleMeta.__init__()` runs once, as the `class Simple` statement finishes,
and patches a new method onto the freshly built class.
In the `display_object()` output,
`uses_metaclass(self)` sits alongside `foo` and `bar`,
indistinguishable from the methods in the class body.
The injected value is a lambda, but a function is a descriptor
([Learning a Name with `__set_name__()`](#learning-a-name-with-__set_name__)),
so `Simple().uses_metaclass()` binds it like any other method.

Since a metaclass is a subclass of `type`,
writing `class Simple(SimpleMeta):` means something else.
That syntax makes `SimpleMeta` an ordinary base class,
so `Simple` inherits `type` and becomes a second metaclass,
not a class built by `SimpleMeta`.
`metaclass=` is the mechanism for naming what builds a class,
independent of its base classes.
A subclass repeats `metaclass=` only if its bases do not already carry the same metaclass,
since Python computes a new class's metaclass from all of its bases.

By convention the first argument of a metaclass method is `cls` rather than `self`,
except for `__new__()`,
whose first argument is the metaclass and usually takes the name `mcls` or `mcs`;
here `cls` is the class object under construction, `Simple`.
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
as on `Simple().uses_metaclass()` above;
and copying the class into an `Any`-typed name, `klass: Any = cls`,
stops attribute checking for everything reached through that name.
Prefer the narrowest escape that fits,
because a broad `Any` also hides genuine mistakes.

## `__init__()` versus `__new__()` in a Metaclass

Metaclass examples appear to use `__new__()` and `__init__()` interchangeably.
The difference is timing.
`__new__()` runs *before* the class object exists, so it can change the name,
bases, and namespace that Python uses to build it.
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
    def __new__(mcls, name: str, bases: tuple[type, ...],
                nmspc: dict[str, Any]) -> type:
        # Before creation: these changes take effect
        nmspc["added_in_new"] = 42
        bases += (Tag,)
        return super().__new__(mcls, name, bases, nmspc)

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

`added_in_init` never appears because `type.__new__()` copies `nmspc` into the new class's own `__dict__` as it builds the class.
By the time `__init__()` runs, the two mappings are independent,
so mutating the original dict changes nothing the class can see.
`setattr(cls, ...)` still works because it modifies the class object.

Override `__new__()` when you must change `name`, `bases`, or the namespace
(including special members like `__slots__`) before Python builds the class.
Otherwise, prefer `__init__()`, which is simpler,
and reserve `__new__()` for a genuine need.

## Intercepting Instance Creation

A method defined on the metaclass becomes a method of the *class object*,
callable on the class but not on its instances.
These are sometimes called *metamethods*,
and they differ from `classmethod`s because a `classmethod` stays callable on both the class and its instances,
while a metamethod works only through the class.
The class is an instance of the metaclass.
The class's own instances are not.

One useful metamethod is `__call__()`.
It is the same method that makes any object callable.
`obj()` invokes `type(obj).__call__(obj, ...)`.
A class is an object, an instance of its metaclass,
so `ClassName()` invokes `__call__()` on the metaclass the same way.
It runs first when you create an instance of the class.
`__new__()` and `__init__()` normally run only because the default `type.__call__()` calls them.
A metaclass that overrides `__call__()` sits above that step and decides whether to call them.
That lets it skip building a new instance,
for example by returning one it already cached.
This is one way to build a [Singleton](24_Singleton.md):

```python
# singleton.py
from typing import Any, ClassVar

class Singleton(type):
    # A shared dict of class objects : instances
    _instances: ClassVar[dict[type, Any]] = {}

    def __call__[T](
            cls: type[T], *args: Any, **kwargs: Any) -> T:
        if cls not in Singleton._instances:
            print(f"building {cls.__name__}")
            Singleton._instances[cls] = type.__call__(
                cls, *args, **kwargs)
        else:
            print(f"reusing {cls.__name__}")
        return Singleton._instances[cls]

class ASingleton(metaclass=Singleton):
    pass

class BSingleton(metaclass=Singleton):
    pass

a = ASingleton()
#: building ASingleton
b = ASingleton()
#: reusing ASingleton
assert a is b

c = BSingleton()
#: building BSingleton
d = BSingleton()
#: reusing BSingleton
assert c is d
assert a is not c
```

The trace shows the interception.
The second `ASingleton()` never reaches `__new__()` or `__init__()`:
`__call__()` finds the cached instance and returns it without building anything.
Each class gets its own entry in the `_instances` dictionary,
so the singletons are independent.
The `[T]` on `__call__()` ties its return type to `cls`,
so a type checker sees `ASingleton()` as an `ASingleton` instead of `Any`.
Without it, every singleton loses its type and a type checker can no longer catch a misspelled attribute access on the result.

That same `[T]` is why the body calls `type.__call__(cls, ...)` instead of the more usual `super().__call__(...)`.
Annotating the first parameter as `type[T]` hides that `cls` is a `Singleton`,
which a checker must confirm before it accepts a zero-argument `super()`.
Both forms do the same work at run time.

You might expect to parameterize[^parametrize] the class,
with `class Singleton[T](type)` and `_instances: ClassVar[dict[type, T]]`.
That does not work.
A `ClassVar` cannot depend on a type parameter of its own class,
because `ClassVar` means one shared value for the whole class,
not a different value per instantiation.
Even ignoring that, a subclass needs to write `class ASingleton(metaclass=Singleton[ASingleton]):`,
naming `ASingleton` before its class body finishes defining it.[^crtp]
The method-level `[T]` on `__call__()` avoids both problems.
It binds `T` from `cls` at the call site, `ASingleton()`,
which runs only after `ASingleton` already exists.

The metaclass version works,
but it is heavier than the problem usually requires.
[Singleton](24_Singleton.md) covers the lighter alternatives,
from a class decorator down to a module.
Choose the lightest tool that solves your problem.

### Multiple Inheritance and Metaclasses

`Singleton` stores its cache in `_instances`, a `dict` attribute.
It doesn't inherit from `dict` directly.
Can a metaclass inherit from more than one class, the way an ordinary class can?

Trying the obvious version fails.
`type` and `dict` are both built-in types with their own C-level instance layout,
and CPython allows multiple inheritance only when at most one base carries a nontrivial layout:

```python
# metaclass_layout_conflict.py
from typing import Any
from exceptions import ignore

with ignore(TypeError):
    class Singleton(type, dict[type, Any]):  # type: ignore
        pass
#: TypeError('multiple bases have instance lay-out conflict')
```

The failure has nothing to do with metaclasses.
`class X(dict, type): pass` fails the same way with no metaclass involved.
`type` and `dict` each bring an incompatible layout,
so combining them is impossible in any context.

<!-- "the very TypeError" is the intensive adjective, not the hedging adverb
     proselint.Very exists to catch. -->
<!-- vale proselint.Very = NO -->
The `# type: ignore` comment appears because ty knows this rule statically.
Its `instance-layout-conflict` check reports at check time the very `TypeError` this example exists to demonstrate at run time.
A checker that predicts a crash before the program runs is static typing at its best;
the comment suppresses the diagnostic only because raising that crash is educational.
<!-- vale proselint.Very = YES -->

A metaclass can multiply inherit like any other class,
as long as the extra class is a mixin with no competing layout:

```python
# mixin.py
from exceptions import ignore

class Mixin:
    def helper(self) -> str:
        return "hi"

class Base(type, Mixin):
    pass

class Derived(metaclass=Base):
    pass

print(Derived.helper())
#: hi

with ignore(AttributeError):  # A metamethod: class only
    Derived().helper()  # type: ignore
#: AttributeError("'Derived' object has no attribute 'helper'")
```

`helper()` arrives through the metaclass,
so `Derived` has it and a `Derived` instance does not.
That is the metamethod rule from the start of [Intercepting Instance Creation](#intercepting-instance-creation),
failing out loud: an instance of `Derived` is not an instance of `Base`,
so nothing in its lookup chain reaches `Mixin`.
A `classmethod` would answer on both.

The constraint here is the ordinary "at most one layout-bearing base" rule that governs every Python class,
not something specific to metaclasses.
Composing a `dict`, the way `Singleton._instances` already does,
sidesteps the conflict.

Multiple inheritance fails a second way, from the other direction.
A class has a single metaclass,
so inheriting from two classes built by different metaclasses has no answer:

```python
# multiple_metaclass_inheritance.py
class MetaA(type):
    pass

class MetaB(type):
    pass

class A(metaclass=MetaA):
    pass

class B(metaclass=MetaB):
    pass

try:
    class C(A, B):  # type: ignore
        pass
except TypeError as error:
    print(type(error).__name__)
#: TypeError
```

This creates a metaclass conflict you must resolve,
by giving `C` a metaclass that inherits both.
As with the layout conflict just shown,
ty reports `conflicting-metaclass` and names both `MetaA` and `MetaB`,
which is why the line carries a `# type: ignore`.
Both failures have the same shape:
an inheritance graph that looks legal until you notice what the bases carry with them.
It's one more reason to avoid metaclasses (and, arguably, multiple inheritance)
unless you truly need them.

## When You Still Need a Metaclass

Use a metaclass when you need to change the class object rather than react to its creation:

- Adding methods *to the class*
  (metamethods such as the `__call__()` shown above, or the `__iter__()` that lets `EnumType` make `for c in Color` work).
- Replacing the namespace mapping with `__prepare__()` so the class body populates a custom dictionary.
- Enforcing an invariant across an entire family of classes through their shared metaclass.

`__prepare__()` is the one with no simpler substitute:

```python
# prepare_namespace.py
from typing import Any
from exceptions import ignore

class NoDuplicates(dict[str, Any]):
    def __setitem__(self, key: str, value: Any) -> None:
        if key in self:
            raise TypeError(f"{key} defined twice")
        super().__setitem__(key, value)

class Strict(type):
    @classmethod
    def __prepare__(cls, name: str, bases: tuple[type, ...],
                    **kwargs: Any) -> NoDuplicates:
        return NoDuplicates()

with ignore(TypeError):
    class Handlers(metaclass=Strict):
        def on_open(self) -> None: ...
        def on_close(self) -> None: ...
        def on_open(self) -> None: ...  # noqa: F811
#: TypeError('on_open defined twice')
```

`__prepare__()` runs before the class body does,
and whatever mapping it returns becomes the namespace for that body.
Every `def` and every assignment in the body becomes a `__setitem__()` call on that mapping,
so `NoDuplicates` sees the second `on_open` assigned to a name it already holds.
Python then hands the finished mapping to `type.__new__()`.
`__prepare__()` must carry `@classmethod`.
Python calls it on the metaclass before any class object exists,
so an ordinary method would receive the class name as its `self` and leave `bases` unfilled,
producing a `TypeError` that says nothing about the real mistake.
No other hook can do this: `__init_subclass__()`, `__set_name__()`,
and a class decorator all run after the body has finished,
by which time the duplicate has already won.
The `# noqa: F811` suppresses ruff's own report of the same mistake,
which is the static half of the check; `__prepare__()` catches it at run time,
including on names the body computes.

These are real but uncommon.
For everything else, `__init_subclass__()`, `__set_name__()`,
and [class decorators](14_Decorators.md#decorating-classes)
are simpler and easier to read.
A class decorator receives the finished class, so it can add, replace,
or inspect members, but it cannot change the name, the bases, or the namespace,
and it cannot give the class object behavior of its own.
Setting `__call__` from a decorator makes *instances* callable;
only a metaclass makes the class callable in a new way.
That is the whole case for a metaclass: the class object needs behavior,
and nothing that runs after the class exists can give it any.

## The `inspect` Module

Up to now, you've been modifying classes.
`type` builds them, and metaclasses and `__init_subclass__()` run code during their creation.
The `inspect` module is the other half of metaprogramming:
it reads the structure of live objects.
It answers questions like which members an object has,
what a function's signature is, and what its docstring says.

`inspect` works on any live object: modules, classes, functions, methods,
and instances.
A few functions cover most needs:

- `inspect.signature(callable)` returns a `Signature` object describing the parameters,
  their annotations, and their defaults.
- `inspect.getdoc(obj)` returns the cleaned-up docstring.
- `inspect.getmembers(obj)` and `inspect.getmembers_static(obj)` return an object's `(name, value)` pairs.
  The `_static` variant reads them without running properties or other descriptors.
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
Python does not discard type annotations (a.k.a. type hints) at runtime.
It keeps them attached to the function and evaluates them on demand,
the deferred evaluation of PEP 649,
even though it [never checks them](08_Static_Typing.md#hints-are-not-enforced-at-run-time).
`signature()` requests that stored data (not the original source text)
to build the `Signature` object.
The `ALL_DUNDERS` listing in [The Tool in Use](#the-tool-in-use)
shows that machinery on a class:
`__annotate_func__` is the code that computes the annotations,
and `__annotations_cache__` holds the result after the first request.

### Building `display_object()`

Throughout the book you've seen `display_object()` show the layout of an object.
The `utils/` prefix on the file marker below puts it in the shared `utils/` directory at the top of the `Examples` tree,
where any chapter can import it:

```python
# utils/display.py
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
    return {**inspect.get_annotations(base)
            for base in reversed(cls.__mro__)}

def _type_name(annotation: object) -> str:
    # A readable name for a type annotation, keeping any [parameters]:
    if isinstance(annotation, type):
        return annotation.__name__
    return str(annotation)

def _redefined(name: str, value: object) -> bool:
    # Restricted to INTERESTING_DUNDERS: every class has __module__,
    # __dict__, and other bookkeeping dunders that always differ from
    # object's, so comparing those never filters anything out.
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
    if budget < 4:  # No room for text plus the ellipsis
        return "..."[:max(budget, 0)]
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
    exclude: Sequence[str] = (),
) -> None:
    # For a class, the class; for an instance, its class:
    cls = obj if inspect.isclass(obj) else type(obj)
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

Importing into any example works because the example tooling puts `utils/` on the import path,
not because Python searches other directories automatically.
`tools/run_examples.py` sets `PYTHONPATH` to the tree's `utils/` directory before running each script.
The same directory reaches pytest through `pythonpath` in `pyproject.toml`.
Without either, `from display import display_object` fails with `ModuleNotFoundError`.

### Sorting Members into Attributes and Methods

`display_object()` walks every member that `inspect.getmembers_static()` returns.
The static variant reads members from the object and its classes directly,
without invoking descriptors, properties, or `__getattr__()`.
Inspecting an object therefore never runs its code or triggers a side effect,
which matters when you point this tool at something unfamiliar.

The tool sorts each member into one of two lists.
Callables become methods,
printed with the signature that `inspect.signature()` reports,
or `(...)` when a built-in has no inspectable signature.
Everything else becomes an attribute, printed as `name: type = value`.
The declared type comes from the class annotations,
gathered across the whole inheritance chain with `inspect.get_annotations()`.
An attribute with no annotation, such as one assigned dynamically,
prints as `name = value`.
The value is the member's `repr()`,
truncated to keep the line within `max_width`.

An attribute tagged `[CV]`, for *class variable*,
does not live in `obj`'s own `__dict__`.
A class has no instance-level storage for the comparison:
every attribute `display_object()` shows for a class already lives on that class or a base class,
so all of them carry the tag.
In [Comparing Ordinary Classes and Data Classes](12_Data_Classes_as_Types.md#comparing-ordinary-classes-and-data-classes),
`classvar_dataclass.py`'s `show(D)` tags both `D.x` and `D.s`,
even though `D` declares them directly, because neither belongs to an instance.
For an instance, the tag distinguishes storage borrowed from the class from storage that lives on the object,
the same rule `Stars.rating` demonstrates in [Class Attributes](09_Class_Attributes.md#class-attributes-are-not-default-values).
`class_with_defaults.py`'s `show(B())`, from that same chapter 12 comparison,
tags `B.x` and `B.s`,
while `display_object(Messenger("foo", 12, 3.14))` tags none,
since `@dataclass` assigns every field straight onto the new instance.
The tag reports this dynamically, from where the value lives,
so it applies whether or not the attribute's declaration uses `typing.ClassVar`.

### Choosing Which Dunders to Show

`display_object()` hides standard dunder members by default.
Pass their names in `dunder` to keep specific ones,
as `new_vs_init.py` does to show `__new__` and `__init__`.
Pass the `ALL_DUNDERS` sentinel instead to keep every dunder member,
including the interpreter's own machinery.
`dunder`'s type is `Sequence[str] | ALL_DUNDERS | REDEFINED_DUNDERS`,
naming each sentinel value rather than the generic `sentinel` class,
so a type checker narrows `dunder` to `Sequence[str]` once it rules out both sentinels,
and `name in dunder` needs no further guard.
`ALL_DUNDERS` is useful for exploring an unfamiliar object,
but it buries a class's own choices under everything `object` and the interpreter add.
`INTERESTING_DUNDERS` names the four a reader typically customizes when defining a class:
`__init__`, `__repr__`, `__eq__`, and `__hash__`.
Pass it as `dunder` to see those four without the surrounding noise.

A class that overrides none of the four still shows all four,
because it inherits `object`'s versions,
and the report cannot tell those from ones the class wrote.
`REDEFINED_DUNDERS` filters harder: among those same four,
it keeps only the ones whose value differs from `object`'s own,
so a class that overrides none of them shows no dunders.
`_redefined()` checks membership in `INTERESTING_DUNDERS` before comparing,
deliberately narrowing the comparison to those four.
The two modes side by side,
on a class that redefines nothing and one that redefines almost everything:

```python
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

display_object(Point, REDEFINED_DUNDERS, exclude=("__hash__",))
#: [Attributes]
#:   None
#: [Methods]
#:   • __eq__(self, other)
#:   • __init__(self, x: int, y: int) -> None
#:   • __repr__(self)
```

`Plain` writes none of the four,
so `INTERESTING_DUNDERS` shows `object`'s versions and `REDEFINED_DUNDERS` shows nothing.
`@dataclass` writes three of them and sets `__hash__` to `None`,
which is why `Point` reports a `__hash__` attribute rather than a method.
The last call drops that row,
the same reason `comparison.py` in [Data Classes as Types](12_Data_Classes_as_Types.md#comparing-ordinary-classes-and-data-classes)
passes `exclude=("__hash__",)`.

Every class, even an empty one, has its own `__module__`, `__dict__`,
and a handful of other bookkeeping dunders that never match `object`'s,
so comparing every dunder this way shows that bookkeeping instead of filtering it out.
The comparison uses `is`, not `==`,
since a dunder inherited unchanged from `object` is the same function object,
not merely an equal one.

`exclude` drops specific names regardless of what `dunder` would otherwise show,
and it applies to any member, not just dunders.
`display_object(obj, REDEFINED_DUNDERS, exclude=("__hash__",))` shows whatever `REDEFINED_DUNDERS` finds redefined,
minus `__hash__`, useful when a listing has already made that particular point and repeating it only adds noise.
The check runs first, before the `dunder` logic sees the name,
so an excluded name never reaches `[Attributes]` or `[Methods]` no matter which mode selects it.

### The Tool in Use

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
`display_object(Fraggle)` inspects the class object.
It lists `y` and `z`, the fields with defaults.
`x`'s declaration is `x: int` with no default,
so on the class it is only an annotation, not a bound attribute,
and `getmembers_static()` does not return it.

`display_object(Fraggle(9, 2.3))` inspects an instance,
whose attributes hold its field values, so `x` now appears beside `y` and `z`.
The method list is the same either way, because methods live on the class.

The third call passes `ALL_DUNDERS`.
A `@dataclass` produces many of these:

- `__dataclass_fields__`
- `__dataclass_params__`
- `__match_args__`
- `__replace__`
- `__hash__`, set to `None`
- `__init__`, `__eq__`, and `__repr__`

The generated `__init__`, `__eq__`, and `__repr__` give `Fraggle` a constructor,
equality, and a `repr()` that you never wrote.

The rest is the bookkeeping every class carries.

## Which Hook for Which Job

Every hook in this chapter is an ordinary function that Python calls at a known moment during class construction.
Putting them all in one class shows the sequence:

```python
# hook_order.py
from typing import Any

class Watched:
    def __set_name__(self, owner: type, name: str) -> None:
        print(f"__set_name__({owner.__name__}, {name})")

class Meta(type):
    @classmethod
    def __prepare__(cls, name: str, bases: tuple[type, ...],
                    **kwargs: Any) -> dict[str, Any]:
        print(f"__prepare__ {name}")
        return {}

    def __new__(mcls, name: str, bases: tuple[type, ...],
                nmspc: dict[str, Any]) -> type:
        print(f"__new__ {name} enter")
        cls = super().__new__(mcls, name, bases, nmspc)
        print(f"__new__ {name} exit")
        return cls

    def __init__(cls, name: str, bases: tuple[type, ...],
                 nmspc: dict[str, Any]) -> None:
        super().__init__(name, bases, nmspc)
        print(f"__init__ {name}")

def tag[T: type](cls: T) -> T:
    print(f"decorator {cls.__name__}")
    return cls

class Base(metaclass=Meta):
    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        print(f"__init_subclass__ {cls.__name__}")
#: __prepare__ Base
#: __new__ Base enter
#: __new__ Base exit
#: __init__ Base

@tag
class Derived(Base):
    field = Watched()
    print("class body")
#: __prepare__ Derived
#: class body
#: __new__ Derived enter
#: __set_name__(Derived, field)
#: __init_subclass__ Derived
#: __new__ Derived exit
#: __init__ Derived
#: decorator Derived
```

`Base`'s four lines are the bare sequence,
and they also show that `Base.__init_subclass__()` never runs for `Base` itself,
the rule [Making a Class Final](#making-a-class-final) needs.
`Derived` adds the rest.
`__prepare__()` runs before the body, which is why its line comes first.
The body then executes, printing `class body`.
`__set_name__()` and `__init_subclass__()` both run between `__new__ Derived enter` and `__new__ Derived exit`,
because `type.__new__()` calls them as it assembles the class,
so they are not merely "after the body" but inside the metaclass's own construction step.
The decorator is last, because it receives a class that is already finished.

Knowing that sequence picks the hook for the job:

- React to each new subclass: `__init_subclass__()`.
- Let a class attribute learn its own name: `__set_name__()`.
- Rewrite a finished class: a class decorator.
- Build a family of classes from data: `type()` with three arguments,
  or an `exec()`ed class body when the definition is easier to read as source.
- Change the name, the bases, or the namespace before Python builds the class:
  a metaclass `__new__()`.
- Control the namespace the body executes into: `__prepare__()`.
- Decide whether an instance gets built: a metaclass `__call__()`.
- Read a class you did not write: `inspect`.

None of this is a special facility bolted onto the language.
A class is an object that Python builds at run time by executing its body,
and `hook_order.py` displays each step of that construction as it runs.
The one hook missing from its trace is `__call__()`, which runs later still,
each time someone calls the finished class.

## Exercises

1.  In `init_subclass.py`,
    add a class `Yellow(Color)` and then `MutedYellow(Yellow)`.
    Predict `Color.registry` after each new class, then confirm.
2.  In `set_name.py`, add a third `Field()` attribute, `z`, to `Point`,
    set `p.z = 9`, and confirm `p.__dict__` now also holds `_z`.
3.  In `singleton.py`, add a third class `CSingleton(metaclass=Singleton)` and confirm `c1 = CSingleton(); c2 = CSingleton(); c1 is c2` is `True`,
    while `c1 is a` (comparing across the different singleton classes)
    is `False`.
4.  Extend `final_runtime.py` so a class declares itself final with a keyword in its header,
    `class B(A, final=True):`,
    using the `**kwargs` that `__init_subclass__()` receives.
    Confirm that a non-final sibling of `B` still subclasses freely.
5.  Using `inspect_tour.py` as a model,
    write a function `describe(func)` that prints a function's name,
    its `inspect.signature()`, and its docstring
    (or `"(no docstring)"` if `inspect.getdoc()` returns `None`),
    then call it on `greet` and on a lambda.
6.  Delete the `# type: ignore` comment from `metaclass_layout_conflict.py` and run ty over the file.
    Compare the `instance-layout-conflict` diagnostic it reports with the `TypeError` the program prints:
    the static report and the runtime failure describe the same collision.
7.  Using `type()` directly, build a class `Celsius` with a base of `float`,
    an attribute `unit = "C"`,
    and a method `describe(self)` returning `f"{self} degrees {self.unit}"`.
    Confirm `Celsius(21.5).describe()` works and that `type(Celsius)` is `type`.
8.  In `new_vs_init.py`,
    move the `bases += (Tag,)` line from `__new__()` into `__init__()` and predict what happens before running it.
    Explain the result in terms of when the class object comes into existence.
9.  `commander.py` validates `class_name` against `KNOWN_COMMANDS` before splicing it into source text.
    Remove that check, call `Command.make_class()` with a name containing a newline and a second statement,
    and confirm that the injected statement runs.
    Restore the check.
10. Change `prepare_namespace.py`'s `NoDuplicates` so that instead of raising an exception,
    it keeps the *first* definition of a duplicated name and discards the later one.
    Confirm that `Handlers().on_open()` then runs the first `on_open`.
    Explain why no class decorator could achieve the same thing.

[^crtp]: C++ templates can do this via the *Curiously Recurring Template Pattern*
(CRTP):

    ```cpp
    template <typename T>
    class Singleton {
    public:
        static T& instance() {
            static T inst;
            return inst;
        }
    };

    class ASingleton : public Singleton<ASingleton> {};
    ```

    The C++ compiler instantiates templates on demand,
    rather than executing them the way Python executes a `class` statement.
    A C++ class name is a valid *incomplete type*
    the moment the compiler sees `class ASingleton`,
    before it reads a single member.
    `Singleton<ASingleton>` can use that name as its template argument
    while the class remains incomplete.
    The compiler does not compile its member functions until something calls them,
    by which point `ASingleton` is complete.

    Python evaluates `Singleton[ASingleton]` eagerly,
    before it binds the name `ASingleton`,
    and offers no equivalent incomplete-type stage to exploit.

[^parametrize]: Four spellings are in use, all correct.
    The stem is `parametr-` or `parameter-`.
    The suffix is `-ize` in the US
    or `-ise` in the UK and Commonwealth countries.
    The two choices are independent,
    giving `parametrize`, `parametrise`, `parameterize`, and `parameterise`.
    This book follows pytest's own spelling for `@pytest.mark.parametrize`,
    and uses "parameterize" everywhere else,
    for the general sense of a class or function taking a parameter.
