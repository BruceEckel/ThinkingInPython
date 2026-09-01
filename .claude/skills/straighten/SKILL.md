---
name: straighten
description: Unwind sentences the reader must hold open too long. A buried actor, a subject far from its verb, a noun rescued by stacked modifiers, or one sentence carrying three consequences gets straightened, usually by naming the actor or splitting at the seam. Use when asked to straighten, simplify, or untangle a chapter's sentences (or the book's). The argument names chapters by number or name; no argument means all of Chapters/.
---

# Straighten: one sentence, one load

A sentence fails when the reader must hold something open
across too much text before it resolves.
The failure is not the words, which the cutting passes already trimmed,
and not the paragraph, which `cohesion` already ordered.
It is the architecture of the single sentence:
what sits in subject position,
how far that subject is from its verb,
and how many claims ride on one predicate.
The tell is a sentence you have to read twice
even though every word in it is right.
This pass finds those and straightens them,
almost always by naming the actor or splitting at the seam.
It edits `Chapters/NN_*.md` prose only;
code blocks, `#:` output markers, and quoted material stay untouched.

## The test

Read the sentence once, at normal speed, and stop at the main verb.
Ask what you were holding in your head when you got there.
If the answer is "a subject I had to keep open" or "I had not found the
verb yet", the sentence needs straightening.

A second test for overload:
count the independent claims after the main verb.
One is a sentence.
Two joined by a real relation is a sentence.
Three, or two joined only by "and", is two sentences waiting to be split.

## Where sentences go wrong

**The buried actor.**
Something in the sentence is doing the acting,
and it is not the subject.
Put it in front and the sentence usually needs no other repair:

- "A `Factory` class nested in every shape is machinery Python does not need."
  becomes "Python does not need a `Factory` class nested in every shape."
- "A dictionary of classes, whether you fill it by hand or the classes
  fill it themselves, is the ordinary Python factory."
  becomes "The ordinary Python factory is a dictionary of classes,
  whether you fill it by hand or the classes fill it themselves."
- "and uncommenting the line that passes a `BrokenFactory` to
  `GameEnvironment` produces `protocol member ... is not defined`"
  becomes "Uncomment the line that passes one to `GameEnvironment`,
  and the checker reports `protocol member ... is not defined`."

**The subject held open.**
The subject arrives, then a relative clause, a parenthetical, or a
citation, and only then the verb.
Ten or so words of gap is the threshold; a parenthetical citation in the
gap is the threshold on its own:

- "Letting each subclass register itself through `__init_subclass__()`
  (see [Metaprogramming](...)) removes that line too"
  becomes "`__init_subclass__()` (see [Metaprogramming](...)) lets each
  subclass register itself. That removes the `SHAPES` line too"
- "so a `kind` read from a configuration file, a request, or a command
  line is arbitrary code rather than a shape name"
  becomes "so a configuration file, a request, or a command line can hand
  it arbitrary code instead of a shape name"

**The overloaded sentence.**
One main verb, then a colon and three consequences,
or two independent facts joined by "and".
Split at the seam and let each stand:

- "Because a `class` statement is executable code, every call would
  define fresh `Circle` and `Square` classes: two shapes from different
  calls would share behavior but not a class, failing `type(a) is
  type(b)` and `isinstance()` alike, and `Shape.__subclasses__()` would
  be empty until the first call, then gain a duplicate on every call
  after that."
  becomes three sentences: the classes get redefined; what that does to
  identity; what it does to `__subclasses__()`.
- "The module body, and with it the registration, does not run until the
  first use of the imported name, and an import written only to trigger
  registration never uses that name."
  becomes two sentences, since the second fact does not depend on the
  first.

A because-clause and a so-clause in the same sentence is the same
finding: split at the seam.

**The noun rescued by stacked modifiers.**
A vague noun ("the form", "the way", "the machinery", "the effect")
followed by a reduced relative clause and then a "where" or "that"
clause. The reader holds the noun open across two layers.
Delete the noun and state the mechanism:

- "uses one to show the form a factory-object design takes where a class
  is not an object you can store"
  becomes "includes one because a language that cannot store a class in
  a dictionary must wrap each constructor in an object"

**The elliptical predicate.**
A "do", "does", or "is" standing in for a verb phrase that is now a
clause away. Spell the verb out, or split so the ellipsis sits next to
what it replaces:

- "the two nested classes satisfy it without naming it, and the
  `ShapeMaker` in the annotation makes the checker verify they do"
  becomes "... conform without naming it. The `ShapeMaker` in the
  annotation makes the checker verify that they conform."

**Punctuation carrying too much.**
A parenthetical wedged between verb and object, or a comma where the
sentence needs a colon:

- "raises a `TypeError` (`cannot pickle '_thread.lock' object`) instead
  of cloning" becomes "raises a `TypeError` instead of cloning:
  `cannot pickle '_thread.lock' object`"
- "removes the other reasonable use, configuring a builder once and
  building from it twice" becomes "... use: configuring a builder once
  and building from it twice"

**Doubled possession and other said-twice phrases.**
Small, but they are what makes a straightened sentence still feel heavy:

- "a subclass that gives itself a `registry` of its own"
  becomes "a subclass that defines its own `registry`"
- "a list of references to each direct subclass of `Shape`"
  becomes "a list of `Shape`'s direct subclasses"

## Boundaries

- **A definitional "is" stays.**
  "Checking against a Protocol is structural typing" is a definition,
  where "is" carries the claim.
  The finding is an abstract noun propped up by a relative clause,
  not every copula.
- **Terms of art stay.**
  "That is the dissolution *Design Patterns* describes" looks like a
  buried actor, but "dissolution" is the book's word in chapters 23, 27,
  and 28, and chapter 28 phrases it the same way.
  Grep the book before rewording a noun that reads like jargon;
  if other chapters use it, it is a term, and changing one instance
  breaks the set.
- **Splitting is not always right.**
  Two clauses joined by a real relation (because, so, but) are one
  thought and stay one sentence.
  Split when the join is "and" or a colon carrying a third claim.
- **Do not cut past the meaning.**
  A sentence that loses its reason or its consequence is not
  straightened, it is broken.
  Restore the missing half rather than trimming further.
- **Leave the listings alone.**
  A long line inside a fenced block is the listing's problem,
  gated by ruff and the `widths` check, not this pass's.
- **Check the exemption records first.**
  `deep_review_db.md` in the repo root carries standing exemptions,
  and `bruce_edit_db.md` carries the promoted editing rules.

## Boundary with the neighboring passes

- `elements-of-style` and `activate` cut words and fix voice.
  If deleting words fixes the sentence, they already did it;
  what is left for this pass is a sentence whose every word earns its
  place and still reads twice.
- `literal` replaces a figure of speech with the mechanism.
  That often produces a longer noun phrase, which is why this pass runs
  after it.
- `cohesion` orders sentences within a paragraph.
  Splitting a sentence hands `cohesion` and `antecedents` new material,
  which is why this pass runs before both.
  If the fix is to move a sentence, leave it for `cohesion`.

## Verify and report

Touched prose gets `make reflow CH=NN` (Semantic Line Breaks),
then `make verify`, then read `git diff Chapters/`:
a changed `#:` marker means an edit strayed into code, so investigate it.
A split sentence can add a `prose` warning (a new sentence opening with
"There is", a new passive), so run `make prose CH=NN` too.
Report each change as the sentence's failing shape and the fix.
List any sentence you judged overloaded but left, with the reason.
Bruce reviews the diff and commits himself.

## Accrued patterns

Sentence shapes Bruce has flagged that the categories above do not name
yet. When he identifies a new one, add it here as a bullet with a
before/after pair, and it becomes part of every future pass.
