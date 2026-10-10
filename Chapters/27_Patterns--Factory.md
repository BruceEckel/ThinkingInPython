# Factory

> Adding a type should mean writing one class,
> but something in the program must still choose which class to construct.
> A *Factory* puts that choice in one place.

When a system needs new types,
start with a base type that gives them a common interface.
The common interface separates the rest of your code from knowledge of the specific types you add.
Adding a type then means writing one subclass,
with no changes to existing code ... or so it seems.
But something must still create an object of the new type,
and that creation code names the concrete class.
If object creation is spread throughout your application,
adding a type means finding and editing every place that names a concrete class.

Here `Triangle` has just joined the hierarchy.
Two call sites build shapes by calling `Circle()` or `Square()`,
and neither has been updated for `Triangle`:

```python
# shapes_naive.py
from abc import ABC, abstractmethod
from typing import override
from exceptions import expect

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...
    @abstractmethod
    def svg(self) -> str: ...

class Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")
    @override
    def svg(self) -> str: return '<circle r="1"/>'

class Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")
    @override
    def svg(self) -> str:
        return '<rect width="1" height="1"/>'

class Triangle(Shape):
    @override
    def draw(self) -> None: print("Triangle.draw")
    @override
    def svg(self) -> str:
        return '<polygon points="0,0 1,0 0,1"/>'

def render(kind: str) -> None:
    if kind == "Circle":
        Circle().draw()
    elif kind == "Square":
        Square().draw()

def export_svg(kind: str) -> None:
    match kind:
        case "Circle":
            print(Circle().svg())
        case "Square":
            print(Square().svg())
        case _:
            raise ValueError(f"Unknown shape: {kind}")

render("Circle")
#: Circle.draw
render("Triangle")  # Draws nothing, reports nothing
export_svg("Square")
#: <rect width="1" height="1"/>
expect(ValueError, export_svg, "Triangle")
#: [ValueError] Unknown shape: Triangle
```

The two call sites fail in different ways.
`render()` accepts `"Triangle"` and draws nothing,
with no error to signal the gap.
`export_svg()` has a wildcard case that raises an exception,
so it does report the gap, but only at runtime,
when someone first asks it for a triangle.
Nothing at edit time points at the missing case,
and the type checker cannot know which strings `export_svg()` should handle.
An `Enum` for `kind` and an `assert_never()` wildcard [move that report to check time](13_Techniques--Pattern_Matching.md#exhaustive-matching),
though an if-chain like `render()` still slips past the check.
Either way, adding a type means editing every call site.

The solution is to encapsulate object creation.
A common *factory* creates every object instead of spreading creational code through the system.
Your program must call this factory whenever it needs an object,
so adding a new type changes the factory and leaves every call site as it was.

Every object-oriented program creates objects,
and you often extend such programs by adding new types.
Thus, *Factory* might be the most common design pattern.

This chapter covers the creational patterns of *GoF Design Patterns*:
*Factory Method*, *Abstract Factory*, *Prototype*, and *Builder*.
The fifth, *Singleton*, has [its own chapter](24_Patterns--Singleton.md).
All five answer two questions: which object to build, and what code builds it.

## Simple Factory Method

Consider a `Shape` hierarchy in the style of [Rethinking Objects](20_Patterns--Rethinking_Objects.md#abstract-base-classes),
here with `draw()` and `erase()`.
We can add a factory as a `@staticmethod` of the base class:

```python
# shape_factory_method.py
import random
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import override

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...
    @abstractmethod
    def erase(self) -> None: ...
    # Create based on class name:
    @staticmethod
    def factory(kind: str) -> Shape:
        match kind:
            case "Circle":
                return _Circle()
            case "Square":
                return _Square()
            case _:
                raise ValueError(f"Bad shape: {kind}")

class _Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")
    @override
    def erase(self) -> None: print("Circle.erase")

class _Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")
    @override
    def erase(self) -> None: print("Square.erase")

def shape_name(n: int) -> Iterator[str]:
    for _ in range(n):
        cls = random.choice(Shape.__subclasses__())
        yield cls.__name__.removeprefix("_")

if __name__ == "__main__":
    random.seed(4)  # Reproducible shape sequence
    shapes = [Shape.factory(s) for s in shape_name(4)]
    for shape in shapes:
        shape.draw()
        shape.erase()
#: Circle.draw
#: Circle.erase
#: Square.draw
#: Square.erase
#: Circle.draw
#: Circle.erase
#: Square.draw
#: Square.erase
```

The `factory()` argument indicates the type of `Shape` to create.
Here that argument is a string, but it could be any sort of data.
Apart from the new subclass,
`factory()` is the only code that changes when you add a new type of `Shape`.

`factory()` names `_Circle` and `_Square` above the point where the file defines either class.
Python looks up a name in a function body when the function runs,
and both classes exist before anything calls `factory()`.

*GoF Design Patterns* defines *Factory Method* as a creation method that [subclasses override](#subclasses-choose-the-type)
to choose the concrete type.
This `factory()` is the smallest version of that idea: one class, one method,
and a `match` where the overrides would be.

`shape_name()` is a [*generator*](23_Patterns--Iterators.md#generators).
Whereas a factory takes information telling it what to build,
a generator object does the opposite.
It holds an internal algorithm and needs no argument to produce the next value.

`shape_name()` takes `n`
(the maximum number of shapes the generator can produce)
and returns a generator object.
That object produces names on demand.
Those names are the arguments to `Shape.factory()`.
Normally the initialization data comes from outside the system rather than through random generation.

Inside `shape_name()`,
`Shape.__subclasses__()` produces a list of `Shape`'s direct subclasses.
`__subclasses__()` covers only the first level of inheritance,
so a class inheriting from `_Circle` is not in the list.
For a deeper hierarchy, recurse through each subclass's own `__subclasses__()`
(see exercise 9).

### Hiding the Concrete Classes

The concrete shapes carry a leading underscore because no caller needs their names.
`factory()` returns `Shape`,
so a caller works with `Shape`s and has no need to name `_Circle`.
The underscore discourages direct construction,
but it is a convention rather than concealment.
[*Singleton*](24_Patterns--Singleton.md#nothing-keeps-the-class-private)
makes the same case.
`shape_name()` strips the underscore,
so the name a caller passes to `factory()` is `"Circle"`, not `_Circle`.

Nesting the classes inside `factory()` looks like stronger enforcement,
but is worse.
Because a `class` statement is executable code,
every `factory()` call defines fresh `Circle` and `Square` classes.
Two shapes from different calls then share behavior but not a class,
failing `type(a) is type(b)` and `isinstance()` alike.
`Shape.__subclasses__()` is empty until the first call,
then gains a duplicate `Circle` and `Square` on every call after that.
Each duplicate stays in the list until the garbage collector finds that no object uses it.

### Alternative Constructors Are Factories

[`Month.of()`](12_Techniques--Data_Classes_as_Types.md#enums-are-types-too)
is an alternative constructor,
a method on the type that builds an instance from data the constructor rejects.
There, `Month(7)` raises a `ValueError` because no member has the value `7`,
while `Month.of(7)` returns `JULY`.
`Month.of()` is also a factory, of the same form as `factory()`.
Both are static methods within the type.
Each takes data and returns an instance,
and each raises an exception for data it does not recognize.
For `Month`, that is a number outside one through twelve.
`of()` needs no `match`.
The `Enum` holds every member `of()` could return,
so the method indexes `list(Month)` instead of naming a class.
A factory over a closed set of products reduces to a lookup.

[`from_fahrenheit()`](07_Foundations--Classes.md#static-and-class-methods)
is the usual form of alternative constructor:
a `@classmethod` that computes the constructor's arguments and ends with `return cls(...)`.
That form is the most common factory,
and `dict.fromkeys()` and `datetime.fromisoformat()` are two from the standard library.
The `@classmethod` form chooses arguments rather than a class,
so a subclass that calls it gets an instance of the subclass with no override.

## The Pythonic Factory: a Dictionary

A factory turns data, such as a name, into an object,
so constructor calls stay in one place.
In Python a class is a first-class object.
You can store it in a variable and call it to construct an instance.
You saw this in [`defaultdict(list)`](03_Foundations--Containers.md#defaultdict)
and [`field(default_factory=list)`](12_Techniques--Data_Classes_as_Types.md#defaults-built-not-shared).
Both take a class where a function would do,
and call it whenever they need a fresh value.

Thus, the simplest factory is a dictionary that maps names to classes,
without a factory method or factory class:

```python
# shape_table.py
from abc import ABC, abstractmethod
from typing import Final, Literal, override

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...

class Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")

class Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")

type Kind = Literal["Circle", "Square"]

SHAPES: Final[dict[Kind, type[Shape]]] = {
    "Circle": Circle,
    "Square": Square,
}

def make(kind: Kind) -> Shape:
    return SHAPES[kind]()

make("Circle").draw()
#: Circle.draw
make("Square").draw()
#: Square.draw
# ty: expected Kind, found Literal["Hexagon"]:
# make("Hexagon").draw()
```

Because the `dict` values are classes, `type[Shape]` is their type,
and calling one constructs an instance.
Adding a `Triangle` means one new class and one new line in `SHAPES`,
and one new member in `Kind`.
Typing `kind` as the closed `Literal` instead of `str` moves a bad name from a runtime `KeyError` to a check-time error,
the same trade [Explicit Registration with a Protocol](#explicit-registration-with-a-protocol)
makes for a class that forgets `draw()`.
`Kind` names the two keys in `SHAPES`,
and the checker rejects a key that `Kind` does not list,
so adding a shape name to `SHAPES` requires adding it to the `Literal` first.

### Self Registration

Better still, a new `Shape` subclass can register itself with no edit to existing code.
In this case, a closed `Literal` complicates things by requiring an edit for every new subclass.

```python
# registry.py
from abc import ABC, abstractmethod
from typing import ClassVar, override

class Shape(ABC):
    registry: ClassVar[dict[str, type[Shape]]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Shape.registry[cls.__name__] = cls

    @abstractmethod
    def draw(self) -> None: ...

class Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")

class Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")

def make(name: str) -> Shape:
    return Shape.registry[name]()
```

[`__init_subclass__()`](17_Techniques--Metaprogramming.md#self-registration-of-subclasses)
lets each subclass register itself.
Nothing in the listing calls a register function.
The two `class` statements fill `Shape.registry` on their own.

Registering through `__init_subclass__()` is why `Shape` is an abstract base class rather than a `Protocol`.
`__init_subclass__()` runs only for classes that inherit from `Shape`,
so a class that satisfies a Protocol structurally,
without inheriting from `Shape`, stays out of the registry.
Inheritance is the mechanism, and `ABC` adds one guard on top of that.

A subclass registers as its `class` statement executes,
so a subclass that forgets `draw()` still registers.
The guard acts when `make()` constructs that class.
The call fails with a `TypeError`,
where a base class whose `draw()` raises a `NotImplementedError` waits for the first `draw()` call.
The type checker reports a line that constructs such a class by name,
but `make()` contains no such line.
`Shape.registry[name]()` calls a `type[Shape]`,
and any of those may be a concrete subclass, so the checker accepts it.
[Explicit Registration with a Protocol](#explicit-registration-with-a-protocol)
moves that report to the check.

To add a `Triangle` is a single class definition,
and `make()` builds it with no change to the factory.
`Shape.__subclasses__()` can build the table instead,
but it stops at direct subclasses,
while `__init_subclass__()` runs for every class anywhere below `Shape`.
[Pattern Refactoring](37_Patterns--Pattern_Refactoring.md#the-trash-hierarchy)
uses this same self-registration.

Importing `registry` runs its two `class` statements,
and the key list shows the table they left behind:

```python
# registry_demo.py
from exceptions import expect
from registry import Shape, make

print(sorted(Shape.registry))
#: ['Circle', 'Square']
for name in ["Circle", "Square", "Circle"]:
    make(name).draw()
#: Circle.draw
#: Square.draw
#: Circle.draw
expect(KeyError, make, "Triangle")
#: [KeyError] 'Triangle'
```

`make("Triangle")` fails with a `KeyError` naming the missing key,
because no class has registered under that name.
The closed `Literal` in `shape_table.py` rejects `"Hexagon"` before the program runs.
An open registry cannot do that,
since a name becomes valid the moment some module defines the class,
so the check moves to runtime.

The figure sets the opening problem from `shapes_naive.py` beside the registry,
so you can compare what adding `Triangle` costs before and after the factory:

![](_images/factory_story)

In the first frame, each call site holds its own arrow to every class,
so a new class needs a new arrow, and an edit, at each call site.
In the registry frames the arrows run the other way.
Each class points at the table, and the callers point at `make()` alone.
`Triangle` adds one arrow, from its own `class` statement.

### Hazards of Self Registration

`__init_subclass__()` runs as the subclass's `class` statement executes.
When the subclasses sit in the same file as `make()`, as in `registry.py`,
the registration runs before anything calls `make()`,
but a subclass defined in another module registers itself only when something imports that module.
The classic failure is a plugin that "never registered."
The class is fine, the registry is fine,
and nothing imported the module that defines the class.

A [lazy import](06_Foundations--Modules_and_Packages.md#lazy-imports)
produces the same failure even when the import statement is in the file.
The module body, and with it the registration,
waits for the first use of the imported name.
An import written only to trigger registration never uses that name.
Running with `-X lazy_imports=all` makes ordinary imports lazy too,
so the same failure can appear in a program with no `lazy` keyword in it.
Import a plugin module eagerly when the import exists for its side effect.

The registry keys on `cls.__name__` alone, so two classes that share a name,
from different modules, silently overwrite each other.
Key on `f"{cls.__module__}.{cls.__qualname__}"` when a collision is possible.

The registry also keeps every entry it receives.
A class defined inside a function or a test stays in the table,
and the strong reference keeps the class alive for the rest of the process.

`__init_subclass__()` names `Shape.registry` rather than `cls.registry` on purpose.
`cls.registry` resolves through the [MRO](07_Foundations--Classes.md#method-resolution-order),
so a subclass that defines its own `registry` creates a second table beside the one `make()` reads,
with no error to signal it.

`make()` stays a module-level function for three reasons.
A `@classmethod` looks up `cls.registry`,
so a subclass with its own `registry` sends `Triangle.make()` to that second table,
the one `__init_subclass__()` avoids by naming `Shape.registry`.
And `Circle.make("Square")` is legal as well as misleading,
since the key decides what `make()` builds,
not the class you name before the dot.
A method of any kind also puts back the factory method that [The Pythonic Factory: a Dictionary](#the-pythonic-factory-a-dictionary)
set out to remove.

### Testing the Registry

Testing confirms that every subclass registers itself,
that `make()` builds the class registered under each name,
and that a new subclass needs no change to `make()`.
Defining a fresh subclass of `Shape` inside `test_new_subclass_registers_itself()` is enough to put it in the registry:

```python
# test_registry.py
from typing import override
import pytest
from registry import Circle, Shape, Square, make

def test_subclasses_register_themselves() -> None:
    assert Shape.registry["Circle"] is Circle
    assert Shape.registry["Square"] is Square

def test_make_builds_the_right_type() -> None:
    assert isinstance(make("Circle"), Circle)
    assert isinstance(make("Square"), Square)

def test_new_subclass_registers_itself() -> None:
    class Triangle(Shape):
        @override
        def draw(self) -> None: ...

    assert Shape.registry["Triangle"] is Triangle
    assert isinstance(make("Triangle"), Triangle)

def test_unknown_name_raises_key_error() -> None:
    with pytest.raises(KeyError):
        make("Hexagon")
```

`test_unknown_name_raises_key_error()` asks for `"Hexagon"` rather than the `"Triangle"` that `registry_demo.py` used,
because the `Triangle` that `test_new_subclass_registers_itself()` defined is still in the registry.

### Explicit Registration with a Protocol

The ABC in `registry.py` exists so that `__init_subclass__()` has a class from which to run.
If registration is explicit instead, `Shape` can be a Protocol,
with a class decorator doing the registering.
The table then needs no class on which to live,
and its natural owner is the factory that reads it.
Python lets you [set an attribute on a function](17_Techniques--Metaprogramming.md#attributes-on-a-function),
but the type checker reports every dotted access to such an attribute,
so the factory becomes a small callable object that holds the table:

```python
# shape_registry.py
from typing import Protocol

class Shape(Protocol):
    def draw(self) -> None: ...

class ShapeFactory:
    def __init__(self) -> None:
        self.registry: dict[str, type[Shape]] = {}

    def register[S: Shape](self, cls: type[S]) -> type[S]:
        self.registry[cls.__name__] = cls
        return cls

    def __call__(self, name: str) -> Shape:
        return self.registry[name]()
```

`register()` stores a class under its name and returns the class unchanged,
so it works as a [class decorator](14_Techniques--Decorators.md#decorating-classes).
[`__call__()`](28_Patterns--Function_Objects.md#a-callable-object-as-a-command)
makes a `ShapeFactory` instance callable,
so you call the factory the way you call `make()` in `registry.py`.
Each class registers with the factory that builds it:

```python
# protocol_registry.py
from shape_registry import ShapeFactory

make = ShapeFactory()

@make.register
class Circle:
    def draw(self) -> None: print("Circle.draw")

@make.register
class Square:
    def draw(self) -> None: print("Square.draw")

print(sorted(make.registry))
#: ['Circle', 'Square']
make("Circle").draw()
#: Circle.draw
# ty: Argument type `Blob` does not satisfy
# upper bound `Shape` of type variable `S`:
# @make.register
# class Blob:
#     pass
```

`@make.register` has the same form as `@nectar.register` in [*Visitor*](33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch),
where `functools.singledispatch` keeps a function's table beside it.
`singledispatch` cannot serve as this factory,
because it picks an implementation by the type of its first argument,
and `make()` receives a name.

The type parameter of `register()` has `Shape` as its bound,
and the bound turns the decorator into a check.
A decorated class must satisfy the Protocol, so a class without `draw()`,
or with a `draw()` that takes an extra parameter,
gets an `invalid-argument-type` diagnostic at its `@make.register` line before the program runs.
That is the case [Self Registration](#self-registration) left to runtime,
where a subclass that forgets `draw()` registers, fails at construction,
and no checker sees it.
`register()` returns `type[S]`, the decorated class's own type,
so after the decorator runs the checker still knows `Circle` as `Circle`,
not as `Shape`.

The bound is also why the factory names `Shape` instead of taking a type parameter.
A generic factory would need `register()`'s bound to name the factory's own type parameter,
and the type checker rejects a bound that contains another type parameter.

Keeping the table in the factory removes two hazards from [Hazards of Self Registration](#hazards-of-self-registration).
No `cls.registry` lookup walks the MRO,
and no `@classmethod` needs a class on which to sit,
since the table belongs to `make` rather than to a class in the hierarchy.
An intermediate class also stays out of the table unless something decorates it.
Under `__init_subclass__()`,
an abstract `Polygon` between `Shape` and `Triangle` registers as well,
and `make("Polygon")` fails with a `TypeError`.

Explicit registration fails the opposite way.
Registration is opt-in,
so a class that satisfies `Shape` but lacks `@make.register` is absent from the table,
and `make()` fails with a `KeyError` that names the key,
not the class that lacks the decorator (see exercise 10).
A subclass of the ABC cannot skip registration that way,
because the subclass line is the registration.
The runtime guard is weaker too.
A class that ignores the checker's report still registers,
and fails with an `AttributeError` at its first `draw()` call rather than a `TypeError` at construction.
Choose the failure you prefer:
the ABC catches the incomplete class at construction,
the Protocol at check time.

A factory that is an object also gives each test its own table.
The test file confirms that `register()` stores the class and returns it,
that the factory builds a registered class, and that a new factory starts empty:

```python
# test_protocol_registry.py
import pytest
from shape_registry import ShapeFactory

class Triangle:
    def draw(self) -> None: ...

def test_register_stores_and_returns_the_class() -> None:
    make = ShapeFactory()
    assert make.register(Triangle) is Triangle
    assert make.registry == {"Triangle": Triangle}

def test_make_builds_a_registered_class() -> None:
    make = ShapeFactory()
    make.register(Triangle)
    assert isinstance(make("Triangle"), Triangle)

def test_each_factory_starts_empty() -> None:
    make = ShapeFactory()
    with pytest.raises(KeyError):
        make("Triangle")
```

`test_each_factory_starts_empty()` passes although `test_make_builds_a_registered_class()` registered `Triangle`,
because each test registers with a `ShapeFactory` of its own.
`test_registry.py` cannot do that.
`Shape.registry` is one table for the whole process,
so `test_unknown_name_raises_key_error()` in `test_registry.py` asks for `"Hexagon"`.

The ordinary Python factory is a dictionary of classes,
whether you fill it by hand, the classes fill it themselves,
or the factory's own decorator fills it.
That is the dissolution [Design Patterns](21_Patterns--Design_Patterns.md#when-a-pattern-dissolves)
describes.
The pattern remains, but no longer needs a class hierarchy to express it.

## Factory Objects

Because the static `factory()` method in `shape_factory_method.py` collects all the creation operations in one place,
that method is the only code you change.
A *factory object* defines a single `create()` method,
so choosing what to build becomes choosing which factory object to call,
rather than passing a string to a `match` statement.
Here, we create one factory object per `Shape` subtype:

```python
# shape_factory_objects.py
import random
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Final, Protocol, override

class ShapeMaker(Protocol):
    def create(self) -> Shape: ...

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...
    @abstractmethod
    def erase(self) -> None: ...

class _Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")
    @override
    def erase(self) -> None: print("Circle.erase")
    class Factory:
        def create(self) -> _Circle: return _Circle()

class _Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")
    @override
    def erase(self) -> None: print("Square.erase")
    class Factory:
        def create(self) -> _Square: return _Square()

FACTORIES: Final[dict[str, ShapeMaker]] = {
    "Circle": _Circle.Factory(),
    "Square": _Square.Factory(),
}

def create_shape(kind: str) -> Shape:
    return FACTORIES[kind].create()

def shape_name(n: int) -> Iterator[str]:
    types = Shape.__subclasses__()
    for _ in range(n):
        cls = random.choice(types)
        yield cls.__name__.removeprefix("_")

if __name__ == "__main__":
    random.seed(4)
    shapes = [create_shape(kind) for kind in shape_name(4)]
    for shape in shapes:
        shape.draw()
        shape.erase()
#: Circle.draw
#: Circle.erase
#: Square.draw
#: Square.erase
#: Circle.draw
#: Circle.erase
#: Square.draw
#: Square.erase
```

Each type of shape defines its own nested `Factory` class whose `create()` method builds an object of that type.
`ShapeMaker` is the interface those factories share.
Here it is a `Protocol`,
so the two nested `Factory` classes conform without naming it.
`FACTORIES` maps each kind's name to an instance of its factory,
and `create_shape()` looks up that factory and calls its `create()`.

A more complex design returns the factory object to the caller,
who keeps it to construct objects later.
Much of the time, however, a single static method in the base class
(as in `shape_factory_method.py`) is enough.

Python does not need a `Factory` class nested in every shape.
`shape_factory_objects.py` includes one because a language that cannot store a class in a dictionary must wrap each constructor in an object.
The registry in `registry.py` does the same job with no nested classes.
Use a separate factory class when object creation needs work beyond calling a constructor,
such as pooling, caching, or consulting external configuration.

You could eliminate `FACTORIES` by dispatching through `eval(f"_{kind}.Factory()")`.
Dispatching through `eval()` is unnecessary, and it makes things worse.
`create_shape()` then compiles and runs any string it receives,
so a configuration file, a request,
or a command line can hand it arbitrary code instead of a shape name.
The dictionary lookup runs no code from the string.
You get either a factory or a `KeyError`,
and the type checker knows the factory as a `ShapeMaker`,
where `eval()` returns `Any`.

## Subclasses Choose the Type

Every factory so far keeps the choice in one place: a `match` in `factory()`,
a key in `SHAPES`, a lookup in `FACTORIES`.
*Factory Method* moves the choice into the type of the object you hold.
A base class calls a creation method it does not implement,
and each subclass overrides that method to name a concrete product:

```python
# shape_sketch.py
from abc import ABC, abstractmethod
from typing import override

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...

class Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")

class Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")

class Sketch(ABC):
    # The factory method:
    @abstractmethod
    def new_shape(self) -> Shape: ...
    def render(self, n: int) -> None:
        for _ in range(n):
            self.new_shape().draw()

class CircleSketch(Sketch):
    @override
    def new_shape(self) -> Shape: return Circle()

class SquareSketch(Sketch):
    @override
    def new_shape(self) -> Shape: return Square()

for sketch in (CircleSketch(), SquareSketch()):
    sketch.render(2)
#: Circle.draw
#: Circle.draw
#: Square.draw
#: Square.draw
```

`render()` uses a `Shape` without naming one.
`new_shape()` is the factory method,
and the only method `CircleSketch` and `SquareSketch` override.
Adding a `Triangle` means one new `Shape` subclass and one new `Sketch` subclass,
with no edit to existing code.
Overriding a creation method in a subclass is the form *GoF Design Patterns* describes,
and the reason the pattern is named for a method rather than for a class.

*Factory Method* adds a second hierarchy.
Each product needs a creator that produces it,
so the two hierarchies grow together.
The second hierarchy is worth having only when the creator does work of its own,
as `render()` does here.
When choosing the class is the creator's only job,
a dictionary of classes says the same thing with no second hierarchy:
`shape_table.py` when the set of shapes is closed,
`protocol_registry.py` when it is open.

## Abstract Factories

The *Abstract Factory* pattern has the same structure as `Sketch`,
with not one but several factory methods, each overridden in a concrete factory.
Each factory method creates a different kind of object.
Creating the factory object chooses the concrete version of every object that factory creates.
The example in *GoF Design Patterns* makes one program work across several graphical user interfaces
(GUIs).
You create a factory object for the GUI you use,
and from then on when you ask that factory for a menu, button, or slider,
the factory creates the version of that item suited to that GUI.
Switching from one GUI to another then touches only a single place in the code,
most likely via startup configuration.

As another example, suppose you are creating a general-purpose gaming environment that supports different types of games.

![](_images/abstract_factory)

`Character` and `Obstacle` are parallel hierarchies,
and each concrete factory declares one method per hierarchy.
`KittiesAndPuzzles` always pairs a `Kitty` with a `Puzzle`,
`WarriorsAndWeapons` always pairs a `Warrior` with a `Weapon`,
and `GameEnvironment.play()` depends on getting such a matched pair.
Choosing the factory chooses both halves at once:

```python
# abstract_factory_abc.py
from abc import ABC, abstractmethod
from typing import override

class Obstacle(ABC):
    @abstractmethod
    def description(self) -> str: ...

class Character(ABC):
    @abstractmethod
    def interact_with(self, obstacle: Obstacle) -> None: ...

class Kitty(Character):
    @override
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Kitty encounters a", obstacle.description())

class Warrior(Character):
    @override
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Warrior battles a", obstacle.description())

class Puzzle(Obstacle):
    @override
    def description(self) -> str:
        return "Puzzle"

class Weapon(Obstacle):
    @override
    def description(self) -> str:
        return "Weapon"

# The Abstract Factory:
class GameElementFactory(ABC):
    @abstractmethod
    def make_character(self) -> Character: ...
    @abstractmethod
    def make_obstacle(self) -> Obstacle: ...

# Concrete factories:
class KittiesAndPuzzles(GameElementFactory):
    @override
    def make_character(self) -> Character: return Kitty()
    @override
    def make_obstacle(self) -> Obstacle: return Puzzle()

class WarriorsAndWeapons(GameElementFactory):
    @override
    def make_character(self) -> Character: return Warrior()
    @override
    def make_obstacle(self) -> Obstacle: return Weapon()

class GameEnvironment:
    def __init__(self, factory: GameElementFactory) -> None:
        self.character = factory.make_character()
        self.obstacle = factory.make_obstacle()
    def play(self) -> None:
        self.character.interact_with(self.obstacle)

g1 = GameEnvironment(KittiesAndPuzzles())
g2 = GameEnvironment(WarriorsAndWeapons())
g1.play()
#: Kitty encounters a Puzzle
g2.play()
#: Warrior battles a Weapon
```

`Character` objects interact with `Obstacle` objects,
but the types of characters and obstacles depend on the game you're playing.
Choosing a particular `GameElementFactory` determines the game.

The `GameEnvironment` controls the setup and play of the game.
Setup and play are simple here,
but the initial conditions and the way the state changes can determine much of a game's outcome.
`GameEnvironment` has no place to vary the rules of play,
so a real game adds one: a subclass overriding `play()`,
or a rules object passed alongside the factory.

`interact_with()` dispatches on the character's type and `obstacle.description()` dispatches again on the obstacle's.
Thus, the pair of calls chooses behavior from both types.
[*Multiple Dispatching*](32_Patterns--Multiple_Dispatching.md)
develops that pair of calls into a technique.

`Obstacle`, `Character`, and `GameElementFactory` are abstract base classes.
Each one lists the methods its subclasses must supply,
as `@abstractmethod`s with no body.
Suppose you write a factory subclass and forget `make_obstacle()`.
Python defines the class,
and the `TypeError` appears when you create an instance,
before `GameEnvironment.__init__()` calls anything,
the same way `make()` fails on a `Shape` subclass that forgets `draw()`,
and `Partial()` does in [*Surrogate*](26_Patterns--Surrogate.md#proxy).
The type checker reports that construction before the program runs.

A Protocol names the required methods and needs no base class,
so a Protocol simplifies the *Abstract Factory*:

```python
# abstract_factory_protocol.py
from typing import Protocol

class Obstacle(Protocol):
    def description(self) -> str: ...

class Character(Protocol):
    def interact_with(self, obstacle: Obstacle) -> None: ...

class GameElementFactory(Protocol):
    def make_character(self) -> Character: ...
    def make_obstacle(self) -> Obstacle: ...

class Kitty:
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Kitty encounters a", obstacle.description())

class Warrior:
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Warrior battles a", obstacle.description())

class Puzzle:
    def description(self) -> str: return "Puzzle"

class Weapon:
    def description(self) -> str: return "Weapon"

# Concrete factories:
class KittiesAndPuzzles:
    def make_character(self) -> Kitty: return Kitty()
    def make_obstacle(self) -> Puzzle: return Puzzle()

class WarriorsAndWeapons:
    def make_character(self) -> Warrior: return Warrior()
    def make_obstacle(self) -> Weapon: return Weapon()

class GameEnvironment:
    def __init__(self, factory: GameElementFactory) -> None:
        self.character = factory.make_character()
        self.obstacle = factory.make_obstacle()
    def play(self) -> None:
        self.character.interact_with(self.obstacle)

class BrokenFactory:
    def make_character(self) -> Kitty: return Kitty()

g1 = GameEnvironment(KittiesAndPuzzles())
g2 = GameEnvironment(WarriorsAndWeapons())
# ty: expected "GameElementFactory", found "BrokenFactory":
# GameEnvironment(BrokenFactory())  # [1]
g1.play()
#: Kitty encounters a Puzzle
g2.play()
#: Warrior battles a Weapon
```

The type checker verifies that each concrete class satisfies the appropriate `Protocol`.
A `GameElementFactory` must supply `make_character()` and `make_obstacle()`,
a `Character` must supply `interact_with()`,
and an `Obstacle` must supply `description()`.
`BrokenFactory` supplies `make_character()` and omits `make_obstacle()`.
If you uncomment `[1]`, which passes a `BrokenFactory` to `GameEnvironment`,
the checker reports `protocol member make_obstacle is not defined on type BrokenFactory`.

Both versions report the omission before the program runs, at different places.
With the abstract base classes in `abstract_factory_abc.py`,
the checker reports the line that constructs the incomplete factory.
With the Protocol, constructing a `BrokenFactory` is legal,
and the checker reports `[1]`, which passes it to `GameEnvironment`.
The two differ more at runtime.
The abstract base class refuses to construct the factory,
while the Protocol has no runtime guard.
A program that ignores the report fails with an `AttributeError` when `GameEnvironment.__init__()` calls `make_obstacle()`.
Checking against a Protocol is [structural typing](08_Foundations--Static_Types.md#structural-typing-with-protocols).
Structural typing preserves the purpose of the interfaces,
without the coupling a shared base class imposes.

## Prototype

The factories so far build each object from a class and some arguments.
*Prototype* instead keeps one fully configured instance and makes new objects by copying it.
Use *Prototype* when a ready-made instance is easier to clone than to construct,
or when construction is slow and the instances share most of the setup.

The `copy` module does the cloning.
`copy.deepcopy()` follows every reference,
so the clone shares no mutable state with the original:

```python
# prototype.py
import copy
from dataclasses import dataclass, field

@dataclass
class Monster:
    name: str
    hp: int
    powers: list[str] = field(default_factory=list)

    def clone(self) -> Monster:
        return copy.deepcopy(self)

goblin = Monster("Goblin", hp=10, powers=["bite"])
# Build a variant by cloning and adjusting:
captain = goblin.clone()
captain.name = "Captain"
captain.hp = 20
captain.powers.append("rally")
print(goblin)
#: Monster(name='Goblin', hp=10, powers=['bite'])
print(captain)
#: Monster(name='Captain', hp=20, powers=['bite', 'rally'])
shallow = copy.copy(goblin)
shallow.powers.append("shared")
print(goblin.powers)  # The original changed too
#: ['bite', 'shared']
# Rebuild through the constructor with new field values:
knight = copy.replace(goblin, name="Knight", hp=30)
print(knight)
#: Monster(name='Knight', hp=30, powers=['bite', 'shared'])
print(knight.powers is goblin.powers)
#: True
```

Because the `clone()` method wraps `copy.deepcopy()`,
`captain` gets its own `powers` list,
and appending to it leaves `goblin.powers` unchanged.
The `shallow` lines are a warning, not an example to follow.
`copy.copy()` duplicates the `Monster` and shares its `powers` list,
so changing that list through one object changes it for the other,
with no error to signal the sharing.

`deepcopy()` restores the clone's state without running the constructor,
so a clone [skips the `__post_init__()` check](12_Techniques--Data_Classes_as_Types.md#copy-skips-the-constructor).
A prototype of a validated type is safe because the prototype is valid,
not because the clone is checked.
When the variant differs only in field values,
`copy.replace()` builds it through the constructor, as `knight` shows,
so a `__post_init__()` check runs on the result.

`copy.replace()` passes every field you do not name by reference,
so `knight` shares `goblin`'s `powers` list, the same sharing `shallow` shows.
Pass a fresh list for that field when the variant must own one.

`deepcopy()` copies everything it can reach,
and it has no way to copy an open file, a socket, or a lock,
so a prototype holding one makes `deepcopy()` raise a `TypeError`.
For a lock the message is `cannot pickle '_thread.lock' object`.
The message names pickling because `deepcopy()` copies a type it has no rule for through the pickle protocol.
Give such a class a `__deepcopy__()` that says what the copy holds instead:
a fresh connection, or an empty slot the clone fills when it first needs one.

You can combine *Prototype* with a registry.
Instead of a registry of classes,
keep a registry of prototypical instances and clone the chosen one:

```python
# prototype_registry.py
import copy
from dataclasses import dataclass, field
from typing import Final, Literal

@dataclass
class Monster:
    name: str
    hp: int
    powers: list[str] = field(default_factory=list)

type Kind = Literal["goblin", "troll"]

PROTOTYPES: Final[dict[Kind, Monster]] = {
    "goblin": Monster("Goblin", hp=10, powers=["bite"]),
    "troll": Monster("Troll", hp=40,
                     powers=["smash", "regen"]),
}

def spawn(kind: Kind) -> Monster:
    return copy.deepcopy(PROTOTYPES[kind])

if __name__ == "__main__":
    a = spawn("goblin")
    b = spawn("goblin")
    b.hp = 5
    print(a.hp, b.hp)  # The copies are independent
    print(spawn("troll"))
#: 10 5
#: Monster(name='Troll', hp=40, powers=['smash', 'regen'])
```

Because `spawn()` returns an independent object every time,
callers can modify their copy while the prototype stays as it was.
Compare `spawn()` with `make()` in `registry.py`.
There the table holds classes and `make()` calls one.
Here the table holds instances and `spawn()` copies one.
Use the prototype form when the interesting part of an object is its configured state rather than its type.

A prototype registry has two required properties.
Each spawn must be independent, and the stored prototype must stay unchanged:

```python
# test_prototype.py
from prototype_registry import PROTOTYPES, spawn

def test_spawn_is_independent() -> None:
    a = spawn("goblin")
    b = spawn("goblin")
    b.powers.append("curse")
    assert a.powers == ["bite"]
    assert b.powers == ["bite", "curse"]

def test_prototype_untouched() -> None:
    spawned = spawn("troll")
    spawned.hp = 1
    spawned.powers.append("bellow")
    assert PROTOTYPES["troll"].hp == 40
    assert spawned.powers is not PROTOTYPES["troll"].powers
    assert PROTOTYPES["troll"].powers == ["smash", "regen"]
```

## Builder

*Builder* is the last of the creational patterns.
It builds a complex object in steps,
keeping the step-by-step assembly separate from the finished object.
In *GoF Design Patterns* a *director* issues the steps to a builder through an abstract interface,
so one construction process can produce different representations.
The example in *GoF Design Patterns* is a document reader that hands each token to a converter,
and the converter decides whether the result is ASCII text or TeX.

The builder most programmers meet is narrower,
the one Joshua Bloch's *Effective Java* recommends.
In Java and C++, a class with many optional settings needs a constructor for every useful combination,
because those languages have no keyword arguments.
That pile of constructors is the *telescoping constructor*.
This builder, translated into Python, is the workaround,
a companion class that collects settings one method call at a time.

```python
# pizza_builder.py
from typing import Self
from record import record

@record
class Pizza:
    size: int
    cheese: bool
    toppings: tuple[str, ...]

class PizzaBuilder:
    def __init__(self) -> None:
        self._size = 12
        self._cheese = True
        self._toppings: list[str] = []

    def size(self, inches: int) -> Self:
        self._size = inches
        return self

    def no_cheese(self) -> Self:
        self._cheese = False
        return self

    def topping(self, name: str) -> Self:
        self._toppings.append(name)
        return self

    def build(self) -> Pizza:
        return Pizza(
            self._size, self._cheese, tuple(self._toppings))

if __name__ == "__main__":
    pizza = (PizzaBuilder()
             .size(16)
             .topping("basil")
             .topping("olives")
             .build())
    print(pizza)
#: Pizza(size=16, cheese=True, toppings=('basil', 'olives'))
```

You can chain the calls because each setter returns `self`.
`build()` freezes the accumulated settings into an immutable `Pizza`.

The builder is quietly single-use.
`build()` reads `self._toppings` without clearing it,
so a second `build()` on the same builder returns a pizza carrying the first pizza's toppings,
and every `.topping()` call in between adds to that same list.
The chained call in `__main__` hides the problem,
because it keeps no reference to the builder after `build()` returns.
Making the builder reusable means resetting the fields in `build()`,
and that reset removes the other reasonable use:
configuring a builder once and building from it twice.

Apart from the single-use hazard,
the builder class solves a problem Python does not have.
Keyword arguments with defaults are Python's built-in builder:

```python
# pizza_direct.py
from dataclasses import replace
from record import record

@record
class Pizza:
    size: int = 12
    cheese: bool = True
    toppings: tuple[str, ...] = ()

if __name__ == "__main__":
    pizza = Pizza(size=16, toppings=("basil", "olives"))
    print(pizza)
    family = replace(pizza, size=20)
    print(family)
#: Pizza(size=16, cheese=True, toppings=('basil', 'olives'))
#: Pizza(size=20, cheese=True, toppings=('basil', 'olives'))
```

Every combination of settings is a single call.
The call site names each option just as the chain does, and the fields,
not a second class, declare the defaults.

A second use for builder chains is to vary an existing configuration.
For a record, `replace()` is *Prototype* and *Builder* in one function,
copying the configured state and changing the chosen fields in the copy.
`copy.replace()` is the [general form of the operation](12_Techniques--Data_Classes_as_Types.md#the-general-form-of-replace),
and works on any object that defines `__replace__()`.

Testing confirms that the two forms produce the same pizza,
that `replace()` changes one field of a copy and keeps the rest,
and that a second `build()` on the same builder carries the first pizza's toppings:

```python
# test_pizza.py
from dataclasses import replace
import pizza_builder as pb
import pizza_direct as pd

def test_builder_and_keywords_agree() -> None:
    built = (pb.PizzaBuilder()
             .size(16).topping("basil").build())
    direct = pd.Pizza(size=16, toppings=("basil",))
    assert (built.size, built.cheese, built.toppings) == (
        direct.size, direct.cheese, direct.toppings)

def test_replace_varies_one_field() -> None:
    base = pd.Pizza()
    variant = replace(base, size=18)
    assert base.size == 12 and variant.size == 18
    assert variant.toppings == base.toppings

def test_second_build_reuses_toppings() -> None:
    builder = pb.PizzaBuilder().topping("basil")
    first = builder.build()
    second = builder.topping("olives").build()
    assert first.toppings == ("basil",)
    assert second.toppings == ("basil", "olives")
```

The (unrelated) [*Decorator* pattern](14_Techniques--Decorators.md#the-decorator-pattern)
has its own `Pizza`,
modeling toppings as wrapper objects instead of builder-collected fields.

*Builder* remains useful in Python when construction is genuinely a process.
The steps must come in order, later steps depend on earlier ones,
and some rules apply across several steps.
`GameBuilder` in [Simulation](38_Patterns--Simulation.md#building-the-maze-in-stages)
is such a builder.
It assembles a maze in three stages: creating rooms,
connecting each room to its neighbors,
then pairing the teleports that share a target letter.
Each stage relies on the previous stage.
No list of keyword arguments can express that.
The standard library's `argparse.ArgumentParser` has the same shape.
`add_argument()` calls accumulate a specification,
and `parse_args()` is the `build()`.

The smallest builder is easy to overlook.
Appending parts to a list and finishing with `"".join(parts)` builds an immutable string through a mutable intermediate.
`PizzaBuilder` has the same shape.
It collects toppings in a list and freezes them into a tuple at `build()`.
That shape is everywhere,
so save the name *Builder* for construction that is a process in its own right,
with intermediate state and rules that apply across several steps.
When each builder call sets one optional value,
a data class with keyword arguments does the job.

## Which Factory to Use

Match the machinery to what varies:

- When a name maps to a class, use a dictionary.
  When the set of classes is closed,
  write the table by hand and key it by a `Literal`, as in `shape_table.py`,
  so a bad name fails at the check.
  When the set is open-ended or spread across modules,
  let the classes fill the table:
  `__init_subclass__()` on an ABC if a subclass must register by existing,
  a factory object whose bounded `@make.register` takes Protocol classes if the checker should reject an incomplete class.
- When the choice is which arguments to pass, not which class,
  write an alternative constructor,
  a `@classmethod` that ends with `return cls(...)`.
- When construction takes real work beyond calling a constructor
  (pooling, caching, consulting configuration), write a factory function,
  and a factory class only when that work has state of its own.
- When you must choose several products together as a matched set,
  use *Abstract Factory*, expressed as a `Protocol` rather than a base class.
- When the interesting part of an object is its configured state rather than its type,
  keep a prototype and copy it.
  For a record, `replace()` is that copy.
- When construction is a genuine process with ordered steps and rules that apply across several of them,
  use *Builder*.
  When each builder call sets one optional value,
  keyword arguments are the builder.

The static `factory()` method and the nested-`Factory`-class dispatcher are here because the object-oriented tradition writes factories that way,
not because Python needs them.
Both exist to work around languages where a class is not an object you can put in a dictionary.

## Exercises

Try each exercise before opening its [solution](../Solutions/27_Patterns--Factory/).

1.  Add a class `Triangle` to `shape_factory_method.py`.
2.  Add a class `Triangle` to `shape_factory_objects.py`.
3.  Add a new type of `GameElementFactory` called `GnomesAndFairies`,
    first to `abstract_factory_abc.py` and then to `abstract_factory_protocol.py`.
    In `abstract_factory_protocol.py`, leave out `make_obstacle()` at first,
    pass the factory to `GameEnvironment`,
    and confirm the error your type checker reports.
    Then add `make_obstacle()`.
4.  Modify `shape_factory_objects.py` to use an *Abstract Factory* to create different sets of shapes
    (for example, one type of factory object creates "thick shapes," another creates "thin shapes," but each factory object can create all the shapes: circles, squares, triangles, etc.).
5.  Add a rule to both pizza examples: a pizza may carry at most four toppings.
    In `pizza_direct.py`, enforce it with `__post_init__()`,
    as [Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#a-type-is-a-set-of-values)
    does for `Stars`.
    In `pizza_builder.py`,
    decide whether it belongs in `topping()` or `build()`.
    In which version can an invalid pizza exist, even momentarily?
    `stars_class.py` in that chapter shows the same hazard.
6.  Move `Circle` and `Square` out of `registry.py` into a new module,
    `extra_shapes.py`.
    Confirm that `make("Circle")` now raises `KeyError` until something imports `extra_shapes`,
    and explain which line of which file registers the class, and when it runs.
    Then make `registry_demo.py` print the same key list it printed before the move.
7.  Give `Monster` in `prototype_registry.py` a `parts: dict[str, int]` field and add a prototype that uses it.
    Change `spawn()` to use `copy.copy()` instead of `copy.deepcopy()`,
    run `test_prototype.py` with `pytest`
    (`uv run pytest Examples/27_Patterns--Factory/test_prototype.py` from the repository root),
    and explain which assertions fail and why.
    Then restore `deepcopy()` and add a test that would have caught the bug through `parts` rather than `powers`.
8.  Recreate the `eval()` dispatcher described after `shape_factory_objects.py`'s listing:
    a `create_shape()` that builds each factory with `eval(f"_{kind}.Factory()")` instead of consulting `FACTORIES`.
    Call it with a `kind` string that is not a shape name but a Python expression with a side effect,
    and show that it runs the expression.
    Then show that the `FACTORIES` version raises `KeyError` for the same string.
9.  Derive `_Oval` from `_Circle` in `shape_factory_method.py`,
    give it its own `draw()`, and add a `case "Oval"` to `factory()`.
    Run the program and confirm that `shape_name()` never yields `"Oval"`,
    then explain why.
    Write a recursive generator `all_subclasses()` that yields a class's direct subclasses and,
    through each one's own `__subclasses__()`, every class below them.
    Use it in `shape_name()` and confirm that `Oval` now appears.
10. Add a `Hexagon` to `protocol_registry.py` that satisfies `Shape` but carries no `@make.register`,
    and show what `make("Hexagon")` does.
    Then write a check that reports every class in the module that satisfies `Shape` and is missing from `make.registry`,
    so you find the forgotten decorator before any `make()` call.
    `@runtime_checkable`, which [*Surrogate*](26_Patterns--Surrogate.md#proxy)
    shows with `isinstance()`,
    also lets `issubclass()` test a class against a Protocol whose members are all methods.
11. Fill `PROTOTYPES` in `prototype_registry.py` by decoration instead of a table literal.
    Write a `@prototype(name)` decorator for a function that builds and returns the `Monster`,
    so that the decorator stores each decorated function's result under `name`.
    Explain why the decorator takes the name as an argument rather than reading the function's `__name__`.
    Write that version and read what `ty` reports.
    Then say what the decorated form gains over the table and what it costs.
