# Control Flow

> Conditionals and loops read the same in Python as in the language you know.
> Recovery from failure is the part that reads differently.

In C++ and Java the careful move is to test before you act:
check that the string parses, that the file is there, that the key exists.
Python goes the other way.
Run the operation and catch the exception when it fails.
The test and the operation can disagree, and the world can change between them.
Exceptions are ordinary control flow here, not a last resort.
This chapter covers them along with conditionals, placeholders, loops,
pattern matching, the `with` statement, and comprehensions.

## Conditionals

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

`0 < x < 10` means `0 < x and x < 10`,
except that Python evaluates the middle operand once.
A C or C++ compiler reads the same expression as `(0 < x) < 10`,
which compares a `0` or `1` against `10`, so it is always true.
Java rejects the expression at compile time.

The example also shows a *conditional expression*:
a one-line `if`/`else` that produces a value.
It does the job of the `?:` operator in C++ and Java,
with the condition in the middle: first the value when the test is true,
then `if` and the test, then `else` and the value when the test is false.

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
On its own as a statement it does nothing, the same as `pass`:

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
as in a [`Protocol`](08_Foundations--Static_Types.md#structural-typing-with-protocols)
method.

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

`print()` ends with a newline by default.
`end=" "` replaces that newline with a space, so the numbers print on one line,
and a bare `print()` emits the missing newline afterward.

`break` and `continue` both apply to the innermost enclosing loop.
Python has no labeled `break`, so leaving two loops at once means either a flag,
a `return` from a function that holds both loops,
or the loop `else` technique that `nested_break.py` shows below.

Python has no `do`/`while` statement.
When the test belongs in the middle or at the bottom of the body,
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

The loop must fetch a value before it can test it,
so the test sits between the `pop()` and the addition.

### The Loop `else` Clause

A loop may have an `else` clause.
It runs when the loop finishes with no `break`,
and that makes it natural for search loops:

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

The loop `else` is also how you leave two nested loops at once.
Put `continue` in the inner loop's `else`, and a `break` after the inner loop,
at the outer loop's level.
When the inner loop `break`s,
Python skips its `else` and the outer `break` runs.
When the inner loop runs to the end,
the `continue` moves the outer loop along instead:

```python
# nested_break.py

grid = [[1, 2], [3, 4]]

def locate(target):
    for row in grid:
        for cell in row:
            if cell == target:
                print(f"found {cell}")
                break  # [1]
        else:  # [2]
            continue
        break  # [3]
    else:  # [4]
        print("not found")
    print(f"searched for {target}")  # [5]

locate(3)
#: found 3
#: searched for 3
locate(9)
#: not found
#: searched for 9
```

`locate(3)` walks the first row to the end, so the inner `else` (`[2]`)
runs its `continue` and the outer loop moves on to the second row.
There the `3` matches, the inner `break` (`[1]`) skips the `else`,
and the outer `break` (`[3]`) runs right after.
`locate(9)` breaks neither loop,
so the inner `else` continues on each row and the outer `else` (`[4]`)
prints `"not found"`.

Each call ends at `[5]`, after both loops, whichever way the search went.
A `return` at the match would leave both loops in one step and skip `[5]` along with them.
The `else` form keeps the function running past the search,
and it also serves loops at the top level of a module, outside any function.

### `range()`, `enumerate()`, and `zip()`

`for` walks the items of any iterable.
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
print(list(enumerate(names, start=1)))
#: [(1, 'Alice'), (2, 'Bob'), (3, 'Carol'), (4, 'Ted')]
```

`enumerate()` yields `(index, item)` pairs counting from zero,
and the loop here unpacks each pair into `index` and `name`.
`for i in range(len(names)):` with `names[i]` inside does the same job,
but that form names the index and not the item,
so every line that needs the item repeats the `names[i]` lookup.
`enumerate()` hands you both.
For output that people read, which usually counts from one,
`start=1` begins the index at one, so a loop body can print it as it comes.
`list()` collects the pairs that the `start=1` form yields,
each index one higher than in the loop.

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
so it drops the extra score.
Stopping without an error is convenient when the lengths differ on purpose and a bug when you expect them to match.
`strict=True` raises a `ValueError` instead,
at the point where iteration finds one argument exhausted and another not,
which is why the listing consumes the `zip()` with `list()`.

When you need the index as well, wrap the `zip()` in `enumerate()`.
The nesting shows up in the loop header, where the inner pair needs parentheses:
`for i, (name, score) in enumerate(zip(names, scores)):`.

### The Walrus Operator

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

Each walrus expression here needs its parentheses.
`:=` binds more loosely than a comparison,
so `if n := len(text) > 3:` gives `n` the result of the comparison, `True`,
and not the length.

The `while` loop is where the walrus helps most.
The header checks that the stack has an item, pops it, names it, and tests it,
so the body starts with that value in hand.
The walrus also collapses `while_true.py` into its loop header:
`while (value := values.pop(0)) != 0:`.
A comprehension can use `:=` the same way,
and [Comprehensions](16_Techniques--Comprehensions.md) covers that use.

### Mutating a Container While Looping

Changing a container while a `for` loop walks it is the classic control-flow bug.
[Containers](03_Foundations--Containers.md#two-list-traps)
shows a `list` skipping items as the loop removes them,
and [a `dict` raising a `RuntimeError`](03_Foundations--Containers.md#dictionaries)
under the same treatment.
Lists and dictionaries are the two containers you are most likely to mutate this way,
and each one fails differently.
A [list comprehension](#comprehensions) fixes the list case by building a new,
filtered list instead of mutating the original in place:

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
Removing an item shifts the next one down into the slot the loop has passed,
so the loop skips it and one of the two `2`s survives,
with no exception to tell you.
Adding the key changes the dictionary's size,
and the dictionary raises a `RuntimeError` instead of skipping silently.
The same three fixes work for both.
Build a new container with a comprehension,
loop over a snapshot such as `list(ages)` while changing the original,
or collect the changes first and apply them after the loop.

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

The first `case` destructures the split command.
It matches a two-item list starting with `"go"` and binds the second item to `direction`.
A bare name in a `case` captures rather than compares.
`case direction:` binds anything to `direction` and matches every value.
Write a constant as a literal (`case "quit":`) or as a dotted name
(`case Command.QUIT:`).

`match` and `case` are *soft keywords*:
they are keywords only in this statement,
so existing code that uses `match` as a variable name still runs.
Avoid the name, though, because a reader must work out which meaning applies.
[Pattern Matching](13_Techniques--Pattern_Matching.md) covers `match` in detail.

## Errors and Exceptions

Python signals an error by *raising* an exception.
As in C++ and Java, an exception propagates up the call stack until it finds a handler.
An exception that finds no handler stops the program and prints the traceback.
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

`checked_divide()` raises a `ValueError` rather than letting Python's own `ZeroDivisionError` through.
Choose the exception that way when the caller should hear about the bad argument rather than the failed arithmetic.

The optional `else` runs when the `try` block raises no exception,
the same shape as the loop `else` that runs when the loop hits no `break`.
Code in the `else` is outside the reach of the `except` clauses,
so no `except` clause mistakes an exception from the follow-up work for the failure it expects.

The optional `finally` always runs, and that makes it the place for cleanup.
A `return`, `break`,
or `continue` inside `finally` swallows any exception in flight,
so keep all three out of cleanup code:

```python
# finally_swallows.py

def risky():
    try:
        raise ValueError("boom")
    finally:
        return "swallowed"

print(risky())
#: swallowed
```

`risky()` raises a `ValueError`,
but the `return` in `finally` discards it before it reaches the caller,
so the caller sees `"swallowed"` and no trace of the exception.
Python also flags the `return` in `finally` at compile time.
Running the listing prints `SyntaxWarning: 'return' in a 'finally' block` to standard error before `swallowed`.

Catch an exception only when you can do something about it.
A broad catch takes a bug in the `try` block along with the failure you expected,
and makes the bug look like that failure.
A bare `except:` with no type is the broadest of all.
It catches everything,
including the `KeyboardInterrupt` you press to stop a runaway program.
When you do need a broad catch, write `except Exception:`.
`KeyboardInterrupt` and `SystemExit` derive from `BaseException` rather than `Exception`,
so they propagate past that clause and still stop the program.

To handle several types the same way, give a tuple:
`except (ValueError, TypeError) as e:`.
Python tries the `except` clauses in order and runs the first whose type matches,
so a broad clause above a narrow one makes the narrow one unreachable.
Order them most specific first.

To log an exception and still let it propagate, re-raise it with a bare `raise`.

### Exception Chaining

Raising an exception while handling another attaches the handled exception to the new one.
Python reports both, and `from` decides how the two connect:

| Form | What Python prints above the new exception |
|---|---|
| `raise X` | During handling of the above exception, another exception occurred: |
| `raise X from e` | The above exception was the direct cause of the following exception: |
| `raise X from None` | Nothing: only `X` appears |

All three raise the same exception.
They differ in three attributes of that exception,
which Python reads to build the report:

```python
# exception_chaining.py

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

def name(e):
    return None if e is None else type(e).__name__

for parse in (implicit, explicit, suppressed):
    try:
        parse("seven")
    except BadNumber as e:
        print(parse.__name__, name(e.__cause__),
              name(e.__context__), e.__suppress_context__)
#: implicit None ValueError False
#: explicit ValueError ValueError True
#: suppressed None ValueError True
```

`BadNumber` is a custom exception type: a class derived from `Exception`.
Its body is `pass` because it needs no behavior of its own.
The handler matches on the class.
[Classes](07_Foundations--Classes.md) covers class definitions in full.

Each output line names a function, then shows the `__cause__`, `__context__`,
and `__suppress_context__` of the `BadNumber` it raised.
`name()` gives an attribute's exception class,
or `None` when the attribute is empty.

In all three functions,
Python records the handled `ValueError` in `__context__`.
With no `from`, that is the only link,
and Python prints it with the "During handling" line.
`from` with any argument sets `__suppress_context__` to `True`,
which hides `__context__` from the report.
`from e` also sets `__cause__`,
and Python prints the cause with the "direct cause" line.
`from None` leaves `__cause__` as `None`,
so nothing appears above the new exception.

Use `from e` when the earlier exception explains this one,
and `from None` when the earlier exception distracts from your own message.

### Ask Forgiveness, Not Permission

Python style favors "easier to ask forgiveness than permission,"
abbreviated EAFP.
Try the operation and handle the exception,
rather than checking every precondition first.
The opposite style, "look before you leap" (LBYL), tests first,
and it breaks whenever the test and the operation disagree:

```python
# eafp.py

def look_first(text):
    if text.isdigit():
        return int(text)
    return None

print(look_first("-5"), int("-5"))
#: None -5
try:
    look_first("\N{SUPERSCRIPT TWO}")
except ValueError as e:
    print("look_first:", e)
#: look_first: invalid literal for int() with base 10: '²'
```

`isdigit()` and `int()` disagree in both directions.
`isdigit()` rejects `"-5"`, which `int()` converts fine,
and `isdigit()` accepts `"²"`, which `int()` refuses with a `ValueError`.
`parse_int()` in `demonstrate_exceptions.py` is the EAFP version of `look_first()`.
Its `try` block asks the only question that matters: does this conversion work?
It returns `-5` for `"-5"` and `None` for `"²"`,
the two answers `look_first()` gets wrong.
The world can also change between the test and the operation.
A file that exists at the `if` can disappear before the `open()`,
and only the EAFP form is safe against that.

## Context Managers

A `with` block guarantees that setup and cleanup run as a pair,
even if the body raises an exception.
It does the work of a `try`/`finally` whose `finally` holds the cleanup.
The object that `with` manages supplies the cleanup, so you cannot leave it out.
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
A `with` statement creates a guarantee about the exit, not a scope,
so `f` is still in scope afterward and the listing can print `f.closed`.

Closing the file is cleanup that runs whether or not the block succeeds.
[Cleanup](10_Foundations--Cleanup.md)
contrasts that guarantee with leaving the close to Python's garbage collector.

Anything that acquires a resource (a file, a lock, a network connection)
can be a context manager.
An object becomes one by defining two methods, `__enter__()` and `__exit__()`:
`with` calls `__enter__()` at the top of the block and `__exit__()` as control leaves it,
and the cleanup lives in `__exit__()`.
[Context Managers](15_Techniques--Context_Managers.md)
shows how to write your own.

For reading or writing a whole file in one call,
`pathlib` provides `read_text()` and `write_text()`,
which open the file and close it again.

## Comprehensions

A *comprehension* builds a list, dictionary,
or set from an iterable in one expression,
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

Every form has the same order: the expression that produces each item,
the `for` clause that supplies the values,
and an optional `if` that filters them.
The delimiters choose the container.
Brackets build a list, braces build a set,
and braces around a `key: value` expression build a dictionary.
[Comprehensions](16_Techniques--Comprehensions.md) covers nesting,
generator expressions, and when to write a loop instead.

## Exercises

Try each exercise before opening its [solution](../Solutions/04_Foundations--Control_Flow/).

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
    Predict which line the traceback shows above `BadNumber` before you run it.
8.  Rewrite `context_manager.py`'s reading half using `path.read_text()`.
    Say what the `with` form gives you that the one-liner does not,
    and when that matters.
9.  In `mutating_while_looping.py`, change the list to `[2, 2, 1, 3]`,
    so a `2` sits in the first slot.
    Use the shifting-slots explanation to predict what the loop leaves in `scores`,
    then run it to check.
10. In `eafp.py`, predict what `look_first()` and `int()` each return for `" 42 "`
    (with a space on each side) and for `"4_2"`, then run both.
    Say what the results tell you about adding more tests to `look_first()`.
