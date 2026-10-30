# Multiple Dispatching: Solutions

Every exercise that adds `Lizard` uses the same rule:
`Lizard` beats Paper and Scissors, and loses to Rock.
Lizard versus Lizard is a draw.

## 1. Adding `Lizard` to the table version

> Add a fourth `Item`, `Lizard`, to `paper_scissors_rock_table.py`.
> Lizard beats Paper and Scissors, and loses to Rock.
> Lizard versus Lizard is a draw.
> Add the seven new entries that `OUTCOME` needs:
> both orders of each mixed pair, plus Lizard versus Lizard.

<details>
<summary>Where to look</summary>

[One Lookup in a Table](../../Chapters/32_Patterns--Multiple_Dispatching.md#one-lookup-in-a-table)
shows that `OUTCOME` is a dictionary keyed on a pair of classes.
Adding a class changes the dictionary and leaves every method alone,
so `compete()` stays as it is.
Write one entry for each ordered pair of `Lizard` with another item,
and one for `Lizard` against `Lizard`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from enum import StrEnum
from typing import Final

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Item:
    def compete(self, opponent: Item) -> Outcome:
        ...

    def __str__(self) -> str:
        ...

class Paper(Item):
    pass
class Scissors(Item):
    pass
class Rock(Item):
    pass
class Lizard(Item):
    pass

type Table = dict[tuple[type[Item], type[Item]], Outcome]

OUTCOME: Final[Table] = {
  (Paper, Rock): Outcome.WIN,
  (Paper, Scissors): Outcome.LOSE,
  (Paper, Paper): Outcome.DRAW,
  (Paper, Lizard): Outcome.LOSE,
  (Scissors, Paper): Outcome.WIN,
  (Scissors, Rock): Outcome.LOSE,
  (Scissors, Scissors): Outcome.DRAW,
  (Scissors, Lizard): Outcome.LOSE,
  (Rock, Scissors): Outcome.WIN,
  (Rock, Paper): Outcome.LOSE,
  (Rock, Rock): Outcome.DRAW,
  (Rock, Lizard): Outcome.WIN,
  (Lizard, Paper): Outcome.WIN,
  (Lizard, Scissors): Outcome.WIN,
  (Lizard, Rock): Outcome.LOSE,
  (Lizard, Lizard): Outcome.DRAW,
}
```

<details>
<summary>Done when</summary>

`Lizard().compete(Paper())` and `Rock().compete(Lizard())` both return `win`,
and `compete()` returns an `Outcome` for all sixteen ordered pairs of the four items,
with no `KeyError`.

<details>
<summary>Solution</summary>

If you write one order of a mixed pair, say `(Lizard, Paper)`,
and leave out `(Paper, Lizard)`, the demo prints `win win`,
since both of its duels find their rows.
`Paper().compete(Lizard())` then raises a `KeyError`,
at the first duel that asks for that order.
The table holds one answer per ordered pair,
so the solution writes both orders of each mixed pair.

```python
# exercise_1.py
from enum import StrEnum
from typing import Final

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Item:
    def compete(self, opponent: Item) -> Outcome:
        return OUTCOME[type(self), type(opponent)]

    def __str__(self) -> str:
        return type(self).__name__

class Paper(Item):
    pass
class Scissors(Item):
    pass
class Rock(Item):
    pass
class Lizard(Item):
    pass

type Table = dict[tuple[type[Item], type[Item]], Outcome]

OUTCOME: Final[Table] = {
  (Paper, Rock): Outcome.WIN,
  (Paper, Scissors): Outcome.LOSE,
  (Paper, Paper): Outcome.DRAW,
  (Paper, Lizard): Outcome.LOSE,
  (Scissors, Paper): Outcome.WIN,
  (Scissors, Rock): Outcome.LOSE,
  (Scissors, Scissors): Outcome.DRAW,
  (Scissors, Lizard): Outcome.LOSE,
  (Rock, Scissors): Outcome.WIN,
  (Rock, Paper): Outcome.LOSE,
  (Rock, Rock): Outcome.DRAW,
  (Rock, Lizard): Outcome.WIN,
  (Lizard, Paper): Outcome.WIN,
  (Lizard, Scissors): Outcome.WIN,
  (Lizard, Rock): Outcome.LOSE,
  (Lizard, Lizard): Outcome.DRAW,
}

if __name__ == "__main__":
    print(Lizard().compete(Paper()),
          Rock().compete(Lizard()))
#: win win
```

**Answer every ordered pair.**
Sixteen entries cover the four types against each other (4 × 4),
the same shape as the original nine (3 × 3).
Adding a fourth `Item` requires one class declaration and seven new dictionary rows:
the six ordered pairs `Lizard` forms with the other three,
plus `(Lizard, Lizard)`.
`compete()` stays as it is.

**Guard the demonstration.**
The `__main__` guard lets exercise 3 import this module and skip its demonstration.
The chapter keeps the method version's demonstration in a separate file,
`methods_demo.py`, so importing `paper_scissors_rock.py` loads its definitions alone.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. Adding `Lizard` to the double-dispatch version

> Add the same `Lizard` to `paper_scissors_rock.py`, the method version,
> which means adding an `eval_lizard()` method to every existing class,
> plus a `Lizard` class with its own `compete()` and four `eval_*()` methods.
> Compare how much code this took versus adding `Lizard` to the table version.

<details>
<summary>Where to look</summary>

[Two Dispatches Through Methods](../../Chapters/32_Patterns--Multiple_Dispatching.md#two-dispatches-through-methods)
shows `compete()` calling an `eval_*()` method on the opponent,
so each class answers for one type.
A new class needs its own `compete()` and four `eval_*()` methods,
and every existing class needs an `eval_lizard()`.
Count the methods you wrote,
then compare with the seven dictionary rows the table version needs.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from enum import StrEnum
from typing import Any

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Item:
    def __str__(self) -> str:
        ...

class Paper(Item):
    def compete(self, opponent: Any) -> Outcome:
        ...

    def eval_paper(self, caller: Any) -> Outcome:
        ...

    def eval_scissors(self, caller: Any) -> Outcome:
        ...

    def eval_rock(self, caller: Any) -> Outcome:
        ...

    def eval_lizard(self, caller: Any) -> Outcome:
        ...

class Scissors(Item):
    def compete(self, opponent: Any) -> Outcome:
        ...

    def eval_paper(self, caller: Any) -> Outcome:
        ...

    def eval_scissors(self, caller: Any) -> Outcome:
        ...

    def eval_rock(self, caller: Any) -> Outcome:
        ...

    def eval_lizard(self, caller: Any) -> Outcome:
        ...

class Rock(Item):
    def compete(self, opponent: Any) -> Outcome:
        ...

    def eval_paper(self, caller: Any) -> Outcome:
        ...

    def eval_scissors(self, caller: Any) -> Outcome:
        ...

    def eval_rock(self, caller: Any) -> Outcome:
        ...

    def eval_lizard(self, caller: Any) -> Outcome:
        ...

class Lizard(Item):
    def compete(self, opponent: Any) -> Outcome:
        ...

    def eval_paper(self, caller: Any) -> Outcome:
        ...

    def eval_scissors(self, caller: Any) -> Outcome:
        ...

    def eval_rock(self, caller: Any) -> Outcome:
        ...

    def eval_lizard(self, caller: Any) -> Outcome:
        ...
```

<details>
<summary>Done when</summary>

`Lizard().compete()` returns `win`, `win`, `lose`, `draw` against `Paper`,
`Scissors`, `Rock`, and `Lizard`, each reversed duel returns the opposite result
(a draw stays a draw),
and you can state how many methods you added against exercise 1's seven rows.

<details>
<summary>Solution</summary>

If you forget `eval_lizard()` on one existing class, say `Rock`,
the type checker accepts the call to the missing method,
because every `opponent` and `caller` parameter takes `Any`.
The demo then raises an `AttributeError` at `Lizard().compete(Rock())`,
the first duel that calls the missing method.
That `AttributeError` is the first sign of the mistake,
so the solution adds `eval_lizard()` to all three existing classes.

```python
# exercise_2.py
from enum import StrEnum
from typing import Any

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Item:
    def __str__(self) -> str:
        return type(self).__name__

class Paper(Item):
    def compete(self, opponent: Any) -> Outcome:
        return opponent.eval_paper(self)

    def eval_paper(self, caller: Any) -> Outcome:
        return Outcome.DRAW

    def eval_scissors(self, caller: Any) -> Outcome:
        return Outcome.WIN

    def eval_rock(self, caller: Any) -> Outcome:
        return Outcome.LOSE

    def eval_lizard(self, caller: Any) -> Outcome:
        return Outcome.WIN

class Scissors(Item):
    def compete(self, opponent: Any) -> Outcome:
        return opponent.eval_scissors(self)

    def eval_paper(self, caller: Any) -> Outcome:
        return Outcome.LOSE

    def eval_scissors(self, caller: Any) -> Outcome:
        return Outcome.DRAW

    def eval_rock(self, caller: Any) -> Outcome:
        return Outcome.WIN

    def eval_lizard(self, caller: Any) -> Outcome:
        return Outcome.WIN

class Rock(Item):
    def compete(self, opponent: Any) -> Outcome:
        return opponent.eval_rock(self)

    def eval_paper(self, caller: Any) -> Outcome:
        return Outcome.WIN

    def eval_scissors(self, caller: Any) -> Outcome:
        return Outcome.LOSE

    def eval_rock(self, caller: Any) -> Outcome:
        return Outcome.DRAW

    def eval_lizard(self, caller: Any) -> Outcome:
        return Outcome.LOSE

class Lizard(Item):
    def compete(self, opponent: Any) -> Outcome:
        return opponent.eval_lizard(self)

    def eval_paper(self, caller: Any) -> Outcome:
        return Outcome.LOSE

    def eval_scissors(self, caller: Any) -> Outcome:
        return Outcome.LOSE

    def eval_rock(self, caller: Any) -> Outcome:
        return Outcome.WIN

    def eval_lizard(self, caller: Any) -> Outcome:
        return Outcome.DRAW

if __name__ == "__main__":
    print(Lizard().compete(Paper()),
          Lizard().compete(Scissors()),
          Lizard().compete(Rock()),
          Lizard().compete(Lizard()))
#: win win lose draw
```

**Retrofit every existing class.**
Every existing class (`Paper`, `Scissors`, `Rock`)
needs a new `eval_lizard()` method.

**Give the new class both dispatches.**
The new `Lizard` class needs a `compete()` plus four `eval_*()` methods,
one per opponent type including its own.
Across the four classes,
the `eval_*()` methods encode the sixteen answers that the table version's `OUTCOME` dictionary collects in one place.
The two implementations agree on all sixteen combinations.

**Guard the demonstration.**
The `__main__` guard serves exercise 3, as in exercise 1.

Extending the table takes one class and seven dictionary rows.
Extending the method version takes one class and five new methods,
plus a method retrofitted onto every existing class.
Each item type you add lengthens that list of retrofits.
The chapter therefore recommends the table by default,
and reserves the method version for behavior that belongs to the class:
a combination that reads the object's own state,
or one a subclass should override while inheriting the rest.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. Sixteen matchups in `EXPECTED`

> In `test_paper_scissors.py`, add `Lizard`'s seven matchups to `EXPECTED`,
> taking it from nine entries to sixteen,
> and confirm both versions still agree with each other and with `EXPECTED`.

<details>
<summary>Where to look</summary>

[Testing Both Versions](../../Chapters/32_Patterns--Multiple_Dispatching.md#testing-both-versions)
keeps one `EXPECTED` mapping and checks both implementations against it.
Add the seven `Lizard` rows to that mapping,
keyed on the player's and opponent's class names.
A helper looks each class up by name with `getattr()` on whichever module it receives,
so one mapping checks both versions.
The test reports any disagreement as a failure.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from types import ModuleType
from typing import Final
import exercise_1 as table
import exercise_2 as methods
from exercise_1 import Outcome

type Name = str

EXPECTED: Final[dict[tuple[Name, Name], Outcome]] = {
    ("Paper", "Rock"): Outcome.WIN,
    ("Paper", "Scissors"): Outcome.LOSE,
    ("Paper", "Paper"): Outcome.DRAW,
    ("Paper", "Lizard"): Outcome.LOSE,
    ("Scissors", "Paper"): Outcome.WIN,
    ("Scissors", "Rock"): Outcome.LOSE,
    ("Scissors", "Scissors"): Outcome.DRAW,
    ("Scissors", "Lizard"): Outcome.LOSE,
    ("Rock", "Scissors"): Outcome.WIN,
    ("Rock", "Paper"): Outcome.LOSE,
    ("Rock", "Rock"): Outcome.DRAW,
    ("Rock", "Lizard"): Outcome.WIN,
    ("Lizard", "Paper"): Outcome.WIN,
    ("Lizard", "Scissors"): Outcome.WIN,
    ("Lizard", "Rock"): Outcome.LOSE,
    ("Lizard", "Lizard"): Outcome.DRAW,
}

def compete(module: ModuleType, player: Name,
            opponent: Name) -> str:
    ...
```

<details>
<summary>Done when</summary>

`uv run pytest` on your `test_paper_scissors.py`,
run against your exercise 1 and exercise 2 versions, reports 32 passed:
sixteen `EXPECTED` cases for each version.

<details>
<summary>Solution</summary>

If you add the seven rows to `EXPECTED` and leave the test importing the chapter's `paper_scissors_rock` and `paper_scissors_rock_table`,
every `Lizard` case fails with an `AttributeError`: fourteen of the 32 cases,
seven per module.
The chapter modules define `Paper`, `Scissors`, and `Rock`,
so `getattr()` raises `AttributeError` when it looks up `"Lizard"`.
The solution points both imports at exercises 1 and 2.

```python
# exercise_3.py
from types import ModuleType
from typing import Final
import exercise_1 as table
import exercise_2 as methods
from exercise_1 import Outcome

type Name = str

EXPECTED: Final[dict[tuple[Name, Name], Outcome]] = {
    ("Paper", "Rock"): Outcome.WIN,
    ("Paper", "Scissors"): Outcome.LOSE,
    ("Paper", "Paper"): Outcome.DRAW,
    ("Paper", "Lizard"): Outcome.LOSE,
    ("Scissors", "Paper"): Outcome.WIN,
    ("Scissors", "Rock"): Outcome.LOSE,
    ("Scissors", "Scissors"): Outcome.DRAW,
    ("Scissors", "Lizard"): Outcome.LOSE,
    ("Rock", "Scissors"): Outcome.WIN,
    ("Rock", "Paper"): Outcome.LOSE,
    ("Rock", "Rock"): Outcome.DRAW,
    ("Rock", "Lizard"): Outcome.WIN,
    ("Lizard", "Paper"): Outcome.WIN,
    ("Lizard", "Scissors"): Outcome.WIN,
    ("Lizard", "Rock"): Outcome.LOSE,
    ("Lizard", "Lizard"): Outcome.DRAW,
}

def compete(module: ModuleType, player: Name,
            opponent: Name) -> str:
    result = getattr(module, player)().compete(
        getattr(module, opponent)())
    assert isinstance(result, module.Outcome)
    return result

for module in (table, methods):
    wrong = [pair for pair, result in EXPECTED.items()
             if compete(module, *pair) != result]
    print(module.__name__, len(EXPECTED), "agree:",
          not wrong)
#: exercise_1 16 agree: True
#: exercise_2 16 agree: True
```

**Check both versions against one mapping.**
The test's helper, `compete()`,
looks each class up by name on whichever module it receives,
so one `EXPECTED` checks both sets of classes.

**Compare across separate enumerations.**
Each module defines its own `Outcome`.
The comparison still works, since a `StrEnum` member equals its string value.

The test in `test_paper_scissors.py` needs two changes once its two imports name modules that include `Lizard`.
One is the sixteen-entry `EXPECTED`.
The other is in the `compete()` helper.
Each of those modules defines its own `Outcome`,
so the chapter's `isinstance(result, Outcome)` assertion fails.
The solution's `compete()` asserts against `module.Outcome`:
the enumeration of the module that produced the result.
The helper's return annotation loosens from `Outcome` to `str`,
the base class that both modules' `Outcome` enumerations share,
but the assertion still rejects a version that returns the bare string `"win"`.

`test_versions_match_expected()` takes its cases from `EXPECTED`.
`pytest` parametrizes it with the keys of that mapping,
so the test reports sixteen cases per module where it reported nine.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. Counting how often each item type appears

> `all_pairs()` yields each pair of types once.
> A tournament of random duels needs a second generator.
> In `arena.py`, write `random_pairs(base, n, counts)`,
> which draws `n` random pairs from `base.__subclasses__()` and yields each as a `(player, opponent)` tuple.
> Give it an optional `counts: Counter[str] | None = None` parameter,
> and have it update that counter in place with a tally of every item type it chooses.
> The counter fills only as you consume the generator,
> so pass in your own `Counter`,
> iterate over all 100 pairs from `random_pairs(Item, 100, counts)`,
> and then print how many times `Lizard` appeared.

<details>
<summary>Where to look</summary>

Write `random_pairs()` as a generator,
like the chapter's `all_pairs()` in `arena.py`,
so its body runs only as you iterate over it.
When `counts` is `None`, create a fresh `Counter` so the body has a single path.
Increment the count for each item inside the loop, before the `yield`,
so the caller's own `Counter` fills as the loop consumes the pairs.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
import random
from collections import Counter
from collections.abc import Iterator
from enum import StrEnum
from typing import Any, Final

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Item:
    def compete(self, opponent: Item) -> Outcome:
        ...

    def __str__(self) -> str:
        ...

class Paper(Item):
    pass
class Scissors(Item):
    pass
class Rock(Item):
    pass
class Lizard(Item):
    pass

type Table = dict[tuple[type[Item], type[Item]], Outcome]

OUTCOME: Final[Table] = {
  (Paper, Rock): Outcome.WIN,
  (Paper, Scissors): Outcome.LOSE,
  (Paper, Paper): Outcome.DRAW,
  (Paper, Lizard): Outcome.LOSE,
  (Scissors, Paper): Outcome.WIN,
  (Scissors, Rock): Outcome.LOSE,
  (Scissors, Scissors): Outcome.DRAW,
  (Scissors, Lizard): Outcome.LOSE,
  (Rock, Scissors): Outcome.WIN,
  (Rock, Paper): Outcome.LOSE,
  (Rock, Rock): Outcome.DRAW,
  (Rock, Lizard): Outcome.WIN,
  (Lizard, Paper): Outcome.WIN,
  (Lizard, Scissors): Outcome.WIN,
  (Lizard, Rock): Outcome.LOSE,
  (Lizard, Lizard): Outcome.DRAW,
}

def duel(player: Any, opponent: Any) -> None:
    ...

def random_pairs[T](base: type[T], n: int,
                    counts: Counter[str] | None = None
                    ) -> Iterator[tuple[T, T]]:
    ...
```

<details>
<summary>Done when</summary>

after your loop over `random_pairs(Item, 100, counts)`,
the four counts sum to 200, two per pair, and `counts["Lizard"]` is near 50.
Printing `counts["Lizard"]` before the loop shows `0`.

<details>
<summary>Solution</summary>

If you print `counts["Lizard"]` right after calling `random_pairs(Item, 100, counts)`,
before iterating over the generator, the `print()` shows `0`.
Calling a generator function returns a generator object,
and the body starts at the first `next()`.
Until then the counter stays empty.
The solution's loop consumes all 100 pairs before it reads the count.

```python
# exercise_4.py
import random
from collections import Counter
from collections.abc import Iterator
from enum import StrEnum
from typing import Any, Final

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Item:
    def compete(self, opponent: Item) -> Outcome:
        return OUTCOME[type(self), type(opponent)]

    def __str__(self) -> str:
        return type(self).__name__

class Paper(Item):
    pass
class Scissors(Item):
    pass
class Rock(Item):
    pass
class Lizard(Item):
    pass

type Table = dict[tuple[type[Item], type[Item]], Outcome]

OUTCOME: Final[Table] = {
  (Paper, Rock): Outcome.WIN,
  (Paper, Scissors): Outcome.LOSE,
  (Paper, Paper): Outcome.DRAW,
  (Paper, Lizard): Outcome.LOSE,
  (Scissors, Paper): Outcome.WIN,
  (Scissors, Rock): Outcome.LOSE,
  (Scissors, Scissors): Outcome.DRAW,
  (Scissors, Lizard): Outcome.LOSE,
  (Rock, Scissors): Outcome.WIN,
  (Rock, Paper): Outcome.LOSE,
  (Rock, Rock): Outcome.DRAW,
  (Rock, Lizard): Outcome.WIN,
  (Lizard, Paper): Outcome.WIN,
  (Lizard, Scissors): Outcome.WIN,
  (Lizard, Rock): Outcome.LOSE,
  (Lizard, Lizard): Outcome.DRAW,
}

def duel(player: Any, opponent: Any) -> None:
    result = player.compete(opponent)
    print(f"{player} <--> {opponent} : {result}")

def random_pairs[T](base: type[T], n: int,
                    counts: Counter[str] | None = None
                    ) -> Iterator[tuple[T, T]]:
    if counts is None:
        counts = Counter()
    items = base.__subclasses__()
    for _ in range(n):
        a, b = (random.choice(items)(),
                random.choice(items)())
        counts[type(a).__name__] += 1
        counts[type(b).__name__] += 1
        yield a, b

random.seed(47)
counts: Counter[str] = Counter()
for player, opponent in random_pairs(Item, 100, counts):
    pass  # duel(player, opponent) in the real version
print(counts["Lizard"])
#: 53
```

**Make the tally optional.**
`counts` is an optional parameter with a default of `None`,
so a caller that needs only the pairs writes `random_pairs(Item, 10)`.

**Tally into the caller's counter.**
A caller that needs the tally passes its own `Counter`.
The generator updates that counter in place for every pair it produces,
one increment per item,
so the caller can read `counts["Lizard"]` during or after the loop.
With the same seed, `random_pairs()` yields the same pairs whether or not it counts them.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 5. `__sub__()` and `__rsub__()` on `Meters`

> Give `Meters` a `__sub__()` and a `__rsub__()`.
> `__sub__()` handles a `Meters`, an `int`, or a `float`,
> and returns `NotImplemented` for anything else.
> `__rsub__()` needs only the `int` and `float` cases,
> since Python skips the reflected form when both operands are `Meters`.
> Subtraction does not commute, so the reflected form must undo the swap.
> Check that `10 - Meters(3)` produces `Meters(7)` rather than `Meters(-7)`.
> Then confirm that `"ten" - Meters(3)` raises a `TypeError` rather than producing a `Meters`.

<details>
<summary>Where to look</summary>

[Operators Dispatch Twice](../../Chapters/32_Patterns--Multiple_Dispatching.md#operators-dispatch-twice)
shows `__add__()` returning `NotImplemented` so Python retries with `__radd__()` on the other operand.
Use the same protocol for subtraction,
with an `isinstance()` check per accepted type and `NotImplemented` for the rest.
In `__rsub__()`, `self` is the right-hand operand,
so compute the other value minus `self.n` to undo the swap.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from exceptions import expected
from record import record

@record
class Meters:
    n: float

    def __sub__(self, other: object) -> Meters:
        ...

    def __rsub__(self, other: object) -> Meters:
        ...
```

<details>
<summary>Done when</summary>

`10 - Meters(3)` prints `Meters(n=7)`,
as do `Meters(10) - Meters(3)` and `Meters(10) - 3`,
and `"ten" - Meters(3)` raises a `TypeError` whose message reads `unsupported operand type(s) for -: 'str' and 'Meters'`.

<details>
<summary>Solution</summary>

If you give `__rsub__()` the body of `__sub__()`,
`10 - Meters(3)` prints `Meters(n=-7)`,
while the other lines print what they should.
The type checker accepts the variant, since both orders produce a `Meters`.
The solution computes `other - self.n`,
because Python passes the left operand to the reflected method as `other`.

```python
# exercise_5.py
from exceptions import expected
from record import record

@record
class Meters:
    n: float

    def __sub__(self, other: object) -> Meters:
        if isinstance(other, Meters):
            return Meters(self.n - other.n)
        if isinstance(other, int | float):
            return Meters(self.n - other)
        return NotImplemented

    def __rsub__(self, other: object) -> Meters:
        if isinstance(other, int | float):
            # Not self.n - other
            return Meters(other - self.n)
        return NotImplemented

print(Meters(10) - Meters(3), Meters(10) - 3)
#: Meters(n=7) Meters(n=7)
print(10 - Meters(3))
#: Meters(n=7)
with expected(TypeError):
    "ten" - Meters(3)
#: [TypeError] unsupported operand type(s) for -: 'str' and
#: 'Meters'
```

**Handle each accepted type.**
`__sub__()` is `__add__()` with the sign changed.
`__rsub__()` needs only the numeric case,
because Python calls the left operand's method first,
and `Meters.__sub__()` handles `Meters(10) - Meters(3)`.
Python skips the reflected form when both operands have the same type,
so no call to `__rsub__()` receives two `Meters`.

**Undo the swap.**
The swap is where subtraction differs from addition.
Python calls `Meters.__rsub__(Meters(3), 10)` for the expression `10 - Meters(3)`,
so `self` is the right operand and `other` is the left one.
The method must put them back in the order the source wrote them.
Copying the body of `__sub__()`, `Meters(self.n - other)`, gives `Meters(-7)`.
The copied `__rsub__()` looks correct and returns a `Meters` for every number,
yet each result is the negative of the right answer.
Addition commutes, so the same copied body in `__radd__()` gives the right answer every time.

**Decline an unsupported operand.**
`"ten" - Meters(3)` finds no `str.__sub__()`,
so Python calls `Meters.__rsub__()` next,
which returns `NotImplemented` for a `str`.
With both sides declining, Python raises `TypeError`,
whose message names both types.

Returning `NotImplemented`, rather than raising an exception,
lets Python report both operand types.
An exception raised inside `__rsub__()` carries the message `Meters` wrote,
in place of Python's `unsupported operand type(s)` message,
which names both types.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. Making the table tolerate subclasses

> Subclass `Paper` as `Origami` and duel it against `Rock` in the table version,
> as `exact_match.py` does.
> Explain the `KeyError` in terms of how the lookup matches.
> Then make the table match subclasses by walking both operands' `__mro__` for the first pair that has a row.
> Say what becomes of each of the two properties the lookup shares with the table-driven state machine:
> exact matching, and failure at the first duel that needs a missing pair.

<details>
<summary>Where to look</summary>

[One Lookup in a Table](../../Chapters/32_Patterns--Multiple_Dispatching.md#one-lookup-in-a-table)
shows `exact_match.py`, where the key uses `type()`.
A dictionary probe compares keys by equality,
so a subclass needs rows of its own.
Every class has an `__mro__` tuple that lists it and then its bases in lookup order.
Loop over one operand's `__mro__`,
and inside that loop over the other operand's `__mro__`.
Skip classes that are not an `Item` (such as `object`),
and return the first pair that has a row in `OUTCOME`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
from enum import StrEnum
from typing import Final

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Item:
    def compete(self, opponent: Item) -> Outcome:
        ...
    def __str__(self) -> str:
        ...

class Paper(Item):
    pass
class Rock(Item):
    pass

type Table = dict[tuple[type[Item], type[Item]], Outcome]

OUTCOME: Final[Table] = {
    (Paper, Rock): Outcome.WIN,
    (Rock, Paper): Outcome.LOSE,
}

class Origami(Paper):
    pass

class TolerantItem(Item):
    def compete(self, opponent: Item) -> Outcome:
        ...

class TolerantPaper(TolerantItem):
    pass
class TolerantRock(TolerantItem):
    pass
class TolerantOrigami(TolerantPaper):
    pass
```

<details>
<summary>Done when</summary>

`Origami().compete(Rock())` first reproduces the `KeyError ['Origami', 'Rock']` line from `exact_match.py`.
After your change it returns `win`, `Rock().compete(Origami())` returns `lose`,
and a new direct subclass of `Item` with no rows still raises a `KeyError` at its first duel.

<details>
<summary>Solution</summary>

If you walk the left operand's MRO and key the right on `type(opponent)` as it is,
`TolerantOrigami().compete(TolerantRock())` still prints `win`,
but `TolerantRock().compete(TolerantOrigami())` raises a `KeyError` for `(TolerantRock, TolerantOrigami)`.
A subclass can sit on either side of a duel, so the solution walks both MROs.

```python
# exercise_6.py
from enum import StrEnum
from typing import Final

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Item:
    def compete(self, opponent: Item) -> Outcome:
        return OUTCOME[type(self), type(opponent)]
    def __str__(self) -> str:
        return type(self).__name__

class Paper(Item):
    pass
class Rock(Item):
    pass

type Table = dict[tuple[type[Item], type[Item]], Outcome]

OUTCOME: Final[Table] = {
    (Paper, Rock): Outcome.WIN,
    (Rock, Paper): Outcome.LOSE,
}

class Origami(Paper):
    pass

try:
    Origami().compete(Rock())
except KeyError as e:
    print(type(e).__name__, [c.__name__ for c in e.args[0]])
#: KeyError ['Origami', 'Rock']

class TolerantItem(Item):
    def compete(self, opponent: Item) -> Outcome:
        for left in type(self).__mro__:
            for right in type(opponent).__mro__:
                if not (issubclass(left, Item)
                        and issubclass(right, Item)):
                    continue  # object is not an Item
                if (left, right) in OUTCOME:
                    return OUTCOME[left, right]
        raise KeyError((type(self), type(opponent)))

class TolerantPaper(TolerantItem):
    pass
class TolerantRock(TolerantItem):
    pass
class TolerantOrigami(TolerantPaper):
    pass

OUTCOME[TolerantPaper, TolerantRock] = Outcome.WIN
OUTCOME[TolerantRock, TolerantPaper] = Outcome.LOSE

print(TolerantOrigami().compete(TolerantRock()))
#: win
```

**Reproduce the exact-match failure.**
The `KeyError` comes from a dictionary probe,
which hashes the key and compares it by equality.
Neither step consults an MRO, so the lookup ignores inheritance.
`Origami` inherits from `Paper` but is a different class,
so `(Origami, Rock)` and `(Paper, Rock)` are different keys.
That is what the chapter's "matches classes exactly" means.
Exact matching sets the table apart from `singledispatch`,
which resolves through the MRO.

**Fall back to an ancestor's row.**
The tolerant version walks both MROs and takes the first pair that has a row,
so `TolerantOrigami` finds `(TolerantPaper, TolerantRock)` one step up on the left.
That version gives up the property the chapter names first, exact matching.
The match now follows inheritance.
That change has three consequences.

The lookup becomes a nested loop over two MROs instead of one probe,
so a miss now takes as many probes as the product of the two depths.
For a table consulted once per duel, that time is negligible.
In an inner loop, it matters.

Order now decides the answer.
`(TolerantPaper, TolerantRock)` and `(TolerantOrigami, TolerantItem)` can both match.
The order in which the loops walk picks the one that wins.
That rule lives in `compete()` instead of in the table.
The exact version settles the question with one probe.
Either the pair is in the table or it is not.

The tolerant version also gives up the `KeyError` that makes the exact version safe,
for one kind of new type: a subclass of a concrete item.
An `Origami(Paper)` whose rows you forgot to write silently inherits `Paper`'s answers and plays as paper.
A `Lizard(TolerantItem)` still fails fast,
since every row's key names two concrete items,
and `Lizard`'s ancestors are `TolerantItem`, `Item`, and `object`.
Tolerance lets you write fewer rows,
but for a subclass of an existing item it drops the fail-fast policy the chapter recommends for a table under construction.
That subclass is the new type most likely to receive an old type's answers by mistake.

Which behavior you want depends on whether a subclass is a new competitor or a variation on an existing one.
`Origami` is paper for the purposes of this game.
A `WetPaper` that loses to everything is a new competitor.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 7. A business-modeling environment

> Create a business-modeling environment with three types of `Inhabitant`:
> `Dwarf` (for engineers), `Elf` (for marketers), and `Troll` (for managers).
> Now create a class called `Project` that creates the different inhabitants and causes them to `interact()` with each other.
> Single dispatch is enough here.
> The next exercise adds the second dispatch.

<details>
<summary>Where to look</summary>

[Two Dispatches Through Methods](../../Chapters/32_Patterns--Multiple_Dispatching.md#two-dispatches-through-methods)
starts with one dispatch, a method call that resolves its receiver's type.
Give `Inhabitant` an `interact()` method and override it in `Dwarf`, `Elf`,
and `Troll`.
`Project` creates the inhabitants with a seeded `random.Random` and calls `interact()` on neighboring pairs.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
import random
from typing import Any

class Inhabitant:
    def interact(self, other: Any) -> str:
        ...

    def __str__(self) -> str:
        ...

class Dwarf(Inhabitant):
    def interact(self, other: Any) -> str:
        ...

class Elf(Inhabitant):
    def interact(self, other: Any) -> str:
        ...

class Troll(Inhabitant):
    def interact(self, other: Any) -> str:
        ...

class Project:
    def __init__(self, seed: int = 0) -> None:
        ...

    def gather(self, n: int) -> list[Inhabitant]:
        ...

    def meet(self, n: int) -> None:
        ...
```

<details>
<summary>Done when</summary>

your `Project` prints one line per `interact()` call,
and each line's wording comes from the calling inhabitant's type:
a `Troll` addresses a `Dwarf` the same way it addresses an `Elf`,
and swapping the two inhabitants of a pair changes the line.

<details>
<summary>Solution</summary>

```python
# exercise_7.py
import random
from typing import Any

class Inhabitant:
    def interact(self, other: Any) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return type(self).__name__

class Dwarf(Inhabitant):
    def interact(self, other: Any) -> str:
        return f"{self} (engineer) negotiates with {other}"

class Elf(Inhabitant):
    def interact(self, other: Any) -> str:
        return f"{self} (marketer) pitches to {other}"

class Troll(Inhabitant):
    def interact(self, other: Any) -> str:
        return f"{self} (manager) directs {other}"

class Project:
    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random(seed)

    def gather(self, n: int) -> list[Inhabitant]:
        kinds = [Dwarf, Elf, Troll]
        return [self.rng.choice(kinds)() for _ in range(n)]

    def meet(self, n: int) -> None:
        team = self.gather(n)
        for a, b in zip(team, team[1:]):
            print(a.interact(b))

Project(seed=1).meet(4)
#: Dwarf (engineer) negotiates with Troll
#: Troll (manager) directs Dwarf
#: Dwarf (engineer) negotiates with Elf
```

**Resolve the receiver's type.**
Exercise 7 uses single dispatch, not double.
`a.interact(b)` resolves on `a`'s type alone.
Each `interact()` interpolates `other` into its message the same way,
whatever `other`'s type.
The design becomes double dispatch when `interact()`'s behavior must vary by `other`'s type too.
Exercise 8 adds that dependence.

**Stage the meetings.**
`Project` creates the inhabitants in `gather()` and makes neighbors interact in `meet()`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 8. Weapons, battles, and a full meeting

> Modify the previous exercise's `Project` to make the interactions more detailed.
> Each `Inhabitant` can randomly produce a `Weapon` using `get_weapon()`:
> a `Dwarf` uses `Jargon` or `Play`,
> an `Elf` uses `InventFeature` or `SellImaginaryProduct`,
> and a `Troll` uses `Edict` or `Schedule`.
> You must decide which weapons "win" and "lose" in each interaction
> (as in `paper_scissors_rock.py`).
> Add a `battle()` method to `Project` that takes two `Inhabitant`s and matches them against each other.
> Now create a `meeting()` method for `Project` that creates groups of `Dwarf`,
> `Elf`, and `Troll` and battles the groups against each other until only members of one group remain.
> These are the "winners."

<details>
<summary>Where to look</summary>

[Two Dispatches Through Methods](../../Chapters/32_Patterns--Multiple_Dispatching.md#two-dispatches-through-methods)
shows the `compete()` and `eval_*()` pair that resolves both types.
Give `Weapon` the same pair for six weapon classes,
and let each `Inhabitant` kind hold a `WEAPONS` tuple from which `get_weapon()` picks one at random.
Rank the weapons around a cycle.
An even count leaves each weapon an opposite that draws.
Then have `battle()` compare two weapons and `meeting()` repeat battles until one group remains.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
import random
from enum import StrEnum
from typing import Any, ClassVar, override

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Weapon:
    def compete(self, item: Any) -> Outcome:
        ...
    def __str__(self) -> str:
        ...

class Jargon(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        ...
    def eval_jargon(self, item: Any) -> Outcome:
        ...
    def eval_play(self, item: Any) -> Outcome:
        ...
    def eval_invent_feature(self, item: Any) -> Outcome:
        ...
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        ...
    def eval_edict(self, item: Any) -> Outcome:
        ...
    def eval_schedule(self, item: Any) -> Outcome:
        ...

class Play(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        ...
    def eval_jargon(self, item: Any) -> Outcome:
        ...
    def eval_play(self, item: Any) -> Outcome:
        ...
    def eval_invent_feature(self, item: Any) -> Outcome:
        ...
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        ...
    def eval_edict(self, item: Any) -> Outcome:
        ...
    def eval_schedule(self, item: Any) -> Outcome:
        ...

class InventFeature(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        ...
    def eval_jargon(self, item: Any) -> Outcome:
        ...
    def eval_play(self, item: Any) -> Outcome:
        ...
    def eval_invent_feature(self, item: Any) -> Outcome:
        ...
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        ...
    def eval_edict(self, item: Any) -> Outcome:
        ...
    def eval_schedule(self, item: Any) -> Outcome:
        ...

class SellImaginaryProduct(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        ...
    def eval_jargon(self, item: Any) -> Outcome:
        ...
    def eval_play(self, item: Any) -> Outcome:
        ...
    def eval_invent_feature(self, item: Any) -> Outcome:
        ...
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        ...
    def eval_edict(self, item: Any) -> Outcome:
        ...
    def eval_schedule(self, item: Any) -> Outcome:
        ...

class Edict(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        ...
    def eval_jargon(self, item: Any) -> Outcome:
        ...
    def eval_play(self, item: Any) -> Outcome:
        ...
    def eval_invent_feature(self, item: Any) -> Outcome:
        ...
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        ...
    def eval_edict(self, item: Any) -> Outcome:
        ...
    def eval_schedule(self, item: Any) -> Outcome:
        ...

class Schedule(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        ...
    def eval_jargon(self, item: Any) -> Outcome:
        ...
    def eval_play(self, item: Any) -> Outcome:
        ...
    def eval_invent_feature(self, item: Any) -> Outcome:
        ...
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        ...
    def eval_edict(self, item: Any) -> Outcome:
        ...
    def eval_schedule(self, item: Any) -> Outcome:
        ...

class Inhabitant2:
    WEAPONS: ClassVar[tuple[type[Weapon], ...]]

    def __init__(self, rng: random.Random) -> None:
        ...

    def get_weapon(self) -> Weapon:
        ...

class Dwarf2(Inhabitant2):
    WEAPONS = (Jargon, Play)
class Elf2(Inhabitant2):
    WEAPONS = (InventFeature, SellImaginaryProduct)
class Troll2(Inhabitant2):
    WEAPONS = (Edict, Schedule)

class Project2:
    def __init__(self, seed: int = 0) -> None:
        ...

    def battle(
        self, a: Inhabitant2, b: Inhabitant2
    ) -> Inhabitant2 | None:
        ...

    def meeting(self, group_size: int) -> str:
        ...
```

<details>
<summary>Done when</summary>

for each of the 36 ordered pairs of your six weapons,
the two orders give opposite results (a draw stays a draw),
`meeting()` returns one group's name,
more than one group wins across many seeds,
and `uv run ty check` passes on your file.

<details>
<summary>Solution</summary>

Each `Inhabitant` kind holds two of six weapon types, ranked around a cycle.
Each weapon beats the previous two in the ranking and loses to the next two.
Six is an even number, so each weapon has one opponent left over: its opposite,
three steps around the circle.
That pair draws.
`paper_scissors_rock.py` has three items, an odd count,
so each item beats half the rest and loses to the other half.
An even count always leaves the opposite pair to define.

```python
# exercise_8.py
import random
from enum import StrEnum
from typing import Any, ClassVar, override

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Weapon:
    def compete(self, item: Any) -> Outcome:
        raise NotImplementedError
    def __str__(self) -> str:
        return type(self).__name__

class Jargon(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        return item.eval_jargon(self)
    def eval_jargon(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_play(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_invent_feature(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_edict(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_schedule(self, item: Any) -> Outcome:
        return Outcome.LOSE

class Play(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        return item.eval_play(self)
    def eval_jargon(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_play(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_invent_feature(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        return Outcome.WIN
    def eval_edict(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_schedule(self, item: Any) -> Outcome:
        return Outcome.LOSE

class InventFeature(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        return item.eval_invent_feature(self)
    def eval_jargon(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_play(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_invent_feature(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        return Outcome.WIN
    def eval_edict(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_schedule(self, item: Any) -> Outcome:
        return Outcome.DRAW

class SellImaginaryProduct(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        return item.eval_sell_imaginary_product(self)
    def eval_jargon(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_play(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_invent_feature(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_edict(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_schedule(self, item: Any) -> Outcome:
        return Outcome.WIN

class Edict(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        return item.eval_edict(self)
    def eval_jargon(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_play(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_invent_feature(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_edict(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_schedule(self, item: Any) -> Outcome:
        return Outcome.WIN

class Schedule(Weapon):
    @override
    def compete(self, item: Any) -> Outcome:
        return item.eval_schedule(self)
    def eval_jargon(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_play(self, item: Any) -> Outcome:
        return Outcome.WIN
    def eval_invent_feature(self, item: Any) -> Outcome:
        return Outcome.DRAW
    def eval_sell_imaginary_product(self,
                                    item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_edict(self, item: Any) -> Outcome:
        return Outcome.LOSE
    def eval_schedule(self, item: Any) -> Outcome:
        return Outcome.DRAW

class Inhabitant2:
    WEAPONS: ClassVar[tuple[type[Weapon], ...]]

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def get_weapon(self) -> Weapon:
        return self.rng.choice(self.WEAPONS)()

class Dwarf2(Inhabitant2):
    WEAPONS = (Jargon, Play)
class Elf2(Inhabitant2):
    WEAPONS = (InventFeature, SellImaginaryProduct)
class Troll2(Inhabitant2):
    WEAPONS = (Edict, Schedule)

class Project2:
    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random(seed)

    def battle(
        self, a: Inhabitant2, b: Inhabitant2
    ) -> Inhabitant2 | None:
        outcome = a.get_weapon().compete(b.get_weapon())
        if outcome is Outcome.WIN:
            return a
        if outcome is Outcome.LOSE:
            return b
        return None  # Draw: no winner this round

    def meeting(self, group_size: int) -> str:
        kinds = {"Dwarf": Dwarf2, "Elf": Elf2,
                 "Troll": Troll2}
        groups = {
            name: [cls(self.rng) for _ in range(group_size)]
            for name, cls in kinds.items()}
        while sum(1 for g in groups.values() if g) > 1:
            names = [n for n, g in groups.items() if g]
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    n1, n2 = names[i], names[j]
                    if not groups[n1] or not groups[n2]:
                        continue
                    winner = self.battle(
                        groups[n1][0], groups[n2][0])
                    if winner is groups[n1][0]:
                        groups[n2].pop(0)
                    elif winner is groups[n2][0]:
                        groups[n1].pop(0)
        survivors = [n for n, g in groups.items() if g]
        return survivors[0]

if __name__ == "__main__":
    print(Play().compete(Jargon()),
          Jargon().compete(Play()),
          Jargon().compete(SellImaginaryProduct()))
    print(Project2(seed=3).meeting(group_size=5))
#: win lose draw
#: Troll
```

**Declare the first dispatch on the base.**
`Weapon` declares `compete()` so that `battle()` can call it on the `Weapon` that `get_weapon()` returns.
The `eval_*()` methods live in the subclasses alone,
and their `item` parameters take `Any`,
as the chapter's `opponent` and `caller` parameters do.

If you leave `compete()` out of `Weapon`, the program prints the same two lines,
since every weapon class defines its own.
The type checker rejects the change.
`ty` reports an `invalid-explicit-override` at each of the six `@override` decorators,
and an `unresolved-attribute` at `battle()`'s call,
because `get_weapon()` returns a `Weapon`.
The solution declares `compete()` on the base,
which gives that call and every `@override` a method to name.

**Answer for the original caller.**
As in `paper_scissors_rock.py`,
each `eval_*()` method answers for the caller its name identifies,
so `Jargon.eval_play()` returns `WIN` because play beats jargon.

**Resolve both weapon types.**
`battle()` starts the two dispatches.
`a.get_weapon().compete(...)` resolves the first weapon's type.
That class's `compete()` calls the `eval_*()` method named for it on the second weapon,
and that second call resolves the second type.

Six weapons take 42 methods:
a `compete()` and six `eval_*()` methods in each class.
More than a hundred lines hold 36 answers, four times the chapter's nine,
because the answers grow with the square of the number of weapons.
A seventh weapon adds an `eval_*()` method to each of the six classes,
plus a new class of eight methods.
[Methods or Table](../../Chapters/32_Patterns--Multiple_Dispatching.md#methods-or-table)
weighs the length of the method version against a table.
Exercise 10 collects the same 36 answers in one place.

The weapon ranking is a cycle.
Every weapon loses to two others, so no group can count on winning.
The same cycle appears at the group level.
An `Elf` beats a `Dwarf` on three of their four weapon pairings,
a `Troll` beats an `Elf` on three of four,
and a `Dwarf` beats a `Troll` on three of four,
with the fourth pairing in each case the draw.
Across two hundred seeds,
each of the three kinds wins `meeting(5)` at least once,
so the outcome depends on the random draws each round,
as it does in a real rock-paper-scissors tournament.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 9. A table of callables

> The chapter claims that a table cell can hold a function,
> so even elaborate behavior fits the table.
> Build that version.
> In `paper_scissors_rock_table.py`,
> give every `OUTCOME` cell a `Callable[[Item, Item], Outcome]` in place of its `Outcome`,
> and have `compete()` call the cell it finds:
> `OUTCOME[type(self), type(opponent)](self, opponent)`.
> The call site stays `player.compete(opponent)`.
> Write a helper that wraps a constant `Outcome` in a callable,
> so the seven unchanged cells stay one line each.
> Then give `Paper` a `wet` attribute and make the `(Paper, Rock)` and `(Rock, Paper)` cells read it.
> Dry paper wraps the rock and wins, wet paper is too soggy and draws,
> whichever of the two calls `compete()`.
> The chapter gives two reasons for preferring the method version.
> Say which one this change answers, and which one survives it.

<details>
<summary>Where to look</summary>

[Methods or Table](../../Chapters/32_Patterns--Multiple_Dispatching.md#methods-or-table)
says a table cell can hold a function,
and [One Lookup in a Table](../../Chapters/32_Patterns--Multiple_Dispatching.md#one-lookup-in-a-table)
shows the lookup.
Store a callable in every cell and call what the lookup returns with both items.
To wrap each constant `Outcome`,
a helper returns a closure that ignores its arguments.
The `(Paper, Rock)` and `(Rock, Paper)` cells each read `wet` from whichever item is the `Paper`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_9.py
from collections.abc import Callable
from enum import StrEnum
from typing import Final

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Item:
    def compete(self, opponent: Item) -> Outcome:
        ...
    def __str__(self) -> str:
        ...

class Paper(Item):
    def __init__(self, wet: bool = False) -> None:
        ...
    def __str__(self) -> str:
        ...

class Scissors(Item):
    pass
class Rock(Item):
    pass

type Cell = Callable[[Item, Item], Outcome]

def always(outcome: Outcome) -> Cell:
    ...

def paper_vs_rock(player: Item, opponent: Item) -> Outcome:
    ...

def rock_vs_paper(player: Item, opponent: Item) -> Outcome:
    ...

OUTCOME: Final[
    dict[tuple[type[Item], type[Item]], Cell]] = {
    (Paper, Rock): paper_vs_rock,
    (Paper, Scissors): always(Outcome.LOSE),
    (Paper, Paper): always(Outcome.DRAW),
    (Scissors, Paper): always(Outcome.WIN),
    (Scissors, Rock): always(Outcome.LOSE),
    (Scissors, Scissors): always(Outcome.DRAW),
    (Rock, Scissors): always(Outcome.WIN),
    (Rock, Paper): rock_vs_paper,
    (Rock, Rock): always(Outcome.DRAW),
}
```

<details>
<summary>Done when</summary>

a dry `Paper` beats `Rock`,
a wet `Paper` draws with `Rock` whichever of the two calls `compete()`,
the other seven pairs return the chapter's answers,
and `uv run ty check` passes on your file.
You can also name the chapter's reason the callable cells answer,
and the reason that survives.

<details>
<summary>Solution</summary>

Every `OUTCOME` cell in the solution holds a callable,
which `compete()` calls after the lookup:

```python
# exercise_9.py
from collections.abc import Callable
from enum import StrEnum
from typing import Final

class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

class Item:
    def compete(self, opponent: Item) -> Outcome:
        return OUTCOME[type(self), type(opponent)](
            self, opponent)
    def __str__(self) -> str:
        return type(self).__name__

class Paper(Item):
    def __init__(self, wet: bool = False) -> None:
        self.wet = wet
    def __str__(self) -> str:
        return "WetPaper" if self.wet else "Paper"

class Scissors(Item):
    pass
class Rock(Item):
    pass

type Cell = Callable[[Item, Item], Outcome]

def always(outcome: Outcome) -> Cell:
    return lambda player, opponent: outcome

def paper_vs_rock(player: Item, opponent: Item) -> Outcome:
    if isinstance(player, Paper) and player.wet:
        return Outcome.DRAW  # Too soggy to wrap a rock
    return Outcome.WIN

def rock_vs_paper(player: Item, opponent: Item) -> Outcome:
    if isinstance(opponent, Paper) and opponent.wet:
        return Outcome.DRAW  # The same soggy draw
    return Outcome.LOSE

OUTCOME: Final[
    dict[tuple[type[Item], type[Item]], Cell]] = {
    (Paper, Rock): paper_vs_rock,
    (Paper, Scissors): always(Outcome.LOSE),
    (Paper, Paper): always(Outcome.DRAW),
    (Scissors, Paper): always(Outcome.WIN),
    (Scissors, Rock): always(Outcome.LOSE),
    (Scissors, Scissors): always(Outcome.DRAW),
    (Rock, Scissors): always(Outcome.WIN),
    (Rock, Paper): rock_vs_paper,
    (Rock, Rock): always(Outcome.DRAW),
}

for player, opponent in [
    (Paper(), Rock()),
    (Paper(wet=True), Rock()),
    (Rock(), Paper(wet=True)),
    (Scissors(), Paper()),
    (Rock(), Rock()),
]:
    result = player.compete(opponent)
    print(f"{player} <--> {opponent} : {result}")
#: Paper <--> Rock : win
#: WetPaper <--> Rock : draw
#: Rock <--> WetPaper : draw
#: Scissors <--> Paper : win
#: Rock <--> Rock : draw
```

**Call what the lookup returns.**
`compete()` changes by one pair of parentheses.
The call site stays the same:
`player.compete(opponent)` reads as it does in `paper_scissors_rock.py`,
where four method definitions per class stand behind it.

**Wrap the constant answers.**
`always()` keeps the table readable.
It returns a closure that ignores both operands and returns one `Outcome`,
so the seven combinations with a constant answer stay one line each and still read as a table of answers.
Only the cells that need code look like code.

**Read the state in both orders.**
The `(Paper, Rock)` cell receives both items, so it consults `player.wet`.
One duel has two orders, and each order has its own cell,
so the `(Rock, Paper)` cell needs the same test.
In that cell the paper is the opponent, so the cell reads `opponent.wet`.
If the `(Rock, Paper)` cell ignores `opponent.wet`,
a rock that calls `compete()` still loses to wet paper.

The chapter gives two reasons for preferring the double-dispatch version.
The first is behavior that reads the object's own state.
A cell holding a function answers that reason.
Whatever `Paper.eval_rock()` reads, `rock_vs_paper()` reads too,
from the same two objects.

The second reason survives:
a subclass that should override one combination and inherit the rest.
`paper_scissors_rock_subclass.py`'s `DampPaper` gets its special case by overriding `compete()` and `eval_rock()`.
In this version `Item` defines `compete()` once and the combinations live in the table,
so a subclass that overrides `compete()` replaces every combination at once.
Changing an existing cell changes that combination for every instance,
since `OUTCOME` is one shared dictionary.

The lookup still matches types exactly,
so an `Origami(Paper)` raises a `KeyError` whether the cells hold callables or `Outcome`s.
The remedy is to write every row for `Origami`.

**Narrow the operand's type.**
`paper_vs_rock()` and `rock_vs_paper()` take two `Item`s,
because every cell must.
Each recovers `Paper` with an `isinstance()` test,
the kind the chapter's ladder version repeats in every class.
Here each test sits inside one cell, so you write it once,
and a new `Item` leaves it untouched.

If you delete the `isinstance()` tests in `paper_vs_rock()` and `rock_vs_paper()` and read `wet`,
the demo prints the same five lines,
because the lookup reaches each cell with a `Paper` in the position it reads.
The type checker rejects the access.
`ty` reports an `unresolved-attribute` in each cell,
since a cell's parameters are `Item`s and `Paper` alone defines `wet`.
The solution keeps the tests so that the type checker narrows the operand to `Paper` before the attribute access.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 10. Exercise 8, rebuilt on a table

> Modify exercise 8 to use the table lookup technique of `paper_scissors_rock_table.py`.

<details>
<summary>Where to look</summary>

[One Lookup in a Table](../../Chapters/32_Patterns--Multiple_Dispatching.md#one-lookup-in-a-table)
replaces the `eval_*()` methods with one dictionary keyed on `type(self)` and `type(opponent)`.
Keep `get_weapon()` and the inhabitant classes as they are,
and shrink the weapons to empty classes.
Write the 36 answers as a grid whose rows and columns follow one `ORDER`,
and build `OUTCOME` from it with a comprehension.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_10.py
import random
from typing import ClassVar, Final
import exercise_8 as methods
from exercise_8 import Outcome

class Weapon:
    def compete(self, item: Weapon) -> Outcome:
        ...
    def __str__(self) -> str:
        ...

class Jargon(Weapon):
    pass
class Play(Weapon):
    pass
class InventFeature(Weapon):
    pass
class SellImaginaryProduct(Weapon):
    pass
class Edict(Weapon):
    pass
class Schedule(Weapon):
    pass

type Table = dict[
    tuple[type[Weapon], type[Weapon]], Outcome]

W: Final[Outcome] = Outcome.WIN
L: Final[Outcome] = Outcome.LOSE
D: Final[Outcome] = Outcome.DRAW
ORDER: Final[tuple[type[Weapon], ...]] = (
    Jargon, Play, InventFeature,
    SellImaginaryProduct, Edict, Schedule)
GRID: Final[tuple[tuple[Outcome, ...], ...]] = (
    (D, L, L, D, W, W),  # Jargon
    (W, D, L, L, D, W),  # Play
    (W, W, D, L, L, D),  # InventFeature
    (D, W, W, D, L, L),  # SellImaginaryProduct
    (L, D, W, W, D, L),  # Edict
    (L, L, D, W, W, D),  # Schedule
)
OUTCOME: Final[Table] = {
    (a, b): cell
    for a, row in zip(ORDER, GRID, strict=True)
    for b, cell in zip(ORDER, row, strict=True)
}

class Inhabitant2:
    WEAPONS: ClassVar[tuple[type[Weapon], ...]]

    def __init__(self, rng: random.Random) -> None:
        ...

    def get_weapon(self) -> Weapon:
        ...

class Dwarf2(Inhabitant2):
    WEAPONS = (Jargon, Play)
class Elf2(Inhabitant2):
    WEAPONS = (InventFeature, SellImaginaryProduct)
class Troll2(Inhabitant2):
    WEAPONS = (Edict, Schedule)

class Project2:
    def __init__(self, seed: int = 0) -> None:
        ...

    def battle(
        self, a: Inhabitant2, b: Inhabitant2
    ) -> Inhabitant2 | None:
        ...

    def meeting(self, group_size: int) -> str:
        ...

def by_methods(a: type[Weapon],
               b: type[Weapon]) -> Outcome:
    ...
```

<details>
<summary>Done when</summary>

your table holds 36 entries,
each matching what your exercise 8 weapons return for the same ordered pair,
and with the same seed `meeting()` names the same winning group as your exercise 8.

<details>
<summary>Solution</summary>

The solution replaces the weapons' `eval_*()` methods with a grid of answers:

```python
# exercise_10.py
import random
from typing import ClassVar, Final
import exercise_8 as methods
from exercise_8 import Outcome

class Weapon:
    def compete(self, item: Weapon) -> Outcome:
        return OUTCOME[type(self), type(item)]
    def __str__(self) -> str:
        return type(self).__name__

class Jargon(Weapon):
    pass
class Play(Weapon):
    pass
class InventFeature(Weapon):
    pass
class SellImaginaryProduct(Weapon):
    pass
class Edict(Weapon):
    pass
class Schedule(Weapon):
    pass

type Table = dict[
    tuple[type[Weapon], type[Weapon]], Outcome]

W: Final[Outcome] = Outcome.WIN
L: Final[Outcome] = Outcome.LOSE
D: Final[Outcome] = Outcome.DRAW
ORDER: Final[tuple[type[Weapon], ...]] = (
    Jargon, Play, InventFeature,
    SellImaginaryProduct, Edict, Schedule)
GRID: Final[tuple[tuple[Outcome, ...], ...]] = (
    (D, L, L, D, W, W),  # Jargon
    (W, D, L, L, D, W),  # Play
    (W, W, D, L, L, D),  # InventFeature
    (D, W, W, D, L, L),  # SellImaginaryProduct
    (L, D, W, W, D, L),  # Edict
    (L, L, D, W, W, D),  # Schedule
)
OUTCOME: Final[Table] = {
    (a, b): cell
    for a, row in zip(ORDER, GRID, strict=True)
    for b, cell in zip(ORDER, row, strict=True)
}

class Inhabitant2:
    WEAPONS: ClassVar[tuple[type[Weapon], ...]]

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def get_weapon(self) -> Weapon:
        return self.rng.choice(self.WEAPONS)()

class Dwarf2(Inhabitant2):
    WEAPONS = (Jargon, Play)
class Elf2(Inhabitant2):
    WEAPONS = (InventFeature, SellImaginaryProduct)
class Troll2(Inhabitant2):
    WEAPONS = (Edict, Schedule)

class Project2:
    def __init__(self, seed: int = 0) -> None:
        self.rng = random.Random(seed)

    def battle(
        self, a: Inhabitant2, b: Inhabitant2
    ) -> Inhabitant2 | None:
        outcome = a.get_weapon().compete(b.get_weapon())
        if outcome is Outcome.WIN:
            return a
        if outcome is Outcome.LOSE:
            return b
        return None  # Draw: no winner this round

    def meeting(self, group_size: int) -> str:
        kinds = {"Dwarf": Dwarf2, "Elf": Elf2,
                 "Troll": Troll2}
        groups = {
            name: [cls(self.rng) for _ in range(group_size)]
            for name, cls in kinds.items()}
        while sum(1 for g in groups.values() if g) > 1:
            names = [n for n, g in groups.items() if g]
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    n1, n2 = names[i], names[j]
                    if not groups[n1] or not groups[n2]:
                        continue
                    winner = self.battle(
                        groups[n1][0], groups[n2][0])
                    if winner is groups[n1][0]:
                        groups[n2].pop(0)
                    elif winner is groups[n2][0]:
                        groups[n1].pop(0)
        survivors = [n for n, g in groups.items() if g]
        return survivors[0]

def by_methods(a: type[Weapon],
               b: type[Weapon]) -> Outcome:
    return getattr(methods, a.__name__)().compete(
        getattr(methods, b.__name__)())

wrong = [pair for pair, result in OUTCOME.items()
         if by_methods(*pair) != result]
print(len(OUTCOME), "pairs agree with exercise 8:",
      not wrong)
#: 36 pairs agree with exercise 8: True
print(Project2(seed=3).meeting(group_size=5))
#: Troll
```

**Lay the answers out as a grid.**
The listing writes the 36 answers out,
as a grid rather than as 36 dictionary rows.
Each row of `GRID` holds one weapon's results as the caller against the weapons in `ORDER`.
A cell holds what one of exercise 8's `eval_*()` methods returns.
Row `Jargon`, column `Play`, holds the `LOSE` that `Play.eval_jargon()` returns.

**Reuse the game around the table.**
The inhabitant classes, `battle()`, and `meeting()` repeat exercise 8's code,
so the seeded meeting draws the same weapons and `Troll` wins again.

**Check against the method version.**
`by_methods()` plays each pair through exercise 8's classes,
finding them by name as exercise 3 does.

If you drop `strict=True` and `Jargon`'s row of `GRID` comes up one cell short,
the comprehension quietly builds 35 entries.
The check then prints `35 pairs agree with exercise 8: True`,
since it plays only the pairs the table holds,
and the seeded meeting raises a `KeyError` for the missing `(Jargon, Schedule)`.
The solution passes `strict=True` to both `zip()` calls,
so the short row raises a `ValueError` when the module loads, before any duel.

The grid holds in six lines the answers that exercise 8 spreads across 42 methods.
A seventh weapon adds an empty class, a row, and a column,
where exercise 8 needs a method in every existing class and an eight-method class.
[Methods or Table](../../Chapters/32_Patterns--Multiple_Dispatching.md#methods-or-table)
reaches the same conclusion: for a ruleset that is a known set of answers,
the table is shorter and easier to maintain.

Exercise 8's version keeps the two advantages the chapter gives the method version.
Its `eval_*()` methods receive the competing objects,
so a weapon whose result depends on its state fits there,
while this grid needs exercise 9's callable cells.
A subclass of one weapon can also override one combination there and inherit the rest,
where the grid matches types exactly and needs a row and a column for the subclass.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
