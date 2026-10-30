# Comprehensions: Solutions

## 1. Squaring digit-only strings from `a_list`

> Using `a_list` from `a_list.py` (`[1, "4", 9, "a", 0, 4]`),
> write a list comprehension that finds the string elements made only of digits
> (`e.isdigit()`), converts each to `int` with `int(e)`, and squares it.
> The filter must reject `"a"` before `int()` receives it.
> `isdigit()` is a `str` method, and `a_list` also holds integers,
> so the filter must test `isinstance(e, str)` before calling it.

<details>
<summary>Where to look</summary>

[List Comprehensions](../../Chapters/16_Techniques--Comprehensions.md#list-comprehensions)
shows the trailing `if` clause that filters elements before the output expression runs.
Combine two tests in that clause with `and`.
The `and` operator stops at the first false operand,
so the second test runs only on the elements the first one accepted.

<details>
<summary>Done when</summary>

your comprehension prints a one-element list holding `16`,
and `uv run ty check` passes on your file.
If you swap the two tests in the filter,
`ty` reports `unresolved-attribute` on `isdigit`,
which confirms that the order of the tests matters.

<details>
<summary>Solution</summary>

If you test `e.isdigit()` alone, or before the type test,
the comprehension raises an `AttributeError` at the first element,
since the integer `1` has no `isdigit()` method.
The type checker flags the call before the program runs.
`ty` reports `unresolved-attribute`, because `e` is `int | str` at that point.
The solution tests `isinstance(e, str)` first,
so `and` calls `isdigit()` only on strings.

```python
# exercise_1.py
a_list = [1, "4", 9, "a", 0, 4]
result = [int(e) ** 2 for e in a_list
          if isinstance(e, str) and e.isdigit()]
print(result)
#: [16]
```

`"a"` fails `isdigit()`,
so the comprehension drops it before `int()` can raise a `ValueError` on it.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 2. A `2` on the diagonal instead of `1`

> In `identity_matrix.py`,
> change the comprehension to put `2` on the diagonal instead of `1`,
> without adding a second pass over the result.

<details>
<summary>Where to look</summary>

[Nested Comprehensions](../../Chapters/16_Techniques--Comprehensions.md#nested-comprehensions)
builds the matrix with an inner comprehension inside an outer one.
The diagonal comes from a conditional expression in the output position,
which chooses between two values.
Change what that expression yields, and leave the loops alone.

<details>
<summary>Done when</summary>

your `identity_matrix.py` prints six rows with `2` on the diagonal,
from `[2, 0, 0, 0, 0, 0]` to `[0, 0, 0, 0, 0, 2]`,
and `matrix` comes straight from the comprehension,
with no statement that changes it afterward.

<details>
<summary>Solution</summary>

```python
# exercise_2.py
from typing import Final

SIZE: Final[int] = 6

matrix = [[2 if col == row else 0 for col in range(SIZE)]
          for row in range(SIZE)]
for row in matrix:
    print(row)
#: [2, 0, 0, 0, 0, 0]
#: [0, 2, 0, 0, 0, 0]
#: [0, 0, 2, 0, 0, 0]
#: [0, 0, 0, 2, 0, 0]
#: [0, 0, 0, 0, 2, 0]
#: [0, 0, 0, 0, 0, 2]
```

The one change is the literal in the conditional expression, from `1` to `2`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 3. Adding `"Galahad"` to `names`

> In `dict_comprehension.py`, add `"Galahad"` to `names`,
> then predict which entries the comprehension produces before running it,
> given the `len(name) > 3` filter.

<details>
<summary>Where to look</summary>

[Dictionary Comprehensions](../../Chapters/16_Techniques--Comprehensions.md#dictionary-comprehensions)
shows a key expression and a value expression with an `if` filter at the end.
The filter runs on the loop variable, before either expression runs.
The comprehension builds a `dict`, which holds one value per key.
A later name whose key matches an earlier one replaces that entry.

<details>
<summary>Done when</summary>

you wrote down the entries before running,
and the edited `dict_comprehension.py` prints the keys and values you wrote.
You can also say why `"Ni"` drops out,
and what happens to the entry count when two names upper-case to the same key.

<details>
<summary>Solution</summary>

```python
# exercise_3.py
names = ["Arthur", "Lancelot", "Bedevere",
         "Ni", "Robin", "Galahad"]

lengths = {name.upper(): len(name)
           for name in names if len(name) > 3}
print(sorted(lengths))
#: ['ARTHUR', 'BEDEVERE', 'GALAHAD', 'LANCELOT', 'ROBIN']
print(lengths["GALAHAD"], "NI" in lengths)
#: 7 False
```

**Filter before building each entry.**
The filter runs before the output expression, so it tests the original name,
not the upper-cased key.
That ordering matters when the output expression changes the length,
as `name * 2` does.

**Keep one value per key.**
Two names that upper-case to the same string collide.
The comprehension builds a `dict`,
so the later value replaces the earlier one under the shared key.
Adding `"robin"` alongside `"Robin"` produces one `'ROBIN'` entry, not two.
Its value comes from whichever of the two names appears later in the list.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 4. Dropping the length filter from `set_comprehension.py`

> In `set_comprehension.py`, drop the `if len(name) > 1` filter,
> and predict how many entries `unique` holds before running it.
> Explain why `"J"` does not collide with `"JOHN"`.

<details>
<summary>Where to look</summary>

[Set Comprehensions](../../Chapters/16_Techniques--Comprehensions.md#set-comprehensions)
normalizes each name and lets the set discard repeats.
Work out the normalized form of every name, including the one-character name,
and count the distinct results.
Two entries collide only if their normalized strings are equal.

<details>
<summary>Done when</summary>

you predicted the count before running, and the edited `set_comprehension.py`,
with a `print(len(unique))` added, prints that number.
You can also say what `"J"` becomes after `capitalize()`,
and why that string differs from what `"JOHN"` becomes.

<details>
<summary>Solution</summary>

```python
# exercise_4.py
names = ["Bob", "JOHN", "alice", "bob", "ALICE", "J", "Bob"]

unique = {name.capitalize() for name in names}

print(len(unique))
#: 4
print(sorted(unique))
#: ['Alice', 'Bob', 'J', 'John']
```

**Collapse the repeats.**
The set holds four entries, one more than the filtered version.
The seven names normalize to `Bob`, `John`, `Alice`, `Bob`, `Alice`, `J`, `Bob`.
A set keeps one of each,
so the duplicates and the case variants collapse to `Bob`, `John`, and `Alice`.
`J` makes the fourth.

**Change the case and keep every character.**
`"J"` stays apart from `"JOHN"` because the normalization changes case and keeps every character.
`"J"` stays `"J"`, because `capitalize()` lower-cases every character after the first,
and `"J"` has one character.

The filter exists to drop the initial `"J"` as noise.
Removing the filter shows what the set does on its own.
The set collapses exact duplicates of the normalized form,
so a `"J"` that abbreviates `"John"` stays a separate entry.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 5. A comprehension that produces something worth keeping

> `comprehension_side_effects.py` builds a list of `None`s.
> Write a version that keeps the printing but produces a list the caller can use,
> then say whether a comprehension or a `for` loop is the right shape for it.

<details>
<summary>Where to look</summary>

[Comprehensions Build, Loops Execute](../../Chapters/16_Techniques--Comprehensions.md#comprehensions-build-loops-execute)
explains why a comprehension is for the collection it builds and a loop is for its side effects.
Write a small function that does the printing and returns a value,
then call it in the output expression.
Decide the shape by asking whether anyone uses the resulting list.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
def show(n: int) -> str:
    ...
```

<details>
<summary>Done when</summary>

your version prints `item 1` through `item 3`,
then a list of three usable values in place of `[None, None, None]`,
and `uv run ty check` passes on your file.
You can also name the shape, comprehension or `for` loop,
that suits each version, and the question that decides it.

<details>
<summary>Solution</summary>

The solution returns the line it printed, so the comprehension collects strings.

```python
# exercise_5.py
def show(n: int) -> str:
    line = f"item {n}"
    print(line)
    return line

lines = [show(n) for n in [1, 2, 3]]
#: item 1
#: item 2
#: item 3
print(lines)
#: ['item 1', 'item 2', 'item 3']

for n in [1, 2, 3]:  # Printing alone stays a loop
    print(f"item {n}")
#: item 1
#: item 2
#: item 3
```

If you leave `return line` out of `show()`,
the function returns `None` implicitly.
`lines` then prints as `[None, None, None]`,
the list `comprehension_side_effects.py` builds.
`ty` reports the omission as `invalid-return-type`,
because `show()` declares a `str` return type.

**Give the output expression a value.**
The original comprehension collects `print()`'s return value,
which is always `None`.
The resulting list holds three `None`s.
The brackets tell the reader that the list matters,
but the printing is the purpose.
When the output expression calls a function that returns a useful value,
the list holds those values instead of `None`s and becomes the point.
A caller can check the strings in `lines`, write them to a file, or join them.

**Choose the shape by the result.**
The right shape depends on whether you want the list.
Here the comprehension is correct,
because `lines` is the point and the printing is incidental.
The `for` loop at the end suits `comprehension_side_effects.py`,
where printing is the purpose.
The chapter's rule decides both cases:
use a comprehension when you want the collection it produces,
and a loop when you want the side effect alone.

A comprehension whose output expression has a side effect still deserves a second look when its list is useful.
`show()` does two jobs.
A reader must open it to learn that one of them is printing.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. Predicting a merge where a key repeats

> In `unpacking_comprehensions.py`,
> add a fourth entry `{"a": 5, "c": 9}` to `dicts` and predict what `{**d for d in dicts}` produces before running it,
> paying attention to which value wins for the key `"a"`.

<details>
<summary>Where to look</summary>

[Unpacking in Comprehensions](../../Chapters/16_Techniques--Comprehensions.md#unpacking-in-comprehensions)
shows `**d` inside a dictionary display,
merging each `d` in the order the loop produces it.
A repeated key keeps the value written last.
A key keeps the position of its first insertion, which decides the print order.

<details>
<summary>Done when</summary>

you wrote the whole printed dictionary, keys in order, before running,
and the edited `unpacking_comprehensions.py` prints what you wrote.
You can also say where the key `"a"` gets its value and where it gets its position.

<details>
<summary>Solution</summary>

```python
# exercise_6.py
dicts = [{"a": 1}, {"b": 2}, {"a": 3}, {"a": 5, "c": 9}]
print({**d for d in dicts})
#: {'a': 5, 'b': 2, 'c': 9}
```

`**` merges the dictionaries in iteration order.
When the same key appears more than once,
the value from the later dictionary overwrites the earlier value.

The key `"a"` takes its value from the last dictionary but its position from the first.
The result orders keys by first insertion, so `"a"` prints first,
ahead of `"b"` and `"c"`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 7. Running `any()` before `sum()`

> In `spent_generator.py`, move the `any()` line above the `sum()` line.
> Predict all three printed values before running it,
> remembering that `any()` stops when it finds a match.

<details>
<summary>Where to look</summary>

[A Generator Expression Runs Once](../../Chapters/16_Techniques--Comprehensions.md#a-generator-expression-runs-once)
shows consumers sharing one generator, each taking what remains.
`any()` stops at its first true value,
so the generator keeps its position when `any()` returns.
Trace which values each later consumer receives.

<details>
<summary>Done when</summary>

you wrote down all three printed values before running,
and the edited `spent_generator.py` prints them in that order.
You can also name the first value `sum()` receives and say why it differs from the chapter's run.

<details>
<summary>Solution</summary>

```python
# exercise_7.py
nums = (n for n in range(10))
print(any(n == 5 for n in nums))
#: True
print(sum(n * n for n in nums))
#: 230
print(list(nums))
#: []
```

`any()` pulls values until one matches,
so it consumes `0` through `5` and reports `True`.
Stopping there leaves the generator part-way through, not empty.
`sum()` continues from `6` and adds `36 + 49 + 64 + 81`,
giving `230` of the full range's `285`.
By then `sum()` has consumed every value, so `list()` returns an empty list.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 8. Closing the gap with brackets

> In `genexp_timing.py`,
> turn the generator expression into a list comprehension and name the result `built`.
> Predict the three printed lines, and their order, before running it.
> Explain which value of `factor` the result uses.

<details>
<summary>Where to look</summary>

[The Gap Between Creation and Consumption](../../Chapters/16_Techniques--Comprehensions.md#the-gap-between-creation-and-consumption)
shows a generator expression delaying its work until a consumer pulls values.
Square brackets make the comprehension run to completion at the line where it appears.
Ask when the comprehension calls `source()` and when it reads `factor`,
then compare with the print order.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
def source() -> list[int]:
    ...
```

<details>
<summary>Done when</summary>

your edited `genexp_timing.py` builds `built` with a list comprehension and prints its three lines in the order you predicted.
You can also say which value of `factor`, `2` or `10`, the products use,
and at which line the comprehension reads it.

<details>
<summary>Solution</summary>

```python
# exercise_8.py
def source() -> list[int]:
    print("source() called")
    return [1, 2, 3]

factor = 2
built = [n * factor for n in source()]
#: source() called
print("list created")
#: list created
factor = 10
print(built)
#: [2, 4, 6]
```

The lines print in the same order as in `genexp_timing.py`,
because the generator expression there also calls `source()` on the line where it appears.
`exercise_8.py` renames the second message to `list created`.

**Compute the products eagerly.**
The printed list changes from `[10, 20, 30]` to `[2, 4, 6]`,
because a list comprehension does all its work on the line where it appears.
The later `factor = 10` leaves `built` as it was,
because `built` holds computed numbers rather than code that reads `factor`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 9. Counting the calls the walrus saves

> In `walrus_filter.py`,
> make `cube_if_even()` append each argument it receives to a list,
> then add a second comprehension that produces the same cubes without the walrus.
> Predict how many calls each comprehension makes over `range(6)`,
> and which arguments the second one passes twice.

<details>
<summary>Where to look</summary>

[Scope and the Walrus Operator](../../Chapters/16_Techniques--Comprehensions.md#scope-and-the-walrus-operator)
shows the filter and the output expression sharing one call through `y`.
Without the walrus, the filter calls `cube_if_even()` for every element.
The output expression calls it again for each element that passes.
Count the elements that pass the filter,
and add that number to the length of `data`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_9.py
def cube_if_even(n: int) -> int | None:
    ...
```

<details>
<summary>Done when</summary>

both comprehensions print `[0, 8, 64]`,
and the recorded arguments match the call count you predicted for each one.
You can also name the arguments that appear twice in the second run and say why the rest appear once.

<details>
<summary>Solution</summary>

```python
# exercise_9.py
calls: list[int] = []

def cube_if_even(n: int) -> int | None:
    calls.append(n)
    return n ** 3 if n % 2 == 0 else None

data = range(6)
cubes = [
    y for x in data if (y := cube_if_even(x)) is not None
]
print(cubes, len(calls))
#: [0, 8, 64] 6
calls.clear()
again = [
    cube_if_even(x) for x in data
    if cube_if_even(x) is not None
]
print(again, len(calls))
#: [0, 8, 64] 9
print(calls)
#: [0, 0, 1, 2, 2, 3, 4, 4, 5]
```

**One call per element with the walrus.**
The output expression reads each result back from `y` instead of calling again.

**A second call for each element that passes.**
`again` calls `cube_if_even()` in the filter for all six values,
then calls it again in the output expression for the three that pass.
`calls` shows the order.
`0`, `2`, and `4` each appear twice in a row,
once for the filter and then once for the output expression.
`1`, `3`, and `5` appear once,
because the filter rejects them before the output expression runs.
Six plus three makes nine calls for the same three cubes.

`cube_if_even()` returns in a moment,
but for a function that reads a file or queries a server,
the walrus halves the calls for every element that passes.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
