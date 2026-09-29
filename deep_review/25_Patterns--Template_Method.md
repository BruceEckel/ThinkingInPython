> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 25_Patterns--Template_Method (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I checked each claim against its listing, the sections the chapter links (17, 20, 24, 28, and chapter 31's end of the constructor-starts-the-engine thread), the GoF text, `unittest` on the pinned interpreter, and `ty` 0.0.84 probes.
Every technical claim in the chapter holds.
The errors were in the Solutions file and in two places where the chapter's wording claimed more than the code does.
`tip verify-ch CH=25` passes 24 of 24, and the whole-book `tip verify` and `tip exercise-refs` pass in the worktree.

## Applied directly

Chapter, corrections:

- "The Anchored Algorithm": "`@final` on `run()` rejects any subclass that overrides it" read as a runtime guarantee, which the section denies three paragraphs later. Now "makes the type checker reject", and "locks the template method" is "declares that no subclass may override".
- `near_miss.py`: the set named `hooks` holds every inherited name, including `run` (the anchor) and helpers such as `report()`, and the section defines a hook as an optional step. Renamed `inherited`, in the listing and the prose.
- `faithless_step.py`: `ran = False` was a bare class-body assignment standing in for per-instance state, against the house rule. Now assigned in `__init__()`.
- `premature_engine.py`: the comment "the engine calls run()" had it backward, since `run()` is the engine. Now "In the usual order, this call runs the engine".
- "Substitutability": "An override can break that trust" introduced a list whose second item, a step left empty, is the absence of an override. The subject is now "A subclass". "Each of these failures" pointed back across a listing, so it is "Each of the three failures".
- "What Anchors the Algorithm": the Discipline bullet said no tool checks a step, but `@abstractmethod` checks that a required step exists. The bullet now says which half a tool covers.

Chapter, teaching:

- `test_template_method.py` sat after the `@abstractmethod` paragraph, a section away from the listing it tests and with no lead-in. It now follows `template_method.py`, with a sentence saying what it checks.
- The `__init_subclass__()` paragraph now says that `near_miss.py` includes the check it describes, so the reader knows the answer is coming.
- The `@abstractmethod` paragraph gained the type checker's half: `ty` reports the construction (`call-non-callable`, "Cannot instantiate abstract class"), which Solutions exercise 4 relies on.
- "Passing the Steps as Functions": added the near-miss for an optional step. A reader would write `Step | None = None` and test for `None` in the loop; the sentence names `lambda: None` as the default.
- Exercise 1: "Customize it two ways" followed by a two-item list read as though the list were the two ways. Now "Supply each of these policies twice".
- Exercise 5 is new. The hooks section holds the chapter's longest listing and had no exercise. The exercise asks what a subclass of `MyApp` with a `reports()` method does (the check refuses it, "did you mean report?") and has the reader narrow the check to the framework's own names.

Chapter, prose:

- "At runtime the decorator only sets" lost its second "only".
- "The checker sees only the decorator" is "That check depends on the decorator."
- "only a near miss produces a `TypeError`" names the condition instead.
- "The `class Typo` statement raises a `TypeError` instead of finishing too" is "also raises a `TypeError`".
- "The heuristic cuts the other way too" is "The heuristic also rejects legitimate names", and "even though" is "although".
- "leans on" is "depends on".
- The emphasis italics on "*can*" are gone.

Solutions:

- Exercise 1 implemented one of the two policies and described the other in a paragraph. It is now three listings: the framework (`exercise_1.py`), the uppercase policy both ways, and the search policy both ways.
- Exercise 1's `process()` was required and raised `NotImplementedError`; the chapter says to declare a required step with `@abstractmethod`, so `FileFramework` now does. Its hand-written `__init__()` only assigned a field. `run()` now takes the file names, as `run_file_framework()` does, so the base class stores nothing. `Search` is a record holding the word list, under an empty `__slots__` on the base.
- Exercise 2 linked *Singleton*'s cached-factory section for "eager versus lazy construction", which that section does not discuss. The link now goes to "Double-Checked Locking and Eager Creation".
- Exercise 3: "the `__init_subclass__()` technique the chapter points at" predates `near_miss.py`, which implements it. The sentence names the listing. "Template Method's central promise" is "the *Template Method*'s central guarantee", italic per the pattern-name rule.
- Exercise 4: "`pending` simply grows forever" described a run that appends twice. Now "grows on every pass".
- Exercise 5's solution is new: `exercise_5.py` shows the refusal, `exercise_5_narrow.py` the narrower check and what it gives up.
- Emphasis italics removed from "*when*" and "*does*".

## Considered and declined

- **Renaming `near_miss.py`.** "Near-miss" is on the don't-use list as a metaphor, but here it is a file name and the literal description of a name that nearly matches. Renaming touches `Examples/` and exercise 5 for no gain in the prose.
- **A sub-subclass method named `runs()` draws "did you mean run?"**, which advises overriding the anchor. True, and an edge of the same heuristic the chapter already calls imperfect through `class Weird`. A second caveat would add length to the longest section.
- **`Inversion of Control` in the Pattern Catalog links `#the-anchored-algorithm`.** The heading is unchanged and the paragraph is still in that section.
- **The opening `unittest` example has no listing.** A listing would put a second framework ahead of the chapter's own, and the three sentences are enough to name `run()` as the template method. Verified by running a `TestCase`: construction runs nothing, and `run()` calls `setUp()`, the test, and `tearDown()` in that order.
- **`HalfDone` in Solutions exercise 4 has a hand-written `__init__()`.** It takes no parameters and creates per-instance state, which is the house rule's `__init__()` case.
- **"At the heart of a framework" and "starts the engine".** The first is the chapter's opening in Bruce's voice; the second is the running term that chapter 31 picks up by name.
