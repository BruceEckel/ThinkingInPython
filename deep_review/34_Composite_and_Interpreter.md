When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/34_Composite_and_Interpreter.md`
in the clean-slate sweep. The mechanical layer is sound: all `#:` markers
validate, `ty`, ruff, and pytest are clean on
`build/examples/34_Composite_and_Interpreter` (19 tests), and the runnable
scripts run. Every checker and runtime claim was probed individually on the
pinned toolchain and all hold: `"a" + x` at runtime builds
`Add(left=Num(value='a'), right=Var(name='x'))` with no complaint, while
`ty` rejects the same line in visible source (`unsupported-operator`),
matching the reflected-methods paragraph and exercise 6; `x and y` returns
`y` and `not x` returns a `bool`, matching the boolean-operator paragraph;
an `ast` probe confirms `a > 1 & b > 2` parses `1 & b` first, matching the
Pandas-parentheses note; the default recursion limit is 1000 ("roughly a
thousand frames"); `t"{a}{b}"` iterates as two `Interpolation` objects and
no strings while `.strings` keeps `('', '', '')`, and `Interpolation`
carries both `.value` and `.expression`, all matching the template section
and all taught first in chapter 2's t-strings section. Chapter 21's updated
taxonomy (Composite under Structural, Interpreter under Behavioral, the
pair "one recursive-data structure") stays consistent with this chapter:
the "Composite is the data / Interpreter is the behavior" close it leans on
is intact. Incoming links from chapters 02, 21, 32, 33, 37, 39, and 44 all
target anchors that still exist, `resources/images/composite_tree.svg`
exists, and `Solutions/34_Composite_and_Interpreter.md` covers all nine
exercises. No finding needs a decision, so this file has no live blocks;
everything found was either applied directly or recorded below as
considered and declined.

## Applied directly

- "A Composite of Data Classes": the varargs-to-tuple note credited the
  call-shape change with making the tree immutable, but the classic
  version's `*entries` also stored a tuple. It now gives the real reason
  for the shape change (`@dataclass` generates `__init__()` from the field
  declarations, and a field is one parameter) and lets the tuple-plus-
  `frozen` paragraph below carry the immutability argument.
- Same section: "In Python, you can define the node types..." is now the
  imperative "define...", matching the two imperatives that follow it.
- Interpreter section: "annotate `evaluate()` with `Operators` and
  `assert_never()` stops working" is now the conditional "if you annotate
  `evaluate()` with `Operators` instead, ..." (imperative-plus-consequence
  rule).
- "`Add` and `Mul` hold expressions themselves" is now "hold other
  expressions", matching the figure caption and dropping the flourish.
- "before the interpreter ever runs" dropped "ever".
- Evaluation section: "The `/` makes the tree positional-only" is now
  "makes `e` positional-only"; positional-onlyness is a property of the
  parameter, not of the tree passed to it.
- Exercise 8: "Raising `sys.setrecursionlimit()` is the other escape" is
  now "Raising the limit with `sys.setrecursionlimit()`..."; the call
  raises the limit, not the function.
- `Solutions/34_Composite_and_Interpreter.md`: exercise 7's listing was
  the only one of the nine with no `# exercise_7.py` marker, so it alone
  escaped extraction and `ty`/ruff coverage; the marker is added and the
  extracted file checks clean.
- Solutions exercises 3 and 4: `evaluate()` (ex. 3) and `to_infix()`
  (ex. 4) are the functions their exercises ask for, yet their `match`
  blocks lacked the `case _: assert_never(...)` the chapter teaches and
  the other solution walkers carry; both now have it (gates re-run clean).
  Exercise 5's support copies of `to_infix()`/`simplify()` were left
  trimmed; there the walker under discussion, `derivative()`, already
  carries `assert_never()`.
- Ran `make reflow CH=34` over the edited prose.

## Considered and declined

- The heading "A Template Is a Tree" while the section itself calls the
  grammar "flat rather than nested": the tension is negotiated in the
  prose ("the walk is a loop instead of a recursion, but everything else
  about it is this chapter's shape"), and chapter 2 links to the explicit
  `#a-template-is-a-tree` anchor, so a retitle costs more than it
  clarifies.
- The three-walker paragraph before "A Template Is a Tree" stays where it
  is, per the standing exemption in `deep_review_db.md`.
- "An unbound variable raises `KeyError`" keeps its bare form: both
  "raises a `KeyError`" and "raises `KeyError`" are established book-wide
  (chapters 15/47 vs. 17/27), so there is no single convention to enforce.
- "Match over a closed set, use polymorphism for an open one." stays: a
  two-imperative sequence the style rules allow, and the section's closing
  beat.
- `simplify.py`'s inline comment "# Share the unchanged subtree" stays:
  existing listing comments are left alone per house style, and the prose
  below explains the `is` guard anyway.
