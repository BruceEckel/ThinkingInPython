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
but no argument types or return types ([Static Typing](08_Static_Typing.md#type-hints) covers these).
Python is dynamically typed, so type errors surface at runtime rather than at compile time.
This means the same function can accept and return different types:

```python
# flexible_args_and_returns.py

def flexible_args_and_returns(arg):
    if arg == 1:
        return "one"
    if arg == "one":
        return True

print(flexible_args_and_returns(1))
#: one
print(flexible_args_and_returns("one"))
#: True
```

Here, the same function applies the '`+`' operator to integers and strings:

```python
# add.py

def add(arg1, arg2):
    return arg1 + arg2

print(add(42, 47))
#: 89
print(add("spam ", "eggs"))
#: spam eggs
```

The only constraint on a function argument is that the function can apply its operations to that object.

## Default and Keyword Arguments

Parameters can have default values.
Keyword arguments let callers pass arguments by name, in any order.
Keyword arguments make a call self-documenting:

```python
# default_args.py

def connect(host, port=5432, timeout=30):
    return f"{host}:{port} (timeout {timeout}s)"

print(connect("db.example.com"))                 # Uses both defaults
#: db.example.com:5432 (timeout 30s)
print(connect("db.example.com", timeout=5))      # Skip to a keyword
#: db.example.com:5432 (timeout 5s)
print(connect(port=80, host="web.example.com"))  # Any order by name
#: web.example.com:80 (timeout 30s)
```

Python evaluates a default value once, at function definition.
This means a mutable default is shared across calls:

```python
# mutable_default.py

def bad_append(item, target=[]):  # The same list every call
    target.append(item)
    return target

print(bad_append(1))
#: [1]
print(bad_append(2))  # Surprise, the default kept the 1
#: [1, 2]

def good_append(item, target=None):
    if target is None:
        target = []    # A fresh list each call
    target.append(item)
    return target

print(good_append(1))
#: [1]
print(good_append(2))
#: [2]
```

A mutable default persists because it lives on the function object;
Python does not recreate it on each call.
This behavior commonly confuses newcomers to the language.

You only need the `None` sentinel when the function modifies the argument.
If the function only reads the parameter, use an immutable default such as an empty tuple.
Calls still share it, but sharing is harmless because it cannot change:

```python
# immutable_default.py

def show(items=()):  # An empty tuple is safe: it can't be mutated
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
such a parameter reads `items: Sequence[str] = ()`.

The `None` sentinel works only because `None` is not a meaningful value here.
When `None` is itself a valid argument, you need a distinct marker.
Python 3.15 ([PEP 661](https://peps.python.org/pep-0661/)) adds a `sentinel`
builtin that creates one unique, self-describing value for exactly this purpose:

```python
# sentinel_default.py

MISSING = sentinel("MISSING")

def get(data, key, default=MISSING):
    if key in data:
        return data[key]
    if default is MISSING:
        raise KeyError(key)
    return default

prefs = {"volume": 3, "mute": None}
print(get(prefs, "volume"))
#: 3
print(get(prefs, "mute"))     # None is a real stored value
#: None
print(get(prefs, "theme", "dark"))
#: dark
```

Here `prefs` stores `mute` as `None`, so `None` cannot also mean "not supplied".
The `MISSING` sentinel keeps the two cases apart. A missing key with no default
raises, while a stored `None` comes back untouched.

## Variable Argument Lists

A `*args` parameter collects extra positional arguments into a tuple,
and `**kwargs` collects extra keyword arguments into a dictionary:

```python
# var_args.py

def report(label, *values, **options):
    print(label, values, options)

report("nums", 1, 2, 3)
#: nums (1, 2, 3) {}
report("point", 3, 4, color="red", size=10)   # Extras land in options
#: point (3, 4) {'color': 'red', 'size': 10}
```

## Unpacking Arguments

`*` and `**` also work in the other direction.
At a call site, `*` unpacks a sequence into separate positional arguments,
and `**` unpacks a dictionary into keyword arguments.

```python
# unpacking.py

def f(a, b, c):
    print(a, b, c)

x = [1, 2, 3]
f(*x)
#: 1 2 3
f(*(1, 2, 3))
#: 1 2 3
# ** unpacks a dictionary into keyword arguments:
d = {"a": 10, "b": 20, "c": 30}
f(**d)
#: 10 20 30

def report(label, *values, **options):
    print(label, values, options)

nums = (1, 2, 3)
opts = {"color": "red", "size": 10}
report("point", *nums, **opts)
#: point (1, 2, 3) {'color': 'red', 'size': 10}
```

Because collecting and unpacking are inverses,
a function can gather arguments with `*args` and `**kwargs`,
then pass them on unchanged, as seen in `report()`.
This is the standard way to write a wrapper around another function.

## Positional-Only and Keyword-Only Parameters

Two markers in a parameter list control how callers may pass arguments.
A `/` ends the *positional-only* parameters.
You must pass every parameter before it by position, never by name.
A `*` begins the *keyword-only* parameters.
You must pass every parameter after it by name.

```python
# param_markers.py
# `/` ends the positional-only parameters.
# `*` begins the keyword-only parameters.

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
```

Calling `divide(a=10, b=2)` is an error,
because `a` and `b` are positional-only.
Calling `make_user("Sue", True)` is an error, because `admin` is keyword-only.

In the standard library,
many built-in functions and methods take positional-only parameters, such as `dict.get(key, default, /)`.
Marking a parameter positional-only also keeps its name out of the method's contract.
That matters when a subclass overrides a method.
Since the name is not part of the interface,
the subclass can rename the parameter, and a type checker will not object.

## Lambdas

A `lambda` is a small anonymous function written as a single expression.
It is useful for passing behavior to functions such as `sorted()`:

```python
# lambdas.py

words = ["banana", "kiwi", "apple", "fig"]
print(sorted(words, key=lambda w: len(w)))  # Sort by length
#: ['fig', 'kiwi', 'apple', 'banana']
square = lambda n: n * n                    # Usually prefer def
print(square(9))
#: 81
```

Compared to other languages,
Python's lambdas allow only a single expression.
For anything more complicated, write a separate function.
