# Humanizer candidates: Chapters/36_Memento.md

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

This chapter is clean. No first-person-plural anywhere (it is second person
throughout, with no editorial "we" to convert), no §7 AI-vocabulary hits, no
curly quotes, no emoji, no boldface lists, no promotional language, no
hedging, no filler phrases, no signposting, no fragmented headers, and no
em dashes at all, so there was nothing to preserve or flag there either.

The one real finding is a single italics-for-emphasis at line 167 (Tier A);
every other italic in the chapter introduces a term on first use, which is
what confirms this one as the outlier. The rest is three arguable
word-level calls (Tier B). Housekeeping is empty.

## Tier A

### A1 — line 167 — italics used for emphasis

The chapter's other five italics (*Memento*, *originator*, *memento*,
*caretaker*, *structural*/*nominal*, *schema migration*) all introduce a
term on first use. This one italicizes the copula for emphasis, which is
the pattern the surrounding correct uses make visible.

CURRENT
```text
Once the state is a frozen data class, every state *is* a memento:
```

PROPOSED
```text
Once the state is a frozen data class, every state is a memento:
```

## Tier B

### B1 — lines 371-372 — "itself" as flourish

"is itself undoable" reads the same with "itself" dropped; the sentence
already says the restore goes through `do()` like any other action, which
is the reason it is undoable. I lean toward applying this, but there is a
readable case that "itself" is doing a little real work, flagging the
recursive point that even a restore can be undone.

CURRENT
```text
It goes through `do()` like any other action,
so the partial restore is itself undoable, as the last line shows.
```

PROPOSED
```text
It goes through `do()` like any other action,
so the partial restore is undoable, as the last line shows.
```

### B2 — line 470 — trailing "ever"

"anywhere, ever" pairs a spatial and a temporal totality claim. There is a
real contrast in view: the previous paragraph's added-field drift *does*
eventually fail when something touches the gap, so "ever" is arguably
carrying the point that this drift never does. I lean toward keeping it
for that reason, but it also reads as an intensifier tacked onto a sentence
that already said "anywhere."

CURRENT
```text
If you delete or rename a field, old bytes load with no error anywhere, ever.
```

PROPOSED
```text
If you delete or rename a field, old bytes load with no error anywhere.
```

### B3 — lines 228-229 — "plain" as filler qualifier

Test from `CLAUDE.md`: does the sentence still work without it? It does.
There is a possible contrast with the earlier `Memento`-wrapper class
(these states need no wrapper at all), but that contrast is never made
explicit nearby, so the word is doing quiet work at best.

CURRENT
```text
With states as plain immutable values,
the caretaker no longer needs to know anything about them.
```

PROPOSED
```text
With states as immutable values,
the caretaker no longer needs to know anything about them.
```

## Housekeeping

1. No `[[ ]]` draft notes.
2. Every heading has exactly one blank line before it, consistently; no
   double-blank-line drift to report.
3. No Semantic Line Break violations found. The handful of prose lines
   over 90 characters (62, 120, 203, 232, 375, 376, 462, 499, 501) are
   each a single clause with no top-level comma/semicolon/colon to break
   at, or are already broken at every such point.
4. No em dashes and no spaced ` -- ` anywhere in the chapter.
5. No prose inside listing comments (every `#` in a fenced block is a
   filename header or a `# type: ignore`/`#:` directive), so no
   "Listing comments" item to report.

## Considered and not flagged

- **Person.** Zero hits on "we"/"us"/"our." The chapter is already
  consistently "you," including the two conditionals at lines 166 and 470
  and the closer at line 502.
- **Line 9, "without ever looking inside."** "ever" is on the watch list,
  but here it asserts the caretaker never once looks, which is the whole
  point of a caretaker; dropping it weakens the claim of total opacity.
- **Line 128, "already immutable."** Marks a real temporal contrast: the
  tuple's immutability is inherent and predates the fix, while the
  attribute's was not and needed `frozen=True`.
- **Line 462, "nothing ever validated."** Same family as line 9; ties back
  to "before a validated field existed" two lines up.
- **Line 117, "honest mistakes."** Contrasts with a deliberate or
  malicious edit, not the ordinary sense of "honest" tone; a real contrast,
  not a flourish.
- **Line 294, "any state type, `int` to full `Sketch`."** Reads like a §12
  false range on the surface, but both endpoints are concrete types the
  chapter already uses, not a grandiose sweep like "from the Big Bang to
  dark matter."
- **Lines 203-205, "Flyweight shares immutable values across space, and
  Memento shares them across time."** Close to a §32 aphorism formula, but
  it is a specific, linked cross-reference to two real chapters, not
  empty profundity.
- **Lines 474-476, three short sentences in a row** ("The added-field
  drift... The removed-field drift... The data is just quietly wrong.").
  Close to §31 staccato, but each fragment reports a distinct fact, not
  manufactured drama, and they vary enough in length.
- **Rule-of-three lists** at lines 383-384 (saved game, session file,
  crash-recovery point) and line 502 (rewind, rollback, restore). Both are
  concrete, distinct enumerations tied to real uses, not padding.
- **No `Memento` class exists, no `save()`, no `restore()`, and no
  copying to protect the past" (line 200).** An elliptical parallel
  listing concrete absent artifacts, not a broken parallel or manufactured
  triple.

## Scan coverage

Found nothing: §7 AI-vocabulary words, curly quotes, emoji,
boldface-header lists (§15, §16), promotional/advertisement language (§4),
vague attributions (§5), a challenges-and-prospects section (§6), copula
avoidance (§8), negative parallelism (§9), elegant variation (§11),
passive/subjectless fragments (§13), hyphenated-pair overuse (§26),
persuasive authority tropes (§27), signposting or announcements (§28),
fragmented headers (§29), diff-anchored writing (§30), collaborative
communication artifacts (§20), knowledge-cutoff disclaimers (§21),
sycophancy (§22), filler phrases (§23), excessive hedging (§24), and a
generic positive conclusion (§25). Word-level scanning was, again, mostly
a dead end here; the one real finding is structural (italics), and the
rest is judgment calls on individual words.
