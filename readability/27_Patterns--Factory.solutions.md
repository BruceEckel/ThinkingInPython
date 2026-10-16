> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability review of `Solutions/27_Patterns--Factory/README.md`,
2026-10-16.
The prose carried few AI tells. Most findings were "and" joins between
clauses with different subjects that hid a consequence or a contrast,
plus three sentences whose claim did not match the listing or the page
(a colon pointing at the wrong file, `pytest` "results below" that the
page describes rather than shows, and `unregistered()` said to print
what it returns). Twenty-two fixes went in directly, and no finding
needed Bruce's judgment, so this file holds no live block and serves as
the applied-directly record.
The claims touched were checked against the listings: the expanded
`eval()` string in `exercise_8.py`, the `[]` that `registry_demo.py`
prints without its import, `unregistered()`'s `return sorted(...)`, and
the chapter's `type Kind = Literal["goblin", "troll"]`.
`tip verify-ch CH=27 ISOLATED=1` passed, 27 of 27.

## Applied directly

Line numbers are in the edited file.

- Lines 85-87, consequence hidden in "and": "asks for a `"Triangle"` that
  `Shape.factory()` cannot build, and `Shape.factory()` raises ..." ->
  "asks for a `"Triangle"`. `Shape.factory()` cannot build one and
  raises ...".
- Lines 139-141, colon pointing at the wrong thing: "Here, `exercise_2.py`
  shows the new shape alone. In the chapter file its entry joins ...
  joins the demo's list:" put the colon after the chapter-file sentence,
  above a listing that shows `exercise_2.py` alone. Now the chapter-file
  sentence comes first and "`exercise_2.py` shows the new shape alone:"
  introduces the listing. "its entry" became "the `_Triangle` entry", and
  the filler "Here," went.
- Lines 345-346, different-subject "and": "A third concrete factory joins
  ..., and `GameEnvironment` stays as it was" -> "`GameEnvironment` stays
  as it was while a third concrete factory joins ...".
- Line 348, a file that "asks for" a factory: "`abstract_factory_protocol.py`
  asks for the same factory without a base class" -> "In
  `abstract_factory_protocol.py` the same factory declares no base class",
  matching the listing's `# Declares no base class`.
- Lines 413-414, different-subject "and": "reports the call ..., and the
  diagnostic names the missing method" -> two sentences, "Its diagnostic
  names the missing method."
- Lines 676-677, treadmill: "The rejection is therefore atomic. The
  constructor call ends in the exception before ..." -> one sentence, the
  colon delivering what "atomic" means ("that is" fits).
- Line 691, imprecise restatement cut: "The window stays open for as long
  as the caller keeps adding toppings." The window stays open until
  `build()` runs, whether or not toppings keep arriving, and the sentence
  before it already says "between the fifth `.topping()` call and that
  `build()` call". The close alternative was "The window stays open until
  `build()` runs."
- Lines 760-761, consequence hidden in "and": "deletes the import, and the
  demo then prints `[]` ..." -> two sentences.
- Line 825, consequence hidden in "and": "stays empty, and every `make()`
  call raises" -> "stays empty, so every `make()` call raises".
- Line 838, contrast hidden in "and": "imports `Shape` and `make` from
  `registry`, and every subclass now lives in `extra_shapes`" -> "..., but
  every subclass now lives in `extra_shapes`".
- Line 956, pointer to nothing: "The `pytest` results below come from ..."
  -> "The `pytest` runs described next use ...", since the page describes
  the failures in prose and shows no `pytest` output.
- Lines 1123-1124, different-subject "and": "raises a `KeyError` naming
  the string, and nothing evaluates that string" -> "... that names the
  string. Nothing evaluates the string."
- Line 1127, one concept per paragraph: the type checker's view of
  `eval()` and the verdict "the table is the only acceptable version"
  now sit in separate paragraphs.
- Lines 1195-1198, two different-subject "and"s: "builds a generator and
  nothing iterates over it" -> "builds a generator and discards it, so
  its body never runs"; "..., and the demo draws no `Oval`" -> its own
  sentence.
- Lines 1275-1276, reason chained with "and": "..., and `names()` requires
  that type" -> "..., the type `names()` requires". The paragraph's stray
  hand-wrap after "keeps the" went with it.
- Lines 1409-1410, different-subject "and": "accepts `Hexagon` wherever
  code takes a `Shape`, and both the checker and ruff accept the module"
  -> two sentences.
- Line 1420, precision: "Calling `unregistered(globals())` ... prints the
  name of each class" -> "returns the names of the classes", since
  `unregistered()` returns a sorted list and the demo's `print()` does
  the printing.
- Lines 1425-1426, contrast hidden in "and": "rejects a decorated class
  that does not fit, and `unregistered()` reports ..." -> two sentences.
- Lines 1431-1432, different-subject "and": "raises a `TypeError`, and
  `isinstance()` on an instance is the fallback" -> "... raises a
  `TypeError`. `isinstance()` on an instance is then the fallback."
- Line 1554, reason chained with "and": "`Builder` is a `Callable`, and a
  `Callable` declares ..." -> two sentences.
- Lines 1562-1567, an "and" whose second clause could read as outside the
  "because", and a different-subject "and": "because it receives a class,
  and `type[S]` has a `__name__`" -> "because it receives a class, a
  `type[S]`, which has a `__name__`"; "`ty` rejects it, and the book checks
  with `ty`" -> "`ty`, the checker the book uses, rejects it."
- Lines 1574-1577, different-subject "and" and a reason stranded after its
  claim: "..., and `PROTOTYPES` needs no edit. The key type widens ... for
  the same reason. An open table cannot list its names in advance." ->
  "... and leave `PROTOTYPES` as it was. The key type widens from the
  chapter's `Kind` to `str`, because an open table cannot list its names
  in advance."

## Considered and declined

- The bold step labels ("**Ask the factory for each product.**" and the
  rest), §15: a Solutions convention used across the README files.
- Line 828, §10 rule of three: "The registry is correct, the
  subclass is correct, and the program still fails" echoes the chapter's
  own triple at its plugin-failure passage, which the chapter review kept
  as deliberate rhythm.
- Line 1002, watch word `worth`: "The second assertion is the one worth
  writing." It weighs the effort of writing a test against what the test
  catches, which the next two sentences state (the `worth` keep in
  `readability_db.md`).
- Line 1129, watch word `only`: "the table is the only acceptable version
  of the two" is the ruled-fine "the only X" shape, and the restriction
  is the claim.
- Lines 970, 1306, 1430, 1587, `only when`: ruled-fine shape, each a real
  restriction ("only when something mutates them in place", "only when it
  is `@runtime_checkable`", "works only when every member is a method",
  "runs only when something imports its module").
- Line 341, negative "does not name `Kitty`, `Warrior`, `Puzzle`, or
  `Weapon`": half of a real contrast with the next sentence, "It calls
  `make_character()` and `make_obstacle()`".
- Lines 1199, 859, `never`/"Neither ... nor": "Neither the type checker
  nor ruff reports the dropped keyword" and "The demo never uses the name
  `extra_shapes`" state the failure itself, the watch-list-absolute keep.
- Lines 404-418, the exercise 3 closing paragraph holds both halves
  (abstract base class and Protocol). One topic, the contrast named in
  its first sentence, so the halves stay together.
- Mixed wrapping (some paragraphs one sentence per line, some wrapped
  near 70 columns): rewrapping paragraphs whose wording did not change
  would add churn, so only edited lines were rewrapped.
