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
when the key is genuinely absent. Here it never comes into play,
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
    print(e)
#: divide() takes 2 positional arguments but 3 were given
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

## 5. `apply_twice()` with a lambda

```python
# exercise_5.py
def apply_twice(func, value):
    return func(func(value))

print(apply_twice(lambda s: s + "!", "hi"))
#: hi!!
print(apply_twice(lambda n: n * n, 3))
#: 81
```

The lambda runs twice, on the original value and then on its own
result, so `"hi"` gains two exclamation points rather than one. The
second call shows the same shape with numbers: `3` squares to `9`,
which squares to `81`, not `9`. A function that takes another function
as an argument needs nothing special to say so. `func` is a parameter
like any other, and the only requirement is that it be callable with
one argument.

## 6. Unpacking both containers at a call site

```python
# exercise_6.py
def report(label, *values, **options):
    print(label, values, options)

args = ("point", 3, 4)
opts = {"color": "red"}
report(*args, **opts)
#: point (3, 4) {'color': 'red'}
```

One `*` and one `**` do the whole job. `*args` spreads the tuple into
three positional arguments, so `"point"` lands on `label` and the
remaining two collect into `values`. `**opts` spreads the dictionary
into keyword arguments, which `**options` collects again. The first
element of `args` is not special to the caller: it becomes `label`
only because of where it sits in the sequence.

## 7. `describe(name, /, **facts)`

```python
# exercise_7.py

def describe(name, /, **facts):
    print(name)
    for key, value in facts.items():
        print(f"{key}={value}")

describe("Bob", role="editor", years=12)
#: Bob
#: role=editor
#: years=12
try:
    describe(name="Bob")  # type: ignore
except TypeError as e:
    print(e)
#: describe() missing 1 required positional argument: 'name'
```

The `/` caused it. `name` is positional-only, so `name="Bob"` cannot
reach it. Where the argument goes instead is the part worth tracing:
`**facts` accepts any keyword the parameters do not claim, and after
the `/` the name `name` is not one of them, so `"Bob"` lands in
`facts` and the positional `name` is left unfilled. The message is
therefore `describe() missing 1 required positional argument: 'name'`,
which points at the parameter the caller thought they were filling.
The mistake is visible without running the code, so the call carries a
`# type: ignore` telling the type checker it is deliberate, the same way
`param_markers.py` marks its two.

Take the `**facts` away and the same call reports the mismatch
directly: `divide(a=1, b=2)` against `def divide(a, b, /)` gives
`got some positional-only arguments passed as keyword arguments:
'a, b'`. Catch-all keywords hide that message, because there is now
somewhere for the stray name to go. Without the `/`, the call
succeeds and `facts` stays empty.

`**facts` is the opposite direction from exercise 6. There, a
dictionary at the call site was spread into separate keyword
arguments. Here, separate keyword arguments are collected back into a
dictionary inside the function. The two forms use the same `**` and
are inverses of each other, which is why a function declaring
`**kwargs` can forward them to another call as `**kwargs` unchanged.

The pair is also why the two markers are worth using together. `/`
fixes what `name` is called, so a later rename breaks no caller, while
`**facts` accepts names the function has never heard of. One parameter
is closed to the caller's vocabulary and the rest is open to it.

## 8. `UnboundLocalError` from both directions

```python
# exercise_8.py
count = 0

def writes_global():
    count += 1  # type: ignore  # noqa: F823, F841

def rebinds():
    print(count)  # type: ignore  # noqa: F823
    count = 99
    print(count)

try:
    writes_global()
except UnboundLocalError as e:
    print(str(e).partition(" where")[0])
#: cannot access local variable 'count'
try:
    rebinds()
except UnboundLocalError as e:
    print(str(e).partition(" where")[0])
#: cannot access local variable 'count'
```

Both calls raise `UnboundLocalError: cannot access local variable
'count' where it is not associated with a value`,
which the listing trims after the variable name. Without `global`,
the assignment in `count += 1` makes `count` local to
`writes_global()`, so the read half of `+=` looks for a local that
has no value yet. `rebinds()` fails for the same reason even though
its `print` comes first in time: Python decides which names are local
when it compiles the function body, and the `count = 99` below the
`print` already made `count` local throughout. The `print` therefore
reads the unassigned local, never the module-level name. The second
`print`, after the assignment, is never reached. Both mistakes are
visible without running the code. The type checker and the linter
each flag them, so the offending lines carry `# type: ignore` and
`# noqa` markers saying the misuse is deliberate, the way
`param_markers.py` marks its two.
