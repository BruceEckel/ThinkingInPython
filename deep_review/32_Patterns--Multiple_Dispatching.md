> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Deep review of chapter 32, run after the `literal`, `positive`, `straighten`,
`cohesion`, and `antecedents` passes (one commit each on `claude/prep-32`).
Every claim about `ty`, Pyright, and mypy in the `-> Meters` paragraph was
re-probed on this branch (`Meters | NotImplementedType` draws
`unresolved-attribute` from `ty`; Pyright and mypy accept it), and every
listing's markers match. The review found one real logic error, the
`DampPaper` asymmetry below, which it fixed along with its twin in
exercise 9. No finding needed a decision only Bruce can make, so this file
holds no live blocks.

## Applied directly

- `paper_scissors_rock_subclass.py`: `DampPaper` overrode only `compete()`,
  so `DampPaper().compete(Rock())` drew while `Rock().compete(DampPaper())`
  still reported the rock losing, through the inherited `Paper.eval_rock()`.
  Added a `DampPaper.eval_rock()` override and a `Rock().compete(DampPaper())`
  line with its `#: draw` marker. The prose now says a combination has two
  sides, one per order of the duel, and names the method behind each side.
- The paragraph after that listing said the table version's change "edits
  one cell ... and every `Item` sees the new cell". A subclass gets no rows
  from `Paper` at all under exact matching, so the paragraph now says
  `DampPaper` needs seven rows of its own, five of them copies of `Paper`'s.
- Exercise 9 and Solutions 32 exercise 9 had the same asymmetry: wet paper
  drew against a rock only when the paper called `compete()`. The exercise
  now asks for both the `(Paper, Rock)` and `(Rock, Paper)` cells to read
  `wet` ("seven unchanged cells", not eight); the solution gains
  `rock_vs_paper()`, a `Rock <--> WetPaper : draw` line, and matching prose.
  Its reference to `DampPaper` now names both overrides.
- "The lookup shares two properties with the table-driven state machine ...
  a missing pair raises a `KeyError`": chapter 31's engine uses `.get()` and
  raises `NoTransition`, not `KeyError`. The shared property is now stated
  as failing at first use, with each chapter's exception named.
- The `Any` paragraph said the only alternative to `Any` was a `Protocol`.
  Declaring the four methods on `Item` as abstract methods is the other one,
  and the parallel the paragraph then draws with the table version's `Item`
  depends on it. Now names both.
- Exercise 10: "Modify Exercise 8" lowercased to match the chapter's other
  exercise references.
- "Every arithmetic and bitwise operator has a reflected form" became
  "Every binary ...": unary operators have none.
- "It works, and it combines the drawbacks of both" (the `isinstance()`
  ladder): the sentences that follow list only the method version's cost
  and the loss of dispatch, so it now says "it keeps the method version's
  cost without its benefit".
- "Methods or Table" moved from an H3 under "One Type or Many" to an H2. It
  compares the chapter's two designs and says nothing about one type versus
  many. The anchor is unchanged, and no other file links to it.

## Considered and declined

- The coupling-panel caption ("`Paper`, `Scissors`, and `Rock` each define
  an eval method for every item and call one through `Any`, so a fourth item
  edits all three") still matches the listing, so `tools/coupling_panels.py`
  was left alone.
- `DampPaper.compete()` uses one `isinstance()` test, a few paragraphs after
  the chapter criticizes the `isinstance()` ladder. The ladder paragraph is
  about a test in every class for every opponent. One override in one
  subclass is a different thing, and Solutions 32 exercise 9 already makes
  that distinction for its cells.
- The `singledispatchmethod` section links forward to chapter 41's catalog
  entry. That link points to a reference, not to a prerequisite. The section
  teaches everything its listing needs.
