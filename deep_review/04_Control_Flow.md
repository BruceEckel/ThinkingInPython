# Deep review: 04_Control_Flow.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Give EAFP an example, and name its opposite

**Kind:** teaching
**Where:** section "Errors and Exceptions" (lines ~328-330)
**Problem:** The section closes by recommending EAFP in two sentences with no listing, no acronym, and no counterexample. The reader is told to prefer a style they have not seen contrasted with anything, and the acronym "EAFP", which they will meet in every Python discussion afterward, appears nowhere in the book (grep over `Chapters/` finds this one sentence and no other mention). The listing immediately above it, `checked_divide()`, tests a precondition before acting, so the advice reads as contradicting the code.

**Proposal:** Replace the closing paragraph with a named contrast plus one listing. Verified output shown.

```
Python's culture leans on "easier to ask forgiveness than permission," abbreviated EAFP.
Try the operation and handle the exception,
rather than checking every precondition first.
The opposite style, "look before you leap" (LBYL), tests first,
and it breaks whenever the test and the operation disagree:
```

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
    print("careful failed:", e)
#: careful failed: invalid literal for int() with base 10: '²'
print(forgiving("\N{SUPERSCRIPT TWO}"))
#: None
```

```
`isdigit()` and `int()` disagree in both directions.
`isdigit()` rejects `"-5"`, which `int()` converts fine,
and it accepts `"²"`, which `int()` refuses.
The `try` block asks the only question that matters:
does this conversion work?
```

*Alternative if the non-ASCII marker is unwelcome:* use `"1_000"` (`isdigit()` says no, `int()` returns 1000) and `" 42 "`, which shows one direction of the disagreement instead of both. The `#:` markers were verified against `uv run python`; `#:` lines already carry non-ASCII elsewhere in the book (chapter 12's bullets).

**Cost:** One new example file, `Examples/04_Control_Flow/eafp.py`. Nothing else references it.

---

## 2. Warn against `except:` with no type

**Kind:** teaching
**Where:** section "Errors and Exceptions" (after line ~267)
**Problem:** This is the reader's first exposure to `except`, and the chapter never says what happens when you leave the type off. A bare `except:` is the single most common beginner mistake with Python exceptions: it catches `KeyboardInterrupt` and `SystemExit`, so it swallows the Ctrl-C used to stop a runaway loop, and it hides typos as if they were expected failures. The chapter also never shows the tuple form, so a reader with two failure modes to handle has no shown way to write it.

**Proposal:** Add after "The optional `finally` always runs, which makes it the place for cleanup.":

```
Catch the exceptions you can do something about.
A bare `except:` with no type catches everything,
including the `KeyboardInterrupt` you press to stop a runaway program,
so a mistake in the `try` block looks like an expected failure.
To handle several types the same way, give a tuple:
`except (ValueError, TypeError) as e:`.
```

**Cost:** none. Prose only.

---

## 3. `zip()` truncates silently, and the chapter never mentions `strict=True`

**Kind:** teaching
**Where:** section "Conditionals and Loops", `looping.py` (lines ~155-167)
**Problem:** The listing deliberately feeds `zip()` a longer `scores` list and drops the last score, and the prose describes the truncation as a feature ("stopping when the shortest runs out"). That truncation is also the classic `zip()` bug: two lists that were supposed to be parallel drift out of sync and the loop silently processes the short prefix. Python has had `strict=True` since 3.10 to turn that into an error, and a reader who is shown the truncation but not the guard has been taught the footgun without the fix.

**Proposal:** Show both. Combined with proposal 4, `zip` moves to its own listing:

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

Prose after it:

```
`zip()` produces one item from each sequence and stops when the shortest runs out,
so the extra score never appears.
That silence is convenient when the lengths differ on purpose and a bug when they were supposed to match.
`strict=True` raises a `ValueError` on the mismatch instead.
```

Output verified against `uv run python` on the pinned interpreter.

**Cost:** Depends on proposal 4. If 4 is rejected, add the `strict=True` lines to `looping.py` instead and keep its `zip(range(10), ...)` call, which makes the mismatch harder to see because `range(10)` is longer than both.

---

## 4. `looping.py` teaches four things at once

**Kind:** structure
**Where:** section "Conditionals and Loops", `looping.py` (lines ~141-167)
**Problem:** One listing introduces `range()`, `enumerate()`, `zip()`, and the `end=`/no-argument forms of `print()`. Its last loop, `zip(range(10), names, scores)`, uses `range(10)` as a counter one line after `enumerate()` was introduced as the way to count, so the listing quietly demonstrates the thing it just told the reader not to need. The arbitrary `10` also has to be big enough to not truncate, which is a detail the reader must notice to understand the output.

**Proposal:** Split into two listings: `looping.py` keeps `range()` and `enumerate()`, and `zipping.py` (proposal 3) takes `zip()` with its own two sequences and no counter. If a reader needs index plus two sequences, `enumerate(zip(names, scores))` is the composition to show, in prose or as a third line.

**Cost:** One added example file; `looping.py` shrinks. No exercise or other chapter names `looping.py`.

---

## 5. `end=` is explained three listings after its first use

**Kind:** structure
**Where:** section "Conditionals and Loops" (lines ~169-170)
**Problem:** `print(n, end=" ")` first appears in `break_continue.py`, and the reader meets an unexplained keyword argument at the exact moment the point of the listing is `break` and `continue`. The explanation arrives two listings later, attached to nothing, and the `sep` half of it is never demonstrated at all.

**Proposal:** Move the sentence about `end` to right after `break_continue.py`, where the reader first needs it, and let it carry the bare `print()` too:

```
`print()` ends with a newline by default.
`end=" "` replaces that newline with a space, so the numbers land on one line,
and a bare `print()` emits the missing newline afterward.
```

Then either drop the `sep` sentence or give it a one-line demo. `sep=` appears nowhere in the whole book (verified by grep over `Chapters/`), so the mention has nothing to attach to. Recommend one demo line in the same listing if `sep` is worth keeping: `print("a", "b", sep="-")` printing `a-b`.

**Cost:** none. Prose moves within one section.

---

## 6. The walrus section claims a `while` use it never shows

**Kind:** teaching
**Where:** section "Conditionals and Loops" (lines ~190-191)
**Problem:** "This is especially handy in `while` conditions and comprehensions, where it avoids repeating a computation" is the strongest thing the walrus does, and it is asserted rather than shown. The listing only demonstrates the weakest case, an `if` where the two-line version reads just as well, which leaves the reader wondering why the operator exists.

**Proposal:** Append to `walrus.py`:

```python
queue = ["a", "b", "c"]
while queue and (item := queue.pop()) != "a":
    print("processing", item)
#: processing c
#: processing b
```

and reword the following paragraph to point at it: the loop names the popped value and tests it in one place, so nothing has to pop it a second time inside the body. Keep the comprehension mention as a forward pointer to [Comprehensions](16_Comprehensions.md).

*Alternative:* the canonical `while line := stream.readline():` over an `io.StringIO`, which is the form readers will meet in real code but introduces `StringIO` here.

**Cost:** `walrus.py` grows by four lines. Markers verified.

---

## 7. A bare name in a `case` matches everything

**Kind:** teaching
**Where:** section "Pattern Matching" (lines ~195-219)
**Problem:** The section sells `match` as a more powerful `switch`, and the first thing a C or Java reader writes is `case QUIT:` with a named constant. In Python that is a capture pattern: it binds every value to the name and matches unconditionally, shadowing the constant and making every later `case` dead. This chapter is where that reflex forms, and chapter 13 is a long way off.

**Proposal:** Add one sentence after "A pattern can also destructure a value and bind its parts.":

```
A bare name in a `case` captures rather than compares:
`case direction:` binds anything to `direction` and matches every value.
Write a constant as a literal (`case "quit":`) or as a dotted name (`case Command.QUIT:`).
```

**Cost:** none, if [Pattern Matching](13_Pattern_Matching.md) still teaches the rule in full. Check that chapter's wording so the two agree.

---

## 8. Exercises cover loops and skip half the chapter

**Kind:** exercise
**Where:** section "Exercises" (lines ~390-405)
**Problem:** Three of the four exercises work on loops, and the fourth on exceptions. Nothing exercises `match`, comprehensions, `with`, the walrus, or exception chaining, which is over half the chapter. Exercise 4's first call, `exceptions(1, 2)`, does the same thing as the `exceptions(1, 1)` call already in the listing, so that half asks the reader to reproduce output they have read.

**Proposal:** Drop the duplicate call from exercise 4 (keep the `TypeError` half, which is the real lesson) and add two exercises:

```
5.  In `pattern_matching.py`, add a `case ["go", direction, distance]`
    that reports both parts, and check what `run("go north 3")` returns
    before and after you add it.
6.  Rewrite the `evens` list comprehension in `comprehensions_intro.py`
    as a `for` loop that appends to a list,
    then say which version you would rather read six months from now.
```

A third candidate, if the set should reach the chaining table: call `implicit("seven")` outside any `try` in `exception_chaining.py` and read the two-part traceback, which is the only place the reader sees the text the table describes.

**Cost:** `Solutions/04_Control_Flow.md` needs the new answers, and exercise 4's solution loses its `demo_exceptions(1, 2)` call and the sentence about it.

---

## 9. "Conditionals and Loops" is half the chapter under one heading

**Kind:** structure
**Where:** section "Conditionals and Loops" (lines ~7-191)
**Problem:** Ten of the chapter's fourteen listings sit under one heading that covers chained comparisons, conditional expressions, `elif`, `pass`, `...`, `while`, `break`/`continue`, loop `else`, `range`/`enumerate`/`zip`, and the walrus. A reader looking for `break` has no heading to aim at, and the placeholder pair (`pass` and `...`) is not about conditionals or loops at all.

**Proposal:** Split into three headings with no prose changes: "Conditionals" (through `if_elif.py`), "Placeholders: `pass` and `...`", and "Loops" (from `while_loop.py` on). The walrus can end "Loops" or become its own short heading.

**Cost:** No inbound cross-reference names `#conditionals-and-loops`; the three chapters that link here use `#pattern-matching`, `#context-managers`, and `#comprehensions`, all untouched. Verified with a grep for `04_Control_Flow`.

---

## 10. `checked_divide()` raises `ValueError` where Python raises `ZeroDivisionError`

**Kind:** code
**Where:** section "Errors and Exceptions", `demonstrate_exceptions.py` (lines ~243-246)
**Problem:** Python already has a specific exception for this, and the listing replaces it with a broader one for no stated reason, right before the prose recommends letting operations fail rather than checking first. A reader learns "write a guard and raise `ValueError`" from the code while reading "try it and handle the exception" in the prose.

**Proposal:** Say why in one sentence, since the chapter does need a `raise` somewhere and a domain error is a defensible thing to teach:

```
`checked_divide()` raises `ValueError` rather than letting Python's own `ZeroDivisionError` through,
which is what you do when the caller should hear about the bad argument, not the failed arithmetic.
```

*Alternatives:* drop `checked_divide()` and let `try: return a / b` raise `ZeroDivisionError`, which makes the section consistently EAFP but removes the chapter's only `raise` outside `exception_chaining.py`; or keep the guard and rename the exception to a custom one, which duplicates `BadNumber` from the next listing.

**Cost:** The alternatives change `Solutions/04_Control_Flow.md` exercise 4, which copies `checked_divide()` verbatim. The recommended one-sentence version costs nothing.

---

## 11. Connect `try`'s `else` back to the loop's `else`

**Kind:** teaching
**Where:** section "Errors and Exceptions" (line ~266)
**Problem:** The chapter teaches two `else` clauses attached to something other than an `if`, thirty lines apart, without connecting them. A reader who found the first one strange meets the second as a second strange thing instead of a pattern. Both mean "the interruption did not occur."

**Proposal:** Extend the sentence at line 266:

```
The optional `else` runs when the `try` block raised no exception,
the same shape as the loop `else` that runs when no `break` occurred.
```

**Cost:** none.

---

## 12. `chaining.py` prints `pass` two listings before `pass` becomes a keyword

**Kind:** code
**Where:** section "Conditionals and Loops", `chaining.py` (lines ~17-19)
**Problem:** The conditional expression yields the string `"pass"` and the marker reads `#: pass`. Three paragraphs later the chapter introduces the `pass` statement. The collision is accidental and a reader skimming markers sees the keyword where a grade was meant.

**Proposal:** Change the strings to `"ok"` and `"low"` (or `"admit"`/`"reject"`), and update the `#:` marker to match.

**Cost:** `Examples/04_Control_Flow/chaining.py` re-syncs. No exercise or solution references it.

---

## 13. "A pattern can also destructure" describes what the listing already did

**Kind:** prose
**Where:** section "Pattern Matching" (line ~218)
**Problem:** `case ["go", direction]` destructures the split command and binds `direction`, and the prose then introduces destructuring as something `match` "can also" do. The reader is told about a capability they just watched work, so the sentence reads as if a second, unshown feature is being named.

**Proposal:** Point at the listing instead:

```
The first `case` destructures the split command: it matches a two-item list starting with `"go"`,
and binds the second item to `direction`.
[Pattern Matching](13_Pattern_Matching.md) covers `match` in detail.
```

**Cost:** none.

---

## 14. `ellipsis_placeholder.py` annotates its return type; its `pass` twin does not

**Kind:** code
**Where:** section "Conditionals and Loops", `ellipsis_placeholder.py` (line ~61)
**Problem:** `def not_implemented_yet() -> None:` carries the chapter's only annotation, four lines after `def not_implemented():` was written without one. Chapters 2 through 7 stay unannotated on purpose, since [Static Typing](08_Static_Typing.md) is chapter 8, so the lone `-> None` reads as an oversight in a paired contrast where the only intended difference is `pass` versus `...`.

**Proposal:** Drop the `-> None` so the two stubs differ only in their body. If it is there because `...` stubs usually appear in typed code (a `Protocol` method), say that in the prose instead, where the sentence about `Protocol` methods already sits.

**Cost:** `Examples/04_Control_Flow/ellipsis_placeholder.py` re-syncs. Output is unchanged either way.

---

## 15. "The explicit-finalizer approach" is chapter-10 vocabulary in chapter 4

**Kind:** prose
**Where:** section "Context Managers" (line ~356)
**Problem:** A reader four chapters in has not met "explicit finalizer" and cannot use the phrase to understand what `with` just did. The sentence names a category from a chapter six ahead instead of describing the mechanism.

**Proposal:**

```
Closing the file is cleanup that runs whether or not the block succeeds,
which [Cleanup](10_Cleanup.md) contrasts with letting Python's garbage collector do it.
```

**Cost:** none. The link still resolves; only the wording changes.

---

## 16. Section order: comprehensions sit two sections away from the loops they replace

**Kind:** structure
**Where:** section "Comprehensions" (line ~363)
**Problem:** The comprehension section opens by defining a comprehension as a replacement for "a loop that builds up a result," but the loop material ended two sections earlier, with pattern matching and exceptions in between. The reader has to re-establish the comparison from memory.

**Proposal:** Consider moving "Comprehensions" to directly follow the loop material, before "Pattern Matching." The chapter then runs statements-that-loop, then the expression form of the same idea, then the remaining statement forms.

*Reason to reject:* the current order groups statements first and defers the expression forms, and the section is short enough that the gap costs little. This is offered because the order is worth a decision, not because it is clearly wrong.

**Cost:** The `#comprehensions` anchor is unchanged, so [Comprehensions](16_Comprehensions.md)'s inbound link keeps working. No listing depends on the order.

---

## Already fixed directly (no decision needed)

Nothing. Every listing runs, every `#:` marker matches real stdout, `ty` and `ruff` pass on `build/examples/04_Control_Flow`, `heading_links.py` and `banned_phrases.py` are clean, and no technical claim in the prose is wrong.

One near-miss worth recording: line 337's "closes the file on the way out" contains a watch-list phrase, but "on the way out" is the author's own idiom, used the same way in chapters 12 and 15, so it was left alone.
