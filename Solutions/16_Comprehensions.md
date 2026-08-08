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

## 3. Adding `"Galahad"` to `names`

```python
# exercise_3.py
names = ["Arthur", "Lancelot", "Bedevere", "Ni", "Robin", "Galahad"]

lengths = {name.upper(): len(name) for name in names if len(name) > 3}
print(sorted(lengths))
#: ['ARTHUR', 'BEDEVERE', 'GALAHAD', 'LANCELOT', 'ROBIN']
print(lengths["GALAHAD"], "NI" in lengths)
#: 7 False
```

`"Galahad"` is seven characters, so it passes the `len(name) > 3`
filter and adds one entry. `"Ni"` is still the only name the filter
drops. The filter tests the original name, not the upper-cased key, so
a name is judged before the output expression ever runs; that ordering
matters when the output expression changes the length, as `name * 2`
would.

Two names that upper-case to the same string would collide, since the
comprehension builds a `dict` and a later key overwrites an earlier
one. Adding `"robin"` alongside `"Robin"` produces one `'ROBIN'` entry,
not two, and the value comes from whichever name appears last in the
list.

## 4. Dropping the length filter from `set_comprehension.py`

```python
# exercise_4.py
names = ["Bob", "JOHN", "alice", "bob", "ALICE", "J", "Bob"]

unique = {name[0].upper() + name[1:].lower() for name in names}

print(len(unique))
#: 4
print(sorted(unique))
#: ['Alice', 'Bob', 'J', 'John']
```

Four entries, one more than the filtered version. The seven names
normalize to `Bob`, `John`, `Alice`, `Bob`, `Alice`, `J`, `Bob`, and a
set keeps one of each, so the duplicates and the case variants collapse
and `J` joins the three that were already there.

`"J"` does not collide with `"JOHN"` because the normalization is a
string transformation, not a truncation: `"J"` becomes `"J"` and
`"JOHN"` becomes `"John"`. `name[1:]` on a one-character string is the
empty string, so nothing is appended to the capital. Two distinct
strings hash differently, so both survive.

The filter existed to drop the initial `"J"` as noise. Removing it
shows what the set is doing on its own: it collapses only exact
duplicates of the normalized form, and it has no notion that `"J"`
might be an abbreviation of `"John"`.

## 5. A comprehension that produces something worth keeping

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

The original comprehension collected `print()`'s return value, which is
always `None`, so the list it built was worthless and the brackets
misled the reader. Giving the output expression something to return
fixes both: `show()` prints and hands back the line, so `lines` holds
the three strings a caller can assert on, write to a file, or join.

Which shape is right depends on whether you want the list. Here the
comprehension is correct, because `lines` is the point and the printing
is incidental. The `for` loop at the end is the right shape for the
original code, where printing was the whole purpose. The rule from the
chapter decides it: use a comprehension when you want the collection it
produces, and a loop when you want the side effect.

A comprehension whose output expression has a side effect is still
worth a second look, even when it returns something useful. `show()`
does two jobs, and a reader has to open it to learn that one of them is
printing.

## 6. Predicting a merge where a key repeats

```python
# exercise_6.py
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
