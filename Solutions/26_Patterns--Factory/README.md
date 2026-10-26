# Factory: Solutions

## 1 & 2. A `Triangle` in both factory styles

> 1.  Add a class `Triangle` to `shape_factory_method.py`.
>
> 2.  Add a class `Triangle` to `shape_factory_objects.py`.

<details>
<summary>Where to look</summary>

[Simple *Factory Method*](../../Chapters/26_Patterns--Factory.md#simple-factory-method)
and [Factory Objects](../../Chapters/26_Patterns--Factory.md#factory-objects)
each create the concrete classes at a single creation point,
and a caller asks that point for a shape by name.
A new shape needs a class that implements `Shape`'s abstract methods,
plus one entry where that creation point chooses by name.
In the first style that entry is a `case` in `Shape.factory()`.
In the second it is a nested `Factory` class,
registered by name in the `FACTORIES` table.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from abc import ABC, abstractmethod
from typing import override

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...

    @staticmethod
    def factory(kind: str) -> Shape:
        ...

class _Circle(Shape):
    @override
    def draw(self) -> None:
        ...

class _Square(Shape):
    @override
    def draw(self) -> None:
        ...

class _Triangle(Shape):
    @override
    def draw(self) -> None:
        ...
```

```python
# The shape of exercise_2.py
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
        ...

    class Factory:
        def create(self) -> _Triangle:
            ...

FACTORIES: Final[dict[str, ShapeMaker]] = {
    "Triangle": _Triangle.Factory(),
}

def create_shape(kind: str) -> Shape:
    ...
```

<details>
<summary>Done when</summary>

your edited `shape_factory_method.py` runs its seeded demo with no `ValueError`,
and with your class defined after the other two,
its fourth line reads `Triangle.draw`.
Your edited `shape_factory_objects.py` prints `Triangle.draw` for a `"Triangle"` in its demo list,
with no `KeyError`.

<details>
<summary>Solution</summary>

If you add the `_Triangle` class to `shape_factory_method.py` and stop there,
the type checker accepts the file,
but with the chapter's seed the demo stops with an exception.
`shape_name()` draws from `Shape.__subclasses__()`,
which lists `_Triangle` as soon as its `class` statement runs,
so the demo asks for a `"Triangle"`.
`Shape.factory()` cannot build one and raises `ValueError: Bad shape: Triangle`.
`shape_factory_objects.py` lists its shapes in a literal,
so its demo asks for `"Triangle"` once you add the name to that list.
Without a `FACTORIES` entry,
`create_shape()` then raises `KeyError: 'Triangle'`.
Each solution therefore adds the class and its entry together.

`shape_factory_method.py`'s single static `factory()` needs one new `case`:

```python
# exercise_1.py
from abc import ABC, abstractmethod
from typing import override

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...

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
                raise ValueError(f"Bad shape: {kind}")

class _Circle(Shape):
    @override
    def draw(self) -> None:
        print("Circle.draw")

class _Square(Shape):
    @override
    def draw(self) -> None:
        print("Square.draw")

class _Triangle(Shape):
    @override
    def draw(self) -> None:
        print("Triangle.draw")

s = Shape.factory("Triangle")
s.draw()
#: Triangle.draw
```

In `shape_factory_objects.py` the `FACTORIES` entry for `_Triangle` joins the entries for `_Circle` and `_Square`,
and `"Triangle"` joins the demo's list.
The listing below shows the new shape alone:

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

Both versions add the `_Triangle` class.
Beyond that, `shape_factory_method.py` edits one function, `Shape.factory()`,
where the new `case` sits inside logic you must re-read.
`shape_factory_objects.py` leaves its dispatcher, `create_shape()`, as it was,
and adds a nested `Factory` to `_Triangle` and one data line to `FACTORIES`.
Every shape in that version carries a nested `Factory` and an entry in the table.
The chapter's `registry.py` drops both the nested class and the entry.
Each class registers itself, so adding a shape means writing its class.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. `GnomesAndFairies`

> Add a new type of `GameElementFactory` called `GnomesAndFairies`,
> first to `abstract_factory_abc.py` and then to `abstract_factory_protocol.py`.
> In `abstract_factory_protocol.py`, leave out `make_obstacle()` at first,
> pass the factory to `GameEnvironment`,
> and confirm the error your type checker reports.
> Then add `make_obstacle()`.

<details>
<summary>Where to look</summary>

[Abstract Factories](../../Chapters/26_Patterns--Factory.md#abstract-factories)
shows `GameElementFactory` as a family of creation methods,
once as an abstract base class and once as a `Protocol`.
A new concrete factory implements both `make_character()` and `make_obstacle()`,
returning a new `Character` and a new `Obstacle` that belong together.
In the `Protocol` version the concrete factory declares no base class,
so constructing it succeeds at runtime.
The type checker reports the missing `make_obstacle()` at the line where you pass the factory to `GameEnvironment`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
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
        ...

    def play(self) -> None:
        ...

class Gnome(Character):
    @override
    def interact_with(self, obstacle: Obstacle) -> None:
        ...

class Fairy(Obstacle):
    @override
    def description(self) -> str:
        ...

class GnomesAndFairies(GameElementFactory):
    @override
    def make_character(self) -> Character:
        ...

    @override
    def make_obstacle(self) -> Obstacle:
        ...
```

```python
# The shape of exercise_3_protocol.py
from typing import Protocol

class Obstacle(Protocol):
    def description(self) -> str: ...

class Character(Protocol):
    def interact_with(self, obstacle: Obstacle) -> None: ...

class GameElementFactory(Protocol):
    def make_character(self) -> Character: ...
    def make_obstacle(self) -> Obstacle: ...

class GameEnvironment:
    def __init__(self, factory: GameElementFactory) -> None:
        ...
    def play(self) -> None:
        ...

class Gnome:
    def interact_with(self, obstacle: Obstacle) -> None:
        ...

class Fairy:
    def description(self) -> str: ...

class GnomesAndFairies:  # Declares no base class
    def make_character(self) -> Gnome: ...
    def make_obstacle(self) -> Fairy: ...
```

<details>
<summary>Done when</summary>

both versions play a game with your new factory through the unchanged `GameEnvironment`.
In the Protocol version without `make_obstacle()`,
`uv run ty check` reports `invalid-argument-type` at the `GameEnvironment(...)` call and names `make_obstacle` as the missing protocol member.

<details>
<summary>Solution</summary>

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

class Fairy(Obstacle):
    @override
    def description(self) -> str:
        return "Fairy"

class GnomesAndFairies(GameElementFactory):
    @override
    def make_character(self) -> Character:
        return Gnome()

    @override
    def make_obstacle(self) -> Obstacle:
        return Fairy()

GameEnvironment(GnomesAndFairies()).play()
#: Gnome discovers a Fairy
```

**Ask the factory for each product.**
`GameEnvironment` does not name `Kitty`, `Warrior`, `Puzzle`, or `Weapon`.
`GameEnvironment` stays as it was while a third concrete factory joins `KittiesAndPuzzles` and `WarriorsAndWeapons`.

In `abstract_factory_protocol.py` you leave `make_obstacle()` out at first,
then add it back:

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

class GameEnvironment:
    def __init__(self, factory: GameElementFactory) -> None:
        self.character = factory.make_character()
        self.obstacle = factory.make_obstacle()
    def play(self) -> None:
        self.character.interact_with(self.obstacle)

class Gnome:
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Gnome discovers a", obstacle.description())

class Fairy:
    def description(self) -> str: return "Fairy"

class GnomesAndFairies:  # Declares no base class
    def make_character(self) -> Gnome: return Gnome()
    def make_obstacle(self) -> Fairy: return Fairy()

GameEnvironment(GnomesAndFairies()).play()
#: Gnome discovers a Fairy
```

With `make_obstacle()` deleted, `ty` reports:

```text
error[invalid-argument-type]: Argument to
`GameEnvironment.__init__` is incorrect
  --> exercise_3_protocol.py:31:17
   |
31 | GameEnvironment(GnomesAndFairies()).play()
   |                 ^^^^^^^^^^^^^^^^^^ Expected
   |                 `GameElementFactory`, found
   |                 `GnomesAndFairies`
info: type `GnomesAndFairies` is not assignable to protocol
`GameElementFactory`
info: └── protocol member `make_obstacle` is not defined on type
`GnomesAndFairies`
```

The two halves fail at different places.
In `abstract_factory_abc.py` the base class declares `make_obstacle()` as an `@abstractmethod`.
Python checks abstract methods when you construct an instance,
so it accepts the definition of a factory that omits `make_obstacle()`.
The type checker reports the line that constructs that factory.
If you run the program without fixing it,
Python raises a `TypeError` at that construction, before the game runs.
In `abstract_factory_protocol.py` no class declares that it satisfies the protocol,
so constructing the factory is legal.
The type checker reports the call that needs the protocol.
At runtime that version fails later, inside the game.
`GameEnvironment.__init__()` raises an `AttributeError` when it calls `make_obstacle()`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. An Abstract Factory for "thick" and "thin" shapes

> Modify `shape_factory_objects.py` to use an *Abstract Factory* to create different sets of shapes
> (for example, one type of factory object creates "thick shapes," another creates "thin shapes," but each factory object can create all the shapes: circles, squares, triangles, etc.).

<details>
<summary>Where to look</summary>

[Abstract Factories](../../Chapters/26_Patterns--Factory.md#abstract-factories)
makes one factory object produce a matching family of products.
Here the family is the set of shapes, and the variation is the style.
Declare a `Protocol` with one creation method per shape,
write one factory class for thick shapes and one for thin,
and give each shape a thickness the factory supplies.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from abc import ABC, abstractmethod
from typing import Literal, Protocol, override
from record import record

type Thickness = Literal["thick", "thin"]

class Shape(ABC):
    __slots__ = ()

    @abstractmethod
    def draw(self) -> None: ...

@record
class Circle(Shape):
    thickness: Thickness

    @override
    def draw(self) -> None:
        ...

@record
class Square(Shape):
    thickness: Thickness

    @override
    def draw(self) -> None:
        ...

class ShapeFactory(Protocol):
    def make_circle(self) -> Shape: ...
    def make_square(self) -> Shape: ...

class ThickShapeFactory:
    def make_circle(self) -> Shape:
        ...

    def make_square(self) -> Shape:
        ...

class ThinShapeFactory:
    def make_circle(self) -> Shape:
        ...

    def make_square(self) -> Shape:
        ...

def build_shapes(factory: ShapeFactory) -> list[Shape]:
    ...
```

<details>
<summary>Done when</summary>

your demo draws each shape twice, first thick and then thin
(the solution prints `thick Circle.draw` and later `thin Circle.draw`).
The code that creates the shapes is the same for both families;
the factory object you pass is the one thing that differs.

<details>
<summary>Solution</summary>

```python
# exercise_4.py
from abc import ABC, abstractmethod
from typing import Literal, Protocol, override
from record import record

type Thickness = Literal["thick", "thin"]

class Shape(ABC):
    __slots__ = ()

    @abstractmethod
    def draw(self) -> None: ...

@record
class Circle(Shape):
    thickness: Thickness

    @override
    def draw(self) -> None:
        print(f"{self.thickness} Circle.draw")

@record
class Square(Shape):
    thickness: Thickness

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

**Build each family in one factory.**
`ShapeFactory` applies `abstract_factory_protocol.py`'s form to shapes instead of game elements:
a `Protocol` with one method per product, `make_circle()` and `make_square()`.
Each concrete factory produces a consistent family of products,
here "all thick" or "all thin," and matches the `Protocol` by its structure.

**Accept any factory.**
`build_shapes()` accepts any object with those two methods,
so you switch a whole family of shapes from thick to thin by passing a different factory object,
not by editing every call site that creates a shape.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 5. A four-topping limit, in both pizza styles

> Add a rule to both pizza examples: a pizza may carry at most four toppings.
> In `pizza_direct.py`, enforce it with `__post_init__()`,
> as [Data Classes as Types](../../Chapters/12_Techniques--Data_Classes_as_Types.md#a-type-is-a-set-of-values)
> does for `Stars`.
> In `pizza_builder.py`,
> decide whether it belongs in `topping()` or `build()`.
> In which version can an invalid pizza exist, even momentarily?
> `stars_class.py` in that chapter shows the same hazard.

<details>
<summary>Where to look</summary>

[*Builder*](../../Chapters/26_Patterns--Factory.md#builder)
separates assembling a pizza from the finished `Pizza`.
In `pizza_direct.py`,
`__post_init__()` runs while the constructor is still executing,
so the constructor raises an exception before it returns a bad pizza.
In `pizza_builder.py`, the check can sit in `topping()` or in `build()`.
For each placement, ask what the builder's list of toppings holds after a fifth `topping()` call.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from typing import Self
from exceptions import expect
from record import record

@record
class Pizza:
    size: int = 12
    cheese: bool = True
    toppings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        ...

class PizzaBuilder:
    def __init__(self) -> None:
        ...

    def topping(self, name: str) -> Self:
        ...

    def build(self) -> Pizza:
        ...
```

<details>
<summary>Done when</summary>

a `Pizza` with five toppings raises a `ValueError` from `__post_init__()`,
and your builder raises a `ValueError` for a five-topping pizza.
You can say, for a check in `topping()` and for one in `build()`,
what the builder's list holds right after a fifth `topping()` call.

<details>
<summary>Solution</summary>

If you put the check in `build()` and let `topping()` append freely,
the call `topping("e")` succeeds,
so the demo's `expect()` raises an `AssertionError` ("no exception raised").
The builder holds five toppings until `build()` raises `ValueError`.
The solution checks in `topping()`,
so the builder's list stops at four toppings.

```python
# exercise_5.py
from typing import Self
from exceptions import expect
from record import record

@record
class Pizza:
    size: int = 12
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
        self._size = 12
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
print(pb.build().toppings)
#: ('a', 'b', 'c', 'd')
```

**Reject the value during construction.**
In `pizza_direct.py`, every `Pizza` carries four toppings or fewer,
at every moment.
`__post_init__()` runs immediately after the constructor assigns every field,
and raises a `ValueError` before that constructor call returns.
The rejection is therefore atomic:
the constructor call ends in the exception before it hands any code a reference to a `Pizza` carrying five toppings.
That guarantee is [A Type Is a Set of Values](../../Chapters/12_Techniques--Data_Classes_as_Types.md#a-type-is-a-set-of-values)
again: illegal values are unrepresentable.

**Check before each change.**
Placing the check in `topping()`, as `exercise_5.py` does,
gives `PizzaBuilder` the same guarantee.
Placing the check in `build()` lets the builder accept a fifth, sixth,
or tenth `.topping()` call and silently accumulate an overlong list.
That builder checks the count when `build()` runs,
so a window opens between the fifth `.topping()` call and that `build()` call.
During that window the builder's internal state violates the rule the finished `Pizza` must guarantee,
while every `Pizza` object obeys it.

That window is the hazard `stars_class.py` shows.
A mutable object that checks its rule after the change keeps the illegal value when the check fails.
`damaged` still prints `Stars(13)` after `f1()` raises a `TypeFailure`.
A builder that checks in `build()` raises its `ValueError` and still holds five toppings.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. A registry whose classes live somewhere else

> Move `Circle` and `Square` out of `registry.py` into a new module,
> `extra_shapes.py`.
> Confirm that `make("Circle")` now raises `KeyError` until something imports `extra_shapes`,
> and explain which line of which file registers the class, and when it runs.
> Then make `registry_demo.py` print the same key list it printed before the move.

<details>
<summary>Where to look</summary>

[Self Registration](../../Chapters/26_Patterns--Factory.md#self-registration)
fills the registry from `__init_subclass__()`,
which runs when a `class` statement executes.
A class registers itself when its module runs,
so a module contributes its classes once something imports it.
To restore the old key list, make `registry_demo.py` import `extra_shapes`.
[Hazards of Self Registration](../../Chapters/26_Patterns--Factory.md#hazards-of-self-registration)
says to keep such an import eager, since it exists for its side effect.
A linter reports that import as unused, so decide what keeps the line in place.

<details>
<summary>The shape</summary>

```python
# The shape of registry.py
from abc import ABC, abstractmethod
from typing import ClassVar

class Shape(ABC):
    registry: ClassVar[dict[str, type[Shape]]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        ...

    @abstractmethod
    def draw(self) -> None: ...

def make(name: str) -> Shape:
    ...
```

```python
# The shape of extra_shapes.py
from typing import override
from registry import Shape

class Circle(Shape):
    @override
    def draw(self) -> None: ...

class Square(Shape):
    @override
    def draw(self) -> None: ...
```

<details>
<summary>Done when</summary>

before anything imports `extra_shapes`,
`make("Circle")` raises `KeyError: 'Circle'`,
and your `registry_demo.py` prints `['Circle', 'Square']` and its old draw lines again.
`uv run ruff check` passes on it with the new import in place.
You can name the line that registers `Circle` and when it runs.

<details>
<summary>Solution</summary>

If you add `import extra_shapes` to `registry_demo.py` without a `noqa` comment,
`ruff check` reports it as `F401`, an unused import,
and offers to fix it by removing the line.
Running `ruff check --fix` deletes the import.
The demo then prints `[]` and raises `KeyError: 'Circle'` at its first `make()` call.
The solution keeps the import and marks it `# noqa: F401`,
because the import exists for its side effect.

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

**Register as the class statement runs.**
`Shape.__init_subclass__()` registers `Circle` as the `class Circle(Shape):` line in `extra_shapes.py` executes.
That line executes the first time something imports `extra_shapes`,
so that import is the one trigger for the registration.
Importing `registry` leaves `extra_shapes` unloaded.
The dependency runs the other way, since `extra_shapes` imports `registry`.
Until some other module imports `extra_shapes`, `Shape.registry` stays empty,
so every `make()` call raises a `KeyError`.

The empty registry is the plugin failure the chapter describes,
reproduced in miniature.
The registry is correct, the subclass is correct, and the program still fails,
because registration is a side effect of import and nobody imported the module.

Real systems run the import deliberately.
They import the plugin package at startup, walk a directory with `importlib`,
or declare entry points that the packaging system imports for them.

`registry_demo.py` imports `Shape` and `make` from `registry`,
but every subclass now lives in `extra_shapes`.
The unchanged demo therefore prints `[]`,
and its first `make()` call raises a `KeyError`.
One added import restores the output:

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

**Mark the import as deliberate.**
The demo never uses the name `extra_shapes`,
so ruff reports the import as unused.
The chapter warns about this form: an import that exists for its side effect.
The `noqa` comment is the one mark in the file that says the import is deliberate.

The import must stay an ordinary import.
A `lazy import` defers the module body, and with it the two `class` statements,
until the first use of `extra_shapes`.
The demo makes no such use, so the classes stay unregistered.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 7. What `copy.copy()` breaks in a prototype registry

> Give `Monster` in `prototype_registry.py` a `parts: dict[str, int]` field and add a prototype that uses it.
> Change `spawn()` to use `copy.copy()` instead of `copy.deepcopy()`,
> run `test_prototype.py` with `pytest`
> (`uv run pytest Examples/26_Patterns--Factory/test_prototype.py` from the repository root),
> and explain which assertions fail and why.
> Then restore `deepcopy()` and add a test that would have caught the bug through `parts` rather than `powers`.

<details>
<summary>Where to look</summary>

[*Prototype*](../../Chapters/26_Patterns--Factory.md#prototype)
contrasts `copy.deepcopy()`, which follows every reference,
with a copy that shares what it holds.
A shallow copy duplicates the `Monster` but reuses the objects its fields reference.
Compare an assertion that rebinds a field with one that mutates a list or dictionary in place,
and see which of them `test_prototype.py` makes.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
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
    "troll": Monster("Troll", hp=40,
                     powers=["smash", "regen"]),
    "hydra": Monster("Hydra", hp=60, powers=["bite"],
                     parts={"heads": 9}),
}

def shallow_spawn(kind: str) -> Monster:
    ...
```

<details>
<summary>Done when</summary>

with `copy.copy()` in `spawn()`,
`pytest` fails both `test_spawn_is_independent()` and `test_prototype_untouched()`,
and you can say why the second test passes its `hp` assertion first.
Your new test, which mutates `parts`,
fails under `copy.copy()` and passes beside the original two once `deepcopy()` is back.

<details>
<summary>Solution</summary>

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
    "troll": Monster("Troll", hp=40,
                     powers=["smash", "regen"]),
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

`exercise_7.py` shows the bug in a function of its own, `shallow_spawn()`.
The `pytest` runs described next use `prototype_registry.py` with `parts` added and `spawn()` changed to `copy.copy()`.

With `copy.copy()`, `test_spawn_is_independent()` fails first.
`b.powers.append("curse")` appends to the one list both spawns share,
so `a.powers` becomes `["bite", "curse"]` and the assertion that it equals `["bite"]` fails.
`test_prototype_untouched()` fails too, on its second assertion.
Its first assertion holds,
because `spawned.hp = 1` rebinds an `int` field on the copy rather than mutating a shared object.
The second assertion finds that `spawned.powers` is the prototype's own list,
so `spawned.powers.append("bellow")` has given `PROTOTYPES["troll"].powers` a third entry.

A shallow copy duplicates the top object and shares everything it references,
so the fields that break are the mutable ones,
and only when something mutates them in place.
Assignment to a field is always safe.
`append()`, `[k] = v`, and `.update()` change the shared object.

A test through `parts` would have caught the bug as well:

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

**Test what the next caller receives.**
The second assertion is the one worth writing.
The first checks that the prototype survived,
but a user of the registry depends on the next spawn being correct.
The second assertion tests that spawn, the one `copy.copy()` corrupts.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 8. What the `eval()` dispatcher accepts

> Recreate the `eval()` factory described after `shape_factory_objects.py`'s listing:
> a `create_shape()` that builds each factory with `eval(f"_{kind}.Factory()")` instead of consulting `FACTORIES`.
> Call it with a `kind` string that is not a shape name but a Python expression with a side effect,
> and show that it runs the expression.
> Then show that the `FACTORIES` version raises `KeyError` for the same string.

<details>
<summary>Where to look</summary>

[Factory Objects](../../Chapters/26_Patterns--Factory.md#factory-objects)
describes the `eval()` dispatcher and the `FACTORIES` table that replaces it.
`eval()` compiles and runs the string it receives,
so `kind` can be an expression with a side effect,
such as a conditional whose test calls `print()`.
A dictionary lookup treats the same string as a key,
and a missing key raises `KeyError`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
from abc import ABC, abstractmethod
from typing import Final, Protocol, override
from exceptions import expect

class ShapeMaker(Protocol):
    def create(self) -> Shape: ...

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...

class _Circle(Shape):
    @override
    def draw(self) -> None: ...
    class Factory:
        def create(self) -> _Circle: ...

def eval_shape(kind: str) -> Shape:
    ...

ATTACK: Final[str] = (
    "Circle.Factory() if print('side effect!')"
    " else _Circle")

FACTORIES: Final[dict[str, ShapeMaker]] = {
    "Circle": _Circle.Factory(),
}

def create_shape(kind: str) -> Shape:
    ...
```

<details>
<summary>Done when</summary>

for a `kind` that is an expression rather than a shape name,
your `eval()` version prints the side effect's output before the shape's `draw()` line,
and the `FACTORIES` version raises a `KeyError` whose message quotes that whole string.

<details>
<summary>Solution</summary>

```python
# exercise_8.py
from abc import ABC, abstractmethod
from typing import Final, Protocol, override
from exceptions import expect

class ShapeMaker(Protocol):
    def create(self) -> Shape: ...

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...

class _Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")
    class Factory:
        def create(self) -> _Circle: return _Circle()

def eval_shape(kind: str) -> Shape:
    maker: ShapeMaker = eval(f"_{kind}.Factory()")
    return maker.create()

# A shape "name" that is really an expression:
ATTACK: Final[str] = (
    "Circle.Factory() if print('side effect!')"
    " else _Circle")
eval_shape(ATTACK).draw()
#: side effect!
#: Circle.draw

FACTORIES: Final[dict[str, ShapeMaker]] = {
    "Circle": _Circle.Factory(),
}

def create_shape(kind: str) -> Shape:
    return FACTORIES[kind].create()

create_shape("Circle").draw()
#: Circle.draw
expect(KeyError, create_shape, ATTACK)
#: [KeyError] "Circle.Factory() if print('side effect!')
#: else _Circle"
```

**Evaluate the name as code.**
`eval_shape()` prepends the underscore and appends `.Factory()`,
so the string it passes to `eval()` is `_Circle.Factory() if print('side effect!') else _Circle.Factory()`.
Python evaluates the condition first, which is the injected side effect.
`print()` returns `None`,
so the `else` branch runs and produces a working factory.
`eval_shape()` returns a `_Circle`, as if `kind` had been a shape name.
An expression in that string can name anything in the module's namespace,
and can load any module through `__import__()`.

**Look the name up as a key.**
`create_shape()` is the chapter's version,
which looks `kind` up in a dictionary keyed on the same names.
The string stays data,
so `create_shape(ATTACK)` raises a `KeyError` for an unknown key.

The type checker verifies that every value in the table is a `ShapeMaker`,
but it accepts the annotation on `maker` as written,
because `eval()` returns `Any`.

Whenever `kind` can come from a configuration file, a request,
or a command line, the table is the only acceptable version of the two.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 9. Recursing through `__subclasses__()`

> Derive `_Oval` from `_Circle` in `shape_factory_method.py`,
> give it its own `draw()`, and add a `case "Oval"` to `factory()`.
> Run the program and confirm that `shape_name()` never yields `"Oval"`,
> then explain why.
> Write a recursive generator `all_subclasses()` that yields a class's direct subclasses and,
> through each one's own `__subclasses__()`, every class below them.
> Use it in `shape_name()` and confirm that `Oval` now appears.

<details>
<summary>Where to look</summary>

[Simple *Factory Method*](../../Chapters/26_Patterns--Factory.md#simple-factory-method)
notes that `__subclasses__()` covers only the first level of inheritance.
Compare that with where `_Oval` sits in the hierarchy.
Write `all_subclasses()` as a recursive generator: yield each direct subclass,
then `yield from` a call on that subclass.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_9.py
import random
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import override

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...
    @staticmethod
    def factory(kind: str) -> Shape:
        ...

class _Circle(Shape):
    @override
    def draw(self) -> None: ...

class _Square(Shape):
    @override
    def draw(self) -> None: ...

class _Oval(_Circle):
    @override
    def draw(self) -> None: ...

def all_subclasses[T](cls: type[T]) -> Iterator[type[T]]:
    ...

def names(classes: Iterable[type[Shape]]) -> list[str]:
    ...

def shape_name(n: int) -> Iterator[str]:
    ...
```

<details>
<summary>Done when</summary>

`Shape.__subclasses__()` lists two classes while `list(all_subclasses(Shape))` lists three,
`_Oval` among them.
With the chapter's `random.seed(4)` and four draws,
your demo prints `Oval.draw` at least once.
You can say where `_Oval` sits relative to the classes `Shape.__subclasses__()` returns.

<details>
<summary>Solution</summary>

If you call `all_subclasses(sub)` without `yield from`,
the call builds a generator and discards it, so its body never runs.
`names(all_subclasses(Shape))` then prints `['Circle', 'Square']`,
the same list as `Shape.__subclasses__()`.
The demo draws no `Oval`.
Neither the type checker nor ruff reports the dropped keyword.
The solution's `yield from` runs each inner generator and yields every class that generator yields.

```python
# exercise_9.py
import random
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import override

class Shape(ABC):
    @abstractmethod
    def draw(self) -> None: ...
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

class _Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")

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

**Show what one level misses.**
`_Oval` is a direct subclass of `_Circle`,
one level below `Shape`'s direct subclasses,
so `Shape.__subclasses__()` lists `_Circle` and `_Square`, leaving `_Oval` out.
The original `shape_name()` draws from that list,
so every name it yields is `"Circle"` or `"Square"`.
The new `case` in `factory()` works when you call `Shape.factory("Oval")`,
but the demo never makes that call.

**Walk the whole hierarchy.**
`all_subclasses()` walks depth first,
so `Oval` comes out between `Circle` and `Square`.

The generic `T` keeps the yielded classes typed as `type[Shape]` when the argument is `Shape`,
the type `names()` requires.

**Choose from the full list.**
`random.choice()` takes a sequence,
so `shape_name()` materializes the generator with `list()`.
With the same seed the sequence differs from the chapter's sequence,
because `choice()` now picks from three classes instead of two.

`Circle` stays in the list,
because recursion adds the deeper classes and keeps the intermediate ones.
A factory that should build leaf classes alone needs a further filter,
`not cls.__subclasses__()`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 10. Finding the class that forgot `@make.register`

> Add a `Hexagon` to `protocol_registry.py` that satisfies `Shape` but carries no `@make.register`,
> and show what `make("Hexagon")` does.
> Then write a check that reports every class in the module that satisfies `Shape` and is missing from `make.registry`,
> so you find the forgotten decorator before any `make()` call.
> `@runtime_checkable`, which [*Surrogate*](../../Chapters/25_Patterns--Surrogate.md#proxy)
> shows with `isinstance()`,
> also lets `issubclass()` test a class against a Protocol whose members are all methods.

<details>
<summary>Where to look</summary>

[Explicit Registration with a Protocol](../../Chapters/26_Patterns--Factory.md#explicit-registration-with-a-protocol)
registers classes with `@make.register`,
so `make.registry` holds the classes that carry the decorator.
The check walks a module's namespace, keeps the objects that are classes,
and tests each against `Shape` with `issubclass()`.
That test works on a `Protocol` only when it is `@runtime_checkable`.
Report the classes that pass the test and are missing from the registry.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_10.py
from typing import Protocol, runtime_checkable
from exceptions import expect

@runtime_checkable
class Shape(Protocol):
    def draw(self) -> None: ...

class ShapeFactory:
    def __init__(self) -> None:
        ...

    def register[S: Shape](self, cls: type[S]) -> type[S]:
        ...

    def __call__(self, name: str) -> Shape:
        ...

make = ShapeFactory()

@make.register
class Circle:
    def draw(self) -> None: ...

@make.register
class Square:
    def draw(self) -> None: ...

class Hexagon:
    def draw(self) -> None: ...

def unregistered(namespace: dict[str, object]) -> list[str]:
    ...
```

<details>
<summary>Done when</summary>

`Hexagon().draw()` works while `make("Hexagon")` raises `KeyError: 'Hexagon'`,
and your check, run on the module's `globals()`,
reports `Hexagon` and leaves out `Circle` and `Square`.
Adding `@make.register` to `Hexagon` empties the report.

<details>
<summary>Solution</summary>

If you leave `@runtime_checkable` off `Shape`,
`Hexagon().draw()` still works and `make("Hexagon")` still raises a `KeyError`,
but `unregistered(globals())` raises a `TypeError` at its `issubclass()` call:
`Instance and class checks can only be used with @runtime_checkable protocols`.
`ty` reports the same call before the program runs,
as `isinstance-against-protocol`.
The solution decorates the Protocol because `issubclass()` requires a runtime-checkable Protocol.

```python
# exercise_10.py
from typing import Protocol, runtime_checkable
from exceptions import expect

@runtime_checkable
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

make = ShapeFactory()

@make.register
class Circle:
    def draw(self) -> None: print("Circle.draw")

@make.register
class Square:
    def draw(self) -> None: print("Square.draw")

class Hexagon:
    def draw(self) -> None: print("Hexagon.draw")

def unregistered(namespace: dict[str, object]) -> list[str]:
    return sorted(
        name
        for name, obj in namespace.items()
        if isinstance(obj, type)
        and obj is not Shape
        and issubclass(obj, Shape)
        and obj not in make.registry.values()
    )

Hexagon().draw()
#: Hexagon.draw
expect(KeyError, make, "Hexagon")
#: [KeyError] 'Hexagon'
print(unregistered(globals()))
#: ['Hexagon']
```

**Leave one class unregistered.**
`Hexagon` is a complete `Shape`, and `Hexagon().draw()` works.
The type checker accepts `Hexagon` wherever code takes a `Shape`.
Both the checker and ruff accept the module,
since `Hexagon` is an ordinary class definition.
The `KeyError` from `make("Hexagon")` names the key rather than the class or the missing line.

**Report the unregistered classes.**
`@runtime_checkable` allows the `issubclass()` call.
The `obj is not Shape` guard drops the Protocol, which passes its own test.
Calling `unregistered(globals())` at the end of the module, or from a test,
returns the names of the classes the registry lacks.

The runtime test is weaker than the type checker's test.
`issubclass()` checks for an attribute named `draw` and ignores its signature,
so a class whose `draw()` takes an extra parameter passes here.
The type checker rejects that class at `@make.register`.
The checker catches a decorated class that does not fit,
while `unregistered()` reports a fitting class that is not decorated.

`unregistered()` has two further limits.
`issubclass()` against a Protocol works only when every member is a method.
If the Protocol has a data attribute, `issubclass()` raises a `TypeError`.
`isinstance()` on an instance is then the fallback.
And `unregistered()` reads one namespace at a time,
so a plugin module must run it over its own `globals()`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 11. Prototypes registered by decoration

> Fill `PROTOTYPES` in `prototype_registry.py` by decoration instead of a table literal.
> Write a `@prototype(name)` decorator for a function that builds and returns the `Monster`,
> so that the decorator stores each decorated function's result under `name`.
> Explain why the decorator takes the name as an argument rather than reading the function's `__name__`.
> Write that version and read what `ty` reports.
> Then say what the decorated form gains over the table and what it loses.

<details>
<summary>Where to look</summary>

[*Prototype*](../../Chapters/26_Patterns--Factory.md#prototype)
keeps ready-made instances in a table,
and [Self Registration](../../Chapters/26_Patterns--Factory.md#self-registration)
fills a table as definitions execute.
`prototype(name)` is a decorator factory.
The outer call takes the name and returns a function that stores the builder's result and returns the builder.
The `__name__` version fails because of what the `Callable` annotation declares,
which the type checker's message shows.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_11.py
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
    ...

@prototype("goblin")
def goblin() -> Monster:
    ...

@prototype("troll")
def troll() -> Monster:
    ...

def spawn(name: str) -> Monster:
    ...
```

<details>
<summary>Done when</summary>

your decorated `prototype_registry.py` fills `PROTOTYPES` with `'goblin'` and `'troll'`,
and `spawn_demo.py` prints its two chapter lines unchanged.
Keying the table on the decorated function's `__name__` makes `uv run ty check` report `unresolved-attribute`.
You can name one gain and one loss against the table literal.

<details>
<summary>Solution</summary>

If you leave out `return build`,
the table still fills and the demo prints the same three lines.
But `register()` then returns `None`,
so the decorator binds the names `goblin` and `troll` to `None` rather than to the builders.
`ty` reports `invalid-return-type`,
since `register()` declares that it returns a `Builder`.
The solution returns the builder unchanged,
so `goblin()` still builds a fresh prototype when a test needs one.

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
b.powers.append("curse")
print(a.powers, b.powers)
#: ['bite'] ['bite', 'curse']
print(spawn("troll"))
#: Monster(name='Troll', hp=40, powers=['smash', 'regen'])
```

**Store each builder's prototype.**
`prototype()` is a decorator factory,
a [decorator that takes arguments](../../Chapters/14_Techniques--Decorators.md#decorators-that-take-arguments).
The table is empty at its declaration and full by the time `spawn()` runs,
because each `@prototype` line executes as the module loads.
The chapter's `registry.py` relies on the same timing.

**Take the key as an argument.**
The name is an argument because the type checker rejects `__name__` on a `Builder`.
`Builder` is a `Callable`.
A `Callable` declares how you call it, not that it carries a `__name__`.
Writing `PROTOTYPES[build.__name__] = build()` draws:

```text
error[unresolved-attribute]: Object of type `Builder` has no attribute `__name__`
```

The chapter's `ShapeFactory.register()` in `shape_registry.py` reads `__name__` safely because it receives a class,
a `type[S]`, which has a `__name__`.
Pyright accepts `build.__name__`,
since it gives every function object's attributes to a `Callable`.
`ty`, the checker the book uses, rejects it.

Passing the name also frees the key from the function's name,
so you can call the builder `make_goblin()` while the key stays `"goblin"`.

The decorated form gains the same openness the registries gain.
Any module can define a prototype, with its name beside its definition,
and leave `PROTOTYPES` as it was.
The key type widens from the chapter's `Kind` to `str`,
because an open table cannot list its names in advance.
The builder is also a function,
so `goblin()` still produces a fresh prototype on demand when a test needs one straight from its builder.

Against that, the decorated form turns the table literal into a decorator plus a function for each monster,
and repeats the name at every definition.
It also has the two failures the chapter describes for registration.
An undecorated builder is absent from the table,
so `spawn()` raises a `KeyError` that names the key and not the builder.
And a builder's decorator runs only when something imports its module.
For two monsters in one file,
the table literal says the same thing in fewer lines.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
