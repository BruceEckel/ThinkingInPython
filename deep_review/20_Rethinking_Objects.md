# Deep review: 20_Rethinking_Objects.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Give the Liskov section a listing

**Kind:** teaching
**Where:** section "The Liskov Substitution Principle" (lines ~58-80)

**Problem:** This is the only section in the chapter that makes a claim and never shows it.
The section says "Nothing stops a subclass from breaking the base class contract while matching it perfectly"
and "The interpreter runs code that violates the LSP without objection,"
but a reader who has not already been bitten by this has no picture of what such a subclass looks like.
Every other claim in the chapter earns a listing: `leaky.py` shows the leak,
`frozen_leaky.py` shows the shallow freeze, `protocol_collision.py` shows the structural blind spot.
The LSP is the load carrier for the chapter's whole argument against inheritance,
and it arrives as an assertion.
The payoff paragraph at line ~716 ("A protocol also sharpens what the LSP does and does not get you")
then asks the reader to recall a concept they were shown only in the abstract, 650 lines earlier.

**Proposal:** Add one listing at the end of the section, after "That code may or may not fail at run time."
The signatures match, `@override` is satisfied, `ty` reports nothing, and the caller still breaks.
Verified: type-checks clean under `ty` 0.0.6x, output as shown.

```python
# lsp_violation.py
from dataclasses import dataclass, field
from typing import ClassVar, override

@dataclass
class Stack:
    items: list[int] = field(default_factory=list)

    def push(self, item: int) -> None:
        self.items.append(item)

@dataclass
class BoundedStack(Stack):
    limit: ClassVar[int] = 2

    @override
    def push(self, item: int) -> None:
        if len(self.items) >= self.limit:
            raise OverflowError("Stack is full")
        super().push(item)

def fill(stack: Stack, count: int) -> int:
    for n in range(count):
        stack.push(n)
    return len(stack.items)

print(fill(Stack(), 5))
#: 5
try:
    fill(BoundedStack(), 5)
except OverflowError as e:
    print(type(e).__name__)
#: OverflowError
```

Followed by prose along these lines:

```
`BoundedStack.push()` takes the same argument and returns the same type,
so `@override` is satisfied and `ty` reports nothing.
`fill()` was written against `Stack`, which never refuses a `push()`,
and a `BoundedStack` handed to it raises an exception on the third item.
The subclass matched the signature and broke the contract behind it.
```

**Cost:** One new listing and one paragraph in a chapter that argues for less machinery,
so it adds length where the chapter is otherwise lean.
The section's explicit anchor `{#liskov-substitution}` is unchanged,
so the incoming links from 25 and 29 keep working.
Nothing else in the book references a `Stack` type by that name.

---

## 2. Say why the `Coord` protocol declares `x` and `y` as properties

**Kind:** teaching
**Where:** section "Protocols Generalize, Composition Adapts" (`distance_protocol.py`, lines ~331-376)

**Problem:** `Coord` writes its two members as read-only properties:

```python
class Coord(Protocol):
    @property
    def x(self) -> float: ...
    @property
    def y(self) -> float: ...
```

The reader has just been told that a protocol "describes that shape,"
so the obvious thing to write is `x: float` on two lines, which is shorter and reads like the dataclass it is matching.
That version fails, and it fails in a way that is hard to diagnose from the message.
A protocol member declared as a bare annotation is read-write,
so an implementer must have a settable attribute.
`Point` still passes, because its dataclass field looks settable to the checker.
`PairCoord`, whose `x` is a read-only property, does not.
Verified with `ty`:

```
error[invalid-argument-type]: Argument to function `distance` is incorrect
info: type `PairCoord` is not assignable to protocol `Coord`
info: └── protocol member `x` is incompatible
info:     └── the member does not accept writes of type `int | float`
```

The chapter's whole point in this section is that composition adapts a type you were handed,
and the adapter is exactly the thing that breaks under the shorter spelling.
Two sentences close the gap.
The section currently gets only two sentences of commentary in total, so it has room.

**Proposal:** After "They both have `x` and `y`, which is all `distance()` requires," add:

```
`Coord` declares `x` and `y` as properties rather than as bare `x: float` annotations.
A bare annotation in a protocol is a read-write attribute,
so an implementer must allow assignment to it.
`PairCoord` computes `x` from its `Pair` and cannot be assigned to,
so it satisfies the property form and fails the annotation form.
Declare a protocol member read-only unless callers really do write to it.
```

**Cost:** none. No listing changes, no anchor changes.

---

## 3. Replace exercise 3, which asks for nothing

**Kind:** exercise
**Where:** section "Exercises", item 3 (line ~985)

**Problem:** Exercise 3 asks the reader to add `p3 = Point(6, 8)` to `point_distance.py`
and confirm the method and the function still agree.
They agree because they are the same arithmetic, which the listing already printed three times.
Nothing about the exercise can surprise, and nothing about it can fail.
Meanwhile the chapter's sharpest lesson, the structural blind spot in `protocol_collision.py`
plus its `NewType` follow-up, has no exercise at all,
and it is the one place where a reader could plausibly ship the bug the section warns about.

**Proposal:** Replace item 3 with:

```
3.  In `protocol_collision.py`, define `Price = NewType("Price", float)`
    and `Weight = NewType("Weight", float)`,
    change `Priced.total()` to return a `Price`, `Weighted.total()` to return a `Weight`,
    and `Package.total()` to return a `Weight`.
    Run `ty check` and read the error it reports for `charge(package)`.
    Then say what still goes wrong at run time if someone deletes the annotations.
```

Verified: `ty` rejects the call with
"protocol member `total` is incompatible / incompatible return types: `Weight` is not assignable to `Price`".
The closing question makes the reader restate the `NewType`-is-checker-only point from line ~691.

**Alternatives:**
Keep item 3 and append this as item 7, if you would rather not lose a listing's exercise coverage.
Or point the new exercise at `overload_example.py` instead
(add a `stringify(value: str) -> str` overload and observe what the implementation signature must become),
since `@overload` is also unexercised.

**Cost:** `point_distance.py` loses its only exercise. It is a four-line listing whose lesson is
carried entirely by the prose about `Point.distance_to(p1, p2)`, which no exercise currently touches either.

---

## 4. Show the coupling that "Prefer Composition to Inheritance" asserts

**Kind:** teaching
**Where:** section "Prefer Composition to Inheritance" (lines ~378-381)

**Problem:** The section opens with "In practice, implementation inheritance couples a subclass to its base
in ways that are hard to undo," then moves directly to composition.
The reader is asked to accept the cost and is then shown only the alternative.
This is the same shape as finding 1: the sections about encapsulation and about protocols
each show their failure before showing their fix, and this one does not.

**Proposal:** Add a short listing before "Before inheritance, there was composition."
Verified: type-checks clean, prints `3 1`.

```python
# counting_list.py
from typing import override

class CountingList(list[int]):
    def __init__(self) -> None:
        super().__init__()
        self.appends = 0

    @override
    def append(self, item: int, /) -> None:
        self.appends += 1
        super().append(item)

counted = CountingList()
counted.append(1)
counted.extend([2, 3])
print(len(counted), counted.appends)
#: 3 1
```

With prose noting that `list.extend()` appends its items without calling `append()`,
so the count is wrong the moment anyone uses the base class's other method.
Nothing in the subclass is incorrect. It inherited an implementation and now depends on how that
implementation is written, which is a fact about `list` that no signature records and no checker reports.

**Cost:** A second new listing in the same chapter as finding 1, which together add real length.
If only one lands, take finding 1: the LSP claim is referenced from two other chapters, this one is not.
Also worth weighing: the listing models subclassing a builtin, which the book otherwise avoids.
That is the point here, but a reader skimming listings could take it as a recommendation.

---

## 5. Sharpen the opener of the Liskov section's second paragraph

**Kind:** prose
**Where:** section "The Liskov Substitution Principle" (line ~73)

**Problem:** "Python has no compiler, but this is not the boundary you might expect."
Which boundary? The word has not appeared yet, and the sentence it belongs with is three lines further on.
The paragraph makes its point well once the reader gets to
"What no tool reads is the behavior behind the signature," but the opener sends them there confused.

**Proposal:** Replace the sentence with:

```
Python has no compiler, but the line between what a tool checks and what it cannot falls in the same place.
```

**Cost:** none.

---

## 6. Attach the exhaustiveness claim to the right half of the trade-off

**Kind:** prose
**Where:** section "Pattern Matching on a Union" (lines ~772-776)

**Problem:** The paragraph reads:

> Adding a new shape is easier in the OOP version because you write one class.
> Adding a new operation over all shapes is easier in the pattern matching (functional) version.
> If you modify one function, the type checker tells you if you missed a case.

The third sentence sits under the second, so it reads as support for "adding an operation is easier."
The exhaustiveness check earns its keep in the other direction: it fires when you add a *shape*
and forget to update a `match`, which is the OOP version's advantage being clawed back.
A reader tracking the expression-problem trade-off has to work out which sentence the third one belongs to.

**Proposal:** Replace those three sentences with:

```
Adding a new shape is easier in the OOP version because you write one class.
Adding a new operation over all shapes is easier in the pattern matching (functional) version,
where the operation is one new function rather than a method added to every class.
The exhaustiveness check covers the other direction.
Adding a member to the `Shape` union leaves every existing `match` incomplete,
and `assert_never()` turns each one into a checker error naming the shape you missed.
```

Verified: adding `Square` to the union without a `case` gives
"Inferred type of argument is `Square & ~Rectangle & ~Circle`", which names the missing shape.

**Alternative:** the minimal fix is to move the third sentence to the front of the paragraph,
so it attaches to "Adding a new shape."

**Cost:** none. Exercise 5 already walks the reader through this and stays correct either way.

---

## 7. `ListLogger` hand-writes a field-assigning `__init__`

**Kind:** code
**Where:** section "Null Object" (`optional_logger.py`, lines ~856-860)

**Problem:** House style says a class whose `__init__()` only assigns fields is a `@dataclass`,
and the deviation is a lesson only when the prose says why.
`ListLogger` assigns one default and nothing else, with no stated reason.
Every other class in this chapter that could be a dataclass is one,
and where a listing deliberately avoids the dataclass form (`Leaky`, `Plugged`)
the prose says so at line ~176.
`ListLogger` is the odd one out, in the section that comes last and is most likely to be copied.

**Proposal:** Leave it, and say nothing.
The dataclass form needs `field(default_factory=list)` and a second import
in a listing whose subject is the `| None` guard three lines below it,
and the noise would cost more than the consistency buys.
I am filing this so the deviation is a recorded decision rather than drift.

**Alternative:** convert it:

```python
@dataclass
class ListLogger:
    lines: list[str] = field(default_factory=list)

    def log(self, message: str) -> None:
        self.lines.append(message)
```

`null_logger.py` imports `ListLogger` from this module, so both listings would need re-running.

**Cost:** none if left as is.

---

## 8. Micro-wording

**Kind:** prose
**Where:** several

Each bullet is independent; strike any you disagree with.

- **line ~80 and line ~811: "run time" vs "runtime."** The chapter uses both.
  Lines 491, 693 and 706 write "at runtime"; lines 80 and 811 write "at run time".
  The book runs about 50 "at runtime" to 4 "at run time", so make the two odd ones out match.
  (Line 35's "run-time world" is an adjective and can stay.)
- **line ~436: "What you buy is the last two lines."** `buy` is on the watch list,
  and the cleft delays the verb. Suggest: "The last two lines are what that arrangement pays back."
  Or plainer: "The last two lines are the payoff."
- **line ~664: "The mismatch lives entirely in what the number means."**
  `entirely` is doing intensifier work here; the contrast with the matched shape is already
  carried by the sentence before it. Suggest dropping the word.
- **line ~36 and line ~70: two metaphorical uses of "promise"** outside the four
  "OOP promise" section themes: "That style makes no substitutability promises"
  and "the way the base class promises."
  If you want the four themed uses to land as a deliberate motif,
  these two dilute it. Suggest "That style guarantees no substitutability"
  and "the way the base class declares."
  Rejecting this bullet is entirely reasonable: both read fine on their own.

**Cost:** none.

---

## Already fixed directly (no decision needed)

- line ~926: "The standard library ships this idea as `logging.NullHandler`" became "includes this idea as".
  `ships` is on the watch list's do-not-use tier.
- line ~680: the comment in `newtype_boundary.py` quoted `ty` as reporting
  expected "UserId", found "int". The real diagnostic is
  `Expected UserId, found Literal[42]`, so the comment now reads `found "Literal[42]"`.
  Verified by removing the `# type: ignore` in a scratch copy and running `uv run ty check`.
  This changes a code block, so the chapter needs a re-sync before the gate runs.
