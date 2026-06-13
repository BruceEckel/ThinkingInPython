# Static Type Checking

Python runs without type declarations. The interpreter checks types at run time,
when an operation is actually attempted, and not before. That is what makes the
language quick to write and easy to read, and the earlier chapters lean on it.

But on a larger program, "find out when it runs" becomes "find out from a bug
report." *Static type checking* adds the missing early warning without taking
away the dynamic nature of the language. You annotate code with *type hints*, and
a separate tool reads those hints and tells you, before you run anything, where
the types do not line up. The hints are optional and the checking is a separate
step, so you opt in exactly as much as pays off.

## Type Hints

A type hint annotates a parameter, a return value, or a variable. The syntax is a
colon for parameters and variables, and an arrow for return types:

```python
# StaticTypeChecking/typed_basics.py
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

Container and optional types read naturally: `list[int]`, `dict[str, float]`,
`tuple[int, ...]`, and `str | None` for "a string or nothing." There is no
separate typing vocabulary to learn for the common cases; you write the types the
way you say them.

## Gradual Typing

You do not have to annotate everything, or anything. Hints can be added one
function at a time, and unannotated code keeps working. A checker treats what it
cannot see as the type `Any`, which is compatible with everything, so untyped and
typed code coexist. This is *gradual typing*: start untyped, add hints where they
earn their keep (public interfaces, tricky data, code others depend on), and
leave throwaway scripts bare. `Any` is also an explicit escape hatch for the rare
spot where a value is genuinely dynamic.

## The Checker: ty

Hints do nothing by themselves. A type checker reads them. This book uses
[`ty`](https://github.com/astral-sh/ty), Astral's fast checker. You run it over
your code:

    ty check

It reports each place where the hints and the code disagree, and says nothing
when they agree. Every runnable example in this book is checked this way, and the
project's continuous integration runs `ty` on every change, so the code you read
here type-checks as well as runs.

## Catching Mistakes

The point of all this is to be told about a mistake before it ships. Consider:

```python
def area(width: int, height: int) -> int:
    return width * height

area("3", 4)   # ty: argument of type "str" is not assignable to "int"
```

At run time `area("3", 4)` does not even raise. It returns `"3333"`, because
`"3" * 4` is valid string repetition. The bug would surface much later, somewhere
that expected a number. The checker flags the call immediately, at the line that
is actually wrong.

## Structural Typing with Protocols

Static typing in some languages forces you to declare, up front, that a class
"is a" `Drawable` by inheriting from it. That fights Python's duck typing, where
what matters is whether an object *has* the right methods, not what it inherits.

A `Protocol` types duck typing directly. It describes a shape: any object with
those methods satisfies it, with no inheritance required:

```python
# StaticTypeChecking/protocols.py
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

`Circle` and `Square` never mention `Drawable`, yet both are accepted, because
each has a `draw()` of the right shape. If you passed an object without a
`draw()`, `ty` would reject it. This is the best of both worlds: the flexibility
of duck typing with the early checking of static types.

## Hints Do Not Change Runtime Behavior

Type hints are not enforced when the program runs. Python stores them but does
not act on them, so a wrong type that slips past the checker behaves exactly as
it would have without any hints. Checking is a separate step you run, like a
linter or the tests. If you need a value's type guaranteed at run time, you still
check it yourself with `isinstance`, or validate it with a library built for that.
The hints are for the tools and the reader; the run-time semantics are unchanged.

## Exercises

1.  Add type hints to a small untyped script of yours, then run `ty check` and
    fix what it reports.
2.  Write a `Protocol` named `Sized` with a `__len__(self) -> int` method, and a
    function that accepts anything matching it. Confirm a `list` and a `str`
    both satisfy it.
3.  Annotate a function to return `str | None`, then write a caller that `ty`
    forces you to handle the `None` case before using the result.
