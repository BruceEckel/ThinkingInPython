# Metaprogramming

Objects are created by other objects: special objects called "classes" that we
set up to produce objects configured to our liking.

Classes are just objects, and you can modify them the same way:

    >>> class Foo: pass
    ...
    >>> Foo.field = 42
    >>> x = Foo()
    >>> x.field
    42
    >>> Foo.method = lambda self: "Hi!"
    >>> x.method()
    'Hi!'

A change to a class affects every object of that class, even ones already
created.

What creates these "class" objects? Other special objects, called *metaclasses*.
The default metaclass is `type`, and in the vast majority of cases it does the
right thing. Sometimes you want to customize how classes are produced, by
running extra code or injecting members as the class is built. That is
metaclass programming.

It is worth saying plainly: *most of the time you do not need a metaclass.* It
is a fascinating tool, and the temptation to use it is strong, but Python
3 added simpler hooks that cover almost every case a metaclass used to handle:

- `__init_subclass__` runs when a subclass is created. It replaces most "do
  something each time a class is defined" metaclasses.
- `__set_name__` lets a descriptor learn the attribute name it was bound to,
  at class-creation time.
- *Class decorators* transform a class after it is built.

Use a metaclass only when these cannot do the job. This chapter shows the
simpler tools first, then metaclasses for the cases that still need them.

## Generating Classes with type

Since metaclasses create classes, you can call the metaclass yourself. `type`
with one argument gives the type of an existing object. `type` with three
arguments creates a new class: the name, a tuple of base classes, and a
namespace dictionary of fields and methods. So the equivalent of:

    class C: pass

is:

    C = type('C', (), {})

You can add bases, fields, and methods the same way:

```python
# my_list.py

def howdy(self, you: str) -> None:
    print("Howdy, " + you)

MyList = type('MyList', (list,), dict(x=42, howdy=howdy))

ml = MyList()
ml.append("Camembert")
print(ml)
print(ml.x)
ml.howdy("John")

print(ml.__class__.__class__)

""" Output:
['Camembert']
42
Howdy, John
"""
```

Printing the class of the class produces the metaclass.

Generating classes programmatically with `type` opens up real possibilities.
Where you might otherwise write many near-identical subclasses by hand, you can
generate them in a loop:

```python
# greenhouse.py

class Event:
    events: list[Event] = [] # static

    def __init__(self, action: str, time: float) -> None:
        self.action = action
        self.time = time
        Event.events.append(self)

    def run(self) -> None:
        print(f"{self.time:.2f}: {self.action}")

    @staticmethod
    def run_events() -> None:
        for e in sorted(Event.events, key=lambda e: e.time):
            e.run()

def create_mc(description: str) -> None:
    "Create subclass using the 'type' metaclass"
    class_name = "".join(x.capitalize() for x in description.split())
    def init(self, time: float) -> None:
        Event.__init__(self, description + " [mc]", time)
    globals()[class_name] = type(
        class_name, (Event,), {"__init__": init})

def create_exec(description: str) -> None:
    "Create subclass by exec-ing a string"
    class_name = "".join(x.capitalize() for x in description.split())
    klass = f"""
class {class_name}(Event):
    def __init__(self, time: float) -> None:
        Event.__init__(self, "{description} [exec]", time)
"""
    exec(klass, globals())

if __name__ == "__main__":
    descriptions = ["Light on", "Light off", "Water on", "Water off",
                    "Thermostat night", "Thermostat day", "Ring bell"]
    initializations = "ThermostatNight(5.00); LightOff(2.00); \
        WaterOn(3.30); WaterOff(4.45); LightOn(1.00); \
        RingBell(7.00); ThermostatDay(6.00)"
    [create_mc(dsc) for dsc in descriptions]
    exec(initializations, globals())
    [create_exec(dsc) for dsc in descriptions]
    exec(initializations, globals())
    Event.run_events()
```

`create_mc()` builds each subclass with `type`. `create_exec()` does the same
thing by running a string of class-definition code with `exec`. The `exec`
version is easier for most readers to follow, because it looks like ordinary
class definitions. Use `type` only when the dynamic version is genuinely
clearer than generated source text.

## Self-Registration of Subclasses

A common need is for a base class to keep track of its subclasses, so you can
enumerate them. This is the textbook reason people used to write a metaclass.
In Python 3 it is a few lines with `__init_subclass__`, which Python calls
automatically every time a subclass is created:

```python
# init_subclass.py
# Track the "leaf" subclasses (those with no subclasses of their own),
# using __init_subclass__ instead of a metaclass.


class Color:
    registry: set[type] = set()

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Color.registry.add(cls)
        Color.registry -= set(cls.__bases__)  # keep only the leaves


class Blue(Color):
    pass
class Red(Color):
    pass
class Green(Color):
    pass
print(sorted(c.__name__ for c in Color.registry))


class PhthaloBlue(Blue):
    pass
class CeruleanBlue(Blue):
    pass
print(sorted(c.__name__ for c in Color.registry))


# A second, independent hierarchy keeps its own registry:
class Shape:
    registry: set[type] = set()

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

""" Output:
['Blue', 'Green', 'Red']
['CeruleanBlue', 'Green', 'PhthaloBlue', 'Red']
['Circle', 'Square']
"""
```

Each time a subclass is created, `__init_subclass__` adds it to the registry
and removes its base classes, so only the current leaves remain. No metaclass
is involved. `__init_subclass__` is implicitly a class method; its first
argument is the new subclass.

## Learning a Name with __set_name__

Another job that once needed a metaclass is letting an attribute object
discover the name it was assigned to. A *descriptor* with `__set_name__` gets
that name when the class is created:

```python
# set_name.py
# A descriptor learns its attribute name at class-creation time.
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


p = Point()
p.x = 3
p.y = 4
print(p.x, p.y)

""" Output:
3 4
"""
```

The `Field` descriptors do not know they are called `x` and `y` until Python
tells them through `__set_name__`. This is metaprogramming, but it needs no
metaclass.

## Writing a Metaclass

When the simpler hooks are not enough, you write a metaclass. A metaclass is a
subclass of `type`. You attach it with the `metaclass=` keyword in the class
header. Python then uses your metaclass, instead of `type`, to build the class.

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
# A method injected by the metaclass:
print(simple.uses_metaclass())  # type: ignore

""" Output:
['bar', 'foo', 'uses_metaclass']
Yes!
"""
```

By convention the first argument of a metaclass method is `cls` rather than
`self`, except for `__new__`, which uses `mcl`. The `cls` is the class object
being built. As with any subclass, call the base-class version first through
`super()`.

> A note on history. Python 2 spelled the hook differently: you set a
> `__metaclass__` field in the class body, and you could even point it at a
> function or an inline class. Python 3 dropped all of that. There is one way
> now, the `metaclass=` keyword, and the metaclass must be a real class. This
> is simpler and more consistent, so the Python 2 forms are not shown here.

## `__init__` versus `__new__` in a Metaclass

Metaclass examples seem to use `__new__` and `__init__` interchangeably. The
difference is timing. `__new__` runs *before* the class object exists, so it can
change the name, bases, and namespace that will be used to build it. `__init__`
runs *after* the class exists, so changing those arguments has no effect, though
you can still modify the finished class object:

```python
# new_vs_init.py
from typing import Any


class Tag:
    pass


class Meta(type):
    def __new__(mcl, name: str, bases: tuple[type, ...],
                nmspc: dict[str, Any]) -> type:
        # Before creation: these changes take effect.
        nmspc["added_in_new"] = 42
        bases += (Tag,)
        return super().__new__(mcl, name, bases, nmspc)

    def __init__(cls, name: str, bases: tuple[type, ...],
                 nmspc: dict[str, Any]) -> None:
        super().__init__(name, bases, nmspc)
        # No effect: the class is already built.
        nmspc["added_in_init"] = 99
        # Effect: this modifies the finished class.
        setattr(cls, "patched_in_init", 3.14)


class Demo(metaclass=Meta):
    pass


print("added_in_new:", Demo.added_in_new)            # type: ignore
print("has Tag base:", Tag in Demo.__bases__)
print("added_in_init present:", hasattr(Demo, "added_in_init"))
print("patched_in_init present:", hasattr(Demo, "patched_in_init"))

""" Output:
added_in_new: 42
has Tag base: True
added_in_init present: False
patched_in_init present: True
"""
```

So override `__new__` when you must change `name`, `bases`, or the namespace
(including special members like `__slots__`) before the class is built.
Otherwise prefer `__init__`, which is simpler. When the choice does not matter,
pick `__init__` and reserve `__new__` for when it has a real reason.

## Intercepting Instance Creation

A method defined on the metaclass becomes a method of the *class object*,
callable on the class but not on its instances. These are sometimes called
*metamethods*. One useful metamethod is `__call__`, which runs when you create
an instance. Overriding it lets a metaclass intercept instance creation, which
is one way to build a Singleton:

```python
# singleton.py
# A Singleton metaclass: intercept instance creation through __call__.
from typing import Any


class Singleton(type):
    _instances: dict[type, Any] = {}

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

""" Output:
ASingleton BSingleton
"""
```

Each class gets its own entry in the `_instances` dictionary, so the singletons
stay independent.

This works, but it is heavier than the problem usually requires. A Singleton is
often clearer as a class decorator, which needs no metaclass at all:

```python
# singleton_decorator.py
# The same idea as a class decorator. Simpler than a metaclass.
from collections.abc import Callable
from typing import Any


def singleton(klass: type) -> Callable[..., Any]:
    instances: dict[type, Any] = {}

    def get_instance(*args: Any, **kwargs: Any) -> Any:
        if klass not in instances:
            instances[klass] = klass(*args, **kwargs)
        return instances[klass]

    return get_instance


@singleton
class Registry:
    def __init__(self) -> None:
        self.items: list[str] = []


a = Registry()
b = Registry()
assert a is b
a.items.append("widget")
print(b.items)

""" Output:
['widget']
"""
```

The simplest Python singleton of all is a module: import it anywhere and you get
the same object. Choose the lightest tool that solves your problem.

## Making a Class Final

It is sometimes useful to forbid inheritance, the way Java's `final` does. The
older literature claims this *requires* a metaclass, because the check must run
as each subclass is created. With `__init_subclass__`, it does not:

```python
# final.py
# Preventing inheritance with __init_subclass__, no metaclass
# required.


class A:
    pass


class B(A):
    # Make B final: any attempt to subclass it fails at class
    # creation.
    def __init_subclass__(cls, **kwargs: object) -> None:
        raise TypeError(
            f"{B.__name__} is final; you cannot subclass it")


print(B.__bases__)

try:
    class C(B):
        pass
except TypeError as error:
    print(error)

""" Output:
(<class '__main__.A'>,)
B is final; you cannot subclass it
"""
```

The check happens at class-creation time, exactly when it must, and `B` itself
is built normally because `A` does not forbid subclassing.

## When You Still Need a Metaclass

After all this, when is a metaclass the right tool? When you need to change the
class object itself rather than react to its creation: adding methods *to the
class* (metamethods such as a custom `__iter__` or `__call__` on the class,
shown above), replacing the namespace mapping with `__prepare__` so the class
body is built in a custom dictionary, or enforcing an invariant across an entire
family of classes through their shared metaclass. These are real but uncommon.
For everything else, `__init_subclass__`, `__set_name__`, and class decorators
are simpler and easier to read.

One caution: a class has exactly one metaclass. Multiple inheritance can
accidentally combine classes with different metaclasses, which raises a
metaclass conflict you then have to resolve. That is one more reason to avoid
metaclasses unless you truly need them.

## Testing the Hooks

Each hook has a small, definite effect, which makes it easy to test. The
registry should hold only the leaf classes, the descriptor should learn its name
and store under it, and a final class should refuse to be subclassed:

```python
# test_metaprogramming.py
import final
import init_subclass
import pytest
import set_name


def test_leaf_registry_tracks_only_leaves() -> None:
    leaves = {c.__name__ for c in init_subclass.Color.registry}
    assert leaves == {"Red", "Green", "PhthaloBlue", "CeruleanBlue"}


def test_independent_hierarchies_have_separate_registries() -> None:
    shapes = {c.__name__ for c in init_subclass.Shape.registry}
    assert shapes == {"Square", "Circle"}  # Round is no longer a leaf


def test_descriptor_learns_its_name() -> None:
    p = set_name.Point()
    p.x = 3
    p.y = 4
    assert (p.x, p.y) == (3, 4)
    assert p.__dict__ == {"_x": 3, "_y": 4}  # stored under the names


def test_descriptor_on_class_returns_itself() -> None:
    assert isinstance(set_name.Point.x, set_name.Field)


def test_final_class_cannot_be_subclassed() -> None:
    with pytest.raises(TypeError):
        class Sub(final.B):
            pass


def test_non_final_base_can_be_subclassed() -> None:
    class Ok(final.A):
        pass

    assert issubclass(Ok, final.A)
```

## Further Reading

> The `__init_subclass__` and `__set_name__` hooks were added in PEP 487:
-   <https://peps.python.org/pep-0487/>

> Python data model reference for class creation, `__set_name__`,
> `__init_subclass__`, `__prepare__`, and metaclasses:
-   <https://docs.python.org/3/reference/datamodel.html#metaclasses>

> Michele Simionato's articles on the difference between Python 2 and 3
> metaclasses:
-   <https://www.artima.com/weblogs/viewpost.jsp?thread=236234>
-   <https://www.artima.com/weblogs/viewpost.jsp?thread=236260>
