# Functions

> A piece of behavior needs a name so other code can call it without knowing how it works.
> A function is that name, with a parameter list that says what to pass.

The `def` keyword defines a function.
After `def` come the function name, the parameter list,
and a colon that begins the function body:

```python
# a_function.py

def a_function(response):
    val = 0
    if response == "yes":
        print("affirmative")
        val = 1
    print("continuing...")
    return val

print(a_function("no"))
#: continuing...
#: 0
print(a_function("yes"))
#: affirmative
#: continuing...
#: 1
```

`response` is a *parameter*, the name the function gives to what it receives.
The value a call passes, `"no"` or `"yes"`, is an *argument*.

A string literal that is the first statement under `def` becomes the function's *docstring*,
stored on `__doc__`:

```python
# documented_function.py

def greet(name):
    """Return a greeting for name."""
    return f"Hello, {name}!"

print(greet("Ann"))
#: Hello, Ann!
print(greet.__doc__)
#: Return a greeting for name.
```

A docstring documents the function for a reader or a tool,
not for the interpreter, which stores the text and otherwise ignores it.
[Metaprogramming](17_Techniques--Metaprogramming.md#the-core-functions)
reads it back with `inspect.getdoc()`.

The signatures so far give the function name and the parameter names,
with no [argument types or return types](08_Foundations--Static_Types.md#type-hints).
Python is dynamically typed,
so it reports a type error at runtime rather than at compile time:

```python
# add.py
from exceptions import expect

def add(arg1, arg2):
    return arg1 + arg2

print(add(42, 47))
#: 89
print(add("spam ", "eggs"))
#: spam eggs
expect(TypeError, add, 42, "spam")
#: [TypeError] unsupported operand type(s) for +: 'int' and
#: 'str'
```

A call succeeds as long as each operation in the function body accepts the arguments it receives.
The call binds each argument to its parameter and accepts any type,
so the failure comes from `+` inside the function body.

[`expect()`](15_Techniques--Context_Managers.md#the-expect-function)
is a helper that many of this book's listings import.
It calls its second argument, passing along the arguments that follow,
and prints the exception that call raises.

A function can also return a different type from one call to the next:

```python
# flexible_args_and_returns.py

def flexible_args_and_returns(arg):
    if arg == 1:
        return "Hello"
    if arg == "one":
        return 2

print(flexible_args_and_returns(1))
#: Hello
print(flexible_args_and_returns("one"))
#: 2
print(flexible_args_and_returns(2))
#: None
```

Every Python function returns a value.
A function that finishes without a `return` returns `None`,
and so does a bare `return`.

A `return` with several expressions produces a tuple,
which the caller usually unpacks:

    def minmax(values):
        return min(values), max(values)

    low, high = minmax([3, 1, 4])

The commas build the tuple, so the function returns one object.
`min_max()` in [Containers](03_Foundations--Containers.md#tuples-and-unpacking)
returns its pair the same way.

## Default Parameter Values

Parameters can have default values.
Keyword arguments let callers pass arguments by name, in any order.
A call that names its arguments documents itself:

```python
# default_args.py

def connect(host, port=5432, timeout=30):
    return f"{host}:{port} (timeout {timeout}s)"

print(connect("db.example.com"))  # Uses both defaults
#: db.example.com:5432 (timeout 30s)
# Skip to a keyword
print(connect("db.example.com", timeout=5))
#: db.example.com:5432 (timeout 5s)
# Any order by name
print(connect(port=80, host="web.example.com"))
#: web.example.com:80 (timeout 30s)
```

A caller can pass any parameter by name,
including a required one such as `host`, which the last call names.

At the call site, write every keyword argument after the positional ones.
`connect(port=80, "web.example.com")` is a `SyntaxError`:
`positional argument follows keyword argument`.
The grammar makes one exception.
A `*` unpacking, which [Unpacking Arguments](#unpacking-arguments) introduces,
can follow a keyword argument, as in `f(x=1, *rest)`.
Its values still bind first, as positional arguments,
so writing every keyword argument last keeps the call in the order Python binds it.

Every required parameter must come before the first parameter with a default.
`def f(a=1, b):` is a `SyntaxError`:
`parameter without a default follows parameter with a default`.
[Keyword-only parameters](#positional-only-and-keyword-only-parameters)
are exempt.
`def f(*, a=1, b):` is legal, because the caller names `b`.

### The Mutable Default Trap

Python evaluates a default value once, when it executes the `def`,
so every call shares that one object.
A mutable default therefore keeps the changes one call makes,
and the next call sees them:

```python
# mutable_default.py

def bad_append(item, target=[]):  # The same list every call
    target.append(item)
    return target

print(bad_append(1))
#: [1]
print(bad_append(2))  # Surprise, the default kept the 1
#: [1, 2]
print(bad_append.__defaults__)
#: ([1, 2],)

def good_append(item, target=None):
    if target is None:
        target = []  # A fresh list each call
    target.append(item)
    return target

print(good_append(1))
#: [1]
print(good_append(2))
#: [2]
```

The function object keeps its default values in the tuple `__defaults__`.
Both `bad_append()` calls append to the same list inside that tuple.
The default looks like an expression each call evaluates,
but Python evaluates it once, at the `def`.

The trap follows from how Python passes arguments.
A parameter is another name bound to the caller's object,
the binding that [Variables and References](02_Foundations--Tour.md#variables-and-references)
describes.
Every `bad_append()` call that uses the default binds `target` to the one list Python builds at the `def`,
so each call mutates the list the next call uses.

A caller that passes a mutable object sees the changes the function makes:

```python
# mutating_arguments.py

def append_all(target, extras):
    target.extend(extras)

mine = [1, 2]
append_all(mine, [3, 4])
print(mine)  # The caller's list changed
#: [1, 2, 3, 4]

def rebind(target):
    target = ["replaced"]  # Rebinds the local name only
    print(target)

rebind(mine)
#: ['replaced']
print(mine)
#: [1, 2, 3, 4]
```

`append_all()` calls a method on the object the caller passed,
so the caller sees the change.
`rebind()` assigns to the parameter,
so the local name points at a new list and the caller's list stays as it was.

### Safe Defaults

`good_append()` builds a fresh list on every call that uses the default.
Any function that mutates a parameter with a default must do the same.
If the function reads the parameter and leaves it as it was,
use an immutable default such as an empty tuple.
Every call shares that tuple,
and the sharing is safe because a tuple is immutable:

```python
# immutable_default.py

def show(items=()):
    for item in items:
        print(item)
    print(f"({len(items)} items)")

show()
#: (0 items)
show(["a", "b"])
#: a
#: b
#: (2 items)
```

With [type hints](08_Foundations--Static_Types.md#type-hints),
such a parameter reads:

    items: Sequence[str] = ()

## Sentinel Values

The `None` default in `good_append()` is a *sentinel*:
a value chosen to mean "the caller passed nothing" rather than to serve as data.
Test the parameter with `is None` rather than truthiness.
`if not target:` also discards an empty list the caller passed on purpose.

`None` works there because every real `target` is a list.
When `None` is a valid argument, you need a distinct sentinel.
Python 3.15 ([PEP 661](https://peps.python.org/pep-0661/))
adds a `sentinel` built-in that creates a unique value that prints as the name you give it:

```python
# sentinel_default.py

MISSING = sentinel("MISSING")

def get(data, key, default=MISSING):
    try:
        return data[key]
    except KeyError:
        if default is MISSING:
            return MISSING  # Normally re-raises here
        return default

prefs = {"volume": 3, "mute": None}
print(get(prefs, "volume"))
#: 3
print(get(prefs, "mute"))  # None is a real stored value
#: None
print(get(prefs, "theme"))
#: MISSING
print(get(prefs, "theme", "dark"))
#: dark
```

`prefs` stores `mute` as `None`,
so a `None` from `get()` cannot also mean "no such key."
With the `MISSING` sentinel, `get()` tells the two cases apart.
Because `get()` tests `default` against `MISSING`,
a caller can also pass `None` as a real default.

Create a sentinel once and share that name.
Two `sentinel()` calls with the same name build two different objects,
so `default is sentinel("MISSING")` compares against a second object and is always false.

Code written before 3.15 builds its sentinel as `MISSING = object()`.
A bare `object()` is unique, so `is` tells it apart from every other value.
It prints as `<object object at 0x...>`, though,
where a `sentinel()` value prints its name.

## Names Inside a Function

A function can read a module-level name,
but assigning to that name anywhere in the function makes it local for the whole function.
Python decides which names are local when it compiles the function body,
so an assignment on the last line of the body has the same effect as one on the first.
`global` tells Python to rebind the module-level name:

```python
# function_scope.py

count = 0

def read_only():
    print(count)

def reads_later():
    print(limit)

def rebinds():
    # A local, unrelated to the module-level count
    count = 99
    print(count)

def writes_global():
    global count
    count += 1

limit = 10
read_only()
#: 0
reads_later()
#: 10
rebinds()
#: 99
print(count)
#: 0
writes_global()
print(count)
#: 1
```

`+=` is an assignment too.
If you drop the `global` from `writes_global()`,
the compiler marks `count` local for the whole function.
The read half of `count += 1` then looks up a local that has no value yet.
A call to `writes_global()` raises an `UnboundLocalError`.
`global` governs rebinding, not reading, so `read_only()` needs no declaration.

`reads_later()` names `limit`, which the module binds after the `def`.
Python looks up a module-level name each time the body reads it,
not when `def` runs.
The module binds `limit` before it calls `reads_later()`,
so the lookup succeeds.

Each call to a function gets its own *execution frame*,
the object Python creates to hold that call's local variables and its position in the body.
While the call runs, the frame is an entry on the call stack,
the call's *stack frame*, and Python discards it when the function returns,
so the local `count` in `rebinds()` exists only during a call to `rebinds()`.
A generator's frame outlives a `yield`,
and [Generators](45_Effects--Generators.md#half-a-coroutine-by-design)
shows what that makes possible.

[Closures](40_Functional--Foundations.md#closures) covers `nonlocal`,
which rebinds a name in an enclosing function the way `global` rebinds a module-level name.

A function that rebinds a global couples every caller to that shared,
mutable state.
As [Pure Functions](40_Functional--Foundations.md#pure-functions) shows,
to understand one call you must trace every call before it.
[Effect Management](44_Effects--Effect_Management.md#what-is-an-effect)
classifies rebinding a global as a side effect and reading one as a side cause.

## Variable Argument Lists

A `*args` parameter collects extra positional arguments into a tuple,
and `**kwargs` collects extra keyword arguments into a dictionary:

```python
# var_args.py

def report(label, *values, **options):
    print(label, values, options)

report("nums", 1, 2, 3)
#: nums (1, 2, 3) {}
report("point", 3, 4, color="red", size=10)
#: point (3, 4) {'color': 'red', 'size': 10}
```

The names `args` and `kwargs` are convention.
The `*` and `**` do the collecting,
so `*values` and `**options` behave like `*args` and `**kwargs`.

## Unpacking Arguments

`*` and `**` also work in the other direction.
At a call site, `*` unpacks any iterable into separate positional arguments,
and `**` unpacks a dictionary into keyword arguments.

```python
# unpacking_arguments.py

def f(a, b, c):
    print(a, b, c)

x = [1, 2, 3]
f(*x)
#: 1 2 3
f(*range(4, 7))
#: 4 5 6
d = {"c": 2.72, "a": 3.14, "b": 1.62}
f(**d)
#: 3.14 1.62 2.72

def report(label, *values, **options):
    print(label, values, options)

nums = (1, 2, 3)
opts = {"color": "red", "size": 10}
report("point", *nums, **opts)
#: point (1, 2, 3) {'color': 'red', 'size': 10}

def trace(func, *args, **kwargs):
    print("calling", func.__name__)
    return func(*args, **kwargs)

trace(report, "point", *nums, **opts)
#: calling report
#: point (1, 2, 3) {'color': 'red', 'size': 10}
```

`f(*range(4, 7))` unpacks a `range`,
which computes its values as `*` consumes them.
`d` lists its keys out of order,
yet `f(**d)` prints the values in parameter order,
because `**` binds each value to the parameter its key names.

A call can use several `*` and `**` operands, mixed with ordinary arguments:
`f(*[1], *(2, 3))` and `f(1, **{"b": 2}, **{"c": 3})` each print `1 2 3`.
[Containers](03_Foundations--Containers.md)
uses the same stars to spread iterables into a list, `[*evens, *odds]`,
and to merge dictionaries, `{**a, **b}`.
A call is stricter than a dictionary literal about a repeated key.
`{**a, **b}` keeps the later value,
while a call whose two `**` operands share a key raises a `TypeError`.

Because collecting and unpacking are inverses,
a function can collect arguments beyond its named parameters and pass them on as they arrived.
`trace()` has the standard shape of a wrapper:
it accepts any call and forwards it.
`expect()` has the same shape.
It receives a function and the arguments for it, and makes the call.
[Decorators](14_Techniques--Decorators.md) builds on that forwarding.

A function is an [object like any other](40_Functional--Foundations.md#functions-as-first-class-objects),
so you can pass `report` to `trace()` as an argument.

A forwarded `**kwargs` can name a parameter that the wrapped function also receives another way.
When a key in the unpacked dictionary names a parameter that a positional argument fills,
Python raises a `TypeError`:

```python
# forwarding_collision.py
from exceptions import expect

def report(label, *values, **options):
    print(label, values, options)

def trace(func, *args, **kwargs):
    print("calling", func.__name__)
    return func(*args, **kwargs)

nums = (1, 2, 3)
opts = {"label": "oops", "color": "red"}
expect(TypeError, trace, report, *nums, **opts)
#: calling report
#: [TypeError] report() got multiple values for argument
#: 'label'
```

`opts` carries a `"label"` key, which `trace()` forwards as `label=`.
The same `func(*args, **kwargs)` call passes the items of `nums` positionally,
so `report()`'s first parameter, `label`, also receives `1`.
Each parameter takes one value.
`trace()` never reads `func`'s signature,
so the clash first appears when `trace()` calls `report()`.
Because Python raises `TypeError` there, `calling report` prints first.

## Positional-Only and Keyword-Only Parameters

Two markers in a parameter list control how callers may pass arguments.
The markers also decide which parameter names you can later rename without breaking a call.
A parameter's name is part of the contract when a caller can write it,
and stays outside the contract when the caller must pass by position.

A `/` ends the *positional-only* parameters.
You must pass every parameter before it by position.
A `*` begins the *keyword-only* parameters.
You must pass every parameter after it by name.
A `*args` parameter also begins the keyword-only parameters.
It collects every remaining positional argument,
so a parameter declared after it can arrive by name alone.

```python
# param_markers.py
from exceptions import expect

def divide(a, b, /):
    return a / b

print(divide(10, 2))
#: 5.0
expect(TypeError, divide, a=10, b=2)  # type: ignore
#: [TypeError] divide() got some positional-only arguments
#: passed as keyword arguments: 'a, b'

def make_user(name, *, admin=False):
    return f"{name} (admin={admin})"

print(make_user("Bob"))
#: Bob (admin=False)
print(make_user("Sue", admin=True))
#: Sue (admin=True)
expect(TypeError, make_user, "Sue", True)  # type: ignore
#: [TypeError] make_user() takes 1 positional argument but 2
#: were given

def tally(label, *values, total=False):
    print(label, values, total)

tally("nums", 1, 2, True)  # [1]
#: nums (1, 2, True) False
tally("nums", 1, 2, total=True)
#: nums (1, 2) True
```

The type checker reports the `divide()` and `make_user()` mistakes before the code runs,
so each of those lines carries a `# type: ignore` saying the misuse is deliberate.

The `True` in the `tally()` call at `[1]` joins `values` like any other positional argument.

A signature can use every form at once, in one set order: positional-only,
positional-or-keyword, `*args`, keyword-only, `**kwargs`.

```python
# all_markers.py

def f(a, /, b, *args, c, **kwargs):
    print(a, b, args, c, kwargs)

f(1, 2, 3, 4, c=5, d=6)
#: 1 2 (3, 4) 5 {'d': 6}
f(1, b=2, c=5)
#: 1 2 () 5 {}
```

In the standard library,
many built-in functions and methods take positional-only parameters,
such as `dict.get(key, default=None, /)`.
Because a positional-only parameter's name stays outside the method's contract,
a subclass that overrides the method can rename the parameter.
The type checker accepts the rename.

The `/` marker also lets `**kwargs` collect a keyword argument that shares a positional-only parameter's name.
With `def trace(func, /, *args, **kwargs)`,
`kwargs` collects a caller's `func=` keyword,
and `trace()` passes it on to the wrapped function.
Without the `/`, the same keyword gives `trace()`'s own `func` a second value,
so the call raises a `TypeError`.

Among the built-ins, `max()` and `min()` take a keyword-only `default`,
which they return for an empty iterable in place of raising a `ValueError`.
With `max(scores, default=0)`, the call returns `0` for an empty `scores`,
so the empty case takes one argument instead of a `try`/`except`.

## Lambdas

A `lambda` is a small anonymous function you write as a single expression.
Use one to pass behavior to functions such as `sorted()`,
which accepts a `key` function, calls it on each element,
and orders by the results.
When an existing function computes the key, pass that function,
as `key=len` does.
Write a lambda when the key is an expression of your own,
such as ordering by a word's last letter:

```python
# lambdas.py

words = ["banana", "kiwi", "apple", "fig"]
print(sorted(words, key=len))
#: ['fig', 'kiwi', 'apple', 'banana']
print(sorted(words, key=lambda w: w[-1]))
#: ['banana', 'apple', 'fig', 'kiwi']
square = lambda n: n * n  # Usually prefer def
print(square.__name__)
#: <lambda>
```

`square = lambda n: n * n` gives up the anonymity that is a lambda's point.
The assignment binds the name `square` and leaves the function's `__name__` as `<lambda>`,
so a traceback shows `<lambda>` where a `def` shows `square`.

Unlike the body of an anonymous function in many other languages,
a lambda body must be a single expression.
If the body needs a statement, such as a `for` loop or a `try`, write a `def`.

For a key that reads an index or an attribute,
`operator.itemgetter()` and `operator.attrgetter()` build that key function without a lambda.
`sorted(words, key=operator.itemgetter(-1))` replaces `key=lambda w: w[-1]` in `lambdas.py`.
For a key that calls a method on each element,
`operator.methodcaller("lower")` replaces `lambda w: w.lower()`,
and when every element is a `str`, so does `str.lower`.
Write a lambda for any other key expression.

## Exercises

Try each exercise before opening its [solution](../Solutions/05_Foundations--Functions/).

1.  In `mutable_default.py`,
    call `bad_append(3)` a third time and predict the result before checking it.
    Then change `bad_append()`'s default from `[]` to `()` and explain why that change alone does not fix `bad_append()`
    (hint: `target.append(item)` on a tuple).
2.  In `sentinel_default.py`, replace `return MISSING` with a bare `raise`,
    so a missing key with no default re-raises `KeyError`.
    Confirm that `get(prefs, "theme")` raises a `KeyError` and that `get(prefs, "theme", None)` returns `None`.
    Explain why `default=None` cannot serve as the sentinel in this function.
3.  In `param_markers.py`, add a parameter `label="result"` to `divide()`,
    keyword-only, so `print(divide(10, 2, label="half"))` shows `half: 5.0`.
    Confirm that `divide(10, 2, "half")`, passing `label` positionally,
    is now a `TypeError`.
4.  Rewrite `report()` from `var_args.py` so it accepts a `total=False` keyword-only flag that,
    when true, also prints `sum(values)`.
    Confirm `report("nums", 1, 2, 3, total=True)` prints the sum.
5.  Write `apply_twice(func, value)` that returns `func(func(value))`,
    then call it with a lambda that appends `"!"` to a string.
    Predict the result of `apply_twice(lambda s: s + "!", "hi")` before running it.
6.  Given `args = ("point", 3, 4)` and `opts = {"color": "red"}`,
    call `report()` from `var_args.py` so it prints `point (3, 4) {'color': 'red'}`,
    passing both containers without naming their contents.
7.  Write `describe(name, /, **facts)` that prints `name` followed by each keyword argument as `key=value`,
    one per line.
    Confirm that `describe(name="Bob")` is a `TypeError`,
    and explain which marker caused it.
8.  In `function_scope.py`,
    delete the `global count` line from `writes_global()` and predict what a call raises before running it.
    Then restore it, and instead add `print(count)` as the first line of `rebinds()`.
    Explain why a call to `rebinds()` also raises an `UnboundLocalError`,
    although the assignment to `count` comes after the `print`.
9.  Write `clear_by_assignment(target)`, which assigns `target = []`,
    and `clear_by_method(target)`, which calls `target.clear()`.
    Pass the same list to each,
    and predict which call empties the caller's list before running them.
10. Using `report()` and `trace()` from `unpacking_arguments.py`,
    predict what `trace(report, "point", func="f")` does, then run it.
    Add a `/` after `func` in `trace()`'s parameter list and run the call again.
    Explain where `func="f"` goes each time.
