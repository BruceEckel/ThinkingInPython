# Containers

With languages like C++ and Java, containers are add-on libraries.
Python acknowledges the essential nature of containers by building them into the core of the language.
Lists, dictionaries, and sets are fundamental data types.

## Lists and Iteration

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
The `for` statement iterates through `odds`, so `x` takes on each value in the `list`.

This example has no type declarations.
Each object carries its own type.

## Lists and Slicing

A `list` holds objects, of any kind, in an ordered, mutable sequence.
Indexing starts at zero, and negative indices count from the end.
A *slice* `[start:stop:step]` copies a subrange, with `stop` excluded:

```python
# slicing.py

xs = [10, 20, 30, 40, 50]
print(xs[0], xs[-1])  # First and last
#: 10 50
print(xs[1:3])   # The stop index is excluded
#: [20, 30]
print(xs[:2])    # From the start
#: [10, 20]
print(xs[2:])    # To the end
#: [30, 40, 50]
print(xs[::2])   # Every second item
#: [10, 30, 50]
print(xs[::-1])  # Reversed
#: [50, 40, 30, 20, 10]
xs.append(60)
print(xs)
#: [10, 20, 30, 40, 50, 60]
xs.insert(3, 5)
print(xs)
#: [10, 20, 30, 5, 40, 50, 60]
print(len(xs), 5 in xs)
#: 7 True
```

Slicing works on any sequence, including strings and tuples.

A `list` does not restrict its elements to one type.
Since each slot just holds a reference to whatever object you put there,
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
a [data class](12_Data_Classes_as_Types.md#data-classes),
or distinct lists, each holding a single type.

## Tuples and Unpacking

A *tuple* is an immutable sequence.
The comma makes the tuple, not the parentheses.
Tuples are the natural way to return several values from a function and to group values for unpacking:

```python
# tuples.py

point = (3, 4)
point = 3, 4        # Also a tuple; the comma is what matters
empty = ()          # Empty tuple
x, y = point        # Unpacking
print(x, y)
#: 3 4
single = (42,)      # A one-element tuple needs the trailing comma
print(len(single))
#: 1
print(tuple([1, 2, 3]))    # Converts a list to a tuple
#: (1, 2, 3)
print(tuple("abc"))
#: ('a', 'b', 'c')

def min_max(values):
    return min(values), max(values)  # Returns a tuple

low, high = min_max([5, 2, 9, 1])
print(low, high)
#: 1 9
```

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

Tuples are fixed-length immutable records where each position has a distinct meaning.

## Dictionaries

A dictionary (`dict`) maps keys to values, with fast lookup.
Lookup computes a hash from each key, so keys must be immutable.

```python
# dictionaries.py

ages = {"Alice": 30, "Bob": 25}
print(ages)
#: {'Alice': 30, 'Bob': 25}
print(ages["Alice"])
#: 30
ages["Carol"] = 41         # Add or update
print("Bob" in ages)       # Membership tests the keys
#: True
print(ages.get("Dan", 0))  # A default when the key is missing
#: 0
for name, age in ages.items():
    print(name, age)
#: Alice 30
#: Bob 25
#: Carol 41
```

Use `dict.get()` instead of `[]` to avoid a `KeyError` when a key might be absent.

## Sets

A set is an unordered collection of unique items.
Like the `dict`, it has fast membership tests.
Sets also provide the expected set algebra:

```python
# sets.py

a = {1, 2, 3, 3}  # Duplicates collapse
print(a)
#: {1, 2, 3}
b = {3, 4, 5}
print(a & b)      # Intersection
#: {3}
print(a | b)      # Union
#: {1, 2, 3, 4, 5}
print(a - b)      # Difference
#: {1, 2}
print(a ^ b)      # Symmetric difference
#: {1, 2, 4, 5}
c = {1, 2}
print(c <= a)     # Subset
#: True
print(a >= c)     # Superset
#: True
print(2 in a)
#: True
```

Every operator above has a named method.
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
They match the `update()`, `intersection_update()`, `difference_update()`, and `symmetric_difference_update()` methods.

## Specialized Containers

The `collections` module in the standard library includes container types built for specific jobs.
Four of these show up consistently: `Counter`, `defaultdict`, `deque`, and `namedtuple`.

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
print(counts.most_common(2))
#: [('the', 3), ('cat', 2)]
```

A missing key counts as zero rather than raising `KeyError`, and `most_common()` returns the highest counts first.

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
# A defaultdict creates the missing list for you:
by_kind = defaultdict(list)
for kind, name in pets:
    by_kind[kind].append(name)
print(by_kind["dog"])
#: ['Rex', 'Fido']
print(by_kind["fish"])  # A missing key gets a fresh empty list
#: []
```

The `defaultdict` constructor argument is a *factory*, a callable that builds the default.
Here, the `list` argument is a factory that produces a fresh empty list for each new key.

### `deque`

A `deque` (double-ended queue) adds and removes items at either end in constant time.
A `list` is fast only at its right end:

```python
# deque.py
from collections import deque
from timeit import timeit

dq = deque([1, 2, 3])
dq.append(4)         # Add on the right
dq.appendleft(0)     # Add on the left
print(dq)
#: deque([0, 1, 2, 3, 4])
print(dq.popleft())  # Remove from the left
#: 0
print(dq.pop())      # Remove from the right
#: 4
print(dq)
#: deque([1, 2, 3])

# A plain list can act as a double-ended queue too:
lst = [1, 2, 3]
lst.append(4)        # Add on the right
lst.insert(0, 0)     # Add on the left
print(lst)
#: [0, 1, 2, 3, 4]
print(lst.pop(0))    # Remove from the left
#: 0
print(lst.pop())     # Remove from the right
#: 4
print(lst)
#: [1, 2, 3]

# Time it to see the difference:
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
print(deque_time < list_time)
#: True
```

A `list` can stand in for a `deque`, but `insert(0, x)` and `pop(0)`
must shift every remaining element, so both are O(n) instead of O(1).
Use a `deque` whenever you need a queue.

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
print(alice[0])               # Still indexable like a tuple
#: Alice
name, age, height = alice     # And unpackable
print(height)
#: 1.65
```

A `namedtuple` is a fixed-length record like the heterogeneous tuple above,
but its fields are self-documenting.
For records with defaults, methods, or type annotations,
prefer a data class (see [Data Classes as Types](12_Data_Classes_as_Types.md#data-classes)).

The standard library has more specialized containers.
For compact homogeneous storage (`array`, `memoryview`) and algorithms over a sorted `list` (`bisect`, `heapq`),
see [Performance](18_Performance.md).

## Immutability

Each mutable container has an immutable counterpart.
A `tuple` is an immutable `list`, and a `frozenset` is an immutable `set`.
Since Python 3.15, `frozendict` ([PEP 814](https://peps.python.org/pep-0814/))
completes the set: a built-in, hashable mapping that rejects modification after creation.
The example below uses tuples and frozensets, plus `MappingProxyType` from the
`types` module, which is not a container of its own but a read-only *view* onto a
`dict` you still hold:

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

Where a `MappingProxyType` is only a read-only window onto a `dict` that still
exists and can change, a `frozendict` owns its contents outright.
It runs under Python 3.15, though type checkers may need a release or two to
recognize the new built-in:

```python
prefs = frozendict(theme="dark", zoom=125)
print(prefs["zoom"])         # 125
prefs == frozendict(zoom=125, theme="dark")  # True; order ignored
prefs["zoom"] = 150          # TypeError: item assignment unsupported
```

Because a `frozendict` cannot change, it is hashable, so like a `tuple` or a
`frozenset` it can serve as a dictionary key or a set member.
This is also why dictionary keys must be immutable.

Use the immutable form whenever a container should not change after you build it.
Neither you nor code you pass it to can modify an immutable container by accident,
so you never need a defensive copy before sharing it.
It is safe to use as a default argument, unlike the mutable default shown in [Functions](05_Functions.md#default-and-keyword-arguments).
A `MappingProxyType` is the one exception to watch.
It blocks writes through the view, but it is a window onto the original `dict`,
so changes to that underlying `dict` still show through.

## Exercises

1.  In `deque.py`, change `n` from `20_000` to `2_000` and run the timing again.
    Does `deque_time < list_time` still hold?
    Change `n` to `200_000` and try again.
    Explain what changes about the comparison as `n` grows.
2.  In `defaultdict.py`, replace `defaultdict(list)` with `defaultdict(int)`,
    change the loop to count occurrences of each `kind` instead of collecting names,
    and print the result.
3.  In `set_methods.py`, add a third set `c = {1, 5, 9}` and print `a.union(b, c)`
    and `a.intersection(b, c)`.
4.  In `immutability.py`, add a line that tries `groups.add([1, 2])`
    (a plain list, not a `frozenset`) and catch the exception it raises.
    Explain, in terms of hashability, why a `frozenset` works as a set member but a `list` does not.
