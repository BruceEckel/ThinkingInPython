[[Reviewed]]
# Deep review: 32_Multiple_Dispatching.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Say what a reader must not write instead of `return NotImplemented`

**Kind:** teaching
**Where:** section "One Type or Many", after the `radd_dispatch.py` discussion (line ~316, following "Declining is not failing; the error appears only when nobody volunteers.")
**Problem:** The chapter teaches the sentinel but not the two rules that decide whether the second dispatch happens at all.
A reader who writes `raise TypeError("bad operand")` inside `__add__()` (the obvious thing to write) kills the fallback silently, and a reader who implements only `__radd__()` finds that `Meters + Meters` never reaches it.
Both were verified on the pinned 3.15 build: raising inside `__add__()` propagates before the right operand is consulted, and `A() + A()` never calls `A.__radd__`.
Chapter 34's exercise 6 sends readers back here for "the idiom," so another chapter depends on this passage being complete.

**Proposal:** add after "Declining is not failing; the error appears only when nobody volunteers.":

```
Two details of the fallback are easy to get wrong.
Raising `TypeError` inside `__add__()` is not the same as returning `NotImplemented`.
The exception propagates immediately, so the right operand never gets its turn;
only the sentinel keeps the second dispatch alive.
Python also skips the reflected call when both operands have the same type,
so `Meters + Meters` is settled inside `__add__()`.
A class that implements only `__radd__()` cannot add itself to its own kind.
```

Optional third sentence, if you want the full rule rather than the useful 95%:

```
One case reverses the order: when the right operand's type is a subclass of the left's
and overrides the reflected method, Python tries that reflected method first,
so the more specific type can answer before its base does.
```

**Cost:** none. No listing changes; the claims are verified against the same `Meters` class already on the page.

---

## 2. Add an exercise on reflected operators

**Kind:** exercise
**Where:** section "Exercises" (line ~375)
**Problem:** All four exercises work on paper-scissors-rock. Nothing exercises `NotImplemented` or the reflected forms, which is roughly the last third of the chapter and the part chapter 34 depends on. The classic bug in reflected operators (forgetting that the operands arrive swapped, which only shows up for a non-commutative operator) is never practiced.

**Proposal:** add as exercise 5:

```
5.  Give `Meters` a `__sub__()` and a `__rsub__()`,
    each returning `NotImplemented` for anything but a `Meters`, an `int`, or a `float`.
    Subtraction does not commute, so the reflected form must undo the swap:
    check that `10 - Meters(3)` produces `Meters(7)` rather than `Meters(-7)`.
    Then confirm that `"ten" - Meters(3)` raises `TypeError` rather than building anything.
```

**Cost:** none. `Meters` is already defined in the chapter, and the exercise needs no new module.

---

## 3. Contrast `singledispatch`'s MRO match with the table's exact match

**Kind:** teaching
**Where:** section "One Type or Many" (line ~222-229)
**Problem:** The section names `functools.singledispatch` and the tuple-keyed `dict` one after the other as the one-type and many-type answers, which invites the reading that they differ only in arity. They also differ in how they match: `singledispatch` resolves through the MRO, so a registration for a base catches every subclass, while the dict probe matches the class exactly. The chapter has taught the exact-match property two paragraphs earlier and the reader is well placed to see the contrast, but nothing draws it.

**Proposal:** append to the sentence pair that names both mechanisms:

```
The two match types differently.
`singledispatch` resolves through the MRO, so registering a base class catches every subclass,
while the table matches the class exactly, as the paragraph above notes.
Swapping one for the other changes which pairings are covered, not just how many types are considered.
```

**Cost:** touches a sentence that chapters 13, 20, 34 and 44 all link to by anchor; the anchor and heading are untouched.

---

## 4. Move the test listing ahead of "One Type or Many"

**Kind:** structure
**Where:** the "pure logic" paragraph, `test_paper_scissors.py`, and the `__main__` note (lines ~318-373)
**Problem:** The chapter currently ends with a test for the two paper-scissors-rock versions and a note about import guards. That material belongs to the two listings it tests, which are three screens earlier, and it lands after the reflected-operator section, which is where the chapter answers the `Number + Number` question it opened with. The reader gets the payoff and then a housekeeping note.

**Proposal:** move the paragraph beginning "The win/lose/draw result is pure logic", the `test_paper_scissors.py` listing, and the "Importing both modules works cleanly..." note up to just before `## One Type or Many`, so the chapter runs: two versions, a test proving they agree, then the discussion of which to use and how Python's own operators do it.

Alternative, if you would rather not move the listing: give the operator material its own `### Operators Dispatch Twice` subheading, so it is findable and the tests read as a coda rather than a topic change.

**Cost:** chapter 44 links to `#one-type-or-many` for "reduces competition between items to pure logic, a dictionary lookup with nothing to mock." That phrase would move one section earlier. The link still resolves and the table discussion it describes stays in the section, so this is a small loss of precision rather than a break. Exercise 3 refers to `test_paper_scissors.py` by name and is unaffected.

---

## 5. Say why the double-dispatch listings are typed `Any`

**Kind:** teaching
**Where:** after the duel narration (line ~155), or after "Each type of `Item` encodes..." (line ~157)
**Problem:** The book argues for precise types over `Any` throughout, and `paper_scissors_rock.py` uses `Any` in eight signatures with no explanation. The reason is instructive and supports the chapter's own argument: `Item` declares neither `compete()` nor any `eval_*()` method, so nothing weaker than `Any` lets `item.eval_scissors(self)` type-check. The consequence is the part the reader needs: the checker cannot report a missing `eval_*()` method, which is precisely the failure mode exercise 2 walks into when it adds `Lizard` to every class.

**Proposal:** add a short paragraph:

```
Note what the `Any` annotations cost.
`Item` declares neither `compete()` nor any `eval_*()` method,
so nothing more precise would let `item.eval_scissors(self)` type-check.
That also means a checker cannot tell you when a class is missing one of the nine methods;
the gap surfaces as an `AttributeError` during whichever duel first needs it.
This is the maintenance problem the table version solves,
where the same nine answers sit in one place and a missing one raises `KeyError`.
```

**Cost:** none, unless proposal 4 moves the test listing, in which case place this before that move.

---

## 6. Make `Meters` a frozen dataclass, or say why it is not one

**Kind:** code
**Where:** `radd_dispatch.py` (line ~264)
**Problem:** `Meters.__init__()` assigns one parameter to one field, which is the definition the house style gives for "this should be a `@dataclass`," and the hand-written `__repr__` differs from the generated one only in dropping the field name. Nothing in the prose says why the manual form is here, so it reads as drift rather than a choice (this is the same shape as chapter 19's `Meter`, which the review skill cites as the canonical case).

**Proposal:** replace the head of the listing with:

```python
# radd_dispatch.py
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Meters:
    n: float

    def __add__(self, other: object) -> Any:
```

The rest of the listing is unchanged. Verified: it type-checks and runs. Every `#:` marker gains the field name:

```
#: __add__(Meters(n=3), Meters(n=4))
#: Meters(n=7)
#: __add__(Meters(n=3), 4)
#: Meters(n=7)
#: __radd__(Meters(n=3), 4)
#: Meters(n=7)
#: __add__(Meters(n=3), 'four')
#: TypeError
```

Alternative, if you prefer the shorter trace lines: keep the manual form and add a clause to the prose introducing the listing, e.g. "`Meters` writes its own `__repr__()` so the trace lines stay short."

**Cost:** the eight `#:` markers above, and the two prose references to trace lines (`__add__(Meters(3), 'four')` is not quoted in the prose, so nothing else needs rewording). Requires the usual sync/validate loop.

---

## 7. Say why the operator dunders return `Any`

**Kind:** teaching
**Where:** `radd_dispatch.py` and its discussion (lines ~275, ~306)
**Problem:** `-> Any` on `__add__()` and `__radd__()` is the second unexplained `Any` in the chapter, and here it has a sharp technical reason worth one sentence: the honest return type is `Meters | NotImplementedType`, and declaring that poisons every downstream expression. Verified under `ty` 0.0.63: with the precise union, `(Meters(1) + Meters(2)).n` fails with `unresolved-attribute: Attribute n is not defined on NotImplementedType`.

**Proposal:** add to the paragraph after the listing:

```
The `Any` return annotations are the honest choice here.
The precise type is `Meters | NotImplementedType`,
and a checker then rejects `(Meters(1) + Meters(2)).n`,
since the sentinel branch has no `n`.
The sentinel is a signal to the interpreter rather than a value a caller ever sees,
so the annotation that describes it accurately describes the wrong thing.
```

**Cost:** none. If proposal 6 is accepted, this paragraph sits alongside it unchanged.

---

## 8. Soften the claim about what other languages cannot do

**Kind:** prose
**Where:** section "One Type or Many" (line ~242)
**Problem:** "a workaround for languages that cannot store types in a table and look a behavior up by them" is not true of the languages a reader will compare against: Java has had `Class` objects usable as `HashMap` keys from the start, and C++ has `std::type_index`. The point that survives is that doing it there is verbose and unchecked, not that it is impossible, and an overstated claim about another language is the kind of thing readers write in about.

**Proposal:** replace with:

```
The double-dispatch version, where each class implements `eval_paper()`,
`eval_scissors()`, and `eval_rock()`,
belongs to languages where keying a table by a pair of types is awkward enough that spreading the table across the classes wins.
Python makes the table cheap, so it is both shorter and easier to maintain.
```

**Cost:** none.

---

## 9. Fix the referent in the sentence introducing the first example

**Kind:** prose
**Where:** the introduction (lines ~29-31)
**Problem:** "The following example names its methods `compete()` and `eval_*()`, and all belong to the same hierarchy" reads as if the methods belong to a hierarchy. The intended contrast is with the next sentence's two interacting hierarchies, so the subject should be the objects. "Here there will be only two dispatches" then restates the count a second time.

**Proposal:** replace the three sentences with:

```
The following example dispatches through methods named `compete()` and `eval_*()`,
with both of the interacting objects drawn from a single hierarchy.
Two unknown types means two dispatches, which is *double dispatching*.
```

**Cost:** none.

---

## 10. Small prose nits

**Kind:** prose
**Where:** several
**Problem and proposal:** each independent; strike any line you disagree with.

- Line ~12, "Python only performs single dispatching": the "only" attaches to the verb.
  Write "Python performs single dispatching only" or, better, "Python dispatches on one type at a time."
- Line ~218, "the fail-fast policy that suits a table under construction, which is what you want while adding `Lizard` in exercise 1": three appositives chained onto one sentence, and "is what" is filler here.
  Suggest "the fail-fast policy that suits a table under construction, as you will see while adding `Lizard` in exercise 1."
- Lines ~234-237, the isinstance-ladder sentence runs "It works, and it is the worst of both worlds, type tests scattered ..., with none of ..., and every new `Item` forces an edit to every ladder," ending a comma-joined list with an independent clause.
  Suggest splitting after "worst of both worlds": "It works, and it is the worst of both worlds. The type tests are scattered through every class as in the method version, with none of dispatch's automatic resolution, and every new `Item` forces an edit to every ladder."
- Exercise 4 says to "print how many times `Lizard` appeared across `item_pair_gen(Item, 100, counts)`."
  `item_pair_gen()` is a generator, so a reader who prints `counts` without consuming it sees zeros. Either make the trap explicit ("remember the counter fills only as you consume the generator") or write "after iterating over all 100 pairs."

**Cost:** none.

---

## Already fixed directly (no decision needed)

- line ~19: the polymorphism definition linked to `20_Rethinking_Objects.md#polymorphism-without-inheritance`, which demonstrates subtype polymorphism only. The sentence defines polymorphism broadly and then lists the three forms, which is the content of that chapter's "What Is Polymorphism?" section. Retargeted the anchor to `#what-is-polymorphism`; `heading_links.py` still passes.
- line ~255: "Every binary operator has a reflected form" was over-broad. Comparison operators have no reflected dunders (there is no `__rlt__`; Python swaps `x < y` to `y > x` instead), and neither do `in` or the boolean operators. Changed to "Every arithmetic and bitwise operator has a reflected form," which covers exactly the set with `__r*__` names.
- line ~387, exercise 3: "add `Lizard` to `EXPECTED` with its nine (now sixteen) matchups" was wrong under every reading. Lizard adds seven entries (both orders of three mixed pairs, plus Lizard versus Lizard), taking `EXPECTED` from nine to sixteen. Reworded to say that.

## Verification run (before edits, against the freshly synced tree)

- `paper_scissors_rock.py`, `paper_scissors_rock_table.py`, `radd_dispatch.py` all run and match their `#:` markers exactly.
- `ty check 32_Multiple_Dispatching`: clean. `ruff check`: clean. `pytest`: 6 passed.
- `heading_links.py` and `banned_phrases.py`: clean, before and after the edits.
- Cross-chapter ends checked and consistent: 34's `expr.py` prose and exercise 6 both point at `#one-type-or-many` and describe the `NotImplemented` idiom the way this chapter teaches it; 31's engine (`type(event)` keyed exactly, no `isinstance()` walk) and 37's `bins[type(t)]` agree with this chapter's exact-match paragraph.
