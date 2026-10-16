> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: 36_Patterns--Memento solutions (2026-10-16)

A full audit of the prose in `Solutions/36_Patterns--Memento/README.md` (hints, the opening paragraph of each solution, and the step paragraphs) against the readability patterns.
No completed review of this file exists, so `readability_db.md` and the chapter's open review were read first; neither holds an entry for this file.
The file is technical register with no Tier 1A or Tier 2 vocabulary, no curly quotes, no spaced `--`, no signposting openers, and no generic closer; the bold step labels are the solutions ladder's convention.
Four sentences fired a rule with one sensible answer and were fixed in place.
Nothing needs your decision, so the file has no live blocks and serves as the applied-directly record.
`tip verify-ch CH=36 ISOLATED=1` passes 27 of 27.

## Applied directly

- Line 334, treadmill (§70 restatement): "`can_undo()` keeps the chapter's body. It asks whether `_past` still holds a state." repeated the solution's opening paragraph ("The solution keeps the chapter's `bool(self._past)`") -> "`can_undo()` asks whether `_past` still holds a state."
- Line 466, "and" joining clauses with different subjects: "All three existing tests fail against this version, and pytest reports them in the order they appear in the file, so ..." -> "All three existing tests fail against this version. They fail in the order they appear in the file, so `test_restore_rewinds_state` is the first failure pytest reports:"
- Line 487, "and" hiding a consequence ("so" fits): "The list inside stays mutable, and every later `draw()` changes it. So `save()` must copy ..." -> "The list inside stays mutable. Every later `draw()` changes that list, so `save()` must copy ..."; the paragraph is rewrapped to the file's column width.
- Line 619, "and" joining clauses with different subjects: "`goto()` reuses the existing `undo()`, calling it repeatedly, and each `undo()` pushes the state it leaves onto `_future`. Redo therefore works as if ..." -> "`goto()` calls the existing `undo()` repeatedly. Each `undo()` pushes the state it leaves onto `_future`, so redo works as if ..."

## Considered and declined

- Lines 796 and 897, §34 "real": "`copy.replace()`, which constructs a real instance". The contrast is named: `pickle.loads()` "builds a bare instance" and skips the constructor (line 891); recurring keep.
- Line 162, a participial opener: "Using a `History` trimmed to what the test needs, the history test checks the same property ...". The participle attaches to the test, its grammatical subject, so it does not dangle.
- Line 389, a quoted diagnostic after a comma: "`hash()` raises a `TypeError`, `unhashable type: 'list'`." A colon would also be right; the appositive comma reads cleanly and the diagnostic is still marked off.
- Line 623, "Jumping several states back "in one call" is a convenience for the caller." Answers the exercise's quoted phrase directly, so it is the paragraph's point rather than a closer.
- Line 640, `only`: "pass it to `copy.replace()` as the only change". The "the only X" shape was ruled fine (2026-10-04), and the restriction is the hint.
- Lines 761-762, a two-sentence verdict: "A library would justify that `Protocol`. A solution reads more easily with the concrete type." A design judgment the reader needs, weighed against a stated alternative, not a flourish.
- Line 901, "In general," as a transition opener (§62). The file's single one, and it marks the shift from the listing to the general rule about constructors and deserializers.
