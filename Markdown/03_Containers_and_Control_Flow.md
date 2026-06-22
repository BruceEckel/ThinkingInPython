# Containers and Control Flow

With languages like C++ and Java, containers are add-on libraries.
In Python, the essential nature of containers for programming is acknowledged by building them into the core of the language.
Both lists and associative arrays (maps, dictionaries, hash tables) are fundamental data types.

In addition, the `for` statement automatically iterates through lists rather than just counting through a sequence of numbers.
Python's `for` automatically uses an iterator that works through a sequence:

```python
# list.py

list = [ 1, 3, 5, 7, 9, 11 ]
print(list)
list.append(13)
for x in list:
    print(x)
```

The first line creates a `list`.
`append()` adds new elements to a `list`;
the `list` automatically resizes itself.
The `for` statement creates an iterator `x` which takes on each value in the `list`.

There are no type declarations in this example;
Python infers types from the way you use them.

## Lists and Slicing

A `list` holds an ordered, mutable sequence of any objects.
Indexing starts at zero, and negative indices count from the end.
A *slice* `[start:stop:step]` copies a subrange, with `stop` excluded:

```python
# slicing.py

xs = [10, 20, 30, 40, 50]
print(xs[0], xs[-1])  # 10 50: first and last
print(xs[1:3])        # [20, 30]: the stop index is excluded
print(xs[:2])         # [10, 20]: from the start
print(xs[2:])         # [30, 40, 50]: to the end
print(xs[::2])        # [10, 30, 50]: every second item
print(xs[::-1])       # [50, 40, 30, 20, 10]: reversed
xs.append(60)
xs.insert(0, 5)
print(len(xs), 30 in xs)  # 7 True
```

Slicing works on any sequence, including strings and tuples.

## Tuples and Unpacking

A *tuple* is an immutable sequence.
The comma makes the tuple, not the parentheses.
Tuples are the natural way to return several values from a function and to group values for unpacking:

```python
# tuples.py

point = (3, 4)
point = 3, 4        # Also a tuple; the comma is what matters
empty = ()          # Empty tuple
x, y = point        # Unpacking
print(x, y)         # 3 4
single = (42,)      # A one-element tuple needs the trailing comma
print(len(single))  # 1
tuple([1, 2, 3])    # Converts to (1, 2, 3)  from a list
tuple("abc")        # ('a', 'b', 'c')

def min_max(values):
    return min(values), max(values)  # Returns a tuple

low, high = min_max([5, 2, 9, 1])
print(low, high)    # 1 9
```

Tuples are often heterogeneous, with each position a different type.
They are fixed-length records where each position has a distinct meaning.

## Dictionaries

A dictionary (`dict`) maps keys to values, with fast lookup.
Keys must be immutable.

```python
# dictionaries.py

ages = {"Alice": 30, "Bob": 25}
print(ages["Alice"])       # 30
ages["Carol"] = 41         # Add or update
print("Bob" in ages)       # True: membership tests the keys
print(ages.get("Dan", 0))  # 0: a default when the key is missing
for name, age in ages.items():
    print(name, age)
```

Use `dict.get()` to avoid a `KeyError` when a key might be absent.

## Sets

A set is an unordered collection of unique items,
with fast membership tests and the usual set algebra:

```python
# sets.py

a = {1, 2, 3, 3}  # Duplicates collapse
b = {3, 4, 5}
print(a)          # {1, 2, 3}
print(a & b)      # {3}: intersection
print(a | b)      # {1, 2, 3, 4, 5}: union
print(a - b)      # {1, 2}: difference
print(2 in a)     # True
```

Every operator above has a named method.
The methods are a little more flexible: they accept any iterable,
not just a set, and they take several arguments at once.
There is also `isdisjoint`, which has no operator form:

```python
# set_methods.py
a = {1, 2, 3}
b = {3, 4, 5}

print(a.intersection(b))  # {3}: same as a & b
print(a.union(b))  # {1, 2, 3, 4, 5}: same as a | b
print(a.difference(b))  # {1, 2}: same as a - b
print(a.symmetric_difference(b))  # {1, 2, 4, 5}: same as a ^ b
print(a.intersection([2, 3, 9]))  # {2, 3}: arg can be any iterable
print(a.union(b, [6, 7]))  # {1, 2, 3, 4, 5, 6, 7}: several args
print(a.isdisjoint({8, 9}))  # True: no operator form
```

## Control Flow

If you add `elif` to an `if` expression, you can chain multiple tests together.

```python
# control_flow.py

def classify(n):
    if n < 0:
        return "negative"
    elif n == 0:
        return "zero"
    else:
        return "positive"

print(classify(-3), classify(0), classify(7))

x = 5
print(0 < x < 10)  # True: chained comparison
grade = "pass" if x >= 3 else "fail"  # Conditional expression
print(grade)
```

Python's comparison operators chain the way they do in mathematics:

A `while` loop runs until its condition is false.
`break` leaves the loop and `continue` skips to the next iteration:

```python
# while_loop.py

n = 27
steps = 0
while n != 1:  # The Collatz sequence
    n = n // 2 if n % 2 == 0 else 3 * n + 1
    print(n)
    steps += 1
print(steps, "steps")
```

For iteration, `for` walks any sequence directly.
Use `range()` for counting, `enumerate()` when you also need the index,
and `zip()` to walk two sequences together:

```python
# looping.py

for i in range(3):  # 0, 1, 2
    print(i, end=" ")
print()
names = ["Alice", "Bob", "Carol"]
for index, name in enumerate(names):
    print(index, name)
scores = [88, 91, 79]
for name, score in zip(names, scores):
    print(name, score)
```

With `print`, the default `end` (printed after the value) is a newline.
With multiple values in a `print` call, you can use `sep` to change the separator between values.

## Pattern Matching

The `match` statement compares a value against structural patterns.
It is reminiscent of a C `switch`, but much more powerful.
A pattern can destructure a value and bind its parts.

```python
# pattern_matching.py

def run(command):
    match command.split():
        case ["go", direction]:
            return f"moving {direction}"
        case ["quit"]:
            return "goodbye"
        case _:  # Default
            return "unknown command"

print(run("go north"))
print(run("quit"))
print(run("dance"))
```

## Errors and Exceptions

Python signals an error by *raising* an exception.
Like C++ and Java, an exception propagates up the call stack until they find a handler.
In Python, handlers are indicated by `except` followed by the exception type it handles:

```python
# exceptions.py

def parse_int(text):
    try:
        return int(text)
    except ValueError:
        return None

print(parse_int("42"))    # 42
print(parse_int("oops"))  # None

def checked_divide(a, b):
    if b == 0:
        raise ValueError("Divide by zero")
    return a / b

def demo_exceptions(a, b):
    try:
        checked_divide(a, b)
    except ValueError as e:
        print("caught:", e)
    else:
        print("no exception")
    finally:
        print("finally always runs")

demo_exceptions(1, 0)
demo_exceptions(1, 1)
```

The optional `else` runs when no exception was raised, and `finally` always runs,
which makes it the place for cleanup.
Python's culture leans on "easier to ask forgiveness than permission."
This means: try the operation and handle the exception,
rather than checking every precondition first.

## Context Managers

A `with` block guarantees that setup and cleanup happen as a pair,
even if the body raises an exception.
Opening a file is the canonical case: the file is closed on the way out,
no matter what:

```python
# context_manager.py
import tempfile
from pathlib import Path

path = Path(tempfile.gettempdir()) / "demo.txt"
with path.open("w") as f:
    f.write("one\ntwo\n")  # f.close() happens automatically

with path.open() as f:
    for line in f:
        print(line.strip())

path.unlink()  # Delete the file
```

This is the explicit-finalizer approach from the [Class Attributes and Cleanup](08_Class_Attributes_and_Cleanup.md) chapter.
Anything that acquires a resource (a file, a lock, a network connection) can be a context manager.
Note that when simply reading or writing to a file,
`pathlib` provides convenient utility methods like `read_text()` and `write_text()`
that handle opening and closing the file for you.

## Comprehensions

A *comprehension* builds a `list`, dictionary,
or set from another sequence in one expression,
replacing a loop that builds up a result:

```python
# comprehensions_intro.py

squares = [n * n for n in range(5)]           # List comprehension
print(squares)                                # [0, 1, 4, 9, 16]
evens = [n for n in range(10) if n % 2 == 0]  # with a filter
print(evens)                                  # [0, 2, 4, 6, 8]
lengths = {w: len(w) for w in ["a", "bb"]}    # Dict comprehension
print(lengths)                                # {'a': 1, 'bb': 2}
parities = {n % 2 for n in range(10)}         # Set comprehension
print(parities)                               # {0, 1}
```

The [Comprehensions](14_Comprehensions.md) chapter covers comprehensions in detail,
as well as generator expressions and the functional tools `map()` and `filter()`.
