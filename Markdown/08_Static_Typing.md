# Static Typing

C++ and Java make you declare the type of everything,
and they check those types before the program runs.
Python checks types at runtime, only when an operation is actually attempted.
Up until this chapter, we haven't used type declarations.

On a small program you do not miss the declarations.
On a large program, type errors that C++ or Java would catch now appear only when the code runs.
Sometimes the error waits until a bug report.

Python 3.5 (2015) introduced *type hints*, which look like static type checking in other languages.
The Python runtime ignores properly formed type hints.
If you want the equivalent of a compiler in a typed language,
you must run a separate type-checking tool (this book uses Astral's `ty`).

You can put type hints on some elements and not others, so you can opt in only as much as it pays off.

## Type Hints

A hint annotates a parameter, a return value, or a variable.
Use a colon for parameters and variables, and an arrow for the return type:

```python
# typed_basics.py

def repeat(text: str, times: int) -> str:
    return text * times

print(repeat("ab", 3))
#: ababab

total: int = 0
for word in ["a", "bb", "ccc"]:
    total += len(word)

print(total)
#: 6
```

Containers and optional types read the way you say them: `list[int]`,
`dict[str, float]`, `tuple[int, ...]`,
and `str | None` for "a string or nothing."

## Constants with Final

The naming convention shown earlier used ALL_CAPS to signal a constant,
but that is only a hint to human readers.
`Final` makes it a hint the type checker enforces.
If you reassign a `Final`, the checker reports it,
even though the Python runtime allows the assignment.

```python
# final_constants.py
from typing import Final

MAX_RETRIES: Final = 3
GREETING: Final[str] = "hello"

# MAX_RETRIES = 5  # ty: cannot assign to final name "MAX_RETRIES"

print(MAX_RETRIES, GREETING)
#: 3 hello
```

You can give the type explicitly, as in `Final[str]`,
or let the checker infer it from the value, as with `MAX_RETRIES`.
Marking values `Final` catches accidental reassignments immediately.

## Gradual Typing

You can add hints one function at a time; the unannotated code keeps working.
The checker treats whatever it cannot see as the type `Any`,
which is compatible with everything, so typed and untyped code live together.
This is *gradual typing*.
You can slowly add hints where they earn their keep: the public interfaces,
the tricky data, the code on which other people depend.
When a value is truly dynamic, `Any` shows that you mean it to be.

## The Checker: `ty`

The hints do nothing on their own.
You need a tool to check them.
This book uses [`ty`](https://github.com/astral-sh/ty), Astral's fast checker:

    ty check

It complains where the hints and the code disagree, and is quiet when they agree.
This book checks every runnable example this way.
The build runs `ty` on every change, so the code you read here checks as well as runs.

## Catching Mistakes

The goal is to discover mistakes before the program runs.
Consider:

```python
# area.py
def area(width: int, height: int) -> int:
    return width * height

# ty: argument of type "str" is not assignable to "int":
print(area("3", 4))  # type: ignore
#: 3333
```

At runtime `area("3", 4)` does not cause an error.
It returns `"3333"`, because `"3" * 4` is the correct syntax for string repetition.
The bug surfaces later, often far from the line that caused it.
The checker immediately discovers the problem.

The `# type: ignore` comment tells the type checker to skip this line,
which allows this book's build to complete successfully.

## Structural Typing with Protocols

Earlier chapters relied on *dynamic typing*. A function accepts any object,
and the only requirement is that the object supports the operations performed on it.
Python checks the type at runtime, when the operation runs.
Programmers often call dynamic typing *duck typing*.
If it looks like a duck and quacks like a duck, treat it as a duck.

*Structural typing* is the static counterpart.
Instead of waiting until the program is running,
a type checker verifies ahead of time that an object has the required *shape*,
which means the methods and attributes required by whatever consumes that type.
Dynamic typing and structural typing are the same idea checked at different moments.
Dynamic typing trusts the object when the code runs;
structural typing proves the shape before the code runs.

A *Protocol* expresses that shape.
Some statically typed languages make you declare up front that a class "is a" `Drawable` by inheriting from it.
A `Protocol` instead describes a required shape.
Any object with that shape qualifies, without inheriting from a base class:

```python
# protocols.py
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> str: ...

class Circle:
    def draw(self) -> str:
        return "circle"

class Square:
    def draw(self) -> str:
        return "square"

def render(shape: Drawable) -> str:   # Accepts anything with draw()
    return shape.draw()

print(render(Circle()))
#: circle
print(render(Square()))
#: square
```

`Circle` and `Square` never mention `Drawable`.
The checker accepts both because each has a `draw()`, so they are of the right shape.
If you pass an object without a `draw()` to `render()`, `ty` rejects it.
Python preserves the flexibility of dynamic typing but gains the early warning of static types.

## Classes as Values: `type[...]` {#classes-as-values-type}

A class is itself a value.
You can pass it to a function, store it in a variable, and call it to make an instance.
So an annotation needs a way to distinguish the class from an instance of that class.
A plain `SomeType` annotation means an *instance* of `SomeType`.
The form `type[SomeType]` means the class object itself, or any subclass of it.
So `type[C]` annotates the class, not an instance:

```python
# class_values.py

class Shape:
    pass

class Circle(Shape):
    pass

def make(kind: type[Shape]) -> Shape:
    return kind()  # Instantiate the class

shape = make(Circle)
print(type(shape).__name__)
#: Circle
```

`make()` takes the class, not an instance, so the argument's annotation is `type[Shape]`.
Passing `Circle` works because `Circle` is a subclass of `Shape`.
Calling `kind()` then produces an instance.
This is the construct functions like `issubclass()` work with, since they compare classes rather than instances.

## Naming Types: The `type` Statement {#the-type-statement}

An annotation can grow until it obscures what it means.
`dict[tuple[int, int], str]` is precise, but it does not say what it means.
The *type statement* gives the annotation a name:

```python
# type_aliases.py
type Coord = tuple[int, int]
type Grid = dict[Coord, str]

def paint(grid: Grid, cell: Coord, color: str) -> None:
    grid[cell] = color

grid: Grid = {}
paint(grid, (2, 3), "red")
print(grid)
#: {(2, 3): 'red'}
```

A `type` alias is a new name, not a new type.
`Coord` and `tuple[int, int]` are interchangeable,
so the checker accepts any pair of ints as a `Coord`.
(To create a distinct type the checker keeps separate,
use `NewType`, listed in the summary below.)
An alias can also name a union.
[Pattern Matching](13_Pattern_Matching.md#exhaustive-matching) writes
`type Shape = Circle | Square` to define a closed set of alternatives
that a `match` can check exhaustively.

## Generic Functions and Classes {#generic-functions-and-classes}

A function that returns the first element of a list works for any element type.
The type that goes in is the type that comes out.
An annotation of `Any` would accept everything but lose that connection.
A *type parameter* keeps it.
Declare the parameter in square brackets after the function name:

```python
# generics.py

def first[T](items: list[T]) -> T:
    return items[0]

n = first([10, 20, 30])  # Here T is int
print(n + 1)
#: 11
s = first(["a", "b"])    # Here T is str
print(s.upper())
#: A
```

`T` is a placeholder, filled in separately at each call.
The checker infers `T` from the argument and then knows the return type.
That is why both `n + 1` and `s.upper()` check, while `n.upper()` would not.

A class declares type parameters the same way:

```python
# generic_box.py

class Box[T]:
    def __init__(self, content: T) -> None:
        self.content = content

    def get(self) -> T:
        return self.content

box = Box("gift")  # A Box[str]
print(box.get().upper())
#: GIFT
```

Constructing `Box("gift")` fixes `T` to `str` for that instance,
so `get()` returns a `str` and the call to `upper()` checks.
A bound constrains the parameter.
`class Box[T: Shape]` accepts only `Shape` and its subclasses.
Before Python 3.12 you wrote type parameters with `TypeVar` and `Generic`,
which you will still see in older code.
A special form, `**P`, captures a whole parameter list.
[Decorators](15_Decorators.md#maintaining-the-wrapped-interface) uses it
to give a wrapper the same signature as the function it wraps.

## The `Self` Return Type {#the-self-type}

A method that returns its own instance lets calls chain.
What should its return annotation be?
Naming the enclosing class works until someone inherits from it.
`Self` means "an instance of the class you called this method on,"
so it follows subclasses:

```python
# self_type.py
from typing import Self

class Tally:
    def __init__(self) -> None:
        self.count = 0

    def bump(self) -> Self:
        self.count += 1
        return self

class NamedTally(Tally):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def report(self) -> str:
        return f"{self.name}: {self.count}"

t = NamedTally("clicks")
print(t.bump().bump().report())
#: clicks: 2
```

`t.bump()` runs on a `NamedTally`, so `Self` is `NamedTally`,
and `report()` is available on the result.
Had `bump()` declared `-> Tally`, the checker would reject `report()`,
which `Tally` does not have.
Alternative constructors benefit the same way.
A `@classmethod` that ends with `return cls(...)` returns `Self`.

## Hints Are Not Enforced at Run Time

Type hints do not change what the program does.
Python stores them and otherwise ignores them.
A wrong type that slips past the checker behaves exactly as it would have with no hints at all.
Checking is a separate step you run, the same way you run tests separately.
If you need a runtime guarantee, use `isinstance()` or a library built to validate data.
The [typeguard](https://typeguard.readthedocs.io) library reads your existing annotations and enforces them at runtime.
[Pydantic](https://docs.pydantic.dev) validates and parses data against typed models,
which is useful at the edges of a program where untrusted input comes in.
The hints themselves are for the tools and for the reader.

## Type Hint Summary

These are the type hints you will encounter, in their modern spelling.
The book uses only a handful of these, but the rest turn up in other code;
check [the Python documentation](https://docs.python.org/3/library/typing.html) or [Thinking in Types](https://thinkingintypes.com/) if one piques your interest.

Annotations go in three places: a parameter (`x: int`), a return value (`-> str`),
and a variable or attribute (`total: int = 0`).
Most of the names below come from the `typing` module; the abstract container
shapes come from `collections.abc`.

### Basic types

| Construct | Meaning |
|-----------|---------|
| `int`, `str`, `float`, `bool`, `bytes`, `complex` | The built-in scalar types |
| `None` | The value `None`; the return type of a function that returns nothing |
| `object` | Any object, but with no behavior assumed (safer than `Any`) |
| `Any` | Opts out of checking; compatible with every type |
| `Never`, `NoReturn` | A function that never returns (it always raises or exits) |
| `LiteralString` | A `str` built only from literals, for injection-sensitive APIs |

### Containers

| Construct | Meaning |
|-----------|---------|
| `list[T]`, `set[T]`, `frozenset[T]` | A homogeneous collection of `T` |
| `dict[K, V]` | A dictionary with keys `K` and values `V` |
| `tuple[A, B]` | A fixed-length tuple (here a pair) |
| `tuple[T, ...]` | A variable-length tuple of `T` |
| `Sequence[T]`, `Iterable[T]`, `Iterator[T]`, `Mapping[K, V]` | Abstract shapes from `collections.abc`; accept more inputs than the concrete types |
| `Callable[[A, B], R]` | A function taking `A`, `B` and returning `R` (`...` for any parameters) |
| `type[C]` | The class object `C` itself, not an instance |

### Unions, optionals, and literals

| Construct | Meaning |
|-----------|---------|
| `X` \| `Y` | A *union*: either type |
| `X` \| `None` | *Optional*: `X` or `None` |
| `Literal[...]` | One of a fixed set of constant values, e.g. `Literal["r", "w"]` |

### Aliases and distinct types

| Construct | Meaning |
|-----------|---------|
| `type Name = ...` | A *type alias* for a longer type, e.g. `type Grid = dict[tuple[int, int], str]` |
| `NewType("Id", int)` | A distinct type that is `int` at runtime but separate to the checker |
| `Annotated[T, meta]` | `T` carrying extra metadata for libraries and tools |

### Constants and class variables

| Construct | Meaning |
|-----------|---------|
| `Final`, `Final[T]` | A name the checker will not let you reassign |
| `ClassVar[T]` | A class-level attribute, not one per instance |

### Generics

| Construct | Meaning |
|-----------|---------|
| `def f[T](x: T) -> T` | A generic function (the type parameter varies per call) |
| `class Box[T]` | A generic class |
| `[T: Base]`, `[T: (int, str)]` | A bounded or constrained type parameter |
| `TypeVar`, `Generic[T]` | The pre-3.12 way to write the two above |
| `**P` (`ParamSpec`) | Captures a callable's whole parameter list, for decorators |
| `*Ts` (`TypeVarTuple`), `Unpack`, `Concatenate` | Variadic generics and parameter manipulation |

### Structural typing

| Construct | Meaning |
|-----------|---------|
| `Protocol` | A required shape (methods and attributes), satisfied without inheritance |
| `@runtime_checkable` | Allows `isinstance()` against a `Protocol` |

### Dictionary and record shapes

| Construct | Meaning |
|-----------|---------|
| `TypedDict` | A dict with specific keys and value types |
| `Required[...]`, `NotRequired[...]`, `ReadOnly[...]` | Per-key control inside a `TypedDict` |
| `NamedTuple` | A typed, named tuple class |

### Type narrowing

| Construct | Meaning |
|-----------|---------|
| `TypeGuard[T]`, `TypeIs[T]` | A boolean predicate that narrows a type when it returns `True` |

### Self and forward references

| Construct | Meaning |
|-----------|---------|
| `Self` | The enclosing class type; handy for fluent methods and alternative constructors |
| `"Name"` | A *forward reference*: a not-yet-defined type, written as a string |

### Typing decorators and directives

| Construct | Meaning |
|-----------|---------|
| `@overload` | Several typed signatures for one function |
| `@override` | Declares a method overrides a base-class method, see [Classes](07_Classes.md#marking-overrides-with-override) |
| `@final` | Forbids subclassing the class, or overriding the method |
| `cast(T, x)` | Tells the checker to treat `x` as `T` |
| `assert_never(x)`, `assert_type(x, T)`, `reveal_type(x)` | Checker assertions and aids |
| `TYPE_CHECKING` | A flag that is `True` only to the checker, for type-only imports |

The runtime ignores all of these; they exist for the checker and the reader.
Older code spells some of them differently: `Optional[X]` for `X | None`,
`Union[X, Y]` for `X | Y`, and `List`, `Dict`, `Set`, `Tuple` from `typing` for
the lowercase built-ins. The forms above are the modern ones.
