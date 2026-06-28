# Factory

> Encapsulating Object Creation

When you discover that you need to add new types to a system,
the most sensible first step is to use polymorphism to create a common interface to those new types.
This separates the rest of the code in your system from the knowledge of the specific types that you are adding.
New types may be added without disturbing existing code ... or so it seems.
At first it would appear that the only place you need to change the code in such a design is the place where you inherit a new type,
but this is not quite true.
You must still create an object of your new type,
and at the point of creation you must specify the exact constructor to use.
Thus, if the code that creates objects is distributed throughout your application,
you have the same problem when adding new types.
You must still chase down all the points of your code where type matters.
It happens to be the *creation* of the type that matters here rather than the *use* of the type (which is taken care of by polymorphism),
but the effect is the same: adding a new type can cause problems.

The solution is to force the creation of objects to occur through a common *factory* rather than to allow the creational code to be spread throughout your system.
If all the code in your program must go through this factory whenever it needs to create one of your objects,
then all you must do when you add a new object is to modify the factory.

Since every object-oriented program creates objects,
and since it's likely you will extend your program by adding new types,
factories might be the most useful design patterns.

## Simple Factory Method

As an example, let's revisit the `Shape` system.

One approach is to make the factory a `static` method of the base class:

```python
# shapefact1/shape_factory1.py
# A simple static factory method.
import random
from collections.abc import Iterator
from typing import override

class Shape:
    def draw(self) -> None: ...
    def erase(self) -> None: ...
    # Create based on class name:
    @staticmethod
    def factory(kind: str) -> Shape:
        if kind == "Circle":
            return Circle()
        if kind == "Square":
            return Square()
        raise ValueError(f"Bad shape creation: {kind}")

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

# Generate shape name strings:
def shape_name_gen(n: int) -> Iterator[str]:
    types = Shape.__subclasses__()
    for i in range(n):
        yield random.choice(types).__name__

if __name__ == "__main__":
    random.seed(47)  # Reproducible shape sequence
    shapes = [Shape.factory(i) for i in shape_name_gen(7)]
    for shape in shapes:
        shape.draw()
        shape.erase()
#: Square.draw
#: Square.erase
#: Circle.draw
#: Circle.erase
#: Square.draw
#: Square.erase
#: Square.draw
#: Square.erase
#: Square.draw
#: Square.erase
#: Square.draw
#: Square.erase
#: Square.draw
#: Square.erase
```

The `factory()` takes an argument that allows it to determine what type of `Shape` to create;
it happens to be a string here but it could be any set of data.
The `factory()` is now the only other code in the system that needs to be changed when a new type of `Shape` is added (the initialization data for the objects will presumably come from somewhere outside the system, and not be a hard-coded array as in the above example).

Note the `@staticmethod` decorator,
which marks a method that takes no `self` and so can be called on the class itself.

I have also used a *generator*.
A generator is a special case of a factory:
it's a factory that takes no arguments in order to create a new object.
Normally you hand some information to a factory in order to tell it what kind of object to create and how to create it,
but a generator has some kind of internal algorithm that tells it what and how to build.
It "generates out of thin air" rather than being told what to create.

Now, this may not look consistent with the code you see above:

    for i in shape_name_gen(7)

It looks like there's an initialization taking place.
This is where a generator is a bit strange:
when you call a function that contains a `yield` statement (`yield` is what makes a function a generator),
that function actually returns a generator object that has an iterator.
This iterator is implicitly used in the `for` statement above,
so it appears that you are iterating through the generator function,
not what it returns.

Thus, the code that you write is actually a kind of factory,
that creates the generator objects that do the actual generation.
You can use the generator explicitly if you want, for example:

```python
# explicit_generator.py
# A generator-factory can be driven by hand: next() pulls the next
# object from it. shape_name_gen is reused from shape_factory1.
import random
from shapefact1.shape_factory1 import shape_name_gen

random.seed(47)  # Make the random choices reproducible

gen = shape_name_gen(7)
print(next(gen))
#: Square
print(next(gen))
#: Circle
```

So `next(gen)` produces the next object from the generator.
`shape_name_gen()` is the factory, and `gen` is the generator.

Inside the generator-factory, you can see the call to `__subclasses__()`,
which produces a list of references to each of the subclasses of `Shape`.
You should be aware, however,
that this only works for the first level of inheritance from `Shape`,
so if you were to inherit a new class from `Circle`,
it wouldn't show up in the list generated by `__subclasses__()`.
If you need to create a deeper hierarchy this way,
you must recurse the `__subclasses__()` list.

Also note that in `shape_name_gen()` the statement:

    types = Shape.__subclasses__()

is only executed when the generator object is produced;
each time the `next()` method of this generator object is called (which, as noted above, may happen implicitly),
only the code in the `for` loop will be executed,
so you don't have wasteful execution (as you would if this were an ordinary function).

### Preventing direct creation

To disallow direct access to the classes,
you can nest the classes within the factory method, like this:

```python
# shapefact1/nested_shape_factory.py
import random
from collections.abc import Iterator
from typing import override

class Shape:
    def draw(self) -> None: ...
    def erase(self) -> None: ...

def factory(kind: str) -> Shape:
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

    if kind == "Circle":
        return Circle()
    if kind == "Square":
        return Square()
    raise ValueError(f"Bad shape creation: {kind}")

def shape_name_gen(n: int) -> Iterator[Shape]:
    for i in range(n):
        yield factory(random.choice(["Circle", "Square"]))

if __name__ == "__main__":
    random.seed(47)  # Reproducible shape sequence
    # Circle()  # Not defined outside factory()
    for shape in shape_name_gen(7):
        shape.draw()
        shape.erase()
#: Square.draw
#: Square.erase
#: Circle.draw
#: Circle.erase
#: Square.draw
#: Square.erase
#: Square.draw
#: Square.erase
#: Square.draw
#: Square.erase
#: Square.draw
#: Square.erase
#: Square.draw
#: Square.erase
```

## The Pythonic Factory: a Dictionary

A factory exists to turn data, such as a name,
into an object without scattering constructors through your code.
In Python a class is itself a first-class object:
you can store it in a variable and call it to make an instance.

Thus, the simplest factory is a dictionary that maps names to classes.
There is no factory method and no factory class; the `dict` *is* the factory.
You can go one step further so the factory never needs editing when a type is added,
by letting each subclass register itself through `__init_subclass__()`:

```python
# registry.py
# A class is a first-class object, so a factory is just a dict of
# classes. __init_subclass__ lets each subclass register itself, so
# the factory never needs editing when you add a type.
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

for kind in ["Circle", "Square", "Circle"]:
    make(kind).draw()
#: Circle.draw
#: Square.draw
#: Circle.draw
```

Adding a `Triangle` is now a single class definition: it registers itself,
and `make()` builds it with no change to the factory.
This is the same self-registration used in [Pattern Refactoring](33_Pattern_Refactoring.md#simulating-a-trash-recycler),
and it is the most common form of factory in idiomatic Python.
The sections below show the classic object-oriented factories for contrast.

A test confirms the two behaviors that matter: every subclass registers itself,
and a new subclass needs no change to `make()`.
Defining a fresh `Shape` inside the test is enough to see it appear in the registry:

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

The static `factory()` method in the previous example forces all the creation operations to be focused in one spot,
so that's the only place you need to change the code.
However, the *Design Patterns* book emphasizes that the reason for the *Factory Method* pattern is so that different types of factories can be subclassed from the basic factory (the above design is mentioned as a special case).
However, the book does not provide an example,
but instead just repeats the example used for the *Abstract Factory* (you'll see an example of this in the next section).
Here is `shape_factory1.py` modified so the factory methods are in a separate class as virtual functions.
Notice also that the specific `Shape` classes are dynamically loaded on demand:

```python
# shapefact2/shape_factory2.py
# Polymorphic factory methods.
import random
from collections.abc import Iterator
from typing import Any, ClassVar, override

class ShapeFactory:
    factories: ClassVar[dict[str, Any]] = {}

    @staticmethod
    def add_factory(kind: str, shape_factory: Any) -> None:
        ShapeFactory.factories[kind] = shape_factory

    # A Template Method:
    @staticmethod
    def create_shape(kind: str) -> Shape:
        if kind not in ShapeFactory.factories:
            ShapeFactory.factories[kind] = eval(kind + '.Factory()')
        return ShapeFactory.factories[kind].create()

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
    def draw(self) -> None:
        print("Square.draw")
    @override
    def erase(self) -> None:
        print("Square.erase")
    class Factory:
        def create(self) -> Square: return Square()

def shape_name_gen(n: int) -> Iterator[str]:
    types = Shape.__subclasses__()
    for i in range(n):
        yield random.choice(types).__name__

if __name__ == "__main__":
    random.seed(47)  # Reproducible shape sequence
    shapes = [ShapeFactory.create_shape(i) for i in shape_name_gen(7)]
    for shape in shapes:
        shape.draw()
        shape.erase()
#: Square.draw
#: Square.erase
#: Circle.draw
#: Circle.erase
#: Square.draw
#: Square.erase
#: Square.draw
#: Square.erase
#: Square.draw
#: Square.erase
#: Square.draw
#: Square.erase
#: Square.draw
#: Square.erase
```

Now the factory method appears in its own class, `ShapeFactory`,
as the `create()` method.
The different types of shapes must each create their own factory with a `create()` method to create an object of their own type.
The actual creation of shapes is performed by calling `ShapeFactory.create_shape()`,
which is a static method that uses the dictionary in `ShapeFactory` to find the appropriate factory object based on an identifier that you pass it.
The factory is immediately used to create the shape object,
but you could imagine a more complex problem where the appropriate factory object is returned and then used by the caller to create an object in a more sophisticated way.
However, it seems that much of the time you don't need the intricacies of the polymorphic factory method,
and a single static method in the base class (as shown in `shape_factory1.py`) will work fine.

Notice that the `ShapeFactory` must be initialized by loading its dictionary with factory objects,
which takes place in the static initialization clause of each of the shape implementations.

This version leans on `eval()` and a `Factory` class nested in every shape,
neither of which Python needs.
Because classes are already first-class objects,
the registry shown above does the same job:
it maps a name straight to a class and constructs it.
Prefer that.
A separate factory *class* earns its keep only when creating an object takes real work beyond calling a constructor,
such as pooling, caching, or consulting external configuration.

## Abstract Factories

The *Abstract Factory* pattern looks like the factory objects we've seen previously,
with not one but several factory methods.
Each of the factory methods creates a different kind of object.
The idea is that at the point of creation of the factory object,
you decide how all the objects created by that factory will be used.
The example given in *Design Patterns* implements portability across various graphical user interfaces (GUIs):
you create a factory object appropriate to the GUI that you're working with,
and from then on when you ask it for a menu, button, slider,
etc. it will automatically create the appropriate version of that item for the GUI.
Thus you're able to isolate, in one place,
the effect of changing from one GUI to another.

As another example suppose you are creating a general-purpose gaming environment and you want to be able to support different types of games.
Here's how it might look using an abstract factory:

```python
# games.py
# An example of the Abstract Factory pattern.
from typing import override

class Obstacle:
    def action(self) -> str:
        raise NotImplementedError

class Character:
    def interact_with(self, obstacle: Obstacle) -> None: ...

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

class NastyWeapon(Obstacle):
    @override
    def action(self) -> str:
        return "NastyWeapon"

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
    def make_obstacle(self) -> Obstacle: return NastyWeapon()

class GameEnvironment:
    def __init__(self, factory: GameElementFactory) -> None:
        self.factory = factory
        self.p = factory.make_character()
        self.ob = factory.make_obstacle()
    def play(self) -> None:
        self.p.interact_with(self.ob)

g1 = GameEnvironment(KittiesAndPuzzles())
g2 = GameEnvironment(WarriorsAndWeapons())
g1.play()
#: Kitty has encountered a Puzzle
g2.play()
#: Warrior now battles a NastyWeapon
```

In this environment, `Character` objects interact with `Obstacle` objects,
but there are different types of Characters and obstacles depending on what kind of game you're playing.
You determine the kind of game by choosing a particular `GameElementFactory`,
and then the `GameEnvironment` controls the setup and play of the game.
In this example, the setup and play is simple,
but those activities (the *initial conditions* and the *state change*) can determine much of the game's outcome.
Here, `GameEnvironment` is not designed to be inherited,
although it might make sense to do that.

This also contains examples of *Double Dispatching* and the *Factory Method*,
both of which are explained later.

The above scaffolding of `Obstacle`,
`Character` and `GameElementFactory` (which was translated from the Java version of this example) is unnecessary;
it's only required for languages that have static type checking.
As long as the concrete Python classes follow the form of the required classes,
we don't need any base classes:

```python
# games2.py
# Simplified Abstract Factory.
from typing import Any

class Kitty:
    def interact_with(self, obstacle: Any) -> None:
        print("Kitty has encountered a", obstacle.action())

class Warrior:
    def interact_with(self, obstacle: Any) -> None:
        print("Warrior now battles a", obstacle.action())

class Puzzle:
    def action(self) -> str: return "Puzzle"

class NastyWeapon:
    def action(self) -> str: return "NastyWeapon"

# Concrete factories:
class KittiesAndPuzzles:
    def make_character(self) -> Kitty: return Kitty()
    def make_obstacle(self) -> Puzzle: return Puzzle()

class WarriorsAndWeapons:
    def make_character(self) -> Warrior: return Warrior()
    def make_obstacle(self) -> NastyWeapon: return NastyWeapon()

class GameEnvironment:
    def __init__(self, factory: Any) -> None:
        self.factory = factory
        self.p = factory.make_character()
        self.ob = factory.make_obstacle()
    def play(self) -> None:
        self.p.interact_with(self.ob)

g1 = GameEnvironment(KittiesAndPuzzles())
g2 = GameEnvironment(WarriorsAndWeapons())
g1.play()
#: Kitty has encountered a Puzzle
g2.play()
#: Warrior now battles a NastyWeapon
```

Another way to put this is that all inheritance in Python is implementation inheritance;
since Python does its type-checking at runtime,
there's no need to use interface inheritance so that you can upcast to the base type.

Does the first one add enough useful information about the pattern that it's worth keeping some aspect of it?
Perhaps all you need is "tagging classes" like this:

    class Obstacle: pass
    class Character: pass
    class GameElementFactory: pass

Then the inheritance serves only to indicate the type of the derived classes.

## Exercises

1.  Add a class `Triangle` to `shape_factory1.py`
2.  Add a class `Triangle` to `shape_factory2.py`
3.  Add a new type of `GameEnvironment` called `GnomesAndFairies` to `games.py`
4.  Modify `shape_factory2.py` so that it uses an *Abstract Factory* to create different sets of shapes (for example, one particular type of factory object creates "thick shapes," another creates "thin shapes," but each factory object can create all the shapes: circles, squares, triangles etc.).
