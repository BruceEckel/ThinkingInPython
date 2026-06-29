# Control Flow

Control-flow statements decide which code runs and how often.
This chapter covers conditionals, loops, pattern matching, exceptions, the `with` statement, and comprehensions.

## Conditionals and Loops

Python's comparison operators chain the way they do in mathematics:

```python
# chaining.py

x = 5
print(0 < x < 10)  # Chained comparison
#: True
grade = "pass" if x >= 3 else "fail"  # Conditional expression
print(grade)
#: pass
```

Adding `elif` to an `if` statement chains multiple tests:

```python
# if_elif.py

def classify(n):
    if n < 0:
        return "negative"
    elif n == 0:
        return "zero"
    else:
        return "positive"

print(classify(-3), classify(0), classify(7))
#: negative zero positive
```

The `pass` statement does nothing.
Use it where Python's syntax requires a statement but you have none to run yet:

```python
# pass_statement.py

def not_implemented():
    pass  # Fill in later

print(not_implemented())
#: None
```

A `while` loop runs until its condition is false:

```python
# while_loop.py

def collatz_sequence(n):
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        print(n)
        steps += 1
    return steps

print(collatz_sequence(10), "steps")
#: 5
#: 16
#: 8
#: 4
#: 2
#: 1
#: 6 steps
```

`break` leaves a loop and `continue` skips to the next iteration:

```python
# break_continue.py

for n in range(10):
    if n == 3:
        continue   # Skip the rest of this iteration
    if n == 6:
        break      # Leave the loop entirely
    print(n, end=" ")
#: 0 1 2 4 5
```

The loop prints `0 1 2`, skips `3` with `continue`, prints `4 5`,
then stops at `6` with `break`, so `6` through `9` never print.

A loop may have an `else` clause.
It runs only if the loop finished without hitting `break`,
which makes it natural for search loops:

```python
# loop_else.py

def find_factor(n):
    for d in range(2, n):
        if n % d == 0:
            print(f"{n} = {d} * {n // d}")
            break
    else:
        print(f"{n} is prime")  # No break means no factor found

find_factor(15)
#: 15 = 3 * 5
find_factor(13)
#: 13 is prime
```

The `else` belongs to the `for`, not the `if`.
A `while` loop can use `else` the same way.

When iterating, `for` walks any sequence directly.
Use `range()` for counting, `enumerate()` when you also need the index,
and `zip()` to walk two sequences together:

```python
# looping.py

for i in range(3):
    print(i, end=" ")
print()
#: 0 1 2
names = ["Alice", "Bob", "Carol"]
for index, name in enumerate(names):
    print(index, name)
#: 0 Alice
#: 1 Bob
#: 2 Carol
scores = [88, 91, 79, 54, 99]  # Last two unused
for name, score in zip(names, scores):
    print(name, score)
#: Alice 88
#: Bob 91
#: Carol 79
```

`enumerate()` yields `(index, item)` pairs counting from zero, which the loop here unpacks into `index` and `name`.
`zip()` walks several sequences at once, producing one item from each and stopping when the shortest runs out.

The *walrus operator* `:=` assigns a value as part of an expression,
so you can compute, name, and test a value in one place:

```python
# walrus.py

text = "hello"
# Without it, you assign first and then test:
length = len(text)
if length > 3:
    print(f"{length} characters")
#: 5 characters
# The walrus assigns inside the condition:
if (n := len(text)) > 3:
    print(f"{n} characters")
#: 5 characters
```

It is especially handy in `while` conditions and comprehensions,
where it avoids repeating a computation.

With `print()`, the default `end` (printed after the value) is a newline.
You can use `sep` to change the separator between values.

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
#: moving north
print(run("quit"))
#: goodbye
print(run("dance"))
#: unknown command
```

[Pattern Matching](12_Pattern_Matching.md) covers `match` in detail.

## Errors and Exceptions

Python signals an error by *raising* an exception.
Like C++ and Java, an exception propagates up the call stack until it finds a handler.
In Python, handlers are indicated by `except` followed by the exception type it handles.
You can give only the type, or add an `as` to capture the exception object,
seen here in `except ValueError as e`:

```python
# exceptions.py

def parse_int(text):
    try:
        return int(text)
    except ValueError:
        return None

print(parse_int("42"))
#: 42
print(parse_int("oops"))
#: None

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
#: caught: Divide by zero
#: finally always runs
demo_exceptions(1, 1)
#: no exception
#: finally always runs
```

The optional `else` runs when no exception was raised, and `finally` always runs,
which makes it the place for cleanup.

Python's culture leans on "easier to ask forgiveness than permission."
Try the operation and handle the exception,
rather than checking every precondition first.

## Context Managers

A `with` block guarantees that setup and cleanup happen as a pair,
even if the body raises an exception.
Opening a file is the canonical case; the file is always closed on the way out:

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
#: one
#: two
path.unlink()  # Delete the file
```

This is the explicit-finalizer approach from [Class Attributes and Cleanup](09_Class_Attributes_and_Cleanup.md#cleanup).
Anything that acquires a resource (a file, a lock, a network connection) can be a context manager.
[Context Managers](15_Context_Managers.md) shows how to write your own.
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
print(squares)
#: [0, 1, 4, 9, 16]
evens = [n for n in range(10) if n % 2 == 0]  # With a filter
print(evens)
#: [0, 2, 4, 6, 8]
lengths = {w: len(w) for w in ["a", "bb"]}    # Dict comprehension
print(lengths)
#: {'a': 1, 'bb': 2}
parities = {n % 2 for n in range(10)}         # Set comprehension
print(parities)
#: {0, 1}
```

[Comprehensions](16_Comprehensions.md#list-comprehensions) covers comprehensions in detail,
as well as generator expressions and the functional tools `map()` and `filter()`.
