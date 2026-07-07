# Factory: Solutions

## 1 & 2. A `Triangle` in both factory styles

`shape_factory1.py`'s single static `factory()` needs one new `case`:

```python
# exercise_1.py
from __future__ import annotations

class Shape:
    def draw(self) -> None: ...
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
                raise ValueError(f"Bad shape creation: {kind}")

class Circle(Shape):
    def draw(self) -> None:
        print("Circle.draw")

    def erase(self) -> None:
        print("Circle.erase")

class Square(Shape):
    def draw(self) -> None:
        print("Square.draw")

    def erase(self) -> None:
        print("Square.erase")

class Triangle(Shape):
    def draw(self) -> None:
        print("Triangle.draw")

    def erase(self) -> None:
        print("Triangle.erase")

s = Shape.factory("Triangle")
s.draw()
#: Triangle.draw
s.erase()
#: Triangle.erase
```

`shape_factory2.py`'s polymorphic version instead needs a `Triangle`
that carries its own nested `Factory`, since `ShapeFactory` never
names concrete shapes itself, it only `eval()`s whatever name it is
given and expects that name's own `Factory` class to build it:

```python
# exercise_2.py
from __future__ import annotations
from typing import Any, ClassVar

class ShapeFactory:
    factories: ClassVar[dict[str, Any]] = {}

    @classmethod
    def create_shape(cls, kind: str) -> Shape:
        if kind not in cls.factories:
            cls.factories[kind] = eval(kind + ".Factory()")
        return cls.factories[kind].create()

class Shape:
    def draw(self) -> None: ...

class Triangle(Shape):
    def draw(self) -> None:
        print("Triangle.draw")

    class Factory:
        def create(self) -> Triangle:
            return Triangle()

ShapeFactory.create_shape("Triangle").draw()
#: Triangle.draw
```

The first version required touching one function
(`Shape.factory()`). The second required touching nothing outside the
new class itself, which is the trade-off the chapter draws between
them: more ceremony up front (a nested `Factory` per shape) in
exchange for a central dispatcher that never needs to change again.

## 3. `GnomesAndFairies`

```python
# exercise_3.py
class Obstacle:
    def action(self) -> str:
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
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Gnome discovers a", obstacle.action())

class Riddle(Obstacle):
    def action(self) -> str:
        return "Riddle"

class GnomesAndFairies(GameElementFactory):
    def make_character(self) -> Character:
        return Gnome()

    def make_obstacle(self) -> Obstacle:
        return Riddle()

GameEnvironment(GnomesAndFairies()).play()
#: Gnome discovers a Riddle
```

`GameEnvironment` never names `Kitty`, `Warrior`, `Puzzle`, or
`NastyWeapon` directly; it only calls `make_character()` and
`make_obstacle()` on whatever `GameElementFactory` it was handed. A
third concrete factory slots in beside `KittiesAndPuzzles` and
`WarriorsAndWeapons` with no change to `GameEnvironment` at all.

## 4. An Abstract Factory for "thick" and "thin" shapes

```python
# exercise_4.py
class Shape:
    def draw(self) -> None: ...

class Circle(Shape):
    def __init__(self, thickness: str) -> None:
        self.thickness = thickness

    def draw(self) -> None:
        print(f"{self.thickness} Circle.draw")

class Square(Shape):
    def __init__(self, thickness: str) -> None:
        self.thickness = thickness

    def draw(self) -> None:
        print(f"{self.thickness} Square.draw")

class ShapeAbstractFactory:
    def make_circle(self) -> Shape:
        raise NotImplementedError

    def make_square(self) -> Shape:
        raise NotImplementedError

class ThickShapeFactory(ShapeAbstractFactory):
    def make_circle(self) -> Shape:
        return Circle("thick")

    def make_square(self) -> Shape:
        return Square("thick")

class ThinShapeFactory(ShapeAbstractFactory):
    def make_circle(self) -> Shape:
        return Circle("thin")

    def make_square(self) -> Shape:
        return Square("thin")

def build_shapes(factory: ShapeAbstractFactory) -> list[Shape]:
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

This is the same shape as `games.py`'s `GameElementFactory`, applied
to shapes instead of game elements: one abstract factory with a method
per product (`make_circle()`, `make_square()`), and concrete factories
that each produce a consistent *family* of products, here "all thick"
or "all thin." `build_shapes()` works with any `ShapeAbstractFactory`,
so switching a whole family of shapes from thick to thin is choosing a
different factory object, not editing every call site that creates a
shape.

## 5. A four-topping limit, in both pizza styles

```python
# exercise_5.py
from dataclasses import dataclass
from typing import Self

@dataclass(frozen=True)
class Pizza:
    size: int = 12
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
        self._size = 12
        self._toppings: list[str] = []

    def topping(self, name: str) -> Self:
        if len(self._toppings) >= 4:
            raise ValueError(
                "a pizza may carry at most four toppings")
        self._toppings.append(name)
        return self

    def build(self) -> Pizza:
        return Pizza(self._size, True, tuple(self._toppings))

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
#: Pizza(size=12, cheese=True, toppings=('a', 'b', 'c', 'd'))
```

In `pizza_direct.py`, an invalid `Pizza` can never exist, not even
momentarily. `__post_init__()` runs immediately after all fields are
assigned and raises before the constructor call returns, so the
five-topping combination is rejected atomically, before any code
anywhere could hold a reference to a `Pizza` carrying it. This is
[A Type Is a Set of Values](12_Data_Classes_as_Types.md#a-type-is-a-set-of-values)
again: illegal values are unrepresentable.

Placing the check in `topping()`, as above, gives `PizzaBuilder` the
same guarantee: the fifth `.topping()` call raises before appending,
so `self._toppings` itself never grows past four. Placing the check
in `build()` instead would change this. The builder would then accept
a fifth, sixth, or tenth `.topping()` call without complaint, silently
accumulating an already-too-long list, and only discover the problem
when `build()` finally runs. During that window, between the fifth
`.topping()` call and the eventual `build()` call, the builder's own
internal state (though never a `Pizza` object) already violates the
rule the finished `Pizza` is supposed to guarantee. Checking in
`topping()` closes that window entirely; checking only in `build()`
leaves it open for as long as the caller keeps adding toppings.
