# Static Type Checking

I spent years in statically typed languages. C++ and Java make you declare the
type of everything, and they check those types before the program runs. When I
came to Python I enjoyed leaving all of that out. The interpreter checks types
at run time, only when an operation is actually attempted, and the earlier
chapters lean on that freedom.

On a small program I do not miss the declarations. On a large one I started to.
A type error that a compiler used to catch now waits until the code runs, and
sometimes that means it waits until a bug report. Python's answer keeps the
freedom and adds the safety net back on your terms. You annotate code with *type
hints*, and a separate tool reads them and tells you, before you run anything,
where the types do not line up. The hints are optional and the checking is a
separate step, so you opt in as much as pays off and no more.

## Type Hints

A hint annotates a parameter, a return value, or a variable. You write a colon
for parameters and variables, and an arrow for the return type:

```python
# typed_basics.py
# Hints annotate parameters, returns, and variables. They do not change how the
# code runs; they let a checker and an editor reason about it.


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
nothing." There is almost no new vocabulary to learn for everyday code.

## Gradual Typing

This is the part I like. You do not have to annotate everything, or anything.
Add hints one function at a time, and the unannotated code keeps working. The
checker treats whatever it cannot see as the type `Any`, which is compatible
with everything, so typed and untyped code live together. This is *gradual
typing*. I start untyped, then add hints where they earn their keep: the public
interfaces, the tricky data, the code other people depend on. Throwaway scripts
I leave bare. When a value really is dynamic, `Any` is an honest way to say so.

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

This is the feature that won me over, because it fits the way Python already
works. Some statically typed languages make you declare, up front, that a class
"is a" `Drawable` by inheriting from it. That fights duck typing, where what
matters is whether an object *has* the methods you call, not what it inherits
from.

A *Protocol* types duck typing directly. You describe a shape, and any object
with that shape satisfies it, with no inheritance:

```python
# protocols.py
# A Protocol types duck typing: any object with the right shape qualifies,
# without inheriting from a base class.
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
`draw()` and `ty` rejects it. You keep the flexibility of duck typing and gain
the early warning of static types.

## The Hints Are Not Enforced at Run Time

Keep one thing straight: the hints do not change what the program does. Python
stores them and otherwise ignores them. A wrong type that slips past the checker
behaves exactly as it would have with no hints at all. Checking is a separate
step you run, like the tests. If you need a guarantee at run time, you still
write `isinstance`, or reach for a library built to validate data. The hints are
for the tools and for the reader. The run-time behavior is unchanged.

## Exercises

1.  Add type hints to a small untyped script of yours, then run `ty check` and
    fix what it reports.
2.  Write a `Protocol` named `Sized` with a `__len__(self) -> int` method, and a
    function that accepts anything matching it. Confirm a `list` and a `str`
    both satisfy it.
3.  Annotate a function to return `str | None`, then write a caller that `ty`
    forces you to handle the `None` case before using the result.
