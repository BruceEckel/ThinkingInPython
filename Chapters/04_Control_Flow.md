# Control Flow

Control-flow statements decide which code runs and how often.
This chapter covers conditionals, placeholders, loops, pattern matching,
exceptions, the `with` statement, and comprehensions.

## Conditionals

[Tour](02_Tour.md#indentation-and-blocks) showed the basic `if`, its colon,
and its indented block.
Python's comparison operators chain the way they do in mathematics:

```python
# chaining.py

x = 5
print(0 < x < 10)  # Chained comparison
#: True
grade = "ok" if x >= 3 else "low"  # Conditional expression
print(grade)
#: ok
```

The example also shows a *conditional expression*:
a one-line `if`/`else` that produces a value.

Adding `elif` to an `if` statement tests several conditions in order:

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

## Placeholders: `pass` and `...` {#placeholders}

The `pass` statement does nothing.
Use it where Python's syntax requires a statement but you have none to run yet.

`...` (the *Ellipsis* literal) is a second placeholder.
Using it alone as a statement does nothing, the same as `pass`:

```python
# placeholders.py

def not_implemented():
    pass  # Fill in later

def not_implemented_yet():
    ...

print(not_implemented(), not_implemented_yet())
#: None None
```

`pass` marks an indented block with nothing in it yet.
`...` is the conventional body for a stub whose implementation lives elsewhere.
You normally write it on the same line as the signature it stubs,
as in a `Protocol` method
([Static Typing](08_Static_Typing.md#structural-typing-with-protocols) uses this).

## Loops

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
        continue  # Skip the rest of this iteration
    if n == 6:
        break  # Leave the loop
    print(n, end=" ")
print()  # The newline that end=" " left off
#: 0 1 2 4 5
```

The loop prints `0 1 2`, skips `3` with `continue`, prints `4 5`,
then stops at `6` with `break`, so `6` through `9` never print.
Both apply to the innermost enclosing loop.
Python has no labeled `break`, so leaving two loops at once means either a flag,
a `return` from a function that holds both loops, or the loop `else` below.

`print()` ends with a newline by default.
`end=" "` replaces that newline with a space, so the numbers print on one line,
and a bare `print()` emits the missing newline afterward.

Python has no `do`/`while` statement.
When the test belongs at the bottom of the body rather than the top,
write `while True:` and `break` out:

```python
# while_true.py

values = [3, 5, 0, 7]
total = 0
while True:
    value = values.pop(0)
    if value == 0:
        break
    total += value
print(total)
#: 8
```

A loop may have an `else` clause.
It runs only if the loop finishes without hitting `break`,
which makes it natural for search loops:

```python
# loop_else.py

def find_factor(n):
    for d in range(2, n):
        if n % d == 0:
            print(f"{n} = {d} * {n // d}")
            break
    else:
        # No break means no factor found
        print(f"{n} is prime")

find_factor(15)
#: 15 = 3 * 5
find_factor(13)
#: 13 is prime
```

The `else` belongs to the `for`, not the `if`.
A `while` loop can use `else` the same way.
This `else` is also how you leave two nested loops at once:
put `continue` in the inner loop's `else` and a `break` right after it.
When the inner loop `break`s,
Python skips its `else` and the outer `break` runs.
When it finishes clean, the `continue` moves the outer loop along instead.

`for` walks any iterable directly.
A list, a set, a dictionary, or a string needs no index.
Use `range()` for counting and `enumerate()` when you also need the index:

```python
# looping.py

for i in range(3):
    print(i, end=" ")
print()
#: 0 1 2
names = ["Alice", "Bob", "Carol", "Ted"]
for index, name in enumerate(names):
    print(index, name)
#: 0 Alice
#: 1 Bob
#: 2 Carol
#: 3 Ted
```

`enumerate()` yields `(index, item)` pairs counting from zero,
which the loop here unpacks into `index` and `name`.
Writing `for i in range(len(names)):` and then indexing `names[i]` does the same job,
but that form names the index and looks the item up again on every line that needs it.
`enumerate()` hands you both.
`zip()` walks several sequences at once:

```python
# zipping.py

names = ["Alice", "Bob", "Carol", "Ted"]
scores = [88, 91, 79, 54, 99]  # One score too many
for name, score in zip(names, scores):
    print(name, score)
#: Alice 88
#: Bob 91
#: Carol 79
#: Ted 54
try:
    list(zip(names, scores, strict=True))
except ValueError as e:
    print(e)
#: zip() argument 2 is longer than argument 1
```

`zip()` produces one item from each sequence and stops when the shortest runs out,
so the extra score never appears.
That silence is convenient when the lengths differ on purpose and a bug when you expect them to match.
`strict=True` raises a `ValueError` on the mismatch instead.
When you need the index as well, wrap the whole thing.
The extra nesting shows up in the loop header,
which needs parentheses around the inner pair:
`for i, (name, score) in enumerate(zip(names, scores)):`.

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
stack = ["a", "b", "c"]
while stack and (item := stack.pop()) != "a":
    print("processing", item)
#: processing c
#: processing b
```

The `while` loop is where this pays off.
It pops a value, names it, and tests it in one place,
so the body needs no second pop and no separate copy.
It also collapses `while_true.py` into its loop header:
`while (value := values.pop(0)) != 0:`.
A comprehension can use `:=` the same way,
which [Comprehensions](16_Comprehensions.md) covers.

Changing a container while a `for` loop walks it is the classic control-flow bug,
and the two containers you are most likely to mutate this way behave differently:

```python
# mutating_while_looping.py

scores = [1, 2, 2, 3]
for s in scores:
    if s == 2:
        scores.remove(s)
print(scores)
#: [1, 2, 3]
print([s for s in [1, 2, 2, 3] if s != 2])
#: [1, 3]
ages = {"a": 1, "b": 2}
try:
    for name in ages:
        ages[name + "!"] = 0
except RuntimeError as e:
    print(e)
#: dictionary changed size during iteration
```

The list loop walks by position.
Removing an item shifts the next one down into the slot the loop already passed,
so the loop skips it and one of the two `2`s survives,
with no exception to tell you.
The dictionary refuses outright instead of skipping silently.
Neither behavior calls for a workaround:
build a new container with a comprehension,
or collect what to remove first and remove it after the loop.

## Pattern Matching

The `match` statement compares a value against structural patterns.
It resembles a C `switch`,
but a pattern can look inside a value and pull out its parts:

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

Only the first matching `case` runs.
Unlike C, a `case` does not fall through, so it needs no `break`.
The first `case` destructures the split command:
it matches a two-item list starting with `"go"` and binds the second item to `direction`.
A bare name in a `case` captures rather than compares:
`case direction:` binds anything to `direction` and matches every value.
Write a constant as a literal (`case "quit":`) or as a dotted name
(`case Command.QUIT:`).

`match` and `case` are *soft keywords*:
they are keywords only in this statement,
so existing code that uses `match` as a variable name still runs.
Avoid the name, though: a reader must work out which meaning applies.
[Pattern Matching](13_Pattern_Matching.md) covers `match` in detail.

## Errors and Exceptions

Python signals an error by *raising* an exception.
As in C++ and Java, an exception propagates up the call stack until it finds a handler.
One that finds none stops the program and prints the traceback.
In Python, a handler is `except` followed by the exception type it handles.
You can give only the type, or add an `as` to capture the exception object,
as in `except ValueError as e`:

```python
# demonstrate_exceptions.py

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

def divide_and_report(a, b):
    try:
        checked_divide(a, b)
    except ValueError as e:
        print("caught:", e)
    else:
        print("no exception")
    finally:
        print("finally always runs")

divide_and_report(1, 0)
#: caught: Divide by zero
#: finally always runs
divide_and_report(1, 1)
#: no exception
#: finally always runs
```

`checked_divide()` raises a `ValueError` rather than letting Python's own `ZeroDivisionError` through,
which you do when the caller should hear about the bad argument,
not the failed arithmetic.

The optional `else` runs when the `try` block raises no exception,
the same shape as the loop `else` that runs when the loop hits no `break`.
The optional `finally` always runs, which makes it the place for cleanup.

Catch an exception only when you can do something about it.
A bare `except:` with no type catches everything,
including the `KeyboardInterrupt` you press to stop a runaway program,
so a mistake in the `try` block looks like an expected failure.
`except Exception:` is the broad catch you want instead:
`KeyboardInterrupt` and `SystemExit` derive from `BaseException` rather than `Exception`,
so they travel past it and still stop the program.
To handle several types the same way, give a tuple:
`except (ValueError, TypeError) as e:`.
Python tries the `except` clauses in order and runs the first whose type matches,
so a broad clause above a narrow one makes the narrow one unreachable.
Order them most specific first.
To log an exception and still let it propagate, re-raise it with a bare `raise`.

An exception raised while handling another one arrives with the first attached.
Python reports both, and `from` decides how the two connect:

| Form | What Python prints above the new exception |
|---|---|
| `raise X` | During handling of the above exception, another exception occurred: |
| `raise X from e` | The above exception was the direct cause of the following exception: |
| `raise X from None` | Nothing: only `X` appears |

All three raise the same exception and differ only in that report:

```python
# exception_chaining.py
import textwrap
import traceback

class BadNumber(Exception):
    pass

def implicit(text):
    try:
        return int(text)
    except ValueError:
        raise BadNumber(text)

def explicit(text):
    try:
        return int(text)
    except ValueError as e:
        raise BadNumber(text) from e

def suppressed(text):
    try:
        return int(text)
    except ValueError:
        raise BadNumber(text) from None

def joining_line(e):
    for part in traceback.format_exception(e):
        line = part.strip()
        if (line.endswith("exception occurred:")
            or line.endswith("following exception:")):
            return line
    return "nothing shown above it"

for parse in (implicit, explicit, suppressed):
    try:
        parse("seven")
    except BadNumber as e:
        print(f"{parse.__name__}:")
        for chunk in textwrap.wrap(joining_line(e), 55):
            print(" ", chunk)
#: implicit:
#:   During handling of the above exception, another
#:   exception occurred:
#: explicit:
#:   The above exception was the direct cause of the
#:   following exception:
#: suppressed:
#:   nothing shown above it
```

`BadNumber` is a custom exception type,
which you create by deriving a class from `Exception`.
Its body is `pass` because it needs no behavior of its own.
The handler matches on the class name.
[Classes](07_Classes.md) covers class definitions in full.

`joining_line()` digs the joining sentence out of the formatted traceback,
so the output above is the text Python would print, not a summary of it.
`from e` sets `__cause__` and produces the "direct cause" line.
With no `from`, Python still records the earlier exception in `__context__` and produces the "During handling" line.
`from None` sets `__suppress_context__`,
and nothing appears above the new exception.
Use `from e` when the earlier exception explains this one,
and `from None` when it would only distract from your own message.

Python's culture leans on "easier to ask forgiveness than permission,"
abbreviated EAFP.
Try the operation and handle the exception,
rather than checking every precondition first.
The opposite style, "look before you leap" (LBYL), tests first,
and it breaks whenever the test and the operation disagree:

```python
# eafp.py

def careful(text):
    if text.isdigit():
        return int(text)
    return None

def forgiving(text):
    try:
        return int(text)
    except ValueError:
        return None

print(careful("-5"), forgiving("-5"))
#: None -5
try:
    careful("\N{SUPERSCRIPT TWO}")
except ValueError as e:
    print("careful:", e)
#: careful: invalid literal for int() with base 10: '²'
print(forgiving("\N{SUPERSCRIPT TWO}"))
#: None
```

`isdigit()` and `int()` disagree in both directions.
`isdigit()` rejects `"-5"`, which `int()` converts fine, and it accepts `"²"`,
which `int()` refuses.
The `try` block asks the only question that matters: does this conversion work?
The gap grows when the world can change between test and operation:
a file that exists at the `if` can disappear before the `open()`,
and only the EAFP form is safe against that.

## Context Managers

A `with` block guarantees that setup and cleanup run as a pair,
even if the body raises an exception.
Opening a file is the canonical case.
The `with` block always closes the file on exit:

```python
# context_manager.py
import tempfile
from pathlib import Path

path = Path(tempfile.gettempdir()) / "demo.txt"
with path.open("w") as f:
    f.write("one\ntwo\n")  # Automatic f.close()

with path.open() as f:
    for line in f:
        print(line.strip())
#: one
#: two
try:
    with path.open("w") as f:
        f.write("partial")
        raise RuntimeError("failed midway")
except RuntimeError as e:
    print(e)
#: failed midway
print("closed:", f.closed)
#: closed: True
path.unlink()  # Delete the file
```

The exception propagates, but the `with` closes the file first.
`f` is still in scope afterward, which is how the listing can check it.
The `with` statement does not create a scope, only a guarantee about the exit.

Closing the file is cleanup that runs whether or not the block succeeds.
[Cleanup](10_Cleanup.md)
contrasts this with letting Python's garbage collector do it.
Anything that acquires a resource (a file, a lock, a network connection)
can be a context manager.
[Context Managers](15_Context_Managers.md) shows how to write your own.
For reading or writing a file,
`pathlib` provides methods like `read_text()` and `write_text()` that open and close the file.

## Comprehensions

A *comprehension* builds a list, dictionary,
or set from another sequence in one expression,
replacing a loop that builds up a result:

```python
# comprehensions_intro.py

squares = [n * n for n in range(5)]  # List comprehension
print(squares)
#: [0, 1, 4, 9, 16]
# With a filter
evens = [n for n in range(10) if n % 2 == 0]
print(evens)
#: [0, 2, 4, 6, 8]
# Dict comprehension
lengths = {w: len(w) for w in ["a", "bb"]}
print(lengths)
#: {'a': 1, 'bb': 2}
parities = {n % 2 for n in range(10)}  # Set comprehension
print(parities)
#: {0, 1}
```

[Comprehensions](16_Comprehensions.md#list-comprehensions)
covers the topic in detail,
as well as generator expressions and the functional tools `map()` and `filter()`.

## Exercises

1.  In `loop_else.py`, call `find_factor(97)`.
    Predict whether the `for` loop's `else` clause runs before you check,
    then confirm.
2.  Change `collatz_sequence()` in `while_loop.py` to also count how many times `n` is odd,
    and print that count alongside the step count.
3.  In `break_continue.py`, swap the order of the two `if` blocks,
    so the `n == 6` `break` check comes first and the `n == 3` `continue` check comes second.
    Predict whether the output changes before running it,
    then explain what you find.
4.  In `demonstrate_exceptions.py`, add a call `divide_and_report(1, "x")`
    (a `TypeError` that `except ValueError` does not catch).
    Run it and read the traceback that escapes.
5.  In `pattern_matching.py`,
    add a `case ["go", direction, distance]` that reports both parts,
    and check what `run("go north 3")` returns before and after you add it.
6.  Rewrite the `evens` list comprehension in `comprehensions_intro.py` as a `for` loop that appends to a list,
    then say which version you would rather read six months from now.
7.  In `exception_chaining.py`,
    add a fourth function that catches the `ValueError` and raises `BadNumber` from a *different* exception object it constructs.
    Predict which line `joining_line()` prints before you run it.
8.  Rewrite `context_manager.py`'s reading half using `path.read_text()`.
    Say what the `with` form gives you that the one-liner does not,
    and when that matters.
9.  In `mutating_while_looping.py`, change the list to `[2, 2, 1, 3]`,
    so a `2` sits in the first slot.
    Use the shifting-slots explanation to predict what the loop leaves in `scores`,
    then run it to check.
