> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability review of `Solutions/02_Foundations--Tour/README.md`, 2026-10-16.
The prose was already close to clean: four fixes went in directly,
and no finding needed Bruce's judgment, so this file holds no live block
and serves as the applied-directly record.
The claims about `safe()`, `shout()`, the `N` rules in `pyproject.toml`,
and Naming Conventions were checked against the chapter and the config
and hold.
`tip verify-ch CH=02 ISOLATED=1` passed, 27 of 27.

## Applied directly

- Line 25, treadmill (restatement): cut "`c = a[:]` builds a new list,
  so `a` still holds `[1, 2, 3, 4]`." The paragraph after the listing
  says the same thing and also answers the exercise's "explain why".
- Line 175, "and" joining clauses with different subjects (global rule):
  "Ruff leaves those rules off by default, and this book's
  `pyproject.toml` turns them on" became two sentences.
- Line 244, treadmill: cut "The `isinstance()` test decides which branch
  each piece takes." Two lines later the paragraph says a two-branch `if`
  decides what to do with each piece, and gives the reason.
- Line 260, §39 self-labeling significance / filler flourish: "That
  failed guess is the argument for `Template` in one example." became
  "`Template` removes that guess, because it keeps each value apart from
  the literal text." It restates lines 245-246 and adds no new claim.
  The close alternative was to cut the sentence, but that would lose the
  link back to `Template`.

## Considered and declined

- Line 240, §15 boldface: "**Tell values from literal text.**" is the
  file's one bold label. Bold step labels are a Solutions convention,
  used in every Solutions README from 03 on, so it stays.
- Line 253, watch word `only`: "A post-processor has only the
  characters" states a real restriction, the point of the paragraph.
- Line 77, colon: "The rule is the same for every container: falsy when
  empty, truthy otherwise." The colon introduces the rule the lead-in
  names.
- Line 169, negative statement: "`totalSum` and `flagBits` say nothing
  about the value." It is half of a contrast with the next sentence.
- Line 262, §47 contrast pair: "a security hole rather than a typo" is a
  real contrast that sets the stakes, not mirroring for rhythm.
- The opening paragraph of solutions 1 and 5 (the wrong version's output,
  then "The solution keeps/passes ..."): this is the Solutions files'
  usual trap-first opening, not a treadmill.
- Lines 108-111: the hand-wrapping of the `.2f` paragraph is uneven, but
  rewrapping it would change no wording, so it was left alone.
