# Containers

In C++ and Java a container is a library class you name and construct.
Python builds its containers into the grammar: `[1, 2]`, `{"a": 1}`,
and `{1, 2}` are literals, and `in`, `len()`,
and slicing work on them without importing anything.
Lists, tuples, dictionaries, and sets are fundamental data types.

## Lists

The `for` statement iterates through a list directly rather than counting through a sequence of numbers:

```python
# list.py

odds = [1, 3, 5, 7, 9, 11]
print(odds)
#: [1, 3, 5, 7, 9, 11]
odds.append(13)
for x in odds:
    print(x)
#: 1
#: 3
#: 5
#: 7
#: 9
#: 11
#: 13
```

The first line creates a `list`.
`append()` adds new elements to `odds`.
The `list` automatically resizes itself.
The `for` statement iterates through `odds`,
so `x` takes on each value in the `list`.

A `list` holds objects, of any kind, in an ordered, mutable sequence.
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
```

Slicing works on any sequence, including strings and tuples.

Lists grow, shrink, and answer questions about themselves:

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
`extend()` adds each item of its argument instead.

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

`sorted(x)` returns the result while `x.sort()` returns `None`,
so `x = x.sort()` binds `None` and loses the list.
Uppercase sorts before lowercase because the comparison is by code point;
[Functions](05_Functions.md#lambdas) shows how `key=` changes that.

A `list` does not restrict its elements to one type.
Since each slot holds a reference to whatever object you put there,
the same `list` can mix strings, numbers, `None`, and other containers:

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

This flexibility is convenient but easy to overuse.
A `list` of mixed types usually means each element needs different handling,
which is often better expressed with a `tuple`,
a [data class](12_Data_Classes_as_Types.md#data-classes), or distinct lists,
each holding a single type.

Two ways of building a `list` produce surprises.
`*` repeats a reference rather than copying what it points at,
so a grid built that way has one row under three names:

```python
# list_traps.py

grid = [[0]] * 3  # Three names for one inner list
grid[0][0] = 1
print(grid)
#: [[1], [1], [1]]
grid = [[0] for _ in range(3)]  # Three separate lists
grid[0][0] = 1
print(grid)
#: [[1], [0], [0]]
```

This is [Variables and References](02_Tour.md#variables-and-references) again:
`*` binds the same object into every slot, and assignment never copies.

Removing items from a `list` while iterating over it has the same flavor.
The loop advances an index as the list shrinks under it,
so it skips the element after every one you remove,
with no exception to tell you.
Build a new list instead, or iterate over a copy with `for x in xs[:]`.

A loop with `append()` is not the usual way to build a list from another one.
[Control Flow](04_Control_Flow.md#comprehensions) introduces the comprehension,
which does it in a single expression, and [Comprehensions](16_Comprehensions.md)
covers the dict and set forms.

## Tuples and Unpacking

A *tuple* is an immutable sequence.
The comma makes the tuple, not the parentheses.
Tuples are the natural way to return several values from a function and to group values for unpacking:

```python
# tuples.py

point = (3, 4)
point = 3, 4  # Also a tuple; the comma matters
empty = ()  # Empty tuple
x, y = point  # Unpacking
print(x, y)
#: 3 4
single = (42,)  # A one-element tuple needs the trailing comma
print(len(single))
#: 1
print(tuple([1, 2, 3]))  # Converts a list to a tuple
#: (1, 2, 3)
print(tuple("abc"))
#: ('a', 'b', 'c')

def min_max(values):
    return min(values), max(values)  # Returns a tuple

low, high = min_max([5, 2, 9, 1])
print(low, high)
#: 1 9
```

The empty tuple `()` is the exception to the comma rule,
because it has nothing to separate.

Unpacking is not limited to one name per element.
A starred name absorbs whatever is left over,
and a target can nest to match the shape of the value:

```python
# unpacking.py

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
    print(type(e).__name__)
#: ValueError
```

At most one target can be starred, and it always produces a `list`,
even when the source is a tuple or a string.
Without a star the number of names must equal the number of elements,
or the assignment raises `ValueError`.
A name whose value you never read is written `_` by convention,
so `*_` discards a run of elements.
[Pattern Matching](13_Pattern_Matching.md)
matches `case` patterns against the same shapes.

Tuples are often heterogeneous, with each position a different type:

```python
# heterogeneous.py

person = ("Alice", 30, 1.65)  # Name, age, height
name, age, height = person
print(name, age, height)
#: Alice 30 1.65
print(person[0], type(person[0]).__name__)
#: Alice str
print(person[1], type(person[1]).__name__)
#: 30 int
print(person[2], type(person[2]).__name__)
#: 1.65 float
```

A tuple used this way is a fixed-length immutable record,
where each position has a distinct meaning.
Used the other way, holding many values of one type, it is an immutable `list`.

## Dictionaries

A dictionary (`dict`) maps keys to values, with fast lookup.
Lookup computes a hash from each key, so keys must be *hashable*.
The mutable built-in containers (`list`, `dict`, `set`) are not hashable,
so they cannot serve as keys.
Strings, numbers, and tuples of hashable values can.

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
print(ages.get("Dan", 0))  # A default when the key is missing
#: 0
print(list(ages))  # Iterating a dict yields its keys
#: ['Alice', 'Bob', 'Carol']
print(list(ages.values()))
#: [30, 25, 41]
for name, age in ages.items():
    print(name, age)
#: Alice 30
#: Bob 25
#: Carol 41
```

Use `dict.get()` instead of `[]` to avoid a `KeyError` when a key might be absent.

A `dict` has three views: `keys()`, `values()`, and `items()`.
Iterating the `dict` itself is the same as iterating `keys()`,
which is why `for name in ages` walks the names.
Only `items()` yields `(key, value)` pairs,
so `for name, age in ages` is a common slip:
it iterates the keys and tries to unpack each one.

A `dict` iterates in insertion order, which the language guarantees.

Entries come out as easily as they go in, and two dictionaries combine:

```python
# dict_ops.py

a = {"x": 1, "y": 2}
b = {"y": 20, "z": 3}
print(a | b)  # Merge; the right side wins a collision
#: {'x': 1, 'y': 20, 'z': 3}
print(a.pop("x"), a)  # Remove and return
#: 1 {'y': 2}
del b["z"]
print(b)
#: {'y': 20}
print(dict(zip("abc", [1, 2, 3])))  # Build from pairs
#: {'a': 1, 'b': 2, 'c': 3}
```

`|` builds a merged `dict` and `|=` updates in place,
the same job `update()` does.
The next section uses `|` for set union, where the operands are symmetric.
They are not symmetric here: on a key both dictionaries hold,
the right operand's value wins, which is why `"y"` comes out as `20`.

## Sets

A set is an unordered collection of unique items.
Like the `dict`, it has fast membership tests.
Sets also provide the expected set algebra:

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

The `{}` literal was taken by `dict` first, so an empty set is `set()`.
The order these sets print comes from CPython's hashing, not from any guarantee,
so never write code, or a test, that depends on it.

Every set-algebra operator above has a named method.
The methods are a little more flexible because they accept any iterable,
not only a set, and they can take several arguments at once.
`isdisjoint()` is also available, with no operator form:

```python
# set_methods.py

a = {1, 2, 3}
b = {3, 4, 5}

print(a.intersection(b))  # Same as a & b
#: {3}
print(a.union(b))  # Same as a | b
#: {1, 2, 3, 4, 5}
print(a.difference(b))  # Same as a - b
#: {1, 2}
print(a.symmetric_difference(b))  # Same as a ^ b
#: {1, 2, 4, 5}
print(a.intersection([2, 3, 9]))  # Arg can be any iterable
#: {2, 3}
print(a.union(b, [6, 7]))  # Several args
#: {1, 2, 3, 4, 5, 6, 7}
c = {1, 2}
print(c.issubset(a))  # Same as c <= a
#: True
print(a.issuperset(c))  # Same as a >= c
#: True
print(a.isdisjoint({8, 9}))  # No operator form
#: True
```

A few operators do not appear above.
`<` and `>` test *proper* subset and superset.
They behave like `<=` and `>=` but also require the two sets to differ.
The augmented assignments `|=`, `&=`, `-=`, and `^=` modify a set in place.
They match the `update()`, `intersection_update()`, `difference_update()`,
and `symmetric_difference_update()` methods.

Speed is the reason to convert a `list` to a `set` before repeated lookups.
A `list` compares against every element in turn;
a `set` computes one hash and looks in one place.
`timeit()` runs a callable `number` times and returns the total elapsed seconds:

```python
# membership_cost.py
from timeit import timeit
from benchmark import report

n = 200_000
items = list(range(n))
lookup = set(items)
missing = -1
list_time = timeit(lambda: missing in items, number=20)
set_time = timeit(lambda: missing in lookup, number=20)
report(list_scan=list_time, set_lookup=set_time)
print(set_time * 100 < list_time)  # Not close
#: True
```

Searching the `list` is O(n) and searching the `set` is O(1),
so the gap widens without limit as `n` grows.

## Specialized Containers

The `collections` module in the standard library includes container types built for specific jobs.
Four of these show up consistently: `Counter`, `defaultdict`, `deque`,
and `namedtuple`.

### `Counter`

A `Counter` tallies the frequency of each item:

```python
# counter.py
from collections import Counter

words = "the cat sat on the mat the cat".split()
counts = Counter(words)
print(counts)
#: Counter({'the': 3, 'cat': 2, 'sat': 1, 'on': 1, 'mat': 1})
print(counts["the"])
#: 3
print(counts["dog"])
#: 0
print("dog" in counts)  # Reading it added nothing
#: False
print(counts.most_common(2))
#: [('the', 3), ('cat', 2)]
```

A missing key counts as zero rather than raising `KeyError`,
and `most_common()` returns the highest counts first.

### `defaultdict`

A `defaultdict` supplies a value the first time you touch a missing key,
which removes the setup-on-first-use boilerplate:

```python
# defaultdict.py
from collections import defaultdict

pets = [("dog", "Rex"), ("cat", "Felix"), ("dog", "Fido")]
# With a plain dict you must create each list before appending:
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
print(by_kind["fish"])  # A missing key gets a fresh empty list
#: []
print("fish" in by_kind)  # Reading it added the key
#: True
```

The `defaultdict` constructor argument is a *factory*,
a callable that builds the default.
The factory runs on the *read*, and the new value is stored,
so touching a missing key grows the dictionary.
Use `in` or `dict.get()` when you only want to look.
Here, `list` produces a fresh empty list for each new key.

A plain `dict` has a second option worth knowing:
`plain.setdefault(kind, []).append(name)` stores the default and returns it when the key is missing,
and returns the existing value when it is not.
It builds the empty list on every call, used or not,
and you must repeat it everywhere you touch the dictionary.
A `defaultdict` states the default once, where the dictionary is created.

### `deque`

A `deque` (double-ended queue)
adds and removes items at either end in constant time.
A `list` is fast only at its append end:

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
window = deque(maxlen=3)  # A bounded sliding window
for i in range(5):
    window.append(i)
print(window)
#: deque([2, 3, 4], maxlen=3)
```

A `list` has an operation for each of those four:

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

A `list` can stand in for a `deque`,
but `insert(0, x)` and `pop(0)` must shift every remaining element,
so both are O(n) instead of O(1).
Timing the two at the left end shows it:

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

A timing depends on the machine that took it,
so every measured listing in this book prints a comparison rather than a number.
`report()` comes from a small helper the book supplies,
and it stays silent unless you ask for the figures:
run the listing with `--numbers`
(see [Numbers on Your Machine](18_Performance.md#numbers-on-your-machine))
and it prints the two times it measured.

Use a `deque` for a single-threaded queue.
A `deque(maxlen=n)` additionally caps its length,
discarding from the far end when a new item overflows it,
which is the sliding window a `list` has no equivalent for.
For a queue shared between threads, use `queue.Queue`
(see [Concurrency](19_Concurrency.md)), and for a priority queue, `heapq`.

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

A `namedtuple` is a fixed-length record like the heterogeneous tuple above,
but its fields are self-documenting.
`typing.NamedTuple` is the class form of the same idea:
it declares a type for each field instead of listing bare names,
so a checker knows what each one holds.
For a record that must be mutable, use a data class
(see [Data Classes as Types](12_Data_Classes_as_Types.md#data-classes)).
[Data Transfer Objects](22_Data_Transfer_Objects.md#the-standard-library-versions)
compares all three.

The standard library has more specialized containers.
For compact homogeneous storage (`array`),
a zero-copy view onto another object's memory (`memoryview`),
binary search in a sorted `list` (`bisect`), and a heap-backed priority queue
(`heapq`), see [Performance](18_Performance.md).

## Immutability

Each of the three built-in mutable containers has an immutable counterpart.
A `tuple` is an immutable `list`, and a `frozenset` is an immutable `set`.
Since Python 3.15, `frozendict` ([PEP 814](https://peps.python.org/pep-0814/))
completes the set: a built-in,
hashable mapping that rejects modification after creation.
The example below uses tuples and frozensets,
plus `MappingProxyType` from the `types` module,
which is not a container of its own but a read-only *view* onto a `dict` you still hold:

```python
# immutability.py
from types import MappingProxyType

# A tuple is an immutable list, and a frozenset is an immutable set:
nums = (1, 2, 3)
primes = frozenset({2, 3, 5, 7})
print(5 in primes)
#: True

# Immutable containers are hashable, so they can be set members
# or dictionary keys. A plain list or set cannot:
groups = {frozenset({1, 2}), frozenset({3, 4})}
print(frozenset({1, 2}) in groups)
#: True

# MappingProxyType wraps a dict in a read-only view:
settings = {"debug": False, "level": 3}
config = MappingProxyType(settings)
print(config["level"])
#: 3
settings["level"] = 4  # The view is live, not a copy
print(config["level"])
#: 4

# Mutating any of them is an error:
try:
    primes.add(11)  # type: ignore
except AttributeError as e:
    print(type(e).__name__)
#: AttributeError
try:
    config["level"] = 9  # type: ignore
except TypeError as e:
    print(type(e).__name__)
#: TypeError
```

Each `# type: ignore` sits on a line that deliberately misbehaves.
Modifying an immutable container is a type error as well as a runtime one,
so the comment lets the example demonstrate the exception it expects.

Where a `MappingProxyType` is only a read-only window onto a `dict` that still exists and can change,
a `frozendict` owns its contents outright.
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
    print(type(e).__name__)
#: TypeError
```

Because a `frozendict` cannot change, it is hashable when its values are,
so like a `tuple` or a `frozenset` it can serve as a dictionary key or a set member.
The requirement on a dictionary key is hashability, not immutability.
Immutability is how a container earns a stable hash.

Use the immutable form whenever a container should not change after you build it.
Neither you nor code you pass it to can add, remove,
or replace an element by accident,
so a container of immutable elements needs no defensive copy before you share it.
It is safe to use as a default argument,
unlike the mutable default shown in [Functions](05_Functions.md#default-and-keyword-arguments).
A `MappingProxyType` is the one exception to watch.
It blocks writes through the view, but it is a window onto the original `dict`,
so changes to that underlying `dict` still show through,
as `immutability.py` showed when writing to `settings` changed what `config` reports.

Immutability is also shallow.
An immutable container fixes which objects it holds,
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
    print(type(e).__name__)
#: TypeError
try:
    nested[0] = 9  # type: ignore
except TypeError as e:
    print(type(e).__name__)
#: TypeError
```

The `tuple` refuses to let go of the `list`,
but nothing stops that `list` from changing,
and a container holding an unhashable object is itself unhashable.
Immutability pays off when it goes all the way down.
[Rethinking Objects](20_Rethinking_Objects.md#the-immutability-solution)
shows the same leak inside a frozen data class.

Choosing a container is mostly one question: what do you do with it most?
Ordered items you walk through are a `list`;
a fixed record whose positions mean different things is a `tuple` or a `namedtuple`;
lookup by key is a `dict`; uniqueness and membership are a `set`.
Go past those four only when a measurement or a specific job says to,
and freeze whichever you pick as soon as it stops changing.

## Exercises

1.  In `deque_timing.py`,
    change `n` from `20_000` to `2_000` and run the timing again.
    Does `deque_time < list_time` still hold?
    Change `n` to `200_000` and try again.
    The list version takes several seconds at that size,
    and much longer on a slow machine; that is the point.
    Explain what changes about the comparison as `n` grows.
2.  In `defaultdict.py`, replace `defaultdict(list)` with `defaultdict(int)`,
    change the loop to count occurrences of each `kind` instead of collecting names,
    and print the result.
3.  In `set_methods.py`,
    add a third set `c = {1, 5, 9}` and print `a.union(b, c)` and `a.intersection(b, c)`.
4.  In `immutability.py`, add a line that tries `groups.add([1, 2])`
    (a plain list, not a `frozenset`) and catch the exception it raises.
    Explain, in terms of hashability,
    why a `frozenset` works as a set member but a `list` does not.
5.  Given `xs = [10, 20, 30, 40, 50]`, write one slice expression for each of:
    the last two items, everything but the first and last,
    and a reversed copy of the middle three.
6.  Rewrite `counter.py`'s tally using a `defaultdict(int)` and no `Counter`.
    Which parts of `Counter` did you have to write yourself?
7.  Rewrite `heterogeneous.py` with a `namedtuple`.
    Show that the unpacking line still works unchanged.
8.  Given `pairs = [("a", 1), ("b", 2), ("c", 3)]`, build a `dict` from it,
    then print its keys, its values,
    and the result of merging it with `{"c": 30, "d": 4}`.
    Which value ends up under `"c"`, and why?
9.  Using one unpacking assignment each, and no indexing,
    pull the first element, the last element,
    and everything in between out of `row = [1, 2, 3, 4, 5]`.
    Then explain why `a, b = row` raises a `ValueError` while `a, *b = row` does not.
