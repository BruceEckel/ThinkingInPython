# Foundations: Solutions

## 1. `deposit()` is impure for the same reason `withdraw()` is

> In `pure_functions.py`, write a third function, `deposit(amount)`,
> that behaves like `withdraw()` but adds to `balance` instead of subtracting.
> Explain, the way the text does for `withdraw()`, why `deposit()` is impure.

```python
# exercise_1.py
balance = 100

def deposit(amount: int) -> int:
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

> In `dispatch.py`, add a `"*"` operator to the `operations` table backed by a new `mul()` function,
> with no change to how `operations["*"](6, 4)` gets called.

```python
# exercise_2.py
from collections.abc import Callable
from operator import mod
from exceptions import expected

def add(a: int, b: int) -> int:
    return a + b
def sub(a: int, b: int) -> int:
    return a - b
def mul(a: int, b: int) -> int:
    return a * b
def floordiv(a: int, b: int) -> int:
    return a // b

operations: dict[str, Callable[[int, int], int]] = {
    "+": add,
    "-": sub,
    "*": mul,
    "//": floordiv,
}
operations["%"] = mod
print(operations["+"](6, 4), operations["-"](6, 4),
      operations["*"](6, 4), operations["//"](6, 4),
      operations["%"](6, 4))
#: 10 2 24 1 2
with expected(KeyError):
    operations["^"](6, 4)
#: [KeyError] '^'
```

You call `operations["*"](6, 4)` the way you call the other four
entries, and the calling code stays as it was. Supporting the new
operator takes one function and one row in the table. `expected()`
from the shared `exceptions` helper catches the missing-key
`KeyError`, as it does in the chapter's `dispatch.py`.

## 3. A fourth independent closure

> In `closures.py`, add `quadruple = multiplier(4)` and confirm it behaves independently of `double` and `triple`,
> each holding its own `factor`.

```python
# exercise_3.py
from collections.abc import Callable

def multiplier(factor: int) -> Callable[[int], int]:
    def multiply(n: int) -> int:
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
are already independent of each other. The three closures share
nothing, because each `factor` is reachable only through the one
function that captured it.

## 4. A three-stage composition

> In `compose_functions.py`, write a third small function, `square(n)`,
> and build `increment_then_double_then_square = compose(square, increment_then_double)`.
> Predict `increment_then_double_then_square(3)` before running it.

```python
# exercise_4.py
from collections.abc import Callable

def compose[T, U, V](
    f: Callable[[U], V], g: Callable[[T], U]
) -> Callable[[T], V]:
    def composed(x: T) -> V:
        return f(g(x))
    return composed

def increment(n: int) -> int:
    return n + 1
def double(n: int) -> int:
    return n * 2
def square(n: int) -> int:
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

## 5. Presetting a leading argument, and why the trailing one differs

> In `placeholder.py`, build a second partial, `at_least_ten`,
> that presets only `low` to 10 and leaves both other arguments to the caller.
> Then try to preset only `high` without a `Placeholder` and explain why that is impossible.

```python
# exercise_5.py
from functools import partial
from exceptions import expect

def clamp(low: int, value: int, high: int, /) -> int:
    return max(low, min(value, high))

at_least_ten = partial(clamp, 10)
print(at_least_ten(3, 100), at_least_ten(50, 100))
#: 10 50
expect(TypeError, partial(clamp, high=100), 0, 5)  # type: ignore
#: [TypeError] clamp() got some positional-only arguments
#: passed as keyword arguments: 'high'
```

`at_least_ten` needs no `Placeholder`. `low` is the first parameter,
and `partial()` already fills positional arguments from the left, so
the two remaining parameters stay open in order.

Presetting `high` alone is the case that needs a `Placeholder`.
`partial()` does not inspect the signature, so building
`partial(clamp, high=100)` succeeds. The call is where the partial fails:
`high` is positional-only, so it cannot arrive by name. Passing
`high` positionally means passing `low` and `value` first, which is
the opposite of leaving them to the caller.
`partial(clamp, Placeholder, Placeholder, 100)` is the version that
works, and it is what `Placeholder` exists for.

The `# type: ignore` is there because `ty` finds the mistake earlier
than the runtime does. `ty` reports `positional-only-parameter-as-kwarg`
on `partial(clamp, high=100)`, the line that builds the partial, where
the runtime waits for the call.

## 6. `Final` locks the name, not the object

> In `immutable_types.py`,
> add `CONFIG: Final[list[int]] = [1, 2]` and a line that appends to it.
> Run `ty`, which reports nothing.
> Then add `MAX_SIZE = 200`, run `ty` again,
> and explain why the rebinding is an error while the append is not.
> Then change the annotation so appending *is* rejected.

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

The reassignment carries a `# type: ignore` so the listing passes the
book's build. With that comment removed, `ty` reports one error here,
not two, and the one it reports is the assignment:

```
error[invalid-assignment]: Reassignment of `Final` symbol `MAX_SIZE` is not allowed
 --> exercise_6.py:7:1
  |
6 | MAX_SIZE: Final[int] = 100
  |           ---------- Symbol declared as `Final` here
7 | MAX_SIZE = 200
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

> In `higher_order.py`,
> replace the `map()` and `filter()` calls with comprehensions,
> and the `sorted(key=len)` call with one that sorts by last letter.
> Then start again from the original file,
> delete the `list()` around the `map()` call, print the result,
> and say what you see and why.

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
values, because `map()` returns a lazy iterator that has computed
nothing yet, so its `repr()` shows only the type and an address. The
second `list(raw)` is the more dangerous half:
it returns `[]` and raises no error. The first `list(raw)` consumed
the iterator, and nothing rewinds it, so any later pass sees an
exhausted object and silently produces nothing. A comprehension hands
back a finished list, which you can walk as many times as you like.

## 8. Only the assigned name needs `nonlocal`

> In `make_counter.py`, give `make_counter()` a `step: int = 1` parameter,
> so `make_counter(10)` builds a counter that counts 10, 20, 30.
> `increment()` reads `step` without declaring it `nonlocal`:
> explain why `count` needs the declaration and `step` does not.
> Then delete the `nonlocal` line and compare the type checker's report with the runtime failure.

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
`count += step` line creates a fresh local and reads it before any
value exists.

Deleting the `nonlocal` line draws two complaints, in order. `ty`
reports `Name 'count' used when not defined` on the `count += step`
line before the program runs. Running anyway raises an
`UnboundLocalError` at the first `tally()` call: "cannot access local
variable 'count' where it is not associated with a value." The type
checker points at the assignment that went wrong. The runtime message
complains about a local variable `increment()` never meant to create.

## 9. A second filter, and why the stages are not interchangeable

> In `pipeline.py`, add `colder_than(limit, r)` beside `warmer_than()`,
> and give `report()` a second `filter()` stage built with `partial()`,
> so only readings between 20.0 and 30.0 Celsius reach the output.
> Then write a second version of `report()` that calls `map(to_fahrenheit, ...)` ahead of both filters,
> and explain the list it returns.

```python
# exercise_9.py
from collections.abc import Sequence
from functools import partial
from record import record

@record
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
into the one-argument callable `filter()` requires. Chaining the two
filters leaves only `b`, whose 25.0 Celsius sits inside the band:
`a` is too cold and `c` is too warm. The two filters commute, because
each one tests the same untouched Celsius value, so swapping the
`warm` and `band` lines reports the same reading.

The empty list from `converted_first()` shows that the `map()` does
not commute with the filters. Once `to_fahrenheit()` has run, every
reading carries a Fahrenheit number, and 64.4, 77.0, and 86.9 all pass
`warmer_than(20.0)` and all fail `colder_than(30.0)`. The predicates
still read `r.celsius`, so they now compare a Fahrenheit number
against a Celsius limit and quietly answer the wrong question. Nothing
raises an exception, because `to_fahrenheit()` and each predicate are
correct on their own.
The unit lives only in the field name. A stage that changes what a
value means must run after every stage that reads the old meaning.

The last `print()` repeats the chapter's point. `report()` and
`converted_first()` both read `data` and neither writes it, so the
Celsius values stay the same after three traversals, and you can run
either function again and get the same answer.
