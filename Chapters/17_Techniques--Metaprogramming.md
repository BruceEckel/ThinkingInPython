# Metaprogramming

> Ordinary code makes objects.
> Metaprogramming works one level up, on the classes that make them.

Every object comes from another, special object.
These special objects are *classes*,
and you configure them to produce the objects you want.

Classes are also objects, and you can modify objects.

```python
# modify_class.py
from display import display_object

class Clay:
    pass

display_object(Clay)
#: [Attributes]
#:   None
#: [Methods]
#:   None

x = Clay()
Clay.n = 42  # type: ignore
Clay.m = lambda self: f"{self.n = }"  # type: ignore
display_object(x)
#: [Attributes]
#:   • n = 42 [CV]
#: [Methods]
#:   • m(self)
print(x.m())  # type: ignore
#: self.n = 42
print(vars(x))
#: {}
```

Attribute lookup on an instance falls through to its class,
so a lookup on any object of that class finds a change to the class,
including on objects created before the change.
The instance stays as it was.
`vars(x)` shows `x`'s instance dictionary still empty.

What creates these "class" objects?
Other special objects, called *metaclasses*.
The default metaclass is `type`, and almost every class needs no other.
You can customize how Python produces classes by running extra code or injecting members as it builds each class.
That is metaclass programming.

You have used metaclasses without writing one.
`abc.ABCMeta` builds [`abc.ABC`](20_Patterns--Rethinking_Objects.md#abstract-base-classes),
and makes a class with an unimplemented abstract method refuse instantiation.
`enum.EnumType` builds each `Enum` subclass,
turning every class-body assignment into a member and making `for c in Color` walk them.
Iterating over a class is behavior on the class object,
and a metaclass puts behavior there.
An ordinary class cannot.

You rarely need a metaclass.
It is a fascinating tool and tempting to use,
but simpler hooks cover almost every case a metaclass handled before those hooks existed:

- `__init_subclass__()` runs at subclass creation.
  It replaces most "do something at each class definition" metaclasses.
- `__set_name__()` gives a class attribute its own name, at class-creation time.
- [*Class decorators*](14_Techniques--Decorators.md#decorating-classes)
  transform a class after Python builds it.

Use a metaclass only when these cannot do the job.

## Generating Classes with `type()`

Since metaclasses create classes, you can call the metaclass yourself.
`type()` with one argument gives the type of an existing object.
`type()` with three arguments creates a new class.
These arguments are the name, a tuple of base classes,
and a namespace dictionary of fields and methods.
A class definition is shorthand for calling `type()`:

```python
# class_via_type.py
class C:
    pass

D = type("D", (), {})  # The class statement, as a call

print(type(C), type(D))
#: <class 'type'> <class 'type'>
# Both inherit object:
print(C.__bases__, D.__bases__)
#: (<class 'object'>,) (<class 'object'>,)
# Both make ordinary instances:
print(isinstance(C(), C), isinstance(D(), D))
#: True True
```

The tuple of bases and the namespace dictionary add bases, fields, and methods:

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
#:   • index(self, value, start=0, stop=92233720368547758...
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

Printing the class of the class produces the metaclass.

### A Family of Generated Classes

Generating classes with `type()` suits a family of classes that differ only by name.
A greenhouse controller runs scheduled events, one class per kind of event.
One module holds the base class `Event`, the seven event names, and `make()`,
which builds the class for one name:

```python
# events.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

type Hour = int
type Minute = int

@dataclass
class Event:
    action: str
    hour: Hour
    minute: Minute

type EventMaker = Callable[[Hour, Minute], Event]
NAMES: Final[frozenset[str]] = frozenset({
    "ThermostatDay", "ThermostatNight", "LightOn",
    "LightOff", "WaterOn", "WaterOff", "RingBell",
})

def make(name: str) -> EventMaker:
    def init(self: Event, hour: Hour,
             minute: Minute) -> None:
        Event.__init__(self, name, hour, minute)
    new_cls = type(name, (Event,), {"__init__": init})
    return new_cls
```

A dict comprehension builds all seven classes:

```python
# eager_event_classes.py
from events import NAMES, Event, make

makers = {name: make(name) for name in NAMES}
print(len(makers))
#: 7
light = makers["LightOn"](1, 0)
water = makers["WaterOff"](2, 0)
print(light)
#: LightOn(action='LightOn', hour=1, minute=0)
print(isinstance(light, Event))
#: True
print(type(light) is type(water))
#: False
```

Each generated class is a real type, not a label.
`light` and `water` belong to distinct subclasses of `Event`,
so `isinstance()` with one of those subclasses tells them apart.

Type checkers read different amounts of a `type()` call.
`ty` reads the bases and a namespace written as a dict literal.
It takes the constructor from the `"__init__"` entry,
so it infers that each generated class takes an hour and a minute.
It then checks `return new_cls` against `EventMaker`,
the two-argument signature `make()` declares.
If `init()` gains a third parameter,
`ty` reports an `invalid-return-type` that names the extra parameter.
Pyright builds the class from its bases alone,
so it gives the class `Event`'s three-argument constructor and rejects `return new_cls`.
Under Pyright `make()` needs `cast(EventMaker, new_cls)`.
Under mypy the result is an unknown class, so mypy accepts either form.

Under `ty` a cast replaces a check with a claim,
the distinction [Where Enforcement Lives](#where-enforcement-lives) draws.
The cast states the signature.
The checker takes that statement on trust.

`make()` exists so that each `init()` closes over its own `name`.
A lambda written inline in the comprehension closes over the comprehension's variable,
so every generated class records the last name the comprehension visits as its `action`.
That is the [late-binding trap](27_Patterns--Function_Objects.md#the-late-binding-trap)
that `late_binding.py` demonstrates.

`init()` calls `Event.__init__(self, ...)` by name instead of `super().__init__(...)`.
It is a nested function, not a method defined inside a `class` statement,
so the compiler gives it no `__class__` cell for zero-argument `super()` to use.

### Building Each Class on First Lookup

The dict comprehension in `eager_event_classes.py` builds all seven classes whether the schedule uses them or not.
Seven classes are few enough to build up front.
With hundreds, the schedule uses few of the classes the comprehension builds.
So the next version delays building each class until the first lookup of its name.
Delaying the build takes a `dict` subclass that calls `make()` from `events.py` when a lookup misses:

```python
# greenhouse.py
from events import NAMES, EventMaker, make

class EventMakers(dict[str, EventMaker]):
    def __missing__(self, name: str) -> EventMaker:
        if name not in NAMES:
            raise KeyError(f"Unknown event class: {name!r}")
        print(f"Creating {name}")
        new_cls = make(name)
        self[name] = new_cls
        return new_cls

    def built(self) -> str:
        return (f"{len(self)} of {len(NAMES)}"
                " event classes built")
```

`EventMakers` subclasses `dict`,
so the call site `makers[name]` reads as an ordinary lookup.
When the key is absent,
`dict.__getitem__()` calls `__missing__()` and returns its result.
The next lookup of that name finds the stored class,
so `__missing__()` builds each class once.
Without `__missing__()`,
every caller checks for the name and builds the missing class.

A new `EventMakers` starts out empty.
`__missing__()` checks a name against `NAMES` before building anything,
so every key the dict acquires names a declared event.

```python
# greenhouse_demo.py
from typing import Final, cast
from greenhouse import EventMakers

SCHEDULE: Final[tuple[tuple[str, int, int], ...]] = (
    ("LightOff", 2, 0),
    ("LightOn", 1, 0),
    ("RingBell", 7, 0),
    ("LightOn", 8, 0),
)
makers = EventMakers()
events = [makers[name](hour, minute)
          for name, hour, minute in SCHEDULE]
#: Creating LightOff
#: Creating LightOn
#: Creating RingBell
print(makers.built())
#: 3 of 7 event classes built
bell = cast(type, makers["RingBell"])
for event in sorted(
        events, key=lambda e: (e.hour, e.minute)):
    prefix = "* " if isinstance(event, bell) else ""
    print(f"{prefix}{event.hour}:{event.minute:02d}"
          f": {event.action}")
#: 1:00: LightOn
#: 2:00: LightOff
#: * 7:00: RingBell
#: 8:00: LightOn
```

On the first lookup of an event type,
`EventMakers` builds the class and registers it under its name,
so `LightOn` gets one `Creating` line though `SCHEDULE` names it twice.
An unknown name raises a `KeyError`, as a missing key in any `dict` does,
so a `try: ... except KeyError` around a lookup catches it.

The demo's loop over the sorted events uses the type distinction.
A distinct subclass lets each event carry its kind as its type,
where `isinstance()` or a `match` class pattern can test it.

Calling the base class, `Event(name, hour, minute)`, sets the same `action`,
`hour`, and `minute` as a generated class does, but every entry shares one type.
The loop then has no `RingBell` class for `isinstance()` to test.
The `* ` marker depends on `RingBell` being a distinct class,
not just a distinct name.

The demo wraps its `RingBell` lookup in `cast(type, ...)`.
`EventMakers` declares its values as `EventMaker`, a callable,
and `isinstance()` requires a class,
so without the cast the type checker reports an `invalid-argument-type`.
Every value `__missing__()` stores is a class that `type()` built,
so the cast states that each value is a class,
a fact the declared type leaves out.

## Generating Classes with `exec()`

The `type()` approach in `events.py` builds a class from a name,
a tuple of bases, and a namespace dict.
A second way is to write an ordinary `class` statement in an f-string,
then `exec()` that string as code.
Here, `klass` holds that class body,
which is easier to read and modify than a namespace dict:

```python
# commander.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import ClassVar, cast
from exceptions import expected

@dataclass
class Command:
    label: str
    KNOWN_COMMANDS: ClassVar[set[str]] = {
        "Start", "Stop", "Pause"}

    def run(self) -> str:
        return f"Running {self.label}"

    @classmethod
    def make_class(
        cls, class_name: str) -> Callable[[], Command]:
        if class_name not in cls.KNOWN_COMMANDS:
            raise ValueError(
                f"Unknown command: {class_name!r}")
        klass = f"""
class {class_name}(Command):
    def __init__(self) -> None:
        super().__init__("{class_name}")
"""
        namespace: dict[str, object] = {"Command": Command}
        exec(klass, namespace)
        return cast(Callable[[], Command],
                    namespace[class_name])

for name in ("Start", "Stop", "Pause"):
    command_class = Command.make_class(name)
    print(command_class().run())
#: Running Start
#: Running Stop
#: Running Pause
with expected(ValueError):
    Command.make_class("Reset")
#: [ValueError] Unknown command: 'Reset'
```

`make_class()` execs `klass` into a private `namespace` dict,
not the module's namespace,
and seeds it with `{"Command": Command}` so the generated class can find its base.
`exec()` also adds a `__builtins__` entry, the dictionary of built-in names,
to any globals mapping that lacks one, so `namespace` holds more than classes.
The type checker skips the code inside the string,
so `namespace` carries the annotation `dict[str, object]`,
and `namespace[class_name]` is an `object`.
Returning an `object` where `make_class()` declares `Callable[[], Command]` draws an `invalid-return-type`.
`cast(Callable[[], Command], ...)` states the actual no-argument signature at the one place that creates the class.

The `namespace` argument also lets `make_class()` read the generated class back as `namespace[class_name]`.
Called inside a function with no namespace argument,
`exec()` writes into a snapshot of the function's local variables.
Since Python 3.13 (PEP 667), each `locals()` call in a function returns a new,
independent snapshot,
so a later `locals()` call misses a class that `exec()` defines there.
A stack frame's `f_locals` attribute returns a write-through proxy,
the supported way for a debugger to change a function's variables.

`EventMakers` stores each class it builds.
`make_class()` builds a fresh class on every call.
Calling `make_class("Start")` twice produces two distinct classes.

The `__init__()` in `klass` sits textually inside a `class` block,
and the compiler treats a block compiled from a string the same as one read from a file.
So this `__init__()` gets a `__class__` cell and can call zero-argument `super()`.
`init()` in `events.py` is a nested function rather than a method in a class body,
so it has no such cell and names `Event.__init__()` instead.

### The Injection Risk

The `klass` string is the danger in this approach.
`exec()` runs its argument with the full power of the language,
and `klass` splices `class_name` into source text as-is.
A name could hold a newline followed by a second statement.
Without validation, that statement breaks out of the `class` block and runs anything,
the same way an unescaped value breaks out of a hand-built SQL query.
The `KNOWN_COMMANDS` check prevents that injection.
Only three known names reach the template.
`make()` in `events.py` is safe from injection,
because `type(name, (Event,), ...)` treats `name` as a string value,
not as source code.
Treat `exec()` and `eval()` like string-built SQL:
safe on values you've validated,
dangerous on anything that reaches the program from outside, unchecked.

### Pickling Generated Classes

Both generators, `type()` and `exec()`, have a second limitation,
unrelated to injection.
`exec()`'s private `namespace` has no `__name__` key,
so the class body's lookup of `__name__` falls through to the built-ins,
and the class gets `__module__` set to `"builtins"`.
`pickle.dumps()` on an instance then raises a `PicklingError`,
because pickle looks the class up as `builtins.Start` and does not find it.
`inspect.getsource()` raises a `TypeError`,
because a built-in class carries no source.

`type()`-built classes fail differently.
`type()` sets `LightOn`'s `__module__` to `events`,
the module where `make()` calls `type()`.
But the `makers` dict holds the class,
and `events` has no attribute named `LightOn`.
Pickle therefore looks for `events.LightOn` and does not find that either.
`inspect.getsource()` raises an `OSError` instead of a `TypeError`.
For both generators' classes, then,
`pickle` and `inspect.getsource()` raise exceptions.
`inspect.signature()` and `inspect.getmembers_static()` still work,
as `display_object(MyList)` shows.

Pickle records a class as its module and name,
and checks that the pair leads back to the class.
If `make()` also binds each class as an attribute of its module,
`globals()[name] = new_cls`, the pair `events.LightOn` leads to `LightOn`,
and the round trip works.
`inspect.getsource()` still raises an `OSError`,
because no source file holds the class.

## Self-Registration of Subclasses

Often a base class needs to keep track of its subclasses.
Tracking subclasses is the textbook justification for a metaclass.
Python calls `__init_subclass__()` automatically for every new subclass,
so a base class can register its own subclasses in a few lines.
Here, each base class tracks its "leaf" subclasses
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
        # Keep only the leaves
        Color.registry -= set(cls.__bases__)

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
print(sorted(c.__name__ for c in Color.registry))  # [1]
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

Each new subclass removes its base classes from the registry,
which is why `Blue` is absent from the `Color` print at `[1]` and `Round` is absent from the `Shape` registry.
None of this needs a metaclass.

`__init_subclass__()` is implicitly a class method.
Its first argument is the new subclass.
`__init_subclass__()` runs for classes derived from the class whose body defines it,
and not for that class,
so neither `Color` nor `Shape` appears in its own registry.

The keyword arguments come from the subclass header.
Writing `class Blue(Color, shade="cool"):` delivers `shade="cool"` to `__init_subclass__()`,
so a subclass can configure its own registration.
The base that declares the keyword takes it as a parameter,
`def __init_subclass__(cls, shade: str = "", **kwargs: object)`,
so the keyword binds to `shade` and `kwargs` collects the rest.
`super().__init_subclass__(**kwargs)` passes `kwargs` up the chain,
so a base further up can take the keywords it declared.
If a keyword remains when the chain reaches `object.__init_subclass__()`,
that method raises a `TypeError`.

Testing shows that each registry holds only its current leaf classes,
and that the two registries are disjoint:

```python
# test_init_subclass.py
import init_subclass

def test_color_registry_holds_only_leaves() -> None:
    leaves = {c.__name__
              for c in init_subclass.Color.registry}
    assert leaves == {"Red", "Green", "PhthaloBlue",
                      "CeruleanBlue"}

def test_independent_hierarchies_have_separate_registries(
) -> None:
    shapes = {c.__name__
              for c in init_subclass.Shape.registry}
    assert "Round" not in shapes
    assert shapes == {"Square", "Circle"}
    # Neither registry leaks into the other
    assert init_subclass.Shape.registry.isdisjoint(
        init_subclass.Color.registry)
```

`__init_subclass__()` runs for every subclass definition Python executes.
The registries built on it fail in two ways that every self-registering design shares,
with or without `__init_subclass__()`.
[Factory](26_Patterns--Factory.md#hazards-of-self-registration) covers both:
a class in a module nobody imports stays out of the registry,
and keying on `cls.__name__` lets two same-named classes overwrite each other.

Functions and classes carry two names.
`__name__` is the bare name from the `def` or `class` header.
`__qualname__`, the *qualified name* from PEP 3155,
prefixes that name with the classes and functions that enclose the definition.
A class `Inner` defined in the body of `Outer` has the qualified name `Outer.Inner`.
`init()` in `events.py` has the qualified name `make.<locals>.init`,
where `<locals>` marks a definition inside a function body.
A registry or a decorator that keys on a name usually needs the qualified one,
combined with `__module__`.
Pickle finds a class or function again through that same pair.

## Attributes on a Function

A function is an object, and like most objects it carries a `__dict__`.
Assigning `f.x = 1` stores `1` in `f.__dict__` under the key `"x"`,
and the entry stays as long as the function exists.
A decorator can use that storage to mark a method.
A method decorator runs as Python executes the class body,
before the class object exists, so it cannot register the method with its class.
It can leave a mark on the function,
and `__init_subclass__()` collects the marks once Python builds the class:

```python
# marked_methods.py
from collections.abc import Callable
from typing import Any, ClassVar

def on[F: Callable[..., object]](
        event: str
) -> Callable[[F], F]:
    def mark(func: F) -> F:
        func.__dict__["event"] = event
        return func
    return mark

class Widget:
    handlers: ClassVar[dict[str, Callable[..., Any]]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        marked = {
            attr.__dict__["event"]: attr
            for attr in vars(cls).values()
            if "event" in getattr(attr, "__dict__", {})
        }
        cls.handlers = {**cls.handlers, **marked}

    def dispatch(self, event: str) -> None:
        self.handlers[event](self)

class Button(Widget):
    @on("click")
    def press(self) -> None:
        print("pressed")

    @on("hover")
    def glow(self) -> None:
        print("glowing")

    def label(self) -> str:
        return "OK"

class SubmitButton(Button):
    @on("submit")
    def send(self) -> None:
        print("sent")

print(sorted(Button.handlers))
#: ['click', 'hover']
print(sorted(SubmitButton.handlers))
#: ['click', 'hover', 'submit']
Button().dispatch("click")
#: pressed
print(Button.press.__dict__)
#: {'event': 'click'}
# ty: Function `press` has no attribute `event`:
# print(Button.press.event)
```

`mark()` returns the same `F` it receives,
so `press()` keeps its own signature through the decoration.

When the `class Button` statement finishes,
`__init_subclass__()` walks `vars(cls)`, the new class's own namespace,
and files each function that carries an `"event"` key under its event.
The namespace also holds the bookkeeping entries every class carries,
such as `__module__`, a string with no `__dict__`.
For those entries, the `{}` default in `getattr()` makes the `"event"` test false.

On the right side of the assignment,
`cls.handlers` still resolves to the base class's dictionary,
so each new table starts from the inherited handlers.
`handlers` holds the functions the class body defined, not bound methods,
so `dispatch()` passes `self` to the function it finds.

The listing writes `func.__dict__["event"]` rather than `func.event` to satisfy the type checker.
A function's type declares a closed set of attributes,
so the type checker reports `Button.press.event` as an unresolved attribute,
and it reports the assignment `func.event = event` the same way.
Every object's type declares `__dict__` as a `dict[str, Any]`,
so indexing it type-checks.

The standard library marks functions the same way.
`@abstractmethod` sets `__isabstractmethod__ = True` on the function.
`ABCMeta` collects the marked names into the class's `__abstractmethods__`,
and `object.__new__()` raises a `TypeError` for a class whose `__abstractmethods__` is nonempty.
`@final` sets `__final__`, and `@override` sets `__override__`.
`near_miss.py` in [*Template Method*](24_Patterns--Template_Method.md#hooks-and-the-misspelled-override)
reads `__final__` through `getattr()` to refuse an override at runtime.
`functools.wraps()` copies the wrapped function's `__dict__` onto the wrapper,
so the wrapper of a decorator written with `@wraps` also carries any mark applied beneath it.

A mark suits data that describes the function and that other code reads later,
as `handlers` does here.
A call count, or any state that changes with each call,
belongs in a closure variable or on a [callable object](14_Techniques--Decorators.md#a-class-form-decorator-with-state),
where the type checker verifies its type.

## Making a Class Final

Sometimes you need to forbid inheritance.
The modern way to say so is the `typing.final` decorator:

```python
# final.py
from typing import final

@final
class B:
    pass

# ty: Class `C` cannot inherit from final class `B`:
# class C(B): pass
b = B()
print(type(b).__name__)
#: B
```

Type checkers such as `ty`, mypy, and Pyright check `@final` statically.
At runtime the decorator marks the class by setting `__final__ = True`,
as `test_final.py` below confirms.
The interpreter ignores that mark, so it still runs `class C(B): pass`.

Older literature claims that making the interpreter refuse subclassing requires a metaclass.
`__init_subclass__()` does the job at each subclass creation:

```python
# final_runtime.py
from exceptions import expected

class A:
    pass

class B(A):
    def __init_subclass__(cls, **kwargs: object) -> None:
        raise TypeError(
            f"{B.__name__} is final; "
            f"you cannot subclass it")

with expected(TypeError):
    class C(B):
        pass
#: [TypeError] B is final; you cannot subclass it
```

The check runs at class-creation time.
Python builds `B` normally.
A class's own `__init_subclass__()` does not run for that class.
At `B`'s creation, Python runs the version `B` inherits from `A`,
which is `object`'s default and accepts every subclass.
Use the runtime version in the rare case where the interpreter must refuse the subclass too.

A decorator like `@final` is a *marker*.
It sets an attribute and leaves enforcement to the type checker.

The test file confirms that:

- The `@final` marker is present.
- The runtime-final class refuses subclassing.
- Its non-final base still allows it.

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

## Where Enforcement Lives

Each device for constraining a class answers one question:
who enforces a rule about a class, and when?
The language devices you have met divide into four families.

### The Four Families

`@final` and `@override` are markers.
At runtime each sets a single attribute, `__final__` or `__override__`,
that the interpreter ignores and your own code can read, as `near_miss.py` does.
The type checker enforces each marker's rule,
and [Making a Class Final](#making-a-class-final)
builds the runtime half with `__init_subclass__()`.

[`@dataclass`](12_Techniques--Data_Classes_as_Types.md) is *mirrored machinery*.
At runtime it is a code generator,
synthesizing `__init__()` and its siblings at class-creation time.
The type checker does not run the decorator.
It recognizes the name and re-implements the generator's rules statically:
the synthesized signature, the frozen write-ban, the field-ordering rule.
The typing specification mandates those rules,
so every conformant checker derives the same class.
Some rules end up enforced twice, independently.
If you declare a field without a default after one with a default,
the checker reports that field before anything runs,
while the interpreter raises its own `TypeError` at class creation.

A third family carries *two real semantics*.
`@abstractmethod` makes the checker report an abstract instantiation,
and separately makes the runtime refuse one.
[`assert_never()`](13_Techniques--Pattern_Matching.md#exhaustive-matching)
proves exhaustiveness statically and raises an `AssertionError` at runtime when a value outside the declared type reaches it.

In the fourth family, a library enforces the checker's types at runtime.
Annotations remain in the running program,
as [The `inspect` Module](#the-inspect-module) shows,
so a library can read them and check values as the program runs.

### `@dataclass_transform` Is a Claim {#dataclass-transform}

Where does the checker get its rules for `@dataclass`?
For the standard library,
the checker's authors wrote those rules into the checker.
For a class-building decorator of your own,
the checker's rules come from what you declare.
`@dataclass_transform` marks a decorator as dataclass-like,
and the declaration alone changes the class the checker infers:

```python
# claimed_transform.py
from typing import dataclass_transform
from exceptions import expect

@dataclass_transform()
def model[T](cls: type[T]) -> type[T]:
    return cls  # The claim, with nothing behind it

@model
class User:
    name: str
    age: int = 0

# The checker accepts this call:
expect(TypeError, User, "Guido", 30)
#: [TypeError] User() takes no arguments
```

The checker synthesizes `User.__init__(self, name: str, age: int = 0)` from the field declarations,
as it does for `@dataclass`.
It accepts the declaration and never runs `model()`,
so the call passes the check and fails at runtime.
This `model()` returns the class unchanged,
so `User` keeps `object`'s constructor, which takes no arguments.
The declaration is a claim, and this one is false.

Libraries like attrs and Pydantic make the claim true by generating the methods their `@dataclass_transform` declares.
The declaration then makes every checker that follows the typing specification synthesize each decorated class's constructor from its field declarations and check each call against that constructor.
The shortest `model()` that makes its claim true delegates the generation:

```python
# kept_transform.py
from dataclasses import dataclass
from typing import dataclass_transform

@dataclass_transform(frozen_default=True)
def model[T](cls: type[T]) -> type[T]:
    return dataclass(frozen=True)(cls)

@model
class User:
    name: str
    age: int = 0

u = User("Guido", 30)
print(u)
#: User(name='Guido', age=30)
# ty: Property `age` defined in `User` is read-only:
# u.age = 9
```

Now the runtime and the checker agree.
The runtime `User` is a real frozen data class,
and `frozen_default=True` tells the checker that classes built by `model()` reject assignment statically too.

`@dataclass_transform` generalizes one shape:
a decorator that builds a class's methods from its field declarations.
The checker cannot represent a class built any other way,
because it neither imports nor executes your code.
The checker emulates the constructs it recognizes, accepts what you declare,
and has no other source of information about a class.
That is why `commander.py` uses a `cast()` to state the real signature.
Its class exists only as [text in a string](#generating-classes-with-exec).

## Learning a Name with `__set_name__()`

A *descriptor* is any object whose class defines at least one of `__get__()`,
`__set__()`, or `__delete__()`.
Most descriptors define `__get__()` and add the others as needed.
When a class attribute holds a descriptor,
that descriptor takes over access to the attribute.
Instead of going to the instance's `__dict__`,
a read calls `__get__()` and a write calls `__set__()`.
[Decorators](14_Techniques--Decorators.md#a-limitation-methods-need-a-descriptor)
depends on this, naming the descriptor and leaving the protocol to this section.
A function is an object like any other, and its class defines `__get__()`,
so every function is a descriptor:

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

`plain.__get__(p, Person)()` is `p.greet()` with the binding written out.
Method binding is the descriptor protocol at work.

### A Descriptor That Learns Its Name

Telling a class attribute its own name is another job that once needed a metaclass.
In `x = Field()` below, `Field()` runs before the assignment,
so `Field`'s constructor finishes before Python binds the name `x`,
too early to learn it.
Python delivers that name automatically.
When a `class` body finishes executing,
Python calls `__set_name__(owner, name)` on every class attribute that defines it,
descriptor or otherwise,
passing the freshly created class and the name that holds the attribute.
`Field` pairs `__set_name__()` with `__get__()` and `__set__()`,
the descriptor protocol, and uses the delivered name to build its storage key.
A `print()` at the top of each method traces the descriptor's whole life,
from naming at class creation through every read and write:

```python
# set_name.py
from typing import Any

class Field:
    def __set_name__(self, owner: type, name: str) -> None:
        print(f"{name}.__set_name__ on {owner.__name__}")
        self.name = name
        self.storage = f"_{name}"

    def __get__(self, obj: Any,
                owner: type | None = None) -> Any:
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

The first two trace lines appear before any instance exists.
Python calls `__set_name__()` as it finishes executing the `class Point` statement,
once for each `Field`,
passing each one the new class and its own attribute name.
From then on, every read and write routes through the descriptor instead of going to the instance's `__dict__`.
In `print(p.x, p.y)`, Python evaluates both arguments before calling `print()`,
so both `__get__` lines appear ahead of `3 4`.
The final access, `Point.x`, goes through the class rather than an instance,
so `__get__()` receives `obj=None` and reports `via class`.
That branch returns `self`, the descriptor object,
which is why `isinstance(Point.x, Field)` is `True`.

Each `Field` stores values under `_x` or `_y` in the instance's `__dict__`.
The underscore prefix keeps each storage key apart from the attribute's name.
A descriptor that defines `__set__()` is a *data descriptor*,
and on every lookup a data descriptor takes precedence over the instance's `__dict__`.
If `__get__()` asks `obj` for `"x"`, the attribute's own name,
that lookup routes back to the descriptor and calls `__get__()` again,
until Python raises a `RecursionError`.
`Point` holds its descriptors under `x` and `y`,
so a lookup of `_x` goes straight to the instance's `__dict__`.

A descriptor that defines `__get__()` alone is a *non-data descriptor*,
and the precedence reverses.
The instance's `__dict__` comes first.
That is why assigning to `greet` on a `Person` instance shadows the method on that one instance,
while `p.x = 3` cannot shadow `Field`, because `Field` defines `__set__()`.

The test file confirms that:

- `__set_name__()` gives the descriptor its name.
- The descriptor stores each value under the storage key built from that name.
- The descriptor returns itself when you read it through the class.

```python
# test_set_name.py
import set_name

def test_descriptor_learns_its_name() -> None:
    field = vars(set_name.Point)["x"]
    assert field.name == "x"
    assert field.storage == "_x"

def test_values_stored_under_storage_keys() -> None:
    p = set_name.Point()
    p.x = 3
    p.y = 4
    assert (p.x, p.y) == (3, 4)
    assert p.__dict__ == {"_x": 3, "_y": 4}

def test_descriptor_on_class_returns_itself() -> None:
    assert isinstance(set_name.Point.x, set_name.Field)
    assert set_name.Point.x is vars(set_name.Point)["x"]
```

### A Descriptor That Validates

`Field` shows the protocol and stores the value you assign.
Use a descriptor when the write must do more than store.
`Positive` checks each value before storing it,
so every attribute declared with one raises a `ValueError` for a value of zero or less:

```python
# validating_descriptor.py
from exceptions import expected

class Positive:
    def __set_name__(self, owner: type, name: str) -> None:
        self.storage = f"_{name}"

    def __get__(self, obj: object,
                owner: type | None = None) -> float:
        return getattr(obj, self.storage)

    def __set__(self, obj: object, value: float) -> None:
        if value <= 0:
            raise ValueError(f"{value} is not positive")
        setattr(obj, self.storage, value)

class Rectangle:
    width = Positive()
    height = Positive()

    def __init__(
        self, width: float, height: float
    ) -> None:
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

r = Rectangle(3.0, 4.0)
print(r.area())
#: 12.0

with expected(ValueError):
    r.width = -1.0
#: [ValueError] -1.0 is not positive

print(r.width)
#: 3.0
```

`Rectangle` writes `Positive()` twice and no checking code of its own.
`self.width = width` inside `__init__()` routes through `Positive.__set__()` like any other write,
so the constructor's two assignments validate its arguments.
The rejected assignment leaves `_width` as it was,
so `r.width` still reads the `3.0` the constructor stored.

A `property` protects one attribute the same way,
but `Rectangle` then carries the check twice, once per attribute.
With a descriptor, one class holds the rule,
and each attribute that needs it says `Positive()`.

`Positive.__get__()` omits the `obj is None` branch that `Field` has,
so it works through an instance and fails through the class.
Reading `Rectangle.width` passes `None` as `obj` and raises an `AttributeError`.
A descriptor meant for wider use returns `self` there, as `Field` does.

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
                 namespace: dict[str, Any]) -> None:
        super().__init__(name, bases, namespace)
        setattr(cls, "uses_metaclass", lambda self: "Yes!")

class Simple(metaclass=SimpleMeta):
    def ping(self) -> None: pass

    @staticmethod
    def pong() -> None: pass

display_object(Simple)
#: [Attributes]
#:   None
#: [Methods]
#:   • ping(self) -> None
#:   • pong() -> None
#:   • uses_metaclass(self)
print(Simple().uses_metaclass())  # type: ignore
#: Yes!
```

`SimpleMeta.__init__()` runs once, as the `class Simple` statement finishes,
and patches a new method onto the freshly built class.
The injected value is a lambda,
but a function is a [descriptor](#learning-a-name-with-__set_name__),
so `Simple().uses_metaclass()` binds it like any other method.

Since a metaclass is a subclass of `type`,
writing `class Simple(SimpleMeta):` means something else.
That syntax makes `SimpleMeta` an ordinary base class,
so `Simple` inherits `type` and becomes a second metaclass,
not a class built by `SimpleMeta`.
`metaclass=` specifies what builds a class, independent of its base classes.
Python computes a new class's metaclass from all of its bases,
so `class Child(Simple):` also gets `SimpleMeta` as its metaclass.

By convention the first argument of a metaclass method is `cls` rather than `self`,
except for `__new__()`,
whose first argument is the metaclass and usually takes the name `mcls` or `mcs`.
Here `cls` is the class object under construction, `Simple`.
As with any subclass, call the base-class version first through `super()`.

Metaprogramming and static typing conflict.
A type describes a known set of attributes and signatures,
but a metaclass changes that structure at runtime,
adding attributes the class does not declare and replacing methods like `__new__()`.
The type checker never runs the metaclass,
so it reports the lines that use those changes as errors.

Three ways suppress the type checker's reports, from narrowest to broadest:

1.  `setattr(cls, "name", value)` adds an attribute through a string the type checker does not track.
2.  A localized `# type: ignore` silences one line,
    as on `Simple().uses_metaclass()` in `simple_meta.py`.
3.  Copying the class into an `Any`-typed name, `klass: Any = cls`,
    stops attribute checking for everything reached through that name.

Prefer the narrowest escape that fits,
because a broad `Any` also suppresses reports of genuine mistakes.

## `__init__()` versus `__new__()` in a Metaclass

Metaclass examples appear to use `__new__()` and `__init__()` interchangeably.
The difference is timing.
`__new__()` runs before the class object exists, so it can change the name,
bases, and namespace that Python uses to build it.
`__init__()` runs after the class exists,
so changing those arguments has no effect,
though you can still modify the finished class object:

```python
# new_vs_init.py
from typing import Any

class Tag:
    pass

class Meta(type):
    def __new__(mcls, name: str, bases: tuple[type, ...],
                namespace: dict[str, Any]) -> type:
        # Before creation: these changes take effect
        namespace["added_in_new"] = 42
        bases += (Tag,)
        return super().__new__(mcls, name, bases, namespace)

    def __init__(cls, name: str, bases: tuple[type, ...],
                 namespace: dict[str, Any]) -> None:
        super().__init__(name, bases, namespace)
        # No effect: the class is already built
        namespace["added_in_init"] = 99
        # Effect: this modifies the finished class
        setattr(cls, "patched_in_init", 3.14)

class Built(metaclass=Meta):
    pass

for attr in ("added_in_new", "added_in_init",
             "patched_in_init"):
    print(attr, hasattr(Built, attr))
#: added_in_new True
#: added_in_init False
#: patched_in_init True
print("has Tag base:", Tag in Built.__bases__)
#: has Tag base: True
```

`added_in_init` reports `False` because `type.__new__()` copies `namespace` into the new class's own `__dict__` as it builds the class.
By the time `__init__()` runs, the two mappings are independent,
so mutating the original dict leaves the class unchanged.
`setattr(cls, ...)` still works because it modifies the class object.

Override `__new__()` when you must change `name`, `bases`, or the namespace
(including special members like `__slots__`) before Python builds the class.
Otherwise, prefer `__init__()`,
which receives the finished class and returns `None`.

## Intercepting Instance Creation

A method defined on the metaclass becomes a method of the class object,
callable on the class but not on its instances.
Such methods are sometimes called *metamethods*.
They differ from `classmethod`s.
A `classmethod` stays callable on both the class and its instances,
while a metamethod works only through the class.
The class is an instance of the metaclass.
The class's own instances are not.

One useful metamethod is `__call__()`.
It is the same method that makes any object callable.
`obj()` invokes `type(obj).__call__(obj, ...)`.
A class is an object, an instance of its metaclass,
so `ClassName()` invokes `__call__()` on the metaclass the same way.
That `__call__()` runs first when you create an instance of the class.
`__new__()` and `__init__()` normally run only because the default `type.__call__()` calls them.
A metaclass that overrides `__call__()` replaces that step,
so its code determines whether `__new__()` and `__init__()` run.
That code can also return a cached instance instead of building a new one.
Caching there is one way to build a [*Singleton*](23_Patterns--Singleton.md):

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
b = ASingleton()  # [1]
#: reusing ASingleton
assert a is b

c = BSingleton()
#: building BSingleton
d = BSingleton()
#: reusing BSingleton
assert c is d
assert a is not c
```

The `ASingleton()` call at `[1]` ends in `__call__()`,
which returns the cached instance.
`__new__()` and `__init__()` run once per class, on the first call.
Each class gets its own entry in the `_instances` dictionary,
so the singletons are independent.

The `[T]` on `__call__()` ties its return type to `cls`,
so `ty` infers `ASingleton` as the type of `ASingleton()` instead of `Any`.
Without the `[T]`, every singleton comes back as `Any` under `ty` and Pyright.
A misspelled attribute access on the result then passes the check.
Under mypy `ASingleton()` has the type `ASingleton` with or without the `[T]`,
because mypy ignores a metaclass `__call__()` return type.

That same `[T]` is why the body calls `type.__call__(cls, ...)` instead of the more usual `super().__call__(...)`.
Annotating the first parameter as `type[T]` drops `Singleton` from the type of `cls`.
`ty` and mypy accept a zero-argument `super()` only when they can confirm that `cls` is a `Singleton`.
Pyright accepts it without the check.
At run time both forms call `type.__call__()` on `cls` with the same arguments.

You might expect to parameterize[^parameterize-spelling] the class,
with `class Singleton[T](type)` and `_instances: ClassVar[dict[type, T]]`.
That fails twice.
A `ClassVar` means one shared value for the whole class,
so it cannot depend on a type parameter that varies per instantiation.
And each class must write `class ASingleton(metaclass=Singleton[ASingleton]):`,
naming `ASingleton` before its class body finishes defining it.[^crtp]
The method-level `[T]` on `__call__()` avoids both problems.
It binds `T` from `cls` at the call site, `ASingleton()`,
and that call runs after `ASingleton` exists.

The metaclass version works,
but it is heavier than the problem usually requires.
[*Singleton*](23_Patterns--Singleton.md) covers the lighter alternatives,
from a class decorator down to a module.

## Multiple Inheritance and Metaclasses

`Singleton` stores its cache in `_instances`, a `dict` attribute,
rather than inheriting from `dict`.
Can a metaclass inherit from more than one class, the way an ordinary class can?

Trying the obvious version fails.
`type` and `dict` are both built-in types with their own C-level instance layout,
and CPython allows multiple inheritance only when the bases' layouts are compatible,
one extending the other:

```python
# metaclass_layout_conflict.py
from typing import Any
from exceptions import expected

with expected(TypeError):
    class Singleton(type, dict[type, Any]):  # type: ignore
        pass
#: [TypeError] multiple bases have instance lay-out conflict
```

The failure comes from the instance layouts, not from metaclasses.
`class X(list, dict): pass` fails the same way.
Neither base is a metaclass.
Because `type`, `list`, and `dict` each bring a layout of their own,
no class can combine two of them.

<!-- "the very TypeError" is the intensive adjective, not the hedging adverb
     proselint.Very exists to catch. -->
<!-- vale proselint.Very = NO -->
The `# type: ignore` comment appears because `ty` checks this rule statically.
At check time, its `instance-layout-conflict` check reports the very `TypeError` this example exists to demonstrate at run time.
The comment suppresses the diagnostic only because provoking that crash is educational.
<!-- vale proselint.Very = YES -->

Python 3.15 adds the `@typing.disjoint_base` marker (PEP 800),
which tells the type checker that a class of your own follows the same rule as `type` and `dict`:
no class can inherit from it and from another unrelated disjoint base.
The type checker reports a class that inherits from two such bases as an `instance-layout-conflict`,
and it treats an `isinstance()` branch that requires both bases as unreachable,
since no object can be an instance of both.

A metaclass can multiply inherit like any other class,
as long as the extra class is a mix-in with no competing layout:

```python
# mixin.py
from exceptions import expected

class Mixin:
    def helper(self) -> str:
        return "hi"

class HelperMeta(type, Mixin):
    pass

class Sub(metaclass=HelperMeta):
    pass

print(Sub.helper())
#: hi

with expected(AttributeError):  # A metamethod: class only
    Sub().helper()  # type: ignore
#: [AttributeError] 'Sub' object has no attribute 'helper'
```

Lookup on `Sub` finds `helper()` through its metaclass,
and lookup on a `Sub` instance does not.
The `AttributeError` comes from the metamethod rule at the start of [Intercepting Instance Creation](#intercepting-instance-creation).
Lookup on a `Sub` instance searches `Sub` and its bases.
`Mixin` sits among the bases of `HelperMeta`, outside that search.
A `classmethod` defined in `Sub` works through both `Sub` and its instances.

A metaclass that needs a `dict` holds one in an attribute,
as `Singleton._instances` does,
and keeps the single layout it inherits from `type`.

Multiple inheritance fails a second way, from the other direction.
A class has a single metaclass,
so Python cannot choose a metaclass for a class whose bases come from two unrelated metaclasses:

```python
# multiple_metaclass_inheritance.py
from exceptions import expected

class MetaA(type):
    pass

class MetaB(type):
    pass

class A(metaclass=MetaA):
    pass

class B(metaclass=MetaB):
    pass

with expected(TypeError):
    class C(A, B):  # type: ignore
        pass
#: [TypeError] metaclass conflict: the metaclass of a
#: derived class must be a (non-strict) subclass of the
#: metaclasses of all its bases

class MetaC(MetaA, MetaB):
    pass

class D(A, B, metaclass=MetaC):
    pass

print(type(D).__name__)
#: MetaC
```

The `expected()` helper wraps the message across three lines to fit the page.
Python reports it as a single line, and that line states the fix.
`D`'s metaclass, `MetaC`, must be a subclass of every base's metaclass,
`MetaA` and `MetaB` both.

As with the layout conflict, `ty` catches this one statically.
It reports `conflicting-metaclass` and names both `MetaA` and `MetaB`,
so the line carries a `# type: ignore`.

Both failures have the same shape:
an inheritance graph that looks legal until you check each base's layout or metaclass.
That shape is one more reason to reserve metaclasses,
and arguably multiple inheritance, for cases that need them.

## When You Still Need a Metaclass

Use a metaclass when you need to change the class object rather than react to its creation:

- Adding methods to the class
  (metamethods such as the `__call__()` in `singleton.py`, or the `__iter__()` that lets `EnumType` make `for c in Color` work).
- Replacing the namespace mapping with `__prepare__()` so the class body populates a custom dictionary.
- Enforcing an invariant across a family of classes that shares no base class.
  `__init_subclass__()` requires a common base to define it.
  Such a family shares a metaclass.

The first case gives the class object an `__iter__()`:

```python
# iterable_class.py
from collections.abc import Iterator
from typing import Any

class IterableMeta(type):
    def __iter__(cls) -> Iterator[Any]:
        return (
            v for k, v in vars(cls).items()
            if not k.startswith("_")
        )

class Color(metaclass=IterableMeta):
    red = "red"
    green = "green"
    blue = "blue"

for c in Color:
    print(c)
#: red
#: green
#: blue
```

Python calls `IterableMeta.__iter__()` when you write `for c in Color`,
which iterates over the class object, not an instance of it.
In `Color`'s namespace the underscore-prefixed names that `__iter__()` skips are the dunder bookkeeping every class carries.
The values come out in source order because a class's namespace keeps the order in which the body defines its names,
a guarantee since Python 3.6 (PEP 520).
A metaclass, a class decorator,
or `__init_subclass__()` that walks `vars(cls)` sees the members in the order the source lists them.

A class decorator cannot make `for c in Color` work.
Python looks up a special method such as `__iter__()` on the object's type and skips the object's own namespace,
so `for c in Color` consults `type(Color)`.
An `__iter__` that a decorator assigns onto `Color` serves instances of `Color`.
For the class object, Python finds a special method on its metaclass.

`__prepare__()` has no simpler substitute either:

```python
# prepare_namespace.py
from typing import Any
from exceptions import expected

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

with expected(TypeError):
    class Handlers(metaclass=Strict):
        def on_open(self) -> None: ...  # [1]
        def on_close(self) -> None: ...
        def on_open(self) -> None: ...  # noqa: F811  # [2]
#: [TypeError] on_open defined twice
```

`__prepare__()` runs before the class body does,
and the mapping it returns becomes the namespace for that body.
Every `def` and every assignment in the body becomes a `__setitem__()` call on that mapping,
so `NoDuplicates.__setitem__()` receives the `on_open` at `[2]` under a key the mapping already holds.
Python then passes the finished mapping to `type.__new__()`.

`__prepare__()` must carry `@classmethod`.
Python calls it on the metaclass before any class object exists,
so an ordinary method receives the class name as its `self` and leaves `bases` unfilled.
The resulting `TypeError` reports a missing `bases` argument and never mentions `@classmethod`.

No other hook can detect the `on_open` at `[2]`.
`__init_subclass__()`, `__set_name__()`,
and a class decorator all run after the body has finished,
by which time `[2]` has overwritten `[1]`.
The static half of the check is ruff's report of the same mistake.
The `# noqa: F811` suppresses that report so the listing can run.
`__prepare__()` detects the mistake at run time,
including on names the body computes.

These needs are real but rare.
For everything else, `__init_subclass__()`, `__set_name__()`,
and [class decorators](14_Techniques--Decorators.md#decorating-classes)
are simpler and easier to read.

A class decorator receives the finished class, so it can add, replace,
or inspect members.
It runs after `type.__new__()` has used the name, the bases, and the namespace,
so changing those means building a replacement class.
A class decorator also cannot give the class object behavior of its own.
Setting `__call__` from a decorator makes instances callable.
Only a metaclass makes the class callable in a new way.
The case for a metaclass rests on that limit.
The class object needs behavior that only its metaclass,
chosen before the class exists, can supply.

Subscripting a class is the exception.
For a class `Box`, `Box[int]` uses the metaclass's `__getitem__()` if the metaclass defines one,
and otherwise calls `Box.__class_getitem__(int)`,
a method PEP 560 added in Python 3.7.
`__class_getitem__()` is implicitly a class method, as `__init_subclass__()` is,
so a class that defines it becomes subscriptable without a metaclass.
`list`, `dict`, and the other built-in containers define it to return a `types.GenericAlias`,
which is how `list[int]` works at runtime.
`typing.Generic` defines it for the classes you write with type parameters.

When a class header lists a `GenericAlias` as a base,
as `dict[str, EventMaker]` does for `EventMakers` in `greenhouse.py`,
Python records the plain `dict` in `__bases__`.
`types.get_original_bases(EventMakers)`, new in Python 3.12,
returns the bases as the header wrote them, with `dict[str, EventMaker]` intact.

## The `inspect` Module

Up to now, you've modified classes.
`type()` builds them,
and metaclasses and `__init_subclass__()` run code during their creation.
The `inspect` module is the other half of metaprogramming.
It reads the structure of live objects.
It answers questions like which members an object has,
what a function's signature is, and what its docstring says.

### The Core Functions

`inspect` works on any live object: modules, classes, functions, methods,
and instances.

- `inspect.signature(callable)` returns a `Signature` object describing the parameters,
  their annotations, and their defaults.
- `inspect.getdoc(obj)` returns the docstring with its common indentation removed.
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
Python keeps type annotations (a.k.a. type hints) at runtime,
although it [does not check them](08_Foundations--Static_Types.md#hints-are-not-enforced-at-run-time).
Under the deferred evaluation of PEP 649,
the annotations stay attached to the function,
and Python evaluates them when code first reads them.
`signature()` reads that stored data (not the original source text)
to build the `Signature` object.

`display_object()` relies on `inspect` functions.
`getmembers_static()` finds the members, `signature()` renders each method,
and `get_annotations()` supplies the declared types,
returning a class's declared annotations in a `dict`.
`display_object()`'s source and its display options are reference material,
collected in [`display_object()` Reference](#display_object-reference)
at the end of this chapter.

The `typing` module adds two functions for a [`Protocol`](08_Foundations--Static_Types.md#structural-typing-with-protocols)
class, both new in Python 3.13.
`typing.is_protocol(cls)` reports whether `cls` is a `Protocol`.
`typing.get_protocol_members(cls)` returns the `frozenset` of attribute and method names that a structural match requires,
and raises a `TypeError` for a class that is not a `Protocol`.

### Sorting Members into Attributes and Methods

`display_object()` walks every member that `inspect.getmembers_static()` returns.
The static variant reads members from the `__dict__` of the object and of each of its classes,
without invoking descriptors, properties, or `__getattr__()`.
Inspecting an object therefore runs none of its properties or descriptors,
which makes the tool safe to point at something unfamiliar.

The tool sorts each member into one of two lists.
Callables become methods,
printed with the signature that `inspect.signature()` reports,
or `(...)` when a built-in has no inspectable signature.
Everything else becomes an attribute, printed as `name: type = value`.
The declared type comes from the class annotations,
which `_annotations()` gathers across the whole inheritance chain,
calling `inspect.get_annotations()` on each class in [`FORWARDREF` format](#reading-annotations-before-their-names-exist).
In that format, a name the module never defined prints as a `ForwardRef` instead of raising a `NameError`.
An attribute with no annotation, such as one assigned dynamically,
prints as `name = value`.
The value is the member's `repr()`,
truncated to keep the line within `max_width`.

An attribute tagged `[CV]` lives on the class or a base class rather than in `obj`'s own `__dict__`.
The tag is short for "class variable," another name for a class attribute.
When `obj` is a class, every attribute lives on a class,
so all of them carry the tag.
In [Comparing Ordinary Classes and Data Classes](12_Techniques--Data_Classes_as_Types.md#comparing-ordinary-classes-and-data-classes),
`show(D)` in `classvar_dataclass.py` tags both `D.x` and `D.s`.
`D` declares them in its own body, but `show(D)` inspects the class,
where both live.

For an instance, the tag says whether the value lives on the class or on the object,
the same rule `Stars.rating` demonstrates in [Class Attributes](09_Foundations--Class_Attributes.md#class-attributes-are-not-default-values).
In that same chapter 12 comparison,
`show(B())` in `class_with_defaults.py` tags `B.x` and `B.s`.
`display_object(Messenger("iris", 12, 3.14))` in chapter 12 tags none,
since `@dataclass` assigns every field straight onto the new instance.
The tag comes from where the value lives,
so it applies whether or not the attribute's declaration uses `typing.ClassVar`.

### Reading Annotations Before Their Names Exist

Deferred evaluation lets an annotation specify a class that the module defines later.
Python evaluates an annotation when code first reads it,
so a class can declare a field whose type appears further down the module.
A metaprogram reads annotations early.
A decorator, an `__init_subclass__()` hook,
or a metaclass runs while Python creates the class.
If one of them reads the annotations then,
a name in those annotations may refer to a class the module defines later.
Evaluating them at that moment raises a `NameError`.

The standard library's `annotationlib` module handles this case.
Its `get_annotations()` takes a `format` argument that chooses how to evaluate the annotations,
and `inspect.get_annotations()` accepts the same argument.

- `Format.VALUE`, the default, evaluates each annotation to a real object,
  and raises a `NameError` when a name is missing.
- `Format.FORWARDREF` evaluates what it can,
  and substitutes an `annotationlib.ForwardRef` for each name it cannot resolve.
- `Format.STRING` evaluates nothing,
  and returns each annotation as a string that matches the source as closely as it can.

The listing reads one forward-referencing annotation in all three formats:

```python
# forward_formats.py
from annotationlib import Format, get_annotations
from exceptions import expect

class Order:
    item: str
    buyer: Customer

expect(NameError, get_annotations, Order,
       format=Format.VALUE)
#: [NameError] name 'Customer' is not defined
fwd = get_annotations(Order, format=Format.FORWARDREF)
print(fwd["item"])
#: <class 'str'>
ref = fwd["buyer"]
print(type(ref).__name__, ref.__forward_arg__)
#: ForwardRef Customer
print(get_annotations(Order, format=Format.STRING))
#: {'item': 'str', 'buyer': 'Customer'}

class Customer:
    pass

print(get_annotations(Order)["buyer"] is Customer)
#: True
```

`Order` specifies `Customer` before `Customer` exists.
The `VALUE` request raises the same `NameError` that a decorator applied to `Order` would get.
`STRING` returns text instead of objects,
so it succeeds before `Customer` exists.
Once `Customer` exists, the default `VALUE` request succeeds,
because the class caches its annotations only after an evaluation succeeds.

A tool that reads annotations at definition time therefore requests `FORWARDREF`.
It keeps the real objects it gets back,
and holds on to each `ForwardRef` until the name exists,
when the reference's `evaluate()` method resolves it to the class.

## Which Hook for Which Job

Every hook in this chapter is an ordinary function that Python calls at a known moment during class construction.

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
                namespace: dict[str, Any]) -> type:
        print(f"__new__ {name} enter")
        cls = super().__new__(mcls, name, bases, namespace)
        print(f"__new__ {name} exit")
        return cls

    def __init__(cls, name: str, bases: tuple[type, ...],
                 namespace: dict[str, Any]) -> None:
        super().__init__(name, bases, namespace)
        print(f"__init__ {name}")

def tag[T](cls: type[T]) -> type[T]:
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

`Base`'s four lines are the bare sequence.
They also show that `Base.__init_subclass__()` does not run for `Base`,
the rule [Making a Class Final](#making-a-class-final) needs.
`__prepare__()` runs before the body, so its line comes first.
`type.__new__()` calls `__set_name__()` and `__init_subclass__()` as it assembles the class,
so their lines sit between `__new__ Derived enter` and `__new__ Derived exit`,
inside the metaclass's own construction step.
The decorator is last, because it receives a finished class.

- React to each new subclass: `__init_subclass__()`.
- Give a class attribute its own name: `__set_name__()`.
- Rewrite a finished class: a class decorator.
- Build a family of classes from data: `type()` with three arguments,
  or an `exec()`ed class body when the definition is easier to read as source.
- Change the name, the bases, or the namespace before Python builds the class:
  a metaclass `__new__()`.
- Control the namespace into which the body executes: `__prepare__()`.
- Decide whether an instance gets built: a metaclass `__call__()`.
- Read a class you did not write: `inspect`.

None of these hooks is a separate facility added to the language.
A class is an object that Python builds at run time by executing its body,
and `hook_order.py` displays each step of that construction as it runs.
The one hook missing from its trace is `__call__()`, which runs later still,
each time someone calls the finished class.

## `display_object()` Reference {#display_object-reference}

The rest of `display_object()` is presentation:
how it formats what `inspect` reports, and which members it shows.
Read it when a listing's output raises a question, and skip it otherwise.

### Building `display_object()`

Throughout the book you've seen `display_object()` show the layout of an object.
Here, the `utils/` prefix on the file marker puts the file in the shared `utils/` directory at the top of the `Examples` tree,
where any chapter can import it:

```python
# utils/display.py
import inspect
from annotationlib import Format
from collections.abc import Callable, Sequence
from typing import Final

ALL_DUNDERS = sentinel("ALL_DUNDERS")
REDEFINED_DUNDERS = sentinel("REDEFINED_DUNDERS")
INTERESTING_DUNDERS: Final[tuple[str, ...]] = (
    "__init__", "__repr__", "__eq__", "__hash__",
)

def _annotations(cls: type) -> dict[str, object]:
    # Annotations declared on the class or any of its bases:
    return {**inspect.get_annotations(
                base, format=Format.FORWARDREF)
            for base in reversed(cls.__mro__)}

def _type_name(annotation: object) -> str:
    # A readable annotation name, keeping [parameters]:
    if isinstance(annotation, type):
        return annotation.__name__
    return str(annotation)

def _redefined(name: str, value: object) -> bool:
    # Restricted to INTERESTING_DUNDERS: every class has
    # __module__, __dict__, and other bookkeeping dunders
    # that always differ from object's, so comparing those
    # never filters anything out.
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
```

`display_object()` hides standard dunder members by default.
Pass their names in `dunder` to keep specific ones.
`dunder=["__init__"]` shows `__init__` and hides the other dunders.
Pass the `ALL_DUNDERS` sentinel instead to keep every dunder member,
including the interpreter's own machinery.
`ALL_DUNDERS` is useful for exploring an unfamiliar object,
but it lists a class's own choices among everything `object` and the interpreter add,
where they are hard to find.
`INTERESTING_DUNDERS` lists the four a reader typically customizes when defining a class:
`__init__`, `__repr__`, `__eq__`, and `__hash__`.
Pass it as `dunder` to see those four without the surrounding noise.

Under `INTERESTING_DUNDERS`, every class shows all four,
because a class inherits `object`'s version of any it leaves out,
and the report lists an inherited dunder the same way as one the class wrote.
`REDEFINED_DUNDERS` filters harder.
Among those same four,
it keeps only the ones whose value differs from `object`'s version,
so a class that overrides none of them shows no dunders.

The comparison uses `is`, not `==`,
since a dunder inherited unchanged from `object` is the same function object,
not merely an equal one.

`dunder`'s type is `Sequence[str] | ALL_DUNDERS | REDEFINED_DUNDERS`,
naming each sentinel value rather than the generic `sentinel` class,
so the type checker narrows `dunder` to `Sequence[str]` once it rules out both sentinels.
`name in dunder` then needs no further guard.

`display_object()` reports differently under `INTERESTING_DUNDERS` and `REDEFINED_DUNDERS`,
on an empty class and on one that redefines almost everything:

```python
# dunder_modes.py
from dataclasses import dataclass
from display import (INTERESTING_DUNDERS, REDEFINED_DUNDERS,
                     display_object)

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

display_object(Point, REDEFINED_DUNDERS,
               exclude=("__hash__",))
#: [Attributes]
#:   None
#: [Methods]
#:   • __eq__(self, other)
#:   • __init__(self, x: int, y: int) -> None
#:   • __repr__(self)
```

`Plain` writes none of the four,
so `INTERESTING_DUNDERS` shows `object`'s versions and `REDEFINED_DUNDERS` shows `None` under both headings.
`@dataclass` writes three of them and sets `__hash__` to `None`,
so `Point` reports a `__hash__` attribute rather than a method.
The last call drops that row,
for the same reason `comparison.py` in [Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#comparing-ordinary-classes-and-data-classes)
passes `exclude=("__hash__",)`.

`exclude` drops specific names regardless of what `dunder` otherwise shows,
and it applies to every member, dunder or ordinary.
The `exclude` check runs before the `dunder` test,
so an excluded name stays out of `[Attributes]` and `[Methods]` no matter which mode selects it.
Excluding `__hash__` helps when an earlier listing has explained its row and repeating the row would add noise.

The rest of the file selects the members, formats each one,
and prints the report:

```python
# utils/display.py (continued)
def _shared(obj: object, name: str) -> bool:
    # A class has no instance-level storage to compare
    # against, so every attribute it shows is class-level
    # storage by construction. For an instance, only a name
    # missing from its own __dict__ is:
    if inspect.isclass(obj):
        return True
    return name not in getattr(obj, "__dict__", {})

def _truncate(text: str, budget: int) -> str:
    # Fit the budget, marking a cut with an ellipsis:
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
    dunder: (Sequence[str] | ALL_DUNDERS
             | REDEFINED_DUNDERS) = (),
    max_width: int = 57,
    exclude: Sequence[str] = (),
) -> None:
    # For a class, the class; for an instance, its class:
    cls = obj if inspect.isclass(obj) else type(obj)
    annotations = _annotations(cls)
    attributes: list[str] = []
    methods: list[str] = []
    # Read members statically, without triggering
    # dynamic descriptors:
    for name, value in inspect.getmembers_static(obj):
        if name in exclude:
            continue
        is_dunder = (name.startswith("__")
                     and name.endswith("__"))
        if is_dunder and not _show_dunder(
                dunder, name, value):
            continue  # Skip standard dunder clutter
        if callable(value):
            methods.append(
                _format_method(name, value, max_width))
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

display_object(Fraggle)  # [1]
#: [Attributes]
#:   • y: float = 1.14659 [CV]
#:   • z: str = 'blivet' [CV]
#: [Methods]
#:   • f(self) -> None
#:   • g(self, x: int) -> float
#:   • h(self, s: str) -> str

display_object(Fraggle(9, 2.3))  # [2]
#: [Attributes]
#:   • x: int = 9
#:   • y: float = 2.3
#:   • z: str = 'blivet'
#: [Methods]
#:   • f(self) -> None
#:   • g(self, x: int) -> float
#:   • h(self, s: str) -> str
```

The calls at `[1]` and `[2]` display the same class two ways.
`display_object(Fraggle)` inspects the class object.
It lists `y` and `z`, the fields with defaults.
`x`'s declaration is `x: int` with no default,
so on the class it is an annotation with no bound attribute,
and `getmembers_static()` skips it.

`display_object(Fraggle(9, 2.3))` inspects an instance,
whose attributes hold its field values, so `x` now appears beside `y` and `z`.
The method list is the same either way, because methods live on the class.

```python
# demo_display_object.py (continued)
# ALL_DUNDERS also reveals what @dataclass generated:
display_object(Fraggle(9, 2.3), dunder=ALL_DUNDERS)  # [1]
#: [Attributes]
#:   • __annotations_cache__ = {'x': <class 'int'>, ... [CV]
#:   • __class__ = <attribute '__class__'> [CV]
#:   • __dataclass_fields__ = {'x': Field(name='x',t... [CV]
#:   • __dataclass_params__ = _DataclassParams(init=... [CV]
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
#:   • __init__(self, x: int, y: float = 1.14659, z: str ...
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

The call at `[1]` passes `ALL_DUNDERS`.
A `@dataclass` produces many of these dunders:

- `__dataclass_fields__`
- `__dataclass_params__`
- `__match_args__`
- `__replace__`
- `__hash__`, set to `None`
- `__init__`, `__eq__`, and `__repr__`

The generated `__init__()`, `__eq__()`,
and `__repr__()` give `Fraggle` a constructor, equality,
and a `repr()` that you did not write.

Beyond those three, the output holds `Fraggle`'s fields and methods,
two annotation entries, and the bookkeeping every class carries.

The output also shows the deferred evaluation of PEP 649 at work on a class.
`__annotate_func__` is the code that computes the annotations,
and `__annotations_cache__` holds the result after the first request.
`__annotate__`, the name PEP 649 gives the function,
is a descriptor on `type` that reads `__annotate_func__`,
so it lives on the metaclass rather than in the class's own namespace.

## Exercises

Try each exercise before opening its [solution](../Solutions/17_Techniques--Metaprogramming/).

1.  In `init_subclass.py`, add a class `Yellow(Color)` and then `Gold(Yellow)`.
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
6.  Delete the `# type: ignore` comment from `metaclass_layout_conflict.py` and run `ty` over the file.
    Compare the `instance-layout-conflict` diagnostic it reports with the `TypeError` the program prints.
    The static report and the runtime failure describe the same collision.
7.  Using `type()` directly, build a class `Celsius` with a base of `float`,
    an attribute `unit = "C"`,
    and a method `describe(self)` returning `f"{self} degrees {self.unit}"`.
    Confirm `Celsius(21.5).describe()` works and that `type(Celsius)` is `type`.
8.  In `new_vs_init.py`,
    move the `bases += (Tag,)` line from `__new__()` into `__init__()` and predict the outcome before running it.
    Explain the result in terms of when the class object comes into existence.
9.  `commander.py` validates `class_name` against `KNOWN_COMMANDS` before splicing it into source text.
    Remove that check, call `Command.make_class()` with a name containing a newline and a second statement,
    and confirm that the injected statement runs.
    `make_class()` splices the name in twice,
    the second time inside a string literal,
    so a bare newline ends the payload as an unterminated string.
    The payload's last line must close or swallow that second splice.
    Restore the check.
10. Change `prepare_namespace.py`'s `NoDuplicates` so that instead of raising an exception,
    it keeps the first definition of a duplicated name and discards the later one.
    Give the two `on_open` bodies different `print()` calls so you can tell them apart,
    then confirm that `Handlers().on_open()` runs the first one.
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
    The compiler compiles its member functions when something first calls them,
    and by then `ASingleton` is complete.

    Python evaluates `Singleton[ASingleton]` eagerly,
    before it binds the name `ASingleton`,
    and offers no equivalent incomplete-type stage to exploit.

[^parameterize-spelling]: The book uses pytest's own spelling, `parametrize`,
    for `@pytest.mark.parametrize`, and "parameterize" everywhere else.
    [Testing](11_Techniques--Testing.md) explains the four possible spellings.
