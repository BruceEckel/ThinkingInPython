[[Reviewed]]
# Humanizer candidates: Chapters/12_Data_Classes_as_Types.md

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

The word-level half of the scan came up empty again: no em dashes anywhere in
the chapter, no curly quotes, no emoji, no boldface at all, no §7 AI vocabulary
beyond two stray "actually"s, no promotional language, no hedging, no rule-of-three
padding. All five italics introduce a term on first use.

The largest finding was person: eleven lines carried an editorial "we," clustered at
the chapter opening and at the head of `## Comparing Ordinary Classes and Data
Classes`. After that it was small stuff: three watch-list words from
`CLAUDE.md` ("in the first place," "buys," "at all"), one "is what makes"
cleft, two announcement sentences, and one word echo inside a single clause.

All Tier A and Tier B edits have been applied. The bare-annotation "promise"
metaphor (Housekeeping 3 below) has also been resolved: since chapter 09's own
review already replaced its "promise" wording with "declaration," the four
matching sites here were updated the same way for consistency, including the
direct quote of chapter 09's line.

## Housekeeping

1. **Typo at line 1171, fixed.** `` `C`s generated `__init__(...)` `` was
   missing an apostrophe; now reads `` `C`'s generated ``, matching line
   1237's `` `show(D())`'s ``.
2. **Semantic Line Break drift.** Several prose lines run well past a sentence or
   clause boundary without breaking: 130, 176, 810, 991, 1039, 1171 are the worst,
   and 1171 is 128 characters. `make reflow CH=12` fixes these; no gate catches
   them. Line numbers shift after the edits above, so re-check rather than
   trusting this list.
3. **Nothing else structural.** No double blank lines before any heading, no
   `[[ ]]` draft notes, no spaced ` -- `, no trailing whitespace runs.

## Considered and not flagged

Recorded so a later pass doesn't re-litigate these.

- **No em dashes in this chapter at all.** §14 had nothing to preserve and nothing
  to flag, same as 46 and 47.
- **All five italics introduce a term on first use**: *type* (3), *Design by
  Contract* (131), *data class* (140), *parse, don't validate* (335), *bare
  annotations* (1103). No emphasis italics anywhere, so the §-italics rule found
  nothing.
- **No boldface in the entire chapter.** §15 and §16 both vacuous here.
- **Lines 322-323**, "If you are holding a `Stars`, it is legal. / You know it
  without checking." A short declarative pair (§31). Kept: the second sentence is
  the chapter's actual claim, not drama, and it is the payoff the section built to.
- **Line 342**, "Illegal values are unrepresentable." A four-word closer, but it
  names the standard term for the idea the paragraph just built.
- **Line 860**, "It is what you do with any immutable value." Survives the
  `CLAUDE.md` deletion test: the words after "is what" are a clause that cannot
  attach without it, so cutting it breaks the sentence rather than tightening it.
- **Line 992**, "The type guards itself." "itself" is genuinely reflexive here,
  since the guard and the guarded thing are the same object.
- **Line 1078**, "`A` is the plain case." "plain" draws a real contrast with `B`'s
  defaults and `C`'s decorator, which is the exception the rule allows.
- **Line 715**, "because a factory function is advice rather than a gate." Reads as
  a §32 aphorism formula, but it states a checkable property and the test above it
  demonstrates exactly that.
- **Line 936**, "recover the constructor arguments, override the named ones,
  rebuild." Rule of three (§10), but it is the actual three-step algorithm, and the
  listing above performs all three.
- **Lines 818 and 1040**, "recursing into nested data classes" and "recursing
  through lists and nested objects." §3 participle tails, but each carries real
  behavior a reader needs, not fake depth.
- **Line 1240**, "`s`, declared `ClassVar[str]`, is a different story." Ordinary
  human idiom, and it earns its place as the pivot between two contrasted fields.
- **"never" x8** (14, 16, 337, 341, 653, 718, 1099, 1103, 1247). Avoid-if-possible
  list, but the chapter's subject is guarantees, and each one states one.
- **"only" x9** (178, 214, 270, 273, 320, 858, 1071, 1184, 1254). Every one is a
  real exclusion.
- **"already" x2** (327, 619). Both mark a genuine prior state.
- **"even" at 995.** Means "including when nested," not emphasis.
- **Line 1060**, "Each one is inspected with the same helper." Passive, but §13 is
  advisory in this repo and the four classes are the right subject to keep in focus.
- **Line 605**, "Every instance shares a single default object." Reads as a claim
  about behavior the language actually rejects, but it is describing the trap the
  rejection prevents, and the cross-reference to chapter 05 lands right there.

## Scan coverage

For a rerun: the word-level half of the skill is clean and does not need
re-running. No hits on §7 beyond the two "actually"s, no curly quotes (§19),
no emoji (§18), no boldface (§15) and therefore no inline-header lists (§16), no
promotional language (§4), no vague attributions (§5), no filler phrases (§23), no
hedging stacks (§24), no sycophancy (§22), no collaborative artifacts (§20), no
knowledge-cutoff disclaimers (§21), no false ranges (§12), no copula avoidance
(§8), no negative parallelisms (§9), no synonym cycling (§11), no hyphenated-pair
overuse (§26), no persuasive-authority tropes (§27), no conversational openers
(§33), no generic upbeat conclusion (§25) — the chapter ends on exercises. Every
finding above was structural: person, announcements, one fragmented header, one
echo, and watch-list words from `CLAUDE.md` rather than from the skill.
