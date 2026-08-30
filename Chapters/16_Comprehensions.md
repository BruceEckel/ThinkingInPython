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
A comprehension is shorter.
It reads like the definition of the result rather than a recipe for it,
and one line replaces several lines of loop bookkeeping.

## List Comprehensions

A list comprehension consists of:

-   An input sequence.
-   A variable representing members of the input sequence.
-   An optional predicate expression.
-   An output expression producing elements of the output list from members of the input sequence that satisfy the predicate.

Several examples in this chapter use the same input list:

```python
# a_list.py
a_list = [1, "4", 9, "a", 0, 4]
```

The list comprehension selects integers from the list and squares them:

```python
# list_comprehension.py
from a_list import a_list

squared_ints = [
    e ** 2 for e in a_list if isinstance(e, int)]
print(squared_ints)
#: [1, 81, 0, 16]
```

![The parts of a list comprehension](_images/listComprehensions)

In this comprehension:

-   The iterator walks through each member `e` of the input sequence `a_list`.
-   The predicate checks if the member is an integer.
-   If the member is an integer,
    the output expression squares it and appends it to the output list.

The built-in functions `map()` and `filter()` with a `lambda` achieve the same results.
`filter()` applies a predicate to a sequence and retains the members that pass it.
It produces a lazy iterator, which `list()` expands into a `list`:

```python
# filtering.py
from a_list import a_list

ints = list(filter(lambda e: isinstance(e, int), a_list))

if __name__ == "__main__":
    print(ints)
#: [1, 9, 0, 4]
```

`map()` applies a function to each member:

```python
# mapping.py
from filtering import ints

print(list(map(lambda e: e ** 2, ints)))  # type: ignore
#: [1, 81, 0, 16]
```

The two combine into a single expression:

```python
# map_and_filter.py
from a_list import a_list

print(list(map(lambda e: e ** 2,  # type: ignore
               filter(lambda e: isinstance(e, int),
                      a_list))))
#: [1, 81, 0, 16]
```

The `map()`/`filter()` form funnels every element through `lambda` calls,
and is harder to read.
The comprehension inlines the test and the expression,
and its brackets show at a glance that it produces a list.
`map()` and `filter()` pay off when the function already exists,
`map(str.strip, lines)` rather than `[line.strip() for line in lines]`.
[Functional Foundations](40_Functional_Foundations.md) returns to the choice.
The `lambda` makes the versions above worse, not `map()`.

The `# type: ignore` comments mark a cost beyond readability.
`filter()` with a `lambda` predicate does not narrow the element type,
so the type checker still sees `int | str` coming out and rejects `e ** 2`.
The comprehension's `if isinstance(e, int)` does narrow,
which is why `list_comprehension.py` needs no such comment.
`filter()` can narrow,
but only when its predicate is a named function annotated to return `TypeIs[int]` or `TypeGuard[int]` rather than `bool`.
`filter(None, items)` is the other narrowing form.
It drops the falsy values, and the type checker knows no `None` survives.

A comprehension has a scope of its own:

```python
# comprehension_scope.py
e = "outer"
squares = [e ** 2 for e in range(4)]
print(squares, e)
#: [0, 1, 4, 9] outer
total = 0
running = [(total := total + n) for n in range(5)]
print(running, total)
#: [0, 1, 3, 6, 10] 10
```

A comprehension's loop variable belongs to the comprehension.
The `e` inside the brackets is a different name from the `e` outside them,
so the outer `e` survives untouched.
A `for` loop behaves the opposite way:
its loop variable stays behind in the enclosing scope after the loop ends.

The walrus operator is the exception.
`total := total + n` assigns in the enclosing scope,
so `total` holds the running sum after the comprehension finishes.
That is deliberate, and it lets a comprehension accumulate a value without a separate loop.
The walrus cannot rebind the comprehension's own iteration variable,
and it cannot appear in a comprehension inside a class body.
Both are a `SyntaxError`.

## Set Comprehensions

Set comprehensions use the same principles as list comprehensions,
with `{}` instead of `[]`.
Braces build a set when the comprehension produces one value per element,
and a dict when it produces a `key: value` pair.
The colon decides which.
Python has no empty-set literal, since `{}` is an empty dict.
Write `set()`.

The following set comprehension normalizes each name
(capital first letter, the rest lower case),
keeps the names longer than one character,
and collapses the duplicates and case variants:

```python
# set_comprehension.py
names = ["Bob", "JOHN", "alice", "bob", "ALICE", "J", "Bob"]

unique = {name[0].upper() + name[1:].lower()
          for name in names if len(name) > 1}

print(sorted(unique))  # Sorted for stable display
#: ['Alice', 'Bob', 'John']

same = set([name[0].upper() + name[1:].lower()
            for name in names if len(name) > 1])

print(unique == same)
#: True
```

`same` builds a list with a list comprehension, then passes it to `set()`.
It produces the same result,
but the throwaway list costs time and memory that the set comprehension avoids.

## Dictionary Comprehensions

A dictionary comprehension builds a `dict`.
Each element produces a key and a value, with an optional filter.
Here each name becomes an upper-case key mapped to its length,
keeping only the names longer than three characters:

```python
# dict_comprehension.py
names = ["Arthur", "Lancelot", "Bedevere", "Ni", "Robin"]

lengths = {name.upper(): len(name)
           for name in names if len(name) > 3}
print(lengths)
#: {'ARTHUR': 6, 'LANCELOT': 8, 'BEDEVERE': 8, 'ROBIN': 5}
```

The three parts mirror the list comprehension:
the `for` clause supplies each `name`, the `if` clause drops `"Ni"`,
and the `key: value` expression before `for` produces each entry.

A common variant swaps a dictionary's keys and values to invert a lookup:

```python
# invert_dict.py
seat_of = {"Arthur": 1, "Galahad": 2, "Robin": 3}

name_at = {seat: name for name, seat in seat_of.items()}
print(name_at)
#: {1: 'Arthur', 2: 'Galahad', 3: 'Robin'}
```

Inverting assumes the values are unique.
If two keys share a value, the later entry wins, just as with any duplicate key.

## Nested Comprehensions

An identity matrix of size `n` is an `n` by `n` square matrix with ones on the main diagonal and zeros elsewhere.
Python represents such a matrix as a list of lists,
where each sub-list is a row.
The following comprehension generates an identity matrix:

```python
# identity_matrix.py
from typing import Final

SIZE: Final[int] = 6

matrix = [[1 if col == row else 0 for col in range(SIZE)]
          for row in range(SIZE)]

for row in matrix:
    print(row)
#: [1, 0, 0, 0, 0, 0]
#: [0, 1, 0, 0, 0, 0]
#: [0, 0, 1, 0, 0, 0]
#: [0, 0, 0, 1, 0, 0]
#: [0, 0, 0, 0, 1, 0]
#: [0, 0, 0, 0, 0, 1]
```

Read a nested comprehension from the outside in, not left to right.
The outer comprehension supplies `row`.
For each `row`, the inner comprehension runs the full `col` loop and produces one sub-list.
The inner `for col` sits to the left of the outer `for row` but runs inside it.
The output expression sits first but runs last, once per innermost iteration.

`1 if col == row else 0` is a conditional expression, not a filter.
It sits in the output position, before the `for`,
and decides what each element *is*.
Every `col` still produces one.
An `if` after the `for`, as in `[e ** 2 for e in a_list if isinstance(e, int)]`,
decides *whether* the comprehension produces an element at all.
The positions are not interchangeable:
`[x for x in xs if a else b]` is a `SyntaxError`,
and a comprehension needing both writes them in both places,
`[x if a else b for x in xs if c]`.

Nesting one comprehension inside another builds a list of lists.
Writing two `for` clauses in one comprehension flattens instead,
producing a single list.
Those clauses *do* read left to right,
in the order the equivalent nested loops would appear:

```python
# flatten.py
rows = [[1, 2], [3, 4], [5]]
print([x for row in rows for x in row])
#: [1, 2, 3, 4, 5]
```

## Feeding the Iterator Clause

Everything to the right of `in` is an ordinary iterable expression,
so anything that produces one works there.

Use `zip()` to walk two sequences together, taking one element from each:

```python
# zip_pairs.py
names = ["a", "b", "c", "d"]
values = [1, 2, 3]
print([f"{n}={v}" for n, v in zip(names, values)])
#: ['a=1', 'b=2', 'c=3']
```

`zip()` stops at the end of the shorter sequence.
Pass `strict=True` to make a length mismatch raise a `ValueError` instead of silently truncating.

Unpack a tuple in the `for` clause's target,
here a `(name, function)` pair applied to a value:

```python
# zip_unpack.py
operations = [
    ("doubled", lambda v: v * 2),
    ("squared", lambda v: v ** 2),
]
values = [10, 3, 42]
print([
    f"{name}({v}) = {f(v)}"
    for (name, f), v in zip(operations, values)
])
#: ['doubled(10) = 20', 'squared(3) = 9']
```

`values` has a third element, and `zip()` drops it, as it did above.

Here's a two-level list comprehension using `Path.walk()`:

```python
# path_walk_comprehension.py
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

`tempfile.TemporaryDirectory()` is a [context manager](15_Context_Managers.md#a-basic-context-manager)
that creates a scratch directory and deletes it, and everything in it,
when the `with` block exits.
That gives the example a throwaway file tree to walk,
without touching any real files or leaving anything behind.

In the `py_paths` comprehension,
the first `for` walks the directories and the second `for` walks the files in each,
flattening the tree into one list of paths.
The filter tests `f.endswith(".py")` on the bare filename rather than building a `Path` and reading its `.suffix`.
That avoids constructing a `Path` for every file in the tree,
including the ones the filter skips.

A `with` block, unlike a function body, does not create a new scope.
The assignment to `py_paths` sits inside the `with`,
but the name is still visible afterward,
in the `for path in sorted(py_paths):` line below it.
By then the directory no longer exists.
The comprehension finishes building `py_paths` as strings while the directory still exists,
so nothing later needs the files.
Turning those brackets into parentheses would break it:
a generator expression would not start walking until `sorted()` pulls on it,
and that pull comes outside the `with`.
[Generator Expressions](#generator-expressions) returns to this.

## Breaking Up a Complex Comprehension

A comprehension earns its place when you can read it in one pass.
You can nest more `for` and `if` clauses,
or wrap the whole thing in another call,
but each one you add makes the expression harder to read in one pass.
Here, filtering, flattening, sorting,
and formatting all run in a single expression:

```python
# dense_comprehension.py
warehouses = {
    "East": [
        ("wrench", 12, 4.50),
        ("drill", 0, 9.00),
        ("hammer", 5, 2.25),
    ],
    "West": [
        ("wrench", 3, 4.75),
        ("sander", 8, 15.00),
    ],
}

report = [
    f"{wh}: {name} (${price:.2f})"
    for wh, name, price in sorted(
        [(wh, name, price)
         for wh, items in warehouses.items()
         for name, qty, price in items
         if qty > 0 and price < 10],
        key=lambda t: t[2])
]

if __name__ == "__main__":
    for line in report:
        print(line)
#: East: hammer ($2.25)
#: East: wrench ($4.50)
#: West: wrench ($4.75)
```

Reading this means untangling several questions at once: which items qualify,
how the warehouses flatten together, in what order the result arrives,
and how each line renders.
A comprehension nested inside `sorted()`,
itself nested inside the outer comprehension, does four jobs in one expression.

Splitting it into named steps removes none of the logic,
but each step now states its own purpose:

```python
# comprehension_steps.py
from dense_comprehension import warehouses

in_stock = [
    (wh, name, price)
    for wh, items in warehouses.items()
    for name, qty, price in items
    if qty > 0 and price < 10
]
in_stock.sort(key=lambda t: t[2])

report = [
    f"{wh}: {name} (${price:.2f})"
    for wh, name, price in in_stock
]

for line in report:
    print(line)
#: East: hammer ($2.25)
#: East: wrench ($4.50)
#: West: wrench ($4.75)
```

`in_stock` answers "which items qualify, flattened across warehouses."
`sort()` answers "in what order."
`report` answers "how each line renders."
Each name documents a stage of the pipeline,
so a reader can follow the transformation one step at a time instead of parsing every step simultaneously.
Use this split whenever a comprehension needs a comment to explain what it does.

## Comprehensions Build, Loops Execute

A comprehension's output expression can be any expression,
including a call with a side effect, such as `print()`.
Nothing stops you from using a comprehension to run code and throw away the result it builds:

```python
# comprehension_side_effects.py
wasted = [print(n) for n in [1, 2, 3]]
print(wasted)
#: 1
#: 2
#: 3
#: [None, None, None]
```

The comprehension calls `print()` for its side effect.
`print()` returns `None`, so `wasted` ends up holding three `None`s,
a list built and immediately discarded.
Worse, a reader scanning `[...]` expects a meaningful collection,
and this is a loop written with the wrong punctuation.

The idiomatic version says what it does:

```python
# for_loop_side_effects.py
for n in [1, 2, 3]:
    print(n)
#: 1
#: 2
#: 3
```

The `for` loop prints the same values without building a wasted list.
The brackets no longer suggest a collection the code never uses.
Use a comprehension when you want the collection it produces,
and a `for` loop when you want the side effect.
If nothing assigns or uses a comprehension's result, write it as a loop instead.

## Generator Expressions {#generator-expressions}

A comprehension evaluates eagerly,
so it immediately builds the entire result in memory.
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

No computation runs until you pull a value.
`next()` produces them one at a time,
and `itertools.islice()` takes a few without building the million-element list.

The parentheses do not make it a tuple comprehension.
No such form exists.
When you need a tuple, pass the generator expression to `tuple()`.

A generator expression can also feed `set()` and `dict()`:

```python
# set_dict_from_genexp.py
words = ["pol", "parrot", "fjord", "ex"]

lengths = set(len(w) for w in words)
print(sorted(lengths))
#: [2, 3, 5, 6]

initials = dict((w, w[0]) for w in words)
print(initials)
#: {'pol': 'p', 'parrot': 'p', 'fjord': 'f', 'ex': 'e'}
```

No lazy `set` or `dict` exists.
A set or dict must hold every element,
so `set(...)` or `dict(...)` consumes the whole generator immediately.
Neither saves anything over the set comprehension `{len(w) for w in words}` or the dict comprehension `{w: w[0] for w in words}`,
which read more directly and are the better choice.

Use a generator expression when the consumer takes values one at a time and does not need them all at once,
such as `sum()`, `any()`, `all()`, `min()`, or `max()`:

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
and `any()` stops when it finds a match.
`str.join()` does not belong on that list: it needs two passes,
one to size the result and one to fill it,
so it converts its argument to a list first.
A generator expression saves nothing over a list comprehension there.

A generator expression needs no parentheses of its own when it is a function's only argument.
If you add a second argument, it does:
`sum(n * n for n in nums, 0)` is a `SyntaxError`,
and `sum((n * n for n in nums), 0)` is the fix.

`genexp_consumers.py` iterates `nums` three times because `range` is re-iterable:
each `for` over it starts again at zero.
A generator expression is not:

```python
# spent_generator.py
nums = (n for n in range(10))
print(sum(n * n for n in nums))
#: 285
print(any(n == 5 for n in nums))
#: False
print(list(nums))
#: []
```

It runs once, and after something consumes its values it is empty.
`sum()` drains `nums`,
so `any()` sees no elements and reports `False` instead of `True`,
with no exception to say the question was never asked.
When you must traverse something twice,
either materialize it with `list()` or write the generator expression again.

A generator expression does not defer everything.
Creating one evaluates a single thing immediately, the outermost iterable:

```python
# genexp_timing.py
def source() -> list[int]:
    print("source() called")
    return [1, 2, 3]

factor = 2
gen = (n * factor for n in source())
#: source() called
print("generator created")
#: generator created
factor = 10
print(list(gen))
#: [10, 20, 30]
```

`source()` runs as Python builds the generator expression,
before the line below it prints.
The output expression waits,
so the code reads `factor` when `list()` pulls the values rather than when you wrote the generator,
and the answer is `[10, 20, 30]` instead of `[2, 4, 6]`.
A list comprehension has no such gap: it reads everything at once.
This is also why `path_walk_comprehension.py` uses brackets.
Its outermost iterable, `root.walk()`, would run at creation,
but the walking and the filtering would wait for a consumer that arrives after the directory disappears.
[Iterators](23_Iterators.md#generators) explores generators further,
and [Generators](45_Generators.md)
covers the values they receive as well as the ones they produce.

## Unpacking in Comprehensions

`path_walk_comprehension.py` flattens a tree with two `for` clauses.
Python 3.15 ([PEP 798](https://peps.python.org/pep-0798/))
adds a more direct way to flatten.
The unpacking operators `*` and `**` may appear in the output expression of a comprehension or generator expression,
splicing each iterable or mapping into the result.
PEP 798 extends the [PEP 448](https://peps.python.org/pep-0448/)
unpacking from `[*a, *b]` and `{**d1, **d2}` to the comprehension form,
and replaces many uses of two-`for` comprehensions, `itertools.chain()`,
and `itertools.chain.from_iterable()`:

```python
# unpacking_comprehensions.py
rows = [[1, 2], [3, 4], [5]]
dicts = [{"a": 1}, {"b": 2}, {"a": 3}]

# *
print([*row for row in rows])
#: [1, 2, 3, 4, 5]

# **
print({**d for d in dicts})
#: {'a': 3, 'b': 2}

# In a generator expression
flat = (*row for row in rows)
print(list(flat))
#: [1, 2, 3, 4, 5]

# Shallow: one level
print([*row for row in [[1, [2, 3]], [4]]])
#: [1, [2, 3], 4]
# Braces plus * build a set
print({*s for s in [{1, 2}, {3}]})
#: {1, 2, 3}
```

`[*row for row in rows]` reads as "splice each `row` in,"
and produces the same flat list as the two-`for` `[x for row in rows for x in row]`,
while saying what it does more directly.
It is a shallow flatten, splicing only the outer iterable,
so the nested `[2, 3]` above comes through unflattened.
`**` does the same for dictionaries,
merging each mapping with later keys winning.
Braces plus `*` build a set instead,
the one place where the colon does not decide between a set and a dict,
because neither form has one.
The unpacking operator decides instead.
The asynchronous generator form (`(*a async for a in agen())`)
works the same way.

## Choosing a Form

The four forms are one expression with different delimiters,
which is why learning the list form teaches all four.
Brackets when you want a list.
Braces for a set, or for a dict when a colon separates a key from a value.
Parentheses when the consumer takes values one at a time and does not need them all at once.
A `for` loop when you want the side effect rather than the collection.

The delimiters also decide when the work runs.
Every form but the parenthesized one runs to completion before the next statement,
so you pay the cost of a comprehension where you wrote it.
A generator expression defers that cost to whoever consumes it,
and pays it only for the values the consumer pulls.

## Exercises

1.  Using `a_list` from `a_list.py` (`[1, "4", 9, "a", 0, 4]`),
    write a list comprehension that finds the string elements made only of digits
    (`e.isdigit()`), converts each to `int` with `int(e)`, and squares it.
    The predicate must reject `"a"` so `int()` never sees it.
    Only `str` has `isdigit()`,
    so the predicate must test `isinstance(e, str)` before calling it.
2.  In `identity_matrix.py`,
    change the comprehension to build a 3 by 3 matrix with `2` on the diagonal instead of `1`,
    without adding a second pass over the result.
3.  In `dict_comprehension.py`, add `"Galahad"` to `names`,
    then predict which entries the comprehension produces before running it,
    given the `len(name) > 3` filter.
4.  In `set_comprehension.py`, drop the `if len(name) > 1` filter,
    and predict how many entries `unique` holds before running it.
    Explain why `"J"` does not collide with `"JOHN"`.
5.  `comprehension_side_effects.py` builds a list of `None`s.
    Write a version that keeps the printing but produces a list the caller can use,
    then say whether a comprehension or a `for` loop is the right shape for it.
6.  In `unpacking_comprehensions.py`,
    add a fourth entry `{"a": 5, "c": 9}` to `dicts` and predict what `{**d for d in dicts}` produces before running it,
    paying attention to which value wins for the key `"a"`.
7.  In `spent_generator.py`, move the `any()` line above the `sum()` line.
    Predict all three printed values before running it,
    remembering that `any()` stops when it finds a match.
