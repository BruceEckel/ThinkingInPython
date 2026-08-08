When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**`utils/result.py`, `Err.bind`: binding the class's own `E` makes a chain
that changes error type fail the checker, and `Ok.bind` allows it.**

```python
    def bind[B](
        self, func: Callable[..., Result[B, E]]
    ) -> Err[E]:
```

`E` here is the class parameter, so `Err[str].bind(f)` requires `f` to return
`Result[B, str]`.
`Ok.bind` declares its own `[B, E]`, so it accepts any error type.
The result is that a chain whose steps report different error types is
rejected, on the `Err` half of the union only:

```python
def start(i: int) -> Result[int, str]: ...
def next_step(n: int) -> Result[int, ValueError]: ...
start(1).bind(next_step)   # error, from Err.bind
```

`ty` reports `element 'Err[ValueError]' of union 'Ok[int] | Err[ValueError]'
is not assignable to 'Ok[Unknown] | Err[str]'`, even though its own inferred
answer for the expression, `Ok[int] | Err[ValueError] | Err[str]`, is exactly
right.

Proposed change (verified: chapters 42 and 44 both still check clean, and the
mixed chain above then type-checks):

```python
    def bind[B, F](
        self, func: Callable[..., Result[B, F]]
    ) -> Err[E]:
```

`utils/` again, so reported rather than applied.
The counter-argument, which is why I am not pushing hard: forcing one error
type per chain is defensible discipline, and the chapter's running example
never mixes them. But if that is the intent it should be stated, because right
now the restriction reads as an accident of which method declared its own
parameters.

---

[] Reject

**`utils/result.py`: adding `@final` to `Ok` and `Err` removes the narrowing
limitation this chapter apologises for, and improves chapter 44 too.
This is a `utils/` change, so it is reported rather than applied.**

The section "Attaching Context to an Exception" ends by explaining that
`isinstance(result, Err)` gives `object` for `result.error` instead of
`Exception`.
That is not a checker limitation. It is a consequence of `Ok` and `Err` being
open classes: `ty` cannot rule out a hypothetical subclass of both, so a
positive `isinstance()` leaves the intersection alive and erases the field
type.

Measured on `ty` 0.0.65 with the current `result.py`:

| form | reveals |
|---|---|
| `isinstance(r, Err)` then `r.error` | `object` |
| `isinstance(r, Ok)` then `r.answer` | `object` |
| `isinstance(r, Ok)` else `r.error` | `Exception` |
| `match`, `case Ok(a)` | `object` |
| `match`, `case Err(e)` | `Exception \| Unknown` |

With `@final` on both classes (`from typing import final`, decorator above
`@dataclass(frozen=True)`), every one of those five becomes exact: `int`,
`int`, `Exception`, `int`, `Exception`.
I built a scratch tree holding chapters 42 and 44 plus the modified `utils/`
and ran `ty` over all of it: clean, no other change needed.

`@final` is also the truth about these two classes. Nothing in the book
subclasses either, subclassing `Ok` would break the `Result` alias's meaning,
and `thinking-in-python-skill.md` already tells you to use the strongest
construct that fits.

Proposed change to `Chapters/42_Functional_Error_Handling.md`'s
`# utils/result.py` block:

```python
# utils/result.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import final

@final
@dataclass(frozen=True)
class Ok[A]:
    ...

@final
@dataclass(frozen=True)
class Err[E]:
    ...
```

If you take it, the paragraph I rewrote after `noted_result.py` (manifest
item 9) should shrink to one sentence, because the trap it describes goes away.
Cost: `make sync` regenerates `Examples/utils/result.py`; chapter 44's
`slope_result.py` is the only other importer and it gets strictly better
narrowing; the listing grows one import and two lines.

---

[] Reject

**New listing proposal: `must_unwrap.py`, the near-miss the reader will write
first.**

"A Result Type" now states that `unwrap()` exists only on `Ok` and that this
is what forces the caller to narrow (manifest item 2). It states it; nothing
shows it. The book has an established form for exactly this — a line that
deliberately misbehaves carrying `# type: ignore`, as in chapters 03, 05 and
08 — and it works here.

Verified: runs, `ruff` clean at 70, `ty` clean, output deterministic.

```python
# must_unwrap.py
from result import Err, Ok, Result

def func_a(i: int) -> Result[int, str]:
    return Err(f"func_a({i})") if i == 1 else Ok(i)

print(hasattr(Ok(1), "unwrap"), hasattr(Err("x"), "unwrap"))
#: True False
try:
    func_a(1).unwrap()  # type: ignore
except AttributeError as e:
    print(e)
#: 'Err' object has no attribute 'unwrap'
```

Two notes on the code. The bare `# type: ignore` is required and is the point:
without it `ty` fails the line with `Attribute 'unwrap' is not defined on
'Err[str]' in union 'Result[int, str]'`, so the prose can say that the comment
is suppressing a real error the reader would otherwise never get past.
(A bracketed `# type: ignore[unresolved-attribute]` does *not* suppress it
under `ty` 0.0.65; only the bare form works.)
The `hasattr` line is what makes the asymmetry visible at runtime rather than
asserted in prose.

Where it goes is your call, which is why this is a proposal.
My suggestion is immediately after `returning_result.py`, before the
`int | None` comparison, so the reader meets the enforcement at the moment the
chapter first claims it.
Alternative, if you would rather not spend a listing: drop the `hasattr` line
and fold the remaining four lines into the existing `returning_result.py`
block, which costs no new file but gives that listing two jobs.

---

[] Reject

**"A Result Type": the chapter says "Ignore `bind()` for the moment" and then,
two paragraphs later, shows a test that asserts what `bind()` does.**

Line 144: "Ignore `bind()` for the moment."
Line 204-205: "The tests check `unwrap()`, and that `bind()` chains a success
and short-circuits a failure", followed by `test_result.py`, two of whose three
tests are about `bind()`.
`bind()` is not explained until "Composing With bind", two sections later.
A reader who took the instruction literally cannot read two thirds of the
listing; one who did not was told to.

Two ways out. I recommend the first.

**Option A: move the whole `test_result.py` listing and its lead-in paragraph
into "Composing With bind",** placed after `composing_with_bind.py` and before
`test_composing.py`.
The lead-in ("Because failures are values, you can assert on them directly,
with no `pytest.raises()`") reads at least as well there, since by that point
the reader has seen three failures travel through a chain.
"Ignore `bind()` for the moment" then means what it says, and the reader meets
`bind()` once, in one place.
Cost: nothing outside this chapter. `test_result.py` imports only `result`, so
it does not care where it sits, and no chapter links to a heading between the
two points.

**Option B: split the listing.** Keep `test_success_unwrap` where it is
(renaming the file, since one test per file is the book's rule and a
one-assert `test_result.py` in two places would collide), and put the two
`bind` tests in "Composing With bind".
Cheaper to read, more files to carry.

---

[] Reject

**"The returns Library" holds the chapter's conclusion under a heading about a
third-party library.**

The section is three paragraphs. The first is about `returns`. The second and
third are the chapter's closing argument — exceptions for the truly
exceptional, `Result` for the failures that are part of a function's job —
and have nothing to do with the library. A reader skimming headings for "so
when do I use this?" finds a library name.

Proposed change: split after the first paragraph and give the remainder its
own heading, e.g.

> ## Which Failures Get a Result
>
> This style does not replace exceptions everywhere.
> ...

Checked before proposing: the inbound anchors from other chapters are
`#a-result-type` (20, 46, 47), `#matching-on-the-error` (43),
`#turning-exceptions-into-results` (44, 46) and `#composing-with-bind` (47).
Nothing links to `#the-returns-library`, and the new heading is additive, so
the split breaks nothing.
The one in-chapter link to `#the-returns-library` is the forward pointer I
added at the end of "Combining Multiple Results" (manifest item 6), which
still lands on the library paragraph and should stay pointing there.

Reported because splitting a section and naming the new one is structure and
voice.
A second thing to consider while you are there: the conclusion states a rule
but names no capability. The deep-review question is what the reader can do at
the end that they could not do at the start, and the honest answer here is
"write a function whose signature admits it can fail, and chain three of
them" — which is worth saying, because it is a real answer and most chapters
cannot give one that concrete.

---

[] Reject

**"Combining Multiple Results" opens at its own maximum difficulty.**

The section has one listing and it is a triple-nested `bind` with three
lambdas, three functions, and a fourth function called at the bottom of the
nest. Every other section in the chapter starts with the smallest thing that
makes the point.

Proposed: precede `combining.py` with the two-input version, so the reader
sees the shape once before it is folded three deep. Verified (runs, `ruff`
clean, `ty` clean):

```python
# combining_two.py
from composing import func_b
from result import Ok, Result
from returning_result import func_a

def pair(i: int, j: int) -> Result[str, str]:
    return func_a(i).bind(
        lambda a: func_b(j).bind(
            lambda b: Ok(f"{a} and {b}")))

if __name__ == "__main__":
    for args in [(7, 5), (1, 5), (7, 2)]:
        print(args, pair(*args))
#: (7, 5) Ok(answer='7 and 5')
#: (1, 5) Err(error='func_a(1)')
#: (7, 2) Err(error='func_b(2)')
```

with a line under it saying that each lambda's parameter is the previous
step's answer, and that the answers stay in scope because the nesting keeps
them there — which is the one thing about this construction a reader does not
get from the three-deep version.

Reported because it adds a listing to a chapter that already has thirteen, and
because you may judge that the nesting explains itself.
Cheaper alternative: keep one listing and add the sentence about lambda
parameters and scope, which is the actual teaching content of the extra
listing.

---

[] Reject

**Exercises: three, all in the `bind` cluster; `@safe`, `add_note()` and the
`Result`-versus-`| None` decision get none.**

Coverage today: 1 extends the `bind` chain, 2 adds `map_error()`, 3 collects
failures instead of short-circuiting. Sections with no exercise: "Turning
Exceptions into Results", "Matching on the Error", "Attaching Context to an
Exception", and the `| None` comparison in "A Result Type".

Proposed additions:

> 4.  Change `@safe` so it takes the exception types it should catch, as in
>     `@safe(ValueError)`, and lets anything else propagate.
>     Show that a `TypeError` raised inside the wrapped function now escapes
>     instead of arriving as an `Err`.
> 5.  Write `load_setting(name, text)` that returns `Result[int, Exception]`
>     and attaches a note naming the setting.
>     Chain two of them with `bind()` and print the notes from whichever one
>     failed. What happens to the note the successful call would have added?
> 6.  Rewrite `func_a()` to return `int | None` instead of `Result[int, str]`
>     and adjust `composing.py` to match.
>     Which of the three failures in the chain can the caller still tell apart,
>     and which have collapsed into each other?

Exercise 4 is the one I would keep if you take only one: it is the direct
follow-through on the `@safe`-catches-everything paragraph I added (manifest
item 8), and it is the difference between the chapter's toy decorator and one
you would ship.
Exercise 6 is the near-miss for the `| None` comparison, which the chapter
currently settles by assertion.

Reported rather than applied because the size of the exercise set is pacing.

---

[] Reject

**The `monad` paragraph is one sentence of dismissal, and chapter 39 sends
readers here specifically for that word.**

`Chapters/39_Pattern_Catalog.md` line 160:

> | [Monad](42_Functional_Error_Handling.md) | Sequence computations inside a
> context such as optionality, error, or async. |

A reader who follows that link arrives at:

> Functional programmers have a name for a type that carries a value plus this
> chaining operation: a *monad*.
> You do not need to know that word to use functional error handling.

The reassurance is right and should stay. But the catalog entry says the point
of the word is that the *same* chaining works for optionality, error and
async, and a reader arriving from there learns nothing about why one word
covers three things.

Proposed addition of one sentence after the existing two:

> What the word buys you is that the shape is reusable:
> `Maybe` chains a value that might be absent, `Result` chains one that might
> have failed, and an async container chains one that has not arrived yet,
> all with the same `bind()`.

Reported rather than applied because the paragraph's brevity looks deliberate
and lengthening it argues against its own last sentence.

---

[] Reject

**Intro, third paragraph: "the type checker reminds every caller to handle it"
is the weakest form of the chapter's strongest claim.**

The line currently reads:

> Failure appears in the return type,
> so the type checker reminds every caller to handle it,
> and a reviewer sees it without reading the body.

"Reminds" is a metaphor for something the checker does literally, and the
literal version is more convincing.
Verified on `ty` 0.0.65 / Python 3.15.0b2: with `func_a` returning
`Result[int, str]`, `func_a(2).unwrap()` is
`error[unresolved-attribute]: Attribute 'unwrap' is not defined on 'Err[str]'
in union 'Result[int, str]'`, and `func_a(2) + 1` is
`error[unsupported-operator]`.
The checker does not remind; it refuses.

Proposed change:

> Failure appears in the return type,
> so the type checker will not let a caller read the answer without dealing
> with the failure first,
> and a reviewer sees it without reading the body.

Reported rather than applied because it is the chapter's opening sentence of
argument and the wording is voice.
(The mechanism itself is now stated in "A Result Type" and the caller-side
hole in the totality paragraph; see the manifest, items 2 and 3.)

---

[] Reject

**`utils/safe.py` carries a top-level demo, against the book's own rule, and
`test_safe.py` re-declares `parse()` because of it.**

`thinking-in-python-skill.md`: "Importable modules carry no top-level demo. If
a module is both a library and a demonstration, split it: a demo-free library
module plus a separate runnable file that imports it and holds the demo."
`utils/safe.py` is the chapter's shared helper *and* holds `@safe def
parse()` plus an `if __name__ == "__main__":` block.
`utils/result.py`, the sibling helper, correctly holds neither.

The cost is visible three listings later: `test_safe.py` opens by defining its
own `parse()` rather than `from safe import parse`, so the same four lines
appear twice in one chapter and the test does not exercise the thing the
chapter just showed.

Proposed change: move the demo out of `utils/safe.py` into a chapter-local
`safe_demo.py` that does `from safe import safe`, leaving `utils/safe.py` as
the decorator alone; then `test_safe.py` imports `parse` from `safe_demo`
instead of redefining it.

`utils/` again, so reported rather than applied.
Note that this affects the prose too: the sentence "Like `result.py`, it lives
in `utils/` and any chapter can import it" currently introduces a listing that
is two things at once, and would introduce one thing after the split.

---

[] Reject

**"Return the Error as a Value", line 63: `int | str` is called a *sum type*,
and the next paragraph explains why it isn't quite one.**

> A union like this is a *sum type*: a value that is one thing or another.

Three sentences later:

> But the distinction depends on the types `int` and `str`, which is fragile.
> If a successful answer were also a string, the two cases collide.

A sum type is a *disjoint* union: the two sides stay apart no matter what they
carry. `int | str` does not, which is the whole reason the next section exists.
Naming it a sum type here and then dismantling it makes the term feel like it
moved.

Proposed change:

> A union like this is Python's untagged spelling of a *sum type*:
> a value that is one thing or another.

The following section now says explicitly that `Ok`/`Err` supply the tag
(manifest item 1), so the two halves of the contrast line up.

Reported rather than applied because "sum type" is the term the PyCon talk
this chapter comes from uses, and you may want it unqualified.

---

[] Reject

**`add_note()` is Python 3.11 and later, and the chapter does not say so.**

Same house-style question raised against chapter 40's `functools.Placeholder`
section: the book targets 3.15, several chapters mark 3.13+/3.15 features
inline, and several do not.
`BaseException.add_note()` (PEP 678) arrived in 3.11, which is old enough that
a call-out may be noise, so this is your convention call rather than a
correction. If you do mark it, the natural spot is
"`BaseException.add_note()` (Python 3.11 and later) avoids the trade."

---

[] Reject

**MANIFEST — not a proposal.
Changes already applied to `Chapters/42_Functional_Error_Handling.md` in this
pass.**

All gates re-run and passing on `ty` 0.0.65 / Python 3.15.0b2:
`validate_output.py --tree build/private/42` (1 ok, 0 failed),
`ruff check` (clean at 70), `ty check` (clean), `pytest` (10 passed, up from 9),
`heading_links.py` ("Anchor links OK"), `banned_phrases.py` ("No banned
phrases found"), and `reflow_prose.py` reports the chapter clean.

**Two extracted files changed, so `Examples/` is out of sync until you run
`make sync`:** `42_Functional_Error_Handling/noted_result.py` and
`42_Functional_Error_Handling/test_combining.py`.

1.  "A Result Type", opening: added that the class is the *tag* that keeps the
    two cases apart, and named the construct (tagged / discriminated union).
    Also corrected "Both are frozen data classes, parameterized over the answer
    type and the error type" — `Ok` is parameterized over the answer type and
    `Err` over the error type, not each over both.
2.  "A Result Type", after `returning_result.py`: added the mechanism behind
    "the caller must unpack the `Result`" — `unwrap()` is defined on `Ok` and
    not on `Err`, so `func_a(i).unwrap()` fails the checker, and using the
    `Result` as a number fails the same way. Both verified.
    The chapter asserted the consequence twice (here and again under `@safe`)
    and never showed the cause.
3.  "A Result Type", totality paragraph: added the caller-side half. The
    paragraph said Python does not enforce totality on the *function*; it did
    not say that a caller can discard the whole `Result` with no complaint.
    Verified: a bare `func_a(3)` statement draws no diagnostic.
4.  "Composing by Hand", after `composing.py`: added the near-miss.
    `Result` is a `type` alias, not a class, so `isinstance(a, Result)` raises
    `TypeError: isinstance() arg 2 must be a type, a tuple of types, or a
    union` at runtime and is rejected by `ty` before that. The chapter's own
    listings narrow with `isinstance(a, Err)` and never say why they name the
    concrete class.
5.  "Composing With bind": explained why `Err.bind`'s signature differs from
    `Ok.bind`'s — `Err` holds no answer, so it cannot name the argument type
    the next step receives. The looser `Callable[..., ...]` is the one place
    in the chapter where a listing departs from the book's precise-types rule,
    and it had no explanation.
6.  "Combining Multiple Results", after `combining.py`: noted that the nesting
    grows with each input and pointed forward to the do-notation mentioned in
    "The returns Library". The chapter raised the problem in this section and
    answered it four sections later with nothing connecting the two.
7.  **Corrected a false claim** in "Composing With bind": ".bind(str) ... the
    chain now holds a bare `str` where a `Result` belongs, which the checker
    flags at the next `bind()`." It does not. Verified: `ty` rejects the
    `.bind(str)` call itself, on that line, for both union variants
    (`Expected '(int, /) -> Result[Unknown, Unknown]', found "<class 'str'>"`).
    Rewritten to say the call is rejected on the spot.
8.  "Turning Exceptions into Results": added a paragraph that `@safe` catches
    `Exception`, so a defect (a misspelled name, a `NameError`)
    comes back as an ordinary `Err`, indistinguishable from bad input, and
    that a production version takes the exception types it should catch. The
    chapter's own conclusion draws the failure/defect distinction that its
    decorator erases, four sections apart, with nothing acknowledging it.
9.  "Attaching Context to an Exception": **corrected a false claim and changed
    `noted_result.py` to match.** The chapter said `ty` "loses the error's
    type through an `Err(...)` pattern and through `isinstance(result, Err)`,
    reporting `object` instead of `Exception`", and used `isinstance` for that
    reason. Half of it is wrong on `ty` 0.0.65: through `match`, `case
    Err(error)` gives `Exception | Unknown`, `error.__notes__` resolves, and a
    bogus attribute is still rejected. I verified the `match` form runs, checks
    clean, and produces byte-identical output, so the listing now uses `match`
    — which is also what `thinking-in-python-skill.md` asks for — and the
    paragraph now states the real cause: a positive `isinstance()` cannot rule
    out a value that inherits from both classes, so the checker keeps the
    intersection and erases the field type.
10. "Attaching Context to an Exception": added that typeshed declares
    `__notes__` on `BaseException` unconditionally (guarded only by
    `sys.version_info >= (3, 11)`, with its own comment "only present after
    add_note() is called"), so reading it on an exception with no notes
    type-checks and then raises `AttributeError`. The chapter already said the
    attribute is absent until the first call; it did not say the checker will
    not warn you, which is what makes it a trap.
11. `test_combining.py`: added the `(7, 2, Err("func_b(2)"))` row. The prose
    says the test confirms "the correct value, or the first failure in the
    chain", and the parametrize list covered the `func_a` and `func_c`
    failures but not `func_b`'s.
12. Ran `reflow_prose.py --write` on this chapter only, so the new prose
    follows Semantic Line Breaks (6 paragraphs re-broken).

Also checked and found clean, so no change was made: no use of the "promise"
metaphor anywhere in the chapter, and the one I typed while drafting item 5
("promises only that an `Err` comes back out") was rewritten to "its return
type states only that"; no "reach for"; no watch-list diction; every `#:`
marker matches stdout on a direct run of each extracted script (all nine
runnable listings run individually, not only through `validate_output.py`);
"Total Function" is capitalized the same way here and in chapter 44; the three
claims about the `returns` library (the cases are named `Success` and
`Failure`, it ships the same `safe` decorator, and it has do-notation via
`Result.do()`) are all correct against its current documentation — the package
is not installed in this venv, so this was checked against the library's docs
rather than its source; the blank line after the `# slug.py` marker in
`exceptions_lose_data.py` and `sum_type.py` matches 90 other import-less
listings in the book and is not a deviation; and the chapter's `Result`,
`@safe` and `add_note` threads agree with their other ends in chapters 20, 39,
43, 44, 46 and 47.
