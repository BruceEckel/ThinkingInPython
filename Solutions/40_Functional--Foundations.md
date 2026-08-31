# Foundations: Solutions

## 1. `deposit()` is impure for the same reason `withdraw()` is

```python
balance = 100

def deposit(amount):
    global balance
    balance += amount
    return balance

print(deposit(30), deposit(30))
#: 130 160
```

Two identical calls, `deposit(30)` and `deposit(30)`, return different
results, `130` then `160`, which is impossible for a pure function:
a pure function must return the same value every time it is called
with the same arguments. `deposit()` reads and mutates `balance`, a
name outside its own scope, so its result depends on how many times it
(or `withdraw()`) has already run. You cannot know what `deposit(30)`
returns without tracking the history of every prior call, which is the
problem the chapter raises for `withdraw()`.

## 2. A `"*"` operator added to the dispatch table

```python
from collections.abc import Callable

def add(a, b):
    return a + b
def sub(a, b):
    return a - b
def mul(a, b):
    return a * b

operations: dict[str, Callable[[int, int], int]] = {
    "+": add,
    "-": sub,
    "*": mul,
}
print(operations["+"](6, 4), operations["-"](6, 4),
      operations["*"](6, 4))
#: 10 2 24
```

`operations["*"](6, 4)` is called the same way as the other
two entries. Nothing about the calling code changes. Supporting a new
operator really was just adding one row to the table, as the chapter
claims.

## 3. A fourth independent closure

```python
def multiplier(factor):
    def multiply(n):
        return n * factor
    return multiply

double = multiplier(2)
triple = multiplier(3)
quadruple = multiplier(4)
print(double(10), triple(10), quadruple(10))
#: 20 30 40
```

Each call to `multiplier()` creates a new `multiply` closure with its
own private `factor`. `quadruple` remembers `4` independently of
`double`'s `2` and `triple`'s `3`, the same way `double` and `triple`
were already independent of each other. Nothing shared between them
could leak, because each closure's `factor` is reachable only through
that particular returned function.

## 4. A three-stage composition

```python
def compose(f, g):
    def composed(x):
        return f(g(x))
    return composed

def increment(n):
    return n + 1
def double(n):
    return n * 2
def square(n):
    return n * n

increment_then_double = compose(double, increment)
increment_then_double_then_square = compose(
    square, increment_then_double)
print(increment_then_double_then_square(3))
#: 64
```

`increment_then_double_then_square(3)` runs `increment_then_double(3)`
first, which computes `(3 + 1) * 2 = 8`, then feeds that `8` into
`square`, giving `8 * 8 = 64`. `compose()` did not need to change at
all to support a third stage. Wrapping one composed function inside
another `compose()` call is enough to extend the pipeline.

## 5. Fixing a leading argument, and why the trailing one differs

```python
import textwrap
from functools import partial

def clamp(low: int, value: int, high: int, /) -> int:
    return max(low, min(value, high))

at_least_ten = partial(clamp, 10)
print(at_least_ten(3, 100), at_least_ten(50, 100))
#: 10 50
try:
    partial(clamp, high=100)(0, 5)
except TypeError as e:
    for line in textwrap.wrap(str(e), 57):
        print(line)
#: clamp() got some positional-only arguments passed as
#: keyword arguments: 'high'
```

`at_least_ten` needs no `Placeholder`. `low` is the first parameter,
and `partial()` already fills positional arguments from the left, so
the two remaining parameters stay open in order.

Fixing `high` alone is the case that has no answer without a
`Placeholder`. `partial(clamp, high=100)` is accepted when you build
it, since `partial()` does not inspect the signature, and fails only
when you call it: `high` is positional-only, so it cannot arrive by
name. Passing it positionally means passing `low` and `value` first,
which is the opposite of leaving them to the caller.
`partial(clamp, Placeholder, Placeholder, 100)` is the version that
works, and it is what `Placeholder` exists for.

## 6. `Final` locks the name, not the object

```python
from typing import Final

CONFIG: Final[list[int]] = [1, 2]
CONFIG.append(3)
MAX_SIZE: Final[int] = 100
MAX_SIZE = 200
print(CONFIG, MAX_SIZE)
#: [1, 2, 3] 200
```

`ty` reports one error here, not two, and the one it reports is the
assignment:

```
error[invalid-assignment]: Reassignment of `Final` symbol `MAX_SIZE` is not allowed
 --> immutable_types.py:6:1
  |
5 | MAX_SIZE: Final[int] = 100
  |           ---------- Symbol declared as `Final` here
6 | MAX_SIZE = 200
  | ^^^^^^^^^^^^^^ Symbol later reassigned here
```

`CONFIG.append(3)` passes because it is not a reassignment. `Final`
constrains the binding between a name and an object: `CONFIG` must
keep pointing at the same list forever. It says nothing about that
list's contents, and `append()` mutates the object while leaving the
binding alone. `MAX_SIZE = 200` is the operation `Final` exists to
reject, because it points the name at a different object.

To reject the append, the value's own type has to be immutable:

```python
from typing import Final

CONFIG: Final[tuple[int, ...]] = (1, 2)
print(CONFIG)
#: (1, 2)
```

Adding `CONFIG.append(3)` to that version reports:

```
error[unresolved-attribute]: Object of type `tuple[Literal[1], Literal[2]]` has no attribute `append`
```

The error arrives from the tuple rather than from `Final`, which is
the chapter's point: `Final` guards the name, and the element type
guards the contents. You need both.

## 7. Comprehensions, a different `key`, and a bare `map` object

```python
numbers = [1, 2, 3, 4, 5]
squares = [n * n for n in numbers]
print(squares)
#: [1, 4, 9, 16, 25]
evens = [n for n in numbers if n % 2 == 0]
print(evens)
#: [2, 4]
words = ["banana", "pie", "kiwi", "watermelon"]
print(sorted(words, key=lambda w: w[-1]))
#: ['banana', 'pie', 'kiwi', 'watermelon']
```

Both comprehensions say what `map()` and `filter()` said, without the
lambda, which is the chapter's rule for an expression written on the
spot. Sorting by last letter happens to produce the same order as
sorting by length for this word list (`a`, `e`, `i`, `n` ascending),
a coincidence worth checking rather than assuming.

Dropping the `list()` is the part that surprises:

```python
numbers = [1, 2, 3, 4, 5]
raw = map(lambda n: n * n, numbers)
print(type(raw).__name__)
#: map
print(list(raw))
#: [1, 4, 9, 16, 25]
print(list(raw))
#: []
```

Printing `raw` directly shows `<map object at 0x...>` rather than any
values, because `map()` returns a lazy iterator and its `__repr__` has
nothing to report. The second `list(raw)` is the more dangerous half:
it returns `[]` with no error at all. The iterator was consumed by the
first pass and cannot be rewound, so any later pass sees an exhausted
object and silently produces nothing. A comprehension hands back a
finished list, which can be walked as many times as you like.

## 8. Only the assigned name needs `nonlocal`

```python
from collections.abc import Callable

def make_counter(step: int = 1) -> Callable[[], int]:
    count = 0
    def increment() -> int:
        nonlocal count
        count += step
        return count
    return increment

tally = make_counter(10)
print(tally(), tally(), tally())
#: 10 20 30
```

`increment()` captures two names, and only one of them needs the
declaration. `step` is only read, like `factor` in `multiplier()`, and
reading a captured name needs no declaration. `count` is assigned, and
assignment is how Python decides a name is local, so without
`nonlocal` the `count += step` line would create a fresh local and
read it before any value exists.

Deleting the `nonlocal` line shows both guides in order. `ty` reports
`Name 'count' used when not defined` on the `count += step` line
before the program runs. Running anyway raises `UnboundLocalError`
("cannot access local variable 'count' where it is not associated
with a value") at the first `tally()` call. The type checker points at the
assignment that went wrong. The runtime message complains about a
local variable the code never meant to create.
