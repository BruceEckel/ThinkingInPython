# Deep review: 28_Function_Objects.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Show the callable object the chapter's title names

**Kind:** teaching
**Where:** section "Command: Choosing the Operation at Runtime" (line ~90, right after the bound-method sentence)
**Problem:** The chapter is called *Function Objects* and never shows one. It opens by defining the term as a decoupling ("A *function object* decouples the choice of function to call from the place that calls it"), which describes the pattern family rather than the thing. Chapter 39's catalog row points here with a different definition: "| [Function Object](28_Function_Objects.md) | An object whose sole purpose is to wrap a single function. |" That object never appears. The reader therefore meets exactly two rungs, a bare function and a five-class `Command` hierarchy, and the middle rung that dissolves the hierarchy is missing. `__call__` was taught in [Decorators](14_Decorators.md) ("A class with `__call__()` is a callable, so a decorator can be a class instead of a function"), so nothing new has to be introduced, only applied. It is also the rung exercise 1 (add undo) is groping toward, and the one chapter 36 names when it refers back here for command-based undo.

**Proposal:** Add one short listing and a paragraph after "…carrying its state without any `Command` class." Verified: runs, `ty` clean, every line under 70.

````
An object can be callable too.
Give a class `__call__()` ([Decorators](14_Decorators.md#a-stateless-class-decorator))
and its instances carry state and still satisfy `Callable[[], None]`:

```python
# callable_command.py
from collections.abc import Callable
from dataclasses import dataclass

@dataclass(frozen=True)
class Repeat:
    text: str
    times: int
    def __call__(self) -> None:
        for _ in range(self.times):
            print(self.text)

macro: list[Callable[[], None]] = [
    Repeat("You're a loony.", 1),
    Repeat("Say no more.", 2),
]
for command in macro:
    command()
#: You're a loony.
#: Say no more.
#: Say no more.
```

`Repeat` holds configuration and drops into the same list as `loony`,
with no `Command` base class to derive from.
That is the rung the classic form skips.
The `Command` class earns its keep only at the next step,
when the command needs a *second* operation, `undo()`,
which no single callable can express.
```
````

**Cost:** The existing sentence "Use the object form when a command must also carry state or support extra operations such as undo" then over-claims, because state alone no longer needs the object form. Change it to name only the second operation. Exercise 1's phrasing ("is a function still enough, or do you now want an object?") gets sharper rather than stale, but check you still like it. Adds one file to `Examples/28_Function_Objects/`.

*Alternative:* keep the listing but drop the last three lines of the paragraph and let exercise 1 discover the undo argument on its own.

---

## 2. Fix the opening's claim that each pattern appears twice

**Kind:** prose
**Where:** opening (line ~11)
**Problem:** "Each pattern below appears twice: first as a function, then as the classic class-based form for contrast." *Command* and *Strategy* do. *Chain of Responsibility* appears once: its classic linked-handler form is described in prose ("each handler holding a reference to the next") but never shown. A reader who takes the sentence literally hunts for a listing that does not exist.

**Proposal:** Replace the sentence with:

```
*Command* and *Strategy* each appear twice below,
first as a function, then as the classic class-based form for contrast.
*Chain of Responsibility* needs only the function form:
its class version is the same idea with the list spelled as a linked chain.
```

**Cost:** none.

*Alternative:* add a fourth classic listing, a linked `Handler` chain with a `successor` field. That costs about 25 lines to make a point the prose already makes in one, and it would be the only classic form the reader meets after two of them.

---

## 3. Warn that a root of `0.0` is falsy

**Kind:** teaching
**Where:** section "Chain of Responsibility" (line ~354, after "success is a non-`None` return")
**Problem:** `chain.py` correctly writes `if root is not None`, and the prose says success is "a non-`None` return," but never says what breaks if you write `if root:` instead. This is the near-miss a reader will actually write, and here it is not hypothetical: a function with a root at zero returns `0.0`, which is falsy, so the truthiness test discards a correct answer and falls through to the next handler. Verified against the built tree: `solve(lambda x: x, -1.0, 1.0, chain)` returns `0.0`, `is not None` is `True`, `bool(root)` is `False`.

**Proposal:** Add after "and success is a non-`None` return.":

```
The test is `root is not None`, not `if root`.
A function with a root at zero returns `0.0`,
which is falsy, so a truthiness test would throw away a correct answer
and hand the problem to the next finder.
Any sentinel-versus-value check on a numeric result has this hazard.
```

**Cost:** none. Ties to the same rule behind `dict.get()` returning a stored falsy value.

---

## 4. Say that the bus dispatches on the exact type

**Kind:** teaching
**Where:** section "An Event Bus: Handlers Keyed by Type" (line ~476, after the `.get()`-versus-indexing paragraph)
**Problem:** `publish` looks up `type(event)`, so a subclass of `Deposit` finds no handler even when a `Deposit` handler is registered. Verified: a `BigDeposit(Deposit)` published to a bus with an `on_deposit` subscriber calls nothing, silently. The events are frozen data classes, and subclassing one is a natural next move for a reader extending the example. The chapter notes the silent no-op for `Closed`, where it is intended, and never mentions the case where it is a surprise. Exact-type dict dispatch is called out in [State Machines](31_State_Machines.md), [Multiple Dispatching](32_Multiple_Dispatching.md) and [Pattern Refactoring](37_Pattern_Refactoring.md); this is the one place it appears without comment.

**Proposal:** Add:

```
The lookup uses `type(event)`, which matches the class and no ancestor.
A subclass of `Deposit` published to this bus finds no handler
and vanishes as quietly as `Closed` does.
Walking `type(event).__mro__` and calling every handler along it
gives subclass events their parent's handlers,
at the cost of an event type no longer naming its audience by itself.
```

**Cost:** none, unless you take up the exercise in proposal 13, which asks the reader to build the MRO walk. Keep both or neither.

---

## 5. Make the two classic base classes agree

**Kind:** code
**Where:** `command_pattern.py` (line ~48) and `strategy_pattern.py` (line ~227)
**Problem:** The chapter's two classic forms spell the abstract method two different ways one page apart: `def execute(self) -> None: ...` and `def find(...) -> float | None: raise NotImplementedError`. [Factory](27_Factory.md#abstract-factories), the chapter immediately before this one, has just told the reader those forms "look interchangeable in a listing and fail at different moments" and compared both against `@abstractmethod`. A reader who took that lesson now sees both forms used interchangeably here with no comment. The `...` body is the weaker of the two: a `Command` subclass that forgets `execute()` inherits a method that silently does nothing.

**Proposal:** Change `command_pattern.py`'s base to match:

```python
class Command:
    def execute(self) -> None:
        raise NotImplementedError
```

**Cost:** none. Output unchanged.

*Alternative:* make both `ABC`/`@abstractmethod` instead. That is more correct and adds an import plus a decorator to each of two listings whose point is how heavy they already are, so I would not.

---

## 6. Make `bisection()`'s exhausted-loop return match its neighbors

**Kind:** code
**Where:** `algorithms.py` (line ~163)
**Problem:** `secant()` and `newton()` return `None` when they run out of iterations. `bisection()` returns `mid`, a value that has not passed the tolerance test. Three functions presented side by side as interchangeable differ in their failure convention, which undercuts the section's whole claim, and it quietly breaks the chain's contract that a non-`None` return means success. In practice the branch is unreachable (bisection on `[0, 2]` converges in about 42 of the 200 iterations), which makes it a stray inconsistency rather than a live bug.

**Proposal:** Change the last line of `bisection()` from `return mid` to `return None`.

**Cost:** none. All markers and tests verified unchanged by inspection; re-run `chain.py`, `strategy.py` and `test_chain.py` after the edit to confirm.

---

## 7. Sharpen why `partial` escapes the late-binding trap

**Kind:** teaching
**Where:** section "Command: Choosing the Operation at Runtime" (line ~125)
**Problem:** "`functools.partial` evaluates its arguments at construction time" reads as though `partial` has special evaluation semantics. It does not. Python evaluates the argument expression before `partial` is called at all, and `partial` only stores the result. The transferable rule is that an argument is evaluated at the call, and a lambda body is not, so a reader who learns "partial evaluates eagerly" will be surprised when `partial(print, lambda: n)` traps them again. The listing sharpens the confusion, because what gets stored is not `n` but the already-formatted string.

**Proposal:** Replace the `partial` sentence with:

```
The argument to `functools.partial` ([Foundations](40_Functional_Foundations.md#partial-application))
is an ordinary expression, evaluated where it is written,
so each command stores the string built from that iteration's `n`.
Nothing is left to look up later.
```

**Cost:** the paragraph is the one [Foundations](40_Functional_Foundations.md) links to by name for the late-binding demo, so keep the `late_binding.py` reference intact. Exercise 4 builds on `partial`, unaffected.

---

## 8. Define "open methods" and describe Newton's hints correctly

**Kind:** prose
**Where:** section "Strategy: Choosing the Algorithm at Runtime" (line ~138)
**Problem:** Two issues in one sentence. "The hints are a bracket for bisection and two starting points for the open methods." Newton is not given two starting points: it averages the hints into one starting value, `x = (a + b) / 2`. And "the open methods" is a numerical-analysis term used twice in the chapter (again at "The open methods do not") and defined neither time, so a reader without that background reads past it.

**Proposal:** Replace with:

```
Bisection reads the two hints as a bracket, an interval whose ends
straddle the root.
The secant method reads them as two starting points,
and Newton's method averages them into one.
Those two are *open* methods: they need somewhere to start, not a bracket,
which is why the chain below can fall back on them.
```

**Cost:** removes the need for the forward pointer in proposal 9, so take one or the other.

---

## 9. Say early why the chapter carries three algorithms

**Kind:** teaching
**Where:** section "Strategy: Choosing the Algorithm at Runtime" (line ~214, after `strategy.py`)
**Problem:** `strategy.py` prints `1.414214` three times. The reader learns the three finders are interchangeable and nothing else, and the obvious question, why keep three algorithms that give the same answer, is answered about 130 lines later in the Chain of Responsibility section. Front-loading that answer gives the whole Strategy section a reason to exist beyond "they have the same signature."

**Proposal:** Add after the listing:

```
Three identical lines is the point: the caller does not change when the
algorithm does.
The algorithms are not equivalent, though.
Bisection needs a bracket and the other two do not,
which the chain below turns into a fallback.
```

**Cost:** overlaps proposal 8. If 8 lands, cut the last two lines here and keep only the first two.

---

## 10. Correct how the checker binds `E` in `subscribe`

**Kind:** prose
**Where:** section "An Event Bus: Handlers Keyed by Type" (line ~460)
**Problem:** "The checker reads `E` from the first argument and requires the handler to accept that exact type." That is not what happens. `ty` solves `E` from both arguments at once. A reader who tries `bus.subscribe(Deposit, on_withdraw)` gets: `Expected Handler[Deposit | Withdraw], found def on_withdraw(event: Withdraw) -> None`, with `E` solved as the union of the two. The rejection is real, the mechanism described is not, and the error message contradicts the sentence that predicted it.

**Proposal:** Replace with:

```
`subscribe` is generic on the event type `E`, which appears in both
parameters,
so the checker must find one `E` that satisfies the class and the handler
together.
No such `E` exists for `subscribe(Deposit, on_withdraw)` and it is a type
error.
The safety check happens once, at registration.
```

**Cost:** none.

---

## 11. Split the `Placeholder` sentence

**Kind:** prose
**Where:** section "Strategy: Choosing the Algorithm at Runtime" (line ~311)
**Problem:** "`functools.partial` does the same job when the configurable version already exists with the setting as a parameter, including the case where the setting is a positional argument that comes after the one the caller supplies, which `Placeholder` (...) handles." Three stacked clauses, and the closing "which" sits five clauses away from the noun it modifies. This is the chapter's one sentence that needs a second reading.

**Proposal:** Replace with:

```
`functools.partial` does the same job when a configurable version already
exists with the setting as a parameter.
If that setting is a positional argument sitting after the one the caller
supplies,
`Placeholder` ([Foundations](40_Functional_Foundations.md#leaving-a-gap-with-placeholder))
fills the gap.
```

**Cost:** none.

---

## 12. Reword the chain's fall-through paragraph

**Kind:** prose
**Where:** section "Chain of Responsibility" (line ~357)
**Problem:** "This is the fall-through: bisection cannot bracket a root. It returns `None`, and the chain continues looking for a method that can." Two problems. "This" points back past two general sentences to the listing's second call, so the referent is guessable rather than stated. And bisection does not bracket anything: the interval `[1.0, 1.3]` fails to bracket the root, which is why bisection declines.

**Proposal:** Replace with:

```
The second call shows the fall-through.
The interval `[1.0, 1.3]` does not straddle the root,
so bisection declines by returning `None`
and the chain moves on to a method that needs no bracket.
```

**Cost:** none.

---

## 13. Add an exercise on the event bus

**Kind:** exercise
**Where:** section "Exercises" (line ~530)
**Problem:** The four exercises cover Command, Chain of Responsibility and Strategy twice over. The event bus, the chapter's longest section and the one carrying its most subtle material (a generic boundary over erased storage, and the read-versus-write difference on a `defaultdict`), has none. It is also the section a reader is most likely to lift into their own code.

**Proposal:** Add:

```
5.  `EventBus.publish()` looks up `type(event)`, so a subclass of `Deposit`
    finds no handler.
    Change `publish()` to walk `type(event).__mro__` and call every handler
    registered along it, parents last.
    Then add `unsubscribe()`.
    Which of the two changes can break an existing caller, and why?
```

**Cost:** pairs with proposal 4, which states the exact-type behavior in prose. Take both or neither, or the exercise gives away material the chapter never raised.

---

## 14. Small prose fixes

**Kind:** prose
**Where:** several (each listed)
**Problem:** Individually minor; grouped so you can strike any bullet you disagree with.
**Proposal:**

- Line ~16-18: "In Python the action is just a function, and a 'macro' is just a list of actions." Two "just"s in one sentence, and a third arrives at line ~88 ("a callback is just a function"). Drop the second: "…and a 'macro' is a list of actions."
- Line ~270: "Strategies-as-functions are used constantly in Python without naming it as a pattern." The "it" has no singular antecedent. Suggest: "Python uses strategies-as-functions constantly without calling them a pattern."
- Line ~307-308: "The coarse strategy stops within a tenth and reports 1.406250. The fine one reports the root to six places." Both print six places; the fine one is *accurate* to six. Suggest: "The fine one agrees with the true root to six places."
- Line ~360: "These tests confirm that the first finder that converges wins, a later finder rescues one that fails, and an empty chain returns `None`." There are four tests; the fourth, every handler failing, is not in the list. Add ", and a chain where every finder fails returns `None` too".
- Line ~506: "This is the [Observer](30_Observer.md#the-pythonic-observer-a-list-of-callables), narrowed to a single subject." "Narrowed" reads oddly for a structure that handles more event types than a single observable does. Chapter 30's own phrasing from the other end is clearer. Suggest: "This is the [Observer](30_Observer.md#the-pythonic-observer-a-list-of-callables) with one shared subject: instead of every observable holding its own list, one bus holds them all and the event type picks the audience."

**Cost:** none.

---

## 15. Give "Chain of Responsibility" a subtitle like its neighbors

**Kind:** structure
**Where:** section heading (line ~318)
**Problem:** Three of the chapter's four section headings name the pattern and then say what varies at runtime: "Command: Choosing the Operation at Runtime", "Strategy: Choosing the Algorithm at Runtime", "An Event Bus: Handlers Keyed by Type". "Chain of Responsibility" alone stands bare, so the table of contents stops telling the reader what the section is about halfway through.

**Proposal:** `## Chain of Responsibility: Choosing the Handler at Runtime`

**Cost:** real, and the reason this is ranked last. The anchor changes from `#chain-of-responsibility` to `#chain-of-responsibility-choosing-the-handler-at-runtime`, and two other chapters link to it: `Chapters/30_Observer.md` line 102 and `Chapters/39_Pattern_Catalog.md` line 44. `heading_links.py` fails until both are updated, so this must be done as one commit across three files.

---

## Already fixed directly (no decision needed)

- line ~128: "The older spelling `lambda n=n: ...`" to "The older form". "Spelling" is on the don't-use list in `~/.claude/CLAUDE.md`; `banned_phrases.py` does not gate it.
