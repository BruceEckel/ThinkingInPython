---
name: deep-review
description: Deep-review a book chapter: a correctness/editing pass, a teaching pass (misconceptions, lookalike pairs, mechanism vs. outcome, near-miss code, plus chapter-level pedagogical structure), and a house-style audit of listings. Use whenever asked to deep review, thoroughly review, or audit a chapter.
---

# Deep-reviewing a chapter: two passes, not one

A request to "deep review" a chapter means an editing pass *and* a
teaching pass. The editing pass is correctness: verify every technical
claim (web-search anything post-cutoff or version-dependent), run the
chapter's gates, execute the extracted scripts directly and compare
against their `#:` markers — repeatedly for timing-comparison booleans,
since the self-healing gate would silently flip a flaky `True` to
`False` — and fix outright errors in prose or code.

The teaching pass asks what's *missing*, which a correctness pass never
surfaces. Read as a first-time reader and apply these lenses:

- **Misconceptions:** what would a reader still misunderstand after each
  section? What question does it raise but not answer?
- **Lookalike pairs:** list every pair of similar constructs the chapter
  uses (`asyncio.sleep()`/`time.sleep()` was the canonical miss); is the
  difference taught, or just assumed?
- **Mechanism vs. outcome:** does each example show *how* the machinery
  works, or only the final result? The test: could a reader narrate the
  mechanism from the output alone? Tracing output (start/resume lines)
  often teaches more than a summary number.
- **Near-miss code:** what would a reader plausibly write instead of the
  shown idiom (`[await c for c in coros]` instead of `gather()`), and
  does the chapter warn them it behaves differently?

Those four lenses work section by section. The teaching pass has a
second altitude: a chapter can pass all four and still be hard to learn
from, because the difficulty is in the order and the pacing rather than
in any one passage. Read the chapter again, front to back, as someone
meeting the topic for the first time, and ask:

- **One claim, one arc.** State the chapter's claim in a sentence. Then
  check that each section moves that claim forward. A section that could
  be cut with nothing downstream noticing should be cut, or the claim is
  bigger than the sentence admits and needs restating.
- **Motivation before mechanism.** Does the reader know why they need
  this before being shown how it works? A section that opens with
  machinery makes them decode syntax with no reason to care, and the
  reason is usually sitting a page later where it does no good.
- **One new thing per listing.** Each listing should introduce a single
  unfamiliar element. A listing that teaches the chapter's topic and an
  unrelated construct at once splits the reader's attention and teaches
  neither. Move the unrelated part into its own listing.
- **Nothing used before it is taught.** Every term is defined at first
  use, and no listing depends on a construct introduced later in the
  book. The reverse direction matters too: when a chapter leans on
  earlier material, it should say which chapter, and a named link
  (`[Iterators](23_Iterators.md)`) beats "as you saw earlier", which
  goes stale silently when chapters are split or renumbered.
- **Escalating difficulty.** The first listing in a section should be
  the smallest thing that makes the point, with complications added one
  at a time afterward. A section that opens at full complexity and then
  simplifies is inverted.
- **Exercises earn their place.** Each exercise should be answerable
  from this chapter, and the set should cover the chapter's main claims
  instead of clustering on whichever section was most fun to write.
- **The reader can do something new.** By the end, name the capability
  the reader gained. If the honest answer is "understands a concept",
  the chapter probably needs a listing they could adapt to their own
  code. The conclusion carries part of this load: it is titled for its
  content and adds an insight rather than rehashing the chapter.

A third, mechanical pass audits each listing against the house style
in `thinking-in-python-skill.md`: the book's listings must practice
what its chapters preach. The trigger is an *unexplained* deviation.
`interned_color.py` hand-rolls what a dataclass generates and the
prose says why, which is fine; chapter 19's `Meter` carried a
hand-written field-assigning `__init__` for no reason, which is the
drift this pass exists to catch. `grep "def __init__(self" Chapters/`
is a cheap sweep for the most common case.

When a chapter documents a third-party library, read that library's
source before asserting anything about it. Its exports and docstrings
are not enough. Reading `stateless`'s `functions.py` and `effect.py`
overturned two claims I had already given the author: that `retry` had
no equivalent (it exists, and its signature explains why it decorates a
function rather than an Effect), and that `catch()` missing a raised
exception was a library bug (it is correct behavior, since `catch()`
matches yielded values). `.venv/Lib/site-packages/<pkg>/` is right there.
Probe with `reveal_type()` for types and a scratch script for runtime.

Implement confident, small fixes directly. For additions — new listings,
new exercises, restructured explanations — propose first and let the
author decide: additions change voice and pacing, and rejecting
candidates that would bloat the chapter is part of the author's role.
Any new listing follows the full verify loop in `CLAUDE.md` (fenced
block with `# slug.py` first line, deterministic markers or wide-margin
threshold booleans, sync, gates, `make reflow CH=NN` on the new prose).

Accrued notes from the chapters 18-38 review sweep:

- "reach for" sits in `tools/data/banned_phrases.txt` and is an easy tic to
  type when drafting new prose; the gate catches it, but check drafts
  for it before running the gate.
- "promise" as a metaphor has no gate and cannot get one: the book has
  ~30 deliberate uses (chapter 20's four "OOP promise" section themes,
  9/12's promise-rather-than-placeholder contrast, 39's Future/Promise
  catalog row, `Effect.runPromise` inside a TypeScript listing), so a
  literal `banned_phrases.txt` entry would fail the build on all of
  them. Check it by reading. A `Promise` is a concrete object in
  JavaScript and Python readers map it onto `Future`, so the metaphor
  misreads as the concurrency construct, worst in 19/44/45/46/47.
  Say what the thing does: an annotation *declares*, *states*, or
  *requires*; a checker *enforces*. Watch for the metaphor shifting
  mid-sentence, one thing promising and another keeping the promise.
- Cross-chapter threads now exist whose ends must stay consistent when
  either end is edited: reflected operators and `NotImplemented` are
  taught in 32 (`radd_dispatch.py`) and applied in 34 (`expr.py`, plus
  its exercise 6); exact-type dict dispatch is noted in 31 (engine),
  32 (OUTCOME table), and 37 (`bins[type(t)]`); the registry factory's
  import-time-registration and name-collision caveats live in 27 and
  back the registries in 20/37; frozen-is-shallow is demonstrated in 20
  (`frozen_leaky.py`) and assumed by 22's `NamedTuple`-vs-frozen
  contrast and 35/36's immutability arguments; the load-bearing-`Any`
  bargain runs 22 → 33; the constructor-starts-the-engine trap runs
  25 (`premature_engine.py`) → 31 (StateMachine's `__init__`); 29 ends
  with the wrapper disambiguation map (Proxy/Decorator/Adapter/Façade)
  that leans on 26 and 14; 21's dissolves-into-the-language thesis
  (Norvig footnote) is what 23/24/27/28's "Pythonic" sections cash in.
