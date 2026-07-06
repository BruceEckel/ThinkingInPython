Thinking in Python
==================

An intermediate-level book for experienced programmers.
Includes a fast introduction for programmers from other languages.

## Setup

1. Clone this repository.
2. You need a `make` command. This is preinstalled on Linux and macOS
   (macOS: install Xcode Command Line Tools if it's missing).
   For Windows: `winget install ezwinports.make`
3. Install [uv](https://docs.astral.sh/uv/).
4. Run `uv sync` once. This creates `.venv` and installs the pinned
   Python (3.15+) and dev tools automatically. No manual Python install is needed.
5. Run `make check-tools` to verify that the essential tools are available.

Type `make` to see the options.

These are optional, but if you want to run
`make site`, `make local`, and `make serve`, you also need `pandoc` on your PATH.
`make prose` needs the standalone `vale` binary. See
[tools/README](https://github.com/BruceEckel/ThinkingInPython/blob/master/tools/README.md)
for details and install links.

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

Two passes per draft: my own edit pass (**Edited**), then incorporating
Claude's review and re-checking (**Reviewed**). Incomplete reviews live in the
`REVIEW_NN.md` files at the repo root.
Delete the review file and mark a cell `X` when that item is done.
The 🔴 denotes an unfinished chapter, so expect that to be in greater disarray.

### Draft (First Pass)

This draft gets all the chapters and sections in place and ready for a serious edit pass.

| Chapter | Edited | Reviewed |
|---------|:------:|:--------:|
| 01_Introduction.md              |X|X|
| 02_Tour.md                      |X|X|
| 03_Containers.md                |X|X|
| 04_Control_Flow.md              |X|X|
| 05_Functions.md                 |X|X|
| 06_Modules_and_Packages.md      |X|X|
| 07_Classes.md                   |X|X|
| 08_Static_Typing.md             |X|X|
| 09_Class_Attributes.md          |X|X|
| 10_Cleanup.md                   |X|X|
| 11_Testing.md                   |X|X|
| 12_Data_Classes_as_Types.md     |X|X|
| 13_Pattern_Matching.md          |X|X|
| 14_Functional_Error_Handling.md |X|X|
| 15_Decorators.md                |X|X|
| 16_Context_Managers.md          |X|X|
| 17_Comprehensions.md            |X|X|
| 18_Metaprogramming.md           |X|X|
| 19_Performance.md               |X|X|
| 20_Concurrency.md               |X| |
| 21_Rethinking_Objects.md        |X|X|
| 22_The_Pattern_Concept.md       |X|X|
| 23_Data_Transfer_Objects.md     |X|X|
| 24_Singleton.md                 |X|X|
| 25_Template_Method.md           |X|X|
| 26_Surrogate.md                 |X|X|
| 27_State_Machines.md            |X|X|
| 28_Iterators.md                 |X|X|
| 29_Factory.md                   |X|X|
| 30_Function_Objects.md          |X|X|
| 31_Changing_the_Interface.md    |X|X|
| 32_Observer.md                  |X|X|
| 33_Multiple_Dispatching.md      |X|X|
| 34_Visitor.md                   |X|X|
| 35_Composite_and_Interpreter.md |X| |
| 36_Flyweight.md                 |X| |
| 37_Memento.md                   | | |
| 38_Pattern_Refactoring.md       |X|X|
| 39_Simulation.md                | | |
| 40_Pattern_Catalog.md           |X|X|
| 41_Functional_Programming.md    |🔴|🔴|
| 42_Effect_Management.md         | | |
