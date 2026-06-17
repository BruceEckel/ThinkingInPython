# Static Type Checking

The functions in the earlier chapters declare no types. C++ and Java make you
declare the type of everything, and they check those types before the program
runs. Python checks types at run time, only when an operation is actually
attempted, and the book so far has leaned on that freedom.

On a small program you do not miss the declarations. On a large one you start to.
A type error that a compiler would have caught now waits until the code runs, and
sometimes that means it waits until a bug report. Python's answer keeps the
freedom and adds the safety net back on your terms. You annotate code with *type
hints*, and a separate tool reads them and tells you, before you run anything,
where the types do not line up. The hints are optional and the checking is a
separate step, so you opt in as much as it pays off and no more.

## Type Hints

A hint annotates a parameter, a return value, or a variable. You write a colon
for parameters and variables, and an arrow for the return type:

```python
# typed_basics.py
# Hints annotate parameters, returns, and variables. They do not
# change how the code runs; they let a checker and an editor reason
# about it.


def repeat(text: str, times: int) -> str:
    return text * times


total: int = 0
for word in ["a", "bb", "ccc"]:
    total += len(word)

print(repeat("ab", 3))
print(total)
```

The container and optional types read the way you say them: `list[int]`,
`dict[str, float]`, `tuple[int, ...]`, and `str | None` for "a string or
nothing."

## Constants with Final

The naming convention earlier used ALL_CAPS to signal a constant, but that is
only a hint to human readers. `Final` makes it a hint the checker enforces:
reassign a `Final` name and the checker reports it, even though Python itself
still allows the assignment at run time.

```python
# final_constants.py
# Final marks a name as a constant. Reassigning it is a type error,
# caught by the checker before the program runs.
from typing import Final

MAX_RETRIES: Final = 3
GREETING: Final[str] = "hello"

# MAX_RETRIES = 5  # ty: cannot assign to final name "MAX_RETRIES"

print(MAX_RETRIES, GREETING)
```

You can give the type explicitly, as in `Final[str]`, or let it be inferred from
the value, as with `MAX_RETRIES`. Marking the values that are meant to stay
fixed turns a class of accidental reassignments into errors you hear about at
once.

## Gradual Typing

You do not have to annotate everything, or anything. Add hints one function at a
time, and the unannotated code keeps working. The checker treats whatever it
cannot see as the type `Any`, which is compatible with everything, so typed and
untyped code live together. This is *gradual typing*. Start untyped, then add
hints where they earn their keep: the public interfaces, the tricky data, the
code other people depend on. Throwaway scripts you leave bare. When a value
really is dynamic, `Any` is an honest way to say so.

## The Checker: ty

The hints do nothing on their own. You need a tool to read them. This book uses
[`ty`](https://github.com/astral-sh/ty), Astral's fast checker. You point it at
your code:

    ty check

It complains where the hints and the code disagree, and stays quiet when they
agree. Every runnable example in this book is checked this way, and the build
runs `ty` on every change, so the code you read here checks as well as runs.

## Catching Mistakes

The whole point is to hear about a mistake before it ships. Look at this:

```python
def area(width: int, height: int) -> int:
    return width * height

area("3", 4)   # ty: argument of type "str" is not assignable to "int"
```

At run time `area("3", 4)` does not even raise. It returns `"3333"`, because
`"3" * 4` is perfectly good string repetition. The bug would surface much later,
somewhere that expected a number, far from the line that caused it. The checker
points at the call right away.

## Structural Typing with Protocols

This feature fits the way Python already works. The earlier chapters relied on
*dynamic typing*: a function accepts any object, and the only requirement is
that the object supports the operations performed on it. The type is checked at
run time, when the operation runs. This is often called *duck typing*: if it
looks like a duck and quacks like a duck, treat it as a duck.

*Structural typing* is the static counterpart. Rather than wait for run time, a
type checker verifies ahead of time that an object has the required shape: the
right methods and attributes, whatever class it was declared as. Dynamic typing
and structural typing are the same idea checked at different moments. Dynamic
typing trusts the object when the code runs; structural typing proves the shape
before the code runs.

A *Protocol* expresses that shape. Some statically typed languages make you
declare up front that a class "is a" `Drawable` by inheriting from it. A
`Protocol` asks only that an object have the right shape, with no inheritance:

```python
# protocols.py
# A Protocol describes a required shape: any object with that shape
# qualifies, without inheriting from a base class.
from typing import Protocol


class Drawable(Protocol):
    def draw(self) -> str: ...


class Circle:
    def draw(self) -> str:
        return "circle"


class Square:
    def draw(self) -> str:
        return "square"


def render(shape: Drawable) -> str:   # accepts anything with draw()
    return shape.draw()


print(render(Circle()))
print(render(Square()))
```

`Circle` and `Square` never mention `Drawable`, and both are accepted, because
each has a `draw()` of the right shape. Hand `render()` an object with no
`draw()` and `ty` rejects it. You keep the flexibility of dynamic typing and gain
the early warning of static types.

## The Hints Are Not Enforced at Run Time

Keep one thing straight: the hints do not change what the program does. Python
stores them and otherwise ignores them. A wrong type that slips past the checker
behaves exactly as it would have with no hints at all. Checking is a separate
step you run, like the tests. If you need a guarantee at run time, you still
write `isinstance`, or use a library built to validate data. The
[typeguard](https://typeguard.readthedocs.io) library reads your existing
annotations and enforces them at run time, and [Pydantic](https://docs.pydantic.dev)
validates and parses data against typed models, which is useful at the edges of a
program where untrusted input comes in. The hints themselves are for the tools and
for the reader. The run-time behavior is unchanged.

## Further Reading

- The official Python tutorial: <https://docs.python.org/3/tutorial/>
- The Python Programming FAQ:
  <https://docs.python.org/3/faq/programming.html>
- Planet Python, an aggregator of Python articles from around the web:
  <https://planetpython.org/>
