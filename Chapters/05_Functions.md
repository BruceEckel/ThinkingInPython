# Functions

You define functions with the `def` keyword,
followed by the function name and parameter list,
and a colon to begin the function body:

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

Here the function signature specifies only the function name and the parameter names,
but no argument types or return types
([Static Typing](08_Static_Typing.md#type-hints) covers these).
Python is dynamically typed,
so type errors surface at runtime rather than at compile time.
The same function can therefore accept and return different types:

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

The third call matches neither test,
so the function reaches its end without returning anything and produces `None`.
Every Python function returns a value.
A bare `return` and a missing `return` both produce `None`.

A `return` with several expressions produces a tuple,
which the caller usually unpacks:

    def minmax(values):
        return min(values), max(values)

    low, high = minmax([3, 1, 4])

The commas build the tuple; the function still returns one object.

Here, the same function applies the `+` operator to integers and strings:

```python
# add.py

def add(arg1, arg2):
    return arg1 + arg2

print(add(42, 47))
#: 89
print(add("spam ", "eggs"))
#: spam eggs
try:
    add(42, "spam")
except TypeError as e:
    print(e)
#: unsupported operand type(s) for +: 'int' and 'str'
```

A function argument works as long as the function can apply its operations to it.
The failure comes from `+`, inside the call, not from the call itself.
Nothing checks the arguments on the way in.

## Default and Keyword Arguments

Parameters can have default values,
and keyword arguments let callers pass them by name, in any order,
which makes a call self-documenting:

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

Passing by name does not require a default: `host` has none,
and the last call still names it.
At the call site, every keyword argument must come after the positional ones.
`connect(port=80, "web.example.com")` is a `SyntaxError`:
`positional argument follows keyword argument`.

A parameter with a default cannot come before one without.
`def f(a=1, b):` is a `SyntaxError`:
`parameter without a default follows parameter with a default`.
[Keyword-only parameters](#positional-only-and-keyword-only-parameters)
are exempt, because the caller names them.

Python evaluates a default value once, at function definition.
So all calls share one mutable default:

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

A mutable default persists because it lives on the function object;
no call rebuilds it.
`__defaults__` holds the tuple of default values,
and both calls append to the same list inside it.
The default looks like an expression the call evaluates, and it is not.

Underneath, a parameter is another name bound to the caller's object,
the binding that [Variables and References](02_Tour.md#variables-and-references)
describes.
When that object is mutable, the caller sees the changes the function makes.
`bad_append()` combines this with a default Python builds once,
so each call mutates the object the next call uses.

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
which points the local name at a new list and leaves the caller's list alone.
Mutating an argument reaches outside the function; rebinding one does not.

The `None` default in `good_append()` is a *sentinel*:
a value chosen to mean "the caller passed nothing" rather than to serve as data.
You need one when the function mutates that parameter,
because the default must then be a fresh object on every call.
Test it with `is None` rather than truthiness:
`if not target:` also discards an empty list the caller passed on purpose.
If the function only reads the parameter,
use an immutable default such as an empty tuple.
Calls still share it, but sharing is harmless because it cannot change:

```python
# immutable_default.py

# An empty tuple is safe: it can't be mutated
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

With the type hints from [Static Typing](08_Static_Typing.md#type-hints),
such a parameter reads:

    items: Sequence[str] = ()

The `None` sentinel works only because `None` is not a meaningful value here.
When `None` is also a valid argument, you need a distinct marker.
Python 3.15 ([PEP 661](https://peps.python.org/pep-0661/))
adds a `sentinel` builtin that creates a unique self-describing value for this purpose:

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

Here `prefs` stores `mute` as `None`, so `None` cannot also mean "not supplied."
The `MISSING` sentinel keeps the two cases apart.
A missing key with no default normally raises an exception.
A stored `None` comes back untouched.

Create a sentinel once and share that name.
Each `sentinel()` call builds a new object, even for the same name,
so `default is sentinel("MISSING")` compares against a second object and is always false.

## Names Inside a Function

A function can read a module-level name,
but assigning to that name anywhere in the function makes it local for the whole function.
Python decides which names are local when it compiles the function body,
so where the assignment sits makes no difference.
`global` tells Python to rebind the module-level name instead:

```python
# function_scope.py

count = 0

def read_only():
    print(count)

def rebinds():
    # A local, unrelated to the module-level count
    count = 99
    print(count)

def writes_global():
    global count
    count += 1

read_only()
#: 0
rebinds()
#: 99
writes_global()
print(count)
#: 1
```

`rebinds()` never touches the module-level `count`.
If you drop the `global` from `writes_global()`,
`count += 1` reads a local before assigning it,
so the call raises an `UnboundLocalError`.
`global` governs rebinding, not reading,
which is why `read_only()` needs nothing.
[Closures](40_Functional_Foundations.md#closures) covers `nonlocal`,
the same idea one scope in.

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

The names `args` and `kwargs` are convention;
the `*` and `**` do the collecting,
so `*values` and `**options` behave identically.

## Unpacking Arguments

`*` and `**` also work in the other direction.
At a call site, `*` unpacks a sequence into separate positional arguments,
and `**` unpacks a dictionary into keyword arguments.

```python
# unpacking_arguments.py

def f(a, b, c):
    print(a, b, c)

x = [1, 2, 3]
f(*x)
#: 1 2 3
f(*(4, 5, 6))
#: 4 5 6
d = {"a": 3.14, "b": 1.62, "c": 2.72}
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

Because collecting and unpacking are inverses,
a function can gather arguments it knows nothing about and pass them on unchanged.
`trace()` accepts any call and forwards it,
which is the standard shape of a wrapper.
A function is an object like any other,
so you can pass `report` to `trace()` as an argument,
and `func.__name__` reads the name of whatever function arrived
(see [Functions as First-Class Objects](40_Functional_Foundations.md#functions-as-first-class-objects)).
[Decorators](14_Decorators.md) builds on this.

## Positional-Only and Keyword-Only Parameters

Two markers in a parameter list control how callers may pass arguments,
which decides how much of a signature you commit to keeping.
A parameter a caller can name is part of the contract; one it cannot is not.
A `/` ends the *positional-only* parameters.
You must pass every parameter before it by position, not by name.
A `*` begins the *keyword-only* parameters.
You must pass every parameter after it by name.
A `*args` parameter has the same effect as a bare `*`.
It absorbs every remaining positional argument,
so you can pass a parameter declared after it only by name.

```python
# param_markers.py

def divide(a, b, /):
    return a / b

print(divide(10, 2))
#: 5.0

def make_user(name, *, admin=False):
    return f"{name} (admin={admin})"

print(make_user("Bob"))
#: Bob (admin=False)
print(make_user("Sue", admin=True))
#: Sue (admin=True)

def tally(label, *values, total=False):
    print(label, values, total)

tally("nums", 1, 2, True)
#: nums (1, 2, True) False
tally("nums", 1, 2, total=True)
#: nums (1, 2) True

try:
    divide(a=10, b=2)  # type: ignore
except TypeError as e:
    print(type(e).__name__)
#: TypeError
try:
    make_user("Sue", True)  # type: ignore
except TypeError as e:
    print(e)
#: make_user() takes 1 positional argument but 2 were given
```

The `True` in the first `tally()` call joins `values` like any other positional argument.
Only the named form reaches `total`.

Calling `divide(a=10, b=2)` is an error,
because `a` and `b` are positional-only.
The full message reports `got some positional-only arguments passed as keyword arguments: 'a, b'`.
Calling `make_user("Sue", True)` is an error, because `admin` is keyword-only.
The type checker catches both mistakes without running the code,
so each line carries a `# type: ignore` saying the misuse is deliberate.

A signature can use every form at once, in one fixed order: positional-only,
positional-or-keyword, `*args`, keyword-only, `**kwargs`:

```python
# all_markers.py

def f(a, /, b, *args, c, **kwargs):
    print(a, b, args, c, kwargs)

f(1, 2, 3, 4, c=5, d=6)
#: 1 2 (3, 4) 5 {'d': 6}
```

`a` can only arrive positionally, `c` can only arrive by name,
and `b` can do either.

In the standard library,
many built-in functions and methods take positional-only parameters,
such as `dict.get(key, default=None, /)`.
Marking a parameter positional-only also keeps its name out of the method's contract.
That matters when a subclass overrides a method:
the subclass can rename the parameter, and a type checker does not object.

## Lambdas

A `lambda` is a small anonymous function you write as a single expression.
Use one to pass behavior to functions such as `sorted()`,
which accepts a `key` function, calls it on each element,
and orders by the results.
When an existing function already computes the key, pass the function itself:
`key=len` needs no lambda.
Write a lambda when nothing existing computes what you want,
such as ordering by a word's last letter:

```python
# lambdas.py

words = ["banana", "kiwi", "apple", "fig"]
print(sorted(words, key=len))
#: ['fig', 'kiwi', 'apple', 'banana']
print(sorted(words, key=lambda w: w[-1]))
#: ['banana', 'apple', 'fig', 'kiwi']
square = lambda n: n * n  # Usually prefer def
print(square(9))
#: 81
```

Assigning a lambda to a name, as `square` does,
gives up the anonymity that is a lambda's point;
`def` also gives the function a real name for tracebacks.
Unlike anonymous functions in many other languages,
a lambda body must be a single expression.
For anything more complicated, write a separate function.

## Exercises

1.  In `mutable_default.py`,
    call `bad_append(3)` a third time and predict the result before checking it.
    Then change `bad_append`'s default from `[]` to `()` and explain why that alone does not fix it
    (hint: `target.append(item)` on a tuple).
2.  In `sentinel_default.py`, add a third key to `prefs`, `"volume2": None`,
    and call `get(prefs, "volume2")` to confirm the sentinel still tells `None`-as-value apart from missing.
3.  In `param_markers.py`, add a parameter `label="result"` to `divide()`,
    keyword-only, so `print(divide(10, 2, label="half"))` shows `half: 5.0`.
    Confirm that `divide(10, 2, "half")`, passing `label` positionally,
    is now a `TypeError`.
4.  Rewrite `report()` from `var_args.py` so it also accepts a `total=False` keyword-only flag that,
    when true, additionally prints `sum(values)`.
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
    Explain why that also raises an `UnboundLocalError`,
    even though the assignment to `count` comes after the `print`.
