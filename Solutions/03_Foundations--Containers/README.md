# Containers: Solutions

## 1. Timing `deque` vs. `list` at different sizes

> In `deque_timing.py`, change `n` from `20_000` to `2_000`,
> change the printed comparison to `deque_time < list_time`,
> and run the timing again.
> Does `deque_time < list_time` still hold?
> Change `n` to `200_000` and try again.
> The list version takes several seconds at that size,
> and much longer on a slow machine.
> Explain what changes about the comparison as `n` grows.

<details>
<summary>Where to look</summary>

[`deque`](../../Chapters/03_Foundations--Containers.md#deque) compares the cost of operations at the left end of a `list` and of a `deque`.
Time a loop of `insert(0, x)` and `pop(0)` calls against `appendleft()` and `popleft()`, once at each size.
Count how many elements each left-end operation on a `list` must move, and compare that with the `deque` version as `n` grows.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from collections import deque
from timeit import timeit
from benchmark import report

def list_left_ops():
    ...

def deque_left_ops():
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_1.py
from collections import deque
from timeit import timeit
from benchmark import report

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
report(list=list_time, deque=deque_time)
print(deque_time < list_time)
#: True
```

`deque_time < list_time` holds at `n = 2_000`, `20_000`, and `200_000`.
But the margin grows with `n`: each `list.insert(0, x)` or
`list.pop(0)` shifts every remaining element, so the whole loop costs
O(n²). Each `deque` operation is O(1), so the `deque` loop costs O(n). At a few
dozen items the constant-factor overhead of a `deque` nearly closes the
gap, though by `n = 2_000` the `deque` finishes several times faster.
At large `n` the quadratic cost of the list dominates and the `deque`
wins by a wide and growing margin.

</details>
</details>
</details>

## 2. `defaultdict(int)` for counting

> In `defaultdict.py`, replace `defaultdict(list)` with `defaultdict(int)`,
> change the loop to count occurrences of each `kind` instead of collecting names,
> and print the result.

<details>
<summary>Where to look</summary>

[`defaultdict`](../../Chapters/03_Foundations--Containers.md#defaultdict) shows a factory called to create a missing value.
The factory here is `int`, so ask what `int()` returns when called with no arguments.
That default lets the loop add to a key before it exists.

<details>
<summary>Solution</summary>

If you start the tally from an empty `dict`,
the first `counts[kind] += 1` raises a `KeyError` for `'dog'`,
because `+=` reads the key before it writes it.
The solution uses `defaultdict(int)`, which supplies the `0` that the first read needs.

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

`defaultdict(int)` supplies `0` the first time the loop reads a key,
because `int()` returns `0`. That default turns `counts[kind] += 1`
into working code with no "does this key exist yet" check, the same
way `defaultdict(list)` removes the check for appending to a fresh
list.

</details>
</details>

## 3. Set operations across three sets

> In `set_methods.py`,
> add a set `d = {1, 5, 9}` and print `a.union(b, d)` and `a.intersection(b, d)`.

<details>
<summary>Where to look</summary>

[Sets](../../Chapters/03_Foundations--Containers.md#sets) lists the set operators, and `set_methods.py` shows the method forms of the same operations.
The methods `union()` and `intersection()` take several arguments at once.
Pass `b` and `d` in a single call to each.

<details>
<summary>Solution</summary>

```python
# exercise_3.py
a = {1, 2, 3}
b = {3, 4, 5}
d = {1, 5, 9}
print(a.union(b, d))
#: {1, 2, 3, 4, 5, 9}
print(a.intersection(b, d))
#: set()
```

`union()` and `intersection()` accept any number of arguments, unlike
the `|` and `&` operators, which take two operands at a time.
The three-way intersection is empty because no single value is a
member of all three sets.

</details>
</details>

## 4. Why a `list` cannot join a set of `frozenset`s

> In `immutable_containers.py`, add a line that tries `groups.add([1, 2])`
> (a plain list, not a `frozenset`) and catch the exception it raises.
> Explain, in terms of hashability,
> why a `frozenset` works as a set member but a `list` does not.

<details>
<summary>Where to look</summary>

[Immutability](../../Chapters/03_Foundations--Containers.md#immutability) explains that immutable containers are hashable, so they can be set members or dictionary keys.
A `set` must hash each element when it adds it.
Wrap the `groups.add()` call in a `try`, catch `TypeError`, and relate the message to what a `list` allows you to do after creation.

<details>
<summary>Solution</summary>

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

A `set` hashes each element once, at insertion, so every element must
be hashable. `frozenset` is hashable because it is immutable: its
contents stay fixed after creation, so its hash stays valid. A `list`
is mutable, so Python refuses to hash it, and an object with no hash
cannot be a set member or a dictionary key.

</details>
</details>

## 5. Four slices of one list

> Given `xs = [10, 20, 30, 40, 50]`, write one slice expression for each of:
> the last two items, everything but the first and last,
> and a reversed copy of the middle three.

<details>
<summary>Where to look</summary>

[Indexing and Slicing](../../Chapters/03_Foundations--Containers.md#indexing-and-slicing) covers `start`, `stop`, and `step`, and the way negative values count from the end.
You can slice a slice to reverse a copy.
A negative `step` also reverses in a single slice, but then `start` and `stop` swap roles.

<details>
<summary>Solution</summary>

If you fold the two slices into one as `xs[1:4:-1]`, you get an empty list.
A negative `step` walks left from `start`,
and index `1` lies left of the stop at `4`,
so the slice ends before it takes an item.
The one-slice form in the solution swaps the bounds to `xs[3:0:-1]`.

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
`xs[1:-1]` trims one from each end. The reversed middle has two
forms: slice, then reverse the copy, or walk backwards with a
negative `step`. The one-slice form is harder to read because the
bounds swap roles: `3` is now the first index visited and `0` is the
excluded stop, so the element at index `0` does not appear.

</details>
</details>

## 6. `defaultdict(int)` in place of `Counter`

> Rewrite `counter.py`'s tally using a `defaultdict(int)` and no `Counter`.
> Which parts of `Counter` did you have to write yourself?

<details>
<summary>Where to look</summary>

[`Counter`](../../Chapters/03_Foundations--Containers.md#counter) lists what `Counter` provides beyond a tally, and [`defaultdict`](../../Chapters/03_Foundations--Containers.md#defaultdict) shows the factory that creates missing entries.
Write the counting loop with `defaultdict(int)`.
Then reproduce `most_common()` with `sorted()` and a `key` function, and notice what reading a missing key does to each container.

<details>
<summary>Solution</summary>

If you leave the minus sign out of the `key` function,
`sorted()` ranks the lowest counts first,
and the slice prints `[('dog', 0), ('sat', 1)]`.
The `'dog'` entry is the `0` that the earlier `counts["dog"]` read stored.
`most_common()` ranks from the highest count down,
so the key negates each count to put the largest first.

```python
# exercise_6.py
from collections import defaultdict

words = "a cat sat on a mat a cat".split()
counts = defaultdict(int)
for word in words:
    counts[word] += 1
print(dict(counts))
#: {'a': 3, 'cat': 2, 'sat': 1, 'on': 1, 'mat': 1}
print(counts["dog"])  # Missing keys still read as zero
#: 0
print(sorted(counts.items(), key=lambda kv: -kv[1])[:2])
#: [('a', 3), ('cat', 2)]
```

**Count each word.** First, you write the loop yourself. `Counter(words)`
counts an iterable inside its constructor, while `defaultdict(int)`
removes the "does this key exist yet" check and leaves the counting to
you.

**Default a missing key to zero.** A read of a missing key also leaves a `Counter` alone, while
`defaultdict(int)` stores a `0` for `"dog"`, so their contents differ
after the `counts["dog"]` line.

**Rebuild the reporting.** The rest is what `Counter` supplies after the tally:
`most_common()` becomes a `sorted()` call with a key function and a
slice, and the `Counter({...})` repr becomes a `dict()` conversion.

</details>
</details>

## 7. `heterogeneous.py` as a `namedtuple`

> Rewrite `heterogeneous.py` with a `namedtuple`.
> Show that the unpacking line still works unchanged.

<details>
<summary>Where to look</summary>

[`namedtuple`](../../Chapters/03_Foundations--Containers.md#namedtuple) builds a tuple subclass with named fields.
Because the result is still a tuple, the unpacking from [Tuples and Unpacking](../../Chapters/03_Foundations--Containers.md#tuples-and-unpacking) works by position.
Create the class with `namedtuple()`, keep the unpacking line as it was, and add a line that reads a field by name.

<details>
<summary>Solution</summary>

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

The unpacking line stays the same, because a `namedtuple` is a tuple
subclass: it unpacks by position like any other tuple. The names add
the second `print()`, where `person.height` says what `person[2]`
means. They cost nothing, so a heterogeneous tuple that outlives one
function is usually better as a `namedtuple` or a data class.

</details>
</details>

## 8. Building and merging a `dict`

> Given `pairs = [("a", 1), ("b", 2), ("c", 3)]`, build a `dict` from it,
> then print its keys, its values,
> and the result of merging it with `{"c": 30, "d": 4}`.
> Which value ends up under `"c"`, and why?

<details>
<summary>Where to look</summary>

[Dictionaries](../../Chapters/03_Foundations--Containers.md#dictionaries) shows the `dict` constructor and the merge operators in `dict_ops.py`.
The `dict()` constructor accepts an iterable of pairs.
The `|` operator builds a new `dict`, so decide from `update()` which operand supplies the value when both hold the same key.

<details>
<summary>Solution</summary>

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

**Build the dictionary.** `dict()` accepts any iterable of two-item pairs, so a list of tuples
becomes a dictionary with no loop. `dict(zip(names, values))` is the
same constructor fed from two parallel sequences.

**Resolve the collision.** `30` ends up under `"c"`, because `|` resolves a collision in favor of
the right operand. The rule follows from what a merge must be: the
result is one value per key, and the two dictionaries disagree about
`"c"`, so one of them must lose. The right intuition for `a | b` is
"start from `a`, then apply `b`", and that reading matches
`a.update(b)`, which has always worked that way.

**Leave the left operand unchanged.** `|=` updates the left dictionary in place, while
`|` builds a new one and leaves the left operand alone, as the last
`print(counts)` above confirms.

Letting the right operand win makes `|` on dictionaries asymmetric,
unlike `|` on sets, where `a | b` and `b | a` are the same set. The
two uses share one operator because both mean "combine," but only the
set version commutes.

</details>
</details>

## 9. Unpacking without indexing

> Using one unpacking assignment each, and no indexing,
> pull the first element, the last element,
> and everything in between out of `row = [1, 2, 3, 4, 5]`.
> Then explain why `a, b = row` raises a `ValueError` while `a, *b = row` does not.

<details>
<summary>Where to look</summary>

[Tuples and Unpacking](../../Chapters/03_Foundations--Containers.md#tuples-and-unpacking) shows a starred target collecting the leftover items into a `list`.
Put the star on the target that should absorb the middle, or at either end.
For the explanation, compare how many items an unstarred target list requires with how many a starred one allows.

<details>
<summary>Solution</summary>

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

**Absorb the remaining items.** A starred target absorbs however many items remain, so one assignment
reaches any of the three positions without an index. The star may
appear anywhere in the target list, so `first, *middle, last = row`
works: `first` and `last` each take one item and `middle` takes the
rest, however many that is.

**Reject a count mismatch.** `a, b = row` fails because an unstarred target list states an exact
count, two, and `row` holds five. Python raises a `ValueError` rather
than dropping the extras, since a silent drop would hide the mismatch.
The same error appears in the other direction, as
`not enough values to unpack`, when the list is shorter than the
target list.

`a, *b = row` states a minimum instead: at least one item for `a`, and
the rest, possibly none, for `b`. So the assignment accepts a
five-item list, a one-item list, and everything between. Only an
empty list falls short. The star turns a fixed-shape assertion into a
flexible one, and the same flexibility lets `*args` work in a
function signature.

</details>
</details>

## 10. A `frozendict` as a dictionary key

> Build a `frozendict` from the pairs `[("host", "localhost"), ("port", 8080)]`,
> then use it as a key in a `dict` that maps a configuration to a connection name.
> Look the connection name up again with a separately built,
> equal `frozendict`.
> Catch the `TypeError` that assigning to one of its entries raises.
> Finally, build a `frozendict` whose value is a `list`, try to hash it,
> and explain the result in terms of shallow immutability.

<details>
<summary>Where to look</summary>

[`frozendict`](../../Chapters/03_Foundations--Containers.md#frozendict) shows construction, equality, and the error on assignment, and [Shallow Immutability](../../Chapters/03_Foundations--Containers.md#shallow-immutability) shows how far immutability reaches.
A dictionary finds a key by hash and equality, so a separately built, equal `frozendict` locates the same entry.
For the last part, ask what `hash()` must do with each value, and what a `list` value does to that.

<details>
<summary>Solution</summary>

```python
# exercise_10.py

pairs = [("host", "localhost"), ("port", 8080)]
config = frozendict(pairs)
print(config)
#: frozendict({'host': 'localhost', 'port': 8080})
connections = {config: "primary"}
same = frozendict(port=8080, host="localhost")
print(connections[same])
#: primary
try:
    config["port"] = 9090  # type: ignore
except TypeError as e:
    print(e)
#: 'frozendict' object does not support item assignment

nested = frozendict(tags=["a", "b"])
try:
    hash(nested)
except TypeError as e:
    print(e)
#: unhashable type: 'list'
```

**Build the configuration.** `frozendict` takes the same arguments `dict` does: an iterable of
two-item pairs, keyword arguments, or another mapping. So `pairs`
builds the same object `frozendict(host="localhost", port=8080)`
would.

**Look up by an equal key.** The lookup with `same` succeeds because a dictionary finds a key by
hash and equality, so an equal key need not be the same object.
`config` and `same` are separate objects built in different entry
orders, but they hold the same pairs, so they compare equal and hash
the same. A `frozendict` key gives you that property: any equal
configuration reaches the same entry, whoever built it and whenever.

**Catch the rejected assignment.** Assigning to an entry raises a `TypeError` rather than quietly
succeeding, and the type checker rejects the assignment too, so the
line carries a `# type: ignore`. The runtime exception is the point of the
listing.

**Find the limit of immutability.** `nested` shows how far that immutability reaches. A `frozendict` freezes
which objects it maps its keys to, not what those objects contain, so
`hash(nested)` must hash a `list` and fails. The immutability is
shallow, as it is for the `tuple` in `shallow_immutability.py`.
`frozendict` is hashable *when its values are*, so keep values
immutable, a `tuple` here instead of a `list`, whenever the mapping has
to serve as a key.

</details>
</details>
