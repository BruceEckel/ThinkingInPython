<h1 align="center"><img src="resources/static/favicon.svg"
  width="32" alt=""> Thinking in Python</h1>
<h3 align="center"><em>Fluency, Types, and Design</em></h3>
<p align="center">
  <img src="resources/static/cover-art.jpg" width="600"
       alt="A python coiled into an infinity sign, swallowing its own tail">
</p>
<h3 align="center">Bruce Eckel</h3>

An intermediate-to-advanced book for experienced programmers.
Opens with a condensed introduction for programmers coming from other languages.

> ***Although you will find the book useful in its current form,
> be aware that it is under development.***

## Read the Book Online

[ThinkingInPython.com](https://bruceeckel.github.io/ThinkingInPython)

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

## Support the Book

Thinking in Python is free. If it has helped you and you'd like to
support the work, you can do that on
[GitHub Sponsors](https://github.com/sponsors/BruceEckel) or
[Ko-fi](https://ko-fi.com/bruceeckel). No obligation, and no
difference in what you get.

## Examples and Solutions

Every listing in the book is a real file that runs. You will find it in
`Examples/`, in its chapter's directory, under the name the book gives it.
The answers to the exercises are in `Solutions/`.

| Directory | Contents |
|---|---|
| `Examples/` | The book's listings, one directory per chapter (`Examples/07_Foundations--Classes/`), each file named the way the book names it (`property_setter.py`). |
| `Examples/utils/` | Helpers that several chapters import, such as `display.py` and `benchmark.py`. Not a chapter. |
| `Solutions/` | Worked answers to the exercises, one Markdown file per chapter, numbered to match that chapter's exercise list. |
| `SolutionsCode/` | The solution listings extracted to `.py` files, the same way `Examples/` is. |
| `Chapters/` | The book itself, one Markdown file per chapter. |

The build generates both code trees from `Chapters/` and `Solutions/`,
where each listing is a fenced `python` block whose first line is a
`# name.py` comment. The code you read is therefore the code that runs.

### Reading a listing

A `#:` marker comment holds the output of the statement(s) above it:

```python
c = Circle(10)
print(c.radius)
#: 10
print(c.area)
#: 314.159
```

The build runs every listing and compares its stdout against these markers,
so a marker in the book always shows what the code prints.

### Working the exercises

Each chapter ends with exercises that name the listing to start from
(e.g.: "Add a method `shrink(self, factor)` to `Circle` in `property_setter.py`").
Copy the example file, change it, run it. Then compare with the numbered answer in
that chapter's `Solutions/` file. Each solution is self-contained: it
repeats whatever it needs from the chapter rather than importing it, so you
can read or run one on its own.

`tip sync` regenerates `Examples/` and `SolutionsCode/` from the Markdown,
discarding any edits you made there. Experiment in them freely, but keep
anything you want to save outside those two trees.

## Setup

You'll need to do this to experiment with the examples and exercises.

### Install

1. Clone this repository onto your local machine:

   ```sh
   git clone https://github.com/BruceEckel/ThinkingInPython.git
   ```

   or, with the [GitHub CLI](https://cli.github.com/):

   ```sh
   gh repo clone BruceEckel/ThinkingInPython
   ```

2. Install [uv](https://docs.astral.sh/uv/):
   - Linux, and macOS without Homebrew:

     ```sh
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```

   - macOS with Homebrew:

     ```sh
     brew install uv
     ```

   - Windows:

     ```sh
     winget install --id=astral-sh.uv -e
     ```

3. The book's commands go through `tip`, a task runner written in Python
   that comes with the repository.
   From the repository's root directory, put a `tip` command on your PATH:

   ```sh
   uv tool install --editable .
   ```

   If your shell cannot find `tip` afterward, `uv tool update-shell` adds
   uv's tool directory to your PATH.
   This works the same on Windows, macOS, and Linux.
   Because the install is editable, a change under `tools/` takes effect
   immediately.

   The install is optional. Without it, put `uv run` in front of each
   command, as in `uv run tip tools-check`, which works from anywhere
   inside the repository. The rest of this README writes the short form,
   `tip tools-check`.

4. Verify the essential tools:

   ```sh
   tip tools-check
   ```

   The book's environment needs no separate install step.
   Every `tip` target goes through `uv run`,
   and the first one you run creates `.venv` and installs the pinned
   Python (3.15+) and the dev tools before it does anything else.
   `uv sync` builds the same environment explicitly,
   for when you need `.venv` before running a target,
   such as pointing an editor at its interpreter.
   On WSL, clone into the Linux filesystem (under `~`), not into a
   Windows checkout under `/mnt/c`. A `.venv` cannot be shared between
   Windows and Linux: each side's `uv` tries to rebuild it for
   itself and fails when the other side has it open. A clone under
   `/mnt/c` also runs every command through the Windows filesystem
   bridge, which turns a three-second install into a minute and slows
   `tip verify` the same way.

That is everything you need to run and test the examples and the solutions.
`tip doctor` diagnoses the two common environment problems:
a stale `uv` stuck on an old Python prerelease, and (on Windows) a process
holding `.venv` open.

Type `tip` to see every target; it opens a picker where
arrow keys choose, Enter runs, and `?` shows a target's full documentation.
Piped into another command, `tip` prints the same list by category instead,
and `tip help style` shows one section of it.
Targets that take a setting use `NAME=value`, as in `tip check-ch CH=07`.
`tip` echoes each command before it runs it, and ends with a timing line
such as `tip verify: 1m 32s`.
`tools/tasks.py` defines every target.

### Run and test everything

The commands below rebuild `build/examples/` and `build/solutions/` from
the Markdown chapters, so they always test the current book, never a stale
copy.

- Execute every example file and report failures:

  ```sh
  tip run
  ```

- Run the book's `pytest` examples, the `test_*.py` files:

  ```sh
  tip test
  ```

- Type-check every example (must come out clean):

  ```sh
  tip ty
  ```

- PEP8-lint every example with `ruff` (must come out clean):

  ```sh
  tip lint
  ```

- Each of those four covers `build/solutions/`, the extracted exercise
  answers, in the same run.

- Run every solutions check at once (exercise numbering, drift, output markers, types, lint, runs, tests):

  ```sh
  tip solutions-gate
  ```

- Run every check over both trees, before you commit:

  ```sh
  tip gate
  ```

A first run also downloads the pinned Python and the dev tools.

To run one example instead of all of them, see
[Run one example by hand](#run-one-example-by-hand) below.

A few examples cannot run unattended because they open a window, wait for
input, or loop forever. `tip run` reports those as "Can't run unattended"
rather than as failures. `tools/data/norun.txt` lists them. Run one by hand
to watch it work, or open all the windowed ones at once:

```sh
tip by-hand
```

Try each window and close it. The command prints a line as each one
closes, and the traceback of any that failed.

`tip gate` runs the solutions checks first, as a prerequisite, so a
failure there hides every `Chapters/` failure behind it. `tip sweep` runs
everything and reports them all instead of stopping at the first. `gate`
also refreshes generated content in place: it rewraps prose to one sentence
per line, and it rewrites any `#:` marker whose listing now prints
something else. Expect `git diff Chapters/` to show both.

### Work on one chapter

Run the whole code-example gate against one chapter instead of all 47:

```sh
tip check-ch CH=07
```

The gate extracts the chapter, then checks output markers, listing format,
types, lint, and tests.
`CH` takes a number or a filename stem. Make this your edit loop.
Only `tip gate` catches breakage across chapters.

### Run one example by hand

`tip run-one` runs any single example from the repo root and shows its
output. Give it the file's name, or as much of its path as you care to
type:

```sh
tip run-one deque_timing
```

```sh
tip run-one Examples/07_Foundations--Classes/property_setter.py
```

`tip run-one F=deque_timing` is the same command in its older form.

It sets up what the example expects, and prints the commands it stood in
for, because those are what you type when `tip` is not at hand:

```sh
cd Examples/03_Foundations--Containers
PYTHONPATH=../utils uv run python deque_timing.py
```

Both lines matter. An example reads its sibling modules and data files by
relative path, so it must run from its own chapter directory. About 70 of
them also import a shared helper that lives in `Examples/utils`
(`from benchmark import report`), so that directory has to be on the
import path. Miss the second line and Python says:

```
ModuleNotFoundError: No module named 'benchmark'
```

PowerShell sets the variable in a statement of its own:

```powershell
cd Examples/03_Foundations--Containers
$env:PYTHONPATH = "../utils"
uv run python deque_timing.py
```

`tip run-one` prints whichever form fits your shell.

Use `uv run python`, not a bare `python`. A `python` already on your PATH is
usually an older release, and these examples use Python 3.15 syntax.

### Optional: Building the Book

Building the book itself needs more. `tip site`, `tip local`, and
`tip serve` need `pandoc` on your PATH, `tip pdf` also needs `typst`, and
`tip prose` needs the standalone `vale` binary.
Check for all of them:

```sh
tip tools-check-full
```

See
[tools/README](https://github.com/BruceEckel/ThinkingInPython/blob/master/tools/README.md)
for details and install links.

---

## History

I started this book in 2008 and by 2011 it had drifted to a stop. I think part of the
problem was that I wanted to move the design patterns work I had done in Java into Python and
even then I was beginning to become uncertain about OOP (The material is still there, translated,
but it is preceded by a chapter explaining my OOP misgivings).

I had forgotten about this book but (especially at Pycons) people would occasionally come up to me
and mention that they had gotten some value out of it. Because of the condition of the book,
which still had a number of examples that were still in Java (!), I found this embarrassing.

In June 2026 I decided to see what the Claude AI could do with it, and in short order it had brought
everything up to Python 3.15, with type annotations, passing standards checkers, cleaning up prose, etc.
I began going back through my Pycon presentations and blog posts and adding those.

---

## Edit checklist

For my own bookkeeping.

| Chapter | Edit State |
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
| 26_Patterns--Surrogate.md                 |X|
| 27_Patterns--Factory.md                   |X|
| 28_Patterns--Function_Objects.md          |X|
| 29_Patterns--Changing_the_Interface.md    |X|
| 30_Patterns--Observer.md                  |_|
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
| A_Effect_Tracking.md                      | |
| B_An_Effect_Checker.md                    | |
