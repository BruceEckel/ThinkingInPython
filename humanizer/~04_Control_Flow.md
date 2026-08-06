[[Reviewed]]
# Humanizer candidates: Chapters/04_Control_Flow.md

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

The chapter is clean. No em dashes anywhere (nothing to preserve, nothing
to flag), no curly quotes, no `we`/`us`/`our`, no AI-vocabulary hits, no
`[[ ]]` draft notes, no double blank lines, and every italicized word is a
genuine first-use term introduction. Tier A is empty. The one thing worth
your attention is a single unnecessary intensifier at line 360 ("simply
reading"); everything else considered below is a deliberate near-miss that
I judged to be real, legitimate technical prose rather than an AI tell.
This is a short reference chapter with almost nothing to fix.

The one Tier B edit has been applied.

## Housekeeping

1. **Clean structurally.** No double blank lines anywhere, no `[[ ]]`
   draft notes, no spaced ` -- `, and no em dashes at all in the chapter.
2. **No Semantic Line Break drift found.** Every prose line breaks at a
   sentence or clause boundary; the two-line break in the Comprehensions
   section (line 386/387, splitting a link from its verb) matches the
   book's existing convention for long link targets, not drift.
3. **No listing-comment findings.** Every `#` comment inside a fenced
   block (`# Skip the rest of this iteration`, `# Automatic f.close()`,
   etc.) is plain and carries no watch-list word or editorial "we."

## Considered and not flagged

- **Line 196**, "It is reminiscent of a C `switch`, but is much more
  powerful." Reads like §1 undue emphasis, but it is a concrete technical
  comparison the following code block immediately backs up, not puffery
  about significance or legacy.
- **Lines 68-70**, "`pass` marks an indented block with nothing in it yet.
  `...` marks a one-line stub..." A short sentence followed by a longer
  one describing the sibling construct. Considered as a possible §31
  staccato pair; it isn't one, since the two sentences carry distinct
  facts and differ in length, which the skill lists as a human signal
  rather than a tell.
- **Lines 134-135**, "The `else` belongs to the `for`, not the `if`. A
  `while` loop can use `else` the same way." Two short sentences, each
  a separate, necessary clarification. Left alone for the same reason.
- **Line 191**, "This is especially handy in `while` conditions and
  comprehensions." Casual but not a watch-list word or filler
  construction; reads as ordinary human phrasing.
- **Line 138-139**, "Use `range()` for counting, `enumerate()` when you
  also need the index, and `zip()` to combine corresponding items from
  several sequences." A rule-of-three shape, but a real enumeration of
  three distinct built-ins the chapter goes on to demonstrate in order,
  not a manufactured triad.
- **Line 328**, "Python's culture leans on 'easier to ask forgiveness
  than permission.'" Reads near §5 vague attribution ("Python's
  culture"), but this is a widely known, real idiom (EAFP) rather than an
  invented authority, and the sentence names the idiom instead of hiding
  behind it.
- **Line 329**, "Try the operation and handle the exception, rather than
  checking every precondition first." A two-imperative sentence; `CLAUDE.md`
  names this exact construction as an allowed exception to the
  imperative-plus-consequence rule.
- **Italics**, five uses: *conditional expression* (22), *Ellipsis* (55),
  *walrus operator* (172), *raising* (223), *comprehension* (365). Every
  one introduces its term on first use in prose; none is emphasis.
- **Line 223**, "Python signals an error by *raising* an exception." Has
  its object ("an exception"), so it satisfies the raise-needs-an-object
  rule rather than violating it.

## Scan coverage

The word-level half of the skill found nothing at all: no §7 AI
vocabulary, no curly quotes, no emoji, no boldface-header lists, no
promotional or notability language, no vague attributions beyond the one
considered above, no copula avoidance, no negative parallelism, no rule-
of-three padding beyond the one considered above, no false ranges, no
collaborative-chat artifacts, no knowledge-cutoff disclaimers, no
sycophancy, no filler phrases beyond B1, no hedging stacks, no generic
upbeat conclusion, no hyphenated-pair overuse, and no diff-anchored
writing. Person consistency is clean (zero `we`/`us`/`our`). Fragmented
headers were checked at all five section headings; every one is followed
by substantive first content, not a restated heading.
