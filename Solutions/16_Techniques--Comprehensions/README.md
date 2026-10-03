# Comprehensions: Solutions

## 1. Squaring digit-only strings from `a_list`

> Using `a_list` from `a_list.py` (`[1, "4", 9, "a", 0, 4]`),
> write a list comprehension that finds the string elements made only of digits
> (`e.isdigit()`), converts each to `int` with `int(e)`, and squares it.
> The predicate must reject `"a"` before `int()` sees it.
> Of the types in `a_list`, only `str` has `isdigit()`,
> so the predicate must test `isinstance(e, str)` before calling it.

<details>
<summary>Where to look</summary>

[List Comprehensions](../../Chapters/16_Techniques--Comprehensions.md#list-comprehensions) shows the trailing `if` clause that filters elements before the output expression runs.
Combine two tests in that clause with `and`.
The `and` operator stops at the first false operand, so the second test does not run on an element the first rejected.

<details>
<summary>Solution</summary>

If you test `e.isdigit()` alone, or before the type test,
the comprehension raises an `AttributeError` at the first element,
since the integer `1` has no `isdigit()` method.
The type checker flags the call before the program runs:
`ty` reports `unresolved-attribute`, because `e` is `int | str` at that point.
The solution tests `isinstance(e, str)` first, and `and` keeps `isdigit()` away from every integer.

```python
# exercise_1.py
a_list = [1, "4", 9, "a", 0, 4]
result = [int(e) ** 2 for e in a_list
          if isinstance(e, str) and e.isdigit()]
print(result)
#: [16]
```

The predicate has two parts, `isinstance(e, str)` and `e.isdigit()`,
both of which must be true before `int(e)` ever runs. `"a"` fails
`isdigit()`, so it does not reach `int()`, which otherwise raises a
`ValueError`. `"4"` is the only element that is both a string and made
entirely of digits, so it is the one the comprehension converts and
squares.

</details>
</details>

## 2. A `2` on the diagonal instead of `1`

> In `identity_matrix.py`,
> change the comprehension to put `2` on the diagonal instead of `1`,
> without adding a second pass over the result.

<details>
<summary>Where to look</summary>

[Nested Comprehensions](../../Chapters/16_Techniques--Comprehensions.md#nested-comprehensions) builds the matrix with an inner comprehension inside an outer one.
The diagonal comes from a conditional expression in the output position, which already chooses between two values.
Change what that expression yields, and leave the loops alone.

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

Only the literal in the conditional expression changes, from `1` to
`2`. Two nested loops still produce a list of lists, with a different
value on the diagonal.

</details>
</details>

## 3. Adding `"Galahad"` to `names`

> In `dict_comprehension.py`, add `"Galahad"` to `names`,
> then predict which entries the comprehension produces before running it,
> given the `len(name) > 3` filter.

<details>
<summary>Where to look</summary>

[Dictionary Comprehensions](../../Chapters/16_Techniques--Comprehensions.md#dictionary-comprehensions) shows a key expression and a value expression with an `if` filter at the end.
The filter runs on the loop variable, before either expression runs.
The comprehension builds a `dict`, which holds one value per key, so a later name whose key matches an earlier one replaces that entry.

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

**Filter before building each entry.** `"Galahad"` is seven characters, so it passes the `len(name) > 3`
filter and adds one entry. `"Ni"` is still the only name the filter
drops. The filter tests the original name, not the upper-cased key, so
the filter judges a name before the output expression ever runs. That
ordering matters when the output expression changes the length, as
`name * 2` does.

**Keep one value per key.** Two names that upper-case to the same string collide, since the
comprehension builds a `dict` and a later key overwrites an earlier
one. Adding `"robin"` alongside `"Robin"` produces one `'ROBIN'` entry,
not two, and the value comes from whichever name appears last in the
list.

</details>
</details>

## 4. Dropping the length filter from `set_comprehension.py`

> In `set_comprehension.py`, drop the `if len(name) > 1` filter,
> and predict how many entries `unique` holds before running it.
> Explain why `"J"` does not collide with `"JOHN"`.

<details>
<summary>Where to look</summary>

[Set Comprehensions](../../Chapters/16_Techniques--Comprehensions.md#set-comprehensions) normalizes each name and lets the set discard repeats.
Work out the normalized form of every name, including the one-character name, and count the distinct results.
Two entries collide only if their normalized strings are equal.

<details>
<summary>Solution</summary>

```python
# exercise_4.py
names = ["Bob", "JOHN", "alice", "bob", "ALICE", "J", "Bob"]

unique = {name[0].upper() + name[1:].lower()
          for name in names}

print(len(unique))
#: 4
print(sorted(unique))
#: ['Alice', 'Bob', 'J', 'John']
```

**Collapse the repeats.** The set holds four entries, one more than the filtered version. The
seven names normalize to `Bob`, `John`, `Alice`, `Bob`, `Alice`, `J`,
`Bob`. A set keeps one of each, so the duplicates and the case variants
collapse to `Bob`, `John`, and `Alice`, and `J` joins them.

**Normalize without truncating.** `"J"` does not collide with `"JOHN"` because the normalization is a
string transformation, not a truncation: `"J"` becomes `"J"` and
`"JOHN"` becomes `"John"`. `name[1:]` on a one-character string is the
empty string, so the concatenation adds nothing to the capital. `"J"`
and `"John"` are distinct strings, so the set keeps both.

The filter exists to drop the initial `"J"` as noise. Removing the filter
shows what the set does on its own: it collapses only exact
duplicates of the normalized form, and it has no notion that `"J"`
might be an abbreviation of `"John"`.

</details>
</details>

## 5. A comprehension that produces something worth keeping

> `comprehension_side_effects.py` builds a list of `None`s.
> Write a version that keeps the printing but produces a list the caller can use,
> then say whether a comprehension or a `for` loop is the right shape for it.

<details>
<summary>Where to look</summary>

[Comprehensions Build, Loops Execute](../../Chapters/16_Techniques--Comprehensions.md#comprehensions-build-loops-execute) explains why a comprehension is for the collection it builds and a loop is for its side effects.
Write a small function that does the printing and returns a value, then call it in the output expression.
Decide the shape by asking whether anyone uses the resulting list.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
def show(n: int) -> str:
    ...
```

<details>
<summary>Solution</summary>

If you leave `return line` out of `show()`,
the function returns `None` implicitly,
and `lines` prints as `[None, None, None]`, the list `comprehension_side_effects.py` builds.
The type checker catches the omission:
`ty` reports `invalid-return-type`, because `show()` declares a `str` return type.
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

**Give the output expression a value.** The original comprehension collects `print()`'s return value, which is
always `None`, so the list it builds is worthless and the brackets
mislead the reader. Giving the output expression something to return
fixes both: `show()` prints and hands back the line, so `lines` holds
the three strings a caller can check, write to a file, or join.

**Choose the shape by the result.** Which shape is right depends on whether you want the list. Here the
comprehension is correct, because `lines` is the point and the printing
is incidental. The `for` loop at the end is the right shape for
`comprehension_side_effects.py`, where printing is the purpose. The rule from the
chapter decides it: use a comprehension when you want the collection it
produces, and a loop when you want the side effect.

A comprehension whose output expression has a side effect is still
worth a second look, even when it returns something useful. `show()`
does two jobs, and a reader has to open it to learn that one of them is
printing.

</details>
</details>
</details>

## 6. Predicting a merge where a key repeats

> In `unpacking_comprehensions.py`,
> add a fourth entry `{"a": 5, "c": 9}` to `dicts` and predict what `{**d for d in dicts}` produces before running it,
> paying attention to which value wins for the key `"a"`.

<details>
<summary>Where to look</summary>

[Unpacking in Comprehensions](../../Chapters/16_Techniques--Comprehensions.md#unpacking-in-comprehensions) shows `**d` inside a dictionary display, merging each `d` as the loop reaches it.
A repeated key keeps the value written last.
A key keeps the position of its first insertion, which fixes the print order.

<details>
<summary>Solution</summary>

```python
# exercise_6.py
dicts = [{"a": 1}, {"b": 2}, {"a": 3}, {"a": 5, "c": 9}]
print({**d for d in dicts})
#: {'a': 5, 'b': 2, 'c': 9}
```

`**` merges the dictionaries in iteration order. When the same key
appears more than once, the value from the *later* dictionary
overwrites the earlier value. The key `"a"` appears in the first, third,
and fourth dictionaries (`1`, then `3`, then `5`), so the final value
is `5`, the last one written. The result orders keys by first
insertion, which is why `"a"` still prints first although its value
comes from the last dictionary in the list.

</details>
</details>

## 7. Running `any()` before `sum()`

> In `spent_generator.py`, move the `any()` line above the `sum()` line.
> Predict all three printed values before running it,
> remembering that `any()` stops when it finds a match.

<details>
<summary>Where to look</summary>

[A Generator Expression Runs Once](../../Chapters/16_Techniques--Comprehensions.md#a-generator-expression-runs-once) shows consumers sharing one generator, each taking what remains.
`any()` stops at its first true value, so the generator keeps its position when it returns.
Trace which values each later consumer receives.

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

`any()` pulls values until one matches, so it consumes `0` through `5`,
reports `True`, and stops. Stopping there leaves the generator part-way
through, not empty: `sum()` continues from `6` and adds `36 + 49 + 64 +
81`, giving `230` rather than the full `285`. By then `sum()` has
drained every value, so `list()` gets nothing. A generator holds a
position rather than a beginning. Each consumer picks up where the
previous one stopped, and `any()`'s early exit leaves values behind for
`sum()` to find.

</details>
</details>

## 8. Closing the gap with brackets

> In `genexp_timing.py`,
> turn the generator expression into a list comprehension and name the result `built`.
> Predict the three printed lines, and their order, before running it.
> Explain which value of `factor` the result uses.

<details>
<summary>Where to look</summary>

[The Gap Between Creation and Consumption](../../Chapters/16_Techniques--Comprehensions.md#the-gap-between-creation-and-consumption) shows a generator expression delaying its work until a consumer pulls values.
Square brackets make the comprehension run to completion at the line where it appears.
Ask when the comprehension calls `source()` and when it reads `factor`, then compare with the print order.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
def source() -> list[int]:
    ...
```

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

**Compute the products eagerly.** The lines print in the same order as in `genexp_timing.py`, and the
last one changes from `[10, 20, 30]` to `[2, 4, 6]`. A list
comprehension does all its work on the line where it appears: it
calls `source()`, reads `factor` while `factor` is `2`, and stores
the three products in `built`. The later `factor = 10` has nothing
to affect, because `built` holds finished numbers and no code that
still needs to look `factor` up.

The generator expression calls `source()` at the same point, which
is why the first line of output does not move. The brackets change
when the output expression runs, and with it which value of
`factor` the expression reads.

</details>
</details>
</details>
