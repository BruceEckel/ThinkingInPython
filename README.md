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

I'm doing as much as I can using Claude; after that my plan is to do an edit/rewrite pass.
In the meantime I hope it's useful.

---

## Edit checklist

Two passes per chapter: my own edit pass (**Edited**), then incorporating
Claude's review and re-checking (**Reviewed**). Incomplete reviews live in the
`REVIEW_NN.md` files at the repo root.
Delete the review file and mark a cell `X` when that item is done.

### Draft 1

| Chapter | Edited | Reviewed |
|---------|:------:|:--------:|
| 01_Introduction.md                  | | |
| 02_Tour.md                          |X|X|
| 03_Containers.md                    |X| |
| 04_Control_Flow.md                  | | |
| 05_Functions.md                     |X|X|
| 06_Modules_and_Packages.md          |X| |
| 07_Classes.md                       |X| |
| 08_Static_Typing.md                 |X| |
| 09_Class_Attributes_and_Cleanup.md  |X| |
| 10_Testing.md                       |X| |
| 11_Data_Classes_as_Types.md         |X| |
| 12_Pattern_Matching.md              |X| |
| 13_Functional_Error_Handling.md     |X|X|
| 14_Decorators.md                    |X|X|
| 15_Context_Managers.md              | | |
| 16_Comprehensions.md                |X| |
| 17_Metaprogramming.md               |X| |
| 18_Performance.md                   | | |
| 19_Rethinking_Objects.md            | | |
| 20_The_Pattern_Concept.md           | | |
| 21_Data_Transfer_Objects.md         | | |
| 22_Singleton.md                     | | |
| 23_Template_Method.md               | | |
| 24_Surrogate.md                     | | |
| 25_State_Machines.md                | | |
| 26_Iterators.md                     | | |
| 27_Factory.md                       | | |
| 28_Function_Objects.md              | | |
| 29_Changing_the_Interface.md        | | |
| 30_Observer.md                      | | |
| 31_Multiple_Dispatching.md          | | |
| 32_Visitor.md                       | | |
| 33_Pattern_Refactoring.md           | | |
| 34_Simulation.md                    | | |
