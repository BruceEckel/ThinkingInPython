# Containers: Solutions

## 1. Timing `deque` vs. `list` at different sizes

```python
# exercise_1.py
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
    print(e)
#: TypeError
#: cannot use 'list' as a set element (unhashable type: 'list')
```

A `set`'s membership test relies on hashing every element once, up
front, so every element must be hashable. `frozenset` is hashable
because it is immutable: nothing can change its contents after
creation, so its hash never goes stale. A `list` is mutable, so Python
refuses to hash it at all, which is exactly why it cannot be a set
member or a dictionary key.
