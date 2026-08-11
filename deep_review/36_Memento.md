When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/36_Memento.md` in the clean-slate
sweep. The mechanical layer is sound: all `#:` markers validate, `ty`, ruff,
and pytest are clean on `build/examples/36_Memento` (9 tests), and all twelve
runnable scripts run. Claims probed individually on the pinned toolchain and
holding: `NewType("Memento", tuple[str, ...])` constructs and vanishes at
runtime (the value is a plain indexable tuple); `copy.replace()` accepts a
`NamedTuple` and a `datetime`; `pickle.loads()` runs neither `__init__()` nor
`__post_init__()` (probed with a recording `__post_init__()`); a plain
defaulted field "appears" after loading old bytes via class-attribute
fallback while a `default_factory` field raises an `AttributeError`, which is
word for word what the exercise-7 solution teaches; the ghost-field object is
`==` to and hashes the same as one built without the field (frozen dataclass
`__eq__`/`__hash__` read declared fields only); and `"".join([...])` is not
constant-folded, so the `sharing.py` identity markers are stable. The
small-int-cache trap recorded against this chapter in project memory no
longer applies: the identity demo now uses a runtime-joined string, not an
int. Outgoing anchors into 20, 35, 08, 28, and 12 resolve
(`heading_links.py` clean), `resources/images/memento_history.svg` exists,
`ignore` is taught in chapter 15 before this use, chapter 28 does discuss
commands that carry `undo()` (so "the Command variation mentioned in
Function Objects" is accurate), and chapter 12's forward pointer ("which
Memento revisits") is delivered by the pickle-drift section. Inbound links
from 12, 21, and 39 carry no anchors, so nothing here can break them.
`Solutions/36_Memento.md` covers all seven exercises, its solutions do what
their exercises ask, and the exercise-4 claim that all three tests fail
checks out by tracing the shared list through each test. One factual error
was found and fixed (first entry below). No finding needs a decision, so
this file has no live blocks.

## Applied directly

- Restoring Part of a State: `partial_restore.py` contradicted its own
  prose. "Producing a state that never existed before" was false: the
  checkpoint sat directly before the rename, so the partial restore's
  result, `(Goose, ("circle",))`, was value-equal to the state right after
  the rename. The listing now draws `beak` between the checkpoint and the
  rename, so the restored state genuinely never existed; markers updated
  and re-validated.
- Pickle-drift explanation, teaching addition (misconception lens): the
  chapter teaches earlier that `frozen=True` fails loudly on assignment,
  then shows pickle silently filling fields. Added the mechanism: the
  fields go straight into the object's `__dict__`, and freezing guards
  attribute assignment, which pickle does not perform.
- "`NewType(...)` answers the checker but nothing else" is now "answers
  only the checker": the next sentence spells the exclusion out, the
  giveaway for dropping the tag.
- "the whole trick immutability buys" is now "makes possible"
  (watch-list "buy").
- "whatever state type a `History` happens to hold" is now "holds", and
  "before the load happens" is now "before the load" (watch-list
  "happen").
- "which one of the exercises explores" is now "which exercise 3
  explores" (named reference over a vague one).
- "The dump of `blob` runs" is now "The dump that builds `blob` runs";
  `blob` is the dump's result, not its argument.
- Added the missing comma in "flags that reassignment as unsound, so it
  carries a `# type: ignore`".
- "`pickle.loads()` never calls `__init__`" and "skips `__post_init__`"
  now write `__init__()` and `__post_init__()` (function refs use empty
  parens).
- "`title` is simply absent" dropped "simply".
- "so `repr()` never shows it and `==` never compares it" is now "so
  `repr()` omits it and `==` ignores it" (double "never", and the verbs
  state what the generated methods do).
- Intro: "without ever looking inside" dropped "ever".
- Ran `make reflow CH=36` over the edited prose (one paragraph).

## Considered and declined

- `Sketch`'s hand-written `__init__()` (the house-style sweep's usual
  hit): the class is the chapter's mutable classic originator, contrasted
  three listings later with the frozen dataclass `Drawing`; making the
  originator a dataclass too would blur the contrast the chapter builds,
  and per-instance state initialized in `__init__()` is the house kind
  for it.
- `History`'s hand-written `__init__()`: the constructor renames what it
  stores (`initial` in, `_present` kept), which a generated `__init__()`
  cannot express, the same justification chapter 31's `StateMachine`
  carries.
- "The tuple inside was already immutable, but the attribute was not"
  keeps "already": it draws the real contrast (immutable with or without
  `frozen=True`), which is the keep case in the style rules.
- "under a different name so a reader never has to ask which one a
  listing means" has two watch-list words, but every rewrite tried read
  worse; the sentence is clear as written.
- The chapter has no separately titled conclusion: "Snapshots in the
  Wild" closes it, is titled for its content, and adds the recognition
  insight ("whenever you see rewind, rollback, or restore"); not a
  missing-summary defect.
- The explicit `{#restoring-part-of-a-state}` anchor duplicates the
  auto-slug; harmless, and it protects the inbound-link surface if the
  heading ever changes, so it stays.
- The exercise-6 solution's demo has the same value-collision the chapter
  listing had (its restored state equals its post-rename state), but its
  prose makes no never-existed claim, so nothing there is wrong; left
  unchanged.
