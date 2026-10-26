# Functions: Solutions

## 1. A third call to `bad_append()`, and why a tuple default doesn't fix it

> In `mutable_default.py`,
> call `bad_append(3)` a third time and predict the result before checking it.
> Then change `bad_append()`'s default from `[]` to `()` and explain why that change alone does not fix `bad_append()`
> (hint: `target.append(item)` on a tuple).

<details>
<summary>Where to look</summary>

[The Mutable Default Trap](../../Chapters/05_Foundations--Functions.md#the-mutable-default-trap)
shows that Python builds a default once, when the `def` runs.
Predict the third call from that,
then see what `()` changes for the one method the function needs.
[Safe Defaults](../../Chapters/05_Foundations--Functions.md#safe-defaults)
shows the pattern that suits a function that mutates its parameter.

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
<summary>Done when</summary>

the third `bad_append(3)` prints `[1, 2, 3]`,
matching the prediction you wrote down first.
With the default changed to `()`,
a call that omits `target` raises an `AttributeError`:
`'tuple' object has no attribute 'append'`.
You can also say why a function that mutates its parameter needs the `None` sentinel from `good_append()`.

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

**Accumulate in the shared default.**
Each call keeps appending to the same list.
Python creates the default once, when it defines the function.
Every call that omits `target` reuses that object.

**Try an immutable default.**
`tuple_append()` is `bad_append()` with its default changed to `()`.
That change removes the shared list and causes a different failure.
A tuple has no `append()`,
so the first call that omits `target` raises an `AttributeError`.

An immutable default suits a parameter the function reads,
as in `immutable_default.py`.
A function that mutates the parameter needs the `None` sentinel.
`good_append()` tests for `None` and builds a new list inside the function body on every call that omits `target`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. A `get()` that re-raises, and why `None` cannot be its sentinel

> In `sentinel_default.py`, replace `return MISSING` with a bare `raise`,
> so a missing key with no default re-raises `KeyError`.
> Confirm that `get(prefs, "theme")` raises a `KeyError` and that `get(prefs, "theme", None)` returns `None`.
> Explain why `default=None` could not serve as the sentinel in this function.

<details>
<summary>Where to look</summary>

[Sentinel Values](../../Chapters/05_Foundations--Functions.md#sentinel-values)
builds a default that no caller can pass as data.
Test the parameter with `is` against that object,
and use a bare `raise` inside the `except` block.
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
<summary>Done when</summary>

`get(prefs, "theme")` raises a `KeyError` for `'theme'` and `get(prefs, "theme", None)` prints `None`.
You can also say what `get()` receives as `default` in each of those two calls if `default=None` were the sentinel,
and why that makes the two calls indistinguishable.

<details>
<summary>Solution</summary>

If you make `None` the sentinel,
writing `default=None` and testing `default is None`,
then `get(prefs, "theme", None)` raises a `KeyError` instead of returning `None`.
A caller who asks for `None` as the default cannot get it.
The solution tests against `MISSING`,
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

**Tell an omitted default from `None`.**
The two calls ask for different things.
With `default=None` as the sentinel,
`get()` receives the same `None` in both calls,
so the two calls look identical to it.
`get()` must raise an exception for both or return `None` for both.
`MISSING` is a marker object reserved for the omitted argument,
so `default is MISSING` identifies the call that omits `default`.

The built-in `getattr()` makes the same distinction.
`getattr(obj, "x")` raises an `AttributeError` when `obj` has no `x`,
and `getattr(obj, "x", None)` returns `None`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[Positional-Only and Keyword-Only Parameters](../../Chapters/05_Foundations--Functions.md#positional-only-and-keyword-only-parameters)
explains the `/` and `*` markers.
Place the new parameter after the `*`, and keep the `/` where it is.
The `TypeError` comes from the extra positional argument.
The call passes one more than the signature accepts.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from exceptions import expect

def divide(a, b, /, *, label="result"):
    ...
```

<details>
<summary>Done when</summary>

`print(divide(10, 2, label="half"))` prints `half: 5.0`,
and `divide(10, 2, "half")` raises a `TypeError`:
`divide() takes 2 positional arguments but 3 were given`.
If that second call returns `half: 5.0` instead,
`label` is still positional-or-keyword.

<details>
<summary>Solution</summary>

If you add `label` after the `/` without a `*`,
as `def divide(a, b, /, label="result")`, `label` is positional-or-keyword.
Then `divide(10, 2, "half")` returns `half: 5.0` instead of raising a `TypeError`.
The solution adds the `*`, so a caller must pass `label` by name.

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

Calling `divide(10, 2, "half")` passes three positional arguments to a function that accepts two,
so Python raises a `TypeError` before the function body runs.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. `report()` with an optional total

> Rewrite `report()` from `var_args.py` so it accepts a `total=False` keyword-only flag that,
> when true, also prints `sum(values)`.
> Confirm `report("nums", 1, 2, 3, total=True)` prints the sum.

<details>
<summary>Where to look</summary>

[Variable Argument Lists](../../Chapters/05_Foundations--Functions.md#variable-argument-lists)
shows `report()`, and [Positional-Only and Keyword-Only Parameters](../../Chapters/05_Foundations--Functions.md#positional-only-and-keyword-only-parameters)
shows how a parameter becomes keyword-only.
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
<summary>Done when</summary>

`report("nums", 1, 2, 3, total=True)` prints `nums (1, 2, 3) {}` and then `6`,
so `total` appears in neither the tuple nor the dictionary.
A `TypeError` about multiple values for argument `'total'` means `total` sits in the wrong place in the parameter list.

<details>
<summary>Solution</summary>

If you put `total` ahead of `*values`,
as in `def report(label, total=False, *values, **options)`,
the call `report("nums", 1, 2, 3, total=True)` raises a `TypeError`:
`report() got multiple values for argument 'total'`.
In that position `total` is an ordinary positional parameter,
so the `1` fills it before `total=True` arrives as a second value.
The solution places `total` after `*values`.
`*values` collects every remaining positional argument,
so a keyword is the one way to set `total`.

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

With the flag added,
`report()` collects its positional and keyword arguments as before.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 5. `apply_twice()` with a lambda

> Write `apply_twice(func, value)` that returns `func(func(value))`,
> then call it with a lambda that appends `"!"` to a string.
> Predict the result of `apply_twice(lambda s: s + "!", "hi")` before running it.

<details>
<summary>Where to look</summary>

[Lambdas](../../Chapters/05_Foundations--Functions.md#lambdas)
shows a lambda passed as an argument, as the `key` of `sorted()`.
`apply_twice()` is a function with a callable parameter,
and it calls that parameter on its own result.
Trace the string through the lambda twice before running the call.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
def apply_twice(func, value):
    ...
```

<details>
<summary>Done when</summary>

`apply_twice(lambda s: s + "!", "hi")` returns `hi!!`,
matching the prediction you wrote down before running it,
and the same `apply_twice()` called with a squaring lambda on `3` returns `81`.

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

A function that takes another function as an argument declares that parameter like any other.
`func` has two requirements: it must be callable with one argument,
and it must accept the value it returns,
since `apply_twice()` passes that value back in.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. Unpacking both containers at a call site

> Given `args = ("point", 3, 4)` and `opts = {"color": "red"}`,
> call `report()` from `var_args.py` so it prints `point (3, 4) {'color': 'red'}`,
> passing both containers without naming their contents.

<details>
<summary>Where to look</summary>

[Unpacking Arguments](../../Chapters/05_Foundations--Functions.md#unpacking-arguments)
shows `*` spreading a sequence and `**` spreading a dictionary at a call site.
Pass each container with its own star.
Python assigns each element of the tuple to a parameter by its position.
The first element of the tuple fills `label`,
and the rest collect into `values`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
def report(label, *values, **options):
    ...
```

<details>
<summary>Done when</summary>

one call to `report()` prints `point (3, 4) {'color': 'red'}`,
and that call names `args` and `opts`, not `"point"`, `3`, `4`, or `"color"`.
If the output shows `(3, 4, {'color': 'red'}) {}`,
the dictionary arrived as one more positional argument.

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

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[Positional-Only and Keyword-Only Parameters](../../Chapters/05_Foundations--Functions.md#positional-only-and-keyword-only-parameters)
explains the `/` marker,
and [Variable Argument Lists](../../Chapters/05_Foundations--Functions.md#variable-argument-lists)
explains `**facts`.
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
<summary>Done when</summary>

`describe("Bob", role="editor", years=12)` prints `Bob`, `role=editor`,
and `years=12` on three lines,
and `describe(name="Bob")` raises a `TypeError` reading `describe() missing 1 required positional argument: 'name'`.
You can also say which parameter received the keyword `name="Bob"`.

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

**Reject a keyword for `name`.**
The `/` causes the `TypeError`.
`name` is positional-only, so it takes its value by position.
The keyword `name="Bob"` is therefore a leftover.
`**facts` collects leftover keywords,
so `facts` receives `name="Bob"` and the parameter `name` stays empty.
The message, `describe() missing 1 required positional argument: 'name'`,
names the parameter the caller thought they were filling.

**Mark the deliberate mistake.**
The type checker reports the mistake before the code runs.
The call therefore carries a `# type: ignore` saying the misuse is deliberate,
the same way `param_markers.py` marks its two bad calls.

Without `**facts`, Python reports the mismatch,
the same error `divide(a=10, b=2)` raises in `param_markers.py`:
`describe() got some positional-only arguments passed as keyword arguments: 'name'`.
`**facts` replaces that message with the missing-argument one.
Without the `/`, `describe(name="Bob")` succeeds and `facts` stays empty.

`**facts` works in the opposite direction from exercise 6.
There, `**opts` at the call site spreads a dictionary into separate keyword arguments.
Here, `**facts` in the parameter list collects separate keyword arguments back into a dictionary.
The two forms share the `**` and invert each other.
That inversion lets `trace()` in `unpacking_arguments.py` collect keywords in `**kwargs` and pass them on to `func` as `**kwargs`.

The `/` has two more effects on `describe()`.
Because callers pass `name` by position,
a later rename of the parameter leaves every caller working.
The `/` also lets `**facts` collect a keyword called `name`,
so `describe("Bob", name="Robert")` stores a fact called `name`.
Without the `/`, the same call fails with two values for `name`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 8. `UnboundLocalError` from both directions

> In `function_scope.py`,
> delete the `global count` line from `writes_global()` and predict what a call raises before running it.
> Then restore it, and instead add `print(count)` as the first line of `rebinds()`.
> Explain why a call to `rebinds()` also raises an `UnboundLocalError`,
> although the assignment to `count` comes after the `print`.

<details>
<summary>Where to look</summary>

[Names Inside a Function](../../Chapters/05_Foundations--Functions.md#names-inside-a-function)
explains how Python decides whether a name is local or global.
Python makes that decision for the whole function body when it compiles the function,
not line by line as the code runs.
Apply that decision to `count += 1` in the first case and to the later `count = 99` in the second.

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
<summary>Done when</summary>

each edit makes its call raise an `UnboundLocalError` reading `cannot access local variable 'count' where it is not associated with a value`,
and `rebinds()` raises it before printing anything.
You can name the line that makes `count` local in each function.

<details>
<summary>Solution</summary>

```python
# exercise_8.py
from exceptions import expect

count = 0

def writes_global():
    count += 1  # type: ignore  # noqa: F823, F841

def rebinds():
    print(count)  # type: ignore  # noqa: F823  # [1]
    count = 99
    print(count)  # [2]

expect(UnboundLocalError, writes_global)
#: [UnboundLocalError] cannot access local variable 'count'
#: where it is not associated with a value
expect(UnboundLocalError, rebinds)
#: [UnboundLocalError] cannot access local variable 'count'
#: where it is not associated with a value
```

**Drop the `global` declaration.**
Without `global`, the assignment in `count += 1` makes `count` local to `writes_global()`,
so the read half of `+=` reads that local before any assignment gives it a value.

**Assign after the read.**
`rebinds()` fails for the same reason,
although the `print()` at `[1]` runs before the assignment.
Python decides which names are local when it compiles the function body,
so the `count = 99` below that `print()` makes `count` local throughout.
The `print()` at `[1]` therefore reads the unassigned local,
not the module-level name.
The exception ends the call before the `print()` at `[2]`.

**Mark the deliberate mistakes.**
The type checker and the linter each flag both mistakes before the code runs.
The offending lines therefore carry `# type: ignore` and `# noqa` markers saying the misuse is deliberate,
the way `param_markers.py` marks its two bad calls.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[The Mutable Default Trap](../../Chapters/05_Foundations--Functions.md#the-mutable-default-trap)
shows `rebind()` and `append_all()` in `mutating_arguments.py`.
A parameter is a second name for the caller's object,
so assigning to it rebinds the local name and leaves the caller's object as it was.
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
<summary>Done when</summary>

printing your list after `clear_by_assignment()` shows its original contents,
printing it after `clear_by_method()` shows `[]`,
and both results match the prediction you wrote down before running them.

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

When a call begins, `target` and `mine` are two names for one list.

**Rebind the local name.**
The assignment in `clear_by_assignment()` binds `target` to a new empty list,
which the function prints.
`mine` still names the original.

**Change the shared list.**
`target.clear()` empties the one list both names share.
Because both names stay bound to that list,
`mine` names an empty list after the call.

`clear_by_assignment()` works like `rebind()` in `mutating_arguments.py`,
and `clear_by_method()` works like `append_all()`.
Here both functions attempt the same operation, emptying a list.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 10. A positional-only `func` in `trace()`

> Using `report()` and `trace()` from `unpacking_arguments.py`,
> predict what `trace(report, "point", func="f")` does, then run it.
> Add a `/` after `func` in `trace()`'s parameter list and run the call again.
> Explain where `func="f"` goes each time.

<details>
<summary>Where to look</summary>

[Positional-Only and Keyword-Only Parameters](../../Chapters/05_Foundations--Functions.md#positional-only-and-keyword-only-parameters)
explains what a `/` does to the names of the parameters before it.
Ask which parameter receives the keyword `func="f"` without the `/`,
and which one collects it with the `/`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_10.py
from exceptions import expect

def report(label, *values, **options):
    ...

def trace(func, *args, **kwargs):
    ...

def positional_trace(func, /, *args, **kwargs):
    ...
```

<details>
<summary>Done when</summary>

without the `/`, the call raises a `TypeError`,
`trace() got multiple values for argument 'func'`,
and `calling report` never prints.
With the `/`, it prints `calling report` and then `point () {'func': 'f'}`.
You can name the two parameters that collect `func="f"` on its way to that output.

<details>
<summary>Solution</summary>

If you predicted a `calling report` line before the error,
compare `forwarding_collision.py`.
There the clash is in the arguments `trace()` passes to `report()`,
so `trace()`'s body runs and prints `calling report` first.
Here the clash is in `trace()`'s own arguments,
so Python raises `TypeError` before `trace()`'s body runs.

```python
# exercise_10.py
from exceptions import expect

def report(label, *values, **options):
    print(label, values, options)

def trace(func, *args, **kwargs):
    print("calling", func.__name__)
    return func(*args, **kwargs)

expect(TypeError, trace, report, "point", func="f")  # type: ignore
#: [TypeError] trace() got multiple values for argument
#: 'func'

def positional_trace(func, /, *args, **kwargs):
    print("calling", func.__name__)
    return func(*args, **kwargs)

positional_trace(report, "point", func="f")
#: calling report
#: point () {'func': 'f'}
```

**Call the original `trace()`.**
`report` fills `func` by position,
and the keyword `func="f"` names the same parameter, so `func` gets two values.
The listing calls through `expect()` and marks the line with `# type: ignore`,
since the type checker reports the clash before the code runs.

**Make `func` positional-only.**
The listing names this version `positional_trace()` so that both versions run in one file.
After the `/`, a caller must fill `func` by position,
so the keyword `func="f"` is a leftover.
`**kwargs` collects it, `positional_trace()` forwards it,
and `report()`'s `**options` collects it again.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
