Thinking in Python
==================

> For the book examples, clone this directory.

> To test the examples, follow [tools/README](https://github.com/BruceEckel/ThinkingInPython/blob/master/tools/README.md).

I started this book in 2008 and after a few years it kind of drifted to a stop. I think part of the
problem was that I wanted to move the design patterns work I had done in Java into Python and
even then I was beginning to become uncertain about OOP (The material is still there, translated,
but it is preceded by a chapter explaining my OOP misgivings).

I had forgotten about this book but (especially at Pycons) people would occasionally come up to me
and mention that they had gotten some value out of it. Because of the condition of the book,
which still had a number of examples that were still in Java (!), I found this embarrassing.

In June 2026 I decided to see what the Claude AI could do with it, and in short order it had brought
everything up to Python 3.14, with type annotations, passing standards checkers, cleaning up prose, etc.
I began going back through my Pycon presentations and blog posts and adding those.
At the moment it is in decent shape and you can read it online:
https://bruceeckel.github.io/ThinkingInPython/

---

## Edit checklist

Two passes per draft: my own edit pass (**Edited**), then incorporating
Claude's review and re-checking (**Reviewed**). Incomplete reviews live in the
`REVIEW_NN.md` files at the repo root.
Delete the review file and mark a cell `X` when that item is done.

### Draft 1

| Chapter | Edited | Reviewed |
|---------|:------:|:--------:|
| 01_Introduction.md              | | |
| 02_Tour.md                      |X|X|
| 03_Containers.md                |X| |
| 04_Control_Flow.md              |X| |
| 05_Functions.md                 |X|X|
| 06_Modules_and_Packages.md      |X| |
| 07_Classes.md                   |X| |
| 08_Static_Typing.md             |X| |
| 09_Class_Attributes.md          |X| |
| 10_Cleanup.md                   |X| |
| 11_Testing.md                   |X| |
| 12_Data_Classes_as_Types.md     |X| |
| 13_Pattern_Matching.md          |X| |
| 14_Functional_Error_Handling.md |X|X|
| 15_Decorators.md                |X|X|
| 16_Context_Managers.md          |X| |
| 17_Comprehensions.md            |X| |
| 18_Metaprogramming.md           |X| |
| 19_Performance.md               | | |
| 20_Rethinking_Objects.md        |X| |
| 21_The_Pattern_Concept.md       |X| |
| 22_Data_Transfer_Objects.md     |X| |
| 23_Singleton.md                 |X| |
| 24_Template_Method.md           |X| |
| 25_Surrogate.md                 | | |
| 26_State_Machines.md            | | |
| 27_Iterators.md                 | | |
| 28_Factory.md                   | | |
| 29_Function_Objects.md          | | |
| 30_Changing_the_Interface.md    | | |
| 31_Observer.md                  | | |
| 32_Multiple_Dispatching.md      | | |
| 33_Visitor.md                   | | |
| 34_Pattern_Refactoring.md       | | |
| 35_Simulation.md                | | |
| 36_Functional_Programming.md    | | |
| A_Pattern_Catalog.md            |X| |
