# Functions

Functions are defined with the `def` keyword,
followed by the function name and argument list,
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
## continuing...
## 0
print(a_function("yes"))
## affirmative
## continuing...
## 1
```

Here the function signature only specifies the name of the function and the argument identifiers,
but no argument types or return types (these are covered in [Static Typing](07_Static_Typing.md#type-hints)).
Python is dynamically typed, so it enforces type constraints at runtime rather than compile time.
This means that different types can be both passed to and returned from the same function:

```python
# flexible_args_and_returns.py

def flexible_args_and_returns(arg):
    if arg == 1:
        return "one"
    if arg == "one":
        return True

print(flexible_args_and_returns(1))
## one
print(flexible_args_and_returns("one"))
## True
```

Here, the same function applies the '`+`' operator to integers and strings:

```python
# sum.py

def add(arg1, arg2):
    return arg1 + arg2

print(add(42, 47))
## 89
print(add('spam ', "eggs"))
## spam eggs
```

The only constraints on an object that is passed into a function are that the function can apply its operations to that object.

## Default and Keyword Arguments

Parameters can have defaults,
and callers can pass arguments by name in any order.
Keyword arguments make a call self-documenting:

```python
# default_args.py

def connect(host, port=5432, timeout=30):
    return f"{host}:{port} (timeout {timeout}s)"

print(connect("db.example.com"))                 # Uses both defaults
## db.example.com:5432 (timeout 30s)
print(connect("db.example.com", timeout=5))      # Skip to a keyword
## db.example.com:5432 (timeout 5s)
print(connect(port=80, host="web.example.com"))  # Any order by name
## web.example.com:80 (timeout 30s)
```

A default value is evaluated once, when the function is defined,
not on each call.
A mutable default is therefore shared across calls:

```python
# mutable_default.py

def bad_append(item, target=[]):  # The same list every call
    target.append(item)
    return target

print(bad_append(1))
## [1]
print(bad_append(2))  # Surprise, the default kept the 1
## [1, 2]

def good_append(item, target=None):
    if target is None:
        target = []    # A fresh list each call
    target.append(item)
    return target

print(good_append(1))
## [1]
print(good_append(2))
## [2]
```

Thus a mutable default persists between calls: it is created once,
at definition time, and lives on the function, not recreated on each call.
This behavior is a common confusion for newcomers to the language.

## Variable Argument Lists

A `*args` parameter collects extra positional arguments into a tuple,
and `**kwargs` collects extra keyword arguments into a dictionary:

```python
# var_args.py

def report(label, *values, **options):
    print(label, values, options)

report("nums", 1, 2, 3)
## nums (1, 2, 3) {}
report("point", 3, 4, color="red", size=10)   # Extras land in options
## point (3, 4) {'color': 'red', 'size': 10}
```

The same `*` and `**` *unpack* a sequence or dictionary back into arguments at a call site,
the mirror image of collecting them.

## Positional-Only and Keyword-Only Parameters

Two markers in a parameter list control how callers may pass arguments.
A `/` ends the *positional-only* parameters:
every parameter before it must be passed by position, never by name.
A `*` begins the *keyword-only* parameters:
every parameter after it must be passed by name.

```python
# param_markers.py
# `/` ends the positional-only parameters.
# `*` begins the keyword-only parameters.

def divide(a, b, /):
    return a / b

print(divide(10, 2))
## 5.0

def make_user(name, *, admin=False):
    return f"{name} (admin={admin})"

print(make_user("Bob"))
## Bob (admin=False)
print(make_user("Sue", admin=True))
## Sue (admin=True)
```

Calling `divide(a=10, b=2)` is an error,
because `a` and `b` are positional-only.
Calling `make_user("Sue", True)` is an error, because `admin` is keyword-only.

In the standard library,
many built-in functions take positional-only arguments such as `dict.get(key, default, /)`.
Marking a parameter positional-only also keeps its name out of the method's contract.
That matters when a subclass overrides a method:
since the name is not part of the interface,
the subclass can rename the parameter, and a type checker will not object.

## Unpacking Arguments

`*` also works in the other direction:
at a call site it *unpacks* a sequence into separate positional arguments.

```python
# unpacking.py
# Turn a sequence into positional arguments with *.
def f(a, b, c):
    print(a, b, c)

x = [1, 2, 3]
f(*x)
## 1 2 3
f(*(1, 2, 3))
## 1 2 3
```

## Lambdas

A `lambda` is a small anonymous function written as a single expression.
It is useful for passing behavior to functions such as `sorted()`:

```python
# lambdas.py

words = ["banana", "kiwi", "apple", "fig"]
print(sorted(words, key=lambda w: len(w)))  # Sort by length
## ['fig', 'kiwi', 'apple', 'banana']
square = lambda n: n * n                    # Usually prefer def
print(square(9))
## 81
```

Compared to other languages, Python's lambdas are constrained because they comprise a single expression.
For anything more complicated you are expected to write a separate function.
