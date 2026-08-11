When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/13_Pattern_Matching.md` in the
clean-slate sweep (resumed from an interrupted run whose draft edits were
verified and kept; they are marked below). The mechanical layer is sound:
the `#:` markers validate, `ty` and `ruff` are clean on
`build/examples/13_Pattern_Matching`, all twelve tests pass, and every
script runs. The chapter's quoted diagnostics were re-verified verbatim on
the pinned 3.15.0b4: all three `SyntaxError` messages (`multiple
assignments to name 'x' in pattern`, `name capture 'DEFAULT' makes
remaining patterns unreachable`, `alternative patterns bind different
names`), the `TypeError: R() accepts 0 positional sub-patterns (1 given)`,
and `assert_never()`'s `AssertionError: Expected code to be unreachable,
but got: 'x'`. Runtime probes confirmed the semantic claims: `case 200:`
matches `200.0` and `case 1:` matches `True`, while `case True:` matches
neither `1` nor `1.0`; a two-element sequence pattern accepts a `range`
and a tuple but not a generator, a `set`, or `"ab"`; a failed guard
leaves its captures bound; `case (x)` is a capture while `case (x,)` is a
one-element sequence pattern; `**rest` binds the unmentioned keys. Two
`ty` probes back the checker claims: deleting `summarize()`'s wildcard
produces `invalid-return-type` ("can implicitly return `None`"), so the
prose about the wildcard satisfying the declared return type is right,
and adding a `Triangle` to `Shape` produces `type-assertion-failure` at
`assert_never(shape)`. The `N806` claim was verified on ruff 0.16.2 (it
does fire on a `case DEFAULT:` capture; the repo's per-file ignore in
`pyproject.toml` is why the gate stays green). No findings met the bar
for a live block.

## Applied directly

Inherited from the interrupted run, verified, and kept:

- Literal section: added "so `case True:` does not match `1`", completing
  the `==`/`is` asymmetry next to "`case 1:` matches `True`".
- `sequence_patterns.py` prose: explained that the last `case _` never
  runs and stays only because the checker cannot prove exhaustiveness of
  the sequence patterns (confirmed by the wildcard-deletion probe).
- `point.py`: `@dataclass` is now `@dataclass(frozen=True)`, per house
  style (frozen unless mutation is the point) and matching every other
  dataclass in the chapter.
- Class patterns: "Despite the call syntax, a class pattern builds
  nothing: it tests the subject's type and reads its attributes",
  heading off the constructor-call misreading.
- Moved "keyword or positional" so it modifies "no arguments" rather
  than dangling after "any `Point` instance".
- Guards: added the `case [x, x]:` near-miss with its verbatim
  `SyntaxError`, steering the equal-elements test into a guard.
- `nested_patterns.py`: "two points, neither at an axis" is now "two
  points"; the old string was false ([Point(0, 5), Point(1, 1)] reaches
  that case with an axis point in it). Marker updated to match.

New in this run:

- Matching Values: added the no-fall-through contrast ("one `case` body
  runs, then the statement ends. Unlike C's `switch`, cases do not fall
  through, and `match` has no `break` to forget"), the classic
  switch-reader misconception the section assumed away.
- Exhaustive Matching: after the Scala/Kotlin/Java comparison, noted
  their forms are expressions while Python's `match` is a statement,
  which is why every `match` in the chapter sits inside a function that
  returns from each `case`. Readers from those languages would try to
  assign a `match`.
- Class patterns: the quoted `TypeError` named `R` with no referent; the
  sentence now introduces it ("For an ordinary class `R` that lacks one,
  `case R(1)` reports ...").
- "The type test is `isinstance()`, which has two consequences" promised
  a count the following prose did not deliver; now "so a subclass
  matches its base's pattern", with the follow-on paragraph opening
  "Because a subclass matches, the order of the cases decides which one
  wins."
- When Not to Match: "`get()` builds its default argument on every call"
  misattributed the cost; now "Python evaluates arguments before the
  call: every lookup builds the default string", which states the
  general rule the example turns on.
- Value patterns: "nothing warns you" is now "Python does not warn you",
  since `ruff` warning you is the very next sentence.
- Prose: activated "Pattern matching was briefly introduced"; "It never
  compares against a variable" lost its "never"; "almost never what a
  pattern means" is now "rarely"; "can also get there" is now "can reach
  the same guarantee".

## Considered and declined

- Mentioning `case [first, *_]` to ignore the rest of a sequence: both
  halves (wildcard, starred capture) are taught; the combination needs
  no separate lesson.
- Noting that `*rest` binds a list even when the subject is a tuple: a
  detail with no consequence in any of the chapter's examples.
- Renaming the three `describe()` functions (`http_status.py`,
  `type_patterns.py`, `keyword_patterns.py`): separate modules, and the
  test imports are explicit; renaming costs more than it buys.
- `broken()`'s trailing `return "unreachable"`: deliberate, and the
  string documents the point that the capture swallows everything.
