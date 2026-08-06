[[Reviewed]]
# Humanizer candidates: Chapters/20_Rethinking_Objects.md

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

Mostly clean, and dense with deliberate craft (the recurring "OOP
promise" framing, the italics-as-term-introduction discipline, four
parallel "Prefer X over Y" guidelines). The real findings were small:
a scattered "we"/"our" leaving the book's second person in three
places, one metaphorical "promise" that CLAUDE.md's rule targets
directly, one verbatim §7 AI-vocabulary hit ("crucial"), one
seven-sentence choppy run, and one participle tail. No curly quotes,
no em-dash issues, no emoji, no boldface-list abuse, no signposting,
no `[[ ]]` notes. The single biggest finding was the person-consistency
cluster: three separate "we"/"our" slips in an otherwise second-person
(or, in the opening, first-person-singular "I") chapter.

All Tier A and Tier B edits have been applied.

## Considered and not flagged

- **The "OOP promise" refrain itself** (lines 36, 70, 84, 282, 381,
  443). "Promise"/"promises" recurs as a deliberate numbered
  structural conceit spanning the whole chapter (four OOP promises:
  encapsulation, methods, inheritance, polymorphism), set up before
  the enumeration even starts ("makes no substitutability promises,"
  "the base class... promises"). This is the controlling metaphor for
  the chapter's organization, not the stray "promise = guarantee" tell
  CLAUDE.md's rule targets. Only the unrelated, isolated use that was
  at line 836 (A3 above) was a different, narrower metaphor and got
  flagged and fixed.
- **"The fourth OOP promise is polymorphism."** (line 443). Bare,
  one-clause, no elaboration, unlike its siblings at lines 84 and 282.
  Reads like it could be a fragmented header (§29), but it introduces
  by far the longest and most-developed section in the chapter, so
  the terseness plays as a deliberate teaser rather than padding.
  Left alone.
- **Guidelines' closing bullet** ("Prioritize simplicity, clarity, and
  maintainability, to produce reliability."). Breaks the "Prefer X
  over Y" parallel of the four bullets above it, but it's doing
  different work: a synthesizing principle behind the four
  preferences, not a fifth preference. Forcing it into the same
  "Prefer... over..." shape would invent a contrast that isn't there.
  Left alone.
- **Italics used correctly throughout.** *Simula*, *Smalltalk*, *C++*,
  *Java*, the *Liskov Substitution Principle*, *shallow* (of a copy),
  the *diamond problem*, *nominal*/*structural*, *Subtype*/*Parametric*/
  *ad-hoc polymorphism*, *function overloading*, and the *Null Object*
  pattern are each a first-use term introduction, consistent with
  CLAUDE.md's rule. None are emphasis-only.
- **Rule-of-three-shaped groupings** (`charge()`/`persist()`/`audit()`
  at line 628; "return a description... finish rather than block...
  describe the object..." at line 723). Each count is structurally
  necessitated by the code or the argument, not an invented triad.
  Left alone.
- **Awkward double comma** ("made sense for the problem, and the
  hardware, of its time," lines 20-21). Reads oddly, but it isn't any
  of the listed AI patterns, just an idiosyncratic aside. Out of scope
  for this pass.

## Scan coverage

No hits anywhere in the chapter for: §1-2 undue-emphasis/notability
language, §4 promotional language ("boasts," "vibrant," "nestled"),
§5 vague attribution, §6 "Challenges and Future Prospects" sections,
§8 copula avoidance ("serves as," "features a"), §9 negative
parallelism/tailing negation, §10 rule-of-three abuse beyond the
structurally real counts noted above, §11 elegant variation, §12 false
ranges, §15 boldface overuse, §16 inline-header vertical lists, §18
emoji, §19 curly quotes, §20-22 chatbot-communication artifacts and
sycophancy, §21 knowledge-cutoff disclaimers, §23-24 filler phrases and
hedging, §25 generic positive conclusions, §26 hyphenated-pair overuse
(every hyphenated compound found is correctly attributive), §27
persuasive-authority tropes, §28 signposting ("let's," "here's what"),
§32 aphorism formulas, and the rest of §7's AI-vocabulary list beyond
"crucial." Person consistency was checked in full: the three sites in
A1 were the only first-person-plural slips in the chapter.
