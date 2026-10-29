# Foundations: Solutions

## 1. `deposit()` is impure for the same reason `withdraw()` is

> In `pure_functions.py`, write a third function, `deposit(amount)`,
> that behaves like `withdraw()` but adds to `balance` instead of subtracting.
> Explain, the way the text does for `withdraw()`, why `deposit()` is impure.

<details>
<summary>Where to look</summary>

[Pure Functions](../../Chapters/40_Functional--Foundations.md#pure-functions)
explains why `withdraw()` is impure.
Write `deposit()` with the same `global` statement,
then check `deposit()` against each half of the definition.
Call it twice with the same argument and compare the two results.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
type Balance = int

def deposit(amount: int) -> Balance:
    ...
```

<details>
<summary>Done when</summary>

starting from a `balance` of `100`,
`print(deposit(30), deposit(30))` prints `130 160`.
You can also name both halves of the chapter's definition of a pure function that `deposit()` breaks,
and say what you must know to predict a call's result.

<details>
<summary>Solution</summary>

```python
# exercise_1.py
type Balance = int

balance: Balance = 100

def deposit(amount: int) -> Balance:
    global balance
    balance += amount
    return balance

print(deposit(30), deposit(30))
#: 130 160
```

`deposit()` reads and mutates `balance`, a name outside its scope.
A pure function reads only values that stay the same and leaves everything outside itself as it was,
so `deposit()` breaks both halves of that definition.
What `deposit(30)` returns depends on how many times `deposit()`
(or `withdraw()`) has run.
Two identical calls to `deposit(30)` return `130` and then `160`,
where a pure function returns the same value both times.
To predict either result, you must track the history of every prior call.
The chapter makes the same point about `withdraw()`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. A `"*"` operator added to the dispatch table

> In `dispatch.py`, add a `"*"` operator to the `operations` table backed by a new `mul()` function,
> with no change to how you call `operations["*"](6, 4)`.

<details>
<summary>Where to look</summary>

[Functions as First-Class Objects](../../Chapters/40_Functional--Foundations.md#functions-as-first-class-objects)
builds `operations` as a `dict` whose values are functions.
Adding an operator means defining one more function and adding one more key.
The calling expression stays the same because every value in the table has the same signature.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from collections.abc import Callable
from operator import mod
from exceptions import expected

def add(a: int, b: int) -> int:
    ...
def sub(a: int, b: int) -> int:
    ...
def mul(a: int, b: int) -> int:
    ...
def floordiv(a: int, b: int) -> int:
    ...
```

<details>
<summary>Done when</summary>

`operations["*"](6, 4)` returns `24`,
and a loop that calls each symbol the same way prints `* 24` beside the unchanged `+ 10`,
`- 2`, `// 1`, and `% 2`.
`operations["^"]` still raises a `KeyError`, and no calling code changed.

<details>
<summary>Solution</summary>

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
for symbol in ["+", "-", "*", "//", "%"]:
    print(symbol, operations[symbol](6, 4))
#: + 10
#: - 2
#: * 24
#: // 1
#: % 2
with expected(KeyError):
    operations["^"](6, 4)
#: [KeyError] '^'
```

The calling code stays as it was.
Supporting the new operator takes one function and one row in the table.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. A third independent closure

> In `closures.py`, add `quadruple = multiplier(4)` and confirm it behaves independently of `double` and `triple`,
> each holding its own `factor`.

<details>
<summary>Where to look</summary>

[Closures](../../Chapters/40_Functional--Foundations.md#closures)
shows `multiplier()` returning an inner function that captures `factor`.
Each call to `multiplier()` runs the body again and creates a new inner function with its own captured value.
Call `multiplier()` a third time and compare the three results on one input.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from collections.abc import Callable

def multiplier(factor: int) -> Callable[[int], int]:
    ...
```

<details>
<summary>Done when</summary>

`print(double(10), triple(10), quadruple(10))` prints `20 30 40`,
and you can say where each of the three functions keeps its own `factor`.

<details>
<summary>Solution</summary>

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

Each call to `multiplier()` creates a new `multiply` closure with its own private `factor`.
Each function keeps its `factor` in its own closure cell, `__closure__[0]`,
so `inspect.getclosurevars(quadruple).nonlocals` reports `{'factor': 4}`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. A three-stage composition

> In `compose_functions.py`, write a third small function, `square(n)`,
> and build `increment_then_double_then_square = compose(square, increment_then_double)`.
> Predict `increment_then_double_then_square(3)` before running it.

<details>
<summary>Where to look</summary>

[Composing Functions](../../Chapters/40_Functional--Foundations.md#composing-functions)
defines `compose()`,
which returns a function that applies one function to the result of another.
The result of `compose()` is a one-argument function,
so it can be an argument to `compose()` again.
Predict the order in which the three functions run,
then compare with the output.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from collections.abc import Callable

def compose[T, U, V](
    f: Callable[[U], V], g: Callable[[T], U]
) -> Callable[[T], V]:
    ...

def increment(n: int) -> int:
    ...
def double(n: int) -> int:
    ...
def square(n: int) -> int:
    ...
```

<details>
<summary>Done when</summary>

you wrote a prediction before running,
and `increment_then_double_then_square(3)` prints `64`.
If you predicted `20`,
you can say which of the two functions passed to `compose()` runs first,
and why.

<details>
<summary>Solution</summary>

If you read `compose(square, increment_then_double)` left to right and predict that `square` runs first,
you expect `(3 * 3 + 1) * 2 = 20`, but the program prints `64`.
`compose(f, g)` runs `g` first, so the stages run from right to left.
Passing the stages square-first, `compose(increment_then_double, square)`,
prints `20`.
The type checker accepts that call too,
since every stage takes and returns an `int`.

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

`increment_then_double_then_square(3)` runs `increment_then_double(3)` first,
which computes `(3 + 1) * 2 = 8`, then passes that `8` to `square`,
giving `8 * 8 = 64`.
`compose()` supports a third stage as it stands.
Wrapping one composed function inside another `compose()` call extends the pipeline.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 5. Presetting a leading argument, and why the trailing one differs

> In `placeholder.py`, build a second partial, `at_least_ten`,
> that presets `low` to 10 and leaves both other arguments to the caller.
> Then try, with `partial()` and no `Placeholder`,
> to preset `high` and leave `low` and `value` open,
> and explain why that is impossible.

<details>
<summary>Where to look</summary>

[Leaving a Gap with `Placeholder`](../../Chapters/40_Functional--Foundations.md#leaving-a-gap-with-placeholder)
shows how `partial()` fills arguments.
Positional arguments given to `partial()` fill parameters from the left.
For the second half,
build a partial with a keyword argument and see where the failure appears,
then consider how a caller can supply a positional-only parameter.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from functools import partial
from exceptions import expect

def clamp(low: int, value: int, high: int, /) -> int:
    ...
```

<details>
<summary>Done when</summary>

`at_least_ten(3, 100)` returns `10` and `at_least_ten(50, 100)` returns `50`.
Building `partial(clamp, high=100)` succeeds,
and calling it with `0, 5` raises a `TypeError` naming `'high'` as positional-only.
You can say why passing `high` by position defeats the goal.

<details>
<summary>Solution</summary>

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

**Preset the leading argument.**
`at_least_ten` needs no `Placeholder`.
`low` is the first parameter,
and `partial()` fills positional arguments from the left,
so `value` and `high` stay open in order.

If you build `at_least_ten` as `partial(clamp, 10, Placeholder, Placeholder)`,
the `partial()` call raises a `TypeError` before you call the result:
"trailing Placeholders are not allowed."
A placeholder at the end marks a position the call's arguments would fill on their own,
because `partial()` appends them after the bound ones.
The library rejects that placeholder as redundant, as the chapter says.

**Show where the keyword fails.**
Presetting `high` alone needs a `Placeholder`.
`partial()` stores its arguments, and the signature check waits for the call,
so building `partial(clamp, high=100)` succeeds.
`high` is positional-only, so the call must pass it by position.

Passing `high` positionally means passing `low` and `value` first,
which is the opposite of leaving them to the caller.
`Placeholder` exists for that case.
`partial(clamp, Placeholder, Placeholder, 100)` presets `high` and leaves `low` and `value` to the caller.

**Suppress the type checker's report.**
The `# type: ignore` silences the type checker,
which finds the mistake earlier than the runtime does.
`ty` reports `positional-only-parameter-as-kwarg` on `partial(clamp, high=100)`,
which builds the partial,
and `missing-argument` on the `expect()` call that passes it `0, 5` with no `high`.
Both reports fall on one line, so one comment covers them.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. `Final` locks the name, not the object

> In `immutable_types.py`,
> add `CONFIG: Final[list[int]] = [1, 2]` and a line that appends to it.
> Run `ty`, which accepts the append.
> Then add `MAX_SIZE = 200`, run `ty` again,
> and explain why the rebinding is an error while the append is not.
> Then change the annotation so `ty` rejects the append.

<details>
<summary>Where to look</summary>

[Immutability in Annotations](../../Chapters/40_Functional--Foundations.md#immutability-in-annotations)
contrasts `Final` with a read-only type such as `Sequence`.
`Final` constrains a name's binding,
and the object's type decides which methods you can call.
To make the append an error,
annotate with an immutable type such as `tuple[int, ...]` and assign a tuple.
A `Sequence` annotation is not enough.
For a `Final` name, the checker keeps the assigned list's own type,
so the append still passes.

<details>
<summary>Done when</summary>

`ty` reports `invalid-assignment` on `MAX_SIZE = 200` and accepts `CONFIG.append(3)`,
and you can say why.
After your annotation change, `ty` reports `unresolved-attribute` on the append.
If the type checker still passes the append,
your annotation leaves the value's type mutable.

<details>
<summary>Solution</summary>

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

**Separate mutation from rebinding.**
`Final` constrains the binding between a name and an object.
`CONFIG` must keep pointing at the same list forever.
`Final` leaves that list's contents free to change,
so the type checker accepts `CONFIG.append(3)`.
`append()` mutates the object and leaves the binding alone.
`MAX_SIZE = 200` is the operation `Final` exists to reject,
because it binds the name to a different object.

**Suppress the rebinding error.**
The reassignment carries a `# type: ignore` so the listing passes the book's build.
With that comment removed, `ty` reports the reassignment and accepts the append:

```
error[invalid-assignment]: Reassignment of `Final` symbol `MAX_SIZE` is not allowed
 --> exercise_6.py:7:1
  |
6 | MAX_SIZE: Final[int] = 100
  |           ---------- Symbol declared as `Final` here
7 | MAX_SIZE = 200
  | ^^^^^^^^^^^^^^ Symbol later reassigned here
```

For the checker to reject the append, the value's own type must be immutable:

```python
# exercise_6_tuple.py
from typing import Final

CONFIG: Final[tuple[int, ...]] = (1, 2)
print(CONFIG)
#: (1, 2)
```

If you add `CONFIG.append(3)` to that version, `ty` reports:

```
error[unresolved-attribute]: Object of type `tuple[Literal[1], Literal[2]]` has no attribute `append`
```

The error comes from the tuple type rather than from `Final`.
That split is the chapter's point:
`Final` makes the checker reject a rebinding of the name,
and the value's own type makes it reject a change to the contents.
You need both.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 7. Comprehensions, a different `key`, and a bare `map` object

> In `higher_order.py`,
> replace the `map()` and `filter()` calls with comprehensions,
> and the `sorted(key=len)` call with one that sorts by last letter.
> Then start again from the original file,
> delete the `list()` around the `map()` call, print the result,
> and say what you see and why.

<details>
<summary>Where to look</summary>

[Higher-Order Functions](../../Chapters/40_Functional--Foundations.md#higher-order-functions)
shows `map()`, `filter()`, and `sorted()` with a `key` function.
A comprehension with a condition replaces `filter()`,
and a `lambda` taking a word and returning its last letter replaces `len`.
For the bare `map` object, print it,
then consume it twice with `list()` and compare the two results.

<details>
<summary>Done when</summary>

your comprehensions print `[1, 4, 9, 16, 25]` and `[2, 4]`,
and the last-letter sort prints `['banana', 'pie', 'kiwi', 'watermelon']`.
You can say why that is the input order.
The bare `map()` result prints as `<map object at 0x...>`,
and a second `list()` over it gives `[]`.

<details>
<summary>Solution</summary>

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

**Write the expressions inline.**
The chapter's rule of thumb picks the comprehension for an expression you write inline.

**Change the sort key.**
The last letters `a`, `e`, `i`,
and `n` appear in alphabetical order in the list,
so sorting by last letter returns the words in their original order.
The chapter's `key=len`, by contrast, puts `pie` first.

Without the `list()`, `raw` is a `map` object:

```python
# exercise_7_map.py
numbers = [1, 2, 3, 4, 5]
raw = map(lambda n: n * n, numbers)
print(type(raw).__name__)
#: map
print(list(raw))  # [1]
#: [1, 4, 9, 16, 25]
print(list(raw))  # [2]
#: []
```

**Inspect the lazy object.**
Printing `raw` bare shows `<map object at 0x...>` in place of the values.
`map()` returns a lazy iterator that computes each value on demand,
so its `repr()` shows the type and an address.
The listing prints the type's name, since the address changes from run to run.

**Exhaust the iterator.**
The second `list(raw)`, at `[2]`, is the more dangerous half.
It returns `[]` instead of raising an exception.
The first `list(raw)`, at `[1]`, consumed the iterator, which stays exhausted,
so every later pass gets an empty result.
A comprehension, by contrast, returns a complete list,
which you can walk as many times as you like.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 8. Only the assigned name needs `nonlocal`

> In `make_counter.py`, give `make_counter()` a `step: int = 1` parameter,
> so `make_counter(10)` builds a counter that counts 10, 20, 30.
> `increment()` reads `step` without declaring it `nonlocal`.
> Explain why `count` needs the declaration and `step` does not.
> Then delete the `nonlocal` line and compare the type checker's report with the runtime failure.

<details>
<summary>Where to look</summary>

[Closures](../../Chapters/40_Functional--Foundations.md#closures)
introduces `make_counter()` and the `nonlocal` declaration.
Python treats a name assigned anywhere in a function as local to that function,
and looks in the enclosing scope for every other name the function reads.
Remove `nonlocal`, run `ty`, then run the program,
and compare where each one reports the problem.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
from collections.abc import Callable

def make_counter(step: int = 1) -> Callable[[], int]:
    ...
```

<details>
<summary>Done when</summary>

`make_counter(10)` gives a counter whose three calls print `10 20 30`.
With `nonlocal` deleted, `ty` reports `unresolved-reference` on `count += step`,
and the first call raises an `UnboundLocalError`.
You can say why assigning `count` makes it local while reading `step` does not.

<details>
<summary>Solution</summary>

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

**Declare the name you assign.**
`increment()` reads `step` the way `multiply()` reads `factor` in `multiplier()`,
so Python finds `step` in the enclosing scope.
`count` differs because `increment()` assigns it.
Assignment is how Python decides a name is local.
Without `nonlocal`, that assignment makes `count` a local of `increment()`,
so `count += step` reads the local before it holds a value.

Deleting the `nonlocal` line produces two errors, in order.
`ty` reports `Name 'count' used when not defined` on the `count += step` line before the program runs.
Running the program raises an `UnboundLocalError` at the first `tally()` call:
"cannot access local variable 'count' where it is not associated with a value."
The type checker points at the assignment that went wrong.
The runtime message names the local variable that assignment created by accident.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 9. A second filter, and why the stages are not interchangeable

> In `pipeline.py`, add `colder_than(limit, r)` beside `warmer_than()`,
> and give `report()` a second `filter()` stage built with `partial()`,
> so only readings between 20.0 and 30.0 Celsius reach the output.
> Then write a second version of `report()` that calls `map(to_fahrenheit, ...)` ahead of both filters,
> and explain the list it returns.

<details>
<summary>Where to look</summary>

[Putting the Pieces Together](../../Chapters/40_Functional--Foundations.md#putting-the-pieces-together)
chains `filter()` and `map()` over `Reading` values,
with `partial()` binding the limit.
Chain a second `filter()` onto the first, each with its own `partial()`.
In the second version of `report()`,
check which field the predicates read and what unit `map()` has put in it.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_9.py
from collections.abc import Sequence
from functools import partial
from record import record

@record
class Reading:
    sensor: str
    celsius: float

def warmer_than(limit: float, r: Reading) -> bool:
    ...

def colder_than(limit: float, r: Reading) -> bool:
    ...

def to_fahrenheit(r: Reading) -> Reading:
    ...

def report(readings: Sequence[Reading]) -> list[str]:
    ...

def converted_first(
    readings: Sequence[Reading],
) -> list[str]:
    ...
```

<details>
<summary>Done when</summary>

`report(data)` on the chapter's three readings returns `['b 77.0']`,
and your second version, with `map(to_fahrenheit, ...)` first, returns `[]`.
You can say which field the predicates read and what unit it holds after the `map()`.

<details>
<summary>Solution</summary>

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

**Add the upper bound.**
`colder_than()` mirrors `warmer_than()`,
and `partial()` turns each into the one-argument callable `filter()` requires.

**Narrow to the band.**
The two filters commute, because each one tests the same original Celsius value.
Applying the `colder_than()` filter first reports the same reading.

**Reorder the stages.**
The empty list from `converted_first()` shows that the `map()` does not commute with the filters.
Once `to_fahrenheit()` has run, every reading carries a Fahrenheit number.
The predicates still read `r.celsius`,
so they now compare a Fahrenheit number against a Celsius limit.
The Fahrenheit values 64.4, 77.0,
and 86.9 all pass `warmer_than(20.0)` and all fail `colder_than(30.0)`.

Every stage runs cleanly,
because `to_fahrenheit()` and each predicate are correct on their own.
The field name `celsius` alone records the unit.
`to_fahrenheit()` stores a Fahrenheit number under that name,
so the field's name and its value disagree.
A stage that changes what a value means must run after every stage that reads the old meaning.

**Show the input untouched.**
The Celsius values stay the same after both calls,
so running either function again gives the same answer.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
