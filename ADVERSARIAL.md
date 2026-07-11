# Adversarial Review

**Status: resolved.** A follow-up pass fixed every finding in sections 1
through 4 and the actionable items in section 5. Notes on that pass:

- `Solutions/` was renamed to the current chapter numbering (via `git mv`),
  its internal stale chapter links were corrected, `SolutionsCode/` was
  regenerated, and `extract_solutions.py` now fails the gate when a
  Solutions stem stops matching a Chapters stem.
- The chapter 06 `noisy` demo and the chapter 03 `frozendict` block are now
  real, verified examples.
- Section 3.1 was resolved by fixing the Introduction's promise (larger
  pattern-chapter exercises are now acknowledged) plus rewriting the two
  worst offenders (ch26 exercise 2, ch29 exercise 1) and their solutions.
- A `tools/check_links.py` script and advisory `make links` target now
  check external URLs; all pass. The one dead link found
  (`github.com/BruceEckel/Understanding_Effects` in ch42, repo not yet
  public) was reduced to an unlinked mention; restore the link when the
  repository exists.
- A draft `43_Afterword.md` addresses 5.4, marked 🔴 in the README pending
  the author's own edit pass.
- Deliberate non-fixes: chapter 40 was not split (5.2; a renumbering
  cascade outweighs the benefit, so this stays a suggestion), and the ch42
  ZIO listing was reviewed for correctness rather than compiled (no Scala
  toolchain here); the `[[Does this compile?]]` note was removed.

The review as originally written follows.

---

A hostile read of the entire book (chapters 01 through 42), plus cross-checks
of the repository claims the prose makes. The mechanical layer is healthy:
`make verify` passes end to end, all 174 tests pass, every referenced image
exists, `tools/norun.txt` is current, and no `#:` marker drifted during a
fresh gate run on this machine. Everything below is therefore editorial,
factual, or structural. Findings are grouped by severity.

## 1. Broken or Wrong

These are statements a reader can falsify, or references that do not resolve.

### 1.1 The Introduction points at a directory that does not exist

`Chapters/01_Introduction.md` (The Examples section) says the `tracer.py`
block in Decorators "is the file `Examples/15_Decorators/tracer.py`". The
chapter is 14 and the directory is `Examples/14_Decorators/`. This is
leftover from a renumbering, and it sits in the one paragraph that teaches
readers how to find example files.

### 1.2 The Solutions tree still uses the old chapter numbering

23 of the 38 files in `Solutions/` carry pre-renumbering numbers. Samples:

| Solutions file | Current chapter |
|---|---|
| `Solutions/14_Functional_Error_Handling.md` | `Chapters/41_...` |
| `Solutions/15_Decorators.md` | `Chapters/14_...` |
| `Solutions/27_State_Machines.md` | `Chapters/31_...` |
| `Solutions/41_Functional_Programming.md` | `Chapters/40_...` |

Everything from old chapter 14 onward is shifted or scrambled. The content
appears current (spot-checked 04 and 27/31), so this is a rename problem,
but the Introduction promises "Solutions live in the `Solutions/` directory
... one file per chapter," and a reader of chapter 41 will open
`Solutions/41_Functional_Programming.md` and find the wrong chapter's
solutions. No gate checks Solutions filenames against Chapters filenames,
so nothing will catch the next renumbering either. Worth a small check in
`make verify` (match by title, not number).

### 1.3 Chapter 04 exercises name files that do not exist

- Exercise 1 says "In `find_factor.py`". The file is `loop_else.py`
  (`find_factor` is the function inside it).
- Exercise 4 says "In `demo_exceptions.py`". The file is `exceptions.py`.

A script check of every exercise file reference across the book found only
these two genuine misses, so the fix is local.

### 1.4 The `noisy` module in chapter 06 does not exist

The second lazy-import listing (`lazy import noisy`) has no filename
comment, so it is never extracted or verified, and no `noisy.py` exists in
`Examples/06_Modules_and_Packages/`. Exercise 3 then tells the reader to
"`lazy import` both `noisy` and `noisy2`", but only `noisy2` is theirs to
write. Either ship `noisy.py` as a real example or rewrite the exercise to
have the reader create both.

### 1.5 Chapter 38 prose contradicts its own code

The Chladni section says "Every 400 frames the view switches the plate to a
new mode." `chladni_view.py` declares `frames_per_mode: int = 200`.

### 1.6 The Introduction describes three parts; the book has four

`tools/build_site.py` defines Part IV, "Effects," starting at chapter 40.
The Introduction's "How the Book Is Organized" describes only Foundations,
Techniques, and Patterns, and even lists "functional error handling" as a
Techniques topic when it is chapter 41, inside Part IV. The book's newest
part is invisible from its own front matter.

### 1.7 Leftover editor's note in chapter 42

`Chapters/42_Effect_Management.md` contains the literal line
`[[Does this compile?]]` above the ZIO listing. The chapter is flagged 🔴
in the README, so this is expected debris, but it is live on the published
site if the site builds from master.

### 1.8 The Pattern Catalog's linking rule is false

Chapter 39 states: "An unlinked name means the pattern appears only in this
catalog." Several unlinked entries are in fact covered in the book:

- Producer-Consumer, Thread Pool, Future/Promise: chapter 19 (queues,
  `ThreadPoolExecutor`, `concurrent.futures`).
- Publish-Subscribe Channel: chapter 28's event bus.
- Value Object: chapter 12's frozen data classes are the pattern.
- Dependency Injection: chapter 11 (injected `random.Random` and clock) and
  chapter 42 (`ask_tell.py` is textbook DI).
- Special Case: a synonym Fowler uses for Null Object, chapter 20.
- Fluent Interface: chapter 27's builder chaining and chapter 08's `Self`.

Either add the links or soften the rule.

## 2. Technical Accuracy

Claims that are wrong or need hedging, even though the code runs.

### 2.1 "Dictionary keys must be immutable" (chapter 03, twice)

Keys must be *hashable*. A user-defined mutable object hashes by identity
and works fine as a key. The immutability shorthand is common in intro
texts, but this book is precise everywhere else (it even distinguishes
`Final` from runtime immutability), and chapter 35 relies on hashing
semantics. Say "hashable" and spend one sentence on why the built-in
mutable containers are not.

### 2.2 The weakref demo depends on CPython without saying so (chapter 10)

`weak_value.py`'s count falling 3, 2, 1, 0 requires immediate refcount
collection. The chapter carefully caveats the `__del__` demo with a PyPy
warning, then presents this second demo with no such caveat ("the
interpreter collects it at once"). On PyPy the counts would not fall
promptly. Chapter 35's `weak_pool.py` names CPython explicitly; chapter 10
should too.

### 2.3 Subinterpreters "run in their own memory space" (chapter 19)

They run in the same process address space; that is the pattern's selling
point. What is isolated is the object graph and interpreter state. The next
sentence (arguments cross by copying) is right, so only this phrase needs
tightening.

### 2.4 Platform-specific byte counts baked into output markers (chapter 18)

`slots_dataclass.py` pins `344`/`48` bytes and `compact_array.py` pins
`325,176`/`80,080` bytes as `#:` markers. These are CPython-build-specific.
Because the gate now runs `validate_output.py --update`, a run on a
different platform will silently rewrite them, and the prose claims keyed
to them ("roughly a seven-to-one," "roughly a four-to-one") will drift out
of sync with nothing failing. Consider printing ratios or booleans, as the
timing examples in the same chapter already do.

### 2.5 A misplaced output marker in chapter 17

In `my_list.py`, the `#: Howdy, John` line sits under
`print(ml.__class__.__class__)`, but the output comes from
`ml.howdy("John")` two lines earlier. The validator matches cumulative
stdout so it passes, but a reader aligning output with statements will be
misled at the moment the chapter is teaching them to trust that alignment.

### 2.6 Calling overridable methods from a constructor goes unremarked

`template_method.py` (chapter 25) has the base `__init__` call
`self.run()`, and chapter 31's `StateMachine.__init__` calls
`self.current_state.run()`. Both work here, but a subclass that defines its
own `__init__` and sets state after calling `super().__init__()` breaks
silently. The book flags exactly this shape of trap elsewhere (dataclass
inheritance, Borg). One sentence would cover it.

### 2.7 "Total Function" is used loosely (chapters 41 and 42)

A Python function returning `Result` can still raise an exception; nothing
enforces totality. The term is presented as a property the signature
guarantees ("nothing left for an exception to sneak out through"), which
overstates what Python can promise. Chapter 42's `@safe` discussion gets
this right; chapters 41's claim could match it.

## 3. Internal Inconsistencies

### 3.1 The Introduction's exercise promise vs. the pattern chapters

The Introduction says exercises "ask you to change a small,
already-working example" and "None of them need a large new program."
That is true through roughly chapter 24, then the legacy exercises
reappear:

- Chapter 25: build a file-processing framework, twice.
- Chapter 26, exercise 2: build a call-counting smart-reference proxy,
  which the chapter itself just presented as `counting_proxy.py`.
- Chapter 29, exercise 1: "load a two-dimensional array of objects into a
  dictionary," which is both large and vague.
- Chapter 31: nine exercises, including "create an elevator state machine
  system" and a heating/air-conditioning system.
- Chapter 33: a multi-part business-modeling environment.

Either these chapters need the exercise treatment the earlier chapters got,
or the Introduction should stop promising uniformity.

### 3.2 Random-seeding practice contradicts chapter 11

Chapter 11 teaches passing a seeded `random.Random` instance as the clean
alternative to patching or global seeding. Chapters 27 and 32 then seed the
global generator, and `arena.py` does it at import time, a side effect on
import that the book would flag in other code. Chapter 38's `Plate` does it
right (`random.Random(seed)` as a parameter). The demos work; the modeling
is just inconsistent with the book's own advice.

### 3.3 Pattern-labeling discipline slips once

Chapter 27's `shape_factory2.py` comments `create_shape()` with
`# A Template Method:`. It has no subclass-supplied steps; it is a caching
lookup. The book elsewhere is careful not to stamp pattern names on code
that lacks the structure (and says so in chapter 21).

### 3.4 Unverified code blocks in a book that promises verified code

The Introduction says "The code you read is the code that runs." Two
blocks are display-only (no filename comment, never extracted): chapter
03's `frozendict` block and chapter 06's `noisy` block. Both could be real
examples with try/except demos, matching the style used one listing
earlier in each case. (The `frozendict` code was verified by hand for this
review and does run.)

### 3.5 The trace decorator's output betrays it

`tracer.py`/`trace_class.py` format arguments with `{args}`, so a one-arg
call prints the tuple repr: `-> greet('Bob',)` appears verbatim in
`stacking.py`'s output. Cosmetic, but it is the chapter teaching people to
write decorators, and the wart is visible in the book's own listing.

## 4. Prose Defects

Sentence-level errors found on this pass. All are one-line fixes.

| Location | Text | Problem |
|---|---|---|
| ch07, Static and Class Methods | "A method needs the class rather than an instance can be a `@classmethod`." | Missing "that" |
| ch07, `@override` section | "At runtime `@override` does nothing but return the method unchanged, so it validates that you've overridden the method correctly." | Non sequitur; the checker validates, the runtime does not |
| ch08, Gradual Typing | "You can type add hints one function at a time." | Garbled ("add type hints") |
| ch08, Constants with Final | "Marking values `Final` catch accidental reassignments" | Agreement ("catches") |
| ch36, Caretaker section | "because immutable states make inexpensive" | Missing object ("make snapshots inexpensive") |
| ch40, `zip_longest` | "`fillvalue` is a keyword-only argument, so a real value needs a distinct sentinel when `None` is itself a valid element" | The "so" does not follow; keyword-only-ness is unrelated to needing a sentinel |
| ch42, What is an Effect | "This is usually involves I/O" | Garbled |
| ch42, A Program can Never be Pure | "Neither `compute_and_discard()` and `do_nothing()` produce anything" | "Neither ... nor" |
| ch42, Subdividing | "Failures turns into a values the type checker can see" | Doubly garbled |
| ch33, `test_visitor.py` | variable `runuculus` | Misspelling of Ranunculus, in a listing |
| ch09, exercise 3 | "add a third instance, `b2 = B()`, after `b.x` has been changed some other way" | There is no `b` instance of `B` in `real_defaults.py`; the exercise is unfollowable as written |
| ch21, vector of change | "'vector' refers to the maximum gradient and not a container class" | A gradient is a vector; the parenthetical muddles rather than clarifies |

The cluster in chapter 42 matches its 🔴 status. The others are in chapters
marked Edited and Reviewed.

## 5. Judgment Calls and Larger Structure

Not errors. Places where a hostile reader pushes back.

### 5.1 History claims in chapter 20 are loose

Simula is described as statically typed "so the Liskov substitution
principle fit naturally," decades before LSP was articulated, and
Smalltalk's inherit-to-extend culture is called "the opposite of Liskov
substitution." LSP is a constraint on subtyping claims, and Smalltalk
simply makes no such claims; orthogonal is closer than opposite. A
historian will quibble; a hedge ("the discipline later named LSP") ends the
quibble.

### 5.2 Chapter 40 is three chapters in a trench coat

At 7,200 words it is triple the median chapter. The `functools` and
`itertools` sections are reference catalogs (29 subsections of one-example
entries) embedded in an essay chapter. They are good catalogs, but they
change the chapter's texture from argument to enumeration, and the essay's
thread (purity, assurance spectrum) has to be picked back up afterward. An
appendix, or a split, would let both halves be what they are.

### 5.3 The pairing case study compares against code the reader never sees

Chapter 40's rotation case study narrates the circle-method implementation
("Building it took a few honest wrong turns," "the same numbers the
pairs-only version earned") but the book never shows that version. The
reader is asked to appreciate a comparison with an invisible baseline.
Either show a minimal circle-method listing or trim the narration of its
bugs.

### 5.4 The book has no ending

Chapter 42's final section is a strong essay close, but it is the close of
an unfinished chapter, not of the book. There is no afterword, no
"where to go from here," and the Resources list lives in the Introduction.
After 41 chapters that repeatedly promise "read patterns through this
lens," a two-page closing that gathers the lens (the guidelines from
chapter 20, the lightest-construct rule from chapter 37, the assurance
spectrum from chapter 40) would land the plane instead of parking it.

### 5.5 External links are ungated

`check_anchors.py` covers internal cross-references, but nothing checks the
book's many external URLs. Chapter 42 alone adds ten links to experimental
AI-language sites, the category of link most likely to rot within a year.
A periodic link-check target (even advisory, not gating) would protect the
published site.

### 5.6 Small polish items

- Chapter 16's two images have empty alt text (`![](_images/...)`); every
  other image in the book has a description. The same two are 2008-era
  GIF/PNG diagrams among modern SVGs.
- Chapter 26 names its delegating class `StateD` with no explanation; the
  reader will wonder what the D means.
- Chapter 27 re-explains generator basics at beginner level ("This is where
  a generator is a bit strange...") four chapters after Iterators covered
  them properly. It reads like preserved 2008 text.
- Chapter 15's `emit()` types its parameter `StringIO | None`, so the
  nullcontext demo cannot accept a real file, which is the stated use case
  ("an optional file to write to"). `IO[str] | None` would match the prose.

## 6. What Survived the Attack

For calibration, things this review tried to break and could not:

- Every `#:` output marker matched a fresh run; no thrash on this platform.
- All 174 tests pass; `ty`, `ruff`, `run_examples`, anchors, and banned
  phrases are clean through `make verify`.
- The `frozendict`, `sentinel`, `lazy import`, PEP 798 unpacking, and
  sampling-profiler material all checks out against the pinned 3.15.
- The chapter 32/33/34/35/36/37 pattern arc (table dispatch,
  singledispatch, match-on-unions, flyweight, memento, refactoring) is
  internally consistent and each chapter's "Pythonic first, classic for
  contrast" structure holds up under cross-referencing.
- Exercise file references are accurate everywhere except the two chapter
  04 cases noted above.
