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
| 03_Containers_and_Control_Flow.md   |X|X|
| 04_Functions.md                     |X| |
| 05_Modules_and_Packages.md          |X| |
| 06_Classes.md                       |X| |
| 07_Static_Typing.md                 |X| |
| 08_Class_Attributes_and_Cleanup.md  |X| |
| 09_Testing.md                       |X| |
| 10_Data_Classes_as_Types.md         |X| |
| 11_Pattern_Matching.md              |X| |
| 12_Functional_Error_Handling.md     |X|X|
| 13_Decorators.md                    |X|X|
| 14_Context_Managers.md              | | |
| 15_Comprehensions.md                |X| |
| 16_Metaprogramming.md               |X| |
| 17_Performance.md                   | | |
| 18_Rethinking_Objects.md            | | |
| 19_The_Pattern_Concept.md           | | |
| 20_Data_Transfer_Objects.md         | | |
| 21_Singleton.md                     | | |
| 22_Template_Method.md               | | |
| 23_Surrogate.md                     | | |
| 24_State_Machines.md                | | |
| 25_Iterators.md                     | | |
| 26_Factory.md                       | | |
| 27_Function_Objects.md              | | |
| 28_Changing_the_Interface.md        | | |
| 29_Observer.md                      | | |
| 30_Multiple_Dispatching.md          | | |
| 31_Visitor.md                       | | |
| 32_Pattern_Refactoring.md           | | |
| 33_Simulation.md                    | | |
