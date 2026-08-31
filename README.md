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

## Setup

1. Clone this repository.
2. You need a `make` command. This is preinstalled on Linux and macOS
   (macOS: install Xcode Command Line Tools if it's missing).
   For Windows: `winget install ezwinports.make`
3. Install [uv](https://docs.astral.sh/uv/).
4. Run `uv sync` once. This creates `.venv` and installs the pinned
   Python (3.15+) and dev tools automatically. No manual Python install is needed.
5. Run `make tools-check` to verify that the essential tools are available.

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
