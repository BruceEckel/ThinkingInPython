# Control Flow: Solutions

## 1. `find_factor(97)` and the loop's `else`

> In `loop_else.py`, call `find_factor(97)`.
> Predict whether the `for` loop's `else` clause runs before you check,
> then confirm.

<details>
<summary>Where to look</summary>

[The Loop `else` Clause](../../Chapters/04_Foundations--Control_Flow.md#the-loop-else-clause)
says when a `for` loop runs its `else`.
Ask whether any value of `d` reaches the `break` for 97.
The `else` depends on how the loop ends, not on what the body does.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
def find_factor(n):
    ...
```

<details>
<summary>Done when</summary>

you have written your prediction down, `find_factor(97)` prints `97 is prime`,
and you can say how the loop ended so that its `else` clause ran.

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

The loop tries every `d` from 2 up to 96, finds no factor,
and so runs to the end of its `range()` without reaching `break`.
A `for` loop's `else` clause runs when the loop ends that way,
so the `else` clause prints `97 is prime`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. Counting odd steps in the Collatz sequence

> Change `collatz_sequence()` in `while_loop.py` to also count how many times `n` is odd,
> and print that count alongside the step count.

<details>
<summary>Where to look</summary>

[Loops](../../Chapters/04_Foundations--Control_Flow.md#loops)
walks through `collatz_sequence()` in a `while` loop.
Add a second counter next to `steps`,
and increment it only in the branch that handles an odd `n`.
Return both counts together so the caller can print them side by side.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
def collatz_sequence(n):
    ...
```

<details>
<summary>Done when</summary>

your `exercise_2.py` prints the chapter's six values for `collatz_sequence(10)` and then `(6, 1)`,
with the step count first.
If you see `(6, 2)`, your count includes the `1` that ends the sequence.

<details>
<summary>Solution</summary>

If you keep the chapter's one-line conditional expression and add `if n % 2 == 1: odd_count += 1` after it,
the test sees the new `n`, not the value `n` held when the step began.
The count then includes the `1` that ends the sequence,
so `collatz_sequence(10)` returns `(6, 2)`.
The solution splits the conditional expression into an `if`/`else` statement.
The odd case then has a branch of its own,
where the increment runs under the same test that chooses `3 * n + 1`.

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

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[Loops](../../Chapters/04_Foundations--Control_Flow.md#loops)
shows `break` leaving the loop and `continue` skipping to the next iteration.
Compare the values of `n` that each `if` tests.
Ask whether any single `n` can satisfy both tests,
since that decides whether their order matters.

<details>
<summary>Done when</summary>

your prediction is written down,
the swapped `break_continue.py` prints `0 1 2 4 5`,
and you can say what a single value of `n` would have to do for the order of the two `if` blocks to change the output.

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

The output is the same as with the original order.
The two `if` blocks test for different values of `n` (`6` and `3`),
so at most one of them is true on any iteration.
Each block's outcome therefore stays the same whichever runs first.
Order matters only when one value satisfies both conditions and the two blocks do different things with it,
as when one ends the loop and the other skips to the next iteration.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 4. An exception that escapes the handler

> In `demonstrate_exceptions.py`, add a call `divide_and_report(1, "x")`
> (the division raises a `TypeError`, which `except ValueError` lets through).
> Run it and read the traceback that escapes.

<details>
<summary>Where to look</summary>

[Errors and Exceptions](../../Chapters/04_Foundations--Control_Flow.md#errors-and-exceptions)
shows how `except` selects which exception types it catches,
and when `finally` and `else` run.
Trace which clauses run when the exception type matches none of the `except` clauses.
To show the exception reaching the caller in a listing,
wrap the call in a `try` that specifies the exception type.

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
<summary>Done when</summary>

your run prints `finally always runs`,
then a traceback ending in `TypeError: unsupported operand type(s) for /: 'int' and 'str'`,
with neither `caught:` nor `no exception` in the output.
You can follow the traceback from your call down to the `/` in `checked_divide()`.

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

**Let an unmatched exception through.**
`divide_and_report(1, "x")` raises a `TypeError` inside `checked_divide()`,
because Python cannot divide an `int` by a `str`.
The `except` clause specifies `ValueError`,
so the `TypeError` propagates past it.
The `finally` block still runs,
since `finally` runs whether or not an exception is propagating.
The `else` clause runs only when the `try` block finishes without an exception,
so the `TypeError` bypasses the `else` clause too.

**Catch the exception at the caller.**
Because the `TypeError` propagates up past `divide_and_report()`,
this listing wraps the call in its own `try`/`except TypeError` to show the exception reaching the caller.
If you call `divide_and_report(1, "x")` at the top level instead,
`finally always runs` prints first, and then the traceback appears,
ending in `TypeError: unsupported operand type(s) for /: 'int' and 'str'`.
Above that last line,
the traceback lists the calls the exception passed on its way out,
from your call at the top down to the `/` in `checked_divide()`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 5. A three-item `case` in `pattern_matching.py`

> In `pattern_matching.py`,
> add a `case ["go", direction, distance]` that reports both parts,
> and check what `run("go north 3")` returns before and after you add it.

<details>
<summary>Where to look</summary>

[Pattern Matching](../../Chapters/04_Foundations--Control_Flow.md#pattern-matching)
shows sequence patterns matching a split command.
A list pattern matches only a sequence of its own length,
so count the items in `"go north 3"` against each existing `case`.
Put the three-item pattern where Python tries it before any `case` that also matches a three-item list,
and bind `direction` and `distance` by name.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
def run(command):
    ...
```

<details>
<summary>Done when</summary>

the file runs without a `SyntaxError`,
`run("go north 3")` returns `unknown command` before your change and a string holding both `north` and `3` after it,
and `run("go north")` still returns `moving north`.

<details>
<summary>Solution</summary>

If you add the new `case` at the bottom of the `match`, below `case _`,
Python rejects the file before running any of it:
`SyntaxError: wildcard makes remaining patterns unreachable`.
A wildcard matches every value,
so it takes every input before a later `case` sees it.
Python treats that unreachable `case` as an error rather than as dead code.
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

**Give the longer command a case.**
Before the new `case` exists, `run("go north 3")` returns `unknown command`.
A list pattern matches on length as well as content,
so `["go", direction]` matches only a list of two items.
The three-item split matches neither list pattern and reaches `case _`.

**Arrange the patterns.**
Order matters only between patterns that could both match the same value.
The two `go` patterns match lists of different lengths,
so either arrangement works here.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. The comprehension written as a loop

> Rewrite the `evens` list comprehension in `comprehensions_intro.py` as a `for` loop that appends to a list,
> then say which version you would rather read six months from now.

<details>
<summary>Where to look</summary>

[Comprehensions](../../Chapters/04_Foundations--Control_Flow.md#comprehensions)
introduces the list comprehension with a filter.
Start from an empty list, loop over `range()`, test the condition with an `if`,
and call `append()`.
Then compare what each version tells the reader about the finished list.

<details>
<summary>Done when</summary>

your loop version prints `[0, 2, 4, 6, 8]`,
the same list the comprehension prints,
and your preference comes with a reason you can point to in the two versions of the code.

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

The loop takes four lines instead of one.
Until it finishes, the name `evens` holds a partial result.
The comprehension states the contents of the list.
The loop says how to build it,
so the reader traces the loop to learn the contents.
For `evens`, the comprehension is the easier read six months from now.

The loop version is a better choice when the body grows past one condition and one expression,
since a comprehension with two filters and a nested loop is harder to read than the nested `for` loops it replaces.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 7. Chaining from an exception you build yourself

> In `exception_chaining.py`,
> add a fourth function that catches the `ValueError` and raises `BadNumber` from a new exception object it constructs,
> rather than from the caught `ValueError`.
> Predict which line the traceback shows above `BadNumber` before you run it.

<details>
<summary>Where to look</summary>

[Exception Chaining](../../Chapters/04_Foundations--Control_Flow.md#exception-chaining)
covers `raise ... from` and the `__cause__` and `__context__` attributes.
The expression after `from` can be any exception object,
including one the `raise` statement constructs.
Predict the joining line from `__cause__`,
then print both attributes to see which exception each one holds.

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
<summary>Done when</summary>

your prediction is written down,
the traceback shows `The above exception was the direct cause of the following exception:` above `BadNumber`,
and printing the classes of `e.__cause__` and `e.__context__` names two different exceptions:
the one you constructed and `ValueError`.

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

**Chain from a constructed cause.**
The prediction is the "direct cause" line, the same one `explicit()` produces.
`from` sets `__cause__` to the object that follows it.
When `__cause__` holds an exception,
Python joins the two tracebacks with the "direct cause" line that `joining_line()` finds.
An exception constructed in the `raise` statement joins the report the same way a caught one does.
`from` accepts any expression that produces an exception.
A name bound by `except` is one such expression.

**Compare the cause with the context.**
At `[1]`, `__cause__` is the `ArithmeticError` you supplied,
and `__context__` is still the `ValueError` Python recorded on its own when `raise` ran inside a handler.
The traceback reports the cause when one exists,
so the context stays in its attribute and out of the report.

`__context__` answers "what was the `except` block handling when `raise` ran,"
and Python fills that attribute in automatically.
`__cause__` answers "what do you, the author, say explains this,"
and `from` alone fills that one in.
`from None` leaves `__cause__` as `None` and sets `__suppress_context__`,
so the traceback omits the `__context__` exception.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 8. `read_text()` in place of the reading `with`

> Rewrite `context_manager.py`'s reading half using `path.read_text()`.
> Say what the `with` form gives you that the one-liner does not,
> and when that matters.

<details>
<summary>Where to look</summary>

[Context Managers](../../Chapters/04_Foundations--Control_Flow.md#context-managers)
explains what the `with` block does on entry and exit,
and names `read_text()` and `write_text()` for reading or writing a whole file in one call.
Call `read_text()` on the `Path` and split the result into lines.
To compare the two forms,
consider what the file object lets you do between the open and the close.

<details>
<summary>Done when</summary>

your rewritten reading half prints `one` and `two`,
as the chapter's version does,
and you can name one thing the open file object lets you do between the open and the close,
plus a kind of file where that matters.

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

`read_text()` opens the file, reads all of it, and closes it,
so one call does the work of the whole `with` block.
For a small file read in one go, the one-liner is the better choice.
The chapter names `read_text()` and `write_text()` for that case.

The `with` form gives you control over the code between the open and the close.
Two things follow from that control.
The `with` form binds the file object to `f`, so you can iterate over it lazily,
holding one line in memory at a time.
`read_text()` builds one string of the entire contents before you see any of it.
The `with` form also lets several operations share one open file,
while each `read_text()` call opens and closes the file again.

That control matters when the file is too large to hold in memory as one string,
or when you read a stream that has no end.

Both forms guarantee the close.
`read_text()` opens the file in a `with` block of its own,
so it closes the file whether the read succeeds or raises an exception.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 9. Adjacent `2`s in `mutating_while_looping.py`

> In `mutating_while_looping.py`, change the list to `[2, 2, 1, 3]`,
> so a `2` sits in the first slot.
> Use the shifting-slots explanation in [Two List Traps](../../Chapters/03_Foundations--Containers.md#two-list-traps)
> to predict what the loop leaves in `scores`, then run it to check.

<details>
<summary>Where to look</summary>

[Mutating a Container While Looping](../../Chapters/04_Foundations--Control_Flow.md#mutating-a-container-while-looping)
explains how `remove()` shifts later items into slots the loop has passed.
Walk the loop by index over `[2, 2, 1, 3]`,
noting which item `remove()` deletes and which item moves into the current position.
Then predict the final list before you run it.

<details>
<summary>Done when</summary>

your prediction is written down, the run prints `[2, 1, 3]`,
and you can say which slot the surviving `2` occupies and why the loop skipped it.

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

One `2` survives again, but this time at the front.
At position 0 the loop sees `2` and `remove()` deletes the first equal item,
which is that same position-0 element.
The second `2` shifts down into slot 0, which the loop has passed,
so the next iteration looks at position 1 and finds `1`.

The prediction covers more than "one survives."
It says which item and where.
The survivor is the item that shifts into a slot the loop has passed,
so its final position depends on the data.
In the chapter's `[1, 2, 2, 3]` the survivor sits mid-list.
Here it sits first.
A prediction of each shifted item's new position therefore holds for one list at a time.

The chapter's three fixes hold for every list.
Each one keeps the list the loop walks as it was, so the loop sees every item.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 10. Strings `isdigit()` rejects and `int()` accepts

> In `eafp.py`, predict what `look_first()` and `int()` each return for `" 42 "`
> (with a space on each side) and for `"4_2"`, then run both.
> Say what the results tell you about adding more tests to `look_first()`.

<details>
<summary>Where to look</summary>

[Ask Forgiveness, Not Permission](../../Chapters/04_Foundations--Control_Flow.md#ask-forgiveness-not-permission)
shows `isdigit()` and `int()` disagreeing on `"-5"` and `"²"`.
`isdigit()` tests each character on its own,
while `int()` reads the whole string as a number,
so ask which characters besides digits a number can carry.
For each string, ask whether `look_first()` would need a new test to agree with `int()`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_10.py
def look_first(text):
    ...
```

<details>
<summary>Done when</summary>

your four predictions match the run,
where `look_first()` returns `None` for both strings,
while `int()` returns `42` for both,
and you can name the test `look_first()` would need for each string and say why `parse_int()` needs none.

<details>
<summary>Solution</summary>

```python
# exercise_10.py
def look_first(text):
    if text.isdigit():
        return int(text)
    return None

for text in (" 42 ", "4_2"):
    print(repr(text), look_first(text), int(text))
#: ' 42 ' None 42
#: '4_2' None 42
```

`int()` strips surrounding whitespace,
and it allows an underscore between digits,
the same rule that makes `10_000_000` a valid literal.
`isdigit()` asks whether every character is a digit,
so the spaces and the underscore each fail it.

Each new disagreement calls for another test in `look_first()`: one for a sign,
one for whitespace, one for underscores, and one to reject `"²"`.
Those tests together are a second parser,
written to predict what `int()` will do.
That parser is right only where it repeats `int()`'s rules.
`parse_int()` calls `int()` and catches the `ValueError`,
so it agrees with `int()` on every string, including strings you have not tried.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
