[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Line 62, "What Is a Pattern?" — "You have seen some design patterns in this
book" points nowhere.**

The paragraph then names inheritance and composition as examples, but neither
gets a link, so a reader who wants to go look has nothing to click. The skill's
rule is that a named link beats a relative phrase, because the phrase goes
stale silently when chapters move.

Proposed change: link both at first use.

```
The goal of design patterns is to isolate changes in your code.
You have seen some design patterns in this book.
For example, [inheritance](07_Classes.md) can be thought of as a design pattern
(albeit one built into the language).
```

and, three lines down:

```
[Composition](20_Rethinking_Objects.md#prefer-composition-to-inheritance)
also qualifies as a pattern, since it allows you to change,
dynamically or statically, the objects that implement your class,
and thus the way that class works.
```

The composition anchor is already used later in this chapter (in the
*Independence* bullet), so repeating it here is a small cost. If you would
rather not repeat it, link inheritance only.

---

[] Reject

**Lines 71-76 and 87-89 — the Iterator explanation is given twice, nearly
verbatim, fourteen lines apart.**

Line 71-73:

> Another pattern that appears in *GoF Design Patterns* is the
> [Iterator](23_Iterators.md), which has been implicitly available in `for`
> loops from the beginning of the language, and became an explicit feature in
> Python 2.2.

Line 87-89:

> Iterator is the clear case. It was implicit in the `for` loop from the start,
> and Python 2.2 made it a protocol the language calls on your behalf.

Both say the same two facts (implicit in `for` from the start; explicit in
2.2). The second one is load-bearing: it is the worked example of the
dissolution thesis. The first is an aside inside a paragraph whose job is
"here are patterns you have already met."

Proposed change: cut the historical clause from the first occurrence and let
"When a Pattern Dissolves" own it.

```
Another pattern that appears in *GoF Design Patterns* is the [Iterator](23_Iterators.md).
An iterator allows you to hide the particular implementation of the container as you're stepping through it.
```

Cost: the *first* mention then stops being an example of "a pattern built into
the language," which is the point the surrounding paragraph is making about
inheritance and composition. If you want to keep that beat, an alternative is
to trim the *second* occurrence instead, to "Iterator is the clear case," and
let the reader carry the history forward from line 71. I recommend the first
version, because the dissolution section is where a reader is looking for the
mechanism.

---

[] Reject

**Line 84 — "The missing piece can arrive in two ways" does not describe the
second way.**

The two ways given are:

1. "Sometimes a language grows the feature and the pattern dissolves into it"
2. "More often the language had the piece all along, and the pattern was
   written for one that didn't."

In the second case nothing arrives; the piece was never missing in this
language. The topic sentence therefore sets up a frame that the second half
contradicts, and a reader has to re-read to see that "arrive" was only meant
literally for case one.

Proposed change, recommended:

```
A pattern meets its missing piece in two ways.
```

Alternative, if you would rather keep "arrive" out of it entirely:

```
There are two ways a pattern finds the piece already in place.
```

Second alternative, keeping the original but repairing case two:

```
The missing piece can turn up in two ways.
```

I recommend the first: "meets" is neutral about whether the piece was grown or
was always there, and it keeps the sentence's length and rhythm.

---

[] Reject

**Section order — "Pattern Evolution" (line 104) probably belongs before
"When a Pattern Dissolves" (line 78).**

"When a Pattern Dissolves" is the chapter's thesis, and the two chapters that
link back to this chapter by anchor
(`23_Iterators.md:567`, `27_Factory.md:274`) both point at
`#when-a-pattern-dissolves`. But the vocabulary that makes dissolution precise
arrives one section later: "Pattern Evolution" gives the four-stage ladder, and
its own closing paragraph ("The ladder runs downward too... Stepping through a
container is stage one in Python and was stage four in the *GoF Design
Patterns* examples") is the same claim as the dissolution section, now stated
in stage numbers. A reader meets the idea twice, informally then formally, in
that order.

Proposed change: move "Pattern Evolution" ahead of "When a Pattern Dissolves",
so the ladder is available when dissolution is named, and "When a Pattern
Dissolves" becomes the section that cashes the ladder in.

Price of the move:

- Two inbound cross-references use the `#when-a-pattern-dissolves` anchor.
  The heading text does not change, so the anchor survives and
  `heading_links.py` stays green. Nothing else names either section by title.
- "When a Pattern Dissolves" currently ends with the forward-looking paragraph
  that names chapters 24/27/28 and points at
  `20_Rethinking_Objects.md#guidelines`. After the move that paragraph would
  sit closer to "Pattern Taxonomy," which is fine; it reads as a bridge either
  way.
- The Iterator duplication in the previous finding gets worse if you move the
  sections without also resolving it, because the two Iterator passages end up
  further apart with the ladder between them. Do both or neither.

This is a pacing change, so it stays a proposal. If you would rather not move
anything, the cheap version is a forward pointer at the end of "When a Pattern
Dissolves": one sentence saying the next section names the stages a pattern
passes through, and that a dissolved pattern has dropped back to the first.

---

[] Reject

**Line 167 — listing *State Machines* among the Behavioral patterns conflicts
with where the book actually puts GoF *State*.**

The Behavioral bullet cites "[Observer](30_Observer.md),
[State Machines](31_State_Machines.md), and [Visitor](33_Visitor.md)".
But `39_Pattern_Catalog.md`'s Behavioral table maps GoF *State* to
`26_Surrogate.md#state`, and this chapter's own Structural bullet lists
[Surrogate](26_Surrogate.md), which is where *Proxy* and *State* live. Chapter
31 opens by saying *StateMachine* is a structure built on top of *State*, not
GoF *State* itself, so the reader is pointed at the derivative rather than the
pattern.

Two things are entangled here, and the second is the interesting one:

1. The named example is off by one chapter. *State*, a Behavioral pattern in
   GoF's own classification, is presented in this chapter under *Structural*
   because the book groups it with *Proxy* by shape.
2. That is not an error, it is the chapter's argument two paragraphs later
   ("Patterns often resemble each other more in their implementations than the
   *GoF Design Patterns* categories suggest, and that is how this book groups
   them"). But the argument arrives after the taxonomy list, so on first
   reading the list just looks wrong.

Proposed change: swap the Behavioral example and add one clause acknowledging
the collision, so the reader sees it is deliberate:

```
    This book contains multiple examples including [Observer](30_Observer.md),
    [State](26_Surrogate.md#state), and [Visitor](33_Visitor.md),
    though *State* appears in this book beside *Proxy*,
    for reasons the next section gives.
```

Alternative, lighter: leave the list alone and only move the "Patterns often
resemble each other" paragraph up, so it precedes the three-bullet list rather
than following it. That fixes the reading order for all three bullets at once
but changes the section's shape.

---

[] Reject

**Lines 194-196 — "design structures" is used where "design patterns" is
meant, and the principle-versus-pattern distinction is never stated plainly.**

> Design principles are at least as important as design structures,
> but for a different reason.
> Principles ask questions about your proposed design and test it for quality.

"Design structures" appears nowhere else in the book; the thing being contrasted
is design patterns. And the contrast is left implicit: a pattern is a shape of
solution, a principle is a test you apply to a solution. That is the sentence a
first-time reader needs, and it is exactly the sentence the section does not
write.

Proposed change:

```
Design principles are at least as important as design patterns,
but they do a different job.
A pattern is a shape of solution.
A principle is a test you apply to whatever shape you chose.
```

---

[] Reject

**Line 196 — "Principles ask questions" but none of the fourteen bullets is a
question.**

Every bullet is an imperative or a definition: "Express independent ideas
independently," "One abstraction per class," "Make things as immutable as
possible." The framing sentence promises questions and the list delivers
assertions, so the reader has to do the conversion themselves.

Two ways out.

Recommended: change the framing to match the list.

```
Each one is a claim you can hold a design up against.
```

Alternative: keep the framing and phrase the list to match, e.g.
*Reflexivity* becomes "Does each class carry exactly one abstraction?" That is
a larger rewrite of a list that reads well as it stands, and it loses the
compactness that makes the list memorable. I would not do it.

---

[] Reject

**Line 206 — "This does not appear to be a linear factor, but an exponential
one" is an unsupported quantitative claim.**

The *Consistency* bullet argues that piling arbitrary rules on a programmer
slows them down, then asserts the slowdown is exponential rather than linear.
There is no measurement behind this, and "exponential" used loosely for "much
worse than linear" is the kind of phrasing the book avoids elsewhere.

Proposed change: keep the point, drop the false precision.

```
    The cost does not grow one rule at a time; the rules interact.
```

Alternative, if you want to keep the shape of the original sentence: "The cost
of each new rule is not independent of the ones already there."

---

[] Reject

**Line 223 — "Generally attributed to Antoine de Saint-Exupéry" hedges an
attribution that the same footnote then makes exactly.**

The footnote reads: "Generally attributed to Antoine de Saint-Exupéry, from
*Wind, Sand and Stars*". The quotation is his, and the book is right (*Terre
des hommes*, 1939, published in English as *Wind, Sand and Stars*). What is
genuinely uncertain is only the English wording, which varies by translation.
As written, "generally attributed" reads as doubt about the author.

Proposed change:

```
^[Antoine de Saint-Exupéry, *Wind, Sand and Stars*: "perfection is reached not when there's nothing left to add, but when there's nothing left to remove". The English wording varies by translation.].
```

If you would rather keep the footnote to one sentence, drop the translation
note and just delete "Generally attributed to".

---

[] Reject

**The chapter has no listing at all, and the three claims that carry the
thesis are asserted rather than shown.**

Lines 92-98 make the chapter's most quotable claims — *Strategy* and *Command*
shrink to passing a function, a Factory becomes a dictionary, a Singleton
becomes a module — and every one of them is a forward promise to a later
chapter. A reader closing this chapter has the argument but has not seen it
happen once.

This is deliberate: line 14 says "This chapter introduces the concepts; the
chapters after it supply the code." So this finding is a question rather than a
defect report.

Proposed change, if you want it: one three-line listing after line 98, showing
the whole of a Strategy in Python, with the classic form named but not written.

~~~python
# strategy_is_a_function.py
from collections.abc import Callable

def apply(nums: list[int], how: Callable[[list[int]], int]) -> int:
    return how(nums)
print(apply([3, 1, 2], max), apply([3, 1, 2], sum))
#: 3 6
~~~

(Verified in this workspace: runs, `ty check` clean, `ruff check` clean at
width 70, output matches the marker.)

That would make the chapter's opening promise concrete at the point it is
made, and chapter 28 still does the full treatment. Cost: it breaks the "no
code in this chapter" rule the chapter states about itself in line 14, so line
14 would need adjusting too ("one listing to make the point, and the chapters
after it supply the rest").

I lean toward not doing this. The chapter is short and reads well as an
argument, and the payoff is one page-turn away. Recorded because the teaching
pass asks the question, not because I think the chapter is weaker without it.

---

[] Reject

**Line 263, Exercises — all three exercises depend on the reader's own prior
code, and there is no `Solutions/21_The_Pattern_Concept.md`.**

Two related problems.

*The exercises are not answerable from the chapter.* Exercise 1 needs "a
program you have written that changed more than once." Exercise 2 needs "a
pattern you know from another language." Exercise 3 needs "a design of your
own." Chapter 1 describes the book's exercises as asking you "to change a
small, already-working example from that chapter and observe the result." This
chapter has no example to change, so its exercises reach outside for material,
and a reader with no such program or no other-language background is stuck at
all three.

*There is no solutions file.* `01_Introduction.md:202` promises, without
qualification, "Solutions live in the `Solutions/` directory of the source
repository." `Solutions/21_The_Pattern_Concept.md` does not exist. (Chapters
44, 45, and 46 have the same gap; see Cross-chapter below.)

The two problems have one cause: open-ended reflective exercises have no single
right answer to put in a solutions file.

Proposed change, recommended: write `Solutions/21_The_Pattern_Concept.md` with
a worked example of each, using your own material — a vector of change from one
of the book's own examples for exercise 1, GoF *Strategy* struck down to a
`Callable` for exercise 2, and one of the book's own designs for exercise 3.
The value is in showing what a good answer looks like, not in being the answer.
That is outside this chapter's file, so I did not write it.

Alternative, if you would rather not write that file: add one line under the
`## Exercises` heading saying these three have no single right answer and no
solutions file, and rephrase Chapter 1's promise from "Solutions live in the
`Solutions/` directory" to "Most chapters' solutions live in the `Solutions/`
directory." Both halves are needed; doing only the first leaves Chapter 1
lying.

Second alternative, if you want the exercises to be self-contained: add a
fourth exercise that works from the chapter alone, e.g. "Take the four stages
in *Pattern Evolution* and place `sorted(key=...)`, a `dict` of handlers, and
`contextlib.contextmanager` on the ladder. Say what would have to change for
each to move up one stage."

---

## Cross-chapter

**`Solutions/` — four chapters with `## Exercises` and no solutions file.**

`21_The_Pattern_Concept.md`, `44_Effect_Management.md`, `45_Generators.md`, and
`46_Stateless.md` all have an `## Exercises` section with no matching file in
`Solutions/`. (`01_Introduction.md` also has an `## Exercises` heading, but it
is the meta-section explaining what exercises are, so it needs nothing.)

`01_Introduction.md:202` states the promise unconditionally. Change to make
there, if you take the "no solutions file" route for chapter 21: line 202
becomes

```
Most chapters' solutions live in the `Solutions/` directory of the source repository.
```

I did not touch `01_Introduction.md` or `Solutions/`.

**Chapters 24 and 28 do not link back to `#when-a-pattern-dissolves`.**

This chapter's thesis is cashed in by four chapters, and only two of them point
back at it:

| Chapter | Section that cashes the thesis | Links back to 21? |
| --- | --- | --- |
| 23 Iterators | "The Pattern That Disappeared" | yes, `#when-a-pattern-dissolves` |
| 24 Singleton | "A Module Is Already a Singleton" | no |
| 27 Factory | "The Pythonic Factory: a Dictionary" | yes, `#when-a-pattern-dissolves` |
| 28 Function Objects | chapter opening, lines 3-14 | no |

Chapter 21 names all four in the forward direction (lines 92-98), so the thread
is one-directional at two of its four ends. The two back-links I would add,
matching the wording 23 and 27 already use:

In `Chapters/24_Singleton.md`, at the end of the "A Module Is Already a
Singleton" section:

```
This is the dissolution described in [The Pattern Concept](21_The_Pattern_Concept.md#when-a-pattern-dissolves).
```

In `Chapters/28_Function_Objects.md`, after line 9 ("These three patterns are
largely unnecessary in Python."):

```
This is the dissolution described in [The Pattern Concept](21_The_Pattern_Concept.md#when-a-pattern-dissolves).
```

I did not touch either chapter. Note that the `#when-a-pattern-dissolves`
anchor now has four inbound references if these land, so that heading's text is
effectively frozen.
