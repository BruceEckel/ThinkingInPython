# Factory: Solutions

## 1 & 2. A `Triangle` in both factory styles

`shape_factory1.py`'s single static `factory()` needs one new `case`:

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
                return Circle()
            case "Square":
                return Square()
            case "Triangle":
                return Triangle()
            case _:
                raise ValueError(
                    f"Bad shape creation: {kind}")

class Circle(Shape):
    @override
    def draw(self) -> None:
        print("Circle.draw")

    @override
    def erase(self) -> None:
        print("Circle.erase")

class Square(Shape):
    @override
    def draw(self) -> None:
        print("Square.draw")

    @override
    def erase(self) -> None:
        print("Square.erase")

class Triangle(Shape):
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

`shape_factory2.py`'s factory-object version instead needs a `Triangle`
that carries its own nested `Factory`, plus one `FACTORIES` entry
mapping the name to an instance of that `Factory`. The listing below
shows the new shape alone; in the chapter file its entry joins
`Circle`'s and `Square`'s:

```python
# exercise_2.py
from abc import ABC, abstractmethod
from typing import Final, Protocol, override

class ShapeMaker(Protocol):
    def create(self) -> Shape: ...

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...

class Triangle(Shape):
    @override
    def draw(self) -> None:
        print("Triangle.draw")

    class Factory:
        def create(self) -> Triangle:
            return Triangle()

FACTORIES: Final[dict[str, ShapeMaker]] = {
    "Triangle": Triangle.Factory(),
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
from typing import override

class Obstacle:
    def description(self) -> str:
        raise NotImplementedError

class Character:
    def interact_with(self, obstacle: Obstacle) -> None: ...

class GameElementFactory:
    def make_character(self) -> Character:
        raise NotImplementedError

    def make_obstacle(self) -> Obstacle:
        raise NotImplementedError

class GameEnvironment:
    def __init__(self, factory: GameElementFactory) -> None:
        self.factory = factory
        self.p = factory.make_character()
        self.ob = factory.make_obstacle()

    def play(self) -> None:
        self.p.interact_with(self.ob)

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

`games2.py` asks for the same factory without a base class. Leaving
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

The two halves fail differently. In `games.py` the base class is
declared, so an unimplemented `make_obstacle()` inherits the base's
`raise NotImplementedError` and fails when the game runs. In
`games2.py` nothing is declared, so the mismatch surfaces at the call
that needs the protocol, before anything runs, and the diagnostic
names the missing method rather than the missing base.

## 4. An Abstract Factory for "thick" and "thin" shapes

```python
# exercise_4.py
from abc import ABC, abstractmethod
from typing import override

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...

class Circle(Shape):
    def __init__(self, thickness: str) -> None:
        self.thickness = thickness

    @override
    def draw(self) -> None:
        print(f"{self.thickness} Circle.draw")

class Square(Shape):
    def __init__(self, thickness: str) -> None:
        self.thickness = thickness

    @override
    def draw(self) -> None:
        print(f"{self.thickness} Square.draw")

class ShapeAbstractFactory:
    def make_circle(self) -> Shape:
        raise NotImplementedError

    def make_square(self) -> Shape:
        raise NotImplementedError

class ThickShapeFactory(ShapeAbstractFactory):
    @override
    def make_circle(self) -> Shape:
        return Circle("thick")

    @override
    def make_square(self) -> Shape:
        return Square("thick")

class ThinShapeFactory(ShapeAbstractFactory):
    @override
    def make_circle(self) -> Shape:
        return Circle("thin")

    @override
    def make_square(self) -> Shape:
        return Square("thin")

def build_shapes(
    factory: ShapeAbstractFactory
) -> list[Shape]:
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

`ShapeAbstractFactory` has the same shape as `games.py`'s
`GameElementFactory`, applied to shapes instead of game elements: one
abstract factory with a method per product (`make_circle()`,
`make_square()`), and concrete factories that each produce a consistent
*family* of products, here "all thick" or "all thin."
`build_shapes()` works with any `ShapeAbstractFactory`, so switching a
whole family of shapes from thick to thin is choosing a different
factory object, not editing every call site that creates a shape.

## 5. A four-topping limit, in both pizza styles

```python
# exercise_5.py
from dataclasses import dataclass
from typing import Self

@dataclass(frozen=True)
class Pizza:
    size: int = 9
    cheese: bool = True
    toppings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if len(self.toppings) > 4:
            raise ValueError(
                "a pizza may carry at most four toppings")

try:
    Pizza(toppings=("a", "b", "c", "d", "e"))
except ValueError as e:
    print("direct rejected:", e)
#: direct rejected: a pizza may carry at most four toppings

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
try:
    pb.topping("e")
except ValueError as e:
    print("builder rejected:", e)
#: builder rejected: a pizza may carry at most four toppings
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

def make(kind: str) -> Shape:
    return Shape.registry[kind]()
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

print(registry.Shape.registry)
#: {}
try:
    registry.make("Circle")
except KeyError as e:
    print("KeyError:", e)
#: KeyError: 'Circle'

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

The split between those two assertions is the whole lesson. A shallow
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

class Shape:
    def draw(self) -> None: ...

class ShapeMaker(Protocol):
    def create(self) -> Shape: ...

class Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")
    class Factory:
        def create(self) -> Circle: return Circle()

class EvalFactory:
    factories: ClassVar[dict[str, ShapeMaker]] = {}

    @classmethod
    def create_shape(cls, kind: str) -> Shape:
        if kind not in cls.factories:
            cls.factories[kind] = eval(f"{kind}.Factory()")
        return cls.factories[kind].create()

# A shape "name" that is really an expression:
ATTACK: Final[str] = "print('side effect!') or Circle"
EvalFactory.create_shape(ATTACK).draw()
#: side effect!
#: Circle.draw

class TableFactory:
    factories: ClassVar[dict[str, ShapeMaker]] = {
        "Circle": Circle.Factory(),
    }

    @classmethod
    def create_shape(cls, kind: str) -> Shape:
        return cls.factories[kind].create()

TableFactory.create_shape("Circle").draw()
#: Circle.draw
try:
    TableFactory.create_shape(ATTACK)
except KeyError as e:
    print(type(e).__name__, e)
#: KeyError "print('side effect!') or Circle"
```

`create_shape()` builds the string `print('side effect!') or
Circle.Factory()` and hands it to `eval()`. Python evaluates the
`print()` call first, which is the injected side effect. `None or
Circle.Factory()` then produces a perfectly good factory, so
`create_shape()` returns a working `Circle` and the caller sees no
error at all. That string can reach anything in the module's
namespace, and anything `__import__()` can reach.

`TableFactory` keys a dictionary on the same names. Looking up a `kind`
that is not a key raises a `KeyError` naming the string, and nothing
evaluates that string. `TableFactory.create_shape()` is also shorter,
needs no `Factory` lookup by name, and lets a type checker see that
every value is a `ShapeMaker`. Whenever `kind` can come from a
configuration file, a request, or a command line, `TableFactory` is the
only acceptable version of the two.
