> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/40_Functional_Foundations.md`

Second review of this chapter.
All three findings in `readability/~40_Functional_Foundations.md` were accepted
and applied, and none were rejected, so nothing is carried forward.

The deep review that ran just before this one added a lot of new prose: a
rewritten Part IV/V preview in the intro, a follow-up under `why_pure.py`, a
`match`-versus-table paragraph, follow-ups under `closures.py` and
`composing.py`, and a whole new closing section. Every finding was in that
new prose. The chapter's older prose is unchanged since the last review and
still reads clean.

Two problems in the new prose were corrected during the apply rather than
recorded here, because they were errors rather than style calls:
"Every idea in the chapter is present and doing work" was false (`pipeline.py`
uses no closure, lambda, `Placeholder`, or `compose()`), and is now
"Five of the chapter's ideas are doing work at once"; and
"`slope()` returns here as well" read as a function return rather than a
reappearance, and is now "`slope()` appears again later in the book".

Every remaining finding cleared the direct-application bar, so this run leaves
no blocks: the fixes are listed for the record, and the `git diff` is the
place to veto any of them.

## Applied directly

- Closing line of "Putting the Pieces Together": "that single property is
  what the chapters ahead keep spending" → "build on" (you do not spend a
  property; "build on" echoes "Purity is the foundation on which everything
  else in these chapters builds" from the Pure Functions section, so the
  closing line becomes a callback to the chapter's own thesis instead of a
  new figure).
- Lead-in to the same section: "They were built to combine:" → "Here they
  work together:" (the passive left it unclear who built them, and read
  literally the claim was about Python's designers rather than the chapter).
- Intro, Part V preview: split into three sentences, with the tail now
  "[Stateless] and [Stateless in Practice] then build a checked Effect
  system on that mechanism." (the old single sentence ran two `and`s and two
  links in a row, and "on top of it" had two candidate referents; "that
  mechanism" removes the ambiguity).

## Considered and declined

**"Functions as First-Class Objects," the closing rule of the `match`
paragraph:** "Choose `match` when the set of cases is fixed and known to the
compiler, and a table when the set is meant to grow from outside." The two
sentences above it draw the same distinction concretely, so this is §70 by
shape. Left alone: the abstraction is short, it is the sentence a reader will
come back for, and the sentences above it are examples rather than a statement
of the rule. Recorded so the next review does not raise it again.

## Checked and clean

- Zero hits across the §7 Tier 1A, 1B, 2, and 3 vocabulary tables in the new
  prose.
- `banned_phrases.py` and `prose_lint.py` both pass on the chapter.
- No em dashes, no spaced ` -- `, no curly quotes, no boldface, no emojis, no
  slot-fill placeholders.
- "A `match` is code: ... The table is data: ..." is a §69 colon reveal by
  shape, twice. Both colons introduce a definition rather than staging a
  surprise, and the parallel structure is the point of the contrast. Not
  flagged.
- "If you delete either `total = 0`, the second assertion fails" was written as
  a condition rather than the banned imperative-plus-consequence form
  ("Delete either `total = 0` and the second assertion fails"), which is what
  the deep-review block proposed. Already handled during the apply; noted here
  so it is not re-raised.
- The new exercises 6 and 7 use the imperative correctly: they are instructions
  to the reader, which the global rules exempt.
