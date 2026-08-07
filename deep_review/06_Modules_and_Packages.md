[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Opening paragraph, line 3 — "a namespaced *module*"**

"Each Python file is a namespaced *module* you can `import` into another Python
file." The italics announce that *module* is the term being defined, but
"namespaced" arrives as an unexplained adjective in front of it, so the sentence
defines the word with a word the reader does not have yet. The next paragraph is
where "namespace" actually gets introduced.

Proposed:

> Each Python file is a *module* you can `import` into another Python file.

The namespace idea is already carried by the paragraph after the two listings;
dropping "namespaced" here loses nothing and removes a term used before it is
taught.

---

[] Reject

**Line 26 — "Importing a module creates a *namespace* within the file that
imports it"**

This is not what happens. The imported module already owns its namespace, which
exists whether or not anything imports it. `import module` binds one name in the
importing file; the namespace it reaches is the imported module's, not a new one
created in the importer. As written, a reader could conclude that the namespace
is a per-importer thing, which then makes the `sys.modules` paragraph twenty
lines later (one module object shared by every importer) contradict it.

Proposed:

> Importing a module makes its namespace reachable in the importing file, under
> the module's name.
> This automatically prevents name clashes between the imported module's names
> and the local ones.

---

[] Reject

**After `using_from.py` (around line 91) — the biggest missing lookalike pair:
`import m` versus `from m import x`**

The chapter shows `import module`, `from module import useful_function`, and
`import module as m` as three spellings of the same idea, and never says that
the second one differs in kind. `from m import x` copies the *current* binding
of `x` into this file. It does not create a live link to `m.x`. Rebinding `m.x`
afterward leaves the local `x` pointing at the old object. This is one of the
most common real bugs in Python module use (the classic case is a config flag or
a counter), and it is exactly the material this chapter covers, so its absence
here is not going to be repaired by any later chapter.

Both listings below were run and checked in `build/examples`: output as shown,
`ty` clean, `ruff` clean.

Proposed addition, immediately after `using_from.py` and before the `using_as.py`
paragraph:

> `from` copies the name's current value into this file rather than linking to
> it. Rebinding the name in the module afterward does not reach the copy:
>
> ```python
> # settings.py
> debug: bool = False
>
> def show() -> None:
>     print(f"settings.debug is {debug}")
> ```
>
> ```python
> # from_snapshot.py
> import settings
> from settings import debug
>
> settings.debug = True
> print(debug, settings.debug)
> #: False True
> settings.show()
> #: settings.debug is True
> ```
>
> `settings.debug` is now `True`, and `show()` sees the new value because it
> looks the name up in its own module every time it runs. The local `debug` is a
> separate binding made once, at import, so it still holds `False`. Import the
> module and write `settings.debug` when the value can change; use
> `from ... import` for things that don't get rebound, such as functions and
> classes.

Alternative if this is too much for chapter 6: keep the prose sentence and drop
the second listing, showing only `print(debug, settings.debug)`. I recommend
keeping `show()`, because the contrast between "the module sees the new value"
and "the importer does not" is what makes the mechanism visible rather than just
the outcome.

---

[] Reject

**`import_once.py` paragraph, line 75 — "The message prints once even though the
module is imported twice"**

Two different modules are in play and both are called "the module" in this
sentence. The printed text is `'module' imported`, which names `module.py`, but
the thing imported twice is `use_module`. A reader tracking two files by those
two names has to stop and work out which one the sentence means.

Proposed:

> `use_module`'s body runs once even though two `import` statements name it.

---

[] Reject

**`sys.modules` paragraph, line 75-80 — the consequence of caching is never
stated**

The paragraph explains the mechanism correctly and stops there. The consequence
a reader hits within a week is the one that is missing: because the body runs
once per process, editing a module's source has no effect on a program (or a
REPL session, or a Jupyter kernel) that already imported it. `importlib.reload()`
is the escape hatch and is worth naming even if the chapter recommends against
relying on it.

Proposed, appended to that paragraph:

> A consequence: a running program never notices an edit to a module it already
> imported. Restart it, or call `importlib.reload(use_module)`, which re-runs the
> body into the existing module object. Reloading leaves every name already bound
> by a `from ... import` pointing at the old objects, which is why restarting is
> the reliable choice.

---

[] Reject

**`globals()` section, line 104-107 — the two halves of "namespace" are never
joined**

The chapter uses "namespace" for two things without connecting them: the module
object you reach through a dotted name, and the dict `globals()` hands back. They
are the same dict. Saying so turns two ideas into one, and it makes the earlier
`use_module` material pay off.

Proposed, appended after "the same dict Python already searches when it looks up
a top-level name":

> It is also the dict behind the dotted name: `use_module.__dict__` from outside
> is the same object `globals()` returns inside `use_module`, which is why
> `module.useful_function()` and a top-level lookup inside `module.py` find the
> same function.

Also: "A module's own namespace is concrete, not just a figure of speech" is
doing rhetorical work rather than saying something. Plainer: "A module's
namespace is an ordinary dict you can read and write."

---

[] Reject

**Packages section, line 133-139 — "Typically, there's no executable code in
`__init__.py`. It is only there to flag the directory as a package."**

This is true of the book's `a_package` and false of most packages the reader will
actually open. The dominant real use of `__init__.py` is to define the package's
public surface, so that `from a_package import function1` works without the
reader knowing which submodule holds it. A reader who takes "only there to flag
the directory" literally will be puzzled by the first `__init__.py` they read in
a library.

Two things are missing and they are the same fix. Right now `a_package/__init__.py`
is empty, so the reader never sees it run either, even though it runs before any
submodule of the package loads. Giving it a print and a re-export teaches both at
once.

Proposed: change the `__init__.py` listing to

```python
# a_package/__init__.py

print("initializing a_package")
```

which makes it visible in the `#:` markers of `using_packages.py`,
`from_packages.py`, `no_qualification.py`, `two_levels.py`, and `use_module4.py`
that the package body runs first, exactly once. Then replace the "no executable
code" sentence with:

> `__init__.py` runs once, before any module inside the package loads. It is
> often empty, and then it only flags the directory as a package. When it isn't,
> it usually re-exports the package's public names, so that
> `from a_package import function1` works and callers never learn which submodule
> `function1` lives in.

Cost of this change: five listings' `#:` markers gain a line, and the
`b_package/__init__.py` listing would want the same treatment for consistency.
That is mechanical, but it is enough churn that I did not apply it. If the
markers are unwelcome, the prose fix alone is still worth taking.

---

[] Reject

**After the `using_packages.py` paragraph (around line 188) — the near-miss the
reader will actually write**

The paragraph says "Loading `module1` also sets it as an attribute of the
package," which is the right mechanism, but it only ever appears as the reason a
success works. The reader's natural first guess is `import a_package` followed by
`a_package.module1.function1()`, and that fails: importing a package does not
import its submodules. Nothing in the chapter warns them, and the error message
(`module 'a_package' has no attribute 'module1'`) reads as though the package is
broken.

Verified in `build/examples`: output as shown, `ty` clean, `ruff` clean. (I
checked the `AttributeError` form too; `ty` emits `possibly-missing-submodule`
on `a_package.module1`, so `hasattr` is the form that passes the gate.)

Proposed addition after that paragraph:

> Importing the package alone does not import what is inside it:
>
> ```python
> # package_only.py
> import a_package
>
> print(hasattr(a_package, "module1"))
> #: False
> ```
>
> No submodule loads, and no message prints. `a_package.module1.function1()`
> here would raise
> `AttributeError: module 'a_package' has no attribute 'module1'`. The submodule
> becomes an attribute of the package only when something imports it by name.

---

[] Reject

**"Imports Within a Package" (line 247-281) — circular imports are never
mentioned**

Two modules in one package importing each other is the failure this section's
material leads straight into, and the chapter is silent about it. The reader who
follows the section's advice ("a package's own modules also import each other")
will eventually write a cycle and get `ImportError: cannot import name 'x' from
partially initialized module 'y' (most likely due to a circular import)`, a
message that is only decodable if you already know that a module's body runs top
to bottom and that `sys.modules` holds the half-finished module while it does.
The chapter has already taught both of those facts, so the explanation costs
three sentences.

The house style skill takes a position on this ("A circular import is a design
signal to resolve, not something to route around by default with
`TYPE_CHECKING`"), which the chapter should state.

Proposed, as a short paragraph at the end of the section:

> Two modules in a package can end up importing each other. The first one to load
> is placed in `sys.modules` before its body finishes, so the second one imports a
> partially initialized module and fails with
> `ImportError: cannot import name ... (most likely due to a circular import)`. A
> cycle is a design signal: move the shared piece into a third module both can
> import. When the cycle exists only in annotations, an
> `if TYPE_CHECKING:` import breaks it, because annotations are not evaluated at
> import time (see [Simulation](38_Simulation.md#a-robot-in-a-maze)).

That is the only place in the book that demonstrates the `TYPE_CHECKING` import;
`08_Static_Typing.md` line 608 only mentions it in the summary table and points
at 38 as well. If a forward link to 38 from chapter 6 is too far, drop the
parenthetical and keep the first two sentences, which carry the actual lesson.

---

[] Reject

**File Names, line 284-286 — the importability rule is stated more narrowly than
it is**

"To be importable, a module's file name must be a valid Python identifier:
letters, digits, and underscores, not starting with a digit, and not a keyword.
Any other name still runs as a script but can never be the target of an
`import`."

Two inaccuracies, both verified on the pinned 3.15:

- Python identifiers are Unicode, not ASCII. `π.py` imports fine as `import π`.
  "letters, digits, and underscores" reads as ASCII-only.
- A file whose name is a keyword, or contains a hyphen, is still loadable:
  `importlib.import_module("class")` and `importlib.import_module("my-mod")` both
  work. The restriction is on the `import` *statement*, whose grammar needs an
  identifier, not on the import machinery.

The practical advice is right; only the absoluteness is wrong. Proposed:

> To be the target of an `import` statement, a module's file name must be a valid
> Python identifier and not a keyword. `import my-mod` cannot parse.
> (`importlib.import_module("my-mod")` still loads it, which is how plugin
> loaders reach oddly named files, but that is not a name you should choose.)

---

[] Reject

**File Names, line 305-307 — "Don't shadow standard-library modules" states the
rule before the reader can understand it**

"A file named `random.py`, `types.py`, or `weakref.py` can hide the stdlib one and
break imports" is true, but *why* it can is `sys.path` ordering, which is the
first sentence of the next section. The reader meets the consequence one section
before the mechanism.

my recommendation: leave the order and add the reason inline —
   "...can hide the stdlib one and break imports, because the directory of the
   script you ran is searched before the standard library (see
   [`PYTHONPATH`](06_Modules_and_Packages.md#pythonpath) below)."

There is also a second, nastier form of shadowing that the chapter does not
cover and the house style skill does: a module already in `sys.modules` is never
re-resolved from `sys.path`, so a widely imported `config.py` or `utils.py` can
silently satisfy an unrelated same-named import elsewhere in the same process
(an `exec()`'d script, a plugin). One sentence: "Give a shared module a
distinctive name for the same reason: the first `config.py` imported anywhere in
the process is the one every later `import config` gets."

---

[] Reject

**`PYTHONPATH` section, line 313-314 — `sys.path[0]` is only the script's
directory when you run a script**

"Its first entry is the directory of the script you ran" holds for
`python use_module.py`. It does not hold for `python -m pkg.mod`, `python -c`, or
the REPL, where `sys.path[0]` is the current directory (`''`), and it does not
hold at all under `-P` / `PYTHONSAFEPATH`, which removes the entry. That last one
matters because it is the recommended way to avoid exactly the shadowing trap the
previous section warns about.

Proposed:

> Its first entry is the directory of the script you ran (the current directory
> when you use `-m` or the REPL), which is why `use_module.py` could
> `import module` with no setup at all.

Optionally, one more sentence tying it to the shadowing warning: "Running with
`-P` drops that first entry, so a local `random.py` can no longer shadow the
standard library."

---

[] Reject

**Lazy Imports, `lazy_imports.py` (line 346-355) — the first listing cannot show
what the prose claims**

"Nothing loads at the `lazy import` lines" is asserted under a listing where
nothing observable distinguishes lazy from eager: `json.dumps` and `Path(...)`
produce the same output either way. The proof arrives two listings later with
`noisy.py`, which is the right listing and is well done.

This is a "front-load the payoff" case rather than an error. The cheapest fix is
to stop the first listing claiming more than it shows: introduce it as the
*syntax* ("A `lazy import` is spelled like an ordinary one, with `lazy` in
front"), and let the sentence "Nothing loads at the `lazy import` lines" move
down to the `lazy_noisy.py` paragraph where it is demonstrated. No code changes.

An alternative is to swap the two listings so the deferral demo comes first. I do
not recommend it: `json`/`Path` is the friendlier first sight of the syntax.

---

[] Reject

**Lazy Imports — `sys.lazy_modules` is not mentioned**

3.15 exposes `sys.lazy_modules` (a set of names that have been lazily imported),
`sys.get_lazy_imports()` / `sys.set_lazy_imports()`, and
`sys.get_lazy_imports_filter()` / `sys.set_lazy_imports_filter()`. All confirmed
present on the pinned build. Only `sys.lazy_modules` seems worth this chapter: it
answers "did that actually defer?" without needing a module that prints, which is
the question a reader has right after the `noisy` demo. One sentence, next to the
`lazy_noisy.py` explanation:

> `sys.lazy_modules` holds the names that are currently deferred, so you can
> check what a run actually put off without instrumenting the modules.

The filter API is a packaging-level tool and I would leave it out.

---

[] Reject

**Exercise 1 and Exercise 2 reuse file names the chapter has already spent**

- Exercise 1 asks for `a_package/module3.py` with a `function3()`. The chapter
  already defines `a_package/b_package/module3.py` with a `function3()`.
- Exercise 2 asks for `a_package/b_package/module4.py` with a `function4()`. The
  chapter already defines `a_package/module4.py` with a `function4()`.

The two exercises are the chapter's own two files with their package levels
swapped, which reads as a mistake even though each is individually legal. It
looks like the exercises predate the `b_package/module3` listing and the "Imports
Within a Package" section, and were never renumbered when those landed.
`Solutions/06_Modules_and_Packages.md` inherits the problem and adds one: its
`use_module4.py` is a different program from the chapter's `use_module4.py`.

Proposed: renumber the exercise files to `module5`/`function5` and
`module6`/`function6`, and rename the solution's driver to `use_module6.py`.
Requires a matching edit to `Solutions/06_Modules_and_Packages.md` and
`SolutionsCode/06_Modules_and_Packages/`, which I did not touch.

Separately, exercise 2's instruction to rename `b_package` to `bPackage` breaks
the chapter's own `two_levels.py` if the reader is working in the book's example
tree. Worth adding "(rename it back afterward)".

---

[] Reject

**Exercise 4 is built on a false premise, and the solution's answer is wrong**

Exercise 4 asks the reader to rename `module.py` to `Module.py`, keep
`import module`, run it, and then "say what would happen on a case-sensitive
filesystem such as Linux's default." The wording promises a contrast between
platforms. There isn't one: the result is `ModuleNotFoundError` everywhere.

Per [PEP 235](https://peps.python.org/pep-0235/), CPython's `FileFinder` matches
the module name against the directory listing case-sensitively even on
case-insensitive filesystems, unless `PYTHONCASEOK` is set. In
`importlib/_bootstrap_external.py` on the pinned 3.15, `_relax_case()` returns
`True` only when the platform is case-insensitive *and* `PYTHONCASEOK` is in the
environment; otherwise the lookup uses `self._path_cache`, which holds the
on-disk spelling `Module.py`, so `"module" + ".py"` misses.

`Solutions/06_Modules_and_Packages.md` §4 answers the exercise the other way:
"Renaming the file to `Module.py` and updating `use_module.py` to `import Module`
still works on this machine, because Windows's default filesystem (NTFS) treats
file names case-insensitively ... so `import Module` finds it regardless of the
case used at the import site." The first half of that is fine (`import Module`
does work, because the case matches). The implication that `import module` would
also find `Module.py` on Windows is wrong.

The lesson is better than the one the exercise currently aims at, so I would keep
the exercise and sharpen it. Proposed:

> 4. Rename `module.py` to `Module.py` and change `use_module.py` to
>    `import Module`. Run it. Then change the import back to `import module`,
>    leaving the file named `Module.py`, and run it again. Predict the result
>    before you run it, then explain what you see, given that Windows and macOS
>    open `module.py` and `Module.py` as the same file. Look up `PYTHONCASEOK` to
>    confirm your explanation.

`Solutions/06_Modules_and_Packages.md` §4 needs rewriting to match; the correct
answer is that `import module` raises `ModuleNotFoundError` on every platform,
because Python verifies the case itself rather than trusting the filesystem, and
that this is deliberate (PEP 235) so that code written on Windows does not break
on Linux. The existing closing point about `snake_case` sidestepping the whole
question still stands. I did not edit `Solutions/`.

---

[] Reject

**Exercise coverage**

The four exercises cover packages (1, 2), lazy imports (3), and file naming (4).
Three of the chapter's sections get nothing: relative imports (which has its own
`###` heading and the only real trap in the chapter, running a package module as
a script), `globals()`, and `PYTHONPATH` / `sys.path`. Exercise 2 comes closest to
relative imports but asks for the absolute form.

Proposed, one addition:

> 5. Change `a_package/module4.py` to use the absolute import
>    `from a_package.module1 import function1` and confirm `use_module4.py` still
>    works. Then run `python a_package/module4.py` directly, both before and after
>    the change, and explain why only one of the two versions can be run that way.

That exercises the relative/absolute pair and the no-parent-package error in one
step, and it is answerable from the section as written.

---

## Cross-chapter

**`Chapters/24_Singleton.md`** — "A Module Is Already a Singleton" (lines 8-42)
re-teaches chapter 6's `sys.modules` caching, in an example file that is also
named `import_once.py`, with no link back. Chapter 6's version establishes the
mechanism; chapter 24's should cash it rather than restate it. Proposed change in
24, at line 10:

> Python imports each module once and caches it in `sys.modules`
> (see [Modules and Packages](06_Modules_and_Packages.md)).

Optionally also rename 24's `import_once.py` to `config_once.py` to stop two
different chapters shipping different programs under one slug. That touches
`Examples/24_Singleton/` and needs `make prune-examples`, so it is a bigger call
than the link.

**`Chapters/27_Factory.md`** — the paragraph at line 279-283 names the classic
self-registration failure ("the class is fine, the registry is fine, and nothing
ever imported the module that defines it"). On 3.15 there is now a second way to
get there: the module *is* imported, but with `lazy import`, or under
`-X lazy_imports=all`, so its body never runs and `__init_subclass__` never
fires. I verified this: a `lazy import plugin` whose name is never touched leaves
the registry empty, and `-X lazy_imports=all` does the same to a plain
`import plugin`. Proposed sentence to add there:

> A `lazy import` of the plugin module has the same effect, since its body does
> not run until something touches the name
> (see [Modules and Packages](06_Modules_and_Packages.md#lazy-imports)).

I added the general form of this warning to chapter 6's Lazy Imports section, so
the two ends will be consistent once 27 carries the pointer.

**`Solutions/06_Modules_and_Packages.md`** — three items, all noted above in
full: §4's answer is factually wrong (PEP 235 case matching); §1/§2's file names
collide with the chapter's own `module3`/`module4`/`use_module4`; and §3's
`noisy.py` prints `"noisy module body running"` / `"noisy announces!"` where the
chapter's `noisy.py` prints `"noisy module loaded"` / `"noisy.announce() called"`,
even though exercise 3 tells the reader to write `noisy2.py` "similar to
`noisy.py` above". The solution should reuse the chapter's `noisy.py` verbatim.
