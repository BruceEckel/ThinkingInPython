# Control Flow: Solutions

## 1. `find_factor(97)` and the loop's `else`

```python
# exercise_1.py
def find_factor(n):
    for d in range(2, n):
        if n % d == 0:
            print(f"{n} = {d} * {n // d}")
            break
    else:
        print(f"{n} is prime")

find_factor(97)
#: 97 is prime
```

The loop tries every `d` from 2 up to 96 and never finds a factor, so
it never hits `break`. The `for`'s `else` clause runs exactly when the
loop finishes without a `break`, so it prints `97 is prime`.

## 2. Counting odd steps in the Collatz sequence

```python
# exercise_2.py
def collatz_sequence(n):
    steps = 0
    odd_count = 0
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
            odd_count += 1
        print(n)
        steps += 1
    return steps, odd_count

print(collatz_sequence(10))
#: 5
#: 16
#: 8
#: 4
#: 2
#: 1
#: (6, 1)
```

Six steps total, and only one of them (`5 -> 16`) starts from an odd
`n`. `odd_count` increments in the branch that takes `3 * n + 1`,
which is the branch that only runs when `n` was odd.

## 3. Swapped order of `continue` and `break`

```python
# exercise_3.py
for n in range(10):
    if n == 6:
        break
    if n == 3:
        continue
    print(n, end=" ")
print()
#: 0 1 2 4 5
```

The output is the same as the original order. The two `if`
blocks test different, mutually exclusive values of `n` (`6` and
`3`), so on any given loop iteration at most one of them can be true.
Since neither block's outcome depends on whether the other one ran
first, checking them in either order produces the same result. Order
only matters when two conditions could both be true for the same
value and send execution down different paths, which is not the
case here.

## 4. An exception that escapes the handler

```python
# exercise_4.py
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

try:
    demo_exceptions(1, "x")
except TypeError as e:
    print("escaped:", type(e).__name__)
#: finally always runs
#: escaped: TypeError
```

`demo_exceptions(1, "x")` raises `TypeError` inside `checked_divide`
(Python cannot divide an `int` by a `str`), and the `except` clause
only catches `ValueError`. The `finally` block still runs, because
`finally` always runs regardless of what kind of exception is in
flight, but the `TypeError` itself is not caught there. It keeps
propagating up past `demo_exceptions()`, which is why this listing
wraps the call in its own `try`/`except TypeError` to show the
exception actually escaping, the same thing an interactive session or
an outer caller sees. Note that `else` never runs here: it belongs to
the case where the `try` block finished cleanly.

## 5. A three-item `case` in `pattern_matching.py`

```python
# exercise_5.py
def run(command):
    match command.split():
        case ["go", direction, distance]:
            return f"moving {direction} for {distance}"
        case ["go", direction]:
            return f"moving {direction}"
        case ["quit"]:
            return "goodbye"
        case _:
            return "unknown command"

print(run("go north 3"))
#: moving north for 3
print(run("go north"))
#: moving north
```

Before the new `case` exists, `run("go north 3")` returns `unknown
command`. A list pattern matches on length as well as content, so
`["go", direction]` matches a two-item list and nothing else; the
three-item split falls through to `case _`. Adding the longer pattern
gives that length somewhere to land. Order matters only between
patterns that could both match the same value, which these two cannot,
so either arrangement works here.

## 6. The comprehension written as a loop

```python
# exercise_6.py
evens = []
for n in range(10):
    if n % 2 == 0:
        evens.append(n)
print(evens)
#: [0, 2, 4, 6, 8]
```

Four lines instead of one, and the name `evens` is bound to an empty
list for three of them. The comprehension says what the list *is*;
the loop says how to build it, and the reader has to run the loop in
their head to find out. The loop version wins when the body grows
past one condition and one expression, since a comprehension with two
filters and a nested loop is harder to read than the code it replaced.
