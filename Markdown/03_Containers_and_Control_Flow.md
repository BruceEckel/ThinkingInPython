# Containers and Control Flow

## Built-In Containers

With languages like C++ and Java, containers are add-on libraries and not
integral to the language. In Python, the essential nature of containers for
programming is acknowledged by building them into the core of the language:
both lists and associative arrays (a.k.a. maps, dictionaries, hash tables) are
fundamental data types. This adds much to the elegance of the language.

In addition, the `for` statement automatically iterates through lists rather
than just counting through a sequence of numbers. This makes a lot of sense
when you think about it, since you're almost always using a `for` loop to step
through an array or a container. Python formalizes this by automatically
making `for` use an iterator that works through a sequence. Here's an example:

```python
# list.py

list = [ 1, 3, 5, 7, 9, 11 ]
print(list)
list.append(13)
for x in list:
    print(x)
```

The first line creates a list. You can print the list and it will look exactly
as you put it in (in contrast, remember that I had to create a special
`Arrays2` class in *Thinking in Java* in order to print arrays in Java). Lists
are like Java containers: you can add new elements to them (here, `append()`
is used) and they will automatically resize themselves. The `for` statement
creates an iterator `x` which takes on each value in the list.

You can create a list of numbers with the `range()` function, so if you really
need to imitate C's `for`, you can.

Notice that there aren't any type declarations: the object names simply
appear, and Python infers their type by the way that you use them. It's as if
Python is designed so that you only need to press the keys that absolutely
must. You'll find after you've worked with Python for a short while that
you've been using up a lot of brain cycles parsing semicolons, curly braces,
and all sorts of other extra verbiage that was demanded by your non-Python
programming language but didn't actually describe what your program was
supposed to do.

### Lists and Slicing

A list holds an ordered, mutable sequence of any objects. Indexing starts at
zero, and negative indices count from the end. A *slice* `[start:stop:step]`
copies a subrange, with `stop` excluded:

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

### Tuples and Unpacking

A *tuple* is an immutable sequence. The comma makes the tuple, not the
parentheses. Tuples are the natural way to return several values from a function
and to group values for unpacking:

```python
# tuples.py

point = (3, 4)
x, y = point        # unpacking
print(x, y)         # 3 4
single = (42,)      # a one-element tuple needs the trailing comma
print(len(single))  # 1

def min_max(values):
    return min(values), max(values)  # returns a tuple

low, high = min_max([5, 2, 9, 1])
print(low, high)    # 1 9
```

### Dictionaries

A dictionary maps keys to values, with fast lookup. Keys must be immutable.

```python
# dictionaries.py

ages = {"Alice": 30, "Bob": 25}
print(ages["Alice"])       # 30
ages["Carol"] = 41         # add or update
print("Bob" in ages)       # True: membership tests the keys
print(ages.get("Dan", 0))  # 0: a default when the key is missing
for name, age in ages.items():
    print(name, age)
```

Reach for `dict.get()` to avoid a `KeyError` when a key might be absent.

### Sets

A set is an unordered collection of unique items, with fast membership tests and
the usual set algebra:

```python
# sets.py

a = {1, 2, 3, 3}  # duplicates collapse
b = {3, 4, 5}
print(a)          # {1, 2, 3}
print(a & b)      # {3}: intersection
print(a | b)      # {1, 2, 3, 4, 5}: union
print(a - b)      # {1, 2}: difference
print(2 in a)     # True
```

## Control Flow

You already saw `if`. Add `elif` for chained tests, and note that Python's
comparison operators chain the way they do in mathematics:

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
grade = "pass" if x >= 3 else "fail"  # conditional expression
print(grade)
```

A `while` loop runs until its condition is false. `break` leaves the loop and
`continue` skips to the next iteration:

```python
# while_loop.py

n = 27
steps = 0
while n != 1:  # the Collatz sequence
    n = n // 2 if n % 2 == 0 else 3 * n + 1
    steps += 1
print(steps, "steps")
```

For iteration, `for` walks any sequence directly. Use `range()` for counting,
`enumerate()` when you also need the index, and `zip()` to walk two sequences
together:

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

### Pattern Matching

The `match` statement compares a value against structural patterns. It is more
than a C `switch`: a pattern can destructure a value and bind its parts. (The
`f"..."` strings below are *f-strings*, covered under Strings.)

```python
# match_command.py

def run(command):
    match command.split():
        case ["go", direction]:
            return f"moving {direction}"
        case ["quit"]:
            return "goodbye"
        case _:
            return "unknown command"

print(run("go north"))
print(run("quit"))
print(run("dance"))
```

## Errors and Exceptions

Python signals an error by *raising* an exception, which propagates up until a
`try`/`except` handles it. Catch specific exception types, not everything:

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
        raise ValueError("cannot divide by zero")
    return a / b

try:
    checked_divide(1, 0)
except ValueError as e:
    print("caught:", e)
finally:
    print("finally always runs")
```

An `except` clause names the exception type. An optional `else` runs when no
exception was raised, and `finally` always runs, which makes it the place for
cleanup. Python's culture leans on "easier to ask forgiveness than permission":
try the operation and handle the exception, rather than checking every
precondition first.

## Context Managers

A `with` block guarantees that setup and cleanup happen as a pair, even if the
body raises. Opening a file is the canonical case: the file is closed on the way
out, no matter what:

```python
# context_manager.py
import os
import tempfile

path = os.path.join(tempfile.gettempdir(), "demo.txt")
with open(path, "w") as f:
    f.write("one\ntwo\n")  # f.close() happens automatically

with open(path) as f:
    for line in f:
        print(line.strip())
os.remove(path)
```

This is the explicit-finalizer approach mentioned under Cleanup. Anything that
acquires a resource (a file, a lock, a network connection) can be a context
manager.

## Comprehensions

A *comprehension* builds a list, dictionary, or set from another sequence in one
expression, replacing a loop that builds up a result:

```python
# comprehensions_intro.py

squares = [n * n for n in range(5)]           # list comprehension
print(squares)                                # [0, 1, 4, 9, 16]
evens = [n for n in range(10) if n % 2 == 0]  # with a filter
print(evens)                                  # [0, 2, 4, 6, 8]
lengths = {w: len(w) for w in ["a", "bb"]}    # dict comprehension
print(lengths)                                # {'a': 1, 'bb': 2}
```

This is such a core idiom that it has its own chapter,
[Comprehensions](13_Comprehensions.md), which also covers generator expressions
and the functional tools `map()` and `filter()`.

