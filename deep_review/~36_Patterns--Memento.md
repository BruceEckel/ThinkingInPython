> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 36_Patterns--Memento (2026-09-25)

This review follows the five prose passes (literal, positive, straighten, cohesion, antecedents), each committed separately on `claude/prep-36`.
This run found nothing that needs your decision, so the file has no live blocks.
Everything had one sensible fix and is listed below.
Probes run for this review: with its `# type: ignore` stripped, `pickle_drift.py`'s `sketch_v1.SketchV1 = SketchV2` draws `invalid-assignment` from `ty` and two errors from mypy, and Pyright accepts it, so the three-checker sentence holds. `ghost_field.py`'s reverse reassignment behaves the same way. `copy.copy()` of a `Sketch` shares its `strokes` list (`is` prints `True`), which backs the new near-miss sentence.

## Applied directly

Corrections, including ones to the prose passes:

- The literal pass wrote "`frozen=True` never runs" about pickle's `__dict__` write. `frozen=True` is a decorator option, not something that runs at load time. The sentence now says `frozen=True` installs a `__setattr__()` that raises `FrozenInstanceError`, and that pickle writes `__dict__` directly.
- The positive pass wrote "the error waits for whatever later reads a field the bytes predate", "This one runs clean with wrong data", and "which closes pickle's security hole". All three were figures standing in for claims, and the first read backwards. They now say that `pickle.loads()` still succeeds and the error comes later, that the deleted field raises nothing and the data is wrong, and that the three libraries never run code from the bytes, so pickle's security risk does not apply.
- The antecedents pass wrote "at the cost [A Snapshot Is Not a Reference] shows", which read as the heading doing the showing. It now reads "and pays the cost described in [A Snapshot Is Not a Reference]".
- `sharing.py` paragraph: "a fresh tuple of `n + 1` pointers" used `n` before defining it. It now reads "On a drawing with `n` strokes, `draw()` builds...".
- `sharing.py` paragraph: "interning makes the identity check print `True` for a copied string too" named a copy that nothing makes. The sentence now gives the reason. Every `"circle"` literal in a module is one object, so `is` would print `True` whether or not `draw()` kept the caller's string. A string built at runtime is its own object, so `True` shows that `after` holds the same string object as `before`.
- Caretaker intro: the straighten pass left a circular pair: the caretaker is opaque because opacity is the point, and `History` works on `Memento` because the classic form has opacity. It now says that the classic form already has that opacity, so `History[S]` holds the classic `Memento` as readily as a `Drawing`.
- `apply()` paragraph: "so both steps happen at every call site" was wrong, because the steps happen inside `apply()`. It now reads "so no call site can build a state and forget to record it". "`do()` stays public for a state that other code builds" now names the case: "a state built some other way than by editing the present, such as the `Sketch` mementos that `history_classic.py` passes to it".
- Schema migrations: "A *schema migration* is the disciplined version of this drift" called the remedy a kind of drift. It now reads "makes the drift deliberate: a versioned step...".
- "Snapshots in the Wild": "the *Memento* pattern applied to a whole file tree" was followed at once by "snapshot of your whole tree". The first sentence is now "Version control applies the *Memento* pattern to files."

Teaching:

- Classic Memento intro: added the near-miss a reader writes first, `copy.copy(sketch)` as `save()`. It copies the `Sketch` but not its list, so it reproduces `aliased_snapshot.py`'s alias one level down.

Solutions:

- Exercise 4 asks the reader to "write the test that exposes the corruption", and the solution never wrote one. It now adds `test_memento_is_a_snapshot()`, which compares `list(checkpoint.strokes)` with `["a"]`. It also notes that the chapter's second and third tests fail on list versus tuple alone, so they would fail even for a `Memento` holding a *copied* list. The test is a fragment, like the solution's buggy `Sketch`, and passes against the chapter's correct `Sketch`.

## Considered and declined

- The coupling-panel caption (the Markdown and `tools/coupling_panels.py`'s `CAPTIONS` and panel `alt`) still matches the listings: `Sketch` names `Memento` in `save()`/`restore()`, and `History[S]` annotates only `S`. Its "it" refers to `History`, and the clause before it makes that clear. It was left unchanged, so neither copy needed an edit.
- `sketch_v1.py`/`sketch_v2.py`, and Solutions' `drawing_v1.py`/`DrawingV2`, keep `@dataclass(frozen=True)`. The chapter's ghost-field and drift arguments read `__dict__`, and CLAUDE.md's `@record` section names these listings.
- `Sketch` and `History` keep their hand-written `__init__()` methods, a standing exemption in `deep_review_db.md`.
- "the *Command* variation that [Function Objects] mentions": chapter 28 does only mention it in prose and leaves the `Protocol` to its exercise 1, so "mentions" is accurate.
- The growth-cost paragraph names "the `History` class in `history.py`" a section before that listing appears. The alternative was to move `growth_cost.py` after the caretaker section, which would split it from `sharing.py`, the listing it qualifies. A forward reference by file name costs less.
