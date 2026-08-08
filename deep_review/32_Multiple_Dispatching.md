[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Line numbers refer to `Chapters/32_Multiple_Dispatching.md` *after* the fixes
this review already applied (see the note at the end for what those were).

---

[] Reject

**Line 4-9 vs. line 258 — the opening promises an expression system that
chapter 34 delivers.**

The chapter opens on "a system that parses and executes mathematical
expressions ... `Number + Number`", and line 258 says the reflected-operator
section "answers the `Number + Number` question that opened this chapter." It
answers the dispatch half. The expression system itself is `expr.py` in
[Composite and Interpreter](34_Composite_and_Interpreter.md), which builds
exactly that and links back here for the mechanism.

Proposed, appended to the `radd_dispatch.py` discussion:

> [Composite and Interpreter](34_Composite_and_Interpreter.md#the-interpreter-pattern)
> builds the expression system this chapter opened with, using these two
> methods to let Python's own parser assemble the tree.

Check the anchor against that chapter's actual heading before applying.

---

[] Reject

**Line 225 — `## One Type or Many` holds three unrelated topics, and chapter 34
links into the wrong one.**

Everything from line 225 to line 403 sits under one heading:

| lines | topic |
|---|---|
| 227-240 | `singledispatch` (MRO) vs. the table (exact) |
| 242-256 | the `isinstance()` ladder, and when the method version wins |
| 258-350 | Python's reflected operators, `NotImplemented`, `radd_dispatch.py` |
| 352-403 | testing the two versions against each other |

Only the first two are "one type or many." The third is the chapter's second
big idea and gets no heading; the fourth is a testing section.

This is not only a table-of-contents problem. `Chapters/34_Composite_and_
Interpreter.md` links to `32_Multiple_Dispatching.md#one-type-or-many` twice
(line 280 and exercise 6, line 616), both times meaning the reflected-operator
idiom. A reader following either link lands on the `singledispatch` comparison
and has to scroll past two more topics to reach what the link promised.

Proposed:

- `## One Type or Many` keeps lines 227-256.
- New `## Operators Dispatch Twice` (or `## Reflected Operators`) at line 258.
- New `## Testing Both Versions` at line 352.

Price: chapter 34's two links must be repointed (logged under Cross-chapter
below). `heading_links.py` will not catch it, because `#one-type-or-many` still
exists — it just means something narrower.

---

[] Reject

**No conclusion.**

The chapter ends on the testing paragraph and goes straight to `## Exercises`.
Every claim is made, but nothing collects them, and the last thing a reader
sees is a note about `if __name__ == "__main__"`.

The insight worth ending on is already latent in the chapter and never stated:
all three techniques here — the `eval_*()` family, the `OUTCOME` table, and
`__add__`/`__radd__` — are the same move, which is turning one unresolved type
into a second dispatch. Python gives you that second dispatch for free in
exactly one place, the binary operators, and everywhere else you choose between
paying for it in methods or paying for it in data. Four or five lines under a
heading named for that idea, rather than "Conclusion."

---

[] Reject

**`arena.py`, lines 55-68 — both `Any`s here are removable, and the chapter
never says why they stay.**

`arena.py` declares `item_pair_gen(base: type, n: int) -> Iterator[tuple[Any,
Any]]` and `duel(item1: Any, item2: Any)`. Neither `Any` is forced. This
version type-checks clean under `ty` and produces byte-identical output to the
current one (verified against both `paper_scissors_rock_table.py` and the
seeded 10-duel loop):

```python
# arena.py
import random
from collections.abc import Iterator
from typing import Any, Protocol
from outcome import Outcome

class Competitor(Protocol):
    def compete(self, item: Any) -> Outcome: ...

def item_pair_gen[T](base: type[T], n: int) -> Iterator[tuple[T, T]]:
    items = base.__subclasses__()
    for _ in range(n):
        yield random.choice(items)(), random.choice(items)()

def duel(item1: Competitor, item2: Competitor) -> None:
    print(f"{item1} <--> {item2} : {item1.compete(item2)}")
```

Price of the change, which is why it is a proposal and not an applied fix:

- `arena.py` currently has no dependency on `outcome.py`; the `Competitor`
  protocol adds one.
- `duel(item1, item2)` in `paper_scissors_rock.py` would stop type-checking,
  because that version's `Item` base deliberately declares no `compete()`. You
  would have to declare `compete()` on that `Item`, which weakens the very
  point the chapter makes about the method version two paragraphs later.

The narrow subset that costs nothing is the generic `item_pair_gen[T]` alone:
it removes one `Any`, keeps `arena.py` dependency-free, and works with both
versions unchanged. If you want only one change here, take that one.

---

[] Reject

**Lines 156-160 — a `Protocol` *would* catch the missing method, and the
chapter should say so plainly.**

The paragraph now reads (after this review's edit):

> `Item` declares neither `compete()` nor any `eval_*()` method,
> so `Any` is the only annotation available short of a `Protocol` naming all
> four methods.
> With `Any`, a checker cannot tell you when a class is missing one of the nine
> answers ...

The clause about the `Protocol` is deliberately terse, because the full point
needs a decision from you. Verified with `ty` 0.0.65: a four-method
`Competitor` protocol catches a class missing `eval_paper()` **twice** — once
at the definition site, inside the incomplete class's own `compete()` body, and
again at every call site that passes it:

```
error[invalid-argument-type]: Argument to bound method `Competitor.eval_paper`
  is incorrect
   |         return item.eval_paper(self)
   |                                ^^^^ Expected `Competitor`, found `Self@compete`
info: type `Broken` is not assignable to protocol `Competitor`
info: └── protocol member `eval_paper` is not defined on type `Broken`
```

So the honest statement of the tradeoff is: the method version *can* be
statically complete, at the cost of a protocol that repeats every method name,
and the table version needs no such declaration because its nine answers are
data. That is a stronger argument for the table than "a checker cannot help
you," which is only true of the `Any` spelling the chapter chose.

Two ways to cash this in; recommending the first:

1. Add one sentence after line 160: "A `Protocol` listing the four methods
   would restore the checking, at the price of a declaration that repeats every
   class's method names; the table version gets the same guarantee for free,
   because its answers are data rather than methods."
2. Show the protocol as a third short listing. More convincing, and more pages.

---

[] Reject

**Line 218-223 — the exact-match claim is asserted three times in the book and
demonstrated nowhere.**

> The match is on classes exactly,
> so a subclass of `Paper` finds none of `Paper`'s rows.

Chapter 31 makes the same claim about `type(event)`, chapter 37 relies on it for
`bins[type(t)]`, and none of the three shows it happening. It is the single most
surprising property of the technique — a reader arriving from `singledispatch`,
which the section compares it to four lines earlier, will assume MRO matching —
and it is the one property the reader is most likely to discover as a
production bug. Six lines appended to `paper_scissors_rock_table.py` would fix
that for all three chapters:

```python
class Origami(Paper):
    pass
try:
    Origami().compete(Rock())
except KeyError as e:
    print(type(e).__name__)
#: KeyError
```

Cost: it changes the `#:` block of a listing whose output currently matches
`paper_scissors_rock.py` line for line, and that identity is itself doing work
(it is what the two-versions-agree test formalizes). Putting the demo in its
own small listing after the table avoids that, at the price of a fourth file.
Recommending the separate listing.

---

[] Reject

**`test_paper_scissors.py`, lines 378-390 — the loops hide every failure after
the first.**

```python
@pytest.mark.parametrize("module", [table, methods])
def test_matches_expected(module: ModuleType) -> None:
    for (player, opponent), result in EXPECTED.items():
        assert compete(module, player, opponent) == result
```

The style skill's rule is "so pytest reports each case independently rather
than a single test hiding after the first failing input." Here the
parametrization is over the *module*, and the nine matchups are a loop inside,
so one wrong cell reports as one failed test and conceals the other eight —
which is exactly the situation exercise 1 puts a reader into while filling in
`Lizard`'s rows. Proposed:

```python
MATCHUPS: Final[list[tuple[str, str, Outcome]]] = [
    (p, o, r) for (p, o), r in EXPECTED.items()
]

@pytest.mark.parametrize("module", [table, methods])
@pytest.mark.parametrize("player, opponent, expected", MATCHUPS)
def test_matches_expected(module: ModuleType, player: str,
                          opponent: str, expected: Outcome) -> None:
    assert compete(module, player, opponent) == expected

@pytest.mark.parametrize("player, opponent, expected", MATCHUPS)
def test_both_versions_agree(player: str, opponent: str,
                             expected: Outcome) -> None:
    assert (compete(methods, player, opponent)
            == compete(table, player, opponent))
```

Reported rather than applied: it takes the run from 6 dots to 33, and whether
that reads as thoroughness or as noise in a printed book is your call.

---

[] Reject

**Exercise 4 — it exercises the helper, not the chapter.**

Exercise 4 asks for a `Counter` parameter on `item_pair_gen()` and a tally of
how often `Lizard` appears. It is a fine exercise about optional mutable
parameters and lazy generators, and it teaches nothing about dispatching on two
types. The set otherwise runs 1-2-3 on `Lizard` and 5 on reflected operators,
so nothing covers the two claims the chapter argues hardest for: exact-type
matching, and `singledispatch`'s MRO matching as the contrast.

Proposed replacement or addition:

> Subclass `Paper` as `Origami` and duel it against `Rock` in the table version.
> Explain the `KeyError` in terms of how the lookup matches.
> Then make the table tolerate subclasses by walking `type(item).__mro__` for
> the first class that has a row, and say what that costs: which of the two
> properties on page N you have just given up.

Keeping exercise 4 as well is fine; the point is that the set should cover
exact matching somewhere.

---

[] Reject

**Lines 227-240 — `functools.singledispatchmethod()` is missing, and it is
Python's built-in double dispatch.**

The section says:

> For dispatch on one argument's type, `functools.singledispatch` ... gives you
> open, per-type functions.
> For dispatch on two or more types at once,
> the table above is the idiomatic answer.

That skips the construct that sits exactly between them. A
`singledispatchmethod` dispatches once on `self` through ordinary method
resolution and a second time on its argument through `singledispatch` — the
same two dispatches the `eval_*()` family hand-rolls, with the second one
supplied by the stdlib. `WhatsNew_Candidates.md` line 49 already flags this
chapter for it.

Verified working, and it reproduces the seeded ten-duel output exactly:

```python
# paper_scissors_rock_sdm.py
import random
from functools import singledispatchmethod
from typing import Any
from arena import duel, item_pair_gen
from outcome import Outcome

class Item:
    def __str__(self) -> str:
        return type(self).__name__

class Paper(Item):
    @singledispatchmethod
    def compete(self, item: Any) -> Outcome:
        raise TypeError(f"no rule for {type(item).__name__}")

class Scissors(Item):
    @singledispatchmethod
    def compete(self, item: Any) -> Outcome:
        raise TypeError(f"no rule for {type(item).__name__}")

class Rock(Item):
    @singledispatchmethod
    def compete(self, item: Any) -> Outcome:
        raise TypeError(f"no rule for {type(item).__name__}")

def rule(winner: type, loser: type) -> None:
    winner.compete.register(loser, lambda self, item: Outcome.WIN)
    loser.compete.register(winner, lambda self, item: Outcome.LOSE)

for cls in (Paper, Scissors, Rock):
    cls.compete.register(cls, lambda self, item: Outcome.DRAW)
rule(Paper, Rock)
rule(Rock, Scissors)
rule(Scissors, Paper)
```

Three teaching points come with it, and they are the reason it earns space:

- Each class needs its own `@singledispatchmethod`. Registering on
  `Item.compete` gives one shared dispatcher, so the first dispatch never
  happens. That is a near-miss a reader will write.
- The registrations cannot go in the class bodies as `@compete.register` with
  an annotated `_`, because `singledispatch.register` resolves the annotation
  eagerly and `Rock` does not exist yet while `Paper`'s body runs. PEP 649
  laziness does not save you here. The `register(cls, func)` call after all
  three classes exist is what works.
- It matches on the MRO, like `singledispatch` and unlike the table, so it
  answers the "which pairings are covered" question the section already raises.

Relevant on 3.15 specifically: gh-143535 (PR python/cpython#144615) made an
unbound `Cls.method(instance, arg)` dispatch on `arg` rather than on
`instance`, so `_singledispatchmethod_get._dispatch_arg_index` is 1 for
class-level access. Confirmed on 3.15.0b2: `Paper.compete(p, r)` and
`p.compete(r)` now agree.

Placement is yours. Shortest version: three sentences in `One Type or Many`
naming the construct and the shared-dispatcher trap, no listing.

---

[] Reject

**`paper_scissors_rock_table.py`, lines 176-179 — `self.__class__` where the
rest of this cross-chapter thread uses `type(x)`.**

The exact-type dict-dispatch thread runs 31 → 32 → 37. Chapter 31 writes
`self.transitions[type(event)]` and its prose says "the lookup keys on
`type(event)` exactly"; chapter 37 writes `bins[type(t)]`. Chapter 32 writes
`OUTCOME[self.__class__, item.__class__]` and `self.__class__.__name__`. Same
idea, three spellings; a reader following the thread has to notice they are the
same operation.

Across `Chapters/`, `type(self)` appears in 12, 14, 31, and 33; `self.__class__`
appears only in 32 (three times) and 33 (twice), so 32 is most of the minority
spelling.

Proposed, in both listings in this chapter:

```python
        return OUTCOME[type(self), type(item)]
    def __str__(self) -> str:
        return type(self).__name__
```

Reported rather than applied because `Solutions/32_Multiple_Dispatching.md`
carries three more copies of `self.__class__` (exercises 1 and 4) and this
review may not edit `Solutions/`; the two should change together, and the
choice is a book-wide one.

---

[] Reject

**Lines 254-256 — "will not fit in a table cell" is not a real constraint, and
chapter 31 already showed why.**

> Use the double-dispatch version only when a combination needs substantial,
> type-specific code that will not fit in a table cell.

A table cell holds anything, including a function. Chapter 31's engine is a
table of `Callable[..., bool]` and `Callable[..., None]`, so a reader who has
just come from that chapter knows the escape hatch and will not believe this
criterion. Changing `OUTCOME` to `dict[tuple[type[Item], type[Item]],
Callable[[Item, Item], Outcome]]` absorbs arbitrarily large behavior.

The real criterion is about where the behavior belongs, not how big it is.
Proposed replacement:

> Use the double-dispatch version when the behavior for a combination belongs
> to the class rather than to the pairing:
> when it reads the object's own state, or when a subclass should be able to
> override one combination and inherit the rest.
> A table cell can hold a function, so size alone never forces the choice.

---

[] Reject

**`paper_scissors_rock.py`, lines 85-123 — the `eval_*()` comments invite
exactly the misreading the prose warns about.**

Every `eval_*()` body carries a comment of the form

```python
    def eval_scissors(self, item: Any) -> Outcome:
        # Item was Scissors; this is Paper's case
        return Outcome.WIN
```

and then lines 148-154 tell the reader that `WIN` is *Scissors'* result, not
Paper's, and that "if you misread that convention, every result in the class
appears backward." "this is Paper's case" is that misreading spelled out in the
code: it reads as "this is Paper's answer," which is the opposite of what the
line returns. The prose is fighting the comments.

Proposed: make the comments say whose answer it is, e.g.

```python
    def eval_scissors(self, item: Any) -> Outcome:
        # Second dispatch: the caller was Scissors, and it wins
        return Outcome.WIN
```

with the same shape in all nine bodies (`... and it loses`, `... and it draws`).
That also makes the `# First dispatch:` comments on `compete()` read as one
series with the second-dispatch comments.

Reported rather than applied because the house-style skill says not to edit
existing example comments without being asked about those specific comments.
This block is the ask.

---

[] Reject

**Lines 401-403 — the paragraph explains the `__main__` guard but not the
`getattr()` trick, which is the stranger half.**

> Importing both modules works cleanly because each guards its demonstration
> loop with `if __name__ == "__main__"` ...

The thing a reader stumbles on in that test is one line earlier:

```python
    result: Outcome = getattr(module, player)().compete(
        getattr(module, opponent)())
```

Two modules each define classes named `Item`, `Paper`, `Scissors`, and `Rock`,
and they are four distinct pairs of classes. The test never imports a class by
name; it looks the name up on whichever module it was handed, so the same
nine-row `EXPECTED` drives two unrelated hierarchies. Proposed sentence to add
before the existing one:

> Neither hierarchy is imported by name.
> `getattr(module, player)` looks the class up on whichever module the test was
> handed, so one table of nine expected answers drives two independent sets of
> `Paper`, `Scissors`, and `Rock` classes.

---

[] Reject

**Lines 265-268 — the `r` prefix invites a collision with the `i` prefix.**

> Every arithmetic and bitwise operator has a reflected form,
> named by inserting an `r` before the operator's name: `__rsub__()`,
> `__rmul__()`, `__rtruediv__()`.

The same operators also have an in-place form named by inserting an `i`
(`__isub__()`, `__imul__()`), and the two prefixes are one letter apart in
otherwise identical names. A reader who has met `__iadd__()` will guess the
prefixes mean variations on the same theme; they are unrelated mechanisms, and
`__iadd__()` never participates in the two-step dispatch this section is about.

Proposed, appended to that sentence:

> Do not confuse this with the in-place forms, `__iadd__()` and its siblings,
> which serve `+=` and take no part in the reflected fallback.

---

[] Reject

**Opening, line 15 — "effectively" hedges a sentence that already trails off.**

> You end up detecting some types manually and effectively producing your own
> dynamic binding behavior.

"effectively" is a hedge with no work to do, and "producing your own dynamic
binding behavior" restates the previous sentence without adding the concrete
thing the reader will actually write. Proposed replacement:

> You end up testing the remaining types by hand,
> writing out the dispatch the language performs for the first one.

Reason for reporting rather than applying: this sentence carries over from
*Thinking in Java* and you may want it verbatim.

---

## Cross-chapter

**`Chapters/34_Composite_and_Interpreter.md` — two links to a heading that is
about to mean something else.**

Only if the section split above is applied. Both of these link to
`32_Multiple_Dispatching.md#one-type-or-many` and both mean the reflected-
operator material, which moves to its own heading:

- line 280: "The reflected methods depend on the operator dispatch from
  [Multiple Dispatching](32_Multiple_Dispatching.md#one-type-or-many)"
- line 616 (exercise 6): "([Multiple Dispatching](32_Multiple_Dispatching.md#one-type-or-many)
  shows the idiom)"

Change both to the new anchor, e.g. `#operators-dispatch-twice`.

**`Chapters/34_Composite_and_Interpreter.md` — no edit needed, but the thread
now agrees.**

`expr.py` annotates `__radd__()` as `-> Add` and `__rmul__()` as `-> Mul`,
which is right. Before this review, chapter 32 said `Any` was "the honest
choice" for exactly these signatures, so a reader doing 34's exercise 6 ("return
`NotImplemented` for a non-`int` operand ... [32] shows the idiom") would have
been told to widen `-> Add` to `-> Any`. Chapter 32 now teaches the precise
annotation, so the two ends match. Nothing to change in 34; noting it so a
future edit to either end does not undo the agreement.

**`Chapters/31_State_Machines.md` and `Chapters/37_Pattern_Refactoring.md` —
spelling of the exact-type key.** See the `self.__class__` block above. If you
take that change, 32 joins 31's `type(event)` and 37's `type(t)`; if you reject
it, the three chapters keep two spellings for one idea and it is worth a
sentence somewhere saying they are the same.

**`Solutions/32_Multiple_Dispatching.md` — exercise 5 has no solution.**

The Solutions file stops at exercise 4. Exercise 5 (`__sub__()`/`__rsub__()`) is
unanswered. It is also the only exercise covering the reflected-operator half of
the chapter, so the gap is on the more error-prone material. Note that this
review rewrote exercise 5 slightly: `__rsub__()` is now told to handle only
`int` and `float`, because the chapter has just taught that Python never calls
the reflected form for two operands of the same type, and the old wording
("anything but a `Meters`, an `int`, or a `float`") asked for a dead `Meters`
branch.

**`Solutions/32_Multiple_Dispatching.md`, section 3 — stale test names.**

> With this `EXPECTED` in place, `test_table_version_matches_expected()`,
> `test_method_version_matches_expected()`, and `test_both_versions_agree()`
> all pass unchanged ...

The first two no longer exist. `test_paper_scissors.py` in the chapter has a
single `test_matches_expected()` parametrized over `[table, methods]`. Proposed:
"`test_matches_expected()`, parametrized over both modules, and
`test_both_versions_agree()` pass unchanged: neither hardcodes the number of
item types."

**`Solutions/32_Multiple_Dispatching.md`, sections 1 and 4 — `OUTCOME` key
annotation.**

This review tightened the chapter's `OUTCOME` to
`Final[dict[tuple[type[Item], type[Item]], Outcome]]`, per the house rule to use
`type[C]` when a class object is stored. Both solutions still declare
`dict[tuple[type, type], Outcome]` (and section 4 drops the `Final` as well).
They type-check as they stand; they just no longer match the chapter.

---

## Applied in this pass, for the record

Four fixes were applied to `Chapters/32_Multiple_Dispatching.md` directly:

1. `radd_dispatch.py` now annotates `__add__()` and `__radd__()` as `-> Meters`
   instead of `-> Any`, and the paragraph justifying the annotation was
   rewritten. The old text claimed the precise annotation was
   `Meters | NotImplementedType` and that `Any` was therefore "the honest
   choice." Typeshed declares `NotImplemented` with a type inheriting `Any`
   (`class _NotImplementedType(Any)` in `builtins.pyi`, kept that way on
   purpose — python/typeshed#11457 was closed as not planned), precisely so a
   binary dunder can declare its real return type. The stdlib stubs do exactly
   that: `timedelta.__add__` is annotated `-> Self`, not a union. Verified clean
   under `ty` 0.0.65, mypy, and pyright.
2. The "Note what the `Any` annotations cost" paragraph dropped its false claim
   that "nothing more precise would let `item.eval_scissors(self)` type-check"
   and its misleading `AttributeError`-vs-`KeyError` contrast (both are runtime
   errors; the table's advantage is that the answers are collected, not that its
   failure mode is better). The `KeyError` point was already made at line 221.
3. `OUTCOME`'s key type tightened to `tuple[type[Item], type[Item]]`.
4. "Python's own operators already *contain* a two-step dispatch" → "*perform*".

Runtime claims spot-checked on 3.15.0b2 and all correct as written: the
same-type skip of the reflected call; the subclass-overriding-the-reflected-
method reversal; `str` having no `__radd__`; `TypeError` propagating out of
`__add__()` instead of falling through.
