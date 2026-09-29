> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 06_Foundations--Modules_and_Packages (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I checked every runtime claim with a probe on the pinned interpreter (3.15.0rc2):
the circular-import messages in four arrangements (beside the script, inside a package with absolute and relative imports, on a later `sys.path` entry),
the five `lazy` syntax errors, `sys.lazy_modules` before and after a load,
the three `-X lazy_imports` values, `importlib.reload()`, `PYTHONCASEOK`,
the `sys.path` order under `PYTHONPATH`, and the messages Solutions 4 and 5 quote.
I read the linked sections in chapters 04, 07, 17, 24, 27, 29, and 38,
NumPy's installed `__init__.py`, and pandas's and SciPy's on GitHub.
PEP 810 still describes `none` and the 3.15 command-line docs list two values,
so the chapter's sentence about the removed third value stands.

## Applied directly

Chapter, corrections:

- "Deferring an Import Before 3.15": "The pandas and numpy packages use that technique" was wrong for pandas, whose `__init__.py` defines no module-level `__getattr__`. Now "NumPy and SciPy", both of which load submodules that way.
- "Importing Names with `from` and `as`": "`from` copies the name's current value" contradicted chapter 03's "assignment never copies" and implied a copied list. Now "`from` works like an assignment: it binds a name in this file to the object the module's name refers to at that moment."
- "`PYTHONPATH`": "raises a `ModuleNotFoundError` when none of them does" said the search ends at the `PYTHONPATH` entries. Python searches all of `sys.path`, and the sentence now says so.
- "Watching the Deferral": "The set already holds more than one name before this script marks `noisy` lazy" described a check the listing does not make (it prints after the `lazy import`). Now "This script marks one import lazy and the set holds more than one name." The lead-in names the actor: standard-library modules loaded at startup carry their own lazy imports (twelve names on this build).
- "Circular Imports": "That wording appears when..." pointed back across an intervening sentence, and the plain-`import` case was split between the third sentence and the last. The plain-`import` sentences now sit together and name the `AttributeError`; the message-wording paragraph follows, and says the "circular import" wording covers every module inside a package.

Chapter, teaching:

- Opening: "an unqualified `import` statement" used "qualify" for something other than the sense the next paragraph defines. The sentence now states the rule the listings only imply (import by file name, without `.py`) and points to `PYTHONPATH` for the other locations.
- *namespace* had italics and no definition. Added "the set of names the module defines".
- "Circular Imports": `TYPE_CHECKING` appeared with no statement of what it is. Added that it is `False` at runtime, so the import runs for the checker alone.
- "What a Module Exports": `# noqa: F403` in `star_import.py` was unexplained, and the chapter showed a star import without advising against one. Added a short paragraph after the result.
- "What a Module Exports": `accounting._Engine` arrived with no introduction. Added "For a module `accounting` that defines `_Engine`".
- Exercise 7, new: a `from`-imported list, mutated and then rebound through the module's name. No exercise covered the `from` binding rule, and mutation against rebinding is the lookalike pair the section leaves open. Appended, so no existing number moves.

Chapter, prose:

- `json.dumps` is `json.dumps()`.
- "loads exactly what `import` loads": dropped "exactly".
- "`globals()` returns it as a mutable `dict`, the same dict Python already searches": the previous sentence said it is a dict you can write. Now "`globals()` returns it, the same dict Python searches".
- "gathers the intended surface": now "gathers the public names".
- "To change the setting for a whole run": no setting had been named. Now "To change which imports are lazy".
- "`from_packages.py`, where `from` binds `module1`": added "below", since the listing comes two listings later.

Solutions:

- Exercises 1 and 2: the Solutions `a_package` and `b_package` had no `__init__.py`, so the markers lacked the `initializing` lines a reader sees, and each solution carried a paragraph explaining the difference. Both packages now carry the chapter's `__init__.py` as a listing, the markers match a reader's run, and the two paragraphs are gone. This also matches the chapter's "this book uses one by default".
- Exercises 1 and 3: markers now follow the statements that print them.
- Exercise 4: on 3.15 the message is `No module named 'module'. Did you mean: 'Module'?`. Quoted in full, with a sentence on what the suggestion shows.
- Exercise 2: "`bPackage` reads as a class" was wrong (camelCase is not the class convention). Now "stands out as something other than a package". "The rename costs everything the convention buys" reworded.
- Exercise 1: "by any of these spellings" is "in any of these forms".
- Small cuts: "genuine", "happily", "at all", "exactly".
- `module5.py`, `noisy.py`, `noisy2.py`: blank line after the file marker, as in the chapter's copies.
- Exercise 7: new solution, `plugin_list.py` and `exercise_7.py`.

## Considered and declined

- **Dropping the annotations in `app_settings.py`.** It is the chapter's only annotated listing, and chapters 04, 05, and 07 annotate nothing. Tried and reverted: without `debug: bool`, `ty` infers `Literal[False]` and rejects `app_settings.debug = True` in `from_snapshot.py`.
- **A listing for "Circular Imports".** The section is prose with quoted messages. The message depends on where the file sits relative to the script, and the validator runs listings with a different `sys.path` than a reader's run, so a marker would show the wording the prose says a reader does not get.
- **"CPython removed it before the 3.15 release."** Reads like version history, which `deep_review_db.md` bars. Kept: PEP 810, which the section links, still describes `none`, and `-X lazy_imports=none` stops the interpreter at startup.
- **`sys.lazy_modules` and `from` imports.** After `lazy from pathlib import Path` loads, `pathlib` leaves the set and `pathlib.Path` stays. The chapter's claims concern a `lazy import` of a module, where they hold, and its advice (check for a name you marked) is unaffected.
- **Moving "`PYTHONPATH`" ahead of "Packages".** The search path explains the first listing, but the opening now links to the section, and "File Names" links to it by anchor.
- **The path separator for `PYTHONPATH`.** The section steers the reader to an install, so the detail would serve the approach it advises against.
