# Restructure Progress

Checkpoint for the book-sectioning restructure. This file is the source of
truth for a looped or resumed run. On restart, read this first, find the first
unchecked stage, and continue from its "next action". Update the checkboxes and
the "Last updated" line before ending each iteration.

Last updated: (none yet, stage 1 not started)
Current stage: 1 (Split)
Next action: split `Markdown/02_Python_for_Programmers.md` into files 02-08 per
the table below, starting with `02_A_Python_Tour.md`.

## Confirmed design

- Three Parts (TOC groupings only; chapter numbers stay sequential 02-30):
  - Part I: Python Foundations
  - Part II: Idioms and Techniques
  - Part III: Design Patterns
- `Markdown/` is the source of truth. `Examples/` is the committed copy and
  must match it (drift check). `ExtractedExamples/` is regenerated.
- Do not commit unless the user asks. Progress is tracked in this file, not git.

## Target structure (old number -> new)

Introduction stays at 01 (front matter, before Part I).

Part I — Python Foundations (02 is the split of old 02):
- 02 A Python Tour            -> 02_A_Python_Tour.md
- 03 Containers and Control Flow -> 03_Containers_and_Control_Flow.md
- 04 Functions               -> 04_Functions.md
- 05 Modules and Packages    -> 05_Modules_and_Packages.md
- 06 Classes                 -> 06_Classes.md
- 07 Initialization and Cleanup -> 07_Initialization_and_Cleanup.md
- 08 Static Type Checking    -> 08_Static_Type_Checking.md

Part II — Idioms and Techniques (renumber old 03-09):
- old 03 Testing                  -> 09_Testing
- old 04 Data Classes as Types    -> 10_Data_Classes_as_Types
- old 05 Functional Error Handling-> 11_Functional_Error_Handling
- old 06 Decorators               -> 12_Decorators
- old 07 Comprehensions           -> 13_Comprehensions
- old 08 Metaprogramming          -> 14_Metaprogramming
- old 09 Rethinking Objects       -> 15_Rethinking_Objects

Part III — Design Patterns (renumber old 10-24):
- old 10 The Pattern Concept      -> 16_The_Pattern_Concept
- old 11 Messenger                -> 17_Messenger
- old 12 Singleton                -> 18_Singleton
- old 13 Application Frameworks   -> 19_Application_Frameworks
- old 14 Fronting for an Implementation -> 20_Fronting_for_an_Implementation
- old 15 State Machines           -> 21_State_Machines
- old 16 Iterators                -> 22_Iterators
- old 17 Factory                  -> 23_Factory
- old 18 Function Objects         -> 24_Function_Objects
- old 19 Changing the Interface   -> 25_Changing_the_Interface
- old 20 Observer                 -> 26_Observer
- old 21 Multiple Dispatching     -> 27_Multiple_Dispatching
- old 22 Visitor                  -> 28_Visitor
- old 23 Pattern Refactoring      -> 29_Pattern_Refactoring
- old 24 Simulation               -> 30_Simulation

## Split map for old 02 (its H2 sections -> new file)

- 02 A Python Tour: opening intro paragraphs (trim the audience overlap with
  the Introduction, REVIEW #4); Scripting vs. Programming; Variables and
  References; Numbers and Arithmetic; Booleans, None, and Truthiness; Strings
  (incl. f-Strings, Common String Operations); Useful Techniques folds in here.
- 03 Containers and Control Flow: Built-In Containers (Lists/Slicing, Tuples/
  Unpacking, Dictionaries, Sets); Control Flow (incl. Pattern Matching); Errors
  and Exceptions; Context Managers. (The brief "Comprehensions" section is
  redundant with the full Comprehensions chapter; drop it or leave a one-line
  pointer. DECISION PENDING.)
- 04 Functions: Functions (Default and Keyword Arguments, Variable Argument
  Lists, Positional-Only and Keyword-Only Parameters, Lambdas); Naming
  Conventions.
- 05 Modules and Packages: Imports, Namespaces and Packages; Packages;
  PYTHONPATH.
- 06 Classes: Classes; Inheritance; Properties; String Representation; Static
  and Class Methods.
- 07 Initialization and Cleanup: Class Attributes Are Not Default Values;
  Cleanup.
- 08 Static Type Checking: Type Hints; Constants with Final; Gradual Typing;
  The Checker: ty; Catching Mistakes; Structural Typing with Protocols; The
  Hints Are Not Enforced at Run Time; Further Reading (place with this chapter
  unless a link clearly belongs elsewhere).
- "Notes" holding pen: resolve into real prose or drop (REVIEW #5). Do not carry
  it into any new chapter as a TODO list.

Each new file needs its own `# Title` H1, then promote that file's former H2s
as-is. Move the matching tagged example files from
`Examples/02_Python_for_Programmers/` into a new folder named for the new file
stem (e.g. `Examples/04_Functions/`). The drift check will flag any example
left in the wrong folder.

## Cross-reference rules (stage 3)

- Rewrite every intra-book `](NN_Name.md)` and `](NN_Name.md#anchor)` link to
  the new filename. Where the anchor's section moved into a split file, point at
  the new file that now contains it.
- Revert the 7 "the Static Type Checking section of the Python for Programmers
  chapter" references to "the Static Type Checking chapter" -> 08_Static_Type_
  Checking.md (this undoes the earlier REVIEW #1 wording, now that it is its own
  chapter again). Files: Data Classes, Functional Error Handling, Decorators,
  Rethinking Objects (x2), Simulation, and the Introduction.
- Refresh the Introduction's "How to Read" lineup if the new Part structure
  changes how chapters are described.

## build_site.py Part dividers (stage 4)

- `discover()` builds a flat list; add Part assignment (by chapter-number range)
  and render Part headings in `render_index()` (the TOC), with a `.part` CSS
  rule. Introduction stays above Part I. Keep the sequential "Chapter N" labels.

## Verify after every stage (all must pass)

```
uv run python tools/extract_examples.py            # drift: book == Examples/
uv run python tools/extract_examples.py --write
uv run python tools/run_examples.py
uv run pytest ExtractedExamples
uv run ty check ExtractedExamples
uv run ruff check ExtractedExamples
uv run python tools/build_site.py                  # site builds clean
```

## Stages

- [ ] Stage 1 — Split old 02 into 02-08, redistribute its Examples, trim the
      intro overlap, resolve the Notes section. Verify.
- [ ] Stage 2 — Renumber old 03-24 to 09-30 (Markdown files and Examples/
      folders). Verify.
- [ ] Stage 3 — Fix all cross-references and the Static Type Checking wording.
      Verify.
- [ ] Stage 4 — Add Part dividers to build_site.py TOC. Verify (build site,
      eyeball index.html).

When all four are checked and the verify block is green, the restructure is
done. Stop the loop (stop scheduling wakeups) and delete this file or leave it
as a record, per the user's preference.
