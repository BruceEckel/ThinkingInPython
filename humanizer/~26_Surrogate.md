[[Reviewed]]
# Humanizer candidates: Chapters/26_Surrogate.md

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

This chapter is clean. Nothing from the AI-vocabulary list, no curly
quotes, no boldface lists, no manufactured drama, no fragmented
headers, no signposting. What surfaced was small and mechanical: one
person slip, one stranded preposition, and two emphasis italics.
The single most important finding was the lone "If we implement" at
line 28, the only first-person slip in a second-person book.

All Tier A and Tier B edits have been applied, along with the
Housekeeping italics-consistency fix (line 61's parenthetical now
italicizes *Proxy* like every other prose reference to the pattern).

## Housekeeping

1. No Semantic Line Break drift: `uv run python tools/reflow_prose.py
   --diff Chapters/26_Surrogate.md` reported 0 paragraphs changed.
2. No double-blank-line-before-heading drift: every heading in this
   chapter (`## Proxy`, `## State`, `## Exercises`) sits behind a
   single blank line, consistently.
3. No `[[ ]]` draft notes and no spaced ` -- ` anywhere in the file.

## Considered and not flagged

- Italicized pattern names (*Proxy*, *State*, *GoF Design Patterns*,
  *Remote proxy*, *Virtual proxy*, *Protection proxy*,
  *Smart reference*, *Surrogate*, *copy-on-write*) — confirmed as a
  book-wide convention by checking sibling pattern chapters
  (27_Factory, 30_Observer, 33_Visitor, 25_Template_Method, etc.),
  not an emphasis-italics tell.
- `*fallback*` at line 361 — legitimate first-use term introduction;
  the second mention at line 369 ("The fallback hook") correctly
  drops the italics, so the rule is already applied correctly here.
- "The beauty of using `__getattr__()` is that `Proxy2` is completely
  generic" (line 167) — this is the author's long-standing signature
  phrasing across the "Thinking in ___" series, not an AI aphorism
  formula.
- The four-item GoF proxy-use list (lines 305-317) as a whole — not a
  manufactured "rule of three." It's a direct, sourced citation of
  GoF's own taxonomy, and there are four items, not three.
- "only" (seven hits) — each one is restrictive and precise about
  actual runtime behavior (e.g. "intercepts only the lookups not
  found," "counts only callable accesses"), not filler.
- "itself" at line 366 ("calls itself forever") — reflexive and
  load-bearing per the CLAUDE.md exception, left alone.
- The "We're Knights of the Round Table" / "We dance..." lines
  (251-274) — quoted Monty Python lyrics inside a code listing, not
  authorial first person, and off limits as code regardless.

## Scan coverage

Clean on: §7 AI-vocabulary word list, curly quotes, boldface
inline-header lists, emojis, sycophantic/servile tone,
knowledge-cutoff disclaimers and speculative gap-filling,
collaborative-communication artifacts, rule-of-three padding, false
ranges, excessive hedging, aphorism formulas, manufactured-punchline
staccato, fragmented headers, diff-anchored writing, and
signposting/announcements. Listing comments (the `#` prose inside
each ```python block) were checked individually and hold no watch-list
words, no "we," and nothing else worth a Housekeeping note. Findings
that did surface were structural: person consistency and emphasis
italics, both direct hits against named precedents from chapters 46
and 47.
