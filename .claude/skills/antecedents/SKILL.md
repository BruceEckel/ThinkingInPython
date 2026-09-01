---
name: antecedents
description: Make every pointer word name its target. A sentence-opening "This" or "That", an "it" with two candidates, a clause-level "which", "the former/latter", or "above/below" gets the noun it stands for whenever a reader could pick the wrong one. Use when asked to clarify references or antecedents in a chapter (or the book). The argument names chapters by number or name; no argument means all of Chapters/.
---

# Antecedents: every pointer names its target

A pronoun is a pointer.
It is correct when exactly one thing in the reader's short-term memory
can be its target, and wrong the moment two can.
Strunk's rules have nothing to say about this,
and the sentence that fails is grammatical,
so the style passes leave it alone;
the tell is a sentence that needs a second reading
to find out what "this" was.
This pass hunts pointers with more than one possible target
and replaces each with the noun.
It never replaces a pointer that has one clear target,
because a paragraph that repeats its nouns in every sentence
reads as if written for a machine.
It edits `Chapters/NN_*.md` prose only;
code blocks, `#:` output markers, and quoted material stay untouched.

## The test

Cover the sentence before the pointer with your hand.
Now read the pointer's sentence.
Can you say, from the pointer's own sentence plus the paragraph's topic,
what it names?
If yes, the pointer is fine.
If you need to uncover the previous sentence,
uncover it and count the candidates:
one candidate, fine;
two or more, name the one meant.

A second test for "it" and "they":
does the pointer's grammatical role match its target's?
"`tkinter` plays no part here. It reuses the same `Observable`"
puts `tkinter` in subject position and then says "It" reuses,
so the grammar hands "It" to `tkinter` even though the model is meant.
The fix names the model.

## Where pointers go wrong

**Sentence-opening "This" and "That" with no noun.**
The commonest case.
"This" at the head of a sentence can name the previous sentence's subject,
its object, its whole claim, or the listing above it.
Add the noun, or restate the claim as the subject:

- "The registry holds one entry per class. This allows lookup by name."
  becomes "... The registry allows lookup by name."
- "Only the metaclass version skips `__init__()`. This is why the first
  call's arguments win."
  becomes "... Skipping `__init__()` is why the first call's arguments win."
- "The type checker accepts the code. This is the problem."
  becomes "... That acceptance is the problem."

Keep "this" when it carries its noun ("this proxy", "this listing")
or when the whole preceding sentence is unmistakably the referent
and no noun phrase inside it competes.

**"It" with two candidates.**
Two singular nouns in the previous sentence make "it" a coin toss:

- "The proxy stores the level on itself, where the next lookup finds it.
  It never consults the implementation again."
  becomes "... The proxy never consults the implementation again."
- "Whoever holds `checkpoint` can restore the drawing.
  It does not reach inside and edit the strokes."
  becomes "... The holder does not reach inside and edit the strokes."

**Clause-level "which".**
A "which" that points at the whole preceding clause rather than a noun
is legal and often clear,
but it is ambiguous whenever a noun sits just before the comma:

- "the distinction depends on the types `int` and `str`, which is fragile"
  (is `str` fragile, or the distinction?)
  becomes "the distinction depends on the types `int` and `str`,
  and that dependence is fragile"
- "the getter returns the same list, which is the leak"
  becomes "the getter returns the same list, and that sharing is the leak"

**"The former", "the latter", "the first", "the second", "the other".**
These make the reader re-read the list to count.
Name the items:

- "`ABC` and `Protocol` both express the interface; the latter needs no base class"
  becomes "... a `Protocol` needs no base class"
- "One forwards reads, the other forwards writes"
  is fine as a contrast on its own line,
  but "the other" three sentences later is not; name it.

**"Above", "below", "here", "earlier", "the previous section".**
Position words point at the page, and the page changes:
a moved listing or a split section leaves them pointing at nothing,
and no gate catches the drift (see `CLAUDE.md` on splitting a chapter).
Name the listing or link the section:

- "the single generic surrogate above"
  becomes "the single generic surrogate in `state_surrogate.py`"
- "as the previous section showed"
  becomes "as [What the Implementation Supplies](#what-the-implementation-supplies)
  showed" (a named link fails loudly at `heading_links.py` instead of
  quietly misleading)

Keep "above" and "below" when the referent is the adjacent listing
and the sentence introduces or follows it directly
("the listing below", "the output above");
those cannot drift because they move with the listing.

**Subject drift across sentences.**
The pointer is fine but the paragraph switched subjects
without saying so, so "it" inherits the wrong one.
This is the boundary with the `cohesion` pass:
if naming the noun fixes the sentence, do it here;
if the paragraph needs its sentences reordered, leave it for `cohesion`.

## Boundaries

- **One clear target means no change.**
  The goal is zero ambiguous pointers, not zero pronouns.
  If you find yourself replacing every "it" in a paragraph,
  stop and reread with the cover test.
- **Do not introduce a new noun.**
  The replacement is a noun already in the passage,
  not a summary the chapter never used
  ("the mechanism", "this approach", "the process").
  If no existing noun fits, the sentence has a different problem;
  note it in the report.
- **A repeated noun beats a clever pronoun.**
  "The proxy ... the proxy ... the proxy" in three consecutive sentences
  is acceptable when the proxy is the topic;
  cohesion (the running topic in subject position) is what makes
  repetition read as natural rather than mechanical.
- **Quoted material stays.**
- **Headings stay** unless the section is already being edited;
  a renamed heading changes its anchor.
- **Check the exemption records first.**
  `deep_review_db.md` in the repo root carries standing exemptions.

## Verify and report

Touched prose gets `make reflow CH=NN` (Semantic Line Breaks),
then `make verify`, then read `git diff Chapters/`:
a changed `#:` marker means an edit strayed into code, so investigate it.
Report each change as the pointer, its candidates, and the noun chosen.
List any pointer you judged ambiguous but left,
with the reason (usually that no existing noun fits).
Bruce reviews the diff and commits himself.

## Accrued patterns

Pointer shapes Bruce has flagged that the categories above do not name yet.
When he identifies a new one,
add it here as a bullet with a before/after pair,
and it becomes part of every future pass.

- **"The two", "the other two", "both", "neither" with the items unnamed.**
  "without providing the rest ... the other two parts are liabilities"
  when the three parts were listed a page earlier;
  "`research()` splits the two" with no pair in sight;
  "`@final` on the two classes" when the classes were named in another
  chapter.
  Name the items where the count appears.
- **A pointer at a listing or example by position.**
  "This codec has a bug:" (the one below), "the last example",
  "the single generic surrogate above".
  Adjacent-listing pointers ("the listing below") are fine;
  anything further names the file: "`property_check.py`'s five-letter
  alphabet", "The next codec has a bug:".
- **A noun that assumes an introduction the text never made.**
  "the simulation" before any listing was called a simulation;
  "this opacity" when the earlier sentence said "restraint";
  "the naive loop" for a loop never called naive.
  Use the noun the text did introduce, or introduce this one first.
- **An "it" whose grammatical subject is the wrong noun.**
  "`tkinter` plays no part here. It reuses the same `Observable`" hands
  "It" to `tkinter` by grammar even though the model is meant;
  "`Outlet` ... and it carries the hour" when the request carries it.
  Name the intended noun.
