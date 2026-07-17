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

Note that `x` sees the changes made to the class *after* `x` was created.
The instance itself never changed; its `__dict__` is as empty as before.
Attribute lookup on an instance falls through to its class,
so a change to a class reaches every object of that class,
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
- `__set_name__()` lets a class attribute learn its own name,
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

class EventMakers(dict[str, EventMaker]):
    def __getitem__(self, class_name: str) -> EventMaker:
        if class_name not in self:
            raise ValueError(f"Unknown event class: {class_name!r}")
        if super().__getitem__(class_name) is NOT_CREATED:
            print(f"Creating {class_name}")
            # Local function to pass to type constructor:
            def init(self: Event, hour: int, minute: int) -> None:
                Event.__init__(self, class_name, hour, minute)
            new_cls = type(class_name, (Event,), {"__init__": init})
            self[class_name] = cast(EventMaker, new_cls)
        return super().__getitem__(class_name)

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

`load_schedule()` reads that file, filtering out blank lines and comments,
then builds an `Event` from each resulting line.
`line.replace(":", " ").split()` turns `"WaterOn 3:30"` into three plain strings in a single step,
replacing the colon with a second space before splitting on whitespace.
`Event._event_maker[class_name]` gets the class object used to build that `Event`.
The first time an event type is needed,
the class is built and registered under its name.

`Event._event_maker` comes pre-populated with the seven legitimate event names,
each paired with the `NOT_CREATED` sentinel as a placeholder.
Populating that dict does not build any classes.
It only reserves the names,
so `EventMakers.__getitem__()` has something to check a `class_name` against before building anything.

The `init()` function nested inside `EventMakers.__getitem__()` calls `Event.__init__(self, ...)` directly instead of `super().__init__(...)`.
`init()` is a nested function, not a method defined inside a `class` statement,
so the compiler never gives it the `__class__` cell that zero-argument `super()` needs.

## Generating Classes with `exec()`

The `type` approach in the previous section builds a class from a name,
a tuple of bases, and a namespace dict.
A second way is to write an ordinary `class` statement in an f-string,
then `exec()` that string as code.
The class definition (`klass`) is easier to read and modify:

```python
# commander.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import ClassVar, cast
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

`make_class()` execs `klass` into a private `namespace` dict rather than the module's namespace,
seeded with `{"Command": Command}` so the generated class can find its base.
The type checker can't see into the string,
so it believes `namespace[class_name]` is a plain `type[Command]` whose constructor takes a `label` argument.
`cast(Callable[[], Command], ...)` records the actual no-argument signature at the one place the class is created,
the same idiom `greenhouse.py` uses for `EventMaker`.
Unlike `EventMakers`, `make_class()` caches nothing:
calling `make_class("Start")` twice builds two distinct classes.

`__init__` is defined textually inside a `class` block.
The compiler doesn't care that the block arrived as a string.

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
`__init_subclass__()` is called automatically for every new subclass,
so it only takes a few lines to produce self-registration.
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
Creating `PhthaloBlue` and `CeruleanBlue` removed their base `Blue`,
leaving those two leaves beside `Green` and `Red`.
For the same reason, `Round` is missing from the `Shape` registry.
Creating `Circle`, a subclass of `Round`, removed `Round`,
leaving `Circle` and `Square`.
This involves no metaclass.
`__init_subclass__()` is implicitly a class method.
Its first argument is the new subclass.

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

## Learning a Name with `__set_name__()`

A *descriptor* is any object whose class defines at least one of `__get__()`,
`__set__()`, or `__delete__()`.
Most descriptors define `__get__()` and add the others as needed.
Assigned to a class attribute, a descriptor takes over access to that attribute.
Instead of going straight to the instance's `__dict__`,
`__get__()` is called on a read and `__set__()` on a write.
[Decorators](14_Decorators.md#a-limitation-methods-need-a-descriptor)
already relied on this without naming it.
A function is an object like any other, and its class defines `__get__()`,
which makes every function a descriptor:

```python
# function_is_descriptor.py
class Person:
    def __init__(self, name: str) -> None:
        self.name = name

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

Here is another job that once needed a metaclass.
In `x = Field()` below, `Field()` runs before the assignment,
so the new instance cannot know it is about to be bound to the name `x`.
Python delivers that name automatically.
When a `class` body finishes executing,
it calls `__set_name__(owner, name)` on every class attribute that defines it,
not only descriptors,
passing the freshly created class and the name the attribute was assigned to.
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
From then on, every read and write routes through the descriptor instead of going straight to the instance's `__dict__`.
`p.x = 3` prints `x.__set__ = 3` before anything is stored.
In `print(p.x, p.y)`, Python evaluates both arguments before calling `print()`,
so both `__get__` lines appear ahead of `3 4`.
The final access, `Point.x`, goes through the class rather than an instance,
so `__get__()` receives `obj=None` and reports `via class`.
That branch returns `self`, the descriptor object itself,
which is why `isinstance(Point.x, Field)` is `True`.

Each `Field` stores values under `_x` or `_y` in the instance's `__dict__`.
The underscore prefix is not decoration.
A descriptor that defines `__set__()` is a *data descriptor*,
and on every lookup a data descriptor outranks the instance's `__dict__`.
If `__get__()` asked `obj` for plain `"x"`,
that lookup would route back to the descriptor and call `__get__()` again,
forever.
Storing under `"_x"`, a name no descriptor claims, breaks the loop.
This is metaprogramming, but it needs no metaclass.

Testing confirms the descriptor learns its name,
stores each value under the storage key built from that name,
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

Since a metaclass is itself a subclass of `type`,
writing `class Simple1(SimpleMeta1):` would mean something else.
That syntax makes `SimpleMeta1` an ordinary base class,
so `Simple1` would become a metaclass-shaped class,
not a class built by `SimpleMeta1`.
`metaclass=` is the particular mechanism for naming what builds a class,
independent of its base classes.
A subclass only needs to repeat `metaclass=` if its own bases do not already carry the same metaclass.
Python computes a new class's metaclass from all of its bases automatically.

```python
# simple_meta1.py
from typing import Any
from display import display_object

class SimpleMeta1(type):
    def __init__(cls, name: str, bases: tuple[type, ...],
                 nmspc: dict[str, Any]) -> None:
        super().__init__(name, bases, nmspc)
        setattr(cls, "uses_metaclass", lambda self: "Yes!")

class Simple1(metaclass=SimpleMeta1):
    def foo(self) -> None: pass

    @staticmethod
    def bar() -> None: pass

display_object(Simple1)
#: [Attributes]
#:   None
#: [Methods]
#:   • bar() -> None
#:   • foo(self) -> None
#:   • uses_metaclass(self)
print(Simple1().uses_metaclass())  # type: ignore
#: Yes!
```

`SimpleMeta1.__init__()` runs once, as the `class Simple1` statement finishes,
and patches a new method onto the freshly built class.
In the `display_object` listing,
`uses_metaclass(self)` sits alongside `foo` and `bar`,
indistinguishable from the methods written in the class body.
The injected value is a plain lambda, but a function is a descriptor
([Learning a Name with `__set_name__()`](#learning-a-name-with-__set_name__)),
so `Simple1().uses_metaclass()` binds it like any other method.

By convention the first argument of a metaclass method is `cls` rather than `self`,
except for `__new__()`, which uses `mcl` (metaclass);
here `cls` is the class object under construction, `Simple1`.
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
as on `Simple1().uses_metaclass()` above;
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

`added_in_init` never appears because `type.__new__()` copies `nmspc` into the new class's own `__dict__` as it builds the class.
By the time `__init__()` runs, the two mappings are independent,
so mutating the original dict changes nothing the class can see.
`setattr(cls, ...)` still works because it modifies the class object itself.

Override `__new__()` when you must change `name`, `bases`, or the namespace
(including special members like `__slots__`) before Python builds the class.
Otherwise, prefer `__init__()`, which is simpler.
When the choice does not matter,
pick `__init__()` and reserve `__new__()` for a genuine need.

## Intercepting Instance Creation

A method defined on the metaclass becomes a method of the *class object*,
callable on the class but not on its instances.
These are sometimes called *metamethods*,
and they differ from `classmethod`s because a `classmethod` stays callable on both the class and its instances,
while a metamethod works only through the class.
The class is an instance of the metaclass.
The class's own instances are not.

One useful metamethod is `__call__()`.
It is the same method that makes any object callable when parentheses are attached.
`obj()` invokes `type(obj).__call__(obj, ...)`.
A class is an object, an instance of its metaclass,
so `ClassName()` invokes `__call__()` on the metaclass the same way.
It is the first thing that runs when you create an instance of the class.
The only reason `__new__()` and `__init__()` normally run is because the default `type.__call__()` calls them.
A metaclass that overrides `__call__()` sits above that step and decides whether to call them at all.
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
            Singleton._instances[cls] = type.__call__(
                cls, *args, **kwargs)
        return Singleton._instances[cls]

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
so the singletons are independent.
The `[T]` on `__call__()` ties its return type to `cls`,
so a type checker sees `ASingleton()` as an `ASingleton` instead of `Any`.
Without it, every singleton would lose its type and a type checker could no longer catch a misspelled attribute access on the result.

You might expect to parameterize[^parametrize] the class itself,
with `class Singleton[T](type)` and `_instances: ClassVar[dict[type, T]]`.
That does not work.
A `ClassVar` cannot depend on a type parameter of its own class,
because `ClassVar` means one shared value for the whole class,
not a different value per instantiation.
Even ignoring that, a subclass would need to write `class ASingleton(metaclass=Singleton[ASingleton]):`,
naming `ASingleton` before its class body finished defining it.[^crtp]
The method-level `[T]` on `__call__()` avoids both problems.
It binds `T` from `cls` at the call site, `ASingleton()`,
which runs only after `ASingleton` already exists.

This works, but it is heavier than the problem usually requires.
[Singleton](24_Singleton.md) covers the lighter alternatives,
from a class decorator down to a module.
Choose the lightest tool that solves your problem.

### Multiple Inheritance in a Metaclass

`Singleton` stores its cache in `_instances`, which is a `dict` attribute.
It doesn't inherit from `dict` directly.
That raises a natural question.
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

The `# type: ignore` comment is there because ty knows this rule statically.
Its `instance-layout-conflict` check reports at check time the very `TypeError` this example exists to demonstrate at run time.
A checker that predicts a crash before the program ever runs is static typing at its best;
the comment suppresses the diagnostic only because raising that crash is the point.

A metaclass can multiply inherit like any other class,
as long as the extra class is a plain mixin with no competing layout:

```python
# mixin.py
class Mixin:
    def helper(self) -> str:
        return "hi"

class Base(type, Mixin):
    pass

class Derived(metaclass=Base):
    pass

print(Derived.helper())
#: hi
```

The constraint here is the ordinary "at most one layout-bearing base" rule that governs every Python class,
not something specific to metaclasses.
Composing a `dict`, the way `Singleton._instances` already does,
sidesteps the conflict.

## Making a Class Final

It is sometimes useful to forbid inheritance.
The modern way to say so is the `typing.final` decorator:

```python
# final.py
from typing import final

@final
class B:
    pass

b = B()
print(type(b).__name__)
#: B
```

The type checker rejects `class C(B): ...` because it would inherit a `final` class.

Type checkers such as ty, mypy, and pyright check `@final` statically.
It states the intent and catches a violation before the code runs.
At runtime it only marks the class, setting `__final__ = True`
(as `test_final.py` below confirms).
Nothing enforces it and the interpreter still runs `class C(B): pass`.

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

The check happens at class-creation time.
Python builds `B` normally because `A` does not forbid subclassing.
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

## When You Still Need a Metaclass

After all this, when is a metaclass the right tool?
When you need to change the class object rather than react to its creation:

- Adding methods *to the class*
  (metamethods such as a custom `__iter__()` or `__call__()` on the class, shown above).
- Replacing the namespace mapping with `__prepare__()` so the class body populates a custom dictionary.
- Enforcing an invariant across an entire family of classes through their shared metaclass.

These are real but uncommon.
For everything else, `__init_subclass__()`, `__set_name__()`,
and class decorators are simpler and easier to read.

One caution: a class has a single metaclass.
Multiple inheritance can accidentally combine classes with different metaclasses:

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

This creates a metaclass conflict you must resolve.
It's one more reason to avoid metaclasses (and arguably, multiple inheritance)
unless you truly need them.

## The `inspect` Module

Up to now we've been modifying classes.
`type` builds them, and metaclasses and `__init_subclass__()` run code during their creation.
The `inspect` module is the other half of metaprogramming.
`inspect` reads the structure of live objects.
It answers questions like:

- Which members an object has
- What a function's signature is
- What its docstring says

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
Type annotations (a.k.a. type hints) are not discarded at runtime.
Python keeps them attached to the function and evaluates them on demand,
the deferred evaluation of PEP 649,
even though it [never checks them](08_Static_Typing.md#hints-are-not-enforced-at-run-time).
`signature()` requests that stored data (not the original source text)
to build the `Signature` object.
The `ALL_DUNDERS` listing at the end of this chapter shows the machinery on a class:
`__annotate_func__` is the code that computes the annotations,
and `__annotations_cache__` holds the result after the first request.

Throughout the book we've been using `display_object()` to show the layout of an object.
The `utils/` prefix makes it live in the shared `utils/` directory at the top of the `Examples` tree,
and any chapter can import it:

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
    exclude: Sequence[str] = (),
) -> None:
    # For a class, the class itself; for an instance, its class:
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

`display_object()` hides standard dunder members by default.
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
`INTERESTING_DUNDERS` names the four a reader typically customizes when defining a class:
`__init__`, `__repr__`, `__eq__`, and `__hash__`.
Pass it as `dunder` to see those four without the surrounding noise.

A class inherits all four of those from `object` without overriding any of them,
so `INTERESTING_DUNDERS` shows `object`'s generic versions,
which can look like the class defined them itself.
`REDEFINED_DUNDERS` filters harder: among those same four,
it keeps only the ones whose value differs from `object`'s own,
so a class that overrides none of them shows no dunders.
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
The method list is the same either way, because methods live on the class.

The third call passes `ALL_DUNDERS`.
A `@dataclass` produces many of these:

- `__dataclass_fields__`
- `__match_args__`
- `__replace__`
- `__hash__`, set to `None`
- The generated `__init__`, `__eq__`, and `__repr__`,
  which give `Fraggle` a constructor, equality, and a `repr()` for free.

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
6.  Delete the `# type: ignore` comment from `metaclass_layout_conflict.py` and run ty over the file.
    Compare the `instance-layout-conflict` diagnostic it reports with the `TypeError` the program prints:
    the static report and the runtime failure describe the same collision.

[^crtp]: C++ templates can do this via the *Curiously Recurring Template Pattern*
(CRTP):

    ```cpp
    template <typename T>
    class Singleton {
        static T& instance() {
            static T inst;
            return inst;
        }
    };

    class ASingleton : public Singleton<ASingleton> {};
    ```

    C++ templates are instantiated by the compiler on demand,
    not executed like Python's `class` statement.
    A C++ class name is a valid *incomplete type*
    the moment the compiler sees `class ASingleton`,
    before it reads a single member.
    `Singleton<ASingleton>` can use that name as its template argument
    without the class being finished.
    Its member functions are not compiled until something actually calls them,
    by which point `ASingleton` is complete.

    Python evaluates `Singleton[ASingleton]` eagerly,
    before the name `ASingleton` is even bound,
    so there is no equivalent incomplete-type stage to lean on.

[^parametrize]: Four spellings are in use, all correct.
    The stem is `parametr-` or `parameter-`.
    The suffix is `-ize` in the US
    or `-ise` in the UK and Commonwealth countries.
    The two choices are independent,
    giving `parametrize`, `parametrise`, `parameterize`, and `parameterise`.
    This book follows pytest's own spelling for `@pytest.mark.parametrize`,
    and uses "parameterize" everywhere else,
    for the general sense of a class or function taking a parameter.
