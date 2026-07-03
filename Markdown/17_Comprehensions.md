# Comprehensions

*Comprehensions* (first introduced in [Control Flow](04_Control_Flow.md#comprehensions))
build one collection from another in a single expression.
The idea originated in mathematical set-builder notation,
and was incorporated into functional programming.
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

The list comprehension is enclosed within list brackets (`[]`),
so it is immediately evident that a list is being produced.
There is only one function call to `isinstance()` and no call to the cryptic `lambda`.
Instead, the list comprehension uses a conventional iterator,
an expression, and an `if` clause for the optional predicate.

## Nested Comprehensions

An identity matrix of size `n` is an `n` by `n` square matrix with ones on the main diagonal and zeros elsewhere.
A 3 by 3 identity matrix is:

![](_images/idMatrix)

In Python we can represent such a matrix by a list of lists,
where each sub-list represents a row.
This matrix can be generated with the following comprehension:

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

Consider a dictionary whose keys are single characters and whose values count how often each appears, with upper and lower case counted separately.
To merge them into a case-insensitive count, the comprehension below sums the upper- and lower-case tallies under one lower-case key.
It does some redundant work: a letter present in both cases (such as `a` and `A`) has the same combined count computed twice, once for each case.

```python
# dict_comprehension.py
mcase = {"a": 10, "b": 34, "A": 7, "Z": 3}

mcase_frequency = {
    k.lower(): mcase.get(k.lower(), 0) + mcase.get(k.upper(), 0)
    for k in mcase
}
print(mcase_frequency)
#: {'a': 17, 'b': 34, 'z': 3}
```

## Generator Expressions {#generator-expressions}

A comprehension is evaluated eagerly,
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

Nothing is computed until you pull a value.
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

There is no lazy `set` or `dict`, though.
A set or dict must hold every element,
so `set(...)` or `dict(...)` consumes the whole generator immediately.
So neither saves anything over the set comprehension `{len(w) for w in words}`
or the dict comprehension `{w: w[0] for w in words}`,
which read more directly and are preferred.

A generator expression earns its keep when the consumer takes values one at a
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
Generators are explored further in [Iterators](27_Iterators.md#generators).
