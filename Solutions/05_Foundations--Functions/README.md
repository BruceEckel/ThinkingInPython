# Functions: Solutions

## 1. A third call to `bad_append()`, and why a tuple default doesn't fix it

> In `mutable_default.py`,
> call `bad_append(3)` a third time and predict the result before checking it.
> Then change `bad_append()`'s default from `[]` to `()` and explain why that change alone does not fix `bad_append()`
> (hint: `target.append(item)` on a tuple).

<details>
<summary>Where to look</summary>

[The Mutable Default Trap](../../Chapters/05_Foundations--Functions.md#the-mutable-default-trap) shows that Python builds a default once, when the `def` runs.
Predict the third call from that, then see what `()` changes for the one method the function needs.
[Safe Defaults](../../Chapters/05_Foundations--Functions.md#safe-defaults) shows the pattern that suits a function that mutates its parameter.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from exceptions import expect

def bad_append(item, target=[]):
    ...

def tuple_append(item, target=()):
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_1.py
from exceptions import expect

def bad_append(item, target=[]):
    target.append(item)
    return target

print(bad_append(1))
#: [1]
print(bad_append(2))
#: [1, 2]
print(bad_append(3))
#: [1, 2, 3]

def tuple_append(item, target=()):
    target.append(item)  # type: ignore
    return target

expect(AttributeError, tuple_append, 1)
#: [AttributeError] 'tuple' object has no attribute 'append'
```

**Accumulate in the shared default.** Each call keeps appending to the same list. Python creates the
default once, when it defines the function, and every call that
omits `target` reuses that same object.

**Try an immutable default.** Changing the default to `()` trades one failure for another. The
function's job is to append, and a tuple has no `append()`, so the
first call that omits `target` raises an `AttributeError`.
`tuple_append()` is `bad_append()` with that one change.

An immutable default suits a parameter the function reads, as in
`immutable_default.py`. A function that mutates the parameter needs
the `None` sentinel. `good_append()` tests for `None` and builds a new
list inside the function body on every call.

</details>
</details>
</details>

## 2. A `get()` that re-raises, and why `None` cannot be its sentinel

> In `sentinel_default.py`, replace `return MISSING` with a bare `raise`,
> so a missing key with no default re-raises the `KeyError`.
> Confirm that `get(prefs, "theme")` raises a `KeyError` and that `get(prefs, "theme", None)` returns `None`.
> Explain why `default=None` could not serve as the sentinel in this function.

<details>
<summary>Where to look</summary>

[Sentinel Values](../../Chapters/05_Foundations--Functions.md#sentinel-values) builds a default that no caller can pass as data.
Test the parameter with `is` against that object, and use a bare `raise` inside the `except` block.
Consider what `get(prefs, "theme", None)` would look like to the function if `None` were the sentinel.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from exceptions import expect

MISSING = sentinel("MISSING")

def get(data, key, default=MISSING):
    ...
```

<details>
<summary>Solution</summary>

If you make `None` the sentinel, writing `default=None` and testing `default is None`,
then `get(prefs, "theme", None)` raises a `KeyError` instead of returning `None`.
A caller who asks for `None` as the default cannot get it.
The solution tests against `MISSING` instead,
so `None` stays available as an ordinary default.

```python
# exercise_2.py
from exceptions import expect

MISSING = sentinel("MISSING")

def get(data, key, default=MISSING):
    try:
        return data[key]
    except KeyError:
        if default is MISSING:
            raise
        return default

prefs = {"volume": 3, "mute": None}
expect(KeyError, get, prefs, "theme")
#: [KeyError] 'theme'
print(get(prefs, "theme", None))
#: None
```

**Tell an omitted default from `None`.** The two calls ask for different things. The first supplies no
default, so a missing key is an error. The second supplies `None` as
the default, so a missing key produces `None`. With `default=None` as
the sentinel, `get()` receives the same `None` in both calls and
cannot tell them apart. It must raise an exception for both or return
`None` for both. `MISSING` is an object no caller passes as data, so
`default is MISSING` is true only when the caller supplied no default.
The built-in `getattr()` draws the same line. `getattr(obj, "x")`
raises an `AttributeError` when `obj` has no `x`, and
`getattr(obj, "x", None)` returns `None`.

</details>
</details>
</details>

## 3. A keyword-only `label` parameter

> In `param_markers.py`, add a parameter `label="result"` to `divide()`,
> keyword-only, so `print(divide(10, 2, label="half"))` shows `half: 5.0`.
> Confirm that `divide(10, 2, "half")`, passing `label` positionally,
> is now a `TypeError`.

<details>
<summary>Where to look</summary>

[Positional-Only and Keyword-Only Parameters](../../Chapters/05_Foundations--Functions.md#positional-only-and-keyword-only-parameters) explains the `/` and `*` markers.
Place the new parameter after the `*`, and keep the `/` where it is.
The `TypeError` comes from the call having one more positional argument than the signature accepts.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from exceptions import expect

def divide(a, b, /, *, label="result"):
    ...
```

<details>
<summary>Solution</summary>

If you add `label` after the `/` without a `*`, as `def divide(a, b, /, label="result")`,
`label` is positional-or-keyword,
and `divide(10, 2, "half")` returns `half: 5.0` instead of raising a `TypeError`.
The solution adds the `*` so that `label` can arrive by name alone.

```python
# exercise_3.py
from exceptions import expect

def divide(a, b, /, *, label="result"):
    return f"{label}: {a / b}"

print(divide(10, 2, label="half"))
#: half: 5.0

expect(TypeError, divide, 10, 2, "half")  # type: ignore
#: [TypeError] divide() takes 2 positional arguments but 3
#: were given
```

`a` and `b` stay positional-only (from the original `/`), and the new
`*` marks everything after it, here `label` alone, as keyword-only.
Calling `divide(10, 2, "half")` passes three positional arguments to
a function that accepts two, so Python raises a `TypeError` before
the function body runs.

</details>
</details>
</details>

## 4. `report()` with an optional total

> Rewrite `report()` from `var_args.py` so it accepts a `total=False` keyword-only flag that,
> when true, also prints `sum(values)`.
> Confirm `report("nums", 1, 2, 3, total=True)` prints the sum.

<details>
<summary>Where to look</summary>

[Variable Argument Lists](../../Chapters/05_Foundations--Functions.md#variable-argument-lists) shows `report()`, and [Positional-Only and Keyword-Only Parameters](../../Chapters/05_Foundations--Functions.md#positional-only-and-keyword-only-parameters) shows how a parameter becomes keyword-only.
Any parameter that follows `*values` is keyword-only.
Put `total` there, ahead of `**options`, and test it in the body.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
def report(label, *values, total=False, **options):
    ...
```

<details>
<summary>Solution</summary>

If you put `total` ahead of `*values`, as in
`def report(label, total=False, *values, **options)`, the call
`report("nums", 1, 2, 3, total=True)` raises a `TypeError`:
`report() got multiple values for argument 'total'`. In that
position `total` is an ordinary positional parameter, so the `1`
fills it before `total=True` arrives as a second value. The solution
places `total` after `*values`, where no positional argument can
reach it, so the keyword is the one way to set it.

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
so it is keyword-only. Callers must write `total=True`, and neither
`values` nor `options` can swallow it by accident. Adding the flag
needs no change to how `report()` collects its positional and
keyword arguments.

</details>
</details>
</details>

## 5. `apply_twice()` with a lambda

> Write `apply_twice(func, value)` that returns `func(func(value))`,
> then call it with a lambda that appends `"!"` to a string.
> Predict the result of `apply_twice(lambda s: s + "!", "hi")` before running it.

<details>
<summary>Where to look</summary>

[Lambdas](../../Chapters/05_Foundations--Functions.md#lambdas) shows a lambda passed as an argument, as the `key` of `sorted()`.
`apply_twice()` is a function with a callable parameter, and it calls that parameter on its own result.
Trace the string through the lambda twice before running the call.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
def apply_twice(func, value):
    ...
```

<details>
<summary>Solution</summary>

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
second call shows the same shape with numbers. `3` squares to `9`,
which squares to `81`, not `9`.

A function that takes another function as an argument needs nothing
special to say so. `func` is a parameter like any other, and it need
only be callable with one argument.

</details>
</details>
</details>

## 6. Unpacking both containers at a call site

> Given `args = ("point", 3, 4)` and `opts = {"color": "red"}`,
> call `report()` from `var_args.py` so it prints `point (3, 4) {'color': 'red'}`,
> passing both containers without naming their contents.

<details>
<summary>Where to look</summary>

[Unpacking Arguments](../../Chapters/05_Foundations--Functions.md#unpacking-arguments) shows `*` spreading a sequence and `**` spreading a dictionary at a call site.
Pass each container with its own star, and let the position of each element decide which parameter receives it.
The first element of the tuple fills `label`, and the rest collect into `values`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
def report(label, *values, **options):
    ...
```

<details>
<summary>Solution</summary>

If you pass `opts` without its `**`, as `report(*args, opts)`,
the call prints `point (3, 4, {'color': 'red'}) {}`.
The dictionary arrives as one more positional argument,
so `values` collects it and `options` stays empty.
The solution spreads `opts` with `**`,
which turns each key into a keyword argument for `**options` to collect.

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
three positional arguments, so `"point"` fills `label` and the
remaining two collect into `values`. `**opts` spreads the dictionary
into keyword arguments, which `**options` collects again. The first
element of `args` is not special to the caller. It becomes `label`
only because of where it sits in the sequence.

</details>
</details>
</details>

## 7. `describe(name, /, **facts)`

> Write `describe(name, /, **facts)` that prints `name` followed by each keyword argument as `key=value`,
> one per line.
> Confirm that `describe(name="Bob")` is a `TypeError`,
> and explain which marker caused it.

<details>
<summary>Where to look</summary>

[Positional-Only and Keyword-Only Parameters](../../Chapters/05_Foundations--Functions.md#positional-only-and-keyword-only-parameters) explains the `/` marker, and [Variable Argument Lists](../../Chapters/05_Foundations--Functions.md#variable-argument-lists) explains `**facts`.
Follow the keyword `name="Bob"` through the signature.
Ask which parameter may receive it, and which one gets no value.
The error message names the missing parameter, so read it closely.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from exceptions import expect

def describe(name, /, **facts):
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_7.py
from exceptions import expect

def describe(name, /, **facts):
    print(name)
    for key, value in facts.items():
        print(f"{key}={value}")

describe("Bob", role="editor", years=12)
#: Bob
#: role=editor
#: years=12
expect(TypeError, describe, name="Bob")  # type: ignore
#: [TypeError] describe() missing 1 required positional
#: argument: 'name'
```

**Reject a keyword for `name`.** The `/` causes the `TypeError`. `name` is positional-only, so
`name="Bob"` cannot reach it. `**facts` accepts any keyword the
parameters do not claim, and after the `/` no parameter claims `name`.
So `"Bob"` goes into `facts`, and the positional `name` stays unfilled.
The message is therefore
`describe() missing 1 required positional argument: 'name'`,
which points at the parameter the caller thought they were filling.

**Mark the deliberate mistake.** The mistake is visible without
running the code, so the call carries a `# type: ignore` telling the
type checker the misuse is deliberate, the same way `param_markers.py`
marks its two bad calls.

Without `**facts`, Python reports the mismatch:
`describe() got some positional-only arguments passed as keyword
arguments: 'name'`, the same error `divide(a=10, b=2)` raises in
`param_markers.py`. Catch-all keywords hide that message, because
the stray name now has somewhere to go. Without the `/`,
`describe(name="Bob")` succeeds and `facts` stays empty.

`**facts` is the opposite direction from exercise 6. There, `**opts`
at the call site spreads a dictionary into separate keyword arguments.
Here, `**facts` in the parameter list collects separate keyword
arguments back into a dictionary. The two forms use the same `**` and
are inverses of each other, and that inversion is why a function
declaring `**kwargs` can forward them to another call as `**kwargs`
unchanged.

The `/` and `**facts` are also worth using together. `/` hides the
parameter name `name` from callers, so a later rename breaks no
caller, while `**facts` accepts any name a caller writes. The `/`
also frees the word `name` for the caller's use.
`describe("Bob", name="Robert")` stores a fact called `name`, where
without the `/` the same call fails with two values for `name`.

</details>
</details>
</details>

## 8. `UnboundLocalError` from both directions

> In `function_scope.py`,
> delete the `global count` line from `writes_global()` and predict what a call raises before running it.
> Then restore it, and instead add `print(count)` as the first line of `rebinds()`.
> Explain why that also raises an `UnboundLocalError`,
> although the assignment to `count` comes after the `print`.

<details>
<summary>Where to look</summary>

[Names Inside a Function](../../Chapters/05_Foundations--Functions.md#names-inside-a-function) explains how Python decides whether a name is local or global.
Python makes that decision for the whole function body when it compiles the function, not line by line as the code runs.
Apply it to `count += 1` in the first case and to the later `count = 99` in the second.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
from exceptions import expect

def writes_global():
    ...

def rebinds():
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_8.py
from exceptions import expect

count = 0

def writes_global():
    count += 1  # type: ignore  # noqa: F823, F841

def rebinds():
    print(count)  # type: ignore  # noqa: F823
    count = 99
    print(count)

expect(UnboundLocalError, writes_global)
#: [UnboundLocalError] cannot access local variable 'count'
#: where it is not associated with a value
expect(UnboundLocalError, rebinds)
#: [UnboundLocalError] cannot access local variable 'count'
#: where it is not associated with a value
```

**Drop the `global` declaration.** Both calls raise `UnboundLocalError: cannot access local variable
'count' where it is not associated with a value`,
which the listing prints in full. Without `global`,
the assignment in `count += 1` makes `count` local to
`writes_global()`, so the read half of `+=` looks for a local that
has no value yet.

**Assign after the read.** `rebinds()` fails for the same reason
although its `print` comes first in time. Python decides which names
are local when it compiles the function body, so the `count = 99`
below the `print` makes `count` local throughout. The first `print`
therefore reads the unassigned local, not the module-level name,
and the second `print` does not run.

**Mark the deliberate mistakes.** Both mistakes
are visible without running the code. The type checker and the linter
each flag them, so the offending lines carry `# type: ignore` and
`# noqa` markers saying the misuse is deliberate, the way
`param_markers.py` marks its two bad calls.

</details>
</details>
</details>

## 9. Rebinding a parameter against mutating it

> Write `clear_by_assignment(target)`, which assigns `target = []`,
> and `clear_by_method(target)`, which calls `target.clear()`.
> Pass the same list to each,
> and predict which call empties the caller's list before running them.

<details>
<summary>Where to look</summary>

[The Mutable Default Trap](../../Chapters/05_Foundations--Functions.md#the-mutable-default-trap) shows `rebind()` and `append_all()` in `mutating_arguments.py`.
A parameter is a second name for the caller's object, so assigning to it moves only the local name.
Calling a method on it changes the one object that both names share.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_9.py
def clear_by_assignment(target):
    ...

def clear_by_method(target):
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_9.py
def clear_by_assignment(target):
    target = []  # Rebinds the local name
    print(target)

def clear_by_method(target):
    target.clear()  # Changes the caller's list

mine = [1, 2, 3]
clear_by_assignment(mine)
#: []
print(mine)
#: [1, 2, 3]
clear_by_method(mine)
print(mine)
#: []
```

Only `clear_by_method()` empties the caller's list. When a call
begins, `target` and `mine` are two names for one list.

**Rebind the local name.** The assignment in `clear_by_assignment()` binds `target` to a new empty
list, which the function prints, and `mine` still names the original.

**Change the shared list.** `target.clear()` rebinds nothing. It calls a method on the one list
both names share, so the caller sees the list empty.

`clear_by_assignment()` and `clear_by_method()` are `rebind()` and
`append_all()` from `mutating_arguments.py` with the same operation,
emptying a list, written both ways.

</details>
</details>
</details>
