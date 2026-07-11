# Comprehensions: Solutions

## 1. Squaring digit-only strings from `a_list`

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
`isdigit()` (letters are not digits), so it never reaches `int()`,
which would otherwise raise `ValueError`. Only `"4"` in the list is
both a string and made entirely of digits, so it is the only element
that survives to be converted and squared.

## 2. A `2` on the diagonal instead of `1`

```python
# exercise_2.py
matrix = [[2 if col == row else 0 for col in range(3)]
          for row in range(3)]
for row in matrix:
    print(row)
#: [2, 0, 0]
#: [0, 2, 0]
#: [0, 0, 2]
```

Only the literal in the conditional expression changes, from `1` to
`2`. The comprehension's structure, two nested loops producing a list
of lists, does the same work either way; only the value placed on the
diagonal is different.

## 3. A fourth entry in `mcase`

```python
# exercise_3.py
mcase = {"a": 10, "b": 34, "A": 7, "Z": 3, "z": 12}

mcase_frequency = {
    k.lower(): mcase.get(k.lower(), 0) + mcase.get(k.upper(), 0)
    for k in mcase
}
print(mcase_frequency)
#: {'a': 17, 'b': 34, 'z': 15}
```

Adding `"z": 12` means the comprehension now visits `"Z"` and `"z"` as
two separate keys, but both map to the same lower-case key `"z"` in
the result, so their combined tally, `12 + 3 = 15`, is computed twice
(once from each key) and lands in the dictionary once. The redundant
work the chapter already calls out just grew from one repeated pair
to two.

## 4. Predicting `islice()` after two `next()` calls

```python
# exercise_4.py
from itertools import islice

squares = (n ** 2 for n in range(1_000_000))
print(next(squares))
#: 0
print(next(squares))
#: 1
print(list(islice(squares, 5)))
#: [4, 9, 16, 25, 36]
```

The two `next()` calls already consumed `0` and `1` (`0**2` and
`1**2`), so the generator's next unconsumed value is `4` (`2**2`).
`islice(squares, 5)` then pulls the next five values in sequence from
wherever the generator currently stands, `4, 9, 16, 25, 36`
(`2**2` through `6**2`), not the first five values of the whole
sequence.

## 5. Predicting a merge where a key repeats

```python
# exercise_5.py
dicts = [{"a": 1}, {"b": 2}, {"a": 3}, {"a": 5, "c": 9}]
print({**d for d in dicts})
#: {'a': 5, 'b': 2, 'c': 9}
```

`**` merges the dictionaries in iteration order, and when the same key
appears more than once, the value from the *later* dictionary
overwrites the earlier one. The key `"a"` appears in the first, third,
and fourth dictionaries (`1`, then `3`, then `5`), so the final value
is `5`, the last one written. Order among distinct keys is preserved
by first insertion, which is why `"a"` still prints first despite its
value coming from the last dictionary in the list.
