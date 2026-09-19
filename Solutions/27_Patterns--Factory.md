# Factory: Solutions

## 1 & 2. A `Triangle` in both factory styles

`shape_factory_method.py`'s single static `factory()` needs one new `case`:

```python
# exercise_1.py
from abc import ABC, abstractmethod
from typing import override

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...

    @abstractmethod
    def erase(self) -> None: ...

    @staticmethod
    def factory(kind: str) -> Shape:
        match kind:
            case "Circle":
                return _Circle()
            case "Square":
                return _Square()
            case "Triangle":
                return _Triangle()
            case _:
                raise ValueError(
                    f"Bad shape creation: {kind}")

class _Circle(Shape):
    @override
    def draw(self) -> None:
        print("Circle.draw")

    @override
    def erase(self) -> None:
        print("Circle.erase")

class _Square(Shape):
    @override
    def draw(self) -> None:
        print("Square.draw")

    @override
    def erase(self) -> None:
        print("Square.erase")

class _Triangle(Shape):
    @override
    def draw(self) -> None:
        print("Triangle.draw")

    @override
    def erase(self) -> None:
        print("Triangle.erase")

s = Shape.factory("Triangle")
s.draw()
#: Triangle.draw
s.erase()
#: Triangle.erase
```

`shape_factory_objects.py`'s factory-object version instead needs a `Triangle`
that carries its own nested `Factory`, plus one `FACTORIES` entry
mapping the name to an instance of that `Factory`. The listing below
shows the new shape alone; in the chapter file its entry joins
`_Circle`'s and `_Square`'s:

```python
# exercise_2.py
from abc import ABC, abstractmethod
from typing import Final, Protocol, override

class ShapeMaker(Protocol):
    def create(self) -> Shape: ...

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...

class _Triangle(Shape):
    @override
    def draw(self) -> None:
        print("Triangle.draw")

    class Factory:
        def create(self) -> _Triangle:
            return _Triangle()

FACTORIES: Final[dict[str, ShapeMaker]] = {
    "Triangle": _Triangle.Factory(),
}

def create_shape(kind: str) -> Shape:
    return FACTORIES[kind].create()

create_shape("Triangle").draw()
#: Triangle.draw
```

Both versions add the `Triangle` class itself. Beyond that, the first
edits one function, `Shape.factory()`, where the new `case` sits inside
logic you must re-read. The second adds a nested `Factory` to
`Triangle` and one data line to `FACTORIES`. That is the trade-off the
chapter draws between the two versions: more ceremony up front (a
nested `Factory` per shape) in exchange for a dispatcher that changes
by table entry rather than by code. The chapter's `registry.py` goes
one step further: each class registers itself, so even the table entry
disappears.

## 3. `GnomesAndFairies`

```python
# exercise_3.py
from abc import ABC, abstractmethod
from typing import override

class Obstacle(ABC):
    @abstractmethod
    def description(self) -> str: ...

class Character(ABC):
    @abstractmethod
    def interact_with(self, obstacle: Obstacle) -> None: ...

class GameElementFactory(ABC):
    @abstractmethod
    def make_character(self) -> Character: ...

    @abstractmethod
    def make_obstacle(self) -> Obstacle: ...

class GameEnvironment:
    def __init__(self, factory: GameElementFactory) -> None:
        self.character = factory.make_character()
        self.obstacle = factory.make_obstacle()

    def play(self) -> None:
        self.character.interact_with(self.obstacle)

class Gnome(Character):
    @override
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Gnome discovers a", obstacle.description())

class Riddle(Obstacle):
    @override
    def description(self) -> str:
        return "Riddle"

class GnomesAndFairies(GameElementFactory):
    @override
    def make_character(self) -> Character:
        return Gnome()

    @override
    def make_obstacle(self) -> Obstacle:
        return Riddle()

GameEnvironment(GnomesAndFairies()).play()
#: Gnome discovers a Riddle
```

`GameEnvironment` never names `Kitty`, `Warrior`, `Puzzle`, or
`Weapon` directly. It only calls `make_character()` and
`make_obstacle()` on whatever `GameElementFactory` it receives. A
third concrete factory slots in beside `KittiesAndPuzzles` and
`WarriorsAndWeapons` with no change to `GameEnvironment` at all.

`abstract_factory_protocol.py` asks for the same factory without a base class. Leaving
`make_obstacle()` out at first is the point of the second half:

```python
# exercise_3_protocol.py
from typing import Protocol

class Obstacle(Protocol):
    def description(self) -> str: ...

class Character(Protocol):
    def interact_with(self, obstacle: Obstacle) -> None: ...

class GameElementFactory(Protocol):
    def make_character(self) -> Character: ...
    def make_obstacle(self) -> Obstacle: ...

class Gnome:
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Gnome discovers a", obstacle.description())

class Riddle:
    def description(self) -> str: return "Riddle"

class GnomesAndFairies:  # Declares no base class
    def make_character(self) -> Gnome: return Gnome()
    def make_obstacle(self) -> Riddle: return Riddle()

def play(factory: GameElementFactory) -> None:
    factory.make_character().interact_with(
        factory.make_obstacle())

play(GnomesAndFairies())
#: Gnome discovers a Riddle
```

With `make_obstacle()` deleted, `ty` reports:

```text
error[invalid-argument-type]: Argument to function `play` is incorrect
  --> exercise_3_protocol.py:28:6
   |
28 | play(GnomesAndFairies())
   |      ^^^^^^^^^^^^^^^^^^ Expected `GameElementFactory`,
   |                         found `GnomesAndFairies`
info: type `GnomesAndFairies` is not assignable to protocol
`GameElementFactory`
info: └── protocol member `make_obstacle` is not defined on type
`GnomesAndFairies`
```

The two halves fail differently. In `abstract_factory_abc.py` the base
class declares `make_obstacle()` as an `@abstractmethod`, so a factory
that omits it defines without complaint and raises a `TypeError` the
moment you instantiate it, before the game runs. In
`abstract_factory_protocol.py` nothing is declared, so the mismatch
surfaces at the call that needs the protocol, before anything runs at
all, and the diagnostic names the missing method rather than the
missing base.

## 4. An Abstract Factory for "thick" and "thin" shapes

```python
# exercise_4.py
from abc import ABC, abstractmethod
from typing import Literal, Protocol, override

type Thickness = Literal["thick", "thin"]

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...

class Circle(Shape):
    def __init__(self, thickness: Thickness) -> None:
        self.thickness = thickness

    @override
    def draw(self) -> None:
        print(f"{self.thickness} Circle.draw")

class Square(Shape):
    def __init__(self, thickness: Thickness) -> None:
        self.thickness = thickness

    @override
    def draw(self) -> None:
        print(f"{self.thickness} Square.draw")

class ShapeFactory(Protocol):
    def make_circle(self) -> Shape: ...
    def make_square(self) -> Shape: ...

class ThickShapeFactory:
    def make_circle(self) -> Shape:
        return Circle("thick")

    def make_square(self) -> Shape:
        return Square("thick")

class ThinShapeFactory:
    def make_circle(self) -> Shape:
        return Circle("thin")

    def make_square(self) -> Shape:
        return Square("thin")

def build_shapes(factory: ShapeFactory) -> list[Shape]:
    return [factory.make_circle(), factory.make_square()]

for shape in build_shapes(ThickShapeFactory()):
    shape.draw()
#: thick Circle.draw
#: thick Square.draw
for shape in build_shapes(ThinShapeFactory()):
    shape.draw()
#: thin Circle.draw
#: thin Square.draw
```

`ShapeFactory` is `abstract_factory_protocol.py`'s form applied to
shapes instead of game elements: a `Protocol` with a method per
product (`make_circle()`, `make_square()`), and concrete factories
that each produce a consistent *family* of products, here "all
thick" or "all thin," without inheriting anything. `build_shapes()`
accepts any object with those two methods, so switching a whole
family of shapes from thick to thin is choosing a different factory
object, not editing every call site that creates a shape.

## 5. A four-topping limit, in both pizza styles

```python
# exercise_5.py
from typing import Self
from exceptions import expect
from record import record

@record
class Pizza:
    size: int = 9
    cheese: bool = True
    toppings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if len(self.toppings) > 4:
            raise ValueError(
                "a pizza may carry at most four toppings")

expect(ValueError, Pizza,
       toppings=("a", "b", "c", "d", "e"))
#: [ValueError] a pizza may carry at most four toppings

class PizzaBuilder:
    def __init__(self) -> None:
        self._size = 9
        self._toppings: list[str] = []

    def topping(self, name: str) -> Self:
        if len(self._toppings) >= 4:
            raise ValueError(
                "a pizza may carry at most four toppings")
        self._toppings.append(name)
        return self

    def build(self) -> Pizza:
        return Pizza(self._size, True,
                     tuple(self._toppings))

pb = (
    PizzaBuilder().topping("a").topping("b")
    .topping("c").topping("d")
)
expect(ValueError, pb.topping, "e")
#: [ValueError] a pizza may carry at most four toppings
print(pb.build())
#: Pizza(size=9, cheese=True, toppings=('a', 'b', 'c', 'd'))
```

In `pizza_direct.py`, an invalid `Pizza` can never exist, not even
momentarily. `__post_init__()` runs immediately after the constructor
assigns every field, and raises a `ValueError` before that constructor
call returns. The rejection is therefore atomic: no code anywhere can
hold a reference to a `Pizza` carrying five toppings. That guarantee is
[A Type Is a Set of Values](../Chapters/12_Techniques--Data_Classes_as_Types.md#a-type-is-a-set-of-values)
again: illegal values are unrepresentable.

Placing the check in `topping()`, as above, gives `PizzaBuilder` the
same guarantee: the fifth `.topping()` call raises a `ValueError`
before appending, so `self._toppings` itself never grows past four.
Placing the check in `build()` instead gives up that guarantee. The
builder then accepts a fifth, sixth, or tenth `.topping()` call without
complaint, silently accumulating an already-too-long list, and
discovers the problem only when `build()` finally runs, leaving a
window between the fifth `.topping()` call and that `build()` call.
During that window the builder's own internal state violates the rule
the finished `Pizza` must guarantee, though no `Pizza` object ever
violates it. Checking in `topping()` closes that window entirely.
Checking only in `build()` leaves it open for as long as the caller
keeps adding toppings.

## 6. A registry whose classes live somewhere else

```python
# registry.py
from abc import ABC, abstractmethod
from typing import ClassVar

class Shape(ABC):
    registry: ClassVar[dict[str, type[Shape]]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Shape.registry[cls.__name__] = cls

    @abstractmethod
    def draw(self) -> None: ...

def make(name: str) -> Shape:
    return Shape.registry[name]()
```

```python
# extra_shapes.py
from typing import override
from registry import Shape

class Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")

class Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")
```

```python
# exercise_6.py
import registry
from exceptions import expect

print(registry.Shape.registry)
#: {}
expect(KeyError, registry.make, "Circle")
#: [KeyError] 'Circle'

import extra_shapes  # noqa: E402  (the import is the point)

print(sorted(registry.Shape.registry))
#: ['Circle', 'Square']
registry.make("Circle").draw()
#: Circle.draw
print(extra_shapes.Circle.__name__)
#: Circle
```

`Shape.__init_subclass__()` registers `Circle` as the
`class Circle(Shape):` line in `extra_shapes.py` executes, and that
line executes the first time something imports `extra_shapes`.
Nothing else triggers the registration. `registry` knows nothing
about `extra_shapes` and never imports it, so until some other module
does, `Shape.registry` is empty and every `make()` call raises a
`KeyError`.

That is the plugin failure the chapter describes, reproduced in
miniature. The registry is correct, the subclass is correct, and the
program still fails, because registration is a side effect of import
and nobody imported the module. Real systems solve that failure by
importing the plugin package explicitly at startup, by walking a
directory with `importlib`, or by declaring entry points that the
packaging system imports for them.

`registry_demo.py` is the same program in miniature. It imports
`Shape` and `make` from `registry`, which no longer defines a single
subclass, so without a change it prints `[]` and the first `make()`
call raises a `KeyError`. One added import restores the output:

```python
# registry_demo.py
import extra_shapes  # noqa: F401
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

The demo never uses the name `extra_shapes`, so ruff reports the
import as unused and the `noqa` comment is the only sign that it is
deliberate. That is the shape the chapter warns about: an import that
exists for its side effect. It must stay an ordinary import, since a
`lazy import` would defer the module body, and with it the two
`class` statements, until the first use of a name the demo never
uses.

## 7. What `copy.copy()` costs a prototype registry

```python
# exercise_7.py
import copy
from dataclasses import dataclass, field
from typing import Final

@dataclass
class Monster:
    name: str
    hp: int
    powers: list[str] = field(default_factory=list)
    parts: dict[str, int] = field(default_factory=dict)

PROTOTYPES: Final[dict[str, Monster]] = {
    "goblin": Monster("Goblin", hp=10, powers=["bite"],
                      parts={"arms": 2}),
    "hydra": Monster("Hydra", hp=60, powers=["bite"],
                     parts={"heads": 9}),
}

def shallow_spawn(kind: str) -> Monster:
    return copy.copy(PROTOTYPES[kind])  # The bug

a = shallow_spawn("hydra")
a.parts["heads"] = 1  # Cut off eight heads
print(PROTOTYPES["hydra"].parts)  # The prototype changed
#: {'heads': 1}
# So does every later spawn
print(shallow_spawn("hydra").parts)
#: {'heads': 1}
```

With `copy.copy()`, `test_clone_is_independent()` fails first.
`b.powers.append("curse")` appends to the one list both spawns share,
so `a.powers` becomes `["bite", "curse"]` and the assertion that it
equals `["bite"]` fails. `test_prototype_untouched()` fails too, but
only on its second assertion: `spawned.powers.append("bellow")`
mutates the shared list, so `PROTOTYPES["troll"].powers` grows a third
entry. Its first assertion still holds, because `spawned.hp = 1`
rebinds an `int` field on the copy rather than mutating a shared
object.

The split between those two assertions carries the lesson. A shallow
copy duplicates the top object and shares everything it refers to, so
the fields that break are exactly the mutable ones, and only when
something mutates them in place. Assignment to a field is always safe.
`append()`, `[k] = v`, and `.update()` are not.

A test through `parts` would have caught it either way:

```python
# test_prototype_parts.py
import copy
from dataclasses import dataclass, field
from typing import Final

@dataclass
class Monster:
    name: str
    hp: int
    parts: dict[str, int] = field(default_factory=dict)

PROTOTYPES: Final[dict[str, Monster]] = {
    "hydra": Monster("Hydra", hp=60, parts={"heads": 9}),
}

def spawn(kind: str) -> Monster:
    return copy.deepcopy(PROTOTYPES[kind])

def test_nested_dict_is_copied() -> None:
    spawned = spawn("hydra")
    spawned.parts["heads"] = 1
    assert PROTOTYPES["hydra"].parts == {"heads": 9}
    assert spawn("hydra").parts == {"heads": 9}
```

The second assertion is the one worth writing. Checking that the
prototype survived is good. Checking that the *next* spawn is still
correct is what a user of the registry actually depends on, and that
assertion fails loudly under `copy.copy()`.

## 8. What the `eval()` dispatcher accepts

```python
# exercise_8.py
from typing import ClassVar, Final, Protocol, override
from exceptions import expect

class Shape:
    def draw(self) -> None: ...

class ShapeMaker(Protocol):
    def create(self) -> Shape: ...

class _Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")
    class Factory:
        def create(self) -> _Circle: return _Circle()

class EvalFactory:
    factories: ClassVar[dict[str, ShapeMaker]] = {}

    @classmethod
    def create_shape(cls, kind: str) -> Shape:
        if kind not in cls.factories:
            cls.factories[kind] = eval(f"_{kind}.Factory()")
        return cls.factories[kind].create()

# A shape "name" that is really an expression:
ATTACK: Final[str] = (
    "Circle.Factory() if print('side effect!')"
    " else _Circle")
EvalFactory.create_shape(ATTACK).draw()
#: side effect!
#: Circle.draw

class TableFactory:
    factories: ClassVar[dict[str, ShapeMaker]] = {
        "Circle": _Circle.Factory(),
    }

    @classmethod
    def create_shape(cls, kind: str) -> Shape:
        return cls.factories[kind].create()

TableFactory.create_shape("Circle").draw()
#: Circle.draw
expect(KeyError, TableFactory.create_shape, ATTACK)
#: [KeyError] "Circle.Factory() if print('side effect!')
#: else _Circle"
```

`create_shape()` prepends the underscore and appends `.Factory()`, so
the string it hands to `eval()` is `_Circle.Factory() if
print('side effect!') else _Circle.Factory()`. Python evaluates the
condition first, which is the injected side effect. `print()` returns
`None`, so the `else` branch runs and produces a perfectly good
factory, and `create_shape()` returns a working `_Circle` while the
caller sees no error at all. That string can reach anything in the module's
namespace, and anything `__import__()` can reach.

`TableFactory` keys a dictionary on the same names. Looking up a `kind`
that is not a key raises a `KeyError` naming the string, and nothing
evaluates that string. `TableFactory.create_shape()` is also shorter,
needs no `Factory` lookup by name, and lets a type checker see that
every value is a `ShapeMaker`. Whenever `kind` can come from a
configuration file, a request, or a command line, `TableFactory` is the
only acceptable version of the two.

## 9. Recursing through `__subclasses__()`

```python
# exercise_9.py
import random
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import override

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...
    @abstractmethod
    def erase(self) -> None: ...
    @staticmethod
    def factory(kind: str) -> Shape:
        match kind:
            case "Circle":
                return _Circle()
            case "Square":
                return _Square()
            case "Oval":
                return _Oval()
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

class _Oval(_Circle):
    @override
    def draw(self) -> None: print("Oval.draw")

def all_subclasses[T](cls: type[T]) -> Iterator[type[T]]:
    for sub in cls.__subclasses__():
        yield sub
        yield from all_subclasses(sub)

def names(classes: Iterable[type[Shape]]) -> list[str]:
    return [c.__name__.removeprefix("_") for c in classes]

print(names(Shape.__subclasses__()))
#: ['Circle', 'Square']
print(names(all_subclasses(Shape)))
#: ['Circle', 'Oval', 'Square']

def shape_name(n: int) -> Iterator[str]:
    for _ in range(n):
        cls = random.choice(list(all_subclasses(Shape)))
        yield cls.__name__.removeprefix("_")

random.seed(4)
for shape in [Shape.factory(s) for s in shape_name(6)]:
    shape.draw()
#: Circle.draw
#: Oval.draw
#: Circle.draw
#: Square.draw
#: Oval.draw
#: Oval.draw
```

`_Oval` is a subclass of `_Circle`, not of `Shape`, so
`Shape.__subclasses__()` lists `_Circle` and `_Square` and stops. The
original `shape_name()` draws only from that list, so no seed
produces `"Oval"`, and the new `case` in `factory()` is unreachable
from the demo even though it works when called directly.

`all_subclasses()` yields each direct subclass and then, before moving
to the next one, recurses into that subclass: depth first, so `Oval`
comes out between `Circle` and `Square`. The generic `T` keeps the
result typed as `type[Shape]` when the argument is `Shape`, which is
what `names()` and `factory()` need. `random.choice()` takes a
sequence, so `shape_name()` materializes the generator with `list()`.
With the same seed the sequence differs from the chapter's, because
`choice()` now picks from three classes instead of two.

`_Oval` overrides only `draw()`, so an `Oval` still erases as a
`Circle`. That is also why `Circle` stays in the list: recursion adds
the deeper classes without removing the intermediate ones, and a
factory that should build only leaf classes needs a further filter,
`not cls.__subclasses__()`.

## 10. Finding the class that forgot `@register`

```python
# exercise_10.py
from typing import Final, Protocol, runtime_checkable
from exceptions import expect

@runtime_checkable
class Shape(Protocol):
    def draw(self) -> None: ...

REGISTRY: Final[dict[str, type[Shape]]] = {}

def register[S: Shape](cls: type[S]) -> type[S]:
    REGISTRY[cls.__name__] = cls
    return cls

@register
class Circle:
    def draw(self) -> None: print("Circle.draw")

@register
class Square:
    def draw(self) -> None: print("Square.draw")

class Hexagon:
    def draw(self) -> None: print("Hexagon.draw")

def make(name: str) -> Shape:
    return REGISTRY[name]()

def unregistered(namespace: dict[str, object]) -> list[str]:
    return sorted(
        name
        for name, obj in namespace.items()
        if isinstance(obj, type)
        and obj is not Shape
        and issubclass(obj, Shape)
        and obj not in REGISTRY.values()
    )

Hexagon().draw()
#: Hexagon.draw
expect(KeyError, make, "Hexagon")
#: [KeyError] 'Hexagon'
print(unregistered(globals()))
#: ['Hexagon']
```

`Hexagon` is a complete `Shape`: `ty` accepts it wherever a `Shape`
is expected, and `Hexagon().draw()` works. `make("Hexagon")` fails
with a `KeyError`, because the table never heard of it, and the
error names the key rather than the class or the missing line. No
checker reports the omission, since a class that nothing decorates
is an ordinary class.

`unregistered()` walks a namespace and keeps every class that
`issubclass()` accepts as a `Shape` and that `REGISTRY` lacks.
`@runtime_checkable` is what allows the `issubclass()` call; without
it, testing a class against a Protocol raises a `TypeError`. The
`obj is not Shape` guard drops the Protocol, which passes its own
test. Calling `unregistered(globals())` at the end of the module, or
from a test, turns a silent absence into a printed name.

The runtime test is weaker than the checker's. `issubclass()` looks
for an attribute named `draw` and nothing about its signature, so a
class whose `draw()` takes an extra parameter passes here and fails
at `@register`. The two checks cover each other: the checker
rejects a decorated class that does not fit, and `unregistered()`
reports a fitting class that is not decorated. `issubclass()`
against a Protocol also works only when every member is a method;
a Protocol with a data attribute raises a `TypeError` from
`issubclass()`, and `isinstance()` on an instance is the fallback.
The check also sees one namespace at a time, so a plugin module
must run it over its own `globals()`.

## 11. Prototypes registered by decoration

```python
# exercise_11.py
import copy
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Final

@dataclass
class Monster:
    name: str
    hp: int
    powers: list[str] = field(default_factory=list)

type Builder = Callable[[], Monster]

PROTOTYPES: Final[dict[str, Monster]] = {}

def prototype(name: str) -> Callable[[Builder], Builder]:
    def register(build: Builder) -> Builder:
        PROTOTYPES[name] = build()
        return build
    return register

@prototype("goblin")
def goblin() -> Monster:
    return Monster("Goblin", hp=10, powers=["bite"])

@prototype("troll")
def troll() -> Monster:
    return Monster("Troll", hp=40,
                   powers=["smash", "regen"])

def spawn(name: str) -> Monster:
    return copy.deepcopy(PROTOTYPES[name])

print(sorted(PROTOTYPES))
#: ['goblin', 'troll']
a = spawn("goblin")
b = spawn("goblin")
b.hp = 5
print(a.hp, b.hp)
#: 10 5
print(spawn("troll"))
#: Monster(name='Troll', hp=40, powers=['smash', 'regen'])
```

`prototype()` is a decorator factory, the shape [Decorators](../Chapters/14_Techniques--Decorators.md#decorators-that-take-arguments)
introduces: the outer call takes the name and returns `register()`,
which runs the builder once, stores the result, and hands the builder
back unchanged. The table is empty at its declaration and full by the
time `spawn()` runs, because each `@prototype` line executes as the
module loads, the same timing the chapter's `registry.py` relies on.

The name is an argument because the builder's own name is not
available to the type checker. `Builder` is a `Callable`, and a
`Callable` declares only how it is called, not that it carries a
`__name__`. Writing `PROTOTYPES[build.__name__] = build()` draws:

```text
error[unresolved-attribute]: Object of type `Builder` has no attribute `__name__`
```

The chapter's `register()` in `protocol_registry.py` has no such
problem because it receives a class, and `type[S]` has a `__name__`.
Pyright accepts `build.__name__`, since it gives every function
object's attributes to a `Callable`; `ty` does not, and the book
checks with `ty`. Passing the name also frees the key from the
function's spelling, so the builder can be called `make_goblin()`
while the key stays `"goblin"`.

What the decorated form gains is the same openness the registries
gain: a prototype can be defined in any module, with its name beside
its definition, and `PROTOTYPES` needs no edit. The key type widens
from the chapter's `Kind` to `str` for the same reason: an open table
cannot list its names in advance. The builder is also a
function, so `goblin()` still produces a fresh prototype on demand
when a test wants one that nothing has touched. The costs are the
table literal becoming a decorator plus a function for each monster,
the name repeated at every definition, and the two failures the
chapter attached to registration:
a builder nothing decorates is absent from the table,
with a `KeyError` from `spawn()` that points at nothing, and a
builder in a module nothing imports never runs. For two monsters in
one file, the table literal says the same thing in fewer lines.
