# Publishing Plan: *Thinking in Python* (project history)

A historical record of the plan that took this book from a partial, part-Java
state to its current form. It is no longer an active backlog. For the current
state of the book and the open editorial questions, see `REVIEW.md`.

## What the book is

*Thinking in Python: Insights, Idioms and Patterns* by Bruce Eckel. It began as
a conversion of the abandoned *Python 3 Patterns & Idioms* project, itself
extracted from the design-patterns material in *Thinking in Java*. Prose lives in
`Markdown/`, code examples in `Examples/`, and build scripts in `tools/`.

## Locked decisions

(See also the `book-publishing-decisions` memory.)

- **Patterns:** keep the pattern chapters but reframe each around the Pythonic
  idiom that replaces or simplifies the *GoF Design Patterns* pattern, and be honest where a
  pattern is a "language failure" in Python.
- **Python target:** 3.14+ with type hints throughout, checked with Astral's
  `ty` (not mypy).
- **Output:** clean Markdown/web only for now; no print or EPUB tooling yet.

House style and the code-example conventions are recorded in `CLAUDE.md` and
`tools/README.md`.

## The phases (all complete)

1.  **Infrastructure.** Built the example extractor and runner
    (`tools/extract_examples.py`, `run_examples.py`), the pandoc static-site
    build (`build_site.py`), and GitHub Actions CI. The Markdown is the single
    source of truth for prose and code; examples are extracted, run, and
    type-checked.
2.  **Code modernization.** Removed every Python 2 and Java leftover, added type
    hints, and brought the failing-example count from 67 to 0. Every example now
    runs and is `ty`-clean, with the book and `Examples/` in sync.
3.  **Content triage and front matter.** Rewrote the Introduction as real front
    matter (project and meta content moved to `CONTRIBUTING.md`); resolved the
    stub chapters (cut Generators and Iterators, Machine Discovery, and
    Table-Driven Code; reframed Messenger; finished Static Type Checking); and
    removed the out-of-book material that used to live in `residual/` (since
    deleted) from the build.
4.  **Pattern reframe.** Gave each pattern chapter an explicit
    Python-versus-pattern judgment: the idiom that replaces or shrinks the
    pattern, or the reason it still earns its keep.
5.  **Editorial pass.** The mechanical sweep is done (em-dashes removed, dates
    updated, cross-references resolved). The remaining work is authorial, the
    final one-voice pass, which `REVIEW.md` seeds.

## Structural evolution

The chapter set grew and was renumbered several times as conference talks were
adapted in:

- Added *Data Classes as Types* (from PyCon 2022).
- Added *Functional Error Handling* (from PyCon 2024).
- Added *Rethinking Objects* (from PyCon 2023), a skeptical look at OOP placed
  just before the patterns.
- *Initialization and Cleanup* and *Static Type Checking* were briefly folded
  into a single "Python for Programmers" chapter, then split back out as
  standalone chapters.

The book is now 31 chapters (`01`-`31`), beginning with the Introduction,
grouped into three parts that `build_site.py` injects into the table of contents:
Foundations, Techniques, and Patterns. Because example folders are named for
their chapter stem, renumbering a chapter also renames its `Examples/NN_*`
folder.
