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

def divide_and_report(a, b):
    try:
        checked_divide(a, b)
    except ValueError as e:
        print("caught:", e)
    else:
        print("no exception")
    finally:
        print("finally always runs")

try:
    divide_and_report(1, "x")
except TypeError as e:
    print("escaped:", type(e).__name__)
#: finally always runs
#: escaped: TypeError
```

`divide_and_report(1, "x")` raises `TypeError` inside `checked_divide`
(Python cannot divide an `int` by a `str`), and the `except` clause
only catches `ValueError`. The `finally` block still runs, because
`finally` always runs regardless of what kind of exception is in
flight, but the `TypeError` itself is not caught there. It keeps
propagating up past `divide_and_report()`, which is why this listing
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
`["go", direction]` matches a two-item list and nothing else. The
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
list for three of them. The comprehension says what the list *is*.
The loop says how to build it, and the reader has to run the loop in
their head to find out. The loop version wins when the body grows
past one condition and one expression, since a comprehension with two
filters and a nested loop is harder to read than the code it replaced.

## 7. Chaining from an exception you build yourself

```python
# exercise_7.py
import textwrap
import traceback

class BadNumber(Exception):
    pass

def substituted(text):
    try:
        return int(text)
    except ValueError:
        raise BadNumber(text) from ArithmeticError(
            "no digits here")

def joining_line(e):
    for part in traceback.format_exception(e):
        line = part.strip()
        if (line.endswith("exception occurred:")
            or line.endswith("following exception:")):
            return line
    return "nothing shown above it"

try:
    substituted("seven")
except BadNumber as e:
    for chunk in textwrap.wrap(joining_line(e), 55):
        print(" ", chunk)
    print(type(e.__cause__).__name__,
          type(e.__context__).__name__)
#:   The above exception was the direct cause of the
#:   following exception:
#: ArithmeticError ValueError
```

The prediction is the "direct cause" line, the same one `explicit()`
produces. `from` sets `__cause__` to whatever object follows it, and
`joining_line()` looks at nothing else, so an exception constructed on
the spot joins the report the same way a caught one does. `from` takes
an expression, not a name bound by `except`.

The second `print()` shows what makes this case worth writing. Both
attributes are set, and they hold different exceptions: `__cause__` is
the `ArithmeticError` you supplied, and `__context__` is still the
`ValueError` Python recorded on its own when the `raise` happened
inside a handler. Python reports the cause when there is one, so the
context is present but invisible.

That is the useful shape of the rule. `__context__` answers "what was
being handled when this was raised," which Python fills in whether you
want it or not. `__cause__` answers "what do you, the author, say
explains this," which only `from` fills in. `from None` sets
`__suppress_context__` and hides the first question's answer without
answering the second.

## 8. `read_text()` in place of the reading `with`

```python
# exercise_8.py
import tempfile
from pathlib import Path

path = Path(tempfile.gettempdir()) / "exercise_8.txt"
with path.open("w") as f:
    f.write("one\ntwo\n")

# The whole file at once
for line in path.read_text().splitlines():
    print(line)
#: one
#: two
path.unlink()
```

`read_text()` opens the file, reads all of it, and closes it, so the
one-liner is shorter and has no block. For a small file read in one
go, it is the better choice, and the chapter says so.

What the `with` form gives you is control over what happens between
the open and the close. Two things follow from that. It hands you the
file object, so you can iterate lazily, line by line, without the whole
file in memory. `read_text()` builds one string of the entire contents
before you see any of it. And it lets several operations share one
open file, where each `read_text()` call opens and closes again.

That matters when the file is large enough that holding it costs
something, when you are reading a stream that has no end, or when you
are writing rather than reading and the failure case matters: the
`with` form closes the file even when the body raises an exception,
which is the guarantee the section is about. For a configuration file
of a few kilobytes read once at startup, none of it matters, and
`read_text()` is the honest answer.

## 9. Adjacent `2`s in `mutating_while_looping.py`

```python
# exercise_9.py
scores = [2, 2, 1, 3]
for s in scores:
    if s == 2:
        scores.remove(s)
print(scores)
#: [2, 1, 3]
```

One `2` survives again, but this time at the front. At position 0 the
loop sees `2` and `remove()` deletes the first equal item, which is
that same position-0 element. The second `2` slides down into slot 0,
which the loop has already passed, so the next iteration looks at
position 1 and finds `1`. The loop never sees the survivor at all.

The prediction to make is not just "one survives" but *which* one and
*where*: the survivor is whatever slid into an already-visited slot,
so its final position depends on the data. In the chapter's
`[1, 2, 2, 3]` the survivor sits mid-list. Here it sits first. A bug
whose symptom moves around with the input is exactly why the chapter
says to build a new container instead of reasoning your way around
the mutation.
