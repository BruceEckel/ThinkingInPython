When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Chapter opening (lines 3-5): the summary sentence omits the Placeholders
section.**

"This chapter covers conditionals, loops, pattern matching, exceptions, the
`with` statement, and comprehensions" lists six of the seven sections. The
`pass`/`...` section sits second and is not named, so a reader scanning the
opening does not expect it.

Proposed change: extend the list to
"...conditionals, placeholders, loops, pattern matching, exceptions, the
`with` statement, and comprehensions."

Alternative, if you would rather keep the list to the load-bearing topics:
demote Placeholders to a subsection of Conditionals (`###`), since `pass` first
becomes necessary inside an empty `if` body. That changes no anchor that
another chapter links to (only `#pattern-matching`, `#context-managers`, and
`#comprehensions` are linked in from 13, 15, and 16; `{#placeholders}` is not
referenced anywhere).

---

[] Reject

**"Conditionals" (line 9): the section starts mid-topic with no link back to
where `if` was introduced.**

Chapter 2's `if.py` is where the reader met `if`, indentation, and the colon.
Chapter 4's Conditionals section opens on chained comparison, assuming all of
that. The skill's rule is that when a chapter leans on earlier material it
should name the chapter with a link, not rely on the reader remembering.

Proposed change: open the section with one sentence, e.g.
"[Tour](02_Tour.md#how-to-read-the-examples) showed the basic `if`, its colon,
and its indented block.
Python's comparison operators also chain the way they do in mathematics:"

(`#how-to-read-the-examples` rather than the section holding `if.py`, whose
title is "Scripting vs. Programming" and whose pandoc slug therefore keeps the
period: `#scripting-vs.-programming`.)

---

[] Reject

**"Placeholders" (lines 44-68): two listings make one point.**

`pass_statement.py` and `ellipsis_placeholder.py` are the same six lines twice,
each defining an empty function and printing `None`. The house style says a
demo makes its point once and stops, and the contrast between the two
placeholders is the actual content, which two separate listings hide rather
than show.

Proposed change: merge them into one listing that puts the two side by side:

```python
# placeholders.py

def not_implemented():
    pass  # Fill in later

def not_implemented_yet():
    ...

print(not_implemented(), not_implemented_yet())
#: None None
```

Cost: renames two examples, so `Examples/04_Control_Flow/` needs
`make prune-examples` after the sync. No other chapter references either file
name; the chapter's own exercises do not either.

---

[] Reject

**"Placeholders" (lines 70-73): the prose describes a form the listing does not
show.**

"`...` marks a one-line stub, usually a function signature with no real body"
describes `def method(self) -> str: ...`, all on one line. The listing above it
writes `...` on its own indented line, which is the same shape as the `pass`
listing, so the stated difference between the two placeholders is not visible
anywhere on the page.

Proposed change: show the one-line form in the merged listing above, e.g. add

```python
class Named(Protocol):
    def name(self) -> str: ...
```

or, if that pulls `Protocol` in too early, reword the prose to
"`...` is the conventional body for a stub that will be filled in elsewhere,
and it is normally written on the same line as the signature it stubs, as in a
`Protocol` method."

---

[] Reject

**"Loops" (lines 77-98): nothing tells a C/C++/Java reader that Python has no
`do`/`while`, and the `while True:` + `break` idiom never appears.**

The chapter's stated audience has programming experience and the prose
repeatedly compares to C++ and Java ("As in C++ and Java, an exception
propagates...", "reminiscent of a C `switch`"). "Where is `do`/`while`?" is one
of the first questions that audience asks about Python loops, and the answer,
the `while True:` loop with a `break` at the bottom, is used later in the book
(23, 38, 41, 45) without ever being introduced.

Proposed change: after `while_loop.py`, add a short paragraph and listing:

```python
# while_true.py

total = 0
for value in [3, 0, 7]:  # Stands in for reading input
    if value == 0:
        break
    total += value
print(total)
#: 3
```

Better, keep it a real `while True:`:

```python
# while_true.py

values = iter([3, 5, 0, 7])
total = 0
while True:
    value = next(values)
    if value == 0:
        break
    total += value
print(total)
#: 8
```

with prose: "Python has no `do`/`while` statement. When the test belongs at the
bottom of the body rather than the top, write `while True:` and `break` out."

Placement is yours: it could equally follow the `break`/`continue` listing,
since it uses `break`.

---

[] Reject

**`break_continue.py` (lines 100-123): one listing teaches two unrelated
things.**

The listing demonstrates `break` and `continue`, and then, in its last two
lines, `print()`'s `sep=` parameter, which has nothing to do with control flow.
Twelve lines of the surrounding prose (117-123) are then split between the two
subjects, with the control-flow narration first and a `print()` tutorial after
it. The house rule is one new thing per listing.

Proposed change: drop `print("a", "b", sep="-")` and its marker from
`break_continue.py`, and cut the third prose paragraph down to what the listing
still needs:

"`print()` ends with a newline by default. `end=" "` replaces that newline with
a space, so the numbers land on one line, and a bare `print()` emits the
missing newline afterward."

See the Cross-chapter note at the end of this file for where `sep=` belongs.

---

[] Reject

**"Loops" (line 100): `break` and `continue` are never said to apply to the
innermost loop only.**

The chapter introduces both statements with single-level loops and never
returns to them. A reader coming from Java expects a labeled `break` and will
look for one; a reader coming from C will assume the innermost rule and be
right, but the chapter does not confirm it. Nothing anywhere else in the book
states it.

Proposed change: add to the paragraph at line 117:
"Both apply to the innermost enclosing loop. Python has no labeled `break`, so
leaving two loops at once means either a flag, a `return` from a function that
holds both loops, or a `for`/`else` on the outer one."

I recommend the sentence over a listing; the `for`/`else` machinery it points
at is already taught two listings later.

---

[] Reject

**`looping.py` (lines 149-170): the near-miss `for i in range(len(names))` is
never shown or warned about.**

"Use `range()` for counting and `enumerate()` when you also need the index" is
the right advice, but it does not name the construct the reader is most likely
to write instead. `for i in range(len(names)):` followed by `names[i]` is the
single most common non-Pythonic loop written by people arriving from C, Java,
or JavaScript, and it is exactly what `enumerate()` exists to replace.

Proposed change: add after line 170:
"A loop written as `for i in range(len(names)):` and then indexing `names[i]`
does the same job, but it names the index and re-looks-up the item on every
line that needs it. `enumerate()` hands you both."

---

[] Reject

**`zipping.py` (lines 195-196): the `enumerate(zip(...))` advice stops one step
short of the part that trips people up.**

"When you need the index as well, wrap the whole thing: `enumerate(zip(names,
scores))`" names the expression but not the loop header, and the loop header is
where the reader fails: `for i, name, score in ...` is a `ValueError`, because
`enumerate` yields a two-item pair whose second item is itself a pair.

Proposed change: give the header instead of the expression:
"When you need the index as well, wrap the whole thing. The extra nesting shows
up in the loop header, which needs parentheses around the inner pair:
`for i, (name, score) in enumerate(zip(names, scores)):`"

---

[] Reject

**"Loops": mutating a container while iterating over it is not covered here or
anywhere else in the book.**

A `for` loop over a list that the body removes from silently skips elements; a
`for` loop over a dict that the body adds keys to raises `RuntimeError`. This
is the classic control-flow bug, the two containers behave differently, and
neither appears in chapters 3, 4, 16, or 23.

Verified on the pinned 3.15 build:

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

Proposed change: add this listing at the end of the Loops section, after the
walrus, with prose along the lines of: the list loop walks by position, so
removing an item shifts the next one into the slot the loop already passed and
one of the two `2`s survives; the dict refuses outright rather than skipping
silently. Build a new container instead, with a comprehension or by collecting
what to remove first.

This is the largest single gap I found in the chapter. If you take only one
addition from this review, I recommend this one.

---

[] Reject

**"Pattern Matching" (lines 227-262): `match` and `case` are soft keywords, and
the chapter does not say so.**

`match = pattern.search(s)` is still legal, and the book's own style rule says
never to name an identifier after a soft keyword. Chapter 6 uses the term "soft
keyword" for `lazy`, so it is in the book's vocabulary; chapter 13 does not
cover it either.

Proposed change: add one sentence near line 262, before the pointer to chapter
13: "`match` and `case` are *soft keywords*: they are keywords only in this
statement, so existing code that uses `match` as a variable name still runs.
Avoid the name anyway, since a reader has to work out which one is meant."

---

[] Reject

**"Errors and Exceptions" (lines 314-323): nothing says `except` clauses are
tried in order.**

This section is the book's only general treatment of exceptions, and it never
states that Python tries the clauses top to bottom and runs the first whose
type matches. The consequence is a real bug: `except Exception:` written above
`except ValueError:` makes the second clause unreachable, silently.

Proposed change: add after the tuple sentence at line 323:
"Python tries the `except` clauses in order and runs the first whose type
matches, so a broad clause above a narrow one makes the narrow one
unreachable. Order them most specific first."

---

[] Reject

**`demonstrate_exceptions.py` (line 291): `exceptions()` is a poor name for the
function.**

It is a bare plural noun, it names the chapter's topic rather than what the
function does, and it collides conceptually with the section title. The
Solutions file already renamed it: `Solutions/04_Control_Flow.md`, exercise 4,
calls the same function `demo_exceptions()`, which is a sign the name caused
friction for whoever wrote that.

Proposed change: rename to `report()` or `divide_and_report()` in the listing
and in exercise 4's wording. Note this makes the chapter and
`Solutions/04_Control_Flow.md` disagree until the Solutions copy is updated to
match, which is outside this review's scope.

---

[] Reject

**`exception_chaining.py` (lines 332-382): the table promises text the listing
never prints.**

The table at lines 324-328 says what Python prints above the new exception, in
three exact phrases. The listing then inspects `__cause__`, `__context__`, and
`__suppress_context__` and prints a summary of its own invention ("during
handling: ValueError"). The reader is given the rule and the attributes but
never sees Python produce the sentence the table quoted, so the table and the
output are two separate facts they have to trust independently. This is the
mechanism-vs-outcome test: from this output alone a reader cannot narrate what
a real traceback would look like.

Proposed change: swap `earlier()` for a function that pulls the actual joining
line out of the formatted traceback. Verified on the pinned 3.15 build, output
is deterministic (no file paths or line numbers leak through) and every line is
under 70 columns:

```python
import traceback

def joining_line(e):
    for part in traceback.format_exception(e):
        line = part.strip()
        if line.endswith("exception occurred:") or line.endswith(
            "following exception:"
        ):
            return line
    return "nothing shown above it"

for parse in (implicit, explicit, suppressed):
    try:
        parse("seven")
    except BadNumber as e:
        print(f"{parse.__name__}: {joining_line(e)}")
#: implicit: During handling of the above exception, another exception occurred:
#: explicit: The above exception was the direct cause of the following exception:
#: suppressed: nothing shown above it
```

Two caveats. The first two marker lines are 82 and 81 characters, which is
wider than the chapter's other markers, though `#:` markers are not
line-length-gated. And `earlier()` teaches `__cause__`/`__context__`/
`__suppress_context__`, which this version drops; if you want both, keep
`earlier()` and add `joining_line()` as a second listing rather than replacing
it. My recommendation is the replacement: the attribute names are reference
material and the printed sentence is the thing a reader will actually see.

---

[] Reject

**"Context Managers" (lines 428-450): the guarantee the section is about is
never demonstrated.**

"A `with` block guarantees that setup and cleanup happen as a pair, even if the
body raises an exception" is the claim, and `context_manager.py` shows only the
happy path. The reader sees a file opened and closed with nothing going wrong,
which a plain `open()`/`close()` pair would also manage. The exception case is
the whole reason the construct exists.

Proposed change: extend `context_manager.py` with the failing case. Verified on
the pinned 3.15 build:

```python
try:
    with path.open("w") as f:
        f.write("partial")
        raise RuntimeError("failed midway")
except RuntimeError as e:
    print(e)
#: failed midway
print("closed:", f.closed)
#: closed: True
```

Add prose: "The exception propagates, but the file is closed before it does.
`f` is still in scope afterward, which is how the listing can check it; the
`with` statement does not create a scope, only a guarantee about the exit."

That last clause also closes a small loop with chapter 2, which says an
indented block does not create a scope.

---

[] Reject

**"Exercises" (lines 488-507): the set covers the first half of the chapter and
skips the second.**

By section: Conditionals 0, Placeholders 0, Loops 3 (exercises 1, 2, 3), Pattern
Matching 1, Exceptions 1, Context Managers 0, Comprehensions 1. Three of the six
exercises sit on Loops. Nothing exercises the walrus operator, `zip(strict=True)`,
`with`, EAFP-vs-LBYL, or exception chaining, and the chaining table plus
`exception_chaining.py` is the densest passage in the chapter.

Proposed change: add two exercises and consider dropping one of the three loop
exercises (3 is the weakest: it asks the reader to confirm that two mutually
exclusive tests commute, which the question itself half-answers).

- "In `exception_chaining.py`, add a fourth function that catches the
  `ValueError` and raises `BadNumber` from a *different* exception object it
  constructs itself. Predict which line `earlier()` prints before you run it."
- "Rewrite `context_manager.py`'s reading half using `path.read_text()`.
  Say what the `with` form gives you that the one-liner does not, and when that
  matters."

If you would rather keep the count at six, the first of those two is the one I
would add.

## Cross-chapter

**`Chapters/02_Tour.md`** — `print()`'s `sep=` parameter.

The finding above proposes removing `print("a", "b", sep="-")` from chapter 4's
`break_continue.py`, where it is unrelated to the listing's subject. It should
land in chapter 2, which is where `print()` is introduced ("The `print()`
function sends its argument to standard output", line 61) and where the
Strings and f-Strings sections already handle output formatting. The exact
change I would make there: append to `string_methods.py` (or add two lines to
`fstrings.py`, whichever fits the section better):

```python
print("a", "b", sep="-")  # Sep goes between values
#: a-b
print("no newline", end=" ")
print("same line")
#: no newline same line
```

with a sentence noting that `sep=` sets what goes between several values (a
space by default) and `end=` replaces the trailing newline. Chapter 4's
`looping.py` and `break_continue.py` both use `end=" "` and currently explain
it in passing, so moving both parameters to chapter 2 lets chapter 4 use them
without stopping to teach them.

I did not touch chapter 2.

**`Chapters/19_Concurrency.md`** — no change needed, recorded for consistency.

Chapter 19 line 346 explains that `CancelledError` "derives from
`BaseException` rather than `Exception`" as if introducing the distinction. I
added the same distinction to chapter 4's exception section (bare `except:` vs.
`except Exception:`), so 19's sentence is now a callback rather than a first
statement. It still reads correctly as written; if you want them stitched
together, 19's could become "As [Control Flow](04_Control_Flow.md#errors-and-exceptions)
noted, ...". I did not touch chapter 19.
