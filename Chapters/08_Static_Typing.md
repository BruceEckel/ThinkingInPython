# Static Typing

C++ and Java require type declarations,
and they check those types during compilation.
The Python runtime checks types only when an operation is actually attempted.
The examples up to this point have no type declarations,
which you might not miss on small programs.

Python 3.5 (2015) introduced *type hints*,
which look like static type checking in other languages.
The Python runtime ignores type hints, as long as they are properly formed.
If you want static type checking like you get from a compiler in a typed language,
you must run a separate type-checking tool (this book uses [Astral's `ty`](https://docs.astral.sh/ty/)).

## Gradual Typing

You can add type hints one function at a time.
Code without annotations still works.
The checker treats it as the type `Any`, which is compatible with everything.
Thus, typed and untyped code can coexist.
This is *gradual typing*.
You can slowly add hints where they earn their keep: the public interfaces,
the tricky data, the code on which other people depend.
An explicit `Any` indicates that a value is truly dynamic.

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

Marking a value `Final` catches accidental reassignments during type checking.

The naming convention shown earlier used ALL_CAPS to signal a constant,
but that is only a hint to human readers.
At runtime, a `Final` is still a variable,
but attempts to reassign it produce type-checking errors:

```python
# final_constants.py
from typing import Final

MAX_RETRIES: Final = 3
GREETING: Final[str] = "hello"

# MAX_RETRIES = 5  # ty: cannot assign to final name "MAX_RETRIES"

print(MAX_RETRIES, GREETING)
#: 3 hello
```

You can give the type explicitly, as in `GREETING`,
or let the checker infer it from the value, as with `MAX_RETRIES`.

## The Checker: `ty`

The hints do nothing on their own.
You need a tool to check them.
This book uses [`ty`](https://github.com/astral-sh/ty), Astral's fast checker:

    ty check

It complains where the hints and the code disagree,
and is quiet when they agree.
This book checks every runnable example this way.
The build runs `ty` on every change,
so the code you read here checks as well as runs.

## Catching Mistakes

Type checking discovers mistakes before the program runs.
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
It returns `"3333"`,
because `"3" * 4` is the correct syntax for string repetition.
The bug surfaces later, often far from the line that caused it.
The checker immediately discovers the problem.

The `# type: ignore` comment tells the type checker to skip this line,
which allows this book's build to complete successfully.

## Structural Typing with Protocols

Earlier chapters relied on *dynamic typing*.
A function accepts any object,
and the only requirement is that the object supports the operations performed on it.
Python checks the type at runtime, when the operation runs.
Programmers often call dynamic typing *duck typing*.
If it looks like a duck and quacks like a duck, treat it as a duck.

*Structural typing* is the static counterpart.
Instead of waiting until the program is running,
a type checker verifies ahead of time that an object has the required *shape*.
"Shape" means the methods and attributes required by that type's consumer.
Dynamic typing and structural typing are the same idea checked at different moments.
Dynamic typing trusts the object when the code runs.
Structural typing proves the shape before the code runs.

A *Protocol* expresses shape.
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
The checker accepts both because each has a `draw()`,
so they are of the right shape.

`Drawable` only becomes involved when defining `render()`.
If you pass an object without a `draw()` to `render()`, `ty` rejects it.
Protocols preserve the flexibility of dynamic typing but add the early warning of static type checking.

## Classes as Values: `type[C]` {#classes-as-values-type}

A class is also a value.
You can pass it to a function, store it in a variable,
and call it to make an instance.
This means an annotation needs a way to distinguish the class from an instance of that class.

A plain `SomeType` annotation means an *instance* of `SomeType`.
The form `type[SomeType]` means the class object, or any subclass of it.
`type[C]` annotates the class, not an instance:

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

`make()` takes the class, not an instance,
so the argument's annotation is `type[Shape]`.
Passing `Circle` works because `Circle` is a subclass of `Shape`.
Calling `kind()` then produces an instance.
This is the construct functions like `issubclass()` work with,
since they compare classes rather than instances.

## Naming Types: The `type` Statement {#the-type-statement}

An annotation can grow to the point of obscurity.
`dict[tuple[int, int], str]` is precise, but it does not say what it means.
The *type statement* gives the annotation a name:

```python
# type_aliases.py
from typing import Literal

type Coord = tuple[int, int]
type Grid = dict[Coord, str]
type Color = Literal["red", "blue", "green", "yellow"]

def paint(grid: Grid, cell: Coord, color: Color) -> None:
    grid[cell] = color

grid: Grid = {}
paint(grid, (2, 3), "red")
print(grid)
#: {(2, 3): 'red'}
```

A `type` alias is a new name, not a new type.
`Coord` and `tuple[int, int]` are interchangeable,
so the checker accepts any pair of ints as a `Coord`.
(To create a distinct type the checker keeps separate, use `NewType`, listed in the summary below.)

`Color` names a union of literal values instead of a union of types.
`Literal["red", "blue", "green", "yellow"]` restricts the parameter to those four strings and no others.
Passing `"purple"` to `paint()` is a type error,
even though `"purple"` is a valid `str`.
The alias also documents the allowed values in one place,
instead of scattering the literal list across every function that accepts a `Color`.

An alias can also name a union of types.
[Pattern Matching](13_Pattern_Matching.md#exhaustive-matching) uses `type Shape = Circle | Square` to define a closed set of alternatives that a `match` can check exhaustively.

## Generic Functions and Classes {#generic-functions-and-classes}

Consider a function that returns the first element of a list.
This function can be applied to a list holding any type.
A useful annotation would return a type that matches the list's element type,
whatever that type is.

`Any` cannot express that connection.
It accepts any list,
but the returned value doesn't express the type held by the list.

A *type parameter* correctly specifies the returned type.
The type held by the list is the type the function returns.
Declare the parameter in square brackets after the function name:

```python
# generics.py

def first[T](items: list[T]) -> T:
    return items[0]

n = first([10, 20, 30])  # T is int
print(n + 1)
#: 11
s = first(["a", "b"])    # T is str
print(s.upper())
#: A
```

`T` is a placeholder, filled in separately at each call.
The checker infers `T` from the argument and then knows the return type.
Both `n + 1` and `s.upper()` are successful,
while `n.upper()` would fail the type check.

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

A special form, `**P`, captures the types of an entire parameter list.
[Decorators](14_Decorators.md#maintaining-the-wrapped-interface) uses this to give a wrapper the same signature as the function it wraps.

Before Python 3.12 you wrote type parameters with `TypeVar` and `Generic`,
which you will still see in older code.

## The `Self` Return Type {#the-self-type}

A method that returns its own instance allows call chaining.
What should the type annotation be?
Naming the enclosing class works until someone inherits from it.
`Self` means "an instance of the class you called this method on,"
so it automatically adapts to subclassing:

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
A wrong type that slips past the checker behaves as it would have without hints.
Checking is a separate step you run, the same way you run tests separately.
If you need a runtime guarantee,
use `isinstance()` or a library built to validate data.
The [typeguard](https://typeguard.readthedocs.io) library reads your existing annotations and enforces them at runtime.
[Pydantic](https://docs.pydantic.dev) validates and parses data against typed models,
which is useful at the edges of a program where untrusted input enters.
The hints themselves are for the tools and for the reader.

## Type Hint Summary

These are the type hints you will encounter, in their modern forms.
The book uses only a handful of these, but the rest turn up in other code.
Each subsection heading links to the associated [Python documentation](https://docs.python.org/3/library/typing.html).
[Thinking in Types](https://thinkingintypes.com/) explores types in more depth.

Annotations go in three places: a parameter (`x: int`),
a return value (`-> str`), and a variable or attribute (`total: int = 0`).
Most of the names below come from the `typing` module.
The abstract container types come from `collections.abc`.

<!-- Section headers link out to docs.python.org in a new tab. Safe only
     because CHAPTER_TOC_DEPTH (build_site.py) stops the in-page TOC at
     "##"; raising it to 3 would nest an <a> inside the TOC's own <a>
     for every "###" heading below and break those TOC entries. -->

### <a href="https://docs.python.org/3/library/stdtypes.html#built-in-types" target="_blank" rel="noopener">Basic types</a>

| Construct | Meaning |
|-----------|---------|
| `int`, `str`, `float`, `bool`, `bytes`, `complex` | The built-in types, annotated by name alone, with no type parameter |
| `None` | The value `None`; the return type of a function that returns nothing |
| `object` | Any object, but with no behavior assumed (safer than `Any`) |
| `Any` | Opts out of checking; compatible with every type, see [Gradual Typing](#gradual-typing) |
| `Never`, `NoReturn` | `NoReturn` marks a function that never returns (it always raises or exits); `Never` is the broader "impossible" type |
| `LiteralString` | A `str` built only from literals, for injection-sensitive APIs |

### <a href="https://docs.python.org/3/library/stdtypes.html#generic-alias-type" target="_blank" rel="noopener">Containers</a>

| Construct | Meaning |
|-----------|---------|
| `list[T]`, `set[T]`, `frozenset[T]` | A homogeneous collection of `T`; *invariant*, so `list[Circle]` is not a `list[Shape]`, see [Type Hints](#type-hints) |
| `dict[K, V]` | A dictionary with keys `K` and values `V`, see [Type Hints](#type-hints) |
| `tuple[A, B]` | A fixed-length tuple (here a pair), see [Type Hints](#type-hints) |
| `tuple[T, ...]` | A variable-length tuple of `T`, see [Type Hints](#type-hints) |
| `Sequence[T]`, `Iterable[T]`, `Iterator[T]`, `Mapping[K, V]` | Read-only abstract shapes from `collections.abc`; *covariant* in their element type, so `list[Circle]` satisfies `Sequence[Shape]` (`Mapping[K, V]`'s `K` stays invariant), see [Iterators](23_Iterators.md#iteration-is-built-in) |
| `Callable[[A, B], R]` | A function taking `A`, `B` and returning `R` (`...` for any parameters) |
| `type[C]` | The class object `C` is not an instance, see [Classes as Values](#classes-as-values-type) |

### <a href="https://docs.python.org/3/library/typing.html#typing.Union" target="_blank" rel="noopener">Unions, optionals, and literals</a>

| Construct | Meaning |
|-----------|---------|
| `X` \| `Y` | A *union*: either type, see [Type Hints](#type-hints) |
| `X` \| `None` | *Optional*: `X` or `None`, see [Type Hints](#type-hints) |
| `Literal[...]` | One of a fixed set of constant values, e.g. `Literal["r", "w"]`, see [The `type` Statement](#the-type-statement) |

### <a href="https://docs.python.org/3/library/typing.html#type-aliases" target="_blank" rel="noopener">Aliases and distinct types</a>

| Construct | Meaning |
|-----------|---------|
| `type Name = ...` | A *type alias* for a longer type, e.g. `type Grid = dict[tuple[int, int], str]`, see [The `type` Statement](#the-type-statement) |
| `NewType("Id", int)` | A distinct type, `int` at runtime but separate to the checker; the base can be any class, not just a builtin |
| `Annotated[T, meta]` | `T` carrying extra metadata for libraries and tools |

### <a href="https://docs.python.org/3/library/typing.html#typing.Final" target="_blank" rel="noopener">Constants and class variables</a>

| Construct | Meaning |
|-----------|---------|
| `Final`, `Final[T]` | A name the checker will not let you reassign, see [Constants with Final](#constants-with-final) |
| `ClassVar[T]` | A class-level attribute, not one per instance, see [Class Attributes](09_Class_Attributes.md#class-attributes-are-not-default-values) |

### <a href="https://docs.python.org/3/library/typing.html#generics" target="_blank" rel="noopener">Generics</a>

| Construct | Meaning |
|-----------|---------|
| `def f[T](x: T) -> T` | A generic function (the type parameter varies per call), see [Generic Functions and Classes](#generic-functions-and-classes) |
| `class Box[T]` | A generic class, see [Generic Functions and Classes](#generic-functions-and-classes) |
| `[T: Base]`, `[T: (int, str)]` | A bounded or constrained type parameter, see [Generic Functions and Classes](#generic-functions-and-classes) |
| `TypeVar`, `Generic[T]` | The pre-3.12 way to write type parameters, see [Generic Functions and Classes](#generic-functions-and-classes) |
| `**P` (`ParamSpec`) | Captures a callable's parameter list including types, for decorators, see [Decorators](14_Decorators.md#maintaining-the-wrapped-interface) |
| `*Ts` (`TypeVarTuple`), `Unpack`, `Concatenate` | Variadic generics and parameter manipulation |

### <a href="https://docs.python.org/3/library/typing.html#protocols" target="_blank" rel="noopener">Structural typing</a>

| Construct | Meaning |
|-----------|---------|
| `Protocol` | A required shape (methods and attributes), satisfied without inheritance, see [Structural Typing with Protocols](#structural-typing-with-protocols) |
| `@runtime_checkable` | Allows `isinstance()` against a `Protocol`, see [Surrogate](26_Surrogate.md#proxy) |

### <a href="https://docs.python.org/3/library/typing.html#typing.TypedDict" target="_blank" rel="noopener">Dictionary and record shapes</a>

| Construct | Meaning |
|-----------|---------|
| `TypedDict` | A dict with specific keys and value types |
| `Required[...]`, `NotRequired[...]`, `ReadOnly[...]` | Per-key control inside a `TypedDict` |
| `NamedTuple` | A typed, named tuple class, see [Data Transfer Objects](22_Data_Transfer_Objects.md#the-standard-library-versions) |

### <a href="https://docs.python.org/3/library/typing.html#typing.TypeGuard" target="_blank" rel="noopener">Type narrowing</a>

| Construct | Meaning |
|-----------|---------|
| `TypeGuard[T]`, `TypeIs[T]` | A boolean predicate that narrows a type when it returns `True` |

### <a href="https://docs.python.org/3/library/typing.html#typing.Self" target="_blank" rel="noopener">Self and forward references</a>

| Construct | Meaning |
|-----------|---------|
| `Self` | The enclosing class type; useful for fluent methods and alternative constructors, see [The `Self` Return Type](#the-self-type) |
| `"Name"` | A *forward reference* to a not-yet-defined type; quoting is optional under deferred evaluation (PEP 649), see [Simulation](38_Simulation.md#a-robot-in-a-maze) |

### <a href="https://docs.python.org/3/library/typing.html#functions-and-decorators" target="_blank" rel="noopener">Typing decorators and directives</a>

| Construct | Meaning |
|-----------|---------|
| `@overload` | Several typed signatures for one function name |
| `@override` | Declares that a method overrides a base-class method, see [Classes](07_Classes.md#marking-overrides-with-override) |
| `@final` | Forbids subclassing the class, or overriding the method, see [Metaprogramming](17_Metaprogramming.md#making-a-class-final) |
| `cast(T, x)` | Tells the checker to treat `x` as `T`, see [Flyweight](35_Flyweight.md#intrinsic-and-extrinsic-state) |
| `assert_never(x)`, `assert_type(x, T)`, `reveal_type(x)` | Checker assertions and aids; `assert_never()` shown in [Pattern Matching](13_Pattern_Matching.md#exhaustive-matching) |
| `TYPE_CHECKING` | A flag that is `True` only to the checker, for type-only imports, see [Simulation](38_Simulation.md#a-robot-in-a-maze) |

The runtime ignores all of these.
They exist for the checker and the reader.
Older code spells some of them differently: `Optional[X]` for `X | None`,
`Union[X, Y]` for `X | Y`, and `List`, `Dict`, `Set`,
`Tuple` from `typing` for the lowercase built-ins.
The forms above are the modern ones.

## Exercises

1.  In `protocols.py`, add a class `Triangle` with its own `draw()`,
    and pass an instance to `render()` without changing `Drawable` or `render()`.
2.  In `area.py`, remove the `# type: ignore` comment and run `ty check` on the file.
    Read the error, then restore the comment.
3.  In `generics.py`, write a second generic function,
    `last[T](items: list[T]) -> T`, that returns the final element,
    and call it on both a `list[int]` and a `list[str]` the way `first()` is called.
4.  In `self_type.py`, add a subclass of `NamedTally` called `LoudTally` whose `report()` returns the message in all capitals,
    calling `super().report()` first.
    Confirm `.bump().bump().report()` still chains correctly on a `LoudTally`.
