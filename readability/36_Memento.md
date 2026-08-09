> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/36_Memento.md` (r2)

The chapter's older prose still holds up: a full vocabulary scan turns up no
Tier 1A or Tier 2 hits, no boldface, no curly quotes, and no spaced ` -- `.
All five findings from the first review are applied and none was rejected.

Everything below is in prose added since that review, either by the deep review
while it was being written or by today's apply. The first item is a sentence
today's apply broke and needs fixing whatever else you decide.

***

**Section:** The Classic Memento, paragraph beginning "The caretaker's side of
the contract is restraint"
**Pattern:** Clarity, broken subordination (no §; skill step 5) (P1)

Current:
> In Python it is a convention,
> though freezing the memento means an honest mistake,
> swapping the snapshot's strokes for different ones, fails loudly.

Proposed:
> In Python it is a convention,
> though freezing the memento means an honest mistake
> (swapping the snapshot's strokes for different ones)
> fails loudly.

Why: today's apply replaced a parenthetical with a comma-delimited appositive
and broke the sentence. The verb "means" takes the whole clause "an honest
mistake ... fails loudly" as its object, and the reader needs to see "an honest
mistake" and "fails loudly" as one subject and verb. Commas around the gloss
make "means an honest mistake" read as complete, so "fails loudly" then arrives
with no subject and the sentence has to be re-read.

The parentheses were doing structural work, not decoration. The deep review's
finding was about *which* mistake the sentence names, and that correction is
right and should stay; only the punctuation needs restoring.

[] Reject

***

**Section:** Mementos That Outlive the Process, last paragraph
**Pattern:** Clarity, number agreement (no §) (P2)

Current:
> When either limitation rules out `pickle`, other libraries answer them separately.

Proposed:
> When either limitation rules out `pickle`, other libraries answer the two separately.

Why: "either limitation" is singular and "them" is plural, so the pronoun has no
antecedent it agrees with. The sentence means the two limitations named above
(drift and security), and "the two" says that without the mismatch.

Alternative if you would rather not carry a bare "the two": name them, "other
libraries answer drift and security separately," which is also a better handoff
into the three sentences that follow, since those pair each library with one of
the two.

This sentence is new with today's apply, replacing a vaguer one.

[] Reject

***

**Section:** Immutability, paragraph after `frozen_sketch.py`
**Pattern:** §35 Moral-Adjective Category Errors, plus a semicolon carrying two
unrelated clauses (P2)

Current:
> `Drawing` is the same idea as `Sketch` with the mutation removed,
> under a different name so the two never get confused;
> its extra `title` field is there so a later section can restore one field and keep the other.

Proposed:
> `Drawing` is the same idea as `Sketch` with the mutation removed,
> under a different name so a reader never has to ask which one a listing means.
> Its extra `title` field is there so a later section can restore one field and keep the other.

Why: classes do not get confused, readers do, so the current phrasing puts the
confusion in the wrong place. The semicolon is the second problem: it joins the
naming rationale to the field rationale, which are two separate answers to two
separate questions a reader has about this listing. They read better as two
sentences.

New with today's apply, written to explain the rename.

[] Reject

***

**Section:** Immutability, the new closing paragraph
**Pattern:** Comma splice (global rules: break up comma-spliced sentences) (P2)

Current:
> The classic form has not disappeared, it has narrowed.

Proposed:
> The classic form has not disappeared. It has narrowed.

Why: two independent clauses joined by a comma. The global rules call for
breaking these up, and the period is stronger here anyway: the paragraph's whole
job is the second clause, so giving it its own sentence lets it land before the
two conditions that follow.

New with today's apply, from the deep review's block about the intro promising
the classic form "when you need it."

[] Reject

***

**Section:** Mementos That Outlive the Process, paragraph after `ghost_field.py`
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> The three prints are the lesson side by side.
> The `repr()` shows a one-field object while the `__dict__` shows two entries,
> and the loaded object is `==` to a `SketchV1` that never had a title,
> so nothing downstream can tell them apart.

Proposed:
> The `repr()` shows a one-field object while the `__dict__` shows two entries,
> and the loaded object is `==` to a `SketchV1` that never had a title,
> so nothing downstream can tell them apart.

Why: the opening sentence rates the listing rather than reading it, and the
sentence after it does the actual work. It also miscounts now: the listing was
split into three prints to fit the line-length limit, so "side by side" no
longer describes the layout it was written for.

Lowest-confidence item here. If you want a lead-in before the three claims, the
version that carries information is "Each print contradicts the one before it,"
which is true and sets up the sequence.

[] Reject
