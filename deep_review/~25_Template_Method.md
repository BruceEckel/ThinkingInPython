[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/25_Template_Method.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers
validate, `ty`, ruff, and pytest are clean on
`build/examples/25_Template_Method`, and all three scripts run. Probes
confirmed the chapter's checkable claims on the pinned toolchain: `ty`
rejects an override of the `@final` `run()` with
`override-of-final-method`, and flags a misspelled `customise1()` under
`@override` with `invalid-explicit-override`, so both checker claims
hold. The `__init_subclass__()` recipe in prose (raise when
`"run" in cls.__dict__`) was probed directly: it raises a `TypeError`
while the offending subclass's body executes and leaves a compliant
subclass untouched. `TestCase.setUp()` and `tearDown()` are do-nothing
methods whose stdlib docstrings call each a "Hook method", which backs
the new hook sentence below. Every cross-reference points where the
chapter says: chapter 17's [Making a Class Final] shows both `@final`
and the `__init_subclass__()` runtime refusal, chapter 20's
[Polymorphism Without Inheritance] teaches `ABC`/`@abstractmethod` with
the instantiation refusal, and chapter 28's Strategy anchor exists.
The inbound anchors from chapters 31 and 39
(`#dont-start-the-engine-in-the-constructor`, `#the-fixed-algorithm`)
are intact, and `deep_review_db.md` carries nothing binding for this
chapter. No live blocks this run: every finding had one defensible
answer.

## Applied directly

- Hooks paragraph: after "An optional step like this is a *hook*",
  added the tie-back to the opening example: `TestCase` supplies
  do-nothing `setUp()` and `tearDown()`, so a test class that needs no
  setup skips them. The intro ("You subclass `TestCase` and supply
  `setUp()`...") otherwise reads as if all three are mandatory, and the
  term *hook* arrived without touching the example that motivated it.
  Worded without "fixture", which chapter 11 defines as the pytest
  construct.
- `@final` caution: "At runtime Python only records the mark and
  enforces nothing" dropped "only"; "and enforces nothing" carries the
  restriction.
- `premature_engine.py`: the comment "...before this line has happened"
  is now "...before this line runs", pairing with its partner comment
  "engine runs now...". (`Examples/` resynced.)
- Function-form trade-off: "the base already supplies the `...`
  default" dropped "already"; "the function form has to give" is now
  "must give".
- Conclusion: "Choose by asking whom you are protecting the algorithm
  against" fronted the stranded preposition: "asking against whom you
  are protecting the algorithm."
- Ran `make reflow CH=25` over the edited prose (no further changes
  needed).

## Considered and declined

- The heading "What Actually Fixes the Algorithm" keeps its watch-list
  "Actually": it is contrastive, correcting the naive answer that the
  decorator does the fixing. Retitle candidates ("What Holds the
  Algorithm Fixed") lose the correction, and no inbound link names
  this anchor, so a retitle stays cheap if wanted later.
- "you never call that sequence yourself" (intro) keeps "never": it
  carries the inversion-of-control point the chapter is built on.
- The term *hook* stays despite the watch list: it is the standard name
  (GoF, and `unittest`'s own docstrings), introduced in italics as a
  new term.
- "this chapter has shown four of them" (conclusion): the
  `__init_subclass__()` mechanism appears as a one-line prose recipe
  rather than a listing, so "shown" is slightly loose, but a listing
  here would duplicate chapter 17's `final_runtime.py` for one changed
  condition. Left as written.
- "overrides only the steps it cares about": "cares about" sits
  mid-clause with its object fronted in the relative clause, not
  sentence-final stranding. Left.
