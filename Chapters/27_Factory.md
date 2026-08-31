# Factory

When you discover that you need to add new types to a system,
the most sensible first step is to use polymorphism to create a common interface to those new types.
The common interface separates the rest of the code in your system from the knowledge of the specific types that you are adding.
You may add new types without disturbing existing code ... or so it seems.
At first, the only place you appear to change such a design is where you inherit a new type.
But you must still create an object of your new type,
and at the point of creation you must name the exact constructor.
Thus, if the code that creates objects appears throughout your application,
you have the same problem when adding new types.
You must still find and edit every place in your code where the type matters.
Creating the type matters here, not using it (which polymorphism handles).
The effect is the same:
adding a new type means edits scattered through the code.

The solution is to encapsulate object creation:
make a common *factory* create every object instead of spreading creational code through the system.
If your program must call this factory whenever it needs to create one of your objects,
then you change only the factory when you add a new object.

Since every object-oriented program creates objects,
and since you will likely extend your program by adding new types,
Factory might be the most common design pattern.

## Simple Factory Method

As an example, revisit the `Shape` hierarchy from [Rethinking Objects](20_Rethinking_Objects.md#abstract-base-classes).
The factory can be a `@staticmethod` of the base class:

```python
# shapefact1/shape_factory1.py
import random
from collections.abc import Iterator
from typing import override

class Shape:
    def draw(self) -> None: ...
    def erase(self) -> None: ...
    # Create based on class name:
    @staticmethod
    def factory(kind: str) -> Shape:
        match kind:
            case "Circle":
                return Circle()
            case "Square":
                return Square()
            case _:
                raise ValueError(
                    f"Bad shape creation: {kind}")

class Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")
    @override
    def erase(self) -> None: print("Circle.erase")

class Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")
    @override
    def erase(self) -> None: print("Square.erase")

def shape_name_gen(n: int) -> Iterator[str]:
    for _ in range(n):
        yield random.choice(Shape.__subclasses__()).__name__

if __name__ == "__main__":
    random.seed(4)  # Reproducible shape sequence
    shapes = [Shape.factory(kind)
              for kind in shape_name_gen(4)]
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

The `factory()` takes an argument that selects the type of `Shape` to create.
Here the argument is a string, but it could be any kind of data.
The `factory()` is now the only other code in the system that needs to change when you add a new type of `Shape`.

I have also used a *generator* (see [Iterators](23_Iterators.md#generators)).
A factory takes information telling it what to build.
A generator object does the opposite:
it holds an internal algorithm and produces the next value with no argument.
`shape_name_gen()` takes `n` and returns a generator object,
and that object then produces names on demand.
Those names are the arguments to `Shape.factory()`.
In a real program the initialization data comes from outside the system,
not from random generation as here.

Inside `shape_name_gen()`,
`Shape.__subclasses__()` produces a list of references to each direct subclass of `Shape`.
It covers only the first level of inheritance,
so a class inheriting from `Circle` is not in the list.
For a deeper hierarchy, recurse through each subclass's own `__subclasses__()`.

To discourage direct construction of the concrete shapes,
give them module-level names with a leading underscore:
a convention rather than concealment, and the convention is all Python provides
([Singleton](24_Singleton.md#nothing-keeps-the-class-private) makes the same case).
Nesting the classes inside `factory()` looks stronger and is worse.
A `class` statement is executable code,
so every call would define fresh `Circle` and `Square` classes:
two shapes from different calls would share behavior but not a class,
failing `type(a) is type(b)` and `isinstance()` alike,
and `Shape.__subclasses__()` would no longer name the kinds.

## The Pythonic Factory: a Dictionary

A factory turns data, such as a name,
into an object without scattering constructors through your code.
In Python a class is a first-class object.
You can store it in a variable and call it to construct an instance.

Thus, the simplest factory is a dictionary that maps names to classes.
No factory method and no factory class; the `dict` is the factory:

```python
# shape_table.py
from typing import Final, override

class Shape:
    def draw(self) -> None: ...

class Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")

class Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")

SHAPES: Final[dict[str, type[Shape]]] = {
    "Circle": Circle,
    "Square": Square,
}

def make(kind: str) -> Shape:
    return SHAPES[kind]()

make("Circle").draw()
#: Circle.draw
make("Square").draw()
#: Square.draw
```

Because the `dict` values are classes, `type[Shape]` is their type,
and calling one constructs an instance.
Adding a `Triangle` means one new class and one new line in `SHAPES`.

You can remove that line too,
so the factory never needs editing when you add a type,
by letting each subclass register itself through `__init_subclass__()`
(see [Metaprogramming](17_Metaprogramming.md#self-registration-of-subclasses)):

```python
# registry.py
from typing import ClassVar, override

class Shape:
    registry: ClassVar[dict[str, type[Shape]]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        Shape.registry[cls.__name__] = cls

    def draw(self) -> None: ...

class Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")

class Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")

def make(kind: str) -> Shape:
    return Shape.registry[kind]()

if __name__ == "__main__":
    print(sorted(Shape.registry))
    for kind in ["Circle", "Square", "Circle"]:
        make(kind).draw()
#: ['Circle', 'Square']
#: Circle.draw
#: Square.draw
#: Circle.draw
```

Nothing in the listing calls a register function.
The two `class` statements fill `Shape.registry` on their own,
as the printed key list shows.
Adding a `Triangle` is now a single class definition.
It registers itself, and `make()` builds it with no change to the factory.
`Shape.__subclasses__()` could have built the table instead,
but it lists only direct subclasses,
while `__init_subclass__()` runs for every class anywhere below `Shape`.
[Pattern Refactoring](37_Pattern_Refactoring.md#simulating-a-trash-recycler)
uses this same self-registration.

A dictionary of classes,
whether you fill it by hand or the classes fill it themselves,
is the ordinary Python factory.
That is the dissolution [The Pattern Concept](21_The_Pattern_Concept.md#when-a-pattern-dissolves)
describes: the pattern remains,
but no longer needs a class hierarchy to express it.
The remaining sections cover the classic object-oriented factories,
for contrast.

`__init_subclass__()` runs as the subclass's `class` statement executes.
In one file the registration runs before anything calls `make()`,
but a subclass defined in another module registers itself only when something imports that module.
The classic failure is a plugin that "never registered": the class is fine,
the registry is fine, and nothing imported the module that defines the class.
A [lazy import](06_Modules_and_Packages.md#lazy-imports)
produces the same failure even when the import statement is in the file.
The module body, and with it the registration,
does not run until the first use of the imported name,
and an import written only to trigger registration never uses that name.
Running with `-X lazy_imports=all` makes ordinary imports lazy too.
Import a plugin module eagerly when the import exists for its side effect.

Because the registry keys on `cls.__name__` alone,
two classes that share a name, from different modules,
silently overwrite each other.
Key on a qualified name when a collision is possible.

`__init_subclass__()` names `Shape.registry` rather than `cls.registry` on purpose:
`cls.registry` resolves through the MRO,
so a subclass that gives itself a `registry` of its own would create a second table that `make()` never reads,
with no error to signal it.

The tests confirm that every subclass registers itself,
and that a new subclass needs no change to `make()`.
Defining a fresh subclass of `Shape` inside the test is enough to put it in the registry:

```python
# test_registry.py
from typing import override
import pytest
from registry import Circle, Shape, Square, make

def test_subclasses_auto_register() -> None:
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

def test_unknown_name_raises() -> None:
    with pytest.raises(KeyError):
        make("Hexagon")
```

## Polymorphic Factories

Because the static `factory()` method in `shape_factory1.py` collects all the creation operations in one method,
that's the only place you need to change the code.
*GoF Design Patterns*, however,
emphasizes that the *Factory Method* pattern exists so you can subclass different factories from the basic factory
(the design in `shape_factory1.py` is a special case).
For its sample code,
*GoF Design Patterns* reuses the maze example from the *Abstract Factory*
(the next section covers that pattern),
subclassing the game to override its factory methods.
This version of `shape_factory1.py` moves the factory methods into separate classes and calls them polymorphically:

```python
# shapefact2/shape_factory2.py
# Polymorphic factory methods.
import random
from collections.abc import Iterator
from typing import Final, Protocol, override

class ShapeMaker(Protocol):
    def create(self) -> Shape: ...

class Shape:
    def draw(self) -> None: ...
    def erase(self) -> None: ...

class Circle(Shape):
    @override
    def draw(self) -> None: print("Circle.draw")
    @override
    def erase(self) -> None: print("Circle.erase")
    class Factory:
        def create(self) -> Circle: return Circle()

class Square(Shape):
    @override
    def draw(self) -> None: print("Square.draw")
    @override
    def erase(self) -> None: print("Square.erase")
    class Factory:
        def create(self) -> Square: return Square()

FACTORIES: Final[dict[str, ShapeMaker]] = {
    "Circle": Circle.Factory(),
    "Square": Square.Factory(),
}

def create_shape(kind: str) -> Shape:
    return FACTORIES[kind].create()

def shape_name_gen(n: int) -> Iterator[str]:
    types = Shape.__subclasses__()
    for _ in range(n):
        yield random.choice(types).__name__

if __name__ == "__main__":
    random.seed(4)
    shapes = [create_shape(kind)
              for kind in shape_name_gen(4)]
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

Now the factory methods are polymorphic:
each type of shape defines its own nested `Factory` class whose `create()` method builds an object of that type.
`FACTORIES` maps each kind's name to an instance of its factory,
and `create_shape()` looks that factory up and calls it right away.
A more complex design would return the factory object to the caller,
who could keep it and construct objects from it later.
Much of the time, however, you don't need the polymorphic factory method,
and a single static method in the base class (as in `shape_factory1.py`)
is enough.

A `Factory` class nested in every shape is machinery Python does not need,
kept here to show the structure *GoF Design Patterns* intends.
The registry in `registry.py` does the same job with no nested classes.
Write a separate factory class when object creation takes real work beyond calling a constructor,
such as pooling, caching, or consulting external configuration.

An earlier version of this example did without `FACTORIES` by dispatching through `eval(f"{kind}.Factory()")`,
which is worse than unnecessary.
`create_shape()` then compiles and runs whatever string it receives,
so a `kind` read from a configuration file, a request,
or a command line is arbitrary code rather than a shape name.
The dictionary lookup either produces a factory or raises a `KeyError`.
Exercise 8 runs the attack against both.

## Abstract Factories

The *Abstract Factory* pattern has the same structure as the factory objects in `shape_factory2.py`,
with not one but several factory methods.
Each factory method creates a different kind of object.
When you create the factory object,
you choose the concrete version of every object that factory creates.
The example in *GoF Design Patterns* implements portability across graphical user interfaces
(GUIs).
You create a factory object for the GUI you're working with,
and from then on when you ask that factory for a menu, button, or slider,
it creates the version of that item suited to that GUI.
Thus you can isolate, in one place,
the effect of changing from one GUI to another.

As another example, suppose you are creating a general-purpose gaming environment that supports different types of games.
Here's how it might look using an abstract factory:

![Two parallel hierarchies, Character and Obstacle, with each concrete factory producing the one matched pair its game needs: KittiesAndPuzzles always pairs Kitty with Puzzle, WarriorsAndWeapons always pairs Warrior with Weapon](_images/abstract_factory)

```python
# games.py
from typing import override

class Obstacle:
    def action(self) -> str:
        raise NotImplementedError

class Character:
    def interact_with(self, obstacle: Obstacle) -> None:
        raise NotImplementedError

class Kitty(Character):
    @override
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Kitty has encountered a", obstacle.action())

class Warrior(Character):
    @override
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Warrior now battles a", obstacle.action())

class Puzzle(Obstacle):
    @override
    def action(self) -> str:
        return "Puzzle"

class Weapon(Obstacle):
    @override
    def action(self) -> str:
        return "Weapon"

# The Abstract Factory:
class GameElementFactory:
    def make_character(self) -> Character:
        raise NotImplementedError
    def make_obstacle(self) -> Obstacle:
        raise NotImplementedError

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
#: Kitty has encountered a Puzzle
g2.play()
#: Warrior now battles a Weapon
```

In this environment, `Character` objects interact with `Obstacle` objects,
but the types of characters and obstacles depend on the kind of game you're playing.
You determine the kind of game by choosing a particular `GameElementFactory`,
and then the `GameEnvironment` controls the setup and play of the game.
In this example, the setup and play are simple, but those activities
(the *initial conditions* and the *state change*)
can determine much of the game's outcome.
`GameEnvironment` has no place to vary the rules of play,
so a real game would need one,
either a subclass overriding `play()` or a rules object passed alongside the factory.

`interact_with()` dispatches on the character's type,
and `obstacle.action()` dispatches again on the obstacle's,
so the pair of calls chooses behavior from both types.
[Multiple Dispatching](32_Multiple_Dispatching.md)
develops that pair of calls into a technique.

The base classes `Obstacle`, `Character`, and `GameElementFactory`
(translated from the Java version)
force every concrete class to inherit from them.
Those `raise NotImplementedError` bodies enforce less than the listing suggests.
They fail at call time:
a concrete factory that omits `make_obstacle()` constructs with no error and raises an exception only when something calls the missing method.
An `@abstractmethod` fails at instantiation,
the way `Partial()` did in [Surrogate](26_Surrogate.md),
and at least reports the omission before anything calls the missing method.
Python does not need that inheritance to keep the same checking.
A *Protocol* describes the required shape,
and any class with that shape conforms,
with no base class to derive from while still type checking:

```python
# games2.py
# Simplified Abstract Factory.
from typing import Protocol

class Obstacle(Protocol):
    def action(self) -> str: ...

class Character(Protocol):
    def interact_with(self, obstacle: Obstacle) -> None: ...

class GameElementFactory(Protocol):
    def make_character(self) -> Character: ...
    def make_obstacle(self) -> Obstacle: ...

class Kitty:
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Kitty has encountered a", obstacle.action())

class Warrior:
    def interact_with(self, obstacle: Obstacle) -> None:
        print("Warrior now battles a", obstacle.action())

class Puzzle:
    def action(self) -> str: return "Puzzle"

class Weapon:
    def action(self) -> str: return "Weapon"

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
# ty: invalid-argument-type:
# GameEnvironment(BrokenFactory())
g1.play()
#: Kitty has encountered a Puzzle
g2.play()
#: Warrior now battles a Weapon
```

The concrete classes inherit nothing,
but the type checker still verifies that each one satisfies the appropriate `Protocol`:
a `GameElementFactory` must supply `make_character()` and `make_obstacle()`,
a `Character` must supply `interact_with()`,
and an `Obstacle` must supply `action()`.
`BrokenFactory` supplies `make_character()` and omits `make_obstacle()`,
and uncommenting the line that passes a `BrokenFactory` to `GameEnvironment` produces `protocol member make_obstacle is not defined on type BrokenFactory`.
With the Protocol, the checker reports the omission before the program runs,
the earliest rung on the failure-time ladder [Surrogate](26_Surrogate.md#proxy)
climbed.
Checking against a Protocol is structural typing from [Static Types](08_Static_Types.md#structural-typing-with-protocols).
Structural typing preserves the purpose of the interfaces,
without the coupling a shared base class imposes.

## Prototype

The factories so far build each object from a class and some arguments.
*Prototype* instead keeps one fully configured instance and makes new objects by copying it.
Use Prototype when a ready-made instance is easier to clone than to rebuild,
or when construction is slow and the instances share most of the setup.

The `copy` module clones any object.
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
# Build a variant by cloning and adjusting, not rebuilding:
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
```

Because the `clone()` method wraps `copy.deepcopy()`,
`captain` gets its own `powers` list,
and appending to it leaves `goblin.powers` unchanged.
The last three lines show the mistake, not the recommendation:
`copy.copy()` duplicates the `Monster` and shares its `powers` list,
so changing that list through one object changes it for the other,
with no error to signal it.

You can combine prototype with a registry.
Instead of a registry of classes,
keep a registry of prototypical instances and clone the chosen one:

```python
# prototype_registry.py
import copy
from dataclasses import dataclass, field
from typing import Final

@dataclass
class Monster:
    name: str
    hp: int
    powers: list[str] = field(default_factory=list)

PROTOTYPES: Final[dict[str, Monster]] = {
    "goblin": Monster("Goblin", hp=10, powers=["bite"]),
    "troll": Monster("Troll", hp=40,
                     powers=["smash", "regen"]),
}

def spawn(kind: str) -> Monster:
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
callers can modify their copy without modifying the prototype.
Compare `spawn()` with `make()` in `registry.py`.
There the table holds classes and calls a constructor.
In `prototype_registry.py` the table holds instances and copies them.
Use the prototype form when the interesting part of an object is its configured state rather than its type.

These tests check the two required properties for a prototype registry.
Each spawn must be independent, and the stored prototype must never change:

```python
# test_prototype.py
from prototype_registry import PROTOTYPES, spawn

def test_clone_is_independent() -> None:
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
    # deepcopy: the list is not shared either
    assert PROTOTYPES["troll"].powers == ["smash", "regen"]
```

## Builder

*Builder* is the last of the *GoF Design Patterns* creational patterns to cover
([Singleton](24_Singleton.md) has its own chapter):
separate the construction of a complex object from its representation,
assembling it in steps.
In Java and C++ it takes the place of the *telescoping constructor*.
A class with many optional settings needs a constructor for every useful combination,
because those languages have no keyword arguments.
The workaround is a companion class that collects settings one method call at a time.
Translated into Python with its structure intact, it looks like this:

```python
# pizza_builder.py
from dataclasses import dataclass
from typing import Self

@dataclass(frozen=True)
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

Because each setter returns `self`,
annotated with `Self` from [Static Types](08_Static_Types.md#the-self-type),
the calls chain.
`build()` freezes the accumulated settings into an immutable `Pizza`.
The class works and reads well, but it solves a problem Python does not have.
Keyword arguments with defaults are the built-in builder:

```python
# pizza_direct.py
from dataclasses import dataclass, replace

@dataclass(frozen=True)
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

Every combination of settings is a single call,
the call site names each option just as the chain does,
and the fields declare the defaults instead of a second class.
`dataclasses.replace()` covers the second use of builder chains:
starting from an existing configuration and varying it.
For a frozen data class, `replace()` is Prototype and Builder in one function,
copying the configured state and changing the chosen fields in the copy.
`copy.replace()` is the general form of the same operation,
working on any object that defines `__replace__()`.
A data class defines that method for you.
A test confirms the two forms produce the same pizza:

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
```

[Decorators](14_Decorators.md#the-decorator-pattern) has its own `Pizza`,
modeling toppings as wrapper objects instead of builder-collected fields,
to illustrate the unrelated Decorator pattern.

Builder remains useful in Python when construction is genuinely a process.
The steps must come in an order, later steps depend on earlier ones,
and rules span the steps.
`GameBuilder` in [Simulation](38_Simulation.md#a-robot-in-a-maze) qualifies.
It assembles a maze in three stages, creating rooms, connecting doors,
then pairing the teleports that share a target letter,
and each stage relies on what the previous stage established.
No single constructor call can express that.
The standard library's `argparse.ArgumentParser` has the same shape.
`add_argument()` calls accumulate a specification,
and `parse_args()` is the `build()`.

The smallest builder in Python is easy to overlook.
Appending parts to a list and finishing with `"".join(parts)` builds an immutable product,
a string, through a mutable intermediate.
That is the Builder structure.
`PizzaBuilder` collecting toppings in a list and freezing them into a tuple at `build()` is the same structure.
Reserve the pattern, and the name,
for construction that is a process with intermediate state and rules of its own.
When the "steps" are optional values,
keyword arguments and a data class are the builder.

## Which Factory to Use

Match the machinery to what varies:

- A name maps to a class: use a dictionary.
  Add `__init_subclass__()` registration once the set of classes is open,
  or spread across modules.
- Construction takes real work beyond calling a constructor
  (pooling, caching, consulting configuration): write a factory function,
  and a factory class only when that work has state of its own.
- You must choose several products together as a matched set:
  use Abstract Factory, expressed as a `Protocol` rather than a base class.
- The interesting part of an object is its configured state rather than its type:
  keep a prototype and copy it.
  For a frozen data class, `replace()` is that copy.
- Construction is a genuine process with ordered steps and rules spanning them:
  use Builder.
  When the "steps" are optional values, keyword arguments are the builder.

The static `factory()` method and the nested-`Factory`-class dispatcher are here because *GoF Design Patterns* describes them,
not because Python needs them.
Both exist to work around languages where a class is not an object you can put in a dictionary.

## Exercises

1.  Add a class `Triangle` to `shape_factory1.py`.
2.  Add a class `Triangle` to `shape_factory2.py`.
3.  Add a new type of `GameElementFactory` called `GnomesAndFairies`,
    first to `games.py` and then to `games2.py`.
    In `games2.py`, leave out `make_obstacle()` at first and confirm the error your type checker reports.
    Then add it.
4.  Modify `shape_factory2.py` to use an *Abstract Factory* to create different sets of shapes
    (for example, one type of factory object creates "thick shapes," another creates "thin shapes," but each factory object can create all the shapes: circles, squares, triangles, etc.).
5.  Add a rule to both pizza examples: a pizza may carry at most four toppings.
    In `pizza_direct.py`, enforce it with `__post_init__()`.
    In `pizza_builder.py`,
    decide whether it belongs in `topping()` or `build()`.
    In which version can an invalid pizza exist, even momentarily?
6.  Move `Circle` and `Square` out of `registry.py` into a new module,
    `extra_shapes.py`.
    Confirm that `make("Circle")` now raises `KeyError` until something imports `extra_shapes`,
    and explain which line of which file registers the class, and when it runs.
7.  Give `Monster` in `prototype_registry.py` a `parts: dict[str, int]` field and add a prototype that uses it.
    Change `spawn()` to use `copy.copy()` instead of `copy.deepcopy()`,
    run `test_prototype.py`, and explain which assertion fails and why.
    Then restore `deepcopy()` and add a test that would have caught the bug through `parts` rather than `powers`.
8.  Recreate the `eval()` dispatcher described after `shape_factory2.py`'s listing:
    a `create_shape()` that builds each factory with `eval(f"{kind}.Factory()")` instead of consulting `FACTORIES`.
    Call it with a `kind` string that is not a shape name but a Python expression with a side effect,
    and show that it runs the expression.
    Then show that the `FACTORIES` version raises `KeyError` for the same string.
