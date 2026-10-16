> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability review of `Solutions/09_Foundations--Class_Attributes/README.md`,
2026-10-16.
The file carried no AI-vocabulary clusters; its faults were restatements
inside a solution and a few "and"s joining clauses with different subjects.
Eight fixes went in directly, and no finding needed Bruce's judgment, so
this file holds no live block and serves as the applied-directly record.
The `type(self)` fork arithmetic in solution 7 (a subclass constructed
twice reaches `4`) and the commented-out `a.total = 99` in `class_var.py`
were checked and hold.
`tip verify-ch CH=09 ISOLATED=1` passed, 27 of 27.

## Applied directly

- Line 198, treadmill: "`vars(a)` shows the shadow. `a` now has its own
  `total` entry. ... still reports `2`, because the assignment went to
  `a`'s dictionary." became "`vars(a)` shows the shadow: a `total` entry
  in `a`'s own dictionary. `Tally.total` ... still reports `2`." The
  paragraph above already says twice that the write lands on the
  instance. The next paragraph was rewrapped, wording unchanged.
- Line 321, treadmill: cut "The assignment and the `del` both stay on the
  instance, so the class attribute keeps its `100` throughout." The next
  paragraph, labeled "Show that deletes stop at the instance", makes the
  same point with `vars(A)["x"]` as its evidence.
- Line 420, "and" joining clauses with different subjects: "`vars(c)` is
  empty because ..., and reading `c.total` falls back ..." became two
  sentences.
- Line 493, treadmill: cut "because all three names share one list" from
  the first sentence. The paragraph's last sentence makes that claim with
  the `is` tests that prove it.
- Line 502, clarity: "A mutable `ClassVar` in a single class declares its
  sharing" became "In a single class, a mutable `ClassVar` declares its
  sharing", so the sentence opens on the condition that contrasts it with
  the inheritance case after it.
- Line 516, treadmill: "The listing models a bug. The base class declares
  one list, and each subclass treats that list as its own. Every subclass
  appends its entries to that one list." became "The listing models a bug
  in which every subclass treats the single list on the base class as its
  own." The third sentence restated the second, and the paragraph above
  already ends on "one list ... that every subclass mutates".
- Line 586, "and" joining clauses with different subjects: "creates the
  attribute on the instance, and the type checker checks that assignment"
  became two sentences.
- Line 705, "and" joining clauses with different subjects: "holds no
  `total` at any point, and both names report the one shared count, so
  ..." became two sentences.

## Considered and declined

- Lines 35, 195, 246, "brand-new" three times. Each sits in a different
  solution, and in solution 4 the word marks the new instance attribute
  against the class attribute it shadows.
- Line 15 and line 449, hints written one sentence per line rather than
  hand-wrapped. The hint paragraphs across the Solutions files use that
  form, so they stay.
- The bold step labels whose first line runs long (lines 193, 269, 326,
  402, 410, 421, 699, 707). Rewrapping changes no wording; the paragraphs
  touched above were rewrapped as part of their edits.
- Line 503, the paragraph combining `shared_mutable.py` with
  `class_var_inheritance.py`. Saying outright that each mechanism is
  harmless alone would make its contrast clearer, but that is a claim the
  file only implies, so the paragraph got the small reorder above instead.
- Line 581, watch word "never": "never checks that a method assigns
  `seat`" states what the checker guarantees not to do, which is the
  solution's point.
- Line 202, "This shadow is the bug `ClassVar` exists to catch." A short
  verdict that ties the solution back to the chapter, not a §39 flourish.
