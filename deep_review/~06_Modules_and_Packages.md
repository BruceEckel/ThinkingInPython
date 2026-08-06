[[Reviewed]]
# Deep review: 06_Modules_and_Packages.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Teach that a module's body runs once

**Kind:** teaching
**Where:** end of the intro section, after `import_module.py` (line ~78), or a short new section before "Packages"
**Problem:** the chapter never says that Python executes a module's top-level code only the first time it is imported and serves every later import from a cache. Two of the three exercises are built entirely on this fact (exercise 1: "confirm the loading message prints only once"; exercise 2: "explain why the 'importing module1' message does not print a second time"), so the reader is asked to explain a mechanism the chapter withheld. Chapter 24 (Singleton) opens by asserting it as known: "Python imports each module once and caches it in `sys.modules`." It has no home anywhere in the book right now.

**Proposal:** add a listing and two sentences of prose. The listing (verified against the built `a_package`, output shown):

```python
# import_once.py
import sys
import a_package.module1
import a_package.module1
#: importing module1 in a_package

print(sys.modules["a_package.module1"] is a_package.module1)
#: True
```

Prose after it: the second `import` prints nothing because the first one stored the finished module object in `sys.modules`, a dict keyed by dotted module name. Every later `import` of that name, from any file in the program, finds it there and binds the same object instead of re-running the file. That is why `module1`'s message appears once no matter how many of the earlier listings import it, and why a module's top-level code is a one-time setup step rather than something that runs per import.

Alternative, if a fourth listing is too much for this chapter: fold the point into the existing prose after `import_module.py` (line ~77) as two sentences with no listing, and let exercise 2 do the demonstrating.

**Cost:** introduces `sys.modules` in chapter 6, which chapter 24 currently introduces on its own. If accepted, chapter 24's line 10 could be shortened to a back-reference, but it reads fine either way. Adds one file to `Examples/06_Modules_and_Packages/`.

---

## 2. Restore the missing fourth exercise (Solutions has an answer with no question)

**Kind:** exercise
**Where:** "Exercises" (lines 325-341); `Solutions/06_Modules_and_Packages.md` heading "## 4. Renaming `module.py` to `Module.py`"
**Problem:** the Solutions file answers four exercises. The chapter asks three. Solution 4 is a full, well-written treatment of case sensitivity: renaming `module.py` to `Module.py` works on Windows/NTFS and fails on a case-sensitive filesystem, which is why the naming rules recommend `snake_case`. A reader hits an answer to a question the book never asked. Either the exercise was dropped or the solution was written ahead of it.

**Proposal:** add the exercise the solution already answers, as exercise 4:

> 4.  Rename `module.py` to `Module.py` and change `use_module.py` to `import Module`. Run it. Then change the import back to `import module`, leaving the file named `Module.py`, and run it again. Explain the result, and say what would happen on a case-sensitive filesystem such as Linux's default.

Its placement in the exercise set is worth a thought: it tests the "File Names" section, which nothing else exercises, so it fits well alongside proposal 9's replacement for exercise 2. If both are accepted, exercise 2 tests package nesting and naming, and exercise 4 tests case sensitivity, and "File Names" stops being the one section with no exercise.

Alternative: if the exercise was dropped deliberately, the solution should come out of `Solutions/06_Modules_and_Packages.md` instead. Something has to move, since the two files disagree as they stand.

**Cost:** none to the chapter. Separately, and outside this review's edit scope: solution 4 ends with a link written as `[File Names](#file-names)`, a same-page anchor pointing at a heading that lives in `Chapters/06_Modules_and_Packages.md`, not in the Solutions file. It should be `[File Names](../Chapters/06_Modules_and_Packages.md#file-names)` or whatever form the Solutions tree uses for chapter links.

---

## 3. Stop the `globals()` digression from splitting a listing from its explanation

**Kind:** structure
**Where:** lines 31-49 (the `globals()` prose and `globals_demo.py`), sitting between `use_module.py` (line 15) and the `__name__ == "__main__"` explanation (line 51)
**Problem:** `use_module.py` is shown, then the chapter detours through `globals()` for nineteen lines, then line 51 resumes with "The code at the end of the file starts with an `if` clause". Which file? By then two listings have gone by and the referent is no longer obvious. A reader meeting `if __name__ == "__main__":` for the first time has been holding the question across an unrelated topic, and the digression itself ends by admitting it "is rarely useful on its own", which is a tell that it is not paying its way where it sits.

**Proposal:** move the `globals()` paragraph and `globals_demo.py` down, to just after `using_as.py` (line ~100) and before the "Packages" heading. The intro then runs straight through: import and qualify, then `__name__`, then `from`, then `as`, then the namespace-as-a-dict aside that generalizes all of it. Line 51 becomes "The code at the end of `use_module.py` starts with an `if` clause" so it names its referent regardless.

Alternatives: (a) keep the position and only rename the referent at line 51, which fixes the ambiguity but not the interruption; (b) cut the `globals()` material from this chapter and let chapter 17 (Metaprogramming) carry it, since dynamic name creation is that chapter's business.

**Cost:** none downstream. Nothing links to this passage, and `globals_demo.py` does not depend on any other listing.

---

## 4. Say what `import a_package.module1` actually binds

**Kind:** teaching
**Where:** after `using_packages.py` (line ~155)
**Problem:** the chapter shows `import a_package.module1` followed by `a_package.module1.function1()` and says only "you must qualify it with the package name." It never explains why: `import a.b` binds the name `a`, not `b`, and attaches `b` to it as an attribute. Without that, the reader has a rule to memorize instead of a mechanism, and cannot predict the next case they will hit. It also leaves the `import a_package.module1` / `from a_package import module1` pair looking like two spellings of one thing when they bind different names.

**Proposal:** two sentences after `using_packages.py`, plus one line in the listing. Verified: after `import a_package.module1`, `"a_package" in dir()` is `True` and `"module1" in dir()` is `False`.

> `import a_package.module1` binds only the name `a_package` in this file. Loading `module1` also sets it as an attribute of the package, which is why `a_package.module1.function1()` resolves, and why the shorter `module1.function1()` fails here but works in `from_packages.py` below, where `from` binds `module1` directly.

**Cost:** none. It sets up the contrast the next two listings already draw, so `from_packages.py`'s one-line follow-up ("Here you no longer need to qualify the module with the package name") gains a reason.

---

## 5. Add relative imports inside a package

**Kind:** teaching
**Where:** new subsection at the end of "Packages" (after `two_levels.py`, line ~212)
**Problem:** the chapter shows only how code *outside* a package imports from it. It never shows a package's own module importing a sibling, which is the first thing a reader hits once they write a real package. The house style names this as the one place relative imports are preferred ("Prefer absolute imports over relative ones, except within a package's own submodules"), so the book's own rule refers to a construct the book never introduces.

**Proposal:** show both forms in `a_package` and name the trade-off, plus the failure a reader will meet. Both listings verified:

```python
# a_package/module4.py
from .module1 import function1

def function4():
    return f"function4 calls {function1()}"
```

The leading `.` means "the package this module lives in," so `module4` finds its sibling without naming `a_package`. Two dots (`..module1`) reach the parent package, which is how `b_package/module3.py` would import from `a_package`. The absolute form `from a_package.module1 import function1` works from inside the package too, and is the better choice when the import crosses a package boundary; a relative import is for a package's own submodules, where it keeps the package renameable.

The failure worth showing: running `python a_package/module4.py` directly raises `ImportError: attempted relative import with no known parent package`, because a file run as a script has no package context. Run it as `python -m a_package.module4` instead.

**Cost:** adds one file under `a_package/`, and a fourth import form to a chapter that already has four. Consider whether "Packages" is getting long; this could go after "File Names" instead.

---

## 6. Contrast `lazy import` with the function-local import a reader would write

**Kind:** teaching
**Where:** "Lazy Imports", after the paragraph at line ~283 ("Nothing loads at the `lazy import` lines")
**Problem:** deferring an import is not new in 3.15. The idiom every existing Python program uses is putting the `import` inside the function that needs it, and a reader who knows that idiom will ask what `lazy` buys. The chapter's own answer is sitting half-said at line ~268, "while still declaring all imports at the top of the file," but it never names the practice it is replacing, so the sentence reads as a stylistic preference rather than the point.

**Proposal:** a short paragraph naming the near-miss.

> Before 3.15, the way to defer a costly import was to move it inside the function that needed it. That works, but it hides the dependency: nothing at the top of the file says the module is used, tools that read imports miss it, and the `import` statement re-runs its `sys.modules` lookup on every call. `lazy import` keeps the declaration at the top where a reader and a tool can see it, and pays the loading cost once, at first use.

**Cost:** none.

---

## 7. Ground the search path in `sys.path`

**Kind:** teaching
**Where:** "`PYTHONPATH`" section (lines 241-256)
**Problem:** the section describes a search path that Python "keeps searching through" and a package that "resolves by name from anywhere," but never shows the thing being searched. The reader has no way to check what their own path contains when an import fails, which is the situation that brings them to this section. It also leaves the chapter's opening claim ("if the file is in the same directory") ungrounded: same directory as what, and why?

**Proposal:** one sentence and a run-only mention (the values are machine-specific, so no `#:` marker):

> Python searches `sys.path`, a list of directories it builds at startup. `print(sys.path)` shows it. Its first entry is the directory of the script you ran, which is why `use_module.py` could `import module` with no setup at all; `PYTHONPATH` prepends its entries after that, and installed packages sit further down.

**Cost:** none. Deliberately says nothing about virtual environments or installers, per the book's scope.

---

## 8. Tighten the file-name rule

**Kind:** prose
**Where:** "File Names", lines 216-218
**Problem:** "A file name must be a valid identifier containing letters, digits, and underscores. It cannot start with a digit." As written this is false: any name is a legal `.py` file name, and `my-script.py` runs fine. The constraint is on *importability*, which the bullet three lines down half-reveals with "hyphens aren't importable". The rule also misses keywords: `class.py` is a valid identifier's shape but `import class` is a `SyntaxError`.

**Proposal:** replace with:

> To be importable, a module's file name must be a valid Python identifier: letters, digits, and underscores, not starting with a digit, and not a keyword. Any other name still runs as a script but can never be the target of an `import`.

**Cost:** none.

---

## 9. Spread the exercises across the chapter

**Kind:** exercise
**Where:** "Exercises", lines 325-341
**Problem:** three exercises cover two topics. Exercises 1 and 2 both test module caching, and exercise 3 tests lazy-import ordering. Nothing exercises `from`/`as`, nested packages, the naming rules, or `globals()`. The chapter's largest section, "Packages", is touched only incidentally.

**Proposal:** keep exercise 1 (it also drills the three import forms) and exercise 3; replace exercise 2, which duplicates exercise 1's lesson, with one on nesting and naming:

> 2.  Add `a_package/b_package/module4.py` with a `function4()` that calls `function3()` from `module3`. Import and call `function4()` from a script outside `a_package`, then rename `b_package` to `bPackage` and explain, from the naming rules above, why that name is a poor choice even though the import still works.

If proposal 1 is accepted, the old exercise 2 becomes redundant with the new listing as well as with exercise 1, which strengthens the case for replacing it.

**Cost:** `Solutions/06_Modules_and_Packages.md` has a matching "## 2. Importing an already-imported module a second time" that would need replacing along with the exercise. Note that its text opens with "This is the same caching behavior as exercise 1", which concedes the duplication.

---

## 10. Move the narrating comments in the lazy listings into prose

**Kind:** code
**Where:** `lazy_imports.py` line 276, `lazy_noisy.py` line 303
**Problem:** two comments narrate what the next line does, which the house style routes to prose. `# Once used, the names behave like eager imports:` and `# noisy's body runs here, on first access`. The second is redundant with the prose immediately below the listing, which says the same thing in better words ("It runs at `noisy.announce()`, the first access").

**Proposal:** delete both comments. The prose after `lazy_noisy.py` already carries the second one. For `lazy_imports.py`, fold the first into the sentence that follows the listing: "Nothing loads at the `lazy import` lines, and once loaded the names behave exactly like eagerly imported ones."

Flagged rather than done, since the style rule explicitly does not license editing comments already sitting in example code.

**Cost:** none; both files' output is unchanged.

---

## 11. Let the import markers sit against the imports that produce them

**Kind:** code
**Where:** `using_packages.py` (line ~145), `from_packages.py` (line ~160), `no_qualification.py` (line ~176)
**Problem:** all three listings put a blank line between the `import` statements and the `#:` markers those imports produce, so the markers visually attach to the `print()` below them instead:

```python
import a_package.module1
import a_package.module2

#: importing module1 in a_package
#: importing module2 in a_package
print(a_package.module1.function1())
#: function1 in module1 in a_package
```

The convention elsewhere in the book is that each `#:` run hugs the statement that produced it. Here the reader has to work out that the first two markers belong to the imports.

**Proposal:** drop the blank line in all three so the markers follow the imports directly, then keep a blank before the first `print()`. Worth re-running the gate afterward to confirm `validate_output.py` is position-insensitive here.

**Cost:** touches three listings; output text unchanged.

---

## 12. Explain the two directives in `globals_demo.py`

**Kind:** prose
**Where:** line 43, `print(y)  # type: ignore  # noqa: F821`
**Problem:** the reader meets `# type: ignore` and `# noqa` in chapter 6, two chapters before static typing is introduced, with no explanation. They are also the most interesting thing on that line: they exist because neither the checker nor the linter can see a name created by a dict assignment, which is the section's whole point stated from the tooling side.

**Proposal:** one sentence after the listing: "The two directives on the `print(y)` line silence the type checker and the linter, neither of which can see a name that appears only as a dict key. That is the cost of creating names this way, and a reason to keep it rare."

**Cost:** none.

---

## 13. Link the dunder forward-reference

**Kind:** prose
**Where:** lines 52-55
**Problem:** "Dunder methods, for example, hook your class into the language's operators and built-in functions" points at material the reader has not seen and gives no destination. Per the repo's cross-reference rule, a named link beats a bare mention.

**Proposal:** end the sentence with a link, e.g. "...built-in functions (see [Classes](07_Classes.md))." Also consider replacing "hook your class into" with "connect your class to"; "hooks" is on the watch list.

**Cost:** none; `heading_links.py` gates the link.

---

## 14. Small watch-list wording

**Kind:** prose
**Where:** lines 188, 268
**Problem:** two tier-2 watch-list words that the sentences do not need.

**Proposal:**
- line 188: "You can even put a second package underneath the first one" → "You can put a second package underneath the first one".
- line 268: "so you only pay the cost for what you actually need" → "so a run pays only for the modules it uses".

**Cost:** none.

---

## Already fixed directly (no decision needed)

- line ~320: the global lazy-import switches were wrong. The chapter said to "use the `-X lazy_imports` command-line option or the `PYTHON_LAZY_IMPORTS` environment variable"; both require a value on the pinned 3.15.0b4, and a bare `-X lazy_imports` is a fatal startup error (`invalid value; expected 'all' or 'normal'`). Rewritten to `-X lazy_imports=all` / `PYTHON_LAZY_IMPORTS=all`, with the two accepted values named. Note that PEP 810's text also lists a `none` mode; this build rejects it, so the chapter names only `all` and `normal`.
- line ~48: "a module-level name whose spelling isn't known until runtime" → "a module-level name that isn't known until runtime". "spelling" is on the do-not-use tier of the watch list.

## Verified clean (no action)

- Every listing runs and its `#:` markers match stdout exactly (11 scripts re-run individually).
- `ty check` and `ruff check` both pass on `build/examples/06_Modules_and_Packages`. No tests in this chapter.
- All the `lazy` syntax restrictions the chapter states were confirmed on 3.15.0b4: `SyntaxError` inside a function, a class body, and a `try` block; `lazy from ... import *` and `lazy from __future__ ...` both rejected. Also confirmed that a deferred module that is missing or broken raises at first use, not at the `lazy import` line.
- No em-dashes were added or removed. No banned phrases from `tools/data/banned_phrases.txt`.
- The only inbound cross-reference is `Chapters/07_Classes.md:105`, which links the chapter file with no anchor, so nothing here is at risk from a heading change.
