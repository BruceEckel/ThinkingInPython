# Containers

> Every program keeps things in groups: in order, by key, or without duplicates.
> Python gives each grouping a literal and a type of its own.

In C++ and Java a container is a library class you name and construct.
Python builds its containers into the grammar.
`[1, 2]`, `{"a": 1}`, and `{1, 2}` are literals, available in every module.
`in` and `len()` work on all of them, and slicing works on the sequences.
Lists, tuples, dictionaries, and sets are fundamental data types.

## Lists

A `list` holds objects, of any kind, in an ordered, mutable sequence.
The `for` statement iterates through the elements of a list rather than counting through a sequence of numbers:

```python
# list.py

odds = [1, 3, 5]
print(odds)
#: [1, 3, 5]
odds.append(7)
for x in odds:
    print(x)
#: 1
#: 3
#: 5
#: 7
```

The `list` grows automatically.

### Indexing and Slicing

Indexing starts at zero, and negative indices count from the end.
A *slice* `[start:stop:step]` copies a subrange, with `stop` excluded:

```python
# slicing.py

xs = [10, 20, 30, 40, 50]
print(xs[0], xs[-1])  # First and last
#: 10 50
print(xs[1:3])  # The stop index is excluded
#: [20, 30]
print(xs[:2])  # From the start
#: [10, 20]
print(xs[2:])  # To the end
#: [30, 40, 50]
print(xs[::2])  # Every second item
#: [10, 30, 50]
print(xs[::-1])  # Reversed
#: [50, 40, 30, 20, 10]
print(xs[3:99])  # A slice stops at the end
#: [40, 50]
```

An index past the end raises an `IndexError`,
but a slice clips its bounds to the list,
so `xs[3:99]` returns the two items that exist.

Slicing works on the built-in sequences, including strings and tuples.

### Growing, Shrinking, and Sorting

Lists grow and shrink in place.
`len()` and `in` report their size and contents:

```python
# list_ops.py

xs = [10, 20, 30]
xs.append(40)  # Add one item at the end
xs.extend([50, 60])  # Add every item of an iterable
xs.insert(1, 15)  # Insert before index 1
print(xs, len(xs))
#: [10, 15, 20, 30, 40, 50, 60] 7
xs.remove(15)  # Remove the first item equal to 15
del xs[0]  # Remove by index
print(xs, 30 in xs)
#: [20, 30, 40, 50, 60] True
```

`append()` adds its argument as a single element,
so `xs.append([1, 2])` puts a `list` inside the `list`.
`extend()` adds each item of its argument.

`sorted()` builds a new sorted list from any iterable.
`list.sort()` reorders a list in place and returns `None`:

```python
# sorting.py

words = ["pear", "Fig", "apple"]
print(sorted(words))  # A new list; words is untouched
#: ['Fig', 'apple', 'pear']
print(words)
#: ['pear', 'Fig', 'apple']
print(words.sort())  # Sorts in place and returns None
#: None
print(words)
#: ['Fig', 'apple', 'pear']
print(sorted(words, reverse=True))
#: ['pear', 'apple', 'Fig']
```

Because `x.sort()` returns `None` where `sorted(x)` returns the new list,
`x = x.sort()` binds `None` and loses the list.

Uppercase sorts before lowercase because Python compares strings by code point.
A `key=` function changes the ordering.
`sorted(words, key=str.lower)` compares lowercase copies of the words and puts `apple` first.
[Functions](05_Foundations--Functions.md#lambdas) covers `key=` functions.

### Mixed Element Types

Each slot of a `list` holds a reference to the object you put there,
so the same `list` can mix strings, numbers, `None`, and other containers:

```python
# mixed_types.py

mixed = [1, "two", 3.0, True, None, [5, 6]]
for item in mixed:
    print(item, type(item).__name__)
#: 1 int
#: two str
#: 3.0 float
#: True bool
#: None NoneType
#: [5, 6] list
```

Mixing types is convenient but easy to overuse.
A `list` of mixed types usually means each element plays a different role,
so the code that reads the list must test each element's type.
A `tuple` or a [data class](12_Techniques--Data_Classes_as_Types.md#data-classes)
gives each role its own position or field,
and separate lists can each hold a single type.

### Two List Traps

Two list operations produce surprises.
`*` repeats a reference rather than copying the object it references,
so a grid built that way has one row under three names:

```python
# list_traps.py

grid = [[0]] * 3  # Three names for one inner list  # [1]
grid[0][0] = 1
print(grid)
#: [[1], [1], [1]]
# [2]
grid = [[0] for _ in range(3)]  # Three separate lists
grid[0][0] = 1
print(grid)
#: [[1], [0], [0]]
```

The grid at `[1]` repeats the lesson of [Variables and References](02_Foundations--Tour.md#variables-and-references).
Assignment binds a name and shares the object,
so `*` binds the same object into every slot.

The second `grid` (`[2]`) comes from a *comprehension*:
a single expression that produces a new list,
in place of a loop with `append()`.
The comprehension evaluates `[0]` three times,
once for each value from `range(3)`, so the rows are three separate lists.
[Control Flow](04_Foundations--Control_Flow.md#comprehensions)
shows the three comprehension forms,
and [Comprehensions](16_Techniques--Comprehensions.md)
explores every form in depth.

Removing items from a `list` while iterating over it is the second surprise:

```python
# remove_while_iterating.py

xs = [1, 2, 3, 4]
for x in xs:
    print(x)
    xs.remove(x)
#: 1
#: 3
print(xs)
#: [2, 4]
```

Each `remove()` shifts the following elements one place to the left,
and the loop then advances its index,
so it steps over the element that moved into the vacated slot.
No exception reports the skip.
Build a new list instead, with a comprehension that keeps the items you need,
or iterate over a copy with `for x in xs[:]`.

## Tuples and Unpacking

A *tuple* is an immutable sequence.
The comma makes the tuple, not the parentheses.
Tuples are the natural way to return several values from a function and to group values for unpacking:

```python
# tuples.py

point = (3, 4)
point = 3, 4  # Also a tuple; the comma matters
empty = ()
x, y = point  # Unpacking
print(x, y)
#: 3 4
# A one-element tuple needs the trailing comma
number = (42)
single = (42,)
print(type(number).__name__, type(single).__name__)
#: int tuple
print(tuple([1, 2, 3]))
#: (1, 2, 3)
print(tuple("abc"))
#: ('a', 'b', 'c')

def min_max(values):
    return min(values), max(values)  # Returns a tuple

low, high = min_max([5, 2, 9, 1])
print(low, high)
#: 1 9
```

Without its comma, `(42)` is the integer `42` inside parentheses,
so `number` is an `int`.
The empty tuple `()` is the exception to the comma rule,
because it has nothing to separate.

One name per element is the simplest unpacking.
Two extensions handle other shapes.
A starred name collects the remaining elements,
and a target can nest to match the shape of the value:

```python
# unpacking_assignment.py

first, *rest = [10, 20, 30, 40]
print(first, rest)  # A starred name always collects a list
#: 10 [20, 30, 40]
head, *middle, tail = "abcde"  # Any iterable unpacks
print(head, middle, tail)
#: a ['b', 'c', 'd'] e
(name, age), city = ("Alice", 30), "Rome"  # Nested targets
print(name, age, city)
#: Alice 30 Rome
values = [1, 2, 3]
try:
    x, y = values  # Without a star the counts must match
except ValueError as e:
    print(e)
#: too many values to unpack (expected 2, got 3)
```

At most one target at each level can carry the star.
By convention, a value you discard gets the name `_`,
so `*_` discards a run of elements.
[Pattern Matching](13_Techniques--Pattern_Matching.md)
matches `case` patterns against the same shapes.

The star also works in the other direction.
Inside a list or tuple display, `*` spreads an iterable into the new container,
element by element:

```python
# unpacking_displays.py

evens = [0, 2, 4]
odds = (1, 3)
print([*evens, *odds])  # A list from a list and a tuple
#: [0, 2, 4, 1, 3]
print((*odds, 5))  # A tuple display takes stars too
#: (1, 3, 5)
print([*"ab", *range(2)])  # Any iterable spreads
#: ['a', 'b', 0, 1]
print([*sorted("cab"), "d"])  # So does a call's result
#: ['a', 'b', 'c', 'd']
first, *rest = evens
print([*rest, first])  # Collect, then spread
#: [2, 4, 0]
```

Unlike a starred target, any number of operands can carry a star,
and they mix freely with ordinary elements.

`first, *rest = evens` and the display after it use both directions.
`*rest` collects on the left of the assignment and spreads inside the display,
so the pair builds a new list holding `evens` rotated by one place.
`evens` stays as it was.
`+` joins two lists as well, but both operands must be lists,
so `[0, 2] + (1, 3)` raises a `TypeError`.
[Functions](05_Foundations--Functions.md#unpacking-arguments)
uses the same star to spread an iterable into a call's arguments.

Tuples are often heterogeneous, with each position a different type:

```python
# heterogeneous.py

person = ("Alice", 30, 1.65)  # Name, age, height
name, age, height = person
print(name, age, height)
#: Alice 30 1.65
print(type(name).__name__, type(age).__name__,
      type(height).__name__)
#: str int float
```

A tuple used this way is a fixed-length immutable record,
where each position has a distinct meaning.
A tuple holding many values of one type is an immutable `list`.

## Dictionaries

A dictionary (`dict`) maps keys to values, with fast lookup.
Lookup computes a *hash* from each key:
an integer derived from the key's contents.
Python reduces that integer to the slot where the entry lives.
If a key's hash changes after insertion,
the next lookup computes a different slot and misses the entry.
So keys must be *hashable*: able to produce a hash that stays the same,
and comparable with `==`.
Lookup needs `==` because it checks that the key stored in the slot equals the key you looked up.
Strings, numbers, and tuples of hashable values are hashable.
A `list`, a `dict`, and a `set` can change their contents,
so these mutable built-in containers are unhashable and cannot be keys.

```python
# dictionaries.py

ages = {"Alice": 30, "Bob": 25}
print(ages)
#: {'Alice': 30, 'Bob': 25}
print(ages["Alice"])
#: 30
ages["Carol"] = 41  # Add or update
print("Bob" in ages)  # Membership tests the keys
#: True
# A default when the key is missing
print(ages.get("Dan", 0))
#: 0
print(list(ages))  # Iterating over a dict yields its keys
#: ['Alice', 'Bob', 'Carol']
print(list(ages.values()))
#: [30, 25, 41]
for name, age in ages.items():
    print(name, age)
#: Alice 30
#: Bob 25
#: Carol 41
```

When a key might be missing, use `dict.get()`,
which returns a default where `[]` raises a `KeyError`.

Iterating over a `dict` follows insertion order, which the language guarantees.
CPython 3.6 first kept that order, as an implementation detail.
Python 3.7 made the order part of the language.
Since Python 3.8, `reversed()` walks a `dict`, or any of its views,
from the newest entry back to the oldest.

`collections.OrderedDict`, added in Python 3.1,
kept insertion order before `dict` did.
`dict` still lacks two `OrderedDict` features.
Two `OrderedDict`s compare equal when they hold the same entries in the same order,
where `dict` equality ignores order.
`move_to_end()` moves a key to either end,
the step a least-recently-used cache takes each time it reads an entry.

`keys()`, `values()`, and `items()` each return a *view*:
an object that reads the `dict`'s current contents each time you use it,
rather than a copy.
A view therefore also shows the entries added after you made it.

`items()` alone yields `(key, value)` pairs.

Leaving off `items()` is a common slip.
`for name, age in ages` iterates over the keys and tries to unpack each one:

```python
# forgot_items.py

ages = {"Alice": 30, "Bob": 25}
try:
    for name, age in ages:  # [1]
        print(name, age)
except ValueError as e:
    print(e)
#: too many values to unpack (expected 2)
for name, age in {"Bo": 1, "Al": 2}:  # [2]
    print(name, age)
#: B o
#: A l
```

At `[1]`, unpacking `"Alice"` into two names raises a `ValueError`,
since the string has more than two characters.
At `[2]`, every key has two characters,
so each key unpacks into its two letters.

`keys()` is also set-like, and so is `items()` when every value is hashable.
Each supports the [set operators](#sets) `&`, `|`, `-`,
and `^` against another dict's view or against any set.

```python
# dict_views.py

ages = {"Alice": 30, "Bob": 25, "Carol": 41}
names = ages.keys()
ages["Dan"] = 19
print(names)  # The view sees the new key
#: dict_keys(['Alice', 'Bob', 'Carol', 'Dan'])
other = {"Bob": 0, "Eve": 0}
print(names & other.keys())  # Set algebra on a view
#: {'Bob'}
```

`|` merges two dictionaries, `pop()` and `del` remove entries,
and `dict()` builds a dictionary from pairs:

```python
# dict_ops.py

a = {"x": 1, "y": 2}
b = {"y": 20, "z": 3}
print(a | b)  # Merge; the right side wins a collision
#: {'x': 1, 'y': 20, 'z': 3}
print({**a, **b})  # The same merge by unpacking
#: {'x': 1, 'y': 20, 'z': 3}
print(a.pop("x"), a)  # Remove and return
#: 1 {'y': 2}
del b["z"]
print(b)
#: {'y': 20}
print(dict(zip("abc", [1, 2, 3])))  # Build from pairs
#: {'a': 1, 'b': 2, 'c': 3}
```

`|=` updates the left `dict` in place, as `update()` does.
For sets, `|` means union, so the operands can come in either order.
For dictionaries the order matters.
When both dictionaries hold the same key,
the merged `dict` keeps the right operand's value, so `"y"` comes out as `20`.

`**` spreads each dictionary's entries the way `*` spreads a list's elements.
A later entry replaces an earlier one with the same key.
Like a list display,
a `dict` display accepts any number of double-starred operands,
with ordinary `key: value` entries among them.

[`zip()`](04_Foundations--Control_Flow.md#range-enumerate-and-zip)
pairs up two sequences element by element,
so `zip("abc", [1, 2, 3])` yields `("a", 1)`, `("b", 2)`, and `("c", 3)`.
`dict()` accepts any iterable of `(key, value)` pairs and builds a `dict` from them.

A merge copies entries into a new `dict`,
so a later change to `a` or `b` leaves the merged `dict` as it was.
A `ChainMap`, from the `collections` module,
keeps its dictionaries separate and searches them in order:

```python
# chain_map.py
from collections import ChainMap

defaults = {"theme": "light", "zoom": 100}
user = {"zoom": 125}
prefs = ChainMap(user, defaults)
print(prefs["zoom"], prefs["theme"])
#: 125 light
user["theme"] = "dark"
print(prefs["theme"])  # It reads the live dicts
#: dark
prefs["zoom"] = 150  # Writes go to the first dict
print(user["zoom"], defaults["zoom"])
#: 150 100
```

A lookup tries `user` first and falls back to `defaults`,
so `"zoom"` comes from `user`,
and `"theme"` comes from `defaults` until `user` gains its own.
Python looks up a variable name the same way,
through a chain of scopes that ends at the builtins.
Assignment and `del` act on the first dictionary,
so `defaults` keeps its values.

The `list` in `remove_while_iterating.py` skips elements silently.
Changing the size of a `dict` or a `set` while iterating over it raises a `RuntimeError`:

```python
# dict_iteration_trap.py

d = {"a": 1, "b": 2, "c": 3}
try:
    for k in d:
        del d[k]
except RuntimeError as e:
    print(e)
#: dictionary changed size during iteration
s = {1, 2, 3}
try:
    for x in s:
        s.discard(x)
except RuntimeError as e:
    print(e)
#: Set changed size during iteration
```

[`discard()`](#sets) removes an element from a `set`.

Assigning a new value to an existing key leaves the size the same,
so a loop can update a `dict`'s values safely.
To delete entries as you go, iterate over a copy of the keys,
`for k in list(d):`, as `for x in xs[:]` does for a `list`.

## Sets

A set is an unordered collection of unique items.
Like the `dict`, it finds an item by its hash,
so membership tests are fast and every item must be hashable.
Sets also provide the operators of mathematical set algebra:

```python
# sets.py

a = {1, 2, 3, 3}  # Duplicates collapse
print(a)
#: {1, 2, 3}
print(type({}).__name__, type(set()).__name__)
#: dict set
b = {3, 4, 5}
print(a & b)  # Intersection
#: {3}
print(a | b)  # Union
#: {1, 2, 3, 4, 5}
print(a - b)  # Difference
#: {1, 2}
print(a ^ b)  # Symmetric difference
#: {1, 2, 4, 5}
c = {1, 2}
print(c <= a)  # Subset
#: True
print(a >= c)  # Superset
#: True
print(2 in a)
#: True
```

`{}` was the empty `dict` before sets had a literal, so an empty set is `set()`.

CPython's hashing decides the order in which these sets print.
That order is an implementation detail, so write code, and tests,
that accept the elements in any order.

Every set-algebra operator in `sets.py` has a named method:
`intersection()` for `&`, `union()` for `|`, `difference()` for `-`,
`symmetric_difference()` for `^`, `issubset()` for `<=`,
and `issuperset()` for `>=`.
The methods accept any iterable where the operators need a set on both sides.
`union()`, `intersection()`,
and `difference()` also take several arguments at once.
`isdisjoint()` adds one more test, with no operator form:

```python
# set_methods.py

a = {1, 2, 3}
b = {3, 4, 5}

print(a.intersection([2, 3, 9]))  # Arg can be any iterable
#: {2, 3}
print(a.union(b, [6, 7]))  # Several args
#: {1, 2, 3, 4, 5, 6, 7}
print(a.isdisjoint({8, 9}))  # No operator form
#: True
```

`sets.py` leaves out a few operators.
`<` and `>` test *proper* subset and superset.
They behave like `<=` and `>=` but also require the two sets to differ.
The augmented assignments `|=`, `&=`, `-=`, and `^=` modify a set in place.
They match the `update()`, `intersection_update()`, `difference_update()`,
and `symmetric_difference_update()` methods.

`add()` inserts a single element, and `remove()` and `discard()` delete one.
`remove()` raises a `KeyError` on a missing element,
where a `list`'s `remove()` raises a `ValueError`.
`discard()` ignores a missing element.

Repeated lookups run faster against a `set` than against a `list`.
A `list` compares the item you look for against every element in turn.
A `set` computes one hash and usually looks in one slot.

`timeit()` runs a callable `number` times and returns the total elapsed seconds.
The [`lambda:`](05_Foundations--Functions.md#lambdas)
prefix wraps an expression into the callable `timeit()` needs:

```python
# membership_cost.py
from timeit import timeit
from benchmark import report

def scan_gap(n):
    items = list(range(n))
    lookup = set(items)
    missing = -1
    list_time = timeit(lambda: missing in items, number=20)
    set_time = timeit(lambda: missing in lookup, number=20)
    return list_time / set_time

small_gap = scan_gap(20_000)
large_gap = scan_gap(200_000)
report(small_n=small_gap, large_n=large_gap)
print(large_gap > small_gap)  # The gap widens
#: True
```

O(n) (read "order n") describes work that grows in proportion to `n`,
the number of elements.
O(1) describes work that stays the same however large `n` gets.
Searching the `list` is O(n) and searching the `set` is O(1),
so the gap keeps widening as `n` grows.
At ten times the size the `list` search takes roughly ten times as long,
while the `set` search takes about the same time,
so `large_gap` comes out bigger than `small_gap`.

`missing` holds a value absent from both containers, on purpose.
Searching for an absent item is the `list`'s worst case,
since the scan compares all `n` elements before reporting `False`.

A timing depends on the machine that took it,
so nearly every measured listing in this book prints a comparison rather than a number.
The measurements behind the comparison go to `report()`,
a small helper the book supplies.
By default a measured listing prints the comparison alone.
Running one with [`--numbers`](18_Techniques--Performance.md#numbers-on-your-machine)
makes `report()` print the measurements as well.

## Specialized Containers

The `collections` module in the standard library includes container types built for specific jobs.
Four of them come up often: `Counter`, `defaultdict`, `deque`, and `namedtuple`.

### `Counter`

A `Counter` tallies the frequency of each item:

```python
# counter.py
from collections import Counter

words = "a cat sat on a mat a cat".split()
counts = Counter(words)
print(counts)
#: Counter({'a': 3, 'cat': 2, 'sat': 1, 'on': 1, 'mat': 1})
print(counts["a"])
#: 3
print(counts["dog"])
#: 0
print("dog" in counts)  # Reading it added nothing
#: False
print(counts.most_common(2))
#: [('a', 3), ('cat', 2)]
print(Counter("aab") - Counter("ab"))  # Multiset diff
#: Counter({'a': 1})
print(Counter("aab") + Counter("abc"))  # Sum
#: Counter({'a': 3, 'b': 2, 'c': 1})
counts += Counter(["cat", "dog"])  # Add in place
print(counts["cat"], counts["dog"])
#: 3 1
print(Counter("aaab") ^ Counter("abbc"))  # Symmetric diff
#: Counter({'a': 2, 'b': 1, 'c': 1})
```

A missing key counts as zero rather than raising a `KeyError`.
`-`, `&`, and `|` also work between two counters.
They are the operators from [Sets](#sets), here meaning multiset difference,
minimum, and maximum.
Python 3.15 adds `^`, the multiset symmetric difference,
which gives each item the larger of its two counts minus the smaller.

### `defaultdict`

A `defaultdict` supplies a value the first time you look up a missing key,
and so removes the setup-on-first-use boilerplate:

```python
# defaultdict.py
from collections import defaultdict

pets = [("dog", "Rex"), ("cat", "Felix"), ("dog", "Fido")]
# A plain dict makes you create each list first:
plain = {}
for kind, name in pets:
    if kind not in plain:
        plain[kind] = []
    plain[kind].append(name)
print(plain["dog"])
#: ['Rex', 'Fido']
# A defaultdict creates the missing list:
by_kind = defaultdict(list)
for kind, name in pets:
    by_kind[kind].append(name)
print(by_kind["dog"])
#: ['Rex', 'Fido']
# A missing key gets a fresh empty list
print(by_kind["fish"])
#: []
print("fish" in by_kind)  # Reading it added the key
#: True
```

The `defaultdict` constructor argument is a *factory*,
a callable that builds the default.
Here, `list` produces a fresh empty list for each new key.
Reading a missing key runs the factory and stores its result,
so the lookup of `"fish"` adds that key to the dictionary.
For a lookup that leaves the dictionary as it was, use `in` or `dict.get()`.

A plain `dict` has a second option, `setdefault()`.
In `plain.setdefault(kind, []).append(name)`,
`setdefault()` returns the list already stored under `kind`.
When `kind` is missing, `setdefault()` stores the new `[]` and returns that.
The `[]` argument builds an empty list on every call.
A call that finds `kind` discards that list.
Every line that looks up a key must repeat `setdefault()` and its `[]` default.
A `defaultdict` states the default once, where you create the dictionary.

### `deque`

A `deque` (double-ended queue)
adds and removes items at either end in constant time:

```python
# deque.py
from collections import deque

dq = deque([1, 2, 3])
dq.append(4)  # Add on the right
dq.appendleft(0)  # Add on the left
print(dq)
#: deque([0, 1, 2, 3, 4])
print(dq.popleft())  # Remove from the left
#: 0
print(dq.pop())  # Remove from the right
#: 4
print(dq)
#: deque([1, 2, 3])
```

A `list` can also add and remove at either end:

```python
# list_as_deque.py

lst = [1, 2, 3]
lst.append(4)  # Add at the end
lst.insert(0, 0)  # Add at the start
print(lst)
#: [0, 1, 2, 3, 4]
print(lst.pop(0))  # Remove from the start
#: 0
print(lst.pop())  # Remove from the end
#: 4
print(lst)
#: [1, 2, 3]
```

A `list` can stand in for a `deque`.
`append()` and `pop()` at its end are O(1),
but `insert(0, x)` and `pop(0)` must shift every remaining element,
so both are O(n).
Timing `n` insertions and removals at the start of each container shows the difference:

```python
# deque_timing.py
from collections import deque
from timeit import timeit
from benchmark import report

n = 20_000

def list_left_ops():
    items = []
    for i in range(n):
        items.insert(0, i)
    while items:
        items.pop(0)

def deque_left_ops():
    items = deque()
    for i in range(n):
        items.appendleft(i)
    while items:
        items.popleft()

list_time = timeit(list_left_ops, number=1)
deque_time = timeit(deque_left_ops, number=1)
report(list_ops=list_time, deque_ops=deque_time)
print(deque_time * 20 < list_time)  # Not close
#: True
```

`True` means the `deque` finishes more than twenty times faster.
Use a `deque` for a queue.
Indexing its middle is O(n), though,
so keep a `list` wherever you index by position.
When one thread must wait for another to supply the next item,
use [`queue.Queue`](19_Techniques--Concurrency.md#coordinating-threads-with-queues),
whose `get()` blocks until an item arrives.
For a priority queue, use `heapq`.

A `deque(maxlen=n)` caps its length,
discarding from the opposite end when an append overflows it:

```python
# sliding_window.py
from collections import deque

window = deque(maxlen=3)  # A bounded sliding window
for i in range(5):
    window.append(i)
print(window)
#: deque([2, 3, 4], maxlen=3)
```

A `deque` with a `maxlen` is a sliding window.
A `list` keeps every item you append.

### `namedtuple`

A `namedtuple` builds a tuple subclass whose positions also have names:

```python
# named_tuple.py
from collections import namedtuple

Person = namedtuple("Person", ["name", "age", "height"])
alice = Person("Alice", 30, 1.65)
print(alice)
#: Person(name='Alice', age=30, height=1.65)
print(alice.name, alice.age)  # Access by name
#: Alice 30
print(alice[0])  # Still indexable like a tuple
#: Alice
name, age, height = alice  # And unpackable
print(height)
#: 1.65
```

A `namedtuple` is a fixed-length record like the tuple in `heterogeneous.py`,
but each field has a name, so `alice.age` says which value it reads.
`typing.NamedTuple` builds the same kind of tuple subclass from a `class` statement.
You write `class Person(NamedTuple):` and annotate each field in the body,
as in `name: str`, instead of listing bare names.
A type checker then verifies each field against its annotation.
For a record that must be mutable,
use a [data class](12_Techniques--Data_Classes_as_Types.md#data-classes).
[Data Transfer Objects](28_Patterns--Data_Transfer_Objects.md#the-standard-library-versions)
compares `typing.NamedTuple` with a data class.

The standard library has more specialized containers.
[Performance](18_Techniques--Performance.md) covers compact homogeneous storage
(`array`), a zero-copy view onto another object's memory (`memoryview`),
binary search in a sorted `list` (`bisect`), and a heap-backed priority queue
(`heapq`).

## Immutability

Each of the three built-in mutable containers has an immutable counterpart.
A `tuple` is an immutable `list`, and a `frozenset` is an immutable `set`.
Since Python 3.15, `frozendict` ([PEP 814](https://peps.python.org/pep-0814/))
completes the trio: a built-in mapping that rejects changes after creation.

A `frozenset` is hashable, so it can be a set member or a dictionary key.
A `list` or a `set` is unhashable, so it can be neither.
A `frozenset` also has no `add()` method,
so calling `add()` on one raises an `AttributeError`:

```python
# frozen_containers.py

primes = frozenset({2, 3, 5, 7})
print(5 in primes)
#: True
groups = {frozenset({1, 2}), frozenset({3, 4})}
print(frozenset({1, 2}) in groups)
#: True
try:
    primes.add(11)  # type: ignore
except AttributeError as e:
    print(e)
#: 'frozenset' object has no attribute 'add'
```

The type checker reports an attempt to modify an immutable container before the program runs.
The listings in this section make that attempt on purpose,
to show the exception Python raises when the program runs,
so each such line carries a `# type: ignore` comment.
That comment silences the type checker for its line.

Use the immutable form whenever a container should stay the same after you build it.
The container then keeps the same elements, whichever code holds it,
so you can share a container of immutable elements,
where a mutable one calls for a defensive copy.
An immutable container is safe as a default argument,
unlike the [mutable default](05_Foundations--Functions.md#the-mutable-default-trap).

`MappingProxyType`, from the `types` module,
is read-only without being immutable.
It is a view onto a `dict` you still hold, not a container of its own.
Like the `dict` views, it reads that `dict`'s current contents,
so it reflects every change to the `dict`:

```python
# mapping_proxy.py
from types import MappingProxyType

settings = {"debug": False, "level": 3}
config = MappingProxyType(settings)
print(config["level"])
#: 3
settings["level"] = 4
print(config["level"])
#: 4
try:
    config["level"] = 9  # type: ignore
except TypeError as e:
    print(e)
#: 'mappingproxy' object does not support item assignment
```

### `frozendict`

Where a `MappingProxyType` reads a `dict` that can still change,
a `frozendict` holds its own entries, copied in when you build it.
This listing requires Python 3.15:

```python
# frozendict_demo.py

prefs = frozendict(theme="dark", zoom=125)
print(prefs["zoom"])
#: 125
# Equal contents compare equal; entry order is ignored:
print(prefs == frozendict(zoom=125, theme="dark"))
#: True
cache = {prefs: "rendered"}  # Usable as a dict key
print(cache[frozendict(zoom=125, theme="dark")])
#: rendered
try:
    prefs["zoom"] = 150  # type: ignore
except TypeError as e:
    print(e)
#: 'frozendict' object does not support item assignment
```

Because a `frozendict` keeps its entries for its whole life,
it is hashable when its values are.
Like a `tuple` or a `frozenset`,
it can then be a dictionary key or a set member.
A dictionary key must be hashable, though it need not be immutable.
A container's hash comes from its contents,
so immutability keeps that hash stable.

### Shallow Immutability

Immutability is shallow.
An immutable container freezes which objects it holds,
not what those objects contain:

```python
# shallow_immutability.py

nested = (1, [2, 3])
nested[1].append(4)  # The tuple's element is still mutable
print(nested)
#: (1, [2, 3, 4])
try:
    hash(nested)  # So the tuple cannot be hashed
except TypeError as e:
    print(e)
#: unhashable type: 'list'
try:
    nested[0] = 9  # type: ignore
except TypeError as e:
    print(e)
#: 'tuple' object does not support item assignment
```

An immutable container holding an unhashable object is unhashable too.

Immutability is beneficial when every nested object is also immutable,
because then you can share or hash the container and trust that everything inside it stays the same.
[Rethinking Objects](20_Patterns--Rethinking_Objects.md#the-immutability-solution)
shows the same shallow immutability inside a frozen data class.

## Choosing a Container

Choosing a container comes down to one question: what do you do with it most?
Ordered items you walk through are a `list`.
A fixed-length record whose positions mean different things is a `tuple` or a `namedtuple`.
Lookup by key is a `dict`.
Uniqueness and membership are a `set`.
Go past those four only when a measurement or a specific job calls for it,
and freeze whichever you pick as soon as it stops changing.

## Exercises

Try each exercise before opening its [solution](../Solutions/03_Foundations--Containers/).

1.  In `deque_timing.py`, change `n` from `20_000` to `2_000`,
    change the printed comparison to `deque_time < list_time`,
    and run the timing again.
    Does `deque_time < list_time` still hold?
    Change `n` to `200_000` and try again.
    The list version takes several seconds at that size,
    and much longer on a slow machine.
    Explain what changes about the comparison as `n` grows.
2.  In `defaultdict.py`, replace `defaultdict(list)` with `defaultdict(int)`,
    change the loop to count occurrences of each `kind` instead of collecting names,
    and print the result.
3.  In `set_methods.py`,
    add a set `d = {1, 5, 9}` and print `a.union(b, d)` and `a.intersection(b, d)`.
4.  In `frozen_containers.py`, add a line that tries `groups.add([1, 2])`
    (a plain list, not a `frozenset`) and catch the exception it raises.
    Explain, in terms of hashability,
    why a `frozenset` works as a set member but a `list` does not.
5.  Given `xs = [10, 20, 30, 40, 50]`, write one slice expression for each of:
    the last two items, everything but the first and last,
    and a reversed copy of the middle three.
6.  Rewrite `counter.py`'s tally using a `defaultdict(int)` and no `Counter`.
    Which parts of `Counter` did you write yourself?
7.  Rewrite `heterogeneous.py` with a `namedtuple`.
    Show that the unpacking line still works unchanged.
8.  Given `pairs = [("a", 1), ("b", 2), ("c", 3)]`, build a `dict` from it,
    then print its keys, its values,
    and the result of merging it with `{"c": 30, "d": 4}`.
    Which value ends up under `"c"`, and why?
9.  Using one unpacking assignment each, and no indexing,
    pull the first element, the last element,
    and everything in between out of `row = [1, 2, 3, 4, 5]`.
    Then explain why `a, b = row` raises a `ValueError` while `a, *b = row` succeeds.
10. Build a `frozendict` from the pairs `[("host", "localhost"), ("port", 8080)]`,
    then use it as a key in a `dict` that maps a configuration to a connection name.
    Look the connection name up again with a separately built,
    equal `frozendict`.
    Catch the `TypeError` that assigning to one of its entries raises.
    Finally, build a `frozendict` whose value is a `list`, try to hash it,
    and explain the result in terms of shallow immutability.
