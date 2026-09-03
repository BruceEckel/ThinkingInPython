# Foundations: Solutions

## 1. `deposit()` is impure for the same reason `withdraw()` is

```python
# exercise_1.py
balance = 100

def deposit(amount):
    global balance
    balance += amount
    return balance

print(deposit(30), deposit(30))
#: 130 160
```

`deposit()` reads and mutates `balance`, a name outside its own
scope. A pure function reads nothing that can change and changes
nothing outside itself, so `deposit()` breaks both halves of that
definition. What `deposit(30)` returns depends on how many times
`deposit()` (or `withdraw()`) has already run: the two identical calls
`deposit(30)` and `deposit(30)` return `130` and then `160`, where a
pure function returns the same value both times. To predict either
result you must track the history of every prior call, and that
tracking is the problem the chapter raises for `withdraw()`.

## 2. A `"*"` operator added to the dispatch table

```python
# exercise_2.py
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

You call `operations["*"](6, 4)` exactly the way you call the other
two entries, and the calling code stays as it was. Supporting a new
operator really was just adding one row to the table, as the chapter
claims.

## 3. A fourth independent closure

```python
# exercise_3.py
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
were already independent of each other. The three closures share
nothing, because each `factor` is reachable only through the one
function that captured it.

## 4. A three-stage composition

```python
# exercise_4.py
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
`square`, giving `8 * 8 = 64`. `compose()` needs no change to support
a third stage: wrapping one composed function inside another
`compose()` call extends the pipeline.

## 5. Fixing a leading argument, and why the trailing one differs

```python
# exercise_5.py
import textwrap
from functools import partial

def clamp(low: int, value: int, high: int, /) -> int:
    return max(low, min(value, high))

at_least_ten = partial(clamp, 10)
print(at_least_ten(3, 100), at_least_ten(50, 100))
#: 10 50
try:
    partial(clamp, high=100)(0, 5)  # type: ignore
except TypeError as e:
    for line in textwrap.wrap(str(e), 57):
        print(line)
#: clamp() got some positional-only arguments passed as
#: keyword arguments: 'high'
```

`at_least_ten` needs no `Placeholder`. `low` is the first parameter,
and `partial()` already fills positional arguments from the left, so
the two remaining parameters stay open in order.

Fixing `high` alone is the case that needs a `Placeholder`.
`partial()` does not inspect the signature, so building
`partial(clamp, high=100)` succeeds. The call is where it fails:
`high` is positional-only, so it cannot arrive by name. Passing
`high` positionally means passing `low` and `value` first, which is
the opposite of leaving them to the caller.
`partial(clamp, Placeholder, Placeholder, 100)` is the version that
works, and it is what `Placeholder` exists for.

## 6. `Final` locks the name, not the object

```python
# exercise_6.py
from typing import Final

CONFIG: Final[list[int]] = [1, 2]
CONFIG.append(3)
MAX_SIZE: Final[int] = 100
MAX_SIZE = 200  # type: ignore
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

`Final` constrains the binding between a name and an object: `CONFIG`
must keep pointing at the same list forever. `Final` says nothing
about that list's contents, so `CONFIG.append(3)` passes: `append()`
mutates the object and leaves the binding alone. `MAX_SIZE = 200` is
the operation `Final` exists to reject, because it points the name at
a different object.

To reject the append, the value's own type has to be immutable:

```python
# exercise_6_tuple.py
from typing import Final

CONFIG: Final[tuple[int, ...]] = (1, 2)
print(CONFIG)
#: (1, 2)
```

Adding `CONFIG.append(3)` to that version reports:

```
error[unresolved-attribute]: Object of type `tuple[Literal[1], Literal[2]]` has no attribute `append`
```

The error arrives from the tuple rather than from `Final`, and that
split is the chapter's point: `Final` guards the name, and the value's
own type guards the contents. You need both.

## 7. Comprehensions, a different `key`, and a bare `map` object

```python
# exercise_7.py
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
lambda, and the chapter's rule of thumb picks the comprehension for an
expression you write inline. The last letters `a`, `e`, `i`, and `n`
already ascend, so sorting by last letter hands the word list back in
its original order, where the chapter's `key=len` put `pie` first.
Check an order like that rather than assuming it.

Dropping the `list()` is the part that surprises:

```python
# exercise_7_map.py
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
it returns `[]` and raises no error. The first `list(raw)` consumed
the iterator, and nothing rewinds it, so any later pass sees an
exhausted object and silently produces nothing. A comprehension hands
back a finished list, which you can walk as many times as you like.

## 8. Only the assigned name needs `nonlocal`

```python
# exercise_8.py
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
`nonlocal` declaration. It only reads `step`, the way `multiply()`
reads `factor` in `multiplier()`, and reading a captured name needs no
declaration. `increment()` assigns `count`, and assignment is how
Python decides a name is local. Without `nonlocal`, the
`count += step` line would create a fresh local and read it before any
value exists.

Deleting the `nonlocal` line draws two complaints, in order. `ty`
reports `Name 'count' used when not defined` on the `count += step`
line before the program runs. Running anyway raises an
`UnboundLocalError` at the first `tally()` call: "cannot access local
variable 'count' where it is not associated with a value". The type
checker points at the assignment that went wrong. The runtime message
complains about a local variable the code never meant to create.

## 9. A second filter, and why the stages are not interchangeable

```python
# exercise_9.py
from collections.abc import Sequence
from dataclasses import dataclass
from functools import partial

@dataclass(frozen=True)
class Reading:
    sensor: str
    celsius: float

def warmer_than(limit: float, r: Reading) -> bool:
    return r.celsius > limit

def colder_than(limit: float, r: Reading) -> bool:
    return r.celsius < limit

def to_fahrenheit(r: Reading) -> Reading:
    return Reading(r.sensor, r.celsius * 9 / 5 + 32)

def report(readings: Sequence[Reading]) -> list[str]:
    warm = filter(partial(warmer_than, 20.0), readings)
    band = filter(partial(colder_than, 30.0), warm)
    return [f"{r.sensor} {r.celsius:.1f}"
            for r in map(to_fahrenheit, band)]

def converted_first(
    readings: Sequence[Reading],
) -> list[str]:
    hot = map(to_fahrenheit, readings)
    warm = filter(partial(warmer_than, 20.0), hot)
    band = filter(partial(colder_than, 30.0), warm)
    return [f"{r.sensor} {r.celsius:.1f}" for r in band]

data = [Reading("a", 18.0), Reading("b", 25.0),
        Reading("c", 30.5)]
print(report(data))
#: ['b 77.0']
print(converted_first(data))
#: []
print([r.celsius for r in data])
#: [18.0, 25.0, 30.5]
```

`colder_than()` mirrors `warmer_than()`, and `partial()` turns each
into the one-argument callable `filter()` wants. Chaining the two
filters leaves only `b`, whose 25.0 Celsius sits inside the band:
`a` is too cold and `c` is too warm. The two filters commute, because
each one tests the same untouched Celsius value, so swapping the
`warm` and `band` lines reports the same reading.

`converted_first()` shows that the `map()` does not commute with
them. It returns an empty list. Once `to_fahrenheit()` has run, every
reading carries a Fahrenheit number, and 64.4, 77.0, and 86.9 all pass
`warmer_than(20.0)` and all fail `colder_than(30.0)`. The predicates
still read `r.celsius`, so they now compare a Fahrenheit number
against a Celsius limit and quietly answer the wrong question. Nothing
raises an exception, because both stages are correct on their own.
The unit lives only in the field name. A stage that changes what a
value means must run after every stage that reads the old meaning.

The last `print()` repeats the chapter's point. Both reports read
`data` and neither writes it, so the Celsius values are unchanged
after three traversals, and you can run either report again and get
the same answer.
