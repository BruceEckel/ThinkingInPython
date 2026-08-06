# Humanizer candidates: Chapters/30_Observer.md

Run date: 2026-08-05. Source: `humanizer` skill (blader/humanizer, adapted).

All accepted edits were applied on 2026-08-05 and removed from this file.
What remains is the record: what was applied, one housekeeping item that
turned out not to be actionable, and what was never flagged.
This is a changelog now, not a worklist.

## Applied

Every block survived review. Five prose edits:

- A1, the tailing negation fragment at line 161 ("no error anywhere")
  written out as a clause.
- A2, two first-person-plural sites converted to second person
  (lines 216, 307).
- B1, the participle tail at line 196 ("doing the forgetting
  automatically") turned into a relative clause.
- B2, "exactly" at line 274.

The review leaned toward keeping B2, reading it as the precise-logical-match
carve-out. It stayed in the file and was applied; recorded here so a later
pass does not read the lean as the decision.

## Housekeeping: not actionable as written

**Semantic Line Break drift, exercise lines 433 and 439.** The finding said
`make reflow CH=30` fixes both. It does not. `reflow_prose.py` reports zero
paragraphs for this chapter, and breaking the two lines by hand at the points
named produces a diff the tool then reverts: it re-joins them into single
long lines.

The reason is the tool's own rule. Both sentences run long without a
top-level comma, semicolon, or colon, so `_clause_segments()` finds no
boundary and refuses to break mid-clause rather than hard-wrapping to a
column. Under the repo's Semantic Line Break convention these lines are
compliant despite their length, and a manual break puts the file *out* of
compliance. Left as they are.

A later pass should not re-flag these two lines, and should treat "long line
in a list item with no clause marker" as a non-finding generally.

The other two housekeeping notes needed nothing: heading spacing is uniform,
and there are no `[[ ]]` draft notes, no spaced ` -- `, and no em dashes.

## Considered and not flagged

- **"the *Observer* pattern amounts to nothing more than a list of
  callbacks" (line 97).** This is the exact sentence `CLAUDE.md` names
  as the keeper case for "nothing more than": the diminishing is the
  point. Left alone on purpose.
- **"values in, values out" (line 305).** A staccato pair, but it names
  a real property of a pure function (inputs mapped to outputs), the
  same shape as "garbage in, garbage out." Not manufactured drama.
- **"The list of callbacks becomes a line of waits" (line 203).** Reads
  close to an aphorism formula, but the metaphor is concrete and
  accurate (sequential blocking really does queue up waits), not vague
  profundity standing in for a claim.
- **"The `list()` copy inside `notify()` is a single word doing quiet
  work" (line 155) and "Two more realities of Observer deserve a
  sentence each" (line 187).** Both are single instances of a creative,
  slightly personifying turn of phrase. Neither stacks with others, and
  both carry real information about what follows. The skill's own
  guidance says one short emphatic or unusual sentence is not a tell on
  its own.
- **Repeated italics on *Observer*/*observer*/*observable* (lines 3, 5,
  15, 18, 21, 31, 33, 97).** Matches the book's convention of
  italicizing a pattern name on every mention, not just first use,
  which chapter 27's review already established as exempt from the
  strict first-use rule. Lines 31 and 33 re-italicize *observer* and
  *observable* specifically because the paragraph is redefining them in
  Python terms against the classic definition from the opening; that's
  a real second introduction, not emphasis.
- **"never" at lines 10 and 189.** Both state a genuine architectural
  absolute (the observable never needs to know observer types; a
  stopped loop never reaches later observers), not an intensifier.
- **The two-item list at lines 9-10.** Not a rule-of-three; two real,
  distinct properties.
- **"only" (eight sites, e.g. lines 200, 283, 297, 381, 418).** Each is
  a genuine restriction with a real contrast nearby (only prints vs.
  later I/O observers, only the shared contract vs. the rest of each
  file). None read as filler.
- **"itself" (line 157 and the line 174 code comment).** Both reflexive
  and load-bearing: an observer detaching itself is literally the
  subject acting on itself.
- **Chapter-opening roadmap ("This chapter shows the Pythonic version
  first, then extends it... It closes with...", lines 25-27).**
  Describes the chapter's actual structure rather than a conversational
  "let's dive in" announcement. Standard technical-book scaffolding,
  not the §28 tell.
- **§29 fragmented headers.** Checked all four `##` headings
  (`The Pythonic Observer: a List of Callables`, `Observer and I/O`,
  `A Visual Example of Observers`, `Exercises`). None open with a
  sentence that just restates the heading.

## Scan coverage

The word-level half of the skill was entirely clean: no §7
AI-vocabulary hits, no curly quotes, no emoji, no boldface anywhere in
the chapter, no promotional or sycophantic language, no filler phrases,
no hedging stacks, no false ranges, no elegant variation, no copula
avoidance, no predicate hyphenation, no generic upbeat conclusion, and
no em dashes to consider. No stranded prepositions found. Everything
above was structural: one tailing negation, one person slip (two
sites), and two mild Tier B calls.
