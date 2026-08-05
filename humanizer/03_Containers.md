[[Reviewed]]
# Humanizer candidates: Chapters/03_Containers.md

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

This chapter is close to clean. No word-level AI vocabulary, no curly
quotes, no rule-of-three padding, no signposting, no fragmented headers,
no staccato drama, and person is consistently second-person throughout
(no "we"/"us"/"our" anywhere). One real grammar finding (a stranded
preposition) and one arguable wordiness call in the opening paragraph.
No housekeeping issues: no double blank lines, no SLB drift, no draft
notes, no em dashes to worry about (there are none in this chapter at
all, spaced or otherwise).

## Tier A

### A1 — line 309 — stranded preposition

"the end you append to" strands the preposition at the clause end;
the object ("the end") was fronted. A noun-phrase rewrite drops it
without changing the meaning.

CURRENT
```text
A `deque` (double-ended queue)
adds and removes items at either end in constant time.
A `list` is fast only at the end you append to:
```

PROPOSED
```text
A `deque` (double-ended queue)
adds and removes items at either end in constant time.
A `list` is fast only at its append end:
```

## Tier B

### B1 — line 4 — inflated opening phrasing

"acknowledges the essential nature of containers by building them into
the core of the language" is a §1-flavored significance claim (compare
"underscores its importance") where a plainer sentence says the same
thing. This is the chapter's opening line, so it may be a deliberate
authorial flourish rather than padding; I lean toward proposing it but
would understand declining it.

CURRENT
```text
With languages like C++ and Java, containers are add-on libraries.
Python acknowledges the essential nature of containers by building them into the core of the language.
Lists, dictionaries, and sets are fundamental data types.
```

PROPOSED
```text
With languages like C++ and Java, containers are add-on libraries.
Python builds them into the core of the language.
Lists, dictionaries, and sets are fundamental data types.
```

## Housekeeping

None found. No double blank lines, no Semantic Line Break drift, no
`[[ ]]` draft notes, and no spaced ` -- `. The chapter has no em dashes
of any form to check.

## Considered and not flagged

- **"resizes itself" (line 31).** Reflexive and load-bearing (the list
  resizes on its own, no manual step), matching the CLAUDE.md exception
  for `itself`. Not a flourish.
- **Italic on "proper" (line 238), `` `<` and `>` test *proper* subset
  and superset. ``** Introduces the proper-subset/proper-superset
  distinction for the first time, consistent with the chapter's other
  first-use italics (`slice`, `tuple`, `hashable`, `factory`, `view`).
  Not emphasis.
- **"frozendict... completes the set" (line 405).** Reads like a §1
  significance claim on first pass, but it is a literal, accurate
  description of the tuple/frozenset/frozendict pattern the previous
  sentence just established, not vague puffery. Left alone.
- **Parenthetical line break, "A `deque` (double-ended queue) / adds
  and removes items..." (lines 307-308).** Breaks right after a
  parenthetical rather than at a top-level comma/semicolon/colon.
  Not treated as Semantic Line Break drift since it lands at a natural
  clause boundary.
- **Person.** Checked the whole chapter for "we"/"us"/"our"; none
  exist. Second person ("you") is used consistently and correctly
  throughout, including in the immutability section's several `you`
  references.
- **Three- and four-item lists** ("Lists, dictionaries, and sets",
  "`Counter`, `defaultdict`, `deque`, and `namedtuple`", "strings,
  numbers, and tuples") are exhaustive factual enumerations the content
  needs, not rule-of-three padding for the appearance of completeness.

## Scan coverage

Zero hits on: AI-vocabulary list (§7), copula avoidance beyond the one
noted, negative parallelism/tailing negation (§9), elegant variation
(§11), false ranges (§12), vague attributions (§5), promotional/
advertisement language (§4), "Challenges and Future Prospects" sections
(§6), inline-header vertical lists (§16), boldface overuse (§15),
emojis (§18), curly quotes (§19), collaborative/sycophantic artifacts
(§20, §22), knowledge-cutoff disclaimers (§21), filler phrases (§23),
excessive hedging (§24), generic positive conclusions (§25),
hyphenated-pair overuse beyond correct attributive uses (§26),
persuasive-authority tropes (§27), signposting/announcements (§28),
fragmented headers (§29), staccato drama (§31), aphorism formulas (§32),
conversational rhetorical openers (§33), and the "nothing else" family.
Listing comments inside code blocks were also checked line by line;
none carry watch-list words or editorial "we."
