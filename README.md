<h1 align="center"><img src="resources/static/favicon.svg"
  width="32" alt=""> Thinking in Python</h1>
<h3 align="center"><em>Fluency, Types, and Design</em></h3>
<p align="center">
  <img src="resources/static/cover-art.jpg" width="560"
       alt="A python coiled into an infinity sign, swallowing its own tail">
</p>
<h3 align="center">Bruce Eckel</h3>

An intermediate-to-advanced book for experienced programmers.
Includes a fast introduction for programmers from other languages.

## Read the Book Online

[ThinkingInPython.com](https://thinkinginpython.com/)

## Download the Book

The latest release, rebuilt from the current book source:

- [PDF](https://github.com/BruceEckel/ThinkingInPython/releases/latest/download/ThinkingInPython.pdf)
- [EPUB](https://github.com/BruceEckel/ThinkingInPython/releases/latest/download/ThinkingInPython-color.epub)
  with color syntax highlighting, for phone and tablet reading apps.
- [EPUB for e-ink readers](https://github.com/BruceEckel/ThinkingInPython/releases/latest/download/ThinkingInPython-eink.epub),
  which marks code with bolding instead of color.
- Step-by-step guides, simplest way first, to reading it on a
  [Kindle](https://github.com/BruceEckel/ThinkingInPython/releases/latest/download/kindle-uploading.txt),
  an [iPad](https://github.com/BruceEckel/ThinkingInPython/releases/latest/download/ipad-uploading.txt),
  an [Android phone or tablet](https://github.com/BruceEckel/ThinkingInPython/releases/latest/download/android-uploading.txt),
  a [computer](https://github.com/BruceEckel/ThinkingInPython/releases/latest/download/computer-reading.txt),
  or a [Kobo or other EPUB e-reader](https://github.com/BruceEckel/ThinkingInPython/releases/latest/download/ereader-uploading.txt).

All versions are on the
[releases page](https://github.com/BruceEckel/ThinkingInPython/releases).

## Examples and Solutions

Every listing in the book is a real file that runs, and the book's Markdown
source is where it lives. A listing is a fenced `python` block whose first
line is a `# name.py` comment. Everything below is extracted from those
blocks, so the code you read is the code that runs.

| Directory | What is in it |
|---|---|
| `Chapters/` | The book, one Markdown file per chapter. The source of truth. |
| `Examples/` | The book's listings, one directory per chapter (`Examples/07_Foundations--Classes/`), each file named the way the book names it (`property_setter.py`). |
| `Examples/utils/` | Helpers that several chapters import, such as `display.py` and `benchmark.py`. Not a chapter. |
| `Solutions/` | Worked answers to the exercises, one Markdown file per chapter, numbered to match that chapter's exercise list. |
| `SolutionsCode/` | The solution listings extracted to `.py` files, the same way `Examples/` is. |

### Reading a listing

When a chapter names `property_setter.py`, that file is in the chapter's
`Examples/` directory, byte for byte as printed. A `#:` comment holds the
output of the statement above it:

```python
c = Circle(10)
print(c.radius)
#: 10
print(c.area)
#: 314.159
```

The build runs every listing and compares its actual stdout against these
markers, so a marker in the book is never out of date with the code.

### Working the exercises

Each chapter ends with exercises that name the listing to start from
("Add a method `shrink(self, factor)` to `Circle` in `property_setter.py`").
Copy that file, change it, run it. Then compare with the numbered answer in
that chapter's `Solutions/` file. Each solution is self-contained: it
repeats whatever it needs from the chapter rather than importing it, so you
can read or run one on its own.

`Examples/` and `SolutionsCode/` are regenerated from the Markdown, so
`make sync` discards edits made there. Experiment in them freely, but copy
anything you want to keep somewhere outside those two trees.

## Setup

### Install

1. Clone this repository.
2. You need a `make` command. This is preinstalled on Linux and macOS
   (macOS: install Xcode Command Line Tools if it's missing).
   For Windows: `winget install ezwinports.make`
3. Install [uv](https://docs.astral.sh/uv/).
4. Run `uv sync` once. This creates `.venv` and installs the pinned
   Python (3.15+) and dev tools automatically. No manual Python install is needed.
5. Run `make tools-check` to verify that the essential tools are available.

That is everything you need to run and test the examples and the solutions.
`make doctor` diagnoses the two environment problems that bite in practice,
a stale `uv` stuck on an old Python prerelease and (on Windows) a process
holding `.venv` open.

Building the book itself needs more. `make site`, `make local`, and
`make serve` want `pandoc` on your PATH, `make pdf` also wants `typst`, and
`make prose` wants the standalone `vale` binary. `make tools-check-full`
checks for those too. See
[tools/README](https://github.com/BruceEckel/ThinkingInPython/blob/master/tools/README.md)
for details and install links.

Type `make` to see every target. In a terminal that opens a picker: arrow
keys choose, Enter runs, `?` shows a target's full documentation.

### Run and test everything

The commands below rebuild `build/examples/` and `build/solutions/` from
the Markdown first, so they always test the current book, never a stale
copy. Timings are from a recent desktop machine.

| Command | What it does |
|---|---|
| `make run` | Executes every example file and reports failures. About 15 seconds. |
| `make test` | Runs the book's `pytest` examples, the `test_*.py` files. About 5 seconds. |
| `make ty` | Type-checks every example. Must come out clean. |
| `make lint` | PEP8-lints every example with `ruff`. Must come out clean. |
| `make solutions-test` | Runs the solutions' `pytest` examples. About 3 seconds. |
| `make solutions-ty`, `make solutions-lint` | The same two checks over `build/solutions/`. |
| `make solutions-gate` | Every solutions check at once: exercise numbering, drift, output markers, types, lint, tests. |
| `make gate` | Every check over both trees. This is the one to run before committing. |

A first run pays for downloading the pinned Python and the dev tools; after
that `make run` is the slowest of these.

A few examples cannot run unattended, because they open a window, wait
for input, or loop forever. `make run` reports those as "Can't run
unattended" rather than as failures. They are listed in
`tools/data/norun.txt`, and running one by hand is the way to see it work.

Two notes on `make gate`. It runs the solutions checks first, as a
prerequisite, so a failure there hides any `Chapters/` failure behind it.
`make sweep` runs everything and reports every failure instead of stopping
at the first. And `gate` refreshes generated content in place: it rewraps
prose to one sentence per line and rewrites any `#:` marker whose listing
now prints something else. Expect `git diff Chapters/` to show those.

### Work on one chapter

`make check-ch CH=07` runs the whole code-example gate against one chapter
in about a second: extract, output markers, listing format, types, lint,
tests. `CH` takes a number or a filename stem. This is the edit loop.
`make gate` is still what catches breakage across chapters.

### Run one example by hand

Run it from its own chapter directory, so that the sibling modules and data
files it opens resolve the way the book assumes:

```bash
cd Examples/07_Foundations--Classes
uv run python property_setter.py
```

A listing that imports a shared helper (`from display import display_object`)
also needs `Examples/utils` on the import path:

```bash
PYTHONPATH=../utils uv run python display_simple.py
```

In PowerShell that first line is `$env:PYTHONPATH = "../utils"`.

Use `uv run python`, not a bare `python`. A `python` already on your PATH is
usually an older release, and these examples use Python 3.15 syntax.

---

## History

I started this book in 2008 and after a few years it kind of drifted to a stop. I think part of the
problem was that I wanted to move the design patterns work I had done in Java into Python and
even then I was beginning to become uncertain about OOP (The material is still there, translated,
but it is preceded by a chapter explaining my OOP misgivings).

I had forgotten about this book but (especially at Pycons) people would occasionally come up to me
and mention that they had gotten some value out of it. Because of the condition of the book,
which still had a number of examples that were still in Java (!), I found this embarrassing.

In June 2026 I decided to see what the Claude AI could do with it, and in short order it had brought
everything up to Python 3.15, with type annotations, passing standards checkers, cleaning up prose, etc.
I began going back through my Pycon presentations and blog posts and adding those.
At the moment it is in decent shape and you can read it online:
https://bruceeckel.github.io/ThinkingInPython/

---

## Edit checklist

### Post-AI edit (Began August 12, 2026)

After doing everything I could think of to do with AI.
My current strategy is to edit a chapter, ask AI to derive guidelines from my edits,
then AI-apply those guidelines throughout the book before editing the next chapter.
Hypothetically this will produce asymptotically-decreasing edits as I proceed through the book.

Note that I am not starting at the beginning, but picking up where I left off during the "Serious Edit."

| Chapter | Edited |
|---------|:------:|
| 01_Introduction.md                        | |
| 02_Foundations--Tour.md                   | |
| 03_Foundations--Containers.md             | |
| 04_Foundations--Control_Flow.md           | |
| 05_Foundations--Functions.md              | |
| 06_Foundations--Modules_and_Packages.md   | |
| 07_Foundations--Classes.md                | |
| 08_Foundations--Static_Types.md           | |
| 09_Foundations--Class_Attributes.md       | |
| 10_Foundations--Cleanup.md                | |
| 11_Techniques--Testing.md                 | |
| 12_Techniques--Data_Classes_as_Types.md   | |
| 13_Techniques--Pattern_Matching.md        | |
| 14_Techniques--Decorators.md              | |
| 15_Techniques--Context_Managers.md        | |
| 16_Techniques--Comprehensions.md          | |
| 17_Techniques--Metaprogramming.md         | |
| 18_Techniques--Performance.md             | |
| 19_Techniques--Concurrency.md             | |
| 20_Patterns--Rethinking_Objects.md        | |
| 21_Patterns--Design_Patterns.md           | |
| 22_Patterns--Data_Transfer_Objects.md     | |
| 23_Patterns--Iterators.md                 | |
| 24_Patterns--Singleton.md                 | |
| 25_Patterns--Template_Method.md           |X|
| 26_Patterns--Surrogate.md                 |O|
| 27_Patterns--Factory.md                   |r|
| 28_Patterns--Function_Objects.md          |r|
| 29_Patterns--Changing_the_Interface.md    | |
| 30_Patterns--Observer.md                  | |
| 31_Patterns--State_Machines.md            | |
| 32_Patterns--Multiple_Dispatching.md      | |
| 33_Patterns--Visitor.md                   | |
| 34_Patterns--Composite_and_Interpreter.md | |
| 35_Patterns--Flyweight.md                 | |
| 36_Patterns--Memento.md                   | |
| 37_Patterns--Pattern_Refactoring.md       | |
| 38_Patterns--Simulation.md                | |
| 39_Patterns--Pattern_Catalog.md           | |
| 40_Functional--Foundations.md             | |
| 41_Functional--Toolkits.md                | |
| 42_Functional--Error_Handling.md          | |
| 43_Functional--Confidence.md              | |
| 44_Effects--Effect_Management.md          | |
| 45_Effects--Generators.md                 | |
| 46_Effects--Stateless.md                  | |
| 47_Effects--Stateless_in_Practice.md      | |


### Serious Edit

The first serious edit pass.

| Chapter | Edited |
|---------|:------:|
| 01_Introduction.md                        |X|
| 02_Foundations--Tour.md                   |X|
| 03_Foundations--Containers.md             |X|
| 04_Foundations--Control_Flow.md           |X|
| 05_Foundations--Functions.md              |X|
| 06_Foundations--Modules_and_Packages.md   |X|
| 07_Foundations--Classes.md                |X|
| 08_Foundations--Static_Types.md           |X|
| 09_Foundations--Class_Attributes.md       |X|
| 10_Foundations--Cleanup.md                |X|
| 11_Techniques--Testing.md                 |X|
| 12_Techniques--Data_Classes_as_Types.md   |X|
| 13_Techniques--Pattern_Matching.md        |X|
| 14_Techniques--Decorators.md              |X|
| 15_Techniques--Context_Managers.md        |X|
| 16_Techniques--Comprehensions.md          |X|
| 17_Techniques--Metaprogramming.md         |X|
| 18_Techniques--Performance.md             |X|
| 19_Techniques--Concurrency.md             |X|
| 20_Patterns--Rethinking_Objects.md        |X|
| 21_Patterns--Design_Patterns.md           |X|
| 22_Patterns--Data_Transfer_Objects.md     |X|
| 23_Patterns--Iterators.md                 |X|
| 24_Patterns--Singleton.md                 |X|
| 25_Patterns--Template_Method.md           | |
| 26_Patterns--Surrogate.md                 | |
| 27_Patterns--Factory.md                   | |
| 28_Patterns--Function_Objects.md          | |
| 29_Patterns--Changing_the_Interface.md    | |
| 30_Patterns--Observer.md                  | |
| 31_Patterns--State_Machines.md            | |
| 32_Patterns--Multiple_Dispatching.md      | |
| 33_Patterns--Visitor.md                   | |
| 34_Patterns--Composite_and_Interpreter.md | |
| 35_Patterns--Flyweight.md                 | |
| 36_Patterns--Memento.md                   | |
| 37_Patterns--Pattern_Refactoring.md       | |
| 38_Patterns--Simulation.md                | |
| 39_Patterns--Pattern_Catalog.md           | |
| 40_Functional--Foundations.md             | |
| 41_Functional--Toolkits.md                | |
| 42_Functional--Error_Handling.md          | |
| 43_Functional--Confidence.md              | |
| 44_Effects--Effect_Management.md          | |
| 45_Effects--Generators.md                 | |
| 46_Effects--Stateless.md                  |X|
| 47_Effects--Stateless_in_Practice.md      | |

### Initial Draft

This draft gets all the chapters and sections in place and ready for a serious edit pass.
Two passes: my own edit pass (**Edited**), then incorporating
Claude's review and re-checking (**Reviewed**).

The 🔴 denotes an unfinished chapter, so expect that to be in greater disarray.

| Chapter | Edited | Reviewed |
|---------|:------:|:--------:|
| 01_Introduction.md                        |X|X|
| 02_Foundations--Tour.md                   |X|X|
| 03_Foundations--Containers.md             |X|X|
| 04_Foundations--Control_Flow.md           |X|X|
| 05_Foundations--Functions.md              |X|X|
| 06_Foundations--Modules_and_Packages.md   |X|X|
| 07_Foundations--Classes.md                |X|X|
| 08_Foundations--Static_Types.md           |X|X|
| 09_Foundations--Class_Attributes.md       |X|X|
| 10_Foundations--Cleanup.md                |X|X|
| 11_Techniques--Testing.md                 |X|X|
| 12_Techniques--Data_Classes_as_Types.md   |X|X|
| 13_Techniques--Pattern_Matching.md        |X|X|
| 14_Techniques--Decorators.md              |X|X|
| 15_Techniques--Context_Managers.md        |X|X|
| 16_Techniques--Comprehensions.md          |X|X|
| 17_Techniques--Metaprogramming.md         |X|X|
| 18_Techniques--Performance.md             |X|X|
| 19_Techniques--Concurrency.md             |X|X|
| 20_Patterns--Rethinking_Objects.md        |X|X|
| 21_Patterns--Design_Patterns.md           |X|X|
| 22_Patterns--Data_Transfer_Objects.md     |X|X|
| 23_Patterns--Iterators.md                 |X|X|
| 24_Patterns--Singleton.md                 |X|X|
| 25_Patterns--Template_Method.md           |X|X|
| 26_Patterns--Surrogate.md                 |X|X|
| 27_Patterns--Factory.md                   |X|X|
| 28_Patterns--Function_Objects.md          |X|X|
| 29_Patterns--Changing_the_Interface.md    |X|X|
| 30_Patterns--Observer.md                  |X|X|
| 31_Patterns--State_Machines.md            |X|X|
| 32_Patterns--Multiple_Dispatching.md      |X|X|
| 33_Patterns--Visitor.md                   |X|X|
| 34_Patterns--Composite_and_Interpreter.md |X|X|
| 35_Patterns--Flyweight.md                 |X|X|
| 36_Patterns--Memento.md                   |X|X|
| 37_Patterns--Pattern_Refactoring.md       |X|X|
| 38_Patterns--Simulation.md                |X|X|
| 39_Patterns--Pattern_Catalog.md           |X|X|
| 40_Functional--Foundations.md             |X|X|
| 41_Functional--Toolkits.md                |X|X|
| 42_Functional--Error_Handling.md          |X|X|
| 43_Functional--Confidence.md              |X|X|
| 44_Effects--Effect_Management.md          |🔴|🔴|
| 45_Effects--Generators.md                 |🔴|🔴|
| 46_Effects--Stateless.md                  |X|X|
| 47_Effects--Stateless_in_Practice.md      |🔴|🔴|
