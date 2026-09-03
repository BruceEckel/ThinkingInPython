# Adversarial review: the undecided queue

The application pass (2026-09-03) applied 213 of the review's 252
findings and declined one with a contra-reproduction. These 38 are the
rest: every one needs a call only the author can make, usually because
the fix cuts, moves, or rewrites material, adds an exercise that needs
a written solution, or chooses between two reasonable shapes on voice.
Each entry carries the applying agent's recommendation. Deleting an
entry (decided against) or applying it by hand both count as resolving
it; when the file is empty, archive it beside `~adversarial_review.md`.

The one declined finding, recorded so no later pass re-proposes it:
chapter 32's suggestion to type `duel()` with a `Protocol` fails
against the real call shape (`item_pair_gen(Item, n)` types the pair
as base `Item`, which declares no `compete()`; `ty` rejects the
Protocol version with `invalid-argument-type`). The `Any` is
deliberate and the nearby prose already explains the trade.

## Chapter 01 (Introduction)

- **The AI essay splits the two practical "how to use this book"
  sections.** Moving a 65-line personal essay is a structural call.
  Recommendation: move "AI Trigger Warning" after Resources/Copyright,
  or before "Who This Book Is For," so "How the Book Fits Together"
  and "The Examples" sit adjacent.
- **The AI section ends on an unrebutted hedge** ("might have some
  value yet"). Tone is the author's. Recommendation: follow the hedge
  with the stronger guiding-AIs claim already made two paragraphs up,
  instead of trailing off on doubt.
- **The strongest pro-book AI-era argument is asserted, not shown.**
  Needs a real anecdote only Bruce has: one concrete case where
  book-level Python judgment steered an AI to a better solution.

## Chapter 03 (Containers)

- **`frozendict`, the chapter's one 3.15-native feature, has no
  exercise.** A new exercise needs a written solution in
  `Solutions/03`. Recommendation: exercise 10, build a `frozendict`,
  use it as a dict key, catch the mutation `TypeError`.

## Chapter 04 (Control Flow)

- **The opening is a definition plus a table of contents, not a
  hook.** Picking the hook is voice. Recommendation: open with the
  EAFP or no-labeled-`break` contrast, mirroring chapter 03's
  C++/Java opening move.

## Chapter 05 (Functions)

- **"Default and Keyword Arguments" bundles defaults, the
  mutable-default trap, and sentinels under one heading.** Splitting
  it moves the `#default-and-keyword-arguments` anchor, which six
  chapters link to (03, 09, 12, 15, 23, 41), some meaning the
  defaults half and some the sentinel half. Recommendation: split
  into "Default Arguments" and "Sentinel Values" and repoint each of
  the six links to the half it means.

## Chapter 07 (Classes)

- **"Composing Methods with `import`" teaches a technique its own
  closing sentence disavows.** Recommendation: fold it into a short
  aside (2-3 sentences) or cut it, mentioning the import-into-class
  behavior in passing.

## Chapter 12 (Data Classes as Types)

- **The A/B/C/D "Comparing Ordinary Classes and Data Classes"
  digression (~200 lines) interrupts the validate/freeze/compose
  through-line.** Recommendation: move it earlier, right after
  `@dataclass` is introduced, since none of A/B/C/D touch validation.

## Chapter 17 (Metaprogramming)

- **Descriptors get the mechanism with no reason to want one.**
  Making `Field` validate would break the premise of an exercise
  whose solution says "`z = Field()` needs no change to the `Field`
  class itself," and would need a Solutions update. Recommendation:
  add a separate short validating-descriptor example rather than
  modifying `Field`.
- **"The `inspect` Module" spends ~380 of its 430 lines on
  `display.py`'s presentation layer.** Recommendation: move the
  formatting helpers and the dunder/exclude option tour to an
  appendix or reference section, keeping
  `getmembers_static`/`signature`/`get_annotations` in the narrative.
- **The third "you still need a metaclass" bullet is one the chapter
  already solved with `__init_subclass__`.** Recommendation: qualify
  it ("an invariant a base class cannot express because the family
  shares no base") rather than cut it.

## Chapter 19 (Concurrency)

- **The coordination primitives are split across 1,300 lines**
  ("Locks" at 648, "Locks, Semaphores, and Failure Modes" at ~1975).
  Recommendation: move Semaphores up beside Locks and keep only
  Deadlock/Livelock at the end, or move the whole block.

## Chapter 21 (Design Patterns)

- **Nine of the twelve Design Principles are never invoked by name
  again anywhere in the book.** Recommendation: either trim to the
  principles the book uses (Subtraction, immutability, pure
  functions, now LSP) or keep the list as explicit reference
  material; possibly no action needed.

## Chapter 25 (Template Method)

- **Substitutability has no code in the body; exercise 4 is its only
  concrete form.** Showing it in the body partly preempts the
  exercise. Recommendation: add a brief 4-6 line counterexample in
  the body and keep exercise 4's task distinct (a different
  override).

## Chapter 27 (Factory)

- **True Factory Method never appears standalone, only embedded in
  Abstract Factory.** Recommendation: add a short one-hierarchy,
  one-overridden-creation-method listing just before "Abstract
  Factories."

## Chapter 30 (Observer)

- **The ~150-line grid example's incidental complexity outweighs its
  Observer content.** Recommendation: compress `recolored()` and
  `adjacent()` to a short description, or use a simpler
  single-cell-recolor model. (The async gotchas the cut was meant to
  fund are now demonstrated, which weakens the urgency.)

## Chapter 32 (Multiple Dispatching)

- **Exercise 9 asks the reader to build what
  `paper_scissors_rock_table.py` already is.** A retarget rewrites
  the exercise's substance and orphans its existing solution.
  Recommendation: retarget it at a callable-valued table (keeping the
  `item1.compete(item2)` call site) and rewrite the Solutions answer
  alongside.

## Chapter 34 (Composite and Interpreter)

- **The classic/data-class comparison changes four variables at
  once.** Recommendation: rewrite `filesystem_classic.py` as frozen
  dataclasses with methods, isolating where operations live as the
  one difference. A listing rewrite with its own markers.
- **"A Composite of Data Classes" re-derives chapter 20 at nearly
  full depth while the genuinely new part (the recursive union) gets
  three lines.** Recommendation: compress the recap to 2-3 sentences
  with a link, expand the recursion, and name the expression problem.

## Chapter 36 (Memento)

- **`History` names a hazard (`do()` discipline) it could design away
  with an `apply()` method.** Both shapes are defensible; the chapter
  currently teaches the hazard. Recommendation: either add
  `apply(edit)` or add one sentence saying why the explicit two-step
  reads better.

## Chapter 37 (Pattern Refactoring)

- **The Visitor half never earns its redesign with a demonstrated
  requirement and cost**, unlike the first half's plastic scenario.
  Recommendation: invent a second operation-vector requirement (a
  `note()`-consuming operation) and show the cost of methods-on-
  `Trash` growing, mirroring `plastic_dropped.py`'s shape.
- **The Visitor section re-argues chapter 33 before saying anything
  new.** Recommendation: trim the double-dispatch re-explanation to a
  sentence and a link; let the two-dispatch-mechanisms disagreement
  (exact-keyed `bins[type(t)]` vs MRO-following `singledispatch`) be
  the section.
- **`sum_value()`'s per-piece logging buries both sorters' output**
  (~30 marker lines each, 4 of which matter). Cutting it ripples
  through several listings' full marker sets and possibly Solutions.
  Recommendation: drop the per-piece line, leaving the four
  `--- Kind --- / Total value` pairs per run.

## Chapter 38 (Simulation)

- **The robot section fails the chapter's own definition of
  simulation and is its longest section.** Recommendation: either
  move a real path-choosing search into the main text or state
  explicitly that the section teaches polymorphism/Factory/Null
  Object by contrast.
- **Two of the three GUI views re-render what the models already
  print.** Recommendation: keep `chladni_view.py` in full; reduce
  `rats_view.py` and `maze_view.py` to a sentence and a file pointer.

## Chapter 40 (Functional Foundations)

- **`pipeline.py`, the chapter's synthesis example, is the only one
  never exercised.** Needs a new exercise plus solution.
  Recommendation: exercise 9, extend `pipeline.py` with a
  `colder_than` stage or a second `map()` step.
- **The Lambdas section has no listing and exists to point forward.**
  Recommendation: merge it into "Higher-Order Functions" as the lead
  paragraph, dropping the standalone heading.

## Chapter 41 (Functional Toolkits)

- **`permutations`/`combinations`/`combinations_with_replacement` are
  three flat reference entries.** Recommendation: merge into one
  entry contrasting order-matters vs not, repeats vs not, matching
  `zip_longest`'s three-way-comparison style.

## Chapter 43 (Confidence)

- **"Declarative Style" is recap-only and its one contribution is
  unargued.** Recommendation: cut it to a short paragraph inside "A
  Confidence Spectrum" unless a concrete law-checkable-on-the-
  declarative-form example is wanted.

## Chapter 44 (Effect Management)

- **The "Custom AI Languages with Effects" catalog: 23 lines of links
  carrying two sentences of teaching, and it will date within a
  year.** Recommendation: keep the two teaching sentences plus Pact
  and Lumen; drop the ten-link catalog.
- **The Effect definition ("causes impurity") and the three-kind
  taxonomy rest on a criterion switch.** Redefining the term touches
  its uses across chapters 44/46/47. Recommendation: define an Effect
  once, in propagation terms (what a caller inherits that the
  signature does not show), after confirming 46/47 stay consistent.
- **The opening anecdote is retold with the same details 340 lines
  later.** Recommendation: compress the retelling to its existing
  one-sentence callback and go straight to the four questions.

## Chapter 46 (Stateless)

- **Handler layering (partial `supply()`) is taught as bullet 2 of
  the DI comparison.** Recommendation: give it its own section next
  to "Supplying the Dependency," with "A Default Binding" as its
  corollary.
- **"Builtin Dependencies" arrives 620 lines after the chapter starts
  hand-rolling `Console`.** The one-line rationale at `greeter.py` is
  now in place; the larger move remains. Recommendation: relocate the
  section and fold the concrete-class-forces-inheritance content into
  "Supplying an Interface."

## Chapter 47 (Stateless in Practice)

- **`wallet.py` uses the module-level global its own prose disowns,
  and the testability payoff is asserted, not shown.**
  Recommendation: give it a `ledger(cell)` factory returning the
  handler pair plus a 3-line test from a fresh `Cell`, matching the
  clock section's pattern.
- **Limit 2 spends ~50 lines proving the case that works and eight
  unevidenced lines on the case that fails.** Recommendation: swap
  the emphasis; show the nested-`handle` `Unknown` reveal, compress
  the working partial-handling demo.
- **"Supplying a Whole Cast" spends ~115 lines of listing on two new
  ideas.** Recommendation: three actors instead of five make the
  Abstract Factory contrast and the nine-overload ceiling at half the
  reading cost.
