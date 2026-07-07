# Functions: Solutions

## 1. A third call to `bad_append()`, and why a tuple default doesn't fix it

```python
# exercise_1.py
def bad_append(item, target=[]):
    target.append(item)
    return target

print(bad_append(1))
#: [1]
print(bad_append(2))
#: [1, 2]
print(bad_append(3))
#: [1, 2, 3]
```

Each call keeps appending to the same list, since the default is
created once, at function-definition time, and every call that omits
`target` reuses that same object.

Changing the default to `()` does not fix anything, because the bug
is not really about mutability by itself. It is about calling a
method that mutates the default *in place*. A tuple has no
`append()`, so `target.append(item)` immediately raises
`AttributeError: 'tuple' object has no attribute 'append'`. The real
fix, shown in `good_append()`, is the `None` sentinel: check for
`None` and build a fresh, genuinely mutable container inside the
function body on every call.

## 2. A stored `None` next to a missing key

```python
# exercise_2.py
MISSING = sentinel("MISSING")

def get(data, key, default=MISSING):
    if key in data:
        return data[key]
    if default is MISSING:
        raise KeyError(key)
    return default

prefs = {"volume": 3, "mute": None, "volume2": None}
print(get(prefs, "volume2"))
#: None
```

`volume2` is a real key whose stored value happens to be `None`. The
`in` check finds it, so `get()` returns the stored `None` directly,
without ever consulting `default`. The `MISSING` sentinel only matters
when the key is genuinely absent; here it never comes into play,
which is the point: a present `None` and an absent key are
different situations, and the sentinel exists to tell them apart.

## 3. A keyword-only `label` parameter

```python
# exercise_3.py
def divide(a, b, /, *, label="result"):
    return f"{label}: {a / b}"

print(divide(10, 2, label="half"))
#: half: 5.0

try:
    divide(10, 2, "half")  # type: ignore
except TypeError as e:
    print("TypeError:", e)
#: TypeError: divide() takes 2 positional arguments but 3 were given
```

`a` and `b` stay positional-only (from the original `/`), and the new
`*` marks everything after it, here just `label`, as keyword-only.
Calling `divide(10, 2, "half")` tries to pass three positional
arguments to a function that only accepts two positionally, so Python
raises `TypeError` before the function body ever runs.

## 4. `report()` with an optional running total

```python
# exercise_4.py
def report(label, *values, total=False, **options):
    print(label, values, options)
    if total:
        print(sum(values))

report("nums", 1, 2, 3, total=True)
#: nums (1, 2, 3) {}
#: 6
```

`total` sits between `*values` and `**options` in the parameter list,
which makes it keyword-only: callers must write `total=True`, and it
can never be swallowed into `values` or `options` by accident. Adding
the flag needed no change to how `report()` already collected its
positional and keyword arguments.
