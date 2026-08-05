[[Reviewed]]
# Humanizer candidates: Chapters/16_Comprehensions.md

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

The chapter is close to clean: no curly quotes, no emoji, no boldface-header
lists, no promotional language, no rule-of-three padding, no aphorism
formulas, no knowledge-cutoff disclaimers, and italics are used correctly
(only to introduce `Comprehensions` and `generator expression` on first use).
The real findings are structural and small: two person slips ("Let's",
"we"), a doubled "already" next to a stray "themselves," and a three-sentence
staccato run that also reads as a tailing-negation fragment. Tier B adds
two heading-echo openers and two minor word echoes. Largest single finding:
the person-consistency slips, since this book is otherwise consistently
second person.

## Tier A

### A1 — lines 27, 111-112 — person consistency

Two first-person-plural slips in an otherwise second-person book.
Neither carries the kind of exception noted for prior chapters
(a real acknowledgment, or a "let's...we" pair Bruce chose to keep),
so both read as simple, low-risk conversions to the book's usual voice.
Delete individual rows you want left alone.

**Line 27**

CURRENT
```text
Let's select the integers from a mixed list and square them.
```

PROPOSED
```text
Select the integers from a mixed list and square them.
```

**Lines 111-112**

CURRENT
```text
In Python we can represent such a matrix by a list of lists,
where each sub-list represents a row.
```

PROPOSED
```text
Python represents such a matrix as a list of lists,
where each sub-list represents a row.
```

### A2 — lines 205-207 — doubled "already," stray "themselves"

"Already" appears twice in adjacent sentences, and the closing "themselves"
adds nothing "the files" doesn't already say. `already` is on the
avoid-if-possible watch list; this is the clearest case of it not earning
its place twice over.

CURRENT
```text
By then the directory is already deleted.
The comprehension already finished building `py_paths` as plain strings while the directory still existed,
so nothing later needs the files themselves.
```

PROPOSED
```text
By then the directory is gone.
The comprehension already finished building `py_paths` as plain strings while the directory still existed,
so nothing later needs the files.
```

### A3 — lines 324-326 — tailing-negation fragment plus staccato run

"Same effect, no wasted list." is the same shape as the skill's flagged
example ("no guessing" tacked onto a fragment instead of a clause), and it
sits right before two more short declaratives, so the run of three reads as
manufactured rhythm rather than a single deliberate beat. The rewrite keeps
"reads honestly," since it draws a real contrast with "a loop wearing a
disguise" a few lines earlier.

CURRENT
```text
Same effect, no wasted list.
The `for` loop reads honestly.
It executes code rather than building a collection.
```

PROPOSED
```text
The `for` loop has the same effect without building a wasted list.
It reads honestly and executes code rather than building a collection.
```

## Tier B

### B1 — lines 14-16 — comma-spliced triad

Three claims about comprehensions (shorter, reads like a definition, one
line replaces several) run together on commas into one sentence. It isn't
a padded, generic AI triad since each claim is specific and true, but the
comma splice is exactly what CLAUDE.md's short-sentences rule flags, and
splitting it gives the first claim its own weight.

CURRENT
```text
A comprehension is shorter,
it reads like the definition of the result rather than a recipe for it,
and one line replaces several lines of loop bookkeeping.
```

PROPOSED
```text
A comprehension is shorter.
It reads like the definition of the result rather than a recipe for it,
and one line replaces several lines of loop bookkeeping.
```

I lean toward applying this one; the comma splice is real, but it's a
judgment call whether the original's momentum is worth keeping.

### B2 — lines 50, 56 — word echoes

Two spots repeat a word's root within the same sentence or bullet
("iterator"/"iterates", "predicate"/"predicate"). Minor, and arguably fine
in technical prose where precision matters more than variety, so this is a
genuine judgment call rather than a clear fix.
Delete individual rows you want left alone.

**Line 50**

CURRENT
```text
-   The iterator part iterates through each member `e` of the input sequence `a_list`.
```

PROPOSED
```text
-   The iterator walks through each member `e` of the input sequence `a_list`.
```

**Line 56**

CURRENT
```text
`filter()` applies a predicate to a sequence and retains the members that satisfy the predicate.
```

PROPOSED
```text
`filter()` applies a predicate to a sequence and retains the members that pass it.
```

### B3 — heading-echo openers

Both "Set Comprehensions" and "Dictionary Comprehensions" open with a
sentence whose subject just restates the heading's own words. Prior
chapters treated this per-instance (declined once, accepted once), so it's
a real call for Bruce rather than a rule. Both openers carry real content
(not filler), which argues for leaving them; the echo is the only issue.
Delete individual rows you want left alone.

**Lines 334-335**

CURRENT
```text
Set comprehensions construct sets using the same principles as list comprehensions.
Instead of `[]`, a set comprehension uses `{}`.
```

PROPOSED
```text
Set comprehensions use same principles as list comprehensions, with `{}` instead of `[]`.
```

**Lines 365-366**

CURRENT
```text
A dictionary comprehension builds a `dict`,
producing a key and a value for each element, with an optional filter.
```

PROPOSED
```text
A dictionary comprehension builds a `dict`.
Each element produces a key and a value, with an optional filter.
```

### B4 — line 522 — minor "already"

Isolated instance, not adjacent to another one like A2. Dropping it changes
nothing, but it's a single low-stakes word in an exercise, easy to leave.

CURRENT
```text
    given that `next(squares)` was already called twice before that line.
```

PROPOSED
```text
    given that `next(squares)` was called twice before that line.
```

## Housekeeping

None found. Checked and clean: no double blank line before any heading
(every heading in this chapter uses exactly one), no `[[ ]]` draft notes,
no spaced ` -- `, no stray em dashes of any kind, and Semantic Line Breaks
look intact throughout (every long sentence already breaks at its clause
boundaries; the one very long bullet at line 25 has no internal comma to
break at, so it isn't drift).

## Considered and not flagged

- Italics are used only to introduce `Comprehensions` (line 3) and
  `generator expression` (line 403) on first use; no emphasis-italics
  anywhere in the chapter.
- "itself nested inside the outer comprehension" (line 254) is load-bearing:
  it disambiguates which noun ("sorted()") the participial phrase modifies.
  Dropping it makes the sentence ambiguous, so it stays.
- "reads honestly" (line 325) draws a real contrast with "a loop wearing a
  disguise" (line 311) a few sentences earlier; it earns its place under
  the watch-list test and is kept in the A3 rewrite above.
- "a loop wearing a disguise" (line 311) is a specific, fresh metaphor, not
  a generic aphorism formula ("X is the Y of Z"); left alone.
- The three short parallel sentences at lines 284-286
  (`in_stock` answers.../`sort()` answers.../`report` answers...) and the
  "three parts mirror the list comprehension" passage at lines 379-381 both
  map onto a real, distinct three-part structure in the code, not a padded
  rule-of-three list; left alone.
- The semicolon at lines 146-147 (`zip()` stops...; pass `strict=True`...)
  ties two tightly linked clauses, matching the sparing-use rule in
  CLAUDE.md; left alone.
- No em dashes appear anywhere in the chapter, so there's nothing to
  protect or flag on that front.

## Scan coverage

Clean, no hits: curly quotes, emoji, boldface-header vertical lists,
promotional/advertisement language, vague attributions and weasel words,
knowledge-cutoff disclaimers and speculative gap-filling, sycophantic tone,
filler phrases, excessive hedging, false ranges, hyphenated-word-pair
overuse, persuasive-authority tropes, the "nothing else"/"nothing
but"/"nothing more" family, "Challenges and Future Prospects"-style
sections, collaborative-communication artifacts, and diff-anchored writing.
Word-level AI vocabulary (§7: delve, crucial, intricate, underscore,
showcase, testament, vibrant, tapestry, pivotal, landscape, garner, align
with, fostering, enhance) had zero hits, consistent with the same result in
chapters 46 and 47.
