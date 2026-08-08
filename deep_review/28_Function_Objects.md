[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**`algorithms.py`: the three "interchangeable" finders do not use the same
definition of success, and in a chain that matters.**

`bisection()` returns only when the *residual* is small (`abs(f(mid)) < TOLERANCE`).
`secant()` and `newton()` return when the *step* is small (`abs(x2 - x1) < TOLERANCE`,
`abs(step) < TOLERANCE`). A step-size test can converge on a point that is not a
root: on a function that flattens out, the step shrinks below tolerance while `f(x)`
is still far from zero, and the finder returns a wrong answer instead of `None`.

That is worth a sentence precisely because the chain section says "success is a
non-`None` return". The chain's contract is only as good as each handler's
self-assessment, and two of the three handlers can report success wrongly.

Proposed change: either

1. add a residual check before the successful return in `secant()` and
   `newton()`, e.g. `if abs(x2 - x1) < TOLERANCE: return x2 if abs(f(x2)) < 1e-6 else None`
   (this makes all three agree on what "found" means), or
2. leave the code and add one sentence after the chain listing: "A handler is
   trusted to know when it failed. `secant()` and `newton()` stop when their
   step stops shrinking, which is not quite the same as landing on a root, so a
   chain is only as honest as its handlers."

I recommend (2): the chapter is teaching dispatch, not numerics, and the caveat
is the transferable lesson. I did not implement either, because both change what
the listings claim.

---

[] Reject

**Lines 137-139: "The `Command` class earns its keep only at the next step, when
the command needs a *second* operation, `undo()`, which no single callable can
express" overreaches, and the recommendation contradicts the book's own
Protocol-over-base-class rule.**

`Repeat`, two lines above, is a callable *object*. Giving it an `undo()` method
alongside `__call__()` needs no `Command` base class at all:

```python
@dataclass(frozen=True)
class Deposit:
    account: Account
    amount: int
    def __call__(self) -> None: ...
    def undo(self) -> None: ...
```

What the second operation really costs is the *type*: the list can no longer be
`list[Callable[[], None]]`, because `Callable` has room for exactly one call. It
needs a name for "callable, plus `undo()`", and in this book that name is a
`Protocol` (the style skill: "Use a `Protocol` for duck-typed conformance with no
base class. Prefer it over both `Any` and ABCs"), not a base class. A `Command`
base class earns its keep only when you also want shared implementation, or when
you deliberately want the GoF shape.

Proposed change: rewrite the passage as something like

> The second operation is what a plain callable cannot express: `Callable[[], None]`
> has room for exactly one call, so the list needs a name for "callable, plus
> `undo()`". In Python that name is a `Protocol` with both members, and the
> `Command` base class earns its keep only when the commands also want shared
> implementation. [[rewrite "earns its keep"]]

Note this also affects `Solutions/28_Function_Objects.md` §1, whose prose repeats
the same reasoning ("a callable has only one call ... that is the step the chapter
names, where the `Command` class earns its keep"). If you take this change, that
paragraph should be reworded to match, and the solution could show the `Protocol`
alongside the base class. I did not touch `Solutions/`.

---

[] Reject

**The chapter has no conclusion.**

It ends on the event bus's cross-reference paragraph and goes straight into
Exercises. Its neighbors all close deliberately: 24 "Which Should You Use?",
27 "Which Factory Should You Use?", 29 "Telling the Wrappers Apart",
30 "What Stayed Constant", 37 "Choosing the Lightest Construct". The gap shows,
because chapter 28 has an unusually clean answer to give and never gives it: the
chapter is a ladder, and the reader who has climbed it deserves to be shown the
rungs in one place.

The rungs, in the order the chapter presents them:

1. a plain function (`command.py`, `strategy.py`)
2. a bound method, when the state is already an object's
3. a `partial` or a closure, when the state is a fixed configuration
   (`configured_strategy.py`)
4. a callable object, when the configuration wants a name and a `repr`
   (`callable_command.py`)
5. a class with two or more operations, when one call is not enough
   (`command_pattern.py`'s `undo()` argument)

Proposed change: add a short closing section, "Choosing the Lightest Callable"
or similar, holding that list and one sentence of the rule ("go down the list and
stop at the first rung that carries what you need"). No new listing; the section
should be prose only, naming the listings the reader has already seen.

Cost of the change: it lengthens the chapter by roughly fifteen lines, and the
list overlaps the per-section verdicts already in the text (lines 137-139,
"Save the strategy class for an algorithm that carries several related methods or
mutable state"). If you take it, those verdicts should stay where they are and
the closing section should reference rather than restate them.

---

[] Reject

**`callable_command.py` (line 115): `@dataclass(frozen=True)` is used before the
chapter points at where it is taught.**

The first frozen data class in the chapter is `Repeat`, at line 115.
The chapter's only cross-reference for the construct sits at line 469, in the
event-bus section: "written as [frozen data classes](12_Data_Classes_as_Types.md#immutability)".
A reader who needs the link needs it at the first use, not four sections later.

Proposed change: move the reference to the sentence introducing `callable_command.py`
("An object can be callable too. Give a class `__call__()` ..."), so it reads
along the lines of

> An object can be callable too.
> Give a class `__call__()`
> ([Decorators](14_Decorators.md#a-stateless-class-decorator))
> and its instances carry state and still satisfy `Callable[[], None]`.
> `Repeat` below is a [frozen data class](12_Data_Classes_as_Types.md#immutability),
> so its configuration cannot change after it is built:

and drop the link at line 469 down to bare words ("written as frozen data classes"),
since by then it has already been given.
Alternative, if you would rather not lengthen the introduction: leave line 469
as the link and add nothing, accepting that the first use is unannotated.

---

[] Reject

**`strategy_pattern.py` (line 317): the `Bisection()` passed to the constructor
is thrown away on the first loop iteration.**

```python
solver = RootSolver(Bisection())
for algorithm in (Bisection(), Newton(), Secant()):
    solver.change_algorithm(algorithm)
```

The first thing the loop does is replace the strategy the constructor was just
given, so the demo builds two `Bisection()` instances and uses one. It reads like
an oversight rather than a point about the classic form.

Proposed change: start the solver with the first algorithm and let the loop
supply the rest, or keep the constructor call and drop `Bisection()` from the
tuple, so each line in the output corresponds to one strategy that was actually
installed on purpose. Either is a two-line edit; I left it alone because the
current form does show the constructor-takes-a-strategy half of the classic
Context, which the alternatives lose.

---

[] Reject

**Exercises: nothing exercises `late_binding.py`, which is the chapter's most
directly reusable listing.**

The five exercises cover Command (1), Chain (2), Strategy (3, 4), and the event
bus (5). The late-binding trap gets no exercise, even though it is the one thing
in the chapter a reader is likely to hit in their own code this week, and even
though `Functional Foundations` links back to it by name
(`40_Functional_Foundations.md` line 406).

Proposed change: add an exercise along the lines of

> Build a list of three commands in a `for` loop (not a comprehension) with
> `lambda: print(n)`. Call them and explain the output. Fix it three ways:
> with a default argument, with `functools.partial`, and with a factory
> function that takes `n` and returns the command. Which one still works if
> the value must be computed at call time rather than at build time?

The last clause is the part with teeth: none of the three fixes preserve
late lookup, which is what makes the trap a trap rather than a bug.

---

[] Reject

**Lines 425-428: the paragraph after `chain.py` puts two unrelated sentences
together and then repeats the listing's own comment.**

```
Adding, removing, or reordering handlers means editing a list.
The second call shows the fall-through.
The interval `[1.0, 1.3]` does not straddle the root,
so bisection declines by returning `None` and the chain moves on to a method that needs no bracket.
```

"Adding, removing, or reordering handlers means editing a list" is the payoff of
the list-instead-of-linked-chain design and belongs with the preceding paragraph
about structure. The remaining three lines describe the second call, which the
listing's inline comment (`# [1.0, 1.3] does not bracket it; bisection fails,
secant finds it:`) already stated.

Also, the order of the two paragraphs is inverted for a first-time reader: the
`root is not None` subtlety is discussed before the reader has been walked
through what the two calls did.

Proposed change: swap the two paragraphs, so the fall-through walkthrough comes
first and the `is not None` hazard second, and fold "Adding, removing, or
reordering handlers means editing a list" onto the end of the fall-through
paragraph, where it lands as the conclusion the demo has just earned.

---

[] Reject

**Line 136: "That is the rung the classic form skips" is a metaphor standing in
for a literal statement.**

No ladder has been established, so "rung" asks the reader to reconstruct the
progression (plain function, callable object, `Command` hierarchy) from a single
word. The chapter does walk that progression, so the literal version is short:

> The classic form skips this middle step: it goes from a plain function
> straight to a base class.

Proposed change: replace line 136 with that sentence, or with any plain
restatement that names the step being skipped.

---

## Cross-chapter

**`Chapters/31_State_Machines.md`, `Chapters/32_Multiple_Dispatching.md`,
`Chapters/37_Pattern_Refactoring.md` — the exact-type dict-dispatch thread does
not name its earliest instance.**

`37_Pattern_Refactoring.md` (around line 320) says of `bins[type(t)]`:

> The key is the *exact* class,
> the same dictionary-probe dispatch as the tables in [State Machines](31_State_Machines.md#the-engine)
> and [Multiple Dispatching](32_Multiple_Dispatching.md).

Chapter 28's `EventBus` is the first place in reading order where a reader meets
this, and it is the place where the consequence is spelled out most fully
("The lookup uses `type(event)`, which matches the class and no ancestor. A
subclass of `Deposit` published to this bus finds no handler and vanishes as
quietly as `Closed` does."). Exercise 5 then has the reader fix it with the MRO
walk.

Change I would make in 37, at the end of that sentence:
`and [Multiple Dispatching](32_Multiple_Dispatching.md), and first seen in
[Function Objects](28_Function_Objects.md#an-event-bus-handlers-keyed-by-type)'s
event bus.`

I did not add the reverse link from 28 to 37, because 28 already links to 37 in
its closing paragraph (for `singledispatch`) and a second link to the same
chapter three paragraphs earlier would read as clutter. If you would rather the
link went that direction, it belongs on the `type(event)` paragraph
(lines 548-551 of the edited chapter).

---

**`Solutions/28_Function_Objects.md` §2 — the solution re-declares the three
finders instead of importing them, and drops every annotation.**

`exercise_2.py` copies `bisection`, `secant`, and `newton` out of
`algorithms.py` as untyped functions (`def bisection(f, a, b):`). The exercise
only asks the reader to rewrite `chain.py`'s `solve()`, so the copies are
incidental, and they diverge from the chapter: the copied `bisection` returns
`mid` rather than `None` when it fails to converge, and it recomputes `mid` in a
different place.

Two consequences worth checking. First, the copies are silently exempt from the
book's typing standard: `ty` accepts them because implicit `Any` is not an error,
so `solutions-gate` will not notice. Second, I changed the chapter's `bisection`
to compare `f(a) * f(mid) <= 0` (see the fix list in my report), and the
solution's copy still uses `<`, so the two now differ by one character for no
stated reason.

Change I would make in `Solutions/28_Function_Objects.md` §2: replace the copied
finders with `from algorithms import bisection, newton, secant` and keep only
`solve()` and `f()` in the listing. The exercise asks for a rewritten `chain.py`,
and the solution's own discussion concedes the handlers needed no change
("Each handler function already reports its own outcome through its return
value"), so the copies buy nothing. §4 has the same shape and would benefit from
the same treatment, though there the copy is deliberate: the exercise asks the
reader to add a parameter to `newton()`.
