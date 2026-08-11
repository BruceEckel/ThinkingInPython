---
name: activate
description: Rewrite prose into the active, direct register: clear the passive-voice and there-is warnings from `make prose`, and cut metadiscourse, empty frames, and expletive constructions Vale cannot see. Use when asked to activate a chapter (or the whole book). The argument names chapters by number or name; no argument means all of Chapters/.
---

# Activating prose: put the agent in the subject

The book's register is active and direct.
A sentence earns its length by content, not by frame:
no dummy subject holding a place,
no announcement that a point is coming,
no participle hiding who acts.
This skill is the cleanup pass for that register.
It has two sources of findings:
the mechanical warnings `make prose` reports,
and a read-through for the constructions no linter catches.
The pass edits `Chapters/NN_*.md` prose only;
code blocks, `#:` output markers, and quoted material stay untouched.

## Step 1: collect the mechanical findings

Run `make prose CH=NN` (one chapter) or `make prose` (whole book);
it needs the standalone `vale` binary.
Collect the `write-good.Passive` and `write-good.ThereIs` hits.
`make prose` is not part of any gate,
so a clean `make verify` says nothing about these warnings.

## Step 2: read for what Vale misses

Vale flags "to be + participle" and sentence-initial "There is/are".
It does not flag metadiscourse, empty frames,
or an expletive buried mid-sentence.
Read the chapter for the categories below.

## The categories and their rewrites

**Passive voice.**
The test: is there a real agent, present in the discussion,
that the sentence demoted or dropped?
If so, promote it to the subject:

- "a `test_*.py` file is run by `pytest`" becomes "`pytest` runs each `test_*.py` file"
- "The `{}` literal was taken by `dict` first" becomes "`dict` claimed the `{}` literal first"
- "where they are worked in pairs" becomes "where pairs work through them"

When no agent is on stage, swap the verb instead of inventing one:

- "The text is licensed CC BY-NC-ND" becomes "The text carries a CC BY-NC-ND license"
- "The book is organized into five parts" becomes "The book has five parts"
- "At most one target can be starred" becomes "At most one target can carry the star"
- "the new value is stored" becomes "its result goes into the dictionary"

Keep a passive when both moves fail:
when the natural rewrite needs a fabricated subject
("the system", "one", "the programmer")
or when the acted-on thing is the topic
and fronting the agent would derail the paragraph.
A kept passive is a judgment call, not a defeat;
note it in the report so the warning's persistence has a recorded reason.

**Expletive constructions.**
"There is / there are / it is ... that" frames.
The content nouns become the subject:

- "There are three cases that matter" becomes "Three cases matter"
- "It is the factory that builds the default" becomes "The factory builds the default"

**Metadiscourse.**
Writing about the writing or the reader:
"note that", "you can see that", "it is worth mentioning",
"as we saw", "keep in mind that".
Usually pure deletion:
"You can see that the loop never runs" becomes "The loop never runs".
State advice as an imperative and facts as a declarative.
Keep "you can" when the option's existence is the news:
"You can supply a different `Console` in a test"
is about the option, and flattening it changes the meaning.

**Empty frames.**
A clause that delays the point without adding one:
"The thing to understand is that X" becomes "X";
"What this means is that Y" becomes "So Y" or just "Y".
The test is deletion: if the sentence means the same without the frame,
the frame was scaffolding.

## Boundaries

- **Bruce's em-dashes stay.** Rewriting a sentence around one is fine;
  deleting or replacing the dash is not.
- **Check the exemption records first.**
  `readability_db.md` and `deep_review_db.md` in the repo root
  carry standing exemptions: prose that reads as a violation on purpose.
  A construction recorded there is settled; leave it.
- **Headings have their own rule** (see the
  `heading-style-infinitive-over-modal` project memory):
  infinitive or noun phrase, not a modal clause,
  so "A Value You Must Check Everywhere" became "A Value to Check Everywhere".
  A renamed heading changes its pandoc anchor;
  grep all of `Chapters/` for the old slug and update every cross-reference.
  `heading_links.py` (in `make verify`) catches a missed one.
- **Meaning outranks activeness.**
  If the active rewrite says more than the original claimed
  (a hedged "can cause" that really is conditional, for example),
  keep the original.

## Verify and report

Touched prose gets `make reflow CH=NN` (Semantic Line Breaks),
then `make verify`, then read `git diff Chapters/`:
a changed `#:` marker means an edit strayed into code, so investigate it.
Re-run `make prose CH=NN` and confirm the Passive/ThereIs count dropped;
list any warning deliberately kept, with its reason.
Bruce reviews the diff and commits himself.

## Accrued patterns

Phrasings Bruce has flagged as passive-feeling that the categories above
do not name yet. When he identifies a new one,
add it here as a bullet with a before/after pair,
and it becomes part of every future pass.

- (none yet)
