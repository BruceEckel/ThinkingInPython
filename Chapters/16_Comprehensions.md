# Comprehensions

*Comprehensions* (first introduced in [Control Flow](04_Control_Flow.md#comprehensions))
build one collection from another in a single expression.
The idea originated in mathematical set-builder notation,
and passed into functional programming.
Haskell had list comprehensions, and Python borrowed them.

Comprehensions require a mental shift.
With a loop you describe how to build the result: make an empty list,
walk the input, test each item, and append the ones you want.
With a comprehension you describe what the result is, as a single expression,
and let Python build it.
A comprehension is shorter,
it reads like the definition of the result rather than a recipe for it,
and one line replaces several lines of loop bookkeeping.

## List Comprehensions

A list comprehension consists of:

-   An input sequence.
-   A variable representing members of the input sequence.
-   An optional predicate expression.
-   An output expression producing elements of the output list from members of the input sequence that satisfy the predicate.

Let's take a list of integers and square them.
Several examples in this chapter use the same input list:

```python
# a_list.py
a_list = [1, "4", 9, "a", 0, 4]
```

The list comprehension selects integers from the list and squares them:

```python
# list_comprehension.py
from a_list import a_list

squared_ints = [e ** 2 for e in a_list if isinstance(e, int)]
print(squared_ints)
#: [1, 81, 0, 16]
```

![](_images/listComprehensions)

The comprehension has three parts:

-   The iterator part iterates through each member `e` of the input sequence `a_list`.
-   The predicate checks if the member is an integer.
-   If the member is an integer, the output expression squares it and appends it to the output list.

You can achieve the same results using the built-in functions `map()` and
`filter()` with an anonymous `lambda`.
`filter()` applies a predicate to a sequence and retains the members that satisfy the predicate.
It produces a lazy iterator, which `list()` turns into a `list`:

```python
# filtering.py
from a_list import a_list

ints = list(filter(lambda e: isinstance(e, int), a_list))

if __name__ == "__main__":
    print(ints)
#: [1, 9, 0, 4]
```

`map()` applies a function to each member.
We reuse `ints` from `filtering.py`:

```python
# mapping.py
from filtering import ints

print(list(map(lambda e: e ** 2, ints)))
#: [1, 81, 0, 16]
```

The two combine into a single expression:

```python
# map_and_filter.py
from a_list import a_list

print(list(map(lambda e: e ** 2,
               filter(lambda e: isinstance(e, int), a_list))))
#: [1, 81, 0, 16]
```

The nested form funnels every element through `lambda` calls, and is harder to read.
The comprehension inlines the test and the expression.

List brackets (`[]`) enclose the list comprehension,
so it is immediately evident that it produces a list.
It calls `isinstance()` once, with no call to the cryptic `lambda`.
Instead, the list comprehension uses a conventional iterator,
an expression, and an `if` clause for the optional predicate.

## Nested Comprehensions

An identity matrix of size `n` is an `n` by `n` square matrix with ones on the main diagonal and zeros elsewhere.
A 3 by 3 identity matrix is:

![](_images/idMatrix)

In Python we can represent such a matrix by a list of lists,
where each sub-list represents a row.
The following comprehension generates this matrix:

```python
# identity_matrix.py
matrix = [[1 if col == row else 0 for col in range(3)]
          for row in range(3)]
for row in matrix:
    print(row)
#: [1, 0, 0]
#: [0, 1, 0]
#: [0, 0, 1]
```

## Techniques

Use `zip()` to walk two sequences together, taking one element from each:

```python
# zip_pairs.py
names = ["a", "b", "c"]
values = [1, 2, 3]
print([f"{n}={v}" for n, v in zip(names, values)])
#: ['a=1', 'b=2', 'c=3']
```

Unpack a tuple in the iterator, here a `(name, function)` pair applied to a value:

```python
# zip_unpack.py
all_slots = [
    ("doubled", lambda v: v * 2),
    ("squared", lambda v: v ** 2),
]
values = [10, 3]
print([
    f"{name}({v}) = {f(v)}"
    for (name, f), v in zip(all_slots, values)
])
#: ['doubled(10) = 20', 'squared(3) = 9']
```

Here's a two-level list comprehension using `Path.walk()`:

```python
# os_walk_comprehension.py
import tempfile
from pathlib import Path

# Build a small tree to walk: two .py files and one to skip
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "pkg").mkdir()
    for name in ("main.py", "pkg/util.py", "pkg/notes.txt"):
        (root / name).write_text("")
    py_paths = [
        (dirpath / f).relative_to(root).as_posix()
        for dirpath, _, files in root.walk()
        for f in files if f.endswith(".py")
    ]

for path in sorted(py_paths):  # Sorted for stable output
    print(path)
#: main.py
#: pkg/util.py
```

The outer `for` walks the directories and the inner `for` walks the files in each, flattening the tree into one list of paths.

## Set Comprehensions

Set comprehensions construct sets using the same principles as list comprehensions.
Instead of `[]`, a set comprehension uses `{}`.

The following set comprehension normalizes each name (capital first letter, the rest lower
case), keeps the names longer than one character, and collapses the duplicates
and case variants:

```python
# set_comprehension.py
names = ["Bob", "JOHN", "alice", "bob", "ALICE", "J", "Bob"]

unique = {name[0].upper() + name[1:].lower()
          for name in names if len(name) > 1}
print(sorted(unique))  # Sorted for stable display
#: ['Alice', 'Bob', 'John']

# set() of a list comprehension gives the same result, but builds a
# throwaway list first, so the set comprehension is preferred:
same = set([name[0].upper() + name[1:].lower()
            for name in names if len(name) > 1])
print(unique == same)
#: True
```

## Dictionary Comprehensions

A dictionary comprehension builds a `dict`, producing a key and a value for
each element, with an optional filter.
Here each name becomes an upper-case key mapped to its length,
keeping only the names longer than three characters:

```python
# dict_comprehension.py
names = ["Arthur", "Lancelot", "Bedevere", "Ni", "Robin"]

lengths = {name.upper(): len(name) for name in names if len(name) > 3}
print(lengths)
#: {'ARTHUR': 6, 'LANCELOT': 8, 'BEDEVERE': 8, 'ROBIN': 5}
```

The three parts mirror the list comprehension: the `for` clause supplies each
`name`, the `if` clause drops `"Ni"`, and the `key: value` expression before
`for` produces each entry.
A common variant swaps a dictionary's keys and values to invert a lookup:

```python
# invert_dict.py
seat_of = {"Arthur": 1, "Galahad": 2, "Robin": 3}

name_at = {seat: name for name, seat in seat_of.items()}
print(name_at)
#: {1: 'Arthur', 2: 'Galahad', 3: 'Robin'}
```

Inverting assumes the values are unique. If two keys share a value,
the later entry wins, just as with any duplicate key.

## Generator Expressions {#generator-expressions}

A comprehension evaluates eagerly,
which means it builds the whole result in memory right away.
For a large data set, that wastes time and space,
especially if you consume the result only once.
A *generator expression* uses the same syntax with parentheses instead of brackets,
and produces its values one at a time, on demand:

```python
# generator_expression.py
from itertools import islice

squares = (n ** 2 for n in range(1_000_000))
print(next(squares))
#: 0
print(next(squares))
#: 1
print(list(islice(squares, 3)))
#: [4, 9, 16]
```

No computation happens until you pull a value.
`next()` produces them one at a time, and `itertools.islice()` takes a few
without ever building the million-element list.

A generator expression can also feed `set()` and `dict()`:

```python
# set_dict_from_genexp.py
words = ["pol", "parrot", "pining", "fjord", "ex"]

lengths = set(len(w) for w in words)
print(sorted(lengths))
#: [2, 3, 5, 6]

initials = dict((w, w[0]) for w in words)
print(initials)
#: {'pol': 'p', 'parrot': 'p', 'pining': 'p', 'fjord': 'f', 'ex': 'e'}
```

No lazy `set` or `dict` exists, though.
A set or dict must hold every element,
so `set(...)` or `dict(...)` consumes the whole generator immediately.
Neither saves anything over the set comprehension `{len(w) for w in words}`
or the dict comprehension `{w: w[0] for w in words}`,
which read more directly and are the better choice.

Use a generator expression when the consumer takes values one at a
time and never needs them all, such as `sum()`, `any()`, `all()`, `min()`,
`max()`, or `str.join()`:

```python
# genexp_consumers.py
nums = range(1_000_000)

print(sum(n * n for n in nums))
#: 333332833333500000
print(any(n == 12_345 for n in nums))
#: True
print(max(len(str(n)) for n in nums))
#: 6
```

None of these builds an intermediate collection of a million items,
and `any()` stops as soon as it finds a match.
[Iterators](23_Iterators.md#generators) explores generators further.

## Unpacking in Comprehensions

The nested comprehensions above flatten by writing two `for` clauses.
Python 3.15 ([PEP 798](https://peps.python.org/pep-0798/)) adds a more direct way.
The unpacking operators `*` and `**` may appear in the output expression of a
comprehension or generator expression, splicing each iterable or mapping into the
result.
This extends the [PEP 448](https://peps.python.org/pep-0448/) unpacking you already
know from `[*a, *b]` and `{**d1, **d2}` to the comprehension form,
and replaces many uses of nested comprehensions, `itertools.chain()`, and
`itertools.chain.from_iterable()`:

```python
# unpacking_comprehensions.py
rows = [[1, 2], [3, 4], [5]]
dicts = [{"a": 1}, {"b": 2}, {"a": 3}]

# * splices each iterable into the result:
print([*row for row in rows])
#: [1, 2, 3, 4, 5]

# ** merges each mapping. Later keys win, order preserved:
print({**d for d in dicts})
#: {'a': 3, 'b': 2}

# The same syntax works in a generator expression:
flat = (*row for row in rows)
print(list(flat))
#: [1, 2, 3, 4, 5]
```

`[*row for row in rows]` reads as "splice each `row` in,"
and produces the same flat list as the nested `[x for row in rows for x in row]`,
while saying what it does more directly.
`**` does the same for dictionaries, merging each mapping with later keys winning.
The set form `{*s for s in sets}` and the asynchronous generator form
(`(*a async for a in agen())`) work the same way.

## Exercises

1.  Using `a_list` from `a_list.py` (`[1, "4", 9, "a", 0, 4]`), write a list comprehension that finds
    the string elements made only of digits (`e.isdigit()`), converts each to `int` with `int(e)`,
    and squares it. The predicate must reject `"a"` so `int()` never sees it.
2.  In `identity_matrix.py`, change the comprehension to build a 3 by 3 matrix
    with `2` on the diagonal instead of `1`, without adding a second pass over the result.
3.  In `dict_comprehension.py`, add `"Galahad"` to `names`, then predict which
    entries the comprehension produces before running it, given the
    `len(name) > 3` filter.
4.  In `generator_expression.py`, replace `islice(squares, 3)` with `islice(squares, 5)`
    and predict which five values it produces,
    given that `next(squares)` was already called twice before that line.
5.  In `unpacking_comprehensions.py`, add a fourth entry `{"a": 5, "c": 9}` to `dicts`
    and predict what `{**d for d in dicts}` produces before running it,
    paying attention to which value wins for the key `"a"`.
