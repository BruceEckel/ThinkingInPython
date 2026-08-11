[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/06_Modules_and_Packages.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers validate,
ruff and `ty` are clean on `build/examples/06_Modules_and_Packages`, and all
23 runnable scripts pass (`a_package/module4.py` is correctly in `norun.txt`).
The technical claims were re-verified on the pinned 3.15.0b4: the `lazy`
syntax restrictions (function/class/`try` bodies, `lazy from ... import *`,
`lazy from __future__` are all `SyntaxError`s), `sys.lazy_modules` holding
currently-deferred names and dropping one once it loads, `-P` suppressing a
local `random.py` shadow, `importlib.import_module("my-mod")` loading a
hyphenated file, the exact circular-import and relative-import-as-script
error messages, the unloaded-submodule `AttributeError` text, and
`python -m a_package.module4` running from the examples directory. The one
real error found: the chapter documented three values for
`-X lazy_imports`/`PYTHON_LAZY_IMPORTS`, but CPython removed the `none` mode
before the 3.15 release (gh-149321, merged May 2026 and backported to the
3.15 branch; the pinned interpreter rejects it with "expected 'all' or
'normal'"). PEP 810's text still lists all three, which is why the removal is
worth a sentence in the chapter rather than silence. The inbound anchors
other chapters use (#lazy-imports from 27, #what-a-module-exports from 29,
#file-names from the Solutions) are untouched. The exercises line up with
`Solutions/06_Modules_and_Packages.md`, whose exercise-5 error messages I
re-verified verbatim.

## Applied directly

- Lazy imports: replaced the three-value mode description with the two that
  exist (`normal`, `all`), noted that `all` defers only what the keyword
  could have marked (a `try`-block import stays eager, verified), and added
  one sentence that PEP 810's `none` off switch was removed before the 3.15
  release, since the linked PEP still describes it.
- Lazy imports: merged the duplicated side-effect warning. The paragraph
  after `lazy_noisy.py` and the chapter-closing paragraph both said "an
  import used only for its side effect never loads under `lazy`"; the first
  occurrence is cut and its Factory link moved into the fuller closing
  paragraph, which keeps the silent-failure consequence and the `all`
  warning together.
- After `no_qualification.py`: added "This listing, `from_packages.py`, and
  `using_packages.py` print the same loading messages: `from` does not load
  less..." The markers demonstrate it, but the prose never stated the
  classic misconception that `from module import name` loads less than the
  whole module.
- Circular imports: "the second one imports a partially initialized module
  and fails" became "a `from` import in the second finds a partially
  initialized module and fails". A plain `import` of a partially
  initialized module succeeds (the failure surfaces later, at attribute
  use); the quoted `cannot import name` message is the `from` form's.
- "This particular `if` condition is only true when" → "is true only when"
  (misplaced `only`).
- "a running program never notices an edit to a module it already imported"
  → "does not notice an edit to a module it has imported" (watch-list
  `never`/`already`, nothing lost).
- "the way to defer a costly import was to move it inside" → "deferring a
  costly import meant moving it inside" (watch-list "was to").
- "for what its body *does*" lost its italics (emphasis, not a new term).

## A listing and an exercise for "What a Module Exports"

It is the only section in the chapter with neither a listing nor an
exercise: the underscore convention, `import *` skipping underscored names,
and `__all__` are all stated but never shown, and the five exercises cover
packages, naming, lazy order, case sensitivity, and relative imports. The
claims are one-line facts a reader can accept on trust, so the section works
as prose; but everywhere else in the chapter a behavioral claim comes with
markers the reader can run. If you want it demonstrated, the minimal pair
is a module and a star-importing consumer:

```python
# exporting.py

__all__ = ["public", "helper"]

def public():
    return "public"

def helper():
    return "helper"

def _internal():
    return "internal"

def undeclared():
    return "undeclared"
```

```python
# star_import.py
from exporting import *  # noqa: F403

print(sorted(n for n in dir() if not n.startswith("__")))
#: ['helper', 'public']
```

with two sentences of prose: without `__all__`, the star import would bind
`public`, `helper`, and `undeclared` (everything not underscored); with it,
only the listed names arrive, and `_internal` is skipped either way. A
matching exercise 6 would have the reader remove `__all__`, predict the new
`dir()` output, and restore it. Not applied because it grows the chapter by
a listing and an exercise, teaches `import *` by using it (the chapter and
the house style both discourage it, so the `# noqa` is part of the price),
and requires a matching solution block; that scope call is yours. If
accepted, I will add the solution in the same change.

[] Reject

## Considered and declined

- `use_module.py` gathers both markers at the listing's end instead of
  hugging the two `print()` calls. Hugging the second would put an indented
  `#:` inside the `if __name__` block, and no indented marker exists
  anywhere in `Chapters/`; end-of-listing is the established shape for
  `__main__` demos.
- The `__init__.py` re-export sentence ("it usually re-exports the
  package's public names") has no demonstrating listing. Showing it means
  editing `a_package/__init__.py`, which would ripple through the loading
  markers of every package listing in the chapter; the relative-import
  section supplies the `from .module1 import function1` form a reader needs
  to do it.
- With `none` gone, the chapter loses its "quickest way to find out whether
  laziness is behind a bug". The remaining off switch is
  `sys.set_lazy_imports_filter(lambda *args: False)` at the program's entry
  point; I left it out as advanced API surface for an introductory chapter,
  and the PEP frames it as a specialist tool.
- `app_settings.py` carries annotations (`debug: bool`, `-> None`) two
  chapters before Static Typing; chapters 04-05 listings are bare.
  Harmless, and `debug: bool = False` documents the demo's intent.
- No closing section before Exercises: chapters 02 through 05 share the
  shape, so this is the tour-part convention, not a missing conclusion.
- "it is what documentation tools read when they ask what a module offers":
  "is what" kept; the following words are a clause that cannot attach
  without it, the style rule's own exception.
