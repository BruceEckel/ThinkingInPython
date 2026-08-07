When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Section: opening / "Matching Values" — the chapter's first listing is the one
use case it immediately disowns.**

`http_status.py` is a literal-to-literal `switch`, and the very next paragraph
says a dictionary is shorter and points at "When Not to Match". A reader's
first impression of `match` is therefore "the tool I was just told not to use
here." The chapter's actual payoff (destructuring, and the closed-union
exhaustiveness in `exhaustive.py`) does not arrive for several sections.

Proposal: keep `http_status.py` where it is, but put a two-line teaser of a
structural pattern in the chapter introduction, before "Matching Values", so
the reader sees what `match` buys before decoding the syntax. Something as
small as

```
match event:
    case {"type": "click", "x": x, "y": y}:
        ...
```

with one sentence saying "no `switch` in any language can do that" would do it.
Alternative, if you'd rather not add a listing: move the sentence "`match`
becomes valuable once the patterns do more than test equality" up into the
chapter introduction, so the promise precedes the weak example instead of
following it.

Cost: none to cross-references; the section titles do not change.

---

[] Reject

**Section: "Matching Values" — `case _:  # Default` in `http_status.py`.**

The comment restates the prose two lines above it ("A `case _` at the end is
the wildcard. It matches anything, like a default."), and the house style puts
descriptions in prose rather than comments. The same comment appears in
chapter 4's `pattern_matching.py`, so this is a two-chapter decision rather
than a slip, which is why it is reported instead of applied.

Proposal: drop `  # Default` from `http_status.py`. If you keep it, keep it in
both places.

---

[] Reject

**Section: "Alternatives and Capture" — the alternation half of the section is
one sentence, and the rule that governs `|` is taught three sections later.**

The section is titled for two topics and spends one line on the first:
"An alternative combines several patterns in one `case` with `|`." The rule a
reader actually needs — every alternative must bind the same set of names —
sits in "Patterns Nest", attached to `Point(0, n) | Point(n, 0)`.

This has a concrete consequence outside the chapter:
`Chapters/34_Composite_and_Interpreter.md` line 466 cites that rule as
"(see [Alternatives and Capture](13_Pattern_Matching.md#alternatives-and-capture))".
The anchor resolves, so `heading_links.py` is silent, but the rule is not in
that section. See the Cross-chapter note at the end for the other way to fix
this.

Proposal (recommended, stays inside chapter 13): state the rule where `|` is
introduced, as one sentence after "An alternative combines several patterns in
one `case` with `|`.":

> Every alternative in a `|` must bind the same set of names.

Leave the `SyntaxError` demonstration in "Patterns Nest" where the code that
triggers it lives. This makes chapter 34's existing link correct with no edit
to chapter 34.

---

[] Reject

**Section: "Sequence Patterns" — `case (x)` is a group pattern, not a
one-element sequence.**

Parentheses in a pattern group; they do not build a tuple. `case (x)` is
exactly `case x`, an unconditional capture that swallows every subsequent
case, while `case (x,)` is a one-element sequence pattern. Verified on the
pinned 3.15: `case (x)` matched both `5` and `[1, 2]`; `case (x,)` matched
`(5,)` and `[5]` but not `5`.

A reader who knows Python tuple syntax will write `case (x)` meaning
"a one-item sequence" and get a silent catch-all — the same class of mistake as
the `case DEFAULT` capture the chapter already teaches, and just as invisible.

Proposal: add after "because the pattern describes a shape, not a concrete
type.":

> Parentheses group a pattern rather than build a tuple:
> `case (x)` is just `case x`, an unconditional capture,
> while `case (x,)` is a one-element sequence pattern.

---

[] Reject

**Section: "Class Patterns" — `keyword_patterns.py` teaches two new things at
once.**

The listing introduces keyword patterns *and* a guard, and the chapter has to
apologize for it: "The `if x == y` on the third case is a *guard*, covered in
the next section." That forward reference is the tell.

Two ways out, and I recommend the first:

1. Drop `case Point(x=x, y=y) if x == y:` from `keyword_patterns.py`. The
   remaining three cases (`Point(x=0)`, `Point(y=0)`, `Point()`) already make
   every point the surrounding prose makes: subset matching, ignoring the rest,
   and the bare `Point()` catch-all. Cost: delete the
   `#: On the diagonal at 2` marker and its `print`, and delete the
   `(Point(2, 2), "On the diagonal at 2")` row from `test_class_patterns.py`'s
   `test_keyword_patterns` parametrize list.
2. Move "Guards" ahead of "Class Patterns". Cost is higher: `guards.py`
   imports `Point` and uses `Point(0, 0)` and `Point(x, y)`, so the guards
   listing would have to be rewritten against a non-class subject, and
   "Class Patterns" is where `point.py` is introduced.

---

[] Reject

**Section: "Class Patterns" — give the `TypeError` its message.**

"Without a `__match_args__` long enough to cover the positions you supply, a
positional pattern raises a `TypeError`." The chapter quotes the exact text of
both `SyntaxError`s it mentions, so this one reads as an omission by
comparison. The messages on the pinned 3.15 are:

```
TypeError: Q() accepts 1 positional sub-pattern (2 given)
TypeError: R() accepts 0 positional sub-patterns (1 given)
```

The second is what a plain class with no `__match_args__` at all produces, and
is worth showing: "accepts 0 positional sub-patterns" is the message a reader
will actually hit.

Proposal: append to that sentence — "a positional pattern raises
`TypeError: Point() accepts 0 positional sub-patterns (2 given)`" — using
whichever wording fits the sentence.

---

[] Reject

**Section: "Patterns Nest" — the opening sentence contradicts the Class
Patterns section.**

"Everything so far has been one pattern at a time." But `case [first, *rest]`
is a starred pattern inside a sequence pattern, and the Class Patterns section
says of `Point(0, y)`: "The literal and the capture combine in one pattern."
Both are already nesting.

Proposal: "Each section so far introduced one pattern form on its own." Then
the next sentence ("A sub-pattern is itself a pattern, so any of these forms
can sit inside any other") lands as the new idea it is.

Related, in the same section: the prose for the second case says "The second
case alternates two class patterns and binds `n` from either", but the case is
`[Point(0, n) | Point(n, 0)]` — the alternation sits inside a *one-element*
sequence pattern, which is why `survey([Point(0, 5)])` matches and
`survey([Point(0, 5), Point(1, 1)])` would not. Worth a clause.

---

[] Reject

**Section: "Exhaustive Matching" — the chapter never says what
`assert_never()` does at runtime.**

Everything the chapter says about `assert_never()` is static: "the type checker
will ensure the match is exhaustive", "the checker flags `assert_never(shape)`".
A reader can reasonably conclude it is a checker-only marker that vanishes at
runtime. It does not: reaching it raises

```
AssertionError: Expected code to be unreachable, but got: 'x'
```

Verified on the pinned 3.15.

Proposal: one sentence after "the checker flags `assert_never(shape)`":

> If one ever does reach it at runtime — a value that lied about its type —
> `assert_never()` raises `AssertionError`, naming the value it got.

---

[] Reject

**Section: "Exhaustive Matching" — Scala's check is a warning, not an error.**

"Scala's `match`, Kotlin's `when`, and Java's newer switch expressions do check
this, as long as the matched type is a sealed hierarchy the compiler can see in
full." Java 21's switch over a sealed type and Kotlin's `when` used as an
expression are hard compile errors. Scala 2 and Scala 3 emit a warning
("match may not be exhaustive"), which only becomes an error under
`-Xfatal-warnings`. The sentence groups them as equivalent.

This matters here because the paragraph exists to argue that Python's
`assert_never()` plus a checker is as good as a `sealed` keyword — and a Scala
warning is exactly the same strength of guarantee that `ty` gives, which is a
better parallel than the sentence currently draws.

Proposal: "...do check this, as an error in Java and Kotlin and a warning in
Scala, as long as the matched type is a sealed hierarchy the compiler can see
in full."

---

[] Reject

**Section: "Mapping Patterns" — `case nonevent:` is named for something the
type annotation rules out.**

`handle()` takes `dict[str, object]`, so the final capture cannot receive a
non-mapping. The only thing that reaches it is a dictionary with no `"type"`
key, and the output line is `Not an event: {'button': 1}`. A reader who just
read (two paragraphs earlier) that `case {}` is a catch-all for any mapping
will wonder why this listing uses a bare capture instead, and the name
`nonevent` suggests the answer is "to catch non-dicts", which is wrong.

Proposal: rename the case to say what it means —
`case unknown: return f"Unrecognized event: {unknown}"` — or use `case {}:`
here and let it be the demonstration of the catch-all the prose just described.
Cost: the `#: Not an event: {'button': 1}` marker and the second assertion in
`test_mapping_patterns.py` both change.

---

[] Reject

**Section: "When Not to Match" — `STATUS.get(status, f"Status {status}")`
builds its default on every call.**

Context: I changed this section's claim from "a dictionary is shorter and
faster" to a statement about how the two scale, because "faster" is
measurably backwards for the listing as written. You should see the numbers.

`min` of 7 `timeit` repeats, 200,000 calls each, on the pinned 3.15 (three
independent runs, all within 1%):

| call | dict `.get()` | `match` |
|---|---|---|
| hit, first case (200) | 0.0298 | 0.0069 |
| hit, last case (500) | 0.0302 | 0.0091 |
| miss (301) | 0.0299 | 0.0275 |

The dictionary version is ~4x slower on hits. Two causes: `.get()` costs a
global load, an attribute load, and a call, and the `f"Status {status}"`
default argument is built eagerly on *every* call, including the hits where it
is thrown away. Rewriting it EAFP (`try: return STATUS[s] / except KeyError:`)
brings the hits to 0.0084, roughly level with `match`, at the cost of a slow
miss (0.0574).

`dis` confirms the mechanism on the `match` side: a literal `match` compiles to
one `COMPARE_OP` per case, no jump table, so it is linear in the number of
cases. Crossover measured at 4-5 cases; at 50 cases `match` is ~10x slower than
the dict.

Proposal: leave the prose as I rewrote it, but consider making the listing's
lookup EAFP, which is what the book's own style guide asks for ("Prefer EAFP
over LBYL for ... a dict lookup") and removes the eager-default waste:

```python
def describe(status: int) -> str:
    try:
        return STATUS[status]
    except KeyError:
        return f"Status {status}"
```

That is four lines instead of one, which weakens the "shorter" argument, so I
did not apply it. Your call which of the two properties the listing should
demonstrate.

---

[] Reject

**Chapter-wide: `match`, `case`, and `type` are soft keywords, and the chapter
never says so.**

`match = re.match(...)` is legal and extremely common in real code, and the
book's own style guide has a rule about it ("Never name identifiers after soft
keywords. No functions, parameters, or variables named `match`, `case`, or
`type`"). This chapter is the only place in the book where that rule has a
natural home, and it also explains why `match` could be added to Python at all
without breaking existing code.

Proposal: two sentences at the end of the chapter introduction, after the
Control Flow link:

> `match` and `case` are *soft* keywords: they only act as keywords in this
> statement, so existing code that uses `match` as a variable name still runs.
> That is also a reason not to write such code — a local named `match`
> shadows nothing but reads like the statement.

---

[] Reject

**Section: "Exercises" — the technique exercise 5 needs is only in the
Solutions, and the chapter's most memorable lesson has no exercise.**

Two separate problems.

First, exercise 5 asks for `quadrant()` "with one `case` per sign combination,
using `|` alternations and no guards". `Solutions/13_Pattern_Matching.md`
answers it by matching on a *transformed subject*:

```python
match sign(p.x), sign(p.y):
    case 0, 0:
        ...
    case (0, _) | (_, 0):
        ...
```

The chapter teaches neither piece of that. It never matches on anything but a
plain parameter, and it never shows the bare-comma forms `match a, b:` and
`case 0, 0:` — every sequence pattern in the chapter is written with brackets.
"Transform the subject so the patterns can be literals" is one of the most
useful `match` techniques there is, and it currently exists only in the answer
key.

Proposal: add a short paragraph to "Sequence Patterns" noting that
`case 0, 0:` and `case [0, 0]` are the same pattern and that the subject can be
any expression, including a tuple built on the spot — `match sign(x), sign(y):`.
That one paragraph makes exercise 5 answerable from the chapter and pays for
itself elsewhere.

Second, the exercise set has nothing on capture-vs-value patterns, which is the
chapter's sharpest lesson (`value_patterns.py`, the `DEFAULT` trap) and the one
a reader is most likely to hit in real code. Proposed exercise:

> Give `Signal` a third member and write `act()` so it compares against a
> module-level constant `FALLBACK: Final[Signal]`. Run it, see that the
> constant captures instead of comparing, then fix it two ways: with a dotted
> name, and with a guard.

---

## Cross-chapter

**`Chapters/34_Composite_and_Interpreter.md`, line 466.**

The sentence

> every alternative in a `|` must bind the same set of names,
> so binding `left` in one and `right` in the other is a `SyntaxError` rather than a runtime surprise
> (see [Alternatives and Capture](13_Pattern_Matching.md#alternatives-and-capture)).

points at a section of chapter 13 that does not contain that rule. Chapter 13
teaches it in "Patterns Nest". The anchor exists, so `heading_links.py` passes
and nothing catches it.

If you take the recommended fix in the "Alternatives and Capture" finding above
(state the rule where `|` is introduced), chapter 34 needs no edit at all and
this note can be ignored. Otherwise, the change I would make in chapter 34 is
exactly:

- `13_Pattern_Matching.md#alternatives-and-capture`
  → `13_Pattern_Matching.md#patterns-nest`

and change the link text from `Alternatives and Capture` to `Patterns Nest`.

I did not touch chapter 34.
