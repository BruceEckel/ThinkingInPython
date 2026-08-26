# Containers: Solutions

## 1. Timing `deque` vs. `list` at different sizes

```python
# exercise_1.py
import sys
from collections import deque
from timeit import timeit

n = 2_000  # then 200_000

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
if "--numbers" in sys.argv:  # Exact times on your machine
    print(f"list {list_time:.6f}, deque {deque_time:.6f}")
print(deque_time < list_time)
#: True
```

`deque_time < list_time` holds at `n = 2_000`, `20_000`, and `200_000`.
But the *margin* grows with `n`: each `list.insert(0, x)` or
`list.pop(0)` shifts every remaining element, so the whole loop costs
O(n²). Each `deque` operation is O(1), so its loop costs O(n). At small
`n` the constant-factor overhead of a `deque` can nearly close the
gap; at large `n` the quadratic cost of the list dominates and the
`deque` wins by a wide and growing margin.

## 2. `defaultdict(int)` for counting

```python
# exercise_2.py
from collections import defaultdict

pets = [("dog", "Rex"), ("cat", "Felix"), ("dog", "Fido")]
counts = defaultdict(int)
for kind, name in pets:
    counts[kind] += 1
print(dict(counts))
#: {'dog': 2, 'cat': 1}
```

`defaultdict(int)` supplies `0` the first time a key is touched, since
`int()` returns `0`. That turns `counts[kind] += 1` into working code
with no "does this key exist yet" check, the same way `defaultdict(list)`
removed the check for appending to a fresh list.

## 3. Set operations across three sets

```python
# exercise_3.py
a = {1, 2, 3}
b = {3, 4, 5}
c = {1, 5, 9}
print(a.union(b, c))
#: {1, 2, 3, 4, 5, 9}
print(a.intersection(b, c))
#: set()
```

`union()` and `intersection()` accept any number of arguments, unlike
the `|` and `&` operators, which only take two operands at a time.
The three-way intersection is empty because no single value is a
member of all three sets.

## 4. Why a `list` cannot join a set of `frozenset`s

```python
# exercise_4.py
groups = {frozenset({1, 2}), frozenset({3, 4})}
try:
    groups.add([1, 2])
except TypeError as e:
    print(type(e).__name__)
    print(str(e).partition(" (")[0])
#: TypeError
#: cannot use 'list' as a set element
```

A `set`'s membership test relies on hashing every element once, up
front, so every element must be hashable. `frozenset` is hashable
because it is immutable: nothing can change its contents after
creation, so its hash never goes stale. A `list` is mutable, so Python
refuses to hash it at all, which is exactly why it cannot be a set
member or a dictionary key.

## 5. Four slices of one list

```python
# exercise_5.py
xs = [10, 20, 30, 40, 50]
print(xs[-2:])  # The last two items
#: [40, 50]
print(xs[1:-1])  # Everything but the first and last
#: [20, 30, 40]
print(xs[1:4][::-1])  # The middle three, reversed
#: [40, 30, 20]
print(xs[3:0:-1])  # The same three, in one slice
#: [40, 30, 20]
```

A negative `start` counts from the end, so `xs[-2:]` needs no length.
`xs[1:-1]` trims one from each end. The reversed middle can be written
two ways: slice, then reverse the copy, or walk backwards with a
negative `step`. The one-slice form is harder to read because the
bounds swap roles: `3` is now the first index visited and `0` is the
excluded stop, so the element at index `0` never appears.

## 6. `defaultdict(int)` in place of `Counter`

```python
# exercise_6.py
from collections import defaultdict

words = "the cat sat on the mat the cat".split()
counts: defaultdict[str, int] = defaultdict(int)
for word in words:
    counts[word] += 1
print(dict(counts))
#: {'the': 3, 'cat': 2, 'sat': 1, 'on': 1, 'mat': 1}
print(counts["dog"])  # Missing keys still read as zero
#: 0
print(sorted(counts.items(), key=lambda kv: -kv[1])[:2])
#: [('the', 3), ('cat', 2)]
```

The tally loop is the same length either way, since `defaultdict(int)`
removes the same "does this key exist yet" check that `Counter` does.
What has to be written by hand is everything else `Counter` supplies:
`most_common()` becomes a `sorted()` call with a key function and a
slice, and the `Counter({...})` repr becomes a `dict()` conversion.
`Counter` also leaves the dictionary alone when a missing key is read,
while `defaultdict(int)` stores a `0` for `"dog"`, so the two disagree
about their own contents after the last line above.

## 7. `heterogeneous.py` as a `namedtuple`

```python
# exercise_7.py
from collections import namedtuple

Person = namedtuple("Person", ["name", "age", "height"])
person = Person("Alice", 30, 1.65)
# Unchanged from the tuple version
name, age, height = person
print(name, age, height)
#: Alice 30 1.65
# Now also reachable by name
print(person.name, person.height)
#: Alice 1.65
print(person[0], type(person[0]).__name__)
#: Alice str
```

The unpacking line does not change, because a `namedtuple` is a tuple
subclass: it unpacks by position like any other tuple. What the names
add is the second line, where `person.height` says what `person[2]`
meant. Nothing is given up, which is why a heterogeneous tuple that
outlives one function is usually better as a `namedtuple` or a data
class.

## 8. Building and merging a `dict`

```python
# exercise_8.py

pairs = [("a", 1), ("b", 2), ("c", 3)]
counts = dict(pairs)
print(counts)
#: {'a': 1, 'b': 2, 'c': 3}
print(list(counts.keys()), list(counts.values()))
#: ['a', 'b', 'c'] [1, 2, 3]
print(counts | {"c": 30, "d": 4})
#: {'a': 1, 'b': 2, 'c': 30, 'd': 4}
print(counts)  # The merge built a new dict
#: {'a': 1, 'b': 2, 'c': 3}
```

`dict()` accepts any iterable of two-item pairs, so a list of tuples
becomes a dictionary with no loop. `dict(zip(names, values))` is the
same constructor fed from two parallel sequences.

`30` ends up under `"c"`, because `|` resolves a collision in favor of
the right operand. The rule follows from what a merge has to be: the
result is one value per key, and the two dictionaries disagree about
`"c"`, so one of them has to lose. Reading `a | b` as "start from `a`,
then apply `b`" gives the right intuition, and it matches `a.update(b)`,
which has always worked that way.

That makes `|` on dictionaries asymmetric, unlike `|` on sets, where
`a | b` and `b | a` are the same set. The operator is spelled the same
because both mean "combine," but only one of them commutes. `|=`
updates the left dictionary in place instead of building a new one,
which the last line above confirms is what `|` did not do.

## 9. Unpacking without indexing

```python
# exercise_9.py

row = [1, 2, 3, 4, 5]
first, *rest = row
print(first, rest)
#: 1 [2, 3, 4, 5]
*most, last = row
print(most, last)
#: [1, 2, 3, 4] 5
first, *middle, last = row
print(first, middle, last)
#: 1 [2, 3, 4] 5
try:
    a, b = row
except ValueError as e:
    print(e)
#: too many values to unpack (expected 2, got 5)
```

A starred target absorbs however many items are left over, so one
assignment reaches any of the three positions without an index. The
star may appear anywhere in the target list, which is what makes the
third line work: `first` and `last` each take one item and `middle`
takes the rest, however many that is.

`a, b = row` fails because an unstarred target list states an exact
count. Five values cannot fill two names, and Python raises a
`ValueError` rather than dropping the extras, since silently discarding
data is never the intent. The same error appears in the other
direction, as `too few values to unpack`, when the list is shorter than
the target.

`a, *b = row` states a minimum instead: at least one item for `a`, and
the rest, possibly none, for `b`. That is why it accepts a five-item
list, a one-item list, and everything between, and fails only on an
empty one. The star turns a fixed-shape assertion into a flexible one,
which is the same reason `*args` works in a function signature.
