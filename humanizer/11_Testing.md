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

## Tier A

### A1 — line 280 — banned word: "ships"

`ships` is on the "don't use" tier. Name the literal thing.

CURRENT
```text
`pytest` ships built-in fixtures for this.
```

PROPOSED
```text
`pytest` includes built-in fixtures for this.
```

### A2 — lines 545-546 — banned word: "spelling", plus a third negation in a row

`spelling` is on the "don't use" tier: it means the name here, so say the
name. The rewrite also breaks up a cluster: lines 544, 546, and 548 all
close on "X, not Y," and the middle one is the least load-bearing of the
three.

CURRENT
```text
Anyone who knows the class name can still reach it, so it changes the spelling,
not the reachability.
```

PROPOSED
```text
Anyone who knows the class name can still reach the attribute,
because the rewrite changes only the name.
```

### A3 — line 515 — emphasis italic

The chapter's other five italics all introduce a term on first use
(*white-box*, *black-box*, *fixtures*, *name mangling*, *property-based*).
This one emphasizes "double" against the single underscore above it,
which the sentence already does on its own.

CURRENT
```text
A leading *double* underscore does something real,
```

PROPOSED
```text
A leading double underscore does something real,
```

### A4 — lines 63, 420 — first person plural

The only two "we" sites in the chapter. Both are listing lead-ins, and
neither is a genuine first person plural. Delete individual rows you want
left alone.

**line 63**

CURRENT
```text
We will test the `Account` class:
```

PROPOSED
```text
The tests that follow check the `Account` class:
```

**line 420**

CURRENT
```text
In the test we provide a fixed value for `now`:
```

PROPOSED
```text
The test provides a fixed value for `now`:
```

### A5 — line 153 — participle tail

§3. The reporting is a second thing `pytest` does, not a gloss on the
first, so a conjunction is more accurate than a participle.

CURRENT
```text
`pytest` runs it once per case, reporting each separately.
```

PROPOSED
```text
`pytest` runs it once per case and reports each separately.
```

### A6 — lines 187-188 — word echo

"function" three times across two lines. Line 186 has already defined a
fixture as a function, so the modifier is not needed either time.

CURRENT
```text
You declare fixtures as parameters to the test functions,
which tells `pytest` to call the fixture function and pass its result to the test function.
```

PROPOSED
```text
You declare fixtures as parameters to a test,
which tells `pytest` to call the fixture and pass its result to the test.
```

### A7 — lines 508-509 — staccato pair

§31. Two clipped sentences where the second is the consequence of the
first. Joining them states the causal link instead of implying it.

CURRENT
```text
Python has no access control.
Every attribute is reachable.
```

PROPOSED
```text
Python has no access control, so every attribute is reachable.
```

## Tier B

### B1 — lines 8-10 — contentless topic sentence

Paragraph 1 has already established unit testing as a habit you build
into the code you write, so "is a development practice" adds no new
claim before the safety-net point. I lean toward cutting it, but if you
meant it to contrast a practice with a phase, that contrast is not in the
sentence and would need saying outright instead.

CURRENT
```text
Unit testing is a development practice.
Tests give you a safety net.
With them you can refactor boldly, change designs, and clean up code.
```

PROPOSED
```text
Tests give you a safety net.
With them you can refactor boldly, change designs, and clean up code.
```

### B3 — line 145 — aphorism formula

"X is a trap" is on the §32 watch list. The concrete claim is that
equality on floats does not hold, which the next two lines then explain.
I lean toward changing it; the sentence loses a little bite.

CURRENT
```text
The second is comparing floating-point numbers, where exact equality is a trap.
```

PROPOSED
```text
The second is comparing floating-point numbers, where testing for exact equality is unreliable.
```

### B4 — lines 155, 356 — "exact" as an intensifier

Two sites where deleting the word changes nothing. `exactly` is on the
watch list and the same test applies to the adjective. Line 512's "that
exact name" is deliberately excluded: it contrasts with the mangled name
and is load-bearing. Delete individual rows you want left alone.

**line 155**

CURRENT
```text
and a failure names the exact case that failed.
```

PROPOSED
```text
and a failure names the case that failed.
```

**line 356**

CURRENT
```text
Patching the function gives you the exact value you want.
```

PROPOSED
```text
Patching the function gives you the value you want.
```

### B5 — lines 197-198 — lead-in narrates the listing twice over

The code comments already label setup, yield, and teardown, and lines
219-221 explain the same three steps again after the listing. This makes
three passes over one idea. I lean toward the cut, but a bare "For
example:" is abrupt if you want the reader oriented before the code.

CURRENT
```text
For example, this fixture builds an account, `yield`s it to the test,
then runs teardown once the test returns:
```

PROPOSED
```text
For example:
```

### B6 — lines 553-554 — staccato pair

§31, weaker than A7 because the second sentence is evidence for the
first rather than a consequence. Joining with a colon makes that
relationship explicit and drops a "never."

CURRENT
```text
The `Account` tests are black-box.
They never read a private attribute.
```

PROPOSED
```text
The `Account` tests are black-box which means they never read a private attribute.
```

### B7 — lines 45-47 — grand framing, then a repeated subject

"With the advent of AI" is the §1 register (an era being marked) for what
is a practical observation, and the next sentence restarts on "AI"
anyway. Merging drops both. Against it: the two-sentence version gives
the second point its own beat, which you may want.

CURRENT
```text
With the advent of AI,
generating tests once you have found a good path becomes far more viable.
AI also makes a thorough test suite easier to produce.
```

PROPOSED
```text
AI makes generating tests far more viable once you have found a good path,
and makes a thorough test suite easier to produce.
```

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
- **"the exact name" at line 512.** Excluded from B4 deliberately; see
  that block.
- **"black-box" in predicate position, line 553.** §26 says drop the
  hyphen after the noun, but this is a term of art introduced in italics
  with the hyphen, so unhyphenating it would read as a typo.
- **"plain programs" at line 572.** `plain` needs to earn its place, and
  here it does: it contrasts with the `test_*.py` files handed to
  `pytest` in the next sentence.
- **"ever" at line 480, "never" at 305, 463, 554, 583.** Watch-list
  words, but each marks a real absolute rather than intensifying.
  Line 554's is dropped by B6 as a side effect.
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
