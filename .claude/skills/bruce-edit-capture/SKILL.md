---
name: bruce-edit-capture
description: Mine Bruce's own prose edits to a chapter for generalizable editing practices, and log them as candidates or promoted rules in `bruce_edit_db.md`. Proposes; never edits a chapter. Use after Bruce has edited a chapter and wants the lesson captured. The argument names the chapter by number or name, or gives a commit or range; no argument means the working tree.
---

# Capturing editing practice from Bruce's edits

Bruce edits a chapter.
The diff is the best available evidence about how he wants the book written:
this sentence, in this context, became that one.
This pass reads that diff, separates the edits carrying a general practice
from the ones that were local to their paragraph,
and writes the general ones into `bruce_edit_db.md` for
`/bruce-edit-apply` to use later.

**This pass proposes. It never edits `Chapters/`.**
The only file it writes is `bruce_edit_db.md`, and only after Bruce approves
the entries. Applying anything to prose belongs to the other skill.

The central risk is over-generalizing.
One edit underdetermines its rule:
"the class itself defines" becoming "the class defines" could mean
never write "itself", or cut "itself" after a noun phrase where it adds
nothing, or something about that sentence against its neighbors.
The broad version sounds like insight and reads well in a rule file,
then fires on 300 sentences across the book.
Every step below exists to hold the generality down to what the evidence
supports.

## Step 1: establish the diff, and whose it is

The argument decides the range:

- A chapter number or name: find Bruce's most recent edits to that chapter.
- A commit or range (`HEAD~3..HEAD`, a SHA): use it directly.
- No argument: the uncommitted working tree.

Provenance matters and git records it.
Commits I author carry a `Co-Authored-By: Claude` trailer,
so a commit on `Chapters/` without that trailer is Bruce's own work:

```
git log --format='%H%x09%s%x09%(trailers:key=Co-Authored-By,valueonly)' -- Chapters/NN_*.md
```

Two provenances, two weights.
Where Bruce rewrote prose I had written, the edit says directly how I should
write, and it is the strong signal.
Where Bruce rewrote his own older draft, the edit may be the chapter maturing
rather than a standing preference, so it is weaker.
Weak-provenance findings can still become candidates; they should rarely be
proposed as immediate promotions.
Record the provenance in every sighting.

## Step 2: get a diff that survives Semantic Line Breaks

`Chapters/*.md` uses Semantic Line Breaks, and `make reflow` re-wraps
paragraphs, so a line-level diff shows changed lines whose words are
identical. Reading one of those as an edit manufactures rules from
whitespace. Use a word diff:

```
git diff --word-diff=porcelain --ignore-all-space -- Chapters/NN_*.md
```

Then drop everything that is not prose:

- Any change inside a fenced code block is a code edit, not a prose edit.
- A changed `#:` output marker is a code result, and often the gate's own
  self-healing rather than an edit at all.
- `Examples/`, `SolutionsCode/`, `build/`, and lock files are derived or
  irrelevant; a change there follows from a code edit.

Count the surviving prose changes before classifying them.
That count is the denominator in the report at Step 6.

## Step 3: classify every prose change

Most prose edits carry no general rule, and treating them as though they do
is the second way this pass goes wrong. Sort each change into one of three
piles.

**Local.** Skip these and do not mine them:

- A fact corrected, a number fixed, a name changed.
- A transition added because that paragraph needed one.
- A word swapped because it repeated a few lines up.
- Terminology specific to the chapter's subject.
- A cut because the section ran long.
- Prose following a listing that changed.

**Generalizable.** The edit would read as an improvement in another chapter,
on another subject. This is the test: transplant the before-text into a
different chapter and ask whether the same fix still applies. If it depends
on the surrounding paragraph, it was local.

**Contradicts a standing decision.** Before proposing anything, check it
against the records that already settled these questions:
the global `~/.claude/CLAUDE.md` watch list and its dedicated bullets,
the `activate` skill's "Accrued patterns",
and the standing keeps and rejections in `readability_db.md` and
`deep_review_db.md`.
An edit that runs against one of those is worth raising by name, since it
means a settled decision moved. Do not file it silently as a new rule; the
older record would then contradict the new one with nothing to flag it.

Note the direction of each generalizable edit.
Subtractive edits (a word or clause cut) dominate any diff.
Additive edits (a clarification, a mechanism spelled out, a sentence Bruce
added) are rarer and worth more, because a rule set made only of cuts
produces compliant, characterless prose. Mark additive candidates so a sweep
can weight them.

## Step 4: state each rule as narrowly as the evidence allows

Write the narrow version. When torn between a narrow rule and a broad one,
the narrow one is correct, because a second sighting will widen it later and
nothing widens a rule that was too broad from the start except a bad sweep.

Each proposed entry carries, in the `bruce_edit_db.md` format:

- the rule, stated as a short imperative;
- a **test** for deciding whether it fires at a given site, phrased so it can
  be answered by looking at one sentence;
- a **keep when** exception if the evidence shows one, or an honest
  "none seen yet";
- the verbatim before and after, with chapter and provenance.

A rule with no usable test is not applicable and stays a candidate however
convincing it sounds. "Cut 'itself'" is not a test. "Cut 'itself' where the
sentence means the same with it deleted" is.

## Step 5: cross-check against the store

Read `bruce_edit_db.md` first and route each proposal:

- **Matches a Retired entry:** drop it. Do not re-propose a rejected rule in
  new wording. This check is the reason Retired records reasons.
- **Matches an existing Rule:** log a confirming sighting on that rule. No
  new entry.
- **Matches an existing Candidate, from a different chapter:** this is the
  second sighting. Propose promotion to a Rule, and reconcile the two
  sightings' wording, which usually means widening the candidate slightly to
  cover both.
- **Matches a Candidate from the same chapter:** not independent. Add the
  sighting, leave it a candidate.
- **New:** propose as a Candidate.

For each proposed promotion, also propose a `Home`: the global CLAUDE.md
watch list for a vocabulary rule, `activate`'s accrued patterns for a
register rule, `deep-review` for a structural or teaching rule, or this file
alone when the rule is too specific for a general guide.

## Step 6: report, then write only what Bruce approves

Cap a round at **eight** proposals. Finding forty means the classifier is
mining noise, not that the chapter taught forty lessons. Present the
strongest eight and say how many were set aside; never truncate silently.

Report in this order:

1. The counts: prose changes examined, classified local, generalizable,
   contradicting a standing decision. A round where nearly everything became
   a rule is a broken round, and the ratio is how Bruce sees that.
2. Confirming sightings on existing rules.
3. Proposed promotions (candidate plus second sighting), with both pairs.
4. New candidates, with their pairs.
5. Anything contradicting a standing decision, by name, with the record it
   contradicts.

Bruce approves, narrows, or rejects each item.
Write `bruce_edit_db.md` only after that.
A rejected proposal goes to Retired with his reason in his terms.
A narrowed one is written as narrowed, not as proposed.

Nothing else is written. `Chapters/` stays untouched, no `make` target runs,
and Bruce commits the store himself.
