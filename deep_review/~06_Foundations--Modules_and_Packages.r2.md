> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 06_Foundations--Modules_and_Packages (2026-10-13)

No live blocks: every finding had one sensible answer and is applied below.
I ran `tip verify-ch CH=06 ISOLATED=1` before and after (27 passed, 0 failed both times),
ran all sixteen chapter scripts and five solution scripts directly from `build/verify-ch-06/` against their markers (all match),
and re-probed the runtime claims on the interpreter the gate now uses, Python 3.15.0 final (the last review used 3.15.0rc2), with `ty` 0.0.86:
the five `lazy` syntax errors (and that `lazy` inside `if` and `with` at module level is accepted),
`-X lazy_imports=none` stopping the interpreter at startup with "expected 'all' or 'normal'",
`all` deferring a plain `import` while an import inside `try` stays eager,
the three circular-import messages (beside the script, inside a package, and the later `AttributeError`),
`package_only.py`'s `AttributeError`, the relative-import `ImportError` from `python a_package/module4.py`,
`PYTHONCASEOK` and the `Did you mean: 'Module'?` message, the `sys.path` order under `PYTHONPATH` and `-P`,
and `ty`/`ruff`'s `unresolved-reference`/`F821` on `globals_demo.py` without its directives.
Solutions 5's `Did you mean: 'b_package'?` message also reproduces.
`tip prose CH=06` reports no new hits.

## Applied directly

Chapter:

- Main guard paragraph: "so the importer gets the definitions alone" was contradicted by the next listing, where importing `use_module` prints its body's message. Now "the `if` skips the code at the bottom of the file, the part meant for a command-line run."
- `import_once.py` walkthrough: `import use_module as second` used `as` a section before it is taught. Added a clause saying `as second` binds the object under a second name, linking the next section.
- Same paragraph: "changes nothing in a program that has imported it" is "in a running program".
- "Imports Within a Package", teaching (near-miss): a reader coming from Python 2 or from scripts writes `from module1 import function1` without the dot. Added that this looks for a top-level `module1` on the search path and stops `use_module4.py` with `ModuleNotFoundError: No module named 'module1'` (probed).
- "Circular Imports": `sys.path[0]` appeared before `sys.path` is explained. Now "the first entry of [`sys.path`](#pythonpath)".
- "Circular Imports": "annotations" links chapter 08's type-hints section, since the paragraph leans on them.
- "What a Module Exports": "silences the linter's objection to the star import, which hides..." had two candidates for "which". Split, with "A star import" as the subject.
- "File Names": "underscores only when they genuinely help" is "when they aid readability".
- "File Names": "a distinctive name for the same reason" pointed at search order, while the `config.py` sentence that follows is about the module cache. Now names `sys.modules` as the reason.
- "`PYTHONPATH`": "edits to its source take effect immediately" contradicted the chapter's own lesson that a running program keeps its loaded module. Now "the next time you run a program that imports it".

Solutions:

- Exercise 1: a broken hand-wrap ("The" alone on a line) rewrapped.
- Exercise 3: "Each `lazy import` reserves the name" is "binds the name and defers the load", matching the hint.
- Exercise 4: "imports happily" is "imports cleanly". The `PYTHONCASEOK` paragraph now puts the confirming inference beside the observation, ahead of the legacy-code advice.
- Exercise 5: "a file you intend to run both ways" did not say which ways. Now "to run with `python file.py`".
- Exercise 6: "compose in one direction only" was opaque, and it implied the underscore still filters when `__all__` exists. Now states that `__all__` replaces the underscore rule (a listed name arrives with or without one, an unlisted name stays out).

## Considered and declined

- **Exercise 6 is answered in the chapter.** The prose after `star_import.py` names the three names a star import binds without `__all__`, so the exercise is a confirmation run. Exercise 1 is the same kind, and the concrete names explain why `undeclared` is in the listing; rewording the prose to hide the answer would cost that.
- **`[façade]` lowercase in "What a Module Exports".** It names an instance ("serve as a façade"), as chapter 29's "The cleaner Python façade is a module" does, so the italic-capital pattern rule does not apply.
- **"Code outside the module can still read `module._name`"** repeats the underscore paragraph's "signal rather than a barrier". Kept: it sets up "Both say which names a caller should use", which echoes chapter 29's "A façade is an agreement about which names to call".
- **`uv sync` versus `uv pip install -e .`.** `uv sync` also installs a packaged project in editable mode, so "or ... for an editable install" undersells it; spelling out when uv installs the project itself is tooling detail the book leaves to uv's docs.
- **Re-proposals.** The prior review's declined items (annotations in `app_settings.py`, a circular-import listing, the `none` sentence, `sys.lazy_modules` and `from`, moving "`PYTHONPATH`", the path separator) still stand on 3.15.0 final.

## For the session

- `tip watch-words` now reports three stale baseline entries for this chapter and its Solutions file (the "genuinely help" and the two exercise 6 "only" sentences, all reworded). `tip internal-names` reports one stale entry unrelated to this chapter: `Examples/15_Techniques--Context_Managers/banner_cm.py::banner.title`.
