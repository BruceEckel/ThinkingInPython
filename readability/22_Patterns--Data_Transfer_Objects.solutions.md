> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability review of `Solutions/22_Patterns--Data_Transfer_Objects/README.md`,
2026-10-16.
The prose had almost no AI vocabulary; most findings were clause joins
where "and" hid a contrast or joined two claims with different subjects,
plus a few hand-wrapped lines that had grown past 100 columns.
Fourteen fixes went in directly, and no finding needed Bruce's judgment,
so this file holds no live block and serves as the applied-directly
record.
The claims touched were checked against the listings: `exercise_4.py`'s
two key orders, `exercise_6.py`'s `True`/`False` pair, and
`exercise_8.py`'s `x, y = other` unpacking.
`tip verify-ch CH=22 ISOLATED=1` passed, 27 of 27.

## Applied directly

- Lines 167-169, hand-wrap: rewrapped the 88-column line in exercise 3's
  closing paragraph. Wording unchanged.
- Lines 217-218, "and" joining different subjects: "`vars()` reads that
  dict, which keeps insertion order, and the two namespaces insert
  `note`" became two sentences.
- Lines 244-245 (hint 5), "and" joining different subjects: "reads the
  fields by name, and a tuple has no `mean` (its `count` is a method),
  so index" became two sentences, the parenthetical folded in: "A tuple
  has no `mean`, and its `count` is a method, so index the tuple
  instead."
- Lines 280-282, hand-wrap: rewrapped the 117-column line in "Read the
  fields by position." Wording unchanged.
- Line 371, "and" hiding a contrast: "The field names serve the reader,
  and `==` ignores them" became "The field names serve the reader. The
  `==` operator ignores them."
- Lines 384-385, restatement: "depends on whether your three numbers
  should be interchangeable with any tuple of the same values, or a
  distinct type whose `==` matches its own class" dropped the "or" half,
  which restated the sentence just before it ("a distinct type, so `==`
  matches it against instances of its own class").
- Line 411, "and" hiding a contrast: "before any instance exists, and here
  the names arrive with the instance" became two sentences.
- Lines 420-421, hand-wrap: rewrapped the 110-column line. Wording
  unchanged.
- Lines 425-426, "and" joining two reasons with different subjects:
  "`SimpleNamespace` compares by contents and defines no hash, and a
  `TypedDict` is a `dict` at runtime" became two sentences.
- Lines 431-433, "and" joining different subjects plus an ambiguous
  "one": "raises a `TypeError`, and the type checker rejects one passed
  to a parameter" became "raises a `TypeError`. The type checker rejects
  a frozen data class passed to a parameter that declares a tuple."
- Lines 436-438, hand-wrap: rewrapped the 135-column line. Wording
  unchanged.
- Line 452, consistency: "at runtime it is a dict" became "a `dict`",
  matching the code span two lines above.
- Lines 541-542, "and" joining different subjects: "type-check as well
  as `Point + Point`, and the unpacking `x, y = other` raises a
  `ValueError`" became two sentences, the second opening "At runtime,"
  to keep the contrast with type-checking that the "and" carried.
- Lines 548-549, overloaded sentence and a figure: "is one more override,
  which is why a `NamedTuple` is the better choice ..., and a record is
  the better choice when that behavior is a surface to defend" became
  two sentences, "So a `NamedTuple` ..." and "a liability" in place of
  "a surface to defend". Close alternative: keep the one sentence and
  change only the figure.

## Considered and declined

- Lines 163-170 (exercise 3), §70 restatement: "One declaration fixing
  both is the clue that they are one problem" echoes the paragraph's
  opening "have one cause". Kept: the opening states the cause, and the
  closer uses the one-line repair as evidence for it, which is the
  exercise's lesson.
- Lines 313-314 (exercise 5), §32/§47 mirrored closer: "A position tells
  the type checker an element's type and tells a reader nothing. A name
  tells both of them what the element is." Kept: both halves are
  accurate, and the pair compresses the whole solution's position-versus-
  name argument into the sentence a reader takes away.
- Lines 288-296 (exercise 5), rule of three: "lose the names", "also
  lose attribute access", "And they lose the type as a name". An
  inventory whose items each get their own consequence, per the
  recurring keep.
- Line 279, "and a `Stats` is a tuple too": a second premise
  sharing the "because", additive, so the "and" stays.
- Lines 408-416 (exercise 7), repetition: "Its keys arrive at runtime",
  "the names arrive with the instance", "every key arrives at runtime".
  Each rules out a different type for the same reason, so the
  repetition is the parallel structure, not a treadmill.
- Lines 468 and 546, watch word "plain": "tuple operations return plain
  tuples" and "`p[:1]` is the plain `(4.0,)`" each contrast with a
  `Point`.
- Line 160, watch word "only": "hashable only when every field is" is
  the ruled-fine "only when" shape.
- Lines 167 and 169, "fixes"/"fixing": the repair sense, which the
  global rule keeps.
