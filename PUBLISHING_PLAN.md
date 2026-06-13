# Publishing Plan: *Thinking in Python*

Status document and work-order backlog for taking this book from its current
partial state to publishable. Each task below is written to be **forked to an
independent implementer** (including a cheaper LLM) with little or no extra
context. Read "Shared context" once, then any task is self-contained.

---

## Shared context (read once)

**What this book is.** *Thinking in Python: Insights, Idioms and Patterns* by
Bruce Eckel. It began as a conversion of the abandoned *Python 3 Patterns &
Idioms* project, itself extracted from the design-patterns material in *Thinking
in Java*. Source lives in `Markdown/` (26 chapters, `NN_Name.md`). Code examples
live in `Examples/`. `residual/` holds out-of-book material. `tools/` holds
build scripts.

**Locked decisions** (do not relitigate; see `.claude/.../memory/book-publishing-decisions.md`):
- **Patterns:** Keep the pattern chapters (12–26) but reframe each around the
  Pythonic idiom that replaces or simplifies the GoF pattern. Be honest where a
  pattern is a "language failure" in Python.
- **Python target:** 3.14+ with type hints throughout. `ty`-clean (use
  Astral's `ty` type checker, not mypy).
- **Output:** Clean Markdown/web only for now. Do **not** build print/EPUB
  tooling yet.

**House writing style** (applies to all prose, enforced in every task):
- No em-dashes (neither `--` nor `—`). Use a colon, comma, parentheses, or
  semicolon, or split the sentence.
- Short, single-clause sentences. Break up compound/comma-spliced sentences.
- Italics only to introduce a new term/concept/language element the first time.
  Never for plain emphasis.

**Code conventions for examples:**
- Every fenced Python block that is a real file starts with a comment naming its
  path, e.g. `# Decorator/nodecorators/CoffeeShop.py`. Preserve this convention.
- Target Python 3.14+. No Python 2 idioms (`has_key`, `print` statement,
  `xrange`, `iteritems`, `os.popen2`, `<>`, `raw_input`).
- Add type hints. Code must run and must pass `ty` (Astral's type checker).

**How to pick up a task.** Each task has: Goal, Inputs, Steps, Acceptance
criteria, Dependencies. Do only what the task says. If a task is prose editing,
do not change code semantics. If a task is code, do not rewrite prose.

**Dependency graph (high level):**
```
P1 (infrastructure) ──► P2 (code modernization)
                   └──► P4 (pattern reframe)
P1 ──► P3 (triage + front matter)   [P3 prose tasks need no code harness]
P2, P3, P4 ──► P5 (editorial pass, last)
```

---

## Phase 1 — Infrastructure

### TASK P1-1 — Markdown example extractor + runner
- **Goal:** A tool that extracts every fenced `python` code block whose first
  line is a `# path/file.py` comment from `Markdown/*.md`, writes each to
  `Examples/<path>`, then executes each extracted file under Python 3.14 and
  reports failures.
- **Inputs:** `Markdown/*.md`; existing dead reference `Examples/CodeManager.py`
  (RST-era, replace its role, do not reuse its RST regexes).
- **Steps:**
  1. Write `tools/extract_examples.py`. Parse fenced blocks ```` ```python ````
     ... ```` ``` ````. A block is a "file" iff its first content line matches
     `^#\s*(\S+\.py)\s*$`. Use that path (relative to `Examples/`).
  2. Write each file, creating parent dirs. Warn on duplicate paths with
     differing content.
  3. Write `tools/run_examples.py` that runs every extracted `.py` and collects
     non-zero exits / exceptions into a report. Some examples need stdin or are
     demos: support an opt-out marker (a `# noqa: run` style comment) and
     document it.
  4. Add a `Makefile` (or `tasks.py`) target `examples` that runs both.
- **Acceptance:** Running the target extracts all file-blocks and produces a
  pass/fail list. No crash on the current Markdown. Document usage in
  `tools/README.md`.
- **Dependencies:** none. **Do first.**

### TASK P1-2 — Static web build from Markdown
- **Goal:** One command renders `Markdown/` into a clean, navigable HTML site
  (ordered TOC, prev/next chapter nav, syntax highlighting).
- **Inputs:** `Markdown/*.md` (note `00_Front.md` carries pandoc YAML metadata),
  `resources/static`, `resources/images`.
- **Steps:** Pick a low-friction static generator (pandoc-per-chapter + a TOC
  page, or MkDocs). Wire images from `resources/images`. Add `Makefile` target
  `site`. Output to `build/site/` (git-ignored).
- **Acceptance:** `make site` produces a browsable site with all 26 chapters in
  numeric order and working syntax highlighting. Do **not** add PDF/EPUB.
- **Dependencies:** none (parallel with P1-1).

### TASK P1-3 — CI pipeline
- **Goal:** On every push, run `examples`, `ty`, and `site` build; fail on any
  error.
- **Steps:** Add a CI workflow (GitHub Actions) using Python 3.14. Cache deps.
- **Acceptance:** Green on a clean checkout once P2 is underway; red when an
  example breaks or the site fails to build.
- **Dependencies:** P1-1, P1-2.

---

## Phase 2 — Modernize code to typed Python 3.14+

> Partition by directory so tasks fork cleanly. One task per `Examples/`
> subtree. Each is independent. Template repeated below.

**TASK TEMPLATE P2-*** (instantiate per subtree):
- **Goal:** Modernize all `.py` under `Examples/<SUBTREE>` to typed 3.14+.
- **Steps:** (1) Remove Py2 idioms. (2) Add type hints to all functions,
  methods, and module-level names where non-obvious. (3) Ensure each file runs
  and is `ty`-clean. (4) If the file's source is an inline block in a
  `Markdown/*.md` chapter, update the chapter block to match exactly (the
  extractor in P1-1 is the source of truth for which blocks map where).
- **Acceptance:** `tools/run_examples.py` passes for the subtree; `ty` clean;
  no Py2 idioms remain (grep clean); prose blocks and extracted files match.
- **Dependencies:** P1-1 (harness) and P1-3 (`ty` in CI) preferred but a task
  can run before CI exists.

Known subtrees (one P2 task each): `AppFrameworks`, `ChangeInterface`,
`Comprehensions`, `Decorator`, `Factory`, `Fronting`, `FunctionObjects`,
`InitializationAndCleanup`, `MachineDiscovery`, `Messenger`, `Metaprogramming`,
`MultipleDispatching`, `Observer`, `PatternRefactoring`, `Projects`, `Py4Prog`,
`Singleton`, `StateMachine`, `UnitTesting`, `Util`, `Visitor`.

Known offenders to prioritize (contain confirmed Py2 idioms):
`Factory/shapefact2/ShapeFactory2.py`, `MachineDiscovery/detect_CPUs.py`,
`PatternRefactoring/dynatrash/DynaTrash.py`, `Py4Prog/utility.py`,
`StateMachine/mousetrap2/MouseTrap2Test.py`.

---

## Phase 3 — Content triage and front matter

### TASK P3-1 — Rewrite the Introduction as real front matter
- **Goal:** Convert `Markdown/01_Introduction.md` into book front matter: the
  vision, who the book is for, prerequisites, how to read it.
- **Steps:** Keep the audience framing (intermediate, not introductory). **Move
  out** of the book body: "My Motives," Translations, royalties, Launchpad,
  Contributions/PR mechanics, "The Printed Book." Relocate those to a project
  `CONTRIBUTING.md` / `docs/`. Apply house style.
- **Acceptance:** Introduction reads as a finished book intro with zero
  project-management/meta content. Relocated material preserved elsewhere.
- **Dependencies:** none.

### TASK P3-2 — Stub chapter decisions
- **Goal:** Resolve the six stub chapters. **Finish** `04_Static_Type_Checking`
  and `08_Generators_and_Iterators` (core language material). **Evaluate for cut
  or merge** `10_Machine_Discovery`, `11_Messenger`, `14_Application_Frameworks`,
  `21_Table_Driven_Code` unless strong material exists.
- **Steps:** For finish-chapters, write full content with runnable typed
  examples (coordinate filenames with P1-1 convention). For cut candidates,
  propose a recommendation per chapter in this file, then act once confirmed by
  the author.
- **Acceptance:** No empty placeholder chapters remain in the build. Each
  remaining chapter has real content.
- **Dependencies:** P1-1 for any new examples. **Author sign-off required for
  cuts.**

### TASK P3-3 — Remove non-book material from the build
- **Goal:** Ensure `residual/` (including "Why This Project Failed") is excluded
  from the site build and not referenced from book chapters.
- **Acceptance:** Site contains only book chapters; residual content stays in
  repo for archival but is not published.
- **Dependencies:** P1-2.

---

## Phase 4 — Pattern reframe (one task per pattern chapter)

**TASK TEMPLATE P4-*** (instantiate per chapter 12–26):
- **Goal:** Add a Pythonic-idiom reframing to `Markdown/<NN_Chapter>.md`.
- **Steps:** (1) Open the chapter. (2) Add framing that asks whether Python's
  language design already solves the problem the pattern addresses. (3) Where it
  does, show the idiom and say so plainly. (4) Where the pattern still earns its
  keep, keep it and explain why. (5) Supply or flag missing figures referenced
  as `_images/...`. (6) Modernize inline code per Phase 2 conventions. (7) Apply
  house style.
- **Acceptance:** Chapter opens or closes with an explicit Python-vs-pattern
  judgment; inline code is typed and runs; no missing-image links left silent
  (either provided or listed as TODO with a tracking note).
- **Dependencies:** P1-1 for example verification.

Chapters: `12_The_Pattern_Concept`, `13_The_Singleton`,
`14_Application_Frameworks`, `15_Fronting_for_an_Implementation`,
`16_State_Machines`, `17_Iterators`, `18_Factory`, `19_Function_Objects`,
`20_Changing_the_Interface`, `21_Table_Driven_Code`, `22_Observer`,
`23_Multiple_Dispatching`, `24_Visitor`, `25_Pattern_Refactoring`,
`26_Simulation`.

---

## Phase 5 — Editorial pass (last)

### TASK P5-1 — Whole-book consistency and style sweep
- **Goal:** One consistent voice; house style enforced everywhere; ordering and
  cross-references correct.
- **Steps:** Enforce no-em-dash and short-sentence rules across all chapters.
  Verify chapter order and inter-chapter references resolve. Update the
  `00_Front.md` date (currently 2017). Final proofread.
- **Acceptance:** Style-linter (or grep for `--`/`—`) clean; all cross-refs
  resolve; date current.
- **Dependencies:** P2, P3, P4 complete.

---

## Progress tracker

| Task | Description | Status |
|------|-------------|--------|
| P1-1 | Example extractor + runner | DONE (baseline: 55 pass / 67 fail / 2 skip) |
| P1-2 | Static web build | DONE (`tools/build_site.py`, `make site`) |
| P1-3 | CI pipeline | DONE (`.github/workflows/ci.yml`; regression-baseline gate) |
| P2-* | Code modernization (per subtree) | IN PROGRESS (baseline 67 → 36; see below) |
| P3-1 | Rewrite Introduction | PARTIAL: meta content relocated to `CONTRIBUTING.md`; revoicing + prerequisites/"how to read" still TODO (author) |
| P3-2 | Stub chapter decisions | TODO (needs author sign-off on cuts) |
| P3-3 | Exclude residual from build | DONE (site builds only from `Markdown/`; no chapter references `residual/`) |
| P4-* | Pattern reframe (per chapter 12–26) | TODO |
| P5-1 | Editorial sweep | TODO |

### P2 detail: what is done and what remains

The "easy" half of P2 was genuine Python 2 / Java-leftover syntax and is **done**.
Every example in these subtrees now runs and is `ty`-clean, with the book and
`Examples/` in sync:

| Subtree | Status |
|---------|--------|
| Singleton | DONE |
| Py4Prog | DONE (kept untyped on purpose: the chapter teaches that Python needs no type declarations) |
| InitializationAndCleanup | DONE (`weakref.py` renamed `weak_value.py` to stop shadowing stdlib) |
| Decorator | DONE |
| Factory | DONE |
| FunctionObjects | DONE |
| Messenger | DONE |
| Util | DONE (Synchronization/Observer cluster) |
| Observer | PARTIAL: `ObservedFlower.py` DONE; `BoxObserver.py` left (see below) |
| StateMachine | PARTIAL: mousetrap half DONE; table-driven half left (see below) |
| UnitTesting | DONE (reframed around pytest; Java framework removed; pytest is now a CI hard gate) |
| Metaprogramming | PARTIAL: `GreenHouse.py` DONE; the `__metaclass__` examples await the Python 3 reframe (`__init_subclass__`) |
| Root scripts | `CodeManager.py` marked `# extract: no-run`; `SanityCheck.py` removed (obsolete, replaced by pytest) |

**The 36 remaining baseline failures are NOT Python 2 syntax.** They are
unconverted Java or chapters mid-conversion. The agreed direction is a Pythonic
reframe for each (and sophisticated pytest, now in place from the Testing
chapter). They stay in `tools/examples_baseline.txt` so CI stays green.
Breakdown:

- **PatternRefactoring (23)** — the *Trash* sorting example imported straight
  from *Thinking in Java*: `0.75f` literals, `Trash t = (Trash)it.next()`,
  `ArrayList()`, reflection-based prototype factory (`getConstructor`). Target:
  Pythonic reframe (`isinstance`/`match` for RTTI, a registry dict or
  `__init_subclass__` for the factory, `functools.singledispatch` for
  double-dispatch and Visitor). Pairs with the Phase 4 reframe of this chapter.
- **Metaprogramming (8 left; `GreenHouse.py` done)** — target: Pythonic reframe.
  Move `RegisterLeafClasses` and `Final` to `__init_subclass__`, show
  `__set_name__`/descriptors and class decorators, convert the `__metaclass__`
  examples to `class C(metaclass=...)`, and replace the Python 2 `SimpleMeta1/2/3`
  contrast with a short "Python 2 did X; Python 3 does Y" note.
- **StateMachine table-driven half (4)** — `stateMachine2/` and `vendingmachine/`
  are labeled "(code only roughly converted)" three times in the prose; they are
  still Java (`boolean condition(input):`, `Iterator it=((List)...)`,
  `for(int i...)`). Needs a Python port of the table-driven machine.
- **Observer/BoxObserver.py (1)** — a Swing GUI example the prose itself flags
  "has not been converted." A GUI port (and would need `# extract: no-run`).
