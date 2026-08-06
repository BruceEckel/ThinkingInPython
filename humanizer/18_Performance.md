[[Reviewed]]
# Humanizer candidates: Chapters/18_Performance.md

Run date: 2026-08-05. Source: `humanizer` skill (blader/humanizer, adapted).

## How to use this

Each edit is a `###` block with a CURRENT and a PROPOSED fence.
Delete any block you don't want, save the file, and hand it back to me.
I apply what survives, verbatim, and run `make verify`.

The CURRENT fences are exact copies from the chapter,
so don't hand-edit inside them or the match will fail.
If you want a different wording, edit the PROPOSED fence instead
and I will use yours.

Tier A is what I'd apply. Tier B is genuinely arguable, delete freely.
Housekeeping is not humanizer output; separate list at the end.

## Verdict

Mostly clean. No AI vocabulary, no curly quotes, no em-dash issues,
no boldface-header lists, no signposting, no chatbot artifacts, no
`[[ ]]` notes. The chapter's real findings were small and specific: one
direct hit on the promotional-language watch list ("boasts a"), one
banned word ("wants"), one leftover "we" in an otherwise second-person
chapter, an "is what" cleft, and two italics used for emphasis instead
of term introduction. The single biggest finding was "boasts a" at
line 35, a verbatim match against §4/§8's watch list, the kind of hit
chapters 46 and 47 didn't have at all.

A1-A5 have been applied. B1 (the seven-sentence AI/Rust paragraph
rewrite) has been applied in place of A6, which it supersedes. B2
(line 148, the garbled `ValueError` sentence Bruce flagged) has now
been rewritten and applied:
"and trying to claim one that another tool already holds raises a
`ValueError`, which is how two profilers avoid quietly fighting over
the same hooks."

## Housekeeping

None found. No double blank lines before headings, no `[[ ]]` draft
notes elsewhere, no spaced ` -- `, and no em dashes anywhere in the chapter. The
long lines a raw column-width scan flags (e.g. line 39, line 99) are
each a single clause with no internal comma or colon to break at, so
they're already compliant with Semantic Line Breaks rather than drift.

## Considered and not flagged

- **Italics used correctly.** *premature optimization* (13), *profiler*
  (44), *sampling* (62), and *heap* (419) each introduce a term on its
  first formal use in prose, immediately after the heading names the
  topic. This is a repeated, deliberate convention, not a tell.
- **Fragmented headers (§29).** Checked every heading in the chapter.
  Several opening sentences echo the heading's own word ("Profilers" /
  "A *profiler* looks for...", "Heap" / "a *heap* keeps...", "Choose
  Better Algorithms" / "a better algorithm") but each is a real,
  substantive definition or claim, not the vacuous "Speed matters."
  restatement the pattern describes. None qualify.
- **"Numba shines" (line 927).** Adjacent in spirit to promotional
  language but not a verbatim hit on the §4 list, and "shines at X" is
  ordinary idiomatic usage for describing a tool's strength. Left alone.
- **"Hook"/"hooks" (lines 93, 150).** Literal PEP 669 vocabulary (the
  interpreter's actual "hook mechanism"), not the metaphorical "hooks"
  CLAUDE.md's banned list targets. Left alone.
- **Rule-of-three groupings.** Three membership-testing methods in
  "Comparison," three memory tools under "Reduce Memory Overhead,"
  three deferred NumPy/Numba/Rust examples. Each is a real, distinct
  count from the material, not an invented triad. Left alone.
- **Repeated parenthetical refrain** ("Expect a different, but still
  large, multiple on yours," lines 888, 936, 996). Verbatim three
  times, but across three structurally parallel deferred-example
  asides; consistent framing, not filler repetition. Left alone.
- **"The goal is not the fastest possible program. It is a program that
  is fast enough..." (lines 1172-1173).** Reads close to the §9
  negative-parallelism formula but makes one specific, real claim
  rather than a formulaic double negation. Left alone.
- **"Only," "already," "even," "plain."** All appear (e.g. "only
  O(log n)," "the plain Python loop"), each doing real, precise work
  contrasting one approach against another. None are flourish uses.

## Scan coverage

No hits anywhere in the chapter for: §7 AI vocabulary (crucial, delve,
tapestry, testament, underscore, etc.), §15 boldface overuse, §16
inline-header vertical lists, §18 emoji, §19 curly quotes, §20-22
chatbot-communication artifacts/disclaimers/sycophancy, §23-24 filler
phrases and hedging, §26 hyphenated-pair overuse, §27 persuasive-
authority tropes ("at its core," "the real question"), §28 signposting
("let's," "here's what"), §32 aphorism formulas, §33 rhetorical
openers ("honestly," "look,"), the "nothing else" family (already swept
book-wide), stranded prepositions, and `raise`/`raises` without an
object (the one instance in the chapter already has one). Person
consistency was checked in full: the single "we" at line 46 is the
only first-person-plural slip in the chapter.
