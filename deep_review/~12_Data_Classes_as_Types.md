[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/12_Data_Classes_as_Types.md` in
the clean-slate sweep. The mechanical layer is sound: all `#:` markers
validate, ruff and `ty` (0.0.70) are clean on
`build/examples/12_Data_Classes_as_Types`, the chapter's 23 tests pass, and
all 30 scripts run. Claims were re-verified on the pinned toolchain: the
quoted `ValueError` ("mutable default <class 'list'> for field months is
not allowed: use default_factory") and `TypeError` ("non-default argument
'b' follows default argument 'a'") match the interpreter verbatim; a probe
confirmed that `ty` reports `invalid-assignment` for
`field(default_factory=dict[int, int])` on a `dict[str, str]` field, so the
"type error before the program runs" claim holds, while the bare-`set`
factory in `factory_checking.py` still passes `ty`, confirming the "loose
enough that a checker accepts it" claim. The PyCon talk link resolves to
the named video. Exercise 6 stays consistent with ty 0.0.70's new
ClassVar/frozen strictness: the working increment goes through the class
name, and the sweep's earlier commit already gave the Solutions' `Wrong`
variant its `# type: ignore`. The review inherited uncommitted edits from
an interrupted earlier pass; all held up under re-verification and are
recorded below with the rest. No findings met the bar for a live block.

## Applied directly

- Intro: "freeze it so it can never change" is now "so it cannot change",
  and "never has to check it again" is now "need not check it again"
  (watch-list "never"/"has to").
- Stars discussion: "then raises, and the object goes on holding" now
  names the exception, "then raises `TypeFailure`" (raise needs an
  object).
- DbC paragraph: "every mutating method has to remember" is now "must
  remember".
- `display_messenger_class.py` prose: "only `depth` appears as an
  attribute because it has an initialization value" now scopes the claim,
  "of the three fields only `depth` appears as an attribute".
- Immutability: after the hashable-as-a-bonus sentence, added "The
  mutability that cost `Messenger` its `__hash__` is gone, so
  `@dataclass` generates one from the fields", closing the loop with the
  `__hash__ = None` display two sections earlier.
- "A Type Is a Set of Values": "every `Stars` is already good" is now
  "every `Stars` is legal", echoing "If you are holding a `Stars`, it is
  legal".
- Normalize-or-refuse paragraph: "Which one you want depends on the
  type" is now "Which to choose depends on the type".
- `C` section: the claim that `@dataclass` reads annotations "through
  `dataclasses.fields()`" had the mechanism backwards; now `@dataclass`
  reads the annotations and `dataclasses.fields()` reports the field
  list it recorded.
- `A` section: "the declaration never gets fulfilled" is now "goes
  unfulfilled".
- `D` section: "does not, by itself, create anything" is now "on its
  own" (itself rule).
- Enum aliasing paragraph: cut "is what" from "which is what `of()`
  relies on".
- NamedTuple section: the error arrives while Python is still
  *executing* the `class` statement, not "reading" it (parsing has
  finished; class creation is what fails).
- After `kw_only_config.py`, added the `kw_only=True` vs `_: KW_ONLY`
  contrast: the decorator argument makes every field keyword-only, the
  marker limits it to the fields after it, leaving `source` positional.
- `asdict()` paragraph: "Changing the result never reaches back into the
  original" is now "cannot reach back" (states the guarantee).
- `replace_vs_copy.py` prose: "a number that no check ever saw" dropped
  "ever".
- JSON encoder prose: "`is_dataclass()` answers `True` for a data class
  itself as well as for an instance" is now "for the class object as
  well as for an instance".
- `json_round_trip.py` and `json_encoder.py`: continuation lines
  realigned with their opening parentheses (synced to `Examples/`).
- Ran `make reflow CH=12` over the edited prose (one paragraph
  repacked).

## Considered and declined

- Moving "Comparing Ordinary Classes and Data Classes" after the two
  Enum sections, so the Person-to-BirthDate composition arc runs
  unbroken: declined because "Defaults Built Fresh" opens directly on
  the preceding listing's `Months`, and the comparison section is
  framed as opening up the tool right after its first real use
  (`stars.py`, `person.py`); both orders are defensible and the current
  one costs the reader less back-reference.
- `month_dataclass.py` uses `field(default_factory=make_months)` one
  section before "Defaults Built Fresh" explains it, but the sentence
  under the listing flags the construct and the explanation is
  adjacent, so no reordering.
- No exercise covers the Inheritance section; the chapter's main claims
  are covered by the seven exercises, and an exercise there would
  restate `dataclass_super_init.py` nearly verbatim.
- Hand-written `__init__()`s in `stars_class.py` (the counterexample),
  `Connection` (a non-data-class base is the point), and `Color`
  (packed storage, no per-field attributes for `dataclasses.replace()`
  to find) are all explained deviations from house style.
- "is legal and does what it looks like" (subscripted-factory
  paragraph) left as in-voice shorthand.
- "No other code repeats the check, because it cannot fail" left: the
  antecedent is the check on a value that already passed construction.
