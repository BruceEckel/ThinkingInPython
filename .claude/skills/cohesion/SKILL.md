---
name: cohesion
description: Make each paragraph read as one line of thought: old information before new, one running topic in subject position, the news at the end of the sentence where the next sentence picks it up, and every connective stating a real relation. Use when asked to improve the flow, cohesion, or coherence of a chapter (or the book). The argument names chapters by number or name; no argument means all of Chapters/.
---

# Cohesion: old before new, one topic string per paragraph

A paragraph can pass every sentence-level test
(active, literal, concrete, no needless words)
and still be hard to follow,
because each sentence starts somewhere the previous one did not leave the reader.
Williams (*Style*, the lessons on cohesion and coherence)
and Gopen and Swan ("The Science of Scientific Writing")
describe the same two reader expectations.
The **topic position**, the start of the sentence,
should hold something the reader already has:
the running topic of the paragraph, or what the previous sentence just introduced.
The **stress position**, the end of the sentence,
should hold the news: the thing the reader will carry into the next sentence.
A paragraph whose sentences honor both reads as one line of thought.
One that reverses them reads as a list of true statements.

This pass works one paragraph at a time and moves information within
and between sentences.
It does not cut, does not add claims,
and does not reorder anything across a listing.
The `activate` pass already fixes each sentence's subject;
this one checks whether the subjects, read down the page, tell a story.
It edits `Chapters/NN_*.md` prose only;
code blocks, `#:` output markers, and quoted material stay untouched.

## The test: read the subjects down the page

For each paragraph, write its sentences' grammatical subjects in a column.
That column is the paragraph's topic string.

- If the column repeats one or two nouns (the proxy, the checker),
  the paragraph has a topic and the reader can follow it.
- If it wanders (the proxy, `object`, the lookup, `type(p)`, a dunder,
  `print()`), the reader restarts orientation at every sentence.
  Re-front the running topic where the meaning allows,
  even at the cost of a passive:
  `activate`'s own boundary says cohesion outranks activation.
- If the column changes topic once, in the middle,
  the paragraph is two paragraphs, or the second half belongs elsewhere.

Then, for each sentence, check its ends.
Does it begin with something the previous sentence gave the reader?
Does it end on the thing the next sentence picks up?

## Where flow breaks

**New before old.**
The sentence opens on its news and ends on its link to the previous sentence.
Swap the halves:

- "A `Protocol` needs no common base and reports the mismatch where code
  uses an object as a `Service`."
  after a sentence about the ABC's inheritance requirement
  becomes "A `Protocol` instead reports the mismatch where code uses an
  object as a `Service`, and needs no common base."
  (the contrast with the ABC is the old information; "no common base" is
  the news that the next sentence, on `isinstance()`, does not need, so
  it can close the sentence)
- "`len(p)` reports the miss because `object` defines no `__len__()`.
  `object` defines `__str__()`, so `print(p)` cannot."
  is already old-before-new: the second sentence opens on `object`,
  which the first just introduced, and ends on the news.

**A stolen stress position.**
The sentence ends on a qualifier, a citation, or a function word,
and the point sits mid-sentence where nothing marks it:

- "`p.f()` reaches a declared method with a declared return type, with
  explicit forwarding, as in `proxy_1.py`."
  becomes "With explicit forwarding, as in `proxy_1.py`, `p.f()` reaches
  a declared method with a declared return type, and the checker
  verifies it."
- "The two disagree, so the proxy stops consulting the implementation,
  as the output shows."
  becomes "The proxy stops consulting the implementation, and the two
  disagree."
  (the output reference adds nothing the marker does not; the
  disagreement is the news)

A trailing "which ..." clause is the usual thief;
either front it or make it its own sentence.

**A wandering topic string.**
Each sentence is fine and the paragraph is not:

- "The assignment stores `level` on the proxy. The next lookup finds it
  there. The implementation is never consulted again. The type checker
  objects to the assignment."
  (subjects: the assignment, the lookup, the implementation, the checker)
  becomes "The assignment stores `level` on the proxy, where the next
  lookup finds it, so the proxy stops consulting the implementation and
  the two disagree. The type checker objects to the assignment, ..."
  (subjects: the assignment, the proxy, the checker: the proxy is the
  topic, and the checker sentence opens the next point)

**A connective that names no relation.**
"Also", "additionally", "in addition", and a bare "and" between
sentences say only that another sentence follows.
Either state the relation ("so", "because", "but", "which means")
or, if there is none, the sentence is a list item and the paragraph
is a list.

- "The double underscore mangles the name. `__getattr__()` also runs
  only on failed lookups."
  has no relation to state; the two facts belong to different paragraphs,
  and the fix is to move the second.
- "A `Protocol` reports the mismatch at the use site. Also, it needs
  no base class."
  becomes "A `Protocol` reports the mismatch at the use site,
  and needs no base class."

**A claim and its reason kept apart.**
The sentence-level version of the deep-review lens
"where the question arises, where it is answered":
a sentence makes a claim the reader will want explained,
and the explanation arrives two sentences later
with an unrelated sentence between.
Move the reason next to the claim.
If the intervening sentence is the paragraph's real topic,
the claim and its reason move together, to after it.

**A paragraph carrying two topics.**
The topic string changes once and stays changed.
Split at the change.
If the second half is one sentence, it usually belongs
at the head of the next paragraph, whose topic it shares.

## Boundaries

- **Never move a sentence across a listing.**
  Prose before a listing sets it up; prose after reads its output.
  A sentence that seems to belong on the other side of a listing
  is a finding for a deep review, not a cohesion edit.
- **Never change a technical claim.**
  Reordering can silently change scope
  ("only" and "not" attach to whatever ends up next to them),
  so reread every moved sentence for what it now says.
- **Do not add transitions that only announce.**
  "Next,", "Now,", "Turning to", "As mentioned" are metadiscourse
  (`activate` removes them);
  a real transition states a relation between two facts.
- **Bruce's fragments and signposts stay.**
  "Two cautions." and "Brackets when you want a list." are deliberate
  paragraph openers; give them their paragraph, do not absorb them.
- **Semantic Line Breaks.**
  A rewritten sentence goes on its own line,
  breaking at top-level commas when it is long;
  `make reflow CH=NN` settles the rest.
- **Headings stay** unless the section is already being edited;
  a renamed heading changes its anchor.
- **Check the exemption records first.**
  `deep_review_db.md` in the repo root carries standing exemptions,
  and its notes on deliberately placed sections (chapter 34's
  three-walker paragraph, chapter 1's disclosure) are the section-level
  form of the same judgment: some placements that look wrong are chosen.

## Verify and report

Touched prose gets `make reflow CH=NN` (Semantic Line Breaks),
then `make verify`, then read `git diff Chapters/`:
a changed `#:` marker means an edit strayed into code, so investigate it.
Report each changed paragraph as its topic string before and after
(the column of subjects), which is the evidence that the edit helped.
List any paragraph whose string wanders but which you left alone,
with the reason (usually that the wander is a deliberate list,
or that fixing it needs a move across a listing).
Bruce reviews the diff and commits himself.

## Accrued patterns

Flow problems Bruce has flagged that the categories above do not name yet.
When he identifies a new one,
add it here as a bullet with a before/after pair,
and it becomes part of every future pass.
