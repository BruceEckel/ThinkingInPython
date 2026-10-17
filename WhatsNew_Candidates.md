# "What's New" Candidates for the Book

A pass through the CPython "What's New" pages from 3.15 back to 3.0,
filtered against what `Chapters/` already covers.
Each entry says what the feature is, where it would go, and how it would earn its place.

This document lists only recommendations.
Features that are out of scope (tooling, platform support, niche stdlib corners)
and features the book already covers adequately have been removed,
so an empty-looking release means that release had nothing worth acting on,
not that it went unread.
An entry survives when it carries an action, including "verify this" and "update this."

3.15 is a different kind of section from the rest.
It is the book's pinned target (`requires-python = ">=3.15"`),
so its features are the baseline rather than a compatibility question.
It is also still in development, so its "What's New" page will grow before release.

Verdicts:

- **Add** means a real gap in material the book already claims to teach.
- **Consider** means it would improve a chapter but nothing is currently wrong.
- **Mention** means one sentence or a footnote, not a section or a listing.

Coverage claims come from grepping `Chapters/`.
On 2026-09-29 every entry was rechecked against the book:
the 30 it now covers were removed,
and each partly covered entry says what is still missing.
A "not covered" note means the term appears nowhere in the book's prose or listings.
Later that day Bruce decided the nine remaining **Add** entries:
seven went into the book, and two were declined and removed.
The declined ones are module `__getattr__()` for deprecation with `__dir__()`
(chapter 6 teaches the hook once),
and `singledispatchmethod()` "dispatching on the second argument" in 3.15,
which did not reproduce on 3.15.0rc2.

---

## Top picks


---

## Python 3.15

The book's target version, so everything here is available to every listing without qualification.
`frozendict`, lazy imports, comprehension unpacking, `sentinel`, and the `profiling` package
are all in use in the book already and are not repeated below.

- **`math.integer` (PEP 791).** **Mention.**
  The integer-only functions (`gcd`, `lcm`, `isqrt`, `comb`, `perm`, `factorial`) now live
  in one namespace.
  Worth a clause anywhere the book uses one of them, since the old `math` names still work.
- **`re.prefixmatch()`, with `re.match()` soft deprecated.** **Mention.**
  The rename exists because `re.match()` matching only at the start surprises everyone,
  and the confusion with the `match` statement makes the old name worse.
  One sentence wherever regular expressions appear.

One task rather than a candidate:
**3.15 removes a batch of long-deprecated APIs** across `ast`, `collections.abc`, `ctypes`,
`datetime`, `glob`, `http.server`, `importlib.resources`, `pathlib`, `platform`,
`sysconfig`, `threading`, `types`, `typing`, and `zipimport`,
and `importlib.metadata` now raises `MetadataNotFound` where it used to be quieter.
The gates run on 3.15, so anything the book uses would already fail,
but prose that names a removed function would not.
Worth one grep pass over `Chapters/` against the removal list before release.

## Python 3.14

The release with the most that the book has no equivalent for.

- **`concurrent.interpreters`, PEP 734.** **Consider.**
  Chapter 19 mentions `InterpreterPoolExecutor` once.
  The underlying module is now the third real concurrency model in the stdlib,
  alongside threads and processes, and the chapter's comparison table is incomplete without it.
  A short section contrasting its isolation with a process pool's cost would fit the existing structure.
  The 3.12 per-interpreter GIL (PEP 684) is the groundwork for this and belongs in the same passage.
  *Rechecked 2026-09-29: partly covered (Chapters/19_Techniques--Concurrency.md:1533-1576 (Subinterpreters section, InterpreterPoolExecutor, PEP 684 at 1541)); missing: concurrent.interpreters module and PEP 734 not covered.*
- **`pathlib.Path.copy()`, `copy_into()`, `move()`, `move_into()`, and `Path.info`.** **Mention.**
  The book uses `pathlib` in eight chapters; a reader who would otherwise use `shutil`
  should know these exist.

## Python 3.13

## Python 3.12

## Python 3.11

## Python 3.10

## Python 3.9

## Python 3.8

## Python 3.7

## Python 3.6

## Python 3.5

## Python 3.4

## Python 3.3

- **Implicit namespace packages (PEP 420).** Chapter 6 mentions namespace packages.
  **Verify** it says why they exist and what goes wrong when a directory silently becomes one,
  which is a common confusion.
  *Rechecked 2026-09-29: partly covered (Chapters/06_Foundations--Modules_and_Packages.md:191-193); missing: says a directory can be imported; does not say why they exist or what goes wrong.*

## Python 3.2

## Python 3.1

## Python 3.0

Almost everything here is simply Python now, and the Python 2 comparison would only date the text.
The value is historical framing on three items:

---

## One structural suggestion

Several of these items are historical rather than instructional:
when annotations got meaning, why `OrderedDict` still exists, why `TypeAlias` gave way to `type`,
why the future import for annotations is no longer needed.
Scattering them through chapters adds noise to each one.

An alternative is a short appendix, roughly "How Python Got Here,"
tracing the features the book depends on back to the release that introduced them.
It would give you one place for the version-history sentences,
let each chapter stay focused on the current form,
and give a reader a map for the older code they will meet outside the book.
It also ages well: a new release adds a row rather than forcing edits in ten chapters.
