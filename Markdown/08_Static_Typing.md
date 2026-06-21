# Static Typing

C++ and Java make you declare the type of everything,
and they check those types before the program runs.
Python checks types at run time, only when an operation is actually attempted.
Up until this chapter, we haven't used type declarations.

On a small program you do not miss the declarations.
On a large program, type errors that C++ or Java would catch now appear only when the code runs.
Sometimes that means it waits until a bug report.

Python 3.5 (2015) introduced *type hints*, which look like static type checking in other languages.
However, the Python runtime does not care if your type hints are *logically* correct as long as they are structurally and syntactically valid.
The runtime ignores properly-formed type hints,
so if you want the equivalent of a compiler in a typed language you must run an additional type checking tool (this book uses Astral's `ty`).

You can put type hints on some elements and not others, so you can opt in only as much as it pays off.

## Type Hints

A hint annotates a parameter, a return value, or a variable.
Use a colon for parameters and variables, and an arrow for the return type:

```python
# typed_basics.py

def repeat(text: str, times: int) -> str:
    return text * times

print(repeat("ab", 3))

total: int = 0
for word in ["a", "bb", "ccc"]:
    total += len(word)

print(total)
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
```

You can give the type explicitly, as in `Final[str]`,
or let it be inferred from the value, as with `MAX_RETRIES`.
Marking values `Final` immediately discovers accidental reassignments.

## Gradual Typing

You can add hints one function at a time; the unannotated code keeps working.
The checker treats whatever it cannot see as the type `Any`,
which is compatible with everything, so typed and untyped code live together.
This is *gradual typing*.
You can slowly add hints where they earn their keep: the public interfaces,
the tricky data, the code other people depend on.
When a value is truly dynamic, `Any` shows that you mean it to be.

## The Checker: `ty`

The hints do nothing on their own.
You need a tool to check them.
This book uses [`ty`](https://github.com/astral-sh/ty), Astral's fast checker:

    ty check

It complains where the hints and the code disagree, and is quiet when they agree.
Every runnable example in this book is checked this way.
The build runs `ty` on every change, so the code you read here checks as well as runs.

## Catching Mistakes

The goal is to discover mistakes before the program runs.
Consider:

```python
def area(width: int, height: int) -> int:
    return width * height

area("3", 4)   # ty: argument of type "str" is not assignable to "int"
```

At run time `area("3", 4)` does not cause an error.
It returns `"3333"`, because `"3" * 4` is the correct syntax for string repetition.
Bugs surface later, often far from the line that caused it.
The checker immediately discovers the problem.

## Structural Typing with Protocols

Earlier chapters relied on *dynamic typing*: a function accepts any object,
and the only requirement is that the object supports the operations performed on it.
The type is checked at run time, when the operation runs.
Dynamic typing is often called *duck typing*:
if it looks like a duck and quacks like a duck, treat it as a duck.

*Structural typing* is the static counterpart.
Rather than wait for run time,
a type checker verifies ahead of time that an object has the required *shape*,
which means the methods and attributes required by whatever consumes that type.
Dynamic typing and structural typing are the same idea checked at different moments.
Dynamic typing trusts the object when the code runs;
structural typing proves the shape before the code runs.

A *Protocol* expresses that shape.
Some statically typed languages make you declare up front that a class "is a" `Drawable` by inheriting from it.
A Protocol describes a required shape: any object with that shape
qualifies, without inheriting from a base class.
A `Protocol` can be used without inheritance:

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
print(render(Square()))
```

`Circle` and `Square` never mention `Drawable`.
Both are accepted because each has a `draw()` of the right shape.
If you pass `render()` an object without a `draw()`, `ty` rejects it.
Python preserves the flexibility of dynamic typing but gains the early warning of static types.

## The Hints Are Not Enforced at Run Time

Keep one thing straight: the hints do not change what the program does.
Python stores them and otherwise ignores them.
A wrong type that slips past the checker behaves exactly as it would have with no hints at all.
Checking is a separate step you run, like the tests.
If you need a guarantee at run time, you still write `isinstance`,
or use a library built to validate data.
The [typeguard](https://typeguard.readthedocs.io) library reads your existing annotations and enforces them at run time,
and [Pydantic](https://docs.pydantic.dev) validates and parses data against typed models,
which is useful at the edges of a program where untrusted input comes in.
The hints themselves are for the tools and for the reader.
The run-time behavior is unchanged.

## Further Reading

- The official Python tutorial: <https://docs.python.org/3/tutorial/>
- The Python Programming FAQ:
  <https://docs.python.org/3/faq/programming.html>
- Planet Python, an aggregator of Python articles from around the web:
  <https://planetpython.org/>
