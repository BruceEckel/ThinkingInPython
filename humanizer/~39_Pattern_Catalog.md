[[Reviewed]]
# Humanizer candidates: Chapters/39_Pattern_Catalog.md

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

This chapter is almost entirely a set of reference tables (pattern name,
one-line intent), with a sixteen-line prose introduction. There is very
little surface for AI tells to hide in: no signposting, no rule-of-three
padding, no vague attributions, no boldface lists, no em dashes, no curly
quotes. The one real finding is a single filler "actually" in a table
cell. The chapter is clean.

## Tier A

### A1 — line 100 — filler word ("actually")

Watch-list word from `CLAUDE.md` ("Consider rewriting" tier). Deleting
it changes nothing: the row still says loading is deferred until it's
needed.

CURRENT
```text
| Lazy Load | Defer loading data until it is actually needed. |
```

PROPOSED
```text
| Lazy Load | Defer loading data until it is needed. |
```

## Tier B

No Tier B candidates. Nothing found rose to "arguable but real."

## Housekeeping

1. Line 10 runs 94 characters, over the 80-character reflow width, and
   has no internal comma or clause boundary to break on ("Each entry has
   a one-line intent so you can recognize a pattern by name and find it
   elsewhere."). `make reflow CH=39` would break it at the dependent
   "so" clause; no gate currently catches this.

## Considered and not flagged

- **"Many overlap, some compete, and several exist only to work around
  limits of a particular language"** (line 12-13) looks like a
  rule-of-three at a glance, but each clause states a distinct, specific
  claim rather than interchangeable vague adjectives. Left alone.
- **The nine "Intent" column definitions** all open with a bare
  imperative verb (Create, Convert, Treat, Attach, Provide, Notify,
  Defer, Represent, Cache, ...) with no stated subject. This reads like
  the passive/subjectless-fragment tell (§13) at first glance, but it's
  the deliberate, consistent convention of a glossary or catalog table,
  not narrative prose hiding its actor. Left alone.
- **"itself"** in the CRTP row ("parameterized by the class itself",
  line 164) is reflexive and load-bearing: it distinguishes "the same
  class" from "some class," which is the whole point of the pattern.
  Kept per the `itself` rule in `CLAUDE.md`.
- **Six other instances of "only"** (lines 4, 13, 16, 61, 79, 99) each
  restrict a real technical claim (one instance, one direction, one
  load per session) rather than functioning as an intensifier. None
  read the same with it removed, so none were flagged.
- **Book-title italics** (*Design Patterns*, *Pattern-Oriented Software
  Architecture*, *Patterns of Enterprise Application Architecture*,
  *Enterprise Integration Patterns*) are first-use italics on proper
  titles, the correct use per the chapter's own italics convention. Not
  emphasis-italics.
- **Table structure itself** (headers, pipe syntax) was checked for
  inline-header vertical-list drift (§16) and emoji decoration (§18);
  neither applies, since these are genuine data tables, not bulleted
  lists dressed up with bold labels.

## Scan coverage

No hits on: em dashes (bare or spaced), curly quotes, boldface-header
lists, emoji, signposting/announcements, fragmented headers, staccato
drama, aphorism formulas, conversational openers, sycophantic tone,
knowledge-cutoff disclaimers, hedging, false ranges, negative
parallelisms, copula avoidance, or the §7 AI-vocabulary list beyond the
one "actually" reported above. Person (we/us/our) does not appear
anywhere in the chapter. `[[ ]]` draft notes: none present.
