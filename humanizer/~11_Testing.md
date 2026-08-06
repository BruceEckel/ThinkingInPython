[[Reviewed]]
# Humanizer candidates: Chapters/11_Testing.md

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

A clean chapter. The prose is concrete, the cadence varies, and the
word-level half of the scan found nothing: no AI-vocabulary hits worth
naming, no curly quotes, no emoji, no boldface-header lists, no
promotional language, no hedging, no sycophancy. The file is pure ASCII,
so there are no em dashes to preserve and none to flag.
The largest single finding is two watch-list words that slipped through,
"ships" at line 280 and "spelling" at line 545, both on the "don't use"
tier of `CLAUDE.md`. The rest of Tier A is small structural work:
two first-person-plural slips, one emphasis italic, one participle tail,
one word echo, one staccato pair.

All Tier A and Tier B edits have been applied.

## Housekeeping

1. **No `[[ ]]` draft notes.** None anywhere in the chapter.
2. **No spaced ` -- `.** The file is pure ASCII: no curly quotes, no
   emoji, no `—`, and no `---` either, so §14 had nothing to preserve.
3. **No double blank lines.** Every heading has exactly one blank line
   before it.
4. **Semantic Line Breaks look compliant.** No line in the file carries
   two sentences. Four lines run past 92 characters (234, 466, 543, 578),
   but none has an interior top-level comma or colon to break at, so
   `make reflow CH=11` will probably leave them. Worth one run to confirm
   rather than trusting this.
5. **"parameterize" vs "parametrize".** Line 238 writes "You can
   parameterize fixtures too," while the heading at 149, the prose at
   152, and exercise 2 at 580 all use pytest's `parametrize`. Both are
   defensible (the API name against the English word), but a reader
   scanning for the decorator may stumble. Your call; I did not propose
   an edit because the heading is involved and its anchor is gated.

## Considered and not flagged

- **Line 3, "One of the most valuable habits in modern programming."**
  `valuable` is on the §7 AI-vocabulary list and the superlative reads
  like §1 significance-puffing. Kept: it is the chapter's thesis rather
  than an aside about an arbitrary aspect, and the word is used
  literally.
- **Line 5, "Tests extend the language."** An aphorism (§32), but a
  specific and arguable one, and the next line cashes it out.
- **Line 22, "Later rarely comes."** A three-word sentence, but a single
  clipped sentence for emphasis is human, and it is not part of a run.
- **Line 34, "when you happen to feel good about the code you just
  wrote."** `happen` is on the watch list. Kept: the phrase carries a
  dry dismissiveness that "when you feel good about" loses.
- **Lines 57-58, "just" twice.** Deliberate parallel repetition setting
  up the two ideas named on line 56, not synonym-free padding.
- **Lines 138-139, "Two situations come up repeatedly in testing, and both
  appear in `test_account.py`."** Looks like a §29 warm-up under its
  heading, but it names the file and sets up the "The first / The second"
  structure, so it carries information.
- **Every rule of three.** "refactor boldly, change designs, and clean
  up code"; the three numbered TDD benefits; "close files, release
  locks, or check a final invariant"; "a database, a message queue, or
  any other service"; the three reasons a network test is bad. All real
  enumerations. §10 is about forcing ideas into threes, and none of
  these is padded to reach the count.
- **The "X, not Y" closers at 382 and 547-548.** "The randomness is now
  an input, not a hidden dependency" and "one of discipline, not of
  compiler enforcement." Both are section closers where the contrast is
  the argument. A2 removes the one instance that made three in a row.
- **"actually" at lines 520 and 538.** On the watch list and on the §7
  list, but both draw the real contrast this section exists for: what
  `ty` reports against what the interpreter does.
- **"the exact name" at line 512.** Excluded from B4 deliberately; the
  word contrasts with the mangled name and is load-bearing there.
- **"black-box" in predicate position, line 553.** §26 says drop the
  hyphen after the noun, but this is a term of art introduced in italics
  with the hyphen, so unhyphenating it would read as a typo.
- **"plain programs" at line 572.** `plain` needs to earn its place, and
  here it does: it contrasts with the `test_*.py` files handed to
  `pytest` in the next sentence.
- **"ever" at line 480, "never" at 305, 463, 583.** Watch-list
  words, but each marks a real absolute rather than intensifying.
  Line 554's was dropped by the B6 edit as a side effect.
- **"already steeped in `datetime`" at line 459.** A metaphor, but a
  vivid and specific one, and `already` marks a real prior state.
- **Lines 330 and 386, "Code that calls `random` produces a different
  value each run" against "Code that reads `time.time()` gives a
  different answer every run."** A deliberate cross-section parallel
  that helps the reader, not §11 synonym cycling.
- **"Better still" (360) against "cleaner still" (409).** A faint echo
  across two sections, far enough apart that changing one would be
  fussing.

## Scan coverage

The word-level half of the skill was clean. No hits on §7 beyond
"valuable" and two contrastive "actually"s, all discussed above. Nothing
on §2 notability, §4 promotional language, §5 vague attribution, §6
challenges-and-prospects sections, §8 copula avoidance, §11 synonym
cycling, §12 false ranges, §15 boldface, §16 inline-header lists, §18
emoji, §19 curly quotes, §20 chatbot artifacts, §21 cutoff disclaimers,
§22 sycophancy, §23 filler phrases, §24 hedging, §25 generic upbeat
conclusions, §27 authority tropes, §28 signposting, §30 diff-anchored
writing, or §33 rhetorical openers. §17 does not apply to book headings,
and §29 produced no real hit across all fifteen headings. Every finding
above came from §3, §9, §31, §32, the person check, the italics rule, or
the `CLAUDE.md` watch list.
