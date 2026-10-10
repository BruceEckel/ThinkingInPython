# Control Flow: Solutions

## 1. `find_factor(97)` and the loop's `else`

> In `loop_else.py`, call `find_factor(97)`.
> Predict whether the `for` loop's `else` clause runs before you check,
> then confirm.

<details>
<summary>Where to look</summary>

[The Loop `else` Clause](../../Chapters/04_Foundations--Control_Flow.md#the-loop-else-clause) says when a `for` loop runs its `else`.
Ask whether any value of `d` reaches the `break` for 97.
The `else` depends on how the loop ended, not on what the body did.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
def find_factor(n):
    ...
```

<details>
<summary>Solution</summary>

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

</details>
</details>
</details>

## 2. Counting odd steps in the Collatz sequence

> Change `collatz_sequence()` in `while_loop.py` to also count how many times `n` is odd,
> and print that count alongside the step count.

<details>
<summary>Where to look</summary>

[Loops](../../Chapters/04_Foundations--Control_Flow.md#loops) walks through `collatz_sequence()` in a `while` loop.
Add a second counter next to `steps`, and increment it only in the branch that handles an odd `n`.
Return both counts together so the caller can print them side by side.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
def collatz_sequence(n):
    ...
```

<details>
<summary>Solution</summary>

If you keep the chapter's one-line conditional expression and add `if n % 2 == 1: odd_count += 1` after it,
the test sees the new `n`, not the value `n` held when the step began.
The count then includes the `1` that ends the sequence, and `collatz_sequence(10)` returns `(6, 2)`.
The solution splits the conditional expression into an `if`/`else` statement,
so the odd case has a branch of its own and the count shares the test that chooses `3 * n + 1`.

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

</details>
</details>
</details>

## 3. Swapped order of `continue` and `break`

> In `break_continue.py`, swap the order of the two `if` blocks,
> so the `n == 6` `break` check comes first and the `n == 3` `continue` check comes second.
> Predict whether the output changes before running it,
> then explain what you find.

<details>
<summary>Where to look</summary>

[Loops](../../Chapters/04_Foundations--Control_Flow.md#loops) shows `break` leaving the loop and `continue` skipping to the next iteration.
Compare the values of `n` that each `if` tests.
Ask whether any single `n` can satisfy both tests, since that decides whether their order matters.

<details>
<summary>Solution</summary>

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

</details>
</details>

## 4. An exception that escapes the handler

> In `demonstrate_exceptions.py`, add a call `divide_and_report(1, "x")`
> (a `TypeError` that `except ValueError` does not catch).
> Run it and read the traceback that escapes.

<details>
<summary>Where to look</summary>

[Errors and Exceptions](../../Chapters/04_Foundations--Control_Flow.md#errors-and-exceptions) shows how `except` selects which exception types it catches, and when `finally` and `else` run.
Trace which clauses run when the exception type matches none of the `except` clauses.
To see the escape in a listing, wrap the call in a `try` that names the exception type.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
def checked_divide(a, b):
    ...

def divide_and_report(a, b):
    ...
```

<details>
<summary>Solution</summary>

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

**Let an unmatched exception through.** `divide_and_report(1, "x")`
raises `TypeError` inside `checked_divide()`, because Python cannot
divide an `int` by a `str`. The `except` clause names
`ValueError`, so the `TypeError` passes it by. The `finally` block
still runs. `finally` runs whatever kind of exception is in flight.
The `else` clause does not run here. It belongs to the case where the
`try` block finishes cleanly.

**Catch the escape at the caller.** The `TypeError` keeps
propagating up past `divide_and_report()`, so this listing wraps the
call in its own `try`/`except TypeError` to show the exception
escaping. An interactive session or an outer caller sees the
`TypeError` escape the same way.

</details>
</details>
</details>

## 5. A three-item `case` in `pattern_matching.py`

> In `pattern_matching.py`,
> add a `case ["go", direction, distance]` that reports both parts,
> and check what `run("go north 3")` returns before and after you add it.

<details>
<summary>Where to look</summary>

[Pattern Matching](../../Chapters/04_Foundations--Control_Flow.md#pattern-matching) shows sequence patterns matching a split command.
A list pattern matches only a sequence of its own length, so count the items in `"go north 3"` against each existing `case`.
Put the three-item pattern where it cannot shadow another, and bind `direction` and `distance` by name.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
def run(command):
    ...
```

<details>
<summary>Solution</summary>

If you add the new `case` at the bottom of the `match`, below `case _`,
Python rejects the file before running any of it:
`SyntaxError: wildcard makes remaining patterns unreachable`.
A wildcard matches every value, so no `case` after it could run,
and Python treats that as an error rather than as dead code.
The solution puts the three-item pattern first, above the wildcard.

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

**Give the longer command a case.** Before the new `case` exists, `run("go north 3")` returns `unknown
command`. A list pattern matches on length as well as content, so
`["go", direction]` matches only a list of two items. The three-item
split matches neither of the original patterns and reaches `case _`.
The longer pattern gives a three-item list a `case` of its own.

**Arrange the patterns.** Order
matters only between patterns that could both match the same value.
The two `go` patterns cannot, so either arrangement works here.

</details>
</details>
</details>

## 6. The comprehension written as a loop

> Rewrite the `evens` list comprehension in `comprehensions_intro.py` as a `for` loop that appends to a list,
> then say which version you would rather read six months from now.

<details>
<summary>Where to look</summary>

[Comprehensions](../../Chapters/04_Foundations--Control_Flow.md#comprehensions) introduces the list comprehension with a filter.
Start from an empty list, loop over `range()`, test the condition with an `if`, and call `append()`.
Then compare what each version tells the reader about the finished list.

<details>
<summary>Solution</summary>

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
with two filters and a nested loop is harder to read than the nested `for`
loops it replaces.

</details>
</details>

## 7. Chaining from an exception you build yourself

> In `exception_chaining.py`,
> add a fourth function that catches the `ValueError` and raises `BadNumber` from a *different* exception object it constructs.
> Predict which line `joining_line()` prints before you run it.

<details>
<summary>Where to look</summary>

[Exception Chaining](../../Chapters/04_Foundations--Control_Flow.md#exception-chaining) covers `raise ... from` and the `__cause__` and `__context__` attributes.
The expression after `from` can be any exception object, including one the `raise` statement constructs.
Predict the joining line from `__cause__`, then print both attributes to see which exception each one holds.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
import textwrap
import traceback

class BadNumber(Exception):
    pass

def substituted(text):
    ...

def joining_line(e):
    ...
```

<details>
<summary>Solution</summary>

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
    print(type(e.__cause__).__name__,  # [1]
          type(e.__context__).__name__)
#:   The above exception was the direct cause of the
#:   following exception:
#: ArithmeticError ValueError
```

**Chain from a constructed cause.** The prediction is the "direct cause" line, the same one `explicit()`
produces. `from` sets `__cause__` to whatever object follows it, and
Python builds the traceback that `joining_line()` searches from
`__cause__`. An exception constructed in the `raise` statement joins the
report the same way a caught one does. `from` takes an expression, not a name
bound by `except`.

**Compare the cause with the context.** The second `print()` (`[1]`)
shows that both attributes hold an exception, and different ones.
`__cause__` is the `ArithmeticError` you supplied, and `__context__`
is still the `ValueError` Python recorded on its own when `raise` ran
inside a handler. Python reports the cause when one exists, so the
context is present but invisible.

`__context__` answers "what was the `except` block handling when
`raise` ran," and Python fills that attribute in whether you want it
or not. `__cause__` answers "what do you, the author, say explains
this," and `from` alone fills that one in. `from None` sets
`__suppress_context__`, hiding the `__context__` answer, and leaves
`__cause__` as `None`.

</details>
</details>
</details>

## 8. `read_text()` in place of the reading `with`

> Rewrite `context_manager.py`'s reading half using `path.read_text()`.
> Say what the `with` form gives you that the one-liner does not,
> and when that matters.

<details>
<summary>Where to look</summary>

[Context Managers](../../Chapters/04_Foundations--Control_Flow.md#context-managers) explains what the `with` block does on entry and exit, and names `read_text()` and `write_text()` for reading or writing a whole file in one call.
Call `read_text()` on the `Path` and split the result into lines.
To compare the two forms, consider what the file object lets you do between the open and the close.

<details>
<summary>Solution</summary>

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
go, the one-liner is a better choice, and the chapter names `read_text()` and
`write_text()` for that case.

The `with` form gives you control over the code between the open and
the close. Two things follow from that control. The `with` form hands
you the file object, so you can iterate over it lazily, line by line,
without the whole file in memory. `read_text()` builds one string of
the entire contents before you see any of it. The `with` form also
lets several operations share one open file, while each `read_text()`
call opens and closes the file again.

That control matters when the file is large enough that holding all
of it strains memory, or when you read a stream that has no end.

The closing guarantee is not the difference. `read_text()` opens the
file in a `with` block of its own, so it closes the file too, whether
or not the read succeeds. For a configuration file of a few kilobytes
read once at startup, `read_text()` is a better choice.

</details>
</details>

## 9. Adjacent `2`s in `mutating_while_looping.py`

> In `mutating_while_looping.py`, change the list to `[2, 2, 1, 3]`,
> so a `2` sits in the first slot.
> Use the shifting-slots explanation to predict what the loop leaves in `scores`,
> then run it to check.

<details>
<summary>Where to look</summary>

[Mutating a Container While Looping](../../Chapters/04_Foundations--Control_Flow.md#mutating-a-container-while-looping) explains how `remove()` shifts later items into slots the loop has passed.
Walk the loop by index over `[2, 2, 1, 3]`, noting which item `remove()` deletes and which item moves into the current position.
Then predict the final list before you run it.

<details>
<summary>Solution</summary>

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
which the loop has passed, so the next iteration looks at position 1
and finds `1`. The loop does not visit the survivor.

The prediction covers more than "one survives." It says which item
and where. The survivor is whatever slides into a slot the loop has
passed, so its final position depends on the data. In the chapter's
`[1, 2, 2, 3]` the survivor sits mid-list. Here it sits first. The
symptom moves with the input, and for that reason the chapter says to
build a new container instead of reasoning your way around the
mutation.

</details>
</details>
