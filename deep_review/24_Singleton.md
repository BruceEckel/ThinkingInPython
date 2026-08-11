When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/24_Singleton.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers
validate, `ty`, ruff, and pytest are clean on
`build/examples/24_Singleton`, and every script runs. The concurrency
claims were probed directly on this machine. The race demo's `#: True`
is stable (10 of 10 standalone runs); the run produces eight distinct
objects, matching "ran that constructor eight times"; the cached
survivor is the last finisher, matching "the cache keeps whichever
finished last" (instrumented with a finish-order list, confirmed twice);
twenty no-sleep trials produced zero duplicates, matching "showed no
duplicates across twenty trials"; and a lock wrapping only the cached
function's body still yields eight objects, confirming note 3 and
exercise 5's premise. The privacy section's claims also held under
probe: the nested-class annotation runs clean, `ty` reports
`unresolved-reference` on it, and `inspect.get_annotations()` raises a
`NameError`; `OnlyOne.__OnlyOne` from outside is a runtime
`AttributeError` that `ty` does not flag, so "not at type-checking time"
is right; the eager `instance: ClassVar[__OnlyOne] = __OnlyOne()`
variant works in the class body while the qualified form raises a
`NameError`, as the parenthetical says. `ty`'s `invalid-base`
diagnostic for `class Sub(Registry)` carries the info line "Definition
of class `Sub` will raise `TypeError` at runtime", so the prose sentence
about the checker's complaint matches the tool verbatim. The Martelli
link resolves and the page says what the chapter says it says. The
chapter-17 cross-reference is consistent with that chapter's metaclass
singleton (its `__call__()` skips `__init__()` on later constructions),
and the `singleton` decorator class's hand-written `__init__` matches
chapter 14's `repeat` class, so it is house precedent, not drift. One
factual error surfaced, in the metaclass comparison paragraph (first
entry below). No live blocks this run: every finding had one defensible
answer.

## Applied directly

- Metaclass paragraph: "A metaclass that replaces `__new__()` instead"
  is now "A class that overrides `__new__()` instead, as
  `singleton_class_variable.py` does". A metaclass overriding
  `__new__()` intercepts class creation, not instance creation; the
  behavior described (`__init__()` rerunning, last call's arguments
  winning) belongs to the chapter's own `__new__()` form, and the fix
  names the listing that shows it.
- Module section: added a closing paragraph on the second cache key.
  `sys.modules` is keyed by module name and the launched file runs as
  `__main__`, so importing that same file by name builds a second
  module object with its own `settings` (probe-verified: `settings is
  app.settings` is `False`). Ends with the advice "Keep singleton
  state in a module you import, not in the script you run." Without
  this, "Python imports each module once" reads as unconditional, and
  the entry-script case is the classic way a module singleton silently
  doubles.
- Nesting paragraph: `inspect.get_annotations(eval_str=True)` is now
  `inspect.get_annotations()`. Probed on the pinned 3.15: the default
  call raises the same `NameError`, since lazy annotations evaluate on
  read; `eval_str=True` implied string annotations were involved.
- Decorator section: moved "Applying `@singleton` to `Registry` runs
  `Registry = singleton(Registry)`. The name `Registry` now refers to
  the decorated instance rather than to the class." from third
  paragraph to first, ahead of the "You might wonder" mechanism
  paragraph that depends on it, and dropped the now-redundant "Calling
  `Registry(...)` returns the cached instance." (already said two
  sentences up).
- "only one `settings` dict is ever built" dropped "ever".
- Note 3: "The check must happen inside the lock" is now "must run
  inside the lock" (watch-list "happen"; "run" is the literal verb).
- Locked-listing prose: "raises `UnboundLocalError`" is now "raises an
  `UnboundLocalError`" (house rule: article before a named exception).
- Ran `make reflow CH=24` over the edited prose.

## Considered and declined

- Note 2's "which the import system builds exactly once" keeps
  "exactly": it draws the real contrast with the racing factory, which
  can build more than once.
- The double-checked-locking discussion stays prose-only, with no
  listing: the chapter argues against using it, and a listing would
  dignify the form the paragraph exists to wave off.
- The `singleton` decorator class keeps its hand-written `__init__`
  rather than becoming a dataclass: chapter 14's `repeat` class
  decorator uses the same shape, so this is the book's established
  style for decorator classes.
- "A singleton is only single inside the interpreter that holds it"
  keeps "only": the restriction is the sentence's point.
- "Which Should You Use?" keeps its question form: the heading rule
  bars "You Can/Must" clauses, not questions, and the section is a
  decision list answering that question.
