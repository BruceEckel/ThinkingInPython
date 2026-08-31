# Static Types

C++ and Java require type declarations,
and they check those types during compilation.
The Python runtime checks types only when an operation runs.
The examples up to this point have gone almost entirely without type declarations,
which you might not miss on small programs.

Python 3.5 (2015) introduced *type hints*,
which look like the type declarations of statically typed languages.
The Python runtime ignores type hints.
It evaluates them only when something asks for them.
If you want static type checking like you get from a compiler in a typed language,
you must run a separate type-checking tool
(this book uses [Astral's `ty`](https://docs.astral.sh/ty/)).

## Gradual Typing

You can add type hints one function at a time.
Code without annotations still works.
The type checker treats it as the type `Any`,
which is compatible with everything.
Thus, typed and untyped code can coexist.
This is *gradual typing*.
You can slowly add hints where they earn their keep: the public interfaces,
the tricky data, the code on which other people depend.
An explicit `Any` indicates that a value is truly dynamic.
`ty` reports the `Any` that comes from a missing annotation as `Unknown`,
to distinguish it from an `Any` you wrote yourself.
They behave the same: both are compatible with everything.

`Any` is not the same as `object`.
Both accept every value,
but `object` guarantees nothing about the value once you have it,
so the type checker rejects every operation you try on it.
`Any` accepts every value and then permits every operation,
which makes it an opt-out rather than a wide type.

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
A function that returns nothing declares `-> None`,
which is why every `__init__()` in this chapter's listings ends that way.

## The Type Checker: `ty`

The hints do nothing on their own.
You need a tool to check them:

    ty check

`uvx ty check` runs it without installing anything,
and `uv tool install ty@latest` puts it on your path.

It complains where the hints and the code disagree,
and stays quiet when they agree.
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

At runtime `area("3", 4)` runs without error.
It returns `"3333"`, because `"3" * 4` repeats the string four times.
The bug surfaces later, often far from the line that caused it.
The type checker discovers the problem immediately.

The `# type: ignore` comment tells the type checker to skip this line,
so this book's build passes.
Without it, `ty check` reports:

```
error[invalid-argument-type]: Argument to function `area` is incorrect
 --> area.py:6:12
  |
6 | print(area("3", 4))
  |            ^^^ Expected `int`, found `Literal["3"]`
info: Function defined here
 --> area.py:2:5
  |
2 | def area(width: int, height: int) -> int:
  |     ^^^^ ---------- Parameter declared here
```

A diagnostic names the rule in brackets, points at the offending line,
pairs what the annotation expected with what the call supplied,
and then points at the declaration that set the expectation.

Listings in this book use a shorthand for a diagnostic.
Where a line would fail the check,
whether commented out or suppressed with `# type: ignore`,
a neighboring `# ty:` comment summarizes what the type checker reports for it.

## Narrowing {#narrowing}

A union type covers every case until you rule some out.
Testing `is not None` on an `X | None` value proves it to the type checker,
not just to you:

```python
# narrowing.py

def shout(text: str | None) -> str:
    if text is not None:
        return text.upper()
    return "(nothing)"

print(shout("hi"))
#: HI
print(shout(None))
#: (nothing)
```

Inside the `if`, the type checker *narrows* `text` from `str | None` to `str`,
so `.upper()` needs no cast.
Outside the `if`, `text` is still the full `str | None`.
The same narrowing follows an `isinstance()` check, an equality test,
or an identity test against a specific value such as `is not SOME_SENTINEL`.

## Constants with Final

Marking a value `Final` catches accidental reassignments during type checking.

The naming convention in [Tour](02_Tour.md#naming-conventions)
uses ALL_CAPS to signal a constant, but that is only a hint to human readers.
At runtime, a `Final` is still a variable,
but reassigning it produces a type-checking error:

```python
# final_constants.py
from typing import Final

MAX_RETRIES: Final = 3
GREETING: Final[str] = "hello"

# ty: cannot assign to final name "MAX_RETRIES":
# MAX_RETRIES = 5

print(MAX_RETRIES, GREETING)
#: 3 hello
```

`Final` blocks rebinding the name, not mutation of the object the name holds.
You can still append to a `Final[list[str]]`.
The type checker refuses only an assignment to the name.

You can give the type explicitly, as in `GREETING`,
or let the type checker infer it from the value, as with `MAX_RETRIES`.
The rest of the book uses the explicit `Final[T]` form,
which declares the intended type instead of accepting whatever the initializer produces.
The difference emerges when the initializer's own type is not the type you mean.
`CACHE: Final = []` infers `list[Unknown]`,
so the type checker ignores whatever goes into the list.
`CACHE: Final[list[str]] = []` says what the list holds,
and the type checker enforces it.

## Structural Typing with Protocols

Earlier chapters relied on *dynamic typing*.
A function accepts any object,
so long as the object supports the operations the function performs on it.
Python checks the type at runtime, when the operation runs.
Programmers often call dynamic typing *duck typing*.
If it looks like a duck and quacks like a duck, treat it as a duck.

*Structural typing* is the static counterpart.
Instead of waiting until the program is running,
a type checker verifies ahead of time that an object has the required *shape*.
"Shape" means the methods and attributes that the type's consumer requires.
Dynamic typing and structural typing are the same idea checked at different moments.
Dynamic typing trusts the object once the code is running,
while structural typing proves the shape beforehand.

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

def render(shape: Drawable) -> str:
    return shape.draw()

class Blob:
    def paint(self) -> str:
        return "blob"

print(render(Circle()))
#: circle
print(render(Square()))
#: square
# ty: expected "Drawable", found "Blob":
# render(Blob())
```

`Circle` and `Square` never mention `Drawable`.
The type checker accepts both because each has a `draw()` that takes no arguments and returns a `str`,
so each matches `Drawable`'s shape.
The signature is part of that shape: a `draw()` that returns an `int`,
or that requires an argument, does not match.
A `Protocol` is a checking-time construct,
so `isinstance(Circle(), Drawable)` raises a `TypeError` instead of answering.
Decorating the Protocol with `@runtime_checkable` allows the call,
at the cost of a weaker check: see [Surrogate](26_Surrogate.md#proxy).

`Drawable` appears only in `render()`'s definition.
If you pass an object without a `draw()` to `render()`, `ty` rejects it.
`Blob` is the case worth watching: it draws, in the everyday sense,
but the method's name is `paint()`,
and a protocol matches on names and signatures rather than on intent.
Protocols preserve the flexibility of dynamic typing but add the early warning of static type checking.

## Classes as Values: `type[C]` {#classes-as-values-type}

A class is also a value, so you can pass it to a function,
store it in a variable, and call it to make an instance.
An annotation needs a way to distinguish the class from an instance of that class.

A plain `SomeType` annotation means an instance of `SomeType`.
The form `type[SomeType]` means the class object, or any subclass of it:

```python
# class_values.py

class Shape:
    pass

class Circle(Shape):
    pass

def make(kind: type[Shape]) -> Shape:
    return kind()

shape = make(Circle)
print(type(shape).__name__)
#: Circle
```

`make()` takes the class, not an instance,
so the argument's annotation is `type[Shape]`.
Passing `Circle` works because `Circle` is a subclass of `Shape`.
Calling `kind()` then produces an instance.
The word `type` plays two roles in this listing:
the annotation `type[Shape]` names the class to the type checker,
while the builtin call `type(shape)` in the demo retrieves an object's class at runtime.

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

Like `match`, `type` is a soft keyword
([Control Flow](04_Control_Flow.md#pattern-matching)):
it is a keyword only at the start of this statement.
Everywhere else, `type` is still the builtin `type()` function,
so `type(grid)` in the same file returns `dict` as it always has.

A `type` alias is a new name, not a new type.
`Coord` and `tuple[int, int]` are interchangeable,
so the type checker accepts any pair of ints as a `Coord`.
(To create a distinct type the type checker keeps separate, use `NewType`, listed in the summary below.)
That is why an alias belongs on a compound shape and not on a bare rename:
`type UserId = int` looks like a new type in a signature while behaving like `int`.

`Color` names a union of literal values instead of a union of types.
`Literal["red", "blue", "green", "yellow"]` restricts the parameter to those four strings.
Passing `"purple"` to `paint()` is a type error,
even though `"purple"` is a valid `str`.
The alias also documents the allowed values in one place,
instead of scattering the literal list across every function that accepts a `Color`.

A `Literal` union is the lightest way to close a set of values.
Once those values need behavior or an identity of their own,
an `Enum` is the better fit.
[Data Classes as Types](12_Data_Classes_as_Types.md#enums-are-types-too)
compares the two.

An alias can also name a union of types.
[Pattern Matching](13_Pattern_Matching.md#exhaustive-matching)
uses `type Shape = Circle | Square` to define a closed set of alternatives that a `match` can check exhaustively.

## Generic Functions and Classes {#generic-functions-and-classes}

Consider a function that returns the first element of a list.
This function works on a list holding any type.
A useful annotation makes the return type match the list's element type,
whatever that type is.

`Any` cannot express that connection.
It accepts any list,
but the return type then says nothing about what the list holds.

A *type parameter* expresses the connection.
Declare the parameter in square brackets after the function name:

```python
# generics.py

def first[T](items: list[T]) -> T:
    return items[0]

n = first([10, 20, 30])  # T is int
print(n + 1)
#: 11
s = first(["a", "b"])  # T is str
print(s.upper())
#: A
```

`T` is a placeholder, filled in separately at each call.
The type checker infers `T` from the argument and then knows the return type.
Both `n + 1` and `s.upper()` pass the type checker, while `n.upper()` fails.

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

### Variance {#variance}

A `list[Circle]` is not a `list[Shape]`,
which surprises most people the first time:

```python
# variance.py
from collections.abc import Sequence

class Shape:
    pass

class Circle(Shape):
    pass

def count(shapes: Sequence[Shape]) -> int:
    return len(shapes)

def add_square(shapes: list[Shape]) -> None:
    shapes.append(Shape())

circles: list[Circle] = [Circle(), Circle()]
print(count(circles))
#: 2
# ty: expected "list[Shape]", found "list[Circle]":
# add_square(circles)
```

A `list` accepts writes.
`add_square()` would append a `Shape` to a list its caller believes holds only circles.
Refusing the call prevents that.
A read-only container has no such problem,
so `Sequence[Shape]` accepts a `list[Circle]`.
Annotating a parameter `Sequence[T]` instead of `list[T]` says the function only reads,
and so accepts more callers.
A `list[T]` is *invariant* in `T`, and a `Sequence[T]` is *covariant*.

### Type Parameter Defaults {#type-parameter-defaults}

A type parameter can carry a default,
which the type checker uses when an annotation names the class without its brackets:

```python
# type_defaults.py

class Stack[T = str]:
    def __init__(self) -> None:
        self.items: list[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def top(self) -> T:
        return self.items[-1]

words: Stack = Stack()  # No brackets, so T is str
words.push("beta")
print(words.top().upper())
#: BETA
counts: Stack[int] = Stack()
counts.push(2)
print(counts.top() + 1)
#: 3
```

Without the default,
`words: Stack` leaves `T` unsolved and the type checker falls back to `Unknown`,
so `words.top().upper()` goes unchecked.
The default gives the bare form a meaning,
which matters most for a class whose parameter has one common answer:
callers content with that answer write nothing,
and the annotation stays precise.

The same applies to a `type` alias, as `Pair` shows:

```python
# alias_default.py

type Pair[T = int] = tuple[T, T]

def is_origin(point: Pair) -> bool:  # Pair means Pair[int]
    return point == (0, 0)

print(is_origin((0, 0)))
#: True
```

Defaulted parameters go last, the way defaulted function parameters do,
so `class Table[K = str, V]` is a syntax error.
Type parameter defaults arrived in Python 3.13,
one release after the bracket syntax.

A special form, `**P`, captures the types of an entire parameter list.
[Decorators](14_Decorators.md#maintaining-the-wrapped-interface)
uses this to give a wrapper the same signature as the function it wraps.

Before Python 3.12 you wrote type parameters with `TypeVar` and `Generic`,
which you still see in older code.

## The `Self` Return Type {#the-self-type}

A method that returns its own instance allows call chaining.
What should the type annotation be?
Naming the enclosing class works until someone inherits from it.
`Self` means "an instance of the class on which you called this method,"
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
and the result has `report()`.
If `bump()` declares `-> Tally`, the type checker rejects `report()`,
which `Tally` does not have.
Alternative constructors benefit the same way.
A `@classmethod` that ends with `return cls(...)` returns `Self`.

## Hints Are Not Enforced at Run Time

Type hints do not change what the program does.
Python stores them and otherwise ignores them.
A wrong type that slips past the type checker behaves as it would have without hints.
Checking is a separate step you run, the same way you run tests.
If you need a runtime guarantee,
use `isinstance()` or a library that validates data.
The [typeguard](https://typeguard.readthedocs.io)
library reads your existing annotations and enforces them at runtime.
[Pydantic](https://docs.pydantic.dev)
validates and parses data against typed models,
which is useful at the edges of a program where untrusted input enters.
The hints are for the tools and for the reader.

From here on, this book assumes the type checker runs on everything.
When a listing says the type checker rejects a line, that is the enforcement.
The following chapters do not repeat that Python itself would run the line anyway.

## How Much to Annotate

Gradual typing leaves the amount up to you,
and the chapter's constructs do not say when each is worth the words.
Annotate what crosses a boundary: function signatures, public attributes,
anything another file imports.
Those are the places where the code's reader and writer are different people,
and where a wrong assumption travels farthest before it fails.

Let the type checker infer the rest.
A local variable whose type is obvious from its initializer gains nothing from an annotation,
and `count: int = 0` says no more than `count = 0` does, at greater length.
(The `total: int = 0` in this chapter's first listing shows the syntax, not a recommendation.)
The value of a hint is proportional to the distance between a value's creation and its use.
A value born and consumed three lines later needs no help.
A value that arrives from another module, through a container,
is worth naming precisely.

## Type Hint Summary

These are the type hints you encounter, in their modern forms.
The book uses only a handful of these, but the rest turn up in other code.
Each subsection heading links to the associated [Python documentation](https://docs.python.org/3/library/typing.html).
[Thinking in Types](https://thinkingintypes.com/) explores types in more depth.

Annotations go in three places: a parameter (`x: int`), a return value
(`-> str`), and a variable or attribute (`total: int = 0`).
Most of the names below come from the `typing` module.
The abstract container types come from `collections.abc`.

<!-- Section headers link out to docs.python.org in a new tab. Safe only
     because CHAPTER_TOC_DEPTH (build_site.py) stops the in-page TOC at
     "##"; raising it to 3 would nest an <a> inside the TOC's own <a>
     for every "###" heading below and break those TOC entries. -->

### <a href="https://docs.python.org/3/library/stdtypes.html#built-in-types" target="_blank" rel="noopener">Basic types</a>

| Construct | Meaning |
|-----------|---------|
| `int`, `str`, `float`, `bool`, `bytes`, `complex` | The built-in types, annotated by name alone, with no type parameter; the type checker accepts an `int` where a declaration says `float`, and an `int` or `float` where it says `complex`, but not the reverse (`bytes` and `complex` do not appear elsewhere in this book) |
| `None` | The value `None`; the return type of a function that returns nothing |
| `object` | Any object, but with no behavior assumed (safer than `Any`) |
| `Any` | Opts out of checking; compatible with every type, see [Gradual Typing](#gradual-typing) |
| `Never`, `NoReturn` | The "impossible" type, which no value has; `NoReturn` marks a function that never returns (it always raises an exception or exits), and `Never` is the same type under a name that also suits other positions |
| `LiteralString` | A `str` built only from literals, for injection-sensitive APIs |

### <a href="https://docs.python.org/3/library/stdtypes.html#generic-alias-type" target="_blank" rel="noopener">Containers</a>

| Construct | Meaning |
|-----------|---------|
| `list[T]`, `set[T]`, `frozenset[T]` | A homogeneous collection of `T`; *invariant*, so `list[Circle]` is not a `list[Shape]`, see [Variance](#variance) |
| `dict[K, V]` | A dictionary with keys `K` and values `V`, see [Type Hints](#type-hints) |
| `tuple[A, B]` | A fixed-length tuple (here a pair), see [Type Hints](#type-hints) |
| `tuple[T, ...]` | A variable-length tuple of `T`, see [Type Hints](#type-hints) |
| `Sequence[T]`, `Iterable[T]`, `Iterator[T]`, `Mapping[K, V]` | Read-only abstract shapes from `collections.abc`; *covariant* in their element type, so `list[Circle]` satisfies `Sequence[Shape]` (`Mapping[K, V]`'s `K` stays invariant), see [Variance](#variance) |
| `Generator[Y, S, R]` | A generator's yield, send, and return types; `Iterator[T]` is enough when it only produces values, see [Generators](45_Effects--Generators.md#annotating-a-generator) |
| `Callable[[A, B], R]` | A function taking `A`, `B` and returning `R` (`...` for any parameters) |
| `type[C]` | The class object `C`, not an instance of it, see [Classes as Values](#classes-as-values-type) |

### <a href="https://docs.python.org/3/library/typing.html#typing.Union" target="_blank" rel="noopener">Unions, optionals, and literals</a>

| Construct | Meaning |
|-----------|---------|
| `X` \| `Y` | A union: either type, see [Type Hints](#type-hints) |
| `X` \| `None` | Optional: `X` or `None`, see [Type Hints](#type-hints) |
| `Literal[...]` | One of a fixed set of constant values, e.g. `Literal["r", "w"]`, see [The `type` Statement](#the-type-statement) |

### <a href="https://docs.python.org/3/library/typing.html#type-aliases" target="_blank" rel="noopener">Aliases and distinct types</a>

| Construct | Meaning |
|-----------|---------|
| `type Name = ...` | A type alias for a longer type, e.g. `type Grid = dict[tuple[int, int], str]`, see [The `type` Statement](#the-type-statement) |
| `NewType("Id", int)` | A distinct type, `int` at runtime but separate to the type checker; the base can be any class, not just a builtin |
| `Annotated[T, meta]` | `T` carrying extra metadata for libraries and tools |

### <a href="https://docs.python.org/3/library/typing.html#typing.Final" target="_blank" rel="noopener">Constants and class variables</a>

| Construct | Meaning |
|-----------|---------|
| `Final`, `Final[T]` | A name the type checker does not let you reassign, see [Constants with Final](#constants-with-final) |
| `ClassVar[T]` | A class-level attribute, not one per instance, see [Class Attributes](09_Class_Attributes.md#declaring-shared-state-with-classvar) |

### <a href="https://docs.python.org/3/library/typing.html#generics" target="_blank" rel="noopener">Generics</a>

| Construct | Meaning |
|-----------|---------|
| `def f[T](x: T) -> T` | A generic function (the type parameter varies per call), see [Generic Functions and Classes](#generic-functions-and-classes) |
| `class Box[T]` | A generic class, see [Generic Functions and Classes](#generic-functions-and-classes) |
| `[T: Base]`, `[T: (int, str)]` | A bounded or constrained type parameter, see [Generic Functions and Classes](#generic-functions-and-classes) |
| `[T = str]` | A type parameter default, used when you omit the brackets, see [Type Parameter Defaults](#type-parameter-defaults) |
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
| `TypeGuard[T]`, `TypeIs[T]` | A boolean predicate that narrows a type: `TypeGuard` narrows only where it returns `True`, `TypeIs` narrows both branches |

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
| `cast(T, x)` | Tells the type checker to treat `x` as `T`; [Flyweight](35_Flyweight.md#typing-the-symbol-set) shows the runtime guard to prefer over it |
| `assert_never(x)`, `assert_type(x, T)`, `reveal_type(x)` | Type-checker assertions and aids; `assert_never()` shown in [Pattern Matching](13_Pattern_Matching.md#exhaustive-matching) |
| `TYPE_CHECKING` | A flag that is `True` only to the type checker, for type-only imports, see [Simulation](38_Simulation.md#a-robot-in-a-maze) |

The runtime ignores all of these.
They exist for the type checker and the reader.
Older code writes some of them differently: `Optional[X]` for `X | None`,
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
    and call it on both a `list[int]` and a `list[str]` the way the listing calls `first()`.
4.  In `self_type.py`, add a subclass of `NamedTally` called `LoudTally` whose `report()` returns the message in all capitals,
    calling `super().report()` first.
    Confirm `.bump().bump().report()` still chains correctly on a `LoudTally`.
5.  Add `reveal_type(words.top())` to `type_defaults.py` and run `ty check` on the file.
    Remove the `= str` default and run it again.
    `ty` reports no error either way.
    Say what that means for a bare `Stack` annotation.
6.  In `type_aliases.py`,
    call `paint(grid, (2, 3), "purple")` and run `ty check`.
    Read the error, then widen `Color` to admit `"purple"` and confirm the error goes away.
7.  In `variance.py`, change `add_square()`'s parameter annotation to `Sequence[Shape]` and uncomment the call.
    Explain why `ty` now accepts the call and why `shapes.append(...)` no longer type-checks.
8.  In `narrowing.py`, replace `if text is not None:` with `if text:` and run `ty check`.
    Explain why the empty string now takes the other branch even though the type checker accepts either version.
