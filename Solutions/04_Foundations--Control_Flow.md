# Control Flow: Solutions

## 1. `find_factor(97)` and the loop's `else`

> In `loop_else.py`, call `find_factor(97)`.
> Predict whether the `for` loop's `else` clause runs before you check,
> then confirm.

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

The loop tries every `d` from 2 up to 96 and finds no factor, so it
does not reach `break`. The `for`'s `else` clause runs when the loop
finishes without a `break`, so it prints `97 is prime`.

## 2. Counting odd steps in the Collatz sequence

> Change `collatz_sequence()` in `while_loop.py` to also count how many times `n` is odd,
> and print that count alongside the step count.

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
`n`. `odd_count` increments in the `else` branch, the one that takes
`3 * n + 1`, and that branch runs only when `n` is odd.

## 3. Swapped order of `continue` and `break`

> In `break_continue.py`, swap the order of the two `if` blocks,
> so the `n == 6` `break` check comes first and the `n == 3` `continue` check comes second.
> Predict whether the output changes before running it,
> then explain what you find.

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

The output is the same as with the original order. The two `if`
blocks test mutually exclusive values of `n` (`6` and `3`), so on
any given iteration at most one of them can be true. Neither block's
outcome depends on whether the other runs first, so checking them in
either order produces the same result. Order matters only when two
conditions can both be true for the same value and send execution
down different paths. Here they cannot.

## 4. An exception that escapes the handler

> In `demonstrate_exceptions.py`, add a call `divide_and_report(1, "x")`
> (a `TypeError` that `except ValueError` does not catch).
> Run it and read the traceback that escapes.

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

`divide_and_report(1, "x")` raises `TypeError` inside
`checked_divide()`, because Python cannot divide an `int` by a `str`.
The `except` clause catches only `ValueError`, so the `TypeError`
passes it by. The `finally` block runs anyway: `finally` runs
whatever kind of exception is in flight. The `TypeError` keeps
propagating up past `divide_and_report()`, so this listing wraps the
call in its own `try`/`except TypeError` to show the exception
escaping. An interactive session or an outer caller sees the same
thing. The `else` clause never runs here: it belongs to the case
where the `try` block finishes cleanly.

## 5. A three-item `case` in `pattern_matching.py`

> In `pattern_matching.py`,
> add a `case ["go", direction, distance]` that reports both parts,
> and check what `run("go north 3")` returns before and after you add it.

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
`["go", direction]` matches only a list of two items. The three-item
split matches neither of the original patterns and reaches `case _`.
The longer pattern gives a three-item list a `case` of its own. Order
matters only between patterns that could both match the same value.
These two cannot, so either arrangement works here.

## 6. The comprehension written as a loop

> Rewrite the `evens` list comprehension in `comprehensions_intro.py` as a `for` loop that appends to a list,
> then say which version you would rather read six months from now.

```python
# exercise_6.py
evens = []
for n in range(10):
    if n % 2 == 0:
        evens.append(n)
print(evens)
#: [0, 2, 4, 6, 8]
```

The loop takes four lines instead of one, and until it finishes the
name `evens` holds a partial result. The comprehension states the
contents of the list. The loop says how to build it, and the reader
runs the loop in their head to learn the contents. The loop version
wins when the body
grows past one condition and one expression, since a comprehension
with two filters and a nested loop is harder to read than the code it
replaced.

## 7. Chaining from an exception you build yourself

> In `exception_chaining.py`,
> add a fourth function that catches the `ValueError` and raises `BadNumber` from a *different* exception object it constructs.
> Predict which line `joining_line()` prints before you run it.

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
Python builds the traceback that `joining_line()` searches from
`__cause__`. An exception constructed in the `raise` statement joins the
report the same way a caught one does. `from` takes an expression, not a name
bound by `except`.

The second `print()` shows what makes this case worth writing. Both
attributes hold an exception, and different ones: `__cause__` is the
`ArithmeticError` you supplied, and `__context__` is still the
`ValueError` Python recorded on its own when the `raise` happened
inside a handler. Python reports the cause when one exists, so the
context is present but invisible.

That difference is the useful shape of the rule. `__context__` answers
"what was the `except` block handling when `raise` ran," and Python
fills that attribute in whether you want it or not. `__cause__` answers
"what do you, the author, say explains this," and only `from` fills
that one in. `from None` sets `__suppress_context__`, hiding the
`__context__` answer, and leaves `__cause__` as `None`.

## 8. `read_text()` in place of the reading `with`

> Rewrite `context_manager.py`'s reading half using `path.read_text()`.
> Say what the `with` form gives you that the one-liner does not,
> and when that matters.

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
go, it is the better choice, and the chapter names `read_text()` and
`write_text()` for that case.

The `with` form gives you control over what happens between the open
and the close. Two things follow from that control. The `with` form
hands you the file object, so you can iterate lazily, line by line,
without the whole file in memory. `read_text()` builds one string of
the entire contents before you see any of it. The `with` form also
lets several operations share one open file, while each `read_text()`
call opens and closes the file again.

That control matters when the file is large enough that holding it
costs something, or when you are reading a stream that has no end.
The closing guarantee is not the difference: `read_text()` opens the
file in a `with` block of its own, so it closes the file too, whether
or not the read succeeds. For a configuration file of a few kilobytes
read once at startup, `read_text()` is the better choice.

## 9. Adjacent `2`s in `mutating_while_looping.py`

> In `mutating_while_looping.py`, change the list to `[2, 2, 1, 3]`,
> so a `2` sits in the first slot.
> Use the shifting-slots explanation to predict what the loop leaves in `scores`,
> then run it to check.

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
position 1 and finds `1`. The loop does not visit the survivor.

The prediction covers more than "one survives": it says which item
and where. The survivor is whatever slid into a slot the loop had
passed, so its final position depends on the data. In the chapter's
`[1, 2, 2, 3]` the survivor sits mid-list. Here it sits first. The
symptom moves with the input, and for that reason the chapter says to
build a new container instead of reasoning your way around the
mutation.
