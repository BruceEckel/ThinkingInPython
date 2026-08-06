[[Reviewed]]
# Humanizer candidates: Chapters/14_Decorators.md

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

Clean chapter overall: no AI-vocabulary hits beyond one ("valuable"),
no curly quotes, no emoji, no rule-of-three padding, no em-dash issues
(the chapter has no em dashes at all), no double blank lines, no
`[[ ]]` notes. Two real findings: a first-person-plural slip at the
open (two "we" instances, the same pattern flagged in chapters 46/47),
and a term ("descriptor") re-italicized on its third mention after
already being properly de-italicized once. The largest single finding
is the person slip, since it sits in the chapter's opening paragraph.

All Tier A edits have been applied.

## Considered and not flagged

- **"*Decorator* pattern" italicized on every mention** (lines 81, 734,
  874). Looks like a first-use violation at first glance, but it's a
  book-wide convention: `30_Observer.md` italicizes "*Observer*" four
  separate times in one chapter, and `27_Factory.md` does the same for
  "*Builder*". Pattern names get italicized every time they name the
  GoF pattern, unlike ordinary technical vocabulary. Left alone.
- **"You can apply..." opening two different sections** (line 541,
  "Stacking Decorators," and line 602, "Decorating Classes"). Read like
  a possible echo or a mild case of §29 fragmented headers, but each
  instance is the first clause of a paragraph that immediately carries
  real content in the same sentence or the next, not a standalone
  restatement of the heading. Weak enough that flagging it would be
  noise.
- **Rule-of-three lists** at lines 116-119 (metadata: name, docstring,
  other attributes; consequences: debuggers, `help()`, documentation
  tools). Both are concrete, specific, technical enumerations, not the
  vague inspirational triads §10 targets. Left alone.
- **"A second surprise sits on the return side"** (line 691) and **"that
  was not an accident"** (line 492). Single short dramatic sentences,
  each isolated rather than part of a run of clipped fragments. The
  detection guidance explicitly says one short emphatic sentence isn't
  evidence of manufactured staccato drama. Left alone.
- **Em dashes.** The chapter has none, so §14 doesn't come up either
  way; nothing to preserve or flag.

## Scan coverage

Full sweep of §1-§33 plus the CLAUDE.md watch list found nothing beyond
what's listed above: no curly quotes, no emoji, no boldface-header
lists, no promotional or vague-attribution language, no hedging, no
false ranges, no signposting/announcement phrases, no "nothing else"
family survivors, no hyphenated-pair overuse, and no spaced ` -- `. Person
consistency and italics-on-reuse were the only categories that produced
real hits; a rerun can treat every other category as already checked
for this chapter.
