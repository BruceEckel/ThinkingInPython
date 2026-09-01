---
name: literal
description: Replace figurative language with a statement of what the machinery does. Every metaphor, image, or personification standing in for a mechanism becomes the mechanism, named with its actor and its event. Use when asked to make a chapter (or the book) literal, or to remove metaphors. The argument names chapters by number or name; no argument means all of Chapters/.
---

# Literal language: say what the machinery does

The book explains mechanisms,
and a metaphor in place of a mechanism asks the reader to decode an image
and then guess which mechanism it stands for.
Orwell's first rule covers it
("never use a metaphor, simile, or other figure of speech
which you are used to seeing in print"),
and the book's own edits show the replacement every time:
not a shorter sentence, but a more specific one.
"`__getattr__()` trades that for reach" became
"`__getattr__()` gives up that check to forward every method,
including ones added later."
The metaphor was two words; the mechanism is a clause;
the clause is what the reader needed.

This pass never shortens prose for its own sake
and never makes a sentence more abstract.
Its one move is to replace an image with the event it stands for.
It edits `Chapters/NN_*.md` prose only;
code blocks, `#:` output markers, and quoted material stay untouched.

## The test

For each verb or verb phrase that is not the plain name of an action,
ask two questions.

1. **Is it the documented term?**
   A word that Python's documentation, the typing PEPs, or the
   standard library uses for this exact thing is literal,
   whatever its origin.
   *Raise* and *catch* an exception, *bind* a name, *hook*,
   *wrap*, *forward*, *delegate*, *fall through*, *shadow*,
   *mangle*, *leak* (memory), *thread*, *pool*, *stack*, *queue*,
   *pipe*, *stream*, *sandbox*, *fixture*, *mock*, *stub*
   are all terms, not figures. Keep them.
2. **What actually happens?**
   Name the actor and the event.
   If the literal sentence says more than the image did,
   it is the right sentence.
   If you cannot say what happens without the image,
   the image was hiding a claim the chapter never made,
   and the fix is a block in a deep review, not a rewording here.

## Where figures hide

**Motion and place standing for control flow.**
Code does not travel. It runs, returns, raises, calls, forwards, reports.

- "the check lands before the loop"
  becomes "the check runs before the loop"
- "the error surfaces as `RecursionError`"
  becomes "the error is reported as `RecursionError`",
  or better, name who reports it:
  "Python reports it as `RecursionError`"
- "`Need[Dough]` and `Need[Oven]` travel up through `yield from`"
  becomes "`yield from` carries the inner Effect's abilities to its caller"
  (the verb "carries" is the documented behavior of `yield from`,
  which relays what the inner generator yields)
- "the failure bubbles up to `run()`"
  becomes "the failure propagates out of every frame to `run()`",
  since *propagate* is the term the exception documentation uses
- "the guarantee is lost at the hop through the surrogate"
  becomes "the checker cannot see a method that `__getattr__()` supplies"

**Force and physical work standing for an effect.**
*Fires, trips, bites, hits, breaks, bolts on, bakes in, wires up,
plugs in, sands off, chews through.*

- "the trap fires on the first attribute access"
  becomes "the first attribute access calls `__getattr__()`,
  which reads the missing name and calls `__getattr__()` again"
- "the decorator bolts a registry onto the class"
  becomes "the decorator adds the class to a registry"
- "the rule is baked into the type"
  becomes "the type declares the rule"
  or "the checker enforces the rule from the annotation"

**Commerce standing for a consequence.**
*Costs, buys, pays, earns, trades, cheap, expensive, the price, the bargain.*
A measured cost (time, memory, a benchmark, a line count) is literal
and stays.
A rhetorical one names nothing:

- "`@final` costs one decorator and protects everyone who runs the checker"
  becomes "`@final` is one decorator,
  and the checker reports an override of `run()` before the program runs"
- "the abstraction buys you nothing here"
  becomes "the abstraction adds a class and removes no line of caller code"
- "that is the price of `__getattr__()`"
  becomes "that is what `__getattr__()` cannot do"

`bruce_edit_db.md`'s R2 already cuts a running tally of costs;
this category handles the single figurative "cost" that R2 leaves.

**Perception standing for verification.**
A type checker does not see, notice, or look through anything.
It verifies, reports, accepts, rejects, infers, narrows.

- "the version a type checker can see through"
  becomes "the version whose calls the checker verifies,
  because `p.f()` reaches a declared method with a declared return type"
- "the checker is blind to the swap"
  becomes "the checker cannot report the swap,
  because both implementations satisfy `Behavior`"
- "`ty` notices the missing method"
  becomes "`ty` reports the missing method"

**Personification standing for a rule.**
Code does not want, know, care, expect, promise, trust, or forget.
The exception is *expect* in its typing sense
("the parameter expects a `str`"), which the checker's own messages use.

- "the proxy knows nothing about the implementation"
  becomes "the proxy names no method of the implementation"
- "the annotation promises a `Console`"
  becomes "the annotation declares a `Console`"
  (the `deep_review_db.md` note on *promise* applies:
  Python readers map it onto `Future`)
- "the registry forgets an unregistered class"
  becomes "the registry never held the class"

**Containers and gaps standing for a limit.**
*A hole in, a gap, closes the gap, escapes the net, slips past, inside the type.*

- "identity has the same gap"
  becomes "identity is the same limit:
  delegation forwards the methods, not the type"
- "a `@runtime_checkable` `Protocol` does not close that gap"
  becomes "a `@runtime_checkable` `Protocol` does not change that"
- "an exception raised where no `@throws` wraps the body slips past the type"
  becomes "an exception raised where no `@throws` wraps the body
  is not in the type"

## Boundaries

- **Terms stay.** The first test above is decisive.
  When in doubt, search the Python documentation for the word;
  if the docs use it for this thing, keep it.
- **A dead metaphor in a heading stays unless the section is being edited
  anyway.** A renamed heading changes its anchor,
  and every cross-reference must follow (`heading_links.py` gates it).
- **Quoted material and GoF's own vocabulary stay.**
  "Smart reference", "virtual proxy", and a quoted sentence
  keep their words.
- **Do not replace an image with an abstraction.**
  "The check lands before the loop" is not fixed by
  "the check occurs prior to the loop";
  it is fixed by naming who runs the check and when.
- **Do not add hedges.** The literal sentence states what happens.
  If the original hedged ("can cost", "tends to bite"),
  decide whether the hedge was real
  (a condition the chapter should name) or decorative (drop it).
- **The Accrued patterns in `activate`'s SKILL.md apply here too**,
  since an activated verb must be literal.
  Never trade a passive for a figure, and never trade a figure for a passive.
- **Check the exemption records first.**
  `deep_review_db.md` in the repo root carries standing exemptions
  and the note on *promise*.

## Verify and report

Touched prose gets `make reflow CH=NN` (Semantic Line Breaks),
then `make verify`, then read `git diff Chapters/`:
a changed `#:` marker means an edit strayed into code, so investigate it.
Report the figures you replaced as before/after pairs,
and separately list any you kept as documented terms
when the call was close, with the documentation that settles it.
Bruce reviews the diff and commits himself.

## Accrued patterns

Figures Bruce has flagged that the categories above do not name yet.
When he identifies a new one,
add it here as a bullet with a before/after pair,
and it becomes part of every future pass.

- "`__getattr__()` trades that for reach" becomes
  "`__getattr__()` gives up that check to forward every method,
  including ones added later" (`d1ec3ac4`).
- "That verification stops at the proxy" becomes
  "Calls on the proxy get no such check" (`458530ea`).
- "the version a type checker can see through" becomes
  "`p.f()` reaches a declared method with a declared return type,
  and the checker verifies it" (`458530ea`).
- "Each has a cost, and each protects against" becomes
  "Each guards against" (`74d84ea3`).
- "The registry also never forgets:" becomes
  "The registry also never removes an entry:" (`40323f50`).
- "hides the problem by throwing the builder away on the same line that
  creates it" becomes "never shows the problem, because it keeps no
  reference to the builder after `build()` returns" (`40323f50`).
- "each implementation picks a side" becomes
  "each implementation chooses one behavior or the other" (`40323f50`).
  These three are R10 in `bruce_edit_db.md`: a judgment or figure about a
  mechanism becomes the mechanism.
