When this file has been applied, change this file's name so it has a leading
`~` to indicate completion, and move it to `archive/`.

# Whole-book adversarial review: the findings queue

RECOMMENDATIONS item 1, run 2026-09-02.
Scope was the one review dimension no prior pass covered: what does not
work, what is missing, and what could be better. Each chapter was read
as a hostile expert reviewer would read it, judged as a teaching
instrument. Factual correctness, exercises, and cross-chapter
consistency were out of scope (the correctness sweep, the exercise
pass, and the gates already cover them).

Like `archive/~correctness_review.md` and `archive/~exercise_review.md`,
this is deliberately **not** in `deep_review/`. It spans all 47
chapters, so `do-reviews` cannot apply it. Applying it is a hand job.

**Method.** One fresh agent per chapter, report-only, all 47 chapters.
The full brief is Appendix A at the bottom of this file. Sonnet ran the
34 mechanical chapters, Opus the 13 dense ones (17, 18, 19, 32, 34, 36,
37, 38, 42, 43, 44, 46, 47), the allocation the exercise pass settled.
Chapters 18 and 19 ran last, alone on a quiet machine, under an extra
brief about wall-clock booleans, `tools/data/timing.txt`, and the
asyncio task cliff; both returned zero timing noise, which is the
outcome that brief exists to produce. Agents ran listings from
`build/examples/` via `uv run`, edited nothing, and anchored every
finding to a current line number.

**Numbers.** 252 findings across 47 chapters. No chapter came back
clean; the lightest (09, 21, 33, 45) carry three findings each, the
heaviest (17, 18, 19, 34, 42, 44) carry eight. By category:
**40 does-not-work** (a listing fails to demonstrate what the prose
claims of it, or a claim is falsified by running the chapter's own
code), **143 missing** (the counterexample, limitation, alternative, or
answer an expert reader expects and never gets), **69 could-be-better**
(structure, ordering, length, emphasis).

**Verification status.** RECOMMENDATIONS says verify before applying,
and both prior passes held to it. Findings that depend on runtime
behavior carry the agent's own reproduction (command and output) in the
finding text, but no second pair of eyes has reproduced them in this
session. Treat every finding as credible and unconfirmed, and reproduce
the way the gate does, not the way that is convenient: `uv run` against
`build/examples/`, and for anything measuring time or memory, through
`validate_output.py` rather than standalone (the two findings declined
in the exercise pass were both context mistakes of exactly that kind).

**Tool versions.** `ty` 0.0.77, Python 3.15.0rc2.

## The systemic patterns

Five shapes recur across nearly every chapter. Whoever applies this
queue will move faster by recognizing the shape than by treating each
finding as novel.

1. **The claim is asserted, never demonstrated.** By far the dominant
   pattern, the bulk of the 143 *missing* findings. The prose states
   the failure mode, the counterexample, or the payoff, and no listing
   runs it: chapter 02's `NameError` from the unbound `val`, chapter
   07's dropped `super().__init__()`, chapter 08's `Final` list,
   chapter 15's partial acquisition, chapter 16's duplicate-value
   collision, chapter 22's cross-type `order=True`, chapter 29's
   `invalid-method-override`, chapter 34's exhaustiveness diagnostic,
   chapter 36's Memento-vs-alias argument. The book's own
   show-then-explain pattern is its strength; these are the places it
   lapses into tell-without-show. The agents verified most of these
   claims true by running them, so the fix is usually a few lines of
   listing, not new research.

2. **The payoff is deferred to an exercise.** A chapter's central claim
   is demonstrated only in an exercise, so a reader who skips exercises
   never sees it: chapter 02's t-string safety (exercise 5), chapter
   08's type-parameter default (exercise 5), chapter 23's `tee`
   lockstep case (exercise 5), chapter 25's substitutability (exercise
   4), chapter 26's virtual proxy (exercise 1), chapter 37's dict
   sorter on plastic (exercise 1), chapter 43's Unicode falsification
   (exercise 4), chapter 44's parameter accumulation (exercise 2).
   Exercises should extend a demonstrated point, not carry it.

3. **The demo proves less than the prose claims.** The listing runs and
   its markers are right, but it would behave identically without the
   feature being taught: chapter 07's `classmethod` with no subclass,
   chapter 17's lazy greenhouse that builds all seven classes and
   generated types nothing dispatches on, chapter 31's dead
   unexpected-input arms, chapter 32's `eval_*()` methods that ignore
   their argument, chapter 37's dict sorter whose output is
   byte-identical to the flawed version it replaces, chapter 19's queue
   with no consumer, chapter 43's "Automatic Parallelism" that is
   measured 2.7x slower in parallel. Nothing gate-detectable here; a
   demo that proves nothing still prints the right output.

4. **The well-known alternative is never weighed.** An expert reader's
   first objection goes unanswered: `Path.rglob()` against the walk
   comprehension (16), `operator.itemgetter` against the sort-key
   lambda (05), module-level `__getattr__` against `lazy import` (06),
   mypy/pyright's existence (08), `case _: raise` against the silent
   `match` (37), a toppings list against decorator pizzas (14), plain
   `try`/`finally` against a one-use context manager (15), FSM
   libraries (31), constructor injection and FastAPI `Depends` against
   the service-locator strawman (46), the iterative Fibonacci (41).
   One dismissing sentence is usually the whole fix.

5. **Real behavior holes the correctness sweep could not see.** The
   sweep checked what the prose asserts against what the code does.
   These findings are about what the code fails to do, so they
   survived it, and they are the queue's highest-value items:
   - 13: the claim that ruff's `N806` catches the `case DEFAULT:`
     capture bug is false; ruff passes that file clean.
   - 25: `near_miss.py`'s guard never blocks an exact-name `run()`
     override, which the prose twice claims it refuses.
   - 26: `hasattr()` on the chapter's own protection proxy raises
     `PermissionError` instead of returning `False`, contradicting the
     "checks with `hasattr()` work" claim.
   - 34: `==` on the operator-overloading nodes returns a dataclass
     `bool`, not a node, against the "overload all the comparison
     operators" claim; and `to_query()` silently mishandles a nested
     `Template`.
   - 38: the teleport-pairing idiom mispairs on any odd letter count,
     one maze typo away.
   - 43: `parallel_pure.py` is slower in parallel than serial at the
     shipped sizes.
   - 46: the `try`/`except`-inside-an-Effect rule fails whenever a
     handler sits between the Effect and `run()`; the chapter's own
     `catch_score.py` has that shape.
   - 47: `fork()` drops the error channel from the revealed type, and
     a forked failure escapes `catch()`.

**Where to start.** The 40 does-not-work findings, most of which carry
a run command and its output. Then pattern 5 above. The *missing*
findings are individually small (a few lines of listing each) and can
ride along whenever their chapter is next opened. The *could-be-better*
findings are hand-editing input more than fixes; several (17's inspect
section, 30's grid example, 38's robot section, 47's cast section)
propose cuts that only the author can rule on.

---


## Chapter 01 (Introduction): 5 findings

### [better] Chapters/01_Introduction.md:96 — the AI essay splits the two practical "how to use this book" sections
"How the Book Fits Together" (structure, lines 48-94) and "The Examples"
(mechanics: file layout, tooling, `#:` markers, lines 162-206) are the two
sections a reader needs before starting Chapter 2. "AI Trigger Warning"
(96-160) sits between them and runs 65 lines, longer than either practical
section. A reader working through "how is this book organized" hits a
personal essay about authorship before reaching "where do I find the code."
Fix: move the AI section after Resources/Copyright, or before "Who This
Book Is For," so the two mechanical sections stay adjacent.

### [does-not-work] Chapters/01_Introduction.md:46 — "not about the tooling" is contradicted two sections later
Line 46 states: "The book is about the language, not the tooling around
it." "The Examples" (164-206), the very next content section, then spends
five paragraphs on the build system as a selling point: `ty` type-checking,
`ruff` linting, `pytest`, `uv`, and the self-verifying `#:` marker system
("The code you read is the code that runs"). A reader can quote line 46
back at the chapter: the book plainly cares about, and advertises, its
tooling. Fix: narrow the claim (e.g. "not about IDEs or deployment," if
that's the intent) or drop it.

### [could-be-better] Chapters/01_Introduction.md:156 — the book's value pitch ends on an unrebutted hedge
"Perhaps I am teaching the equivalent of assembly language after everyone
has started using the equivalent of compilers... Some small percentage of
people might still wish to analyze what the AIs are generating. This book
might have some value yet." This is the closing note of the intro's
longest section, and it markets the book to a "small percentage" with
"might have some value" — weaker than the confident opening thesis (line
3: "developing the judgment to choose the smallest thing that works").
An opening chapter's job is to make the target reader feel addressed; this
lands the opposite. Fix: either cut the hedge or follow it with the
stronger, concrete claim already made at 153-154 (guiding AI toward
better solutions) instead of trailing off on doubt.

### [missing] Chapters/01_Introduction.md:50 — "most chapters are self-contained" isn't reconciled with Part V's stated dependency chain
Line 50-51: "you can... jump to a chapter that interests you, since most
chapters are self-contained." The only named exception is Static Types
(60-62). But the Part V description (89-94) explicitly states a
build-on-each-other chain: one chapter surveys Effect systems, "another
develops the full generator protocol on which such tracking depends," and
"the last two put that idea to work with `stateless`" — four chapters
that read in order, not four self-contained entries. A reader who skips
to chapter 46 or 47 on the strength of line 51 hits a wall the intro
never flagged. Fix: name Part V as sequential the same way Static Types
was called out.

### [missing] Chapters/01_Introduction.md:153 — the strongest pro-book argument for the AI era is asserted, not shown
"I think most programmers will regularly use AI, if they don't already.
The knowledge in this book has helped me guide AIs toward better
solutions." This is the one claim in the AI section that answers "why
read a Python book when AI writes the code," and it is the most
persuasive point available to the chapter, yet it gets one unsupported
sentence with no example of what "guiding AIs toward better solutions"
looked like in practice. Immediately after, the chapter pivots to the
weaker assembly/compiler hedge (finding above) instead of developing this
one. Fix: one concrete instance (a prompt that went wrong until the
author applied book-level Python judgment) would do more work here than
the paragraphs that follow it.

## Chapter 02 (Tour): 6 findings

### [does-not-work] Chapters/02_Foundations--Tour.md:429 — t-string demo never shows the safety it promises
The section's whole motivation is safety: "the reason to care is safety... so it can quote, escape, or reject the values before they become part of the result" (lines 429-432). The demo (`tstrings.py`, lines 449-457) is `shout()`, which uppercases literal text and leaves interpolated values untouched via `format()` — no quoting, escaping, or rejection anywhere. It shows the mechanism (parts kept separate) without showing why anyone wants it. Tellingly, exercise 5 (line 516) asks the reader to write a *second* consumer that wraps values in quotes — the one demonstration that would actually illustrate safety is pushed into an exercise instead of the teaching text. Fix: make `shout()` (or a second in-chapter example) escape or reject a value, e.g. reject one containing a quote character.

### [missing] Chapters/02_Foundations--Tour.md:113 — shallow-copy nested-list trap is asserted, never shown
"so `a` and `c` would still share a nested list" (line 115) is a classic gotcha for readers coming from languages with value-typed containers, but `references.py` only ever holds flat ints, so the claim is never demonstrated. Verified it's true: `a = [1, [2, 3]]; c = a[:]; c[1].append(99)` mutates both. Exercise 1 (line 499) also sidesteps it (asks about appending a top-level int). Fix: add a nested-list line to `references.py` or its prose that shows the shared inner list changing through both names.

### [missing] Chapters/02_Foundations--Tour.md:66 — the NameError from unbound `val` is claimed, never run
"with any answer other than `"yes"`, the assignment never runs, and `print(val)` raises a `NameError`" (lines 66-67) is the payoff of the whole scoping discussion (no new scope from `if`), yet `if.py` only runs the `"yes"` branch, so the reader never sees the failure. Confirmed by running the negative case directly: it raises `NameError: name 'val' is not defined`. This is exactly the counterexample that would make "no block scoping" stick for a C/Java reader. Fix: show the failing branch too, e.g. a second snippet with `response = "no"`.

### [missing] Chapters/02_Foundations--Tour.md:264 — `__bool__`/`__len__` fallback mechanism has no example
"A type says otherwise by defining `__bool__()`. Without one, Python falls back to `__len__()`" (lines 264-266) describes a protocol, but `truthiness.py` tests only built-in `int`/`str`/`list`/`None` values — none of which requires the reader to see the dunder-method mechanism at work, only its result. A minimal custom class with just `__len__` (or just `__bool__`) returning a controlled truthiness would demonstrate the actual mechanism the prose names, not just the built-in outcome.

### [missing] Chapters/02_Foundations--Tour.md:429 — no guidance on when f-strings remain the right choice
The f-strings section closes with "F-strings replaced them [`%` and `.format()`], so this book uses f-strings throughout" (line 419), then the very next section introduces t-strings purely as a safety upgrade with no stated boundary. A reader is left to guess whether t-strings should now be preferred generally. The chapter never states the actual rule (plain output formatting keeps using f-strings; reach for t-strings only when a consumer must inspect/sanitize values before assembling untrusted text). Fix: one sentence contrasting when each is the right tool.

### [better] Chapters/02_Foundations--Tour.md:445 — list comprehension used with none of the care given the generator expression
Lines 205-208 flag the generator expression in `arithmetic.py` as a new concept and link forward to [Comprehensions](16_Techniques--Comprehensions.md#generator-expressions). `tstrings.py` line 445-446 uses an equivalent list comprehension (`[piece.expression for piece in message.interpolations]`) with no comment, flag, or link, even though it is the same "new syntax" by the chapter's own standard just two sections earlier. Fix: either flag/link it the same way, or use a `for` loop to stay consistent with what's already been taught by this point.

## Chapter 03 (Containers): 5 findings

### [missing] Chapters/03_Foundations--Containers.md:302 — dict views' set algebra never connects the Dictionaries and Sets sections
Lines 302-308 enumerate `keys()`, `values()`, `items()` as "views" and explain the `items()`-omission trap, but never mention that `keys()` (and `items()`, when values are hashable) is itself set-like: it supports `&`, `|`, `-`, `^` directly against another dict's keys or any set. Verified: `{"x":1,"y":2}.keys() & {"y":20,"z":3}.keys()` returns `{'y'}`. This sits exactly between the Dictionaries section (ends 341) and the Sets section (starts 342) that teaches those same operators on `sets.py`'s `a`/`b` — the chapter builds the set-algebra vocabulary right next door and never uses it to explain what a dict view already gives for free. Fix: one line and example after 308, e.g. `ages.keys() & other.keys()`.

### [missing] Chapters/03_Foundations--Containers.md:148 — the list mutate-while-iterating trap is taught without its dict/set counterexample
`remove_while_iterating.py` (150-158) is used to teach that mutating a container while iterating it is dangerous, and lines 160-165 stress that "no exception reports the skip." But a `dict` or `set` mutated during iteration does not silently misbehave the same way — it raises immediately. Confirmed: `for k in d: del d[k]` raises `RuntimeError: dictionary changed size during iteration`; the analogous set loop raises `RuntimeError: Set changed size during iteration`. This is the single most instructive contrast available (same mistake, list hides it, dict/set shout it) and the chapter never makes it, even though both containers are taught later in the same chapter. Fix: a short callback in the Dictionaries or Sets section.

### [missing] Chapters/03_Foundations--Containers.md:719 — `frozendict`, the chapter's one genuinely new (3.15) feature, has no exercise
`frozendict_demo.py` (717-734) is the only listing in the chapter demonstrating brand-new stdlib behavior (PEP 814), flagged in prose as requiring 3.15. Every other centerpiece (lists, tuples, dicts, sets, deque, Counter, defaultdict, namedtuple, frozenset) gets direct exercise engagement (exercises 1-3, 5-9), but no exercise touches `frozendict` at all — exercise 4 uses `frozenset`/`groups`, not `frozendict`. The chapter's newest, most noteworthy container goes unexercised. Fix: an exercise building a `frozendict`, using it as a dict key, and catching the mutation `TypeError`.

### [does-not-work] Chapters/03_Foundations--Containers.md:444 — "the gap widens without limit as n grows" is asserted, not shown
`membership_cost.py` measures exactly one `n` (200,000) and prints a single boolean. Running it (`uv run python .../membership_cost.py --numbers`) gives `list_scan 0.027643`, `set_lookup 0.000003` — a real ~9000x gap, but only one data point, not a growing one. The widening claim rests entirely on the O(n)/O(1) argument in the surrounding prose, never on a second measurement at a different `n` the way `deque_timing.py` gets exercised at three different sizes (exercise 1, lines 793-800). The listing proves membership cost differs, not that the gap widens. Fix: add a second `n` (or point to exercise 1's pattern) so growth is actually measured, not just argued.

### [better] Chapters/03_Foundations--Containers.md:462 — Counter's own algebra goes unmentioned right after the chapter teaches set/dict algebra
`Counter` supports `+`, `-`, `&`, `|` between two counters (multiset union/intersection/sum/difference), mirroring exactly the operator-then-named-method pattern the chapter just spent the Sets section building ("Every set-algebra operator in `sets.py` has a named method," line 378). `counter.py` (466-482) shows only construction and `most_common()`, missing the one connection that would reuse and reinforce the vocabulary the reader just learned two sections earlier. Fix: one line and example, e.g. `Counter("aab") - Counter("ab")`.

## Chapter 04 (Control Flow): 4 findings

### [missing] Chapters/04_Foundations--Control_Flow.md:379 — `finally`'s classic trap (return/break swallowing an exception) is never mentioned
The chapter says "The optional `finally` always runs, and that makes it the place for cleanup" and stops there. It never warns that a `return` (or `break`/`continue`) inside `finally` silently discards an in-flight exception, one of the best-known `try`/`finally` gotchas and exactly the kind of failure mode an experienced reader expects a chapter to flag. Verified:
```python
def f():
    try:
        raise ValueError("boom")
    finally:
        return "swallowed"
print(f())
```
prints `swallowed` with no trace of the `ValueError` (CPython even emits a `SyntaxWarning: 'return' in a 'finally' block`). A fix: one sentence and this snippet right after the `finally` claim.

### [better] Chapters/04_Foundations--Control_Flow.md:268 — a list comprehension is used before the chapter teaches comprehensions
`mutating_while_looping.py` writes `print([s for s in [1, 2, 2, 3] if s != 2])` as "the fix" for the mutation bug, with no gloss, 290 lines before the "Comprehensions" section (line 558) that first explains the syntax. This is the brief's own example of the category: a concept used before it is taught within the same chapter. A reader who hasn't seen comprehensions yet gets a syntax they can't parse, presented as an obvious one-liner fix. Fix: add a one-clause gloss at line 268 ("a comprehension, covered later in this chapter, builds the filtered list directly") or move the forward pointer there.

### [missing] Chapters/04_Foundations--Control_Flow.md:164 — the two-loop break/continue technique is described but never run
Lines 114-116 promise "the loop `else` technique that follows `loop_else.py`" for leaving two loops at once, then lines 164-168 describe it entirely in prose (put `continue` in the inner loop's `else`, `break` right after it) with no listing anywhere in the chapter, unlike every other technique here. I verified the described behavior is correct by running it standalone (`for i... for j... if hit: break` / `else: continue` / `break` correctly exits both loops on hit, continues outer loop otherwise), but the reader gets no such check. Fix: add a short listing next to `loop_else.py` demonstrating it.

### [better] Chapters/04_Foundations--Control_Flow.md:1 — the opening is a definition plus a table of contents, not a hook
"Control-flow statements decide which code runs and how often. This chapter covers conditionals, placeholders, loops, pattern matching, exceptions, the `with` statement, and comprehensions." Sibling chapters open with a contrast that motivates the material (ch03: "In C++ and Java a container is a library class... Python builds its containers into the grammar"). Chapter 4 has real hooks available and unused: no braces/labeled `break`, `match` as a newer structural-pattern statement, the walrus as a recent addition, EAFP as a cultural stance foreign to C++/Java readers. As written the opening gives no reason to keep reading before the section list starts.

## Chapter 05 (Functions): 6 findings

### [missing] Chapters/05_Foundations--Functions.md:275 — `global` is taught with no caution, but the book later calls it an anti-pattern
`global` is presented as a plain mechanism ("`global` tells Python to rebind
the module-level name instead"), with `writes_global()` shown as ordinary,
working code. Chapter 40 later uses the *same* pattern (a `balance` global
mutated by `withdraw()`) as the negative example distinguishing impure code
from closures, saying a captured constant differs from "the global `balance`
that makes `withdraw()` unpredictable," and chapter 44 calls a mutable global
"enough on its own" to make a function's behavior unpredictable. Chapter 5
never flags this tension or forward-points to it. Fix: add one sentence
noting `global` couples callers to shared mutable state, with a forward
pointer to chapters 40/44.

### [missing] Chapters/05_Foundations--Functions.md:1 — docstrings are never taught, though the book assumes them from Chapter 14 onward
No chapter through 07 introduces `"""..."""` docstrings or `__doc__`; the
first real explanation is `inspect.getdoc()` in Chapter 17. Yet Chapter 14
(Decorators, line 159) already says an undecorated wrapper "reports its name
as `wrapper` and loses its docstring" as if the term were already familiar.
Functions is the natural place to introduce docstrings (a one-line `"""..."""`
under `def`, `func.__doc__`) since every function in the chapter is a
candidate example. Fix: add a short docstring paragraph and example
alongside `a_function.py`.

### [missing] Chapters/05_Foundations--Functions.md:362 — the `*args`/`**kwargs` forwarding pattern the chapter teaches has a known failure mode never shown
`trace(func, *args, **kwargs)` is presented as "the standard shape of a
wrapper," but nothing warns that a forwarded `**kwargs` can collide with a
named parameter. Confirmed: `report(label, *values, **options)` called as
`report(*nums, **{"label": "oops", ...})` raises
`TypeError: report() got multiple values for argument 'label'`. This is the
exact gotcha Chapter 14's decorators inherit. Fix: one sentence plus a `try`/
`except TypeError` block showing the collision, right after `trace()`.

### [better] Chapters/05_Foundations--Functions.md:90 — "Default and Keyword Arguments" bundles three separate ideas the chapter elsewhere splits apart
The section (lines 90-267, over a third of the chapter) covers default/keyword
mechanics, the mutable-default trap (two listings plus a binding-semantics
digression), and sentinel values (`None` and PEP 661 `sentinel()`), all under
one heading. Contrast the chapter's own practice two sections later, where
closely related "collect" and "unpack" behavior for `*`/`**` get separate
headings (Variable Argument Lists vs. Unpacking Arguments) because they are
distinct ideas. Sentinels in particular are a self-contained concept that
deserves its own heading. Fix: split into "Default Arguments" and "Sentinel
Values" (or similar).

### [missing] Chapters/05_Foundations--Functions.md:466 — Lambdas never mentions `operator.itemgetter`/`attrgetter`, the idiomatic alternative for exactly the case it demonstrates
The chapter's own motivating example, `sorted(words, key=lambda w: w[-1])`,
is precisely the shape `operator.itemgetter` exists to replace for indexing,
and `attrgetter` for attribute access; neither is mentioned anywhere in the
book (`grep -rn "itemgetter\|attrgetter" Chapters/*.md` returns nothing). An
experienced reader coming from idiomatic Python will ask why the chapter
teaches only the lambda form for sort keys. Fix: one sentence noting
`operator.itemgetter`/`attrgetter` as the named alternative, dismissed for
cases needing arbitrary expressions.

### [better] Chapters/05_Foundations--Functions.md:1 — the chapter opens with a mechanical fact rather than telling the reader what it will cover
"The `def` keyword defines a function." starts the chapter with no framing
sentence. Compare Chapter 4 ("Control-flow statements decide which code
runs and how often. This chapter covers conditionals, ...") and Chapter 6
("Each Python file is a *module* ..."), both of which orient the reader
before the first listing. Chapter 5 covers a wide range (defaults, scoping,
`*args`/`**kwargs`, positional/keyword-only markers, lambdas) that a
one-sentence preview would usefully forecast. Fix: add a scene-setting
sentence before line 3.

## Chapter 06 (Modules and Packages): 4 findings

### [does-not-work] Chapters/06_Foundations--Modules_and_Packages.md:554 — `sys.lazy_modules` is not the clean debugging tool the prose describes
Lines 554-555 say `sys.lazy_modules` "holds the names still waiting to
load, so you can check what a run actually put off without
instrumenting the modules." Running a script with **zero** `lazy
import` statements of its own already shows a populated set:
`uv run python <script importing only sys>` prints
`{'copy.copy', 'inspect.iscoroutinefunction', 'pkgutil', 'inspect', ...,
'heapq', 'locale', 'warnings'}` — CPython's own interpreter startup
machinery uses lazy imports internally on this build. A reader who
follows the chapter's implicit invitation to inspect
`sys.lazy_modules` themselves gets a set cluttered with unrelated
stdlib internals, not the clean "what my program deferred" picture the
prose promises. Fix: either don't present it as a general-purpose
check, or show (and explain) the noise.

### [missing] Chapters/06_Foundations--Modules_and_Packages.md:518 — no mention of module-level `__getattr__` (PEP 562), the pre-3.15 real-world answer to the same problem
The "Lazy Imports" section frames the problem ("that eager work slows
startup") and PEP 810's `lazy` keyword as the solution, contrasting it
only with moving the import inside a function (lines 518-524). It
never mentions the pattern real packages have used for years to solve
exactly this — a package `__init__.py` defining module-level
`__getattr__`/`__dir__` to defer submodule imports (used by e.g.
pandas, numpy, and many CLI tools to cut startup cost before PEP 810
existed). `grep -rn "PEP 562\|module.*__getattr__" Chapters/*.md`
returns nothing book-wide. A reader who already knows this idiom gets
no comparison to it, and one who doesn't learns a narrower picture of
how Python code actually solves this today. Fix: one sentence
contrasting `lazy import` with the `__getattr__` pattern it mostly
supersedes.

### [missing] Chapters/06_Foundations--Modules_and_Packages.md:346 — two claims late in "Imports Within a Package" break the chapter's show-then-explain pattern, and one is easy to over-generalize
Line 346-347 ("Two dots (`..module1`) reach the parent package...")
and lines 356-363 (the exact quoted `ImportError` for a circular
import) are both asserted in prose with no runnable listing, unlike
every other behavior claim in the chapter. I built both scenarios to
check: the double-dot claim holds, but the circular-import message is
scenario-dependent in a way the text doesn't flag. Two plain top-level
modules that import each other in a cycle raise `ImportError: cannot
import name 'f' from 'modx' (consider renaming 'modx.py' if it has the
same name as a library you intended to import)` — no "circular
import" wording at all. The exact quoted message
("...partially initialized module... most likely due to a circular
import...") only appears for a *package-relative* cycle (`from . import
...`), which is what the chapter is discussing, but a reader who
hits the plain-module case (equally likely, arguably more likely
outside a package) will see a completely different message and no
way to reconcile it with the text. Fix: add the small repro, or note
that the message differs outside a package.

### [better] Chapters/06_Foundations--Modules_and_Packages.md:598 — Exercise 4 tests a concept the book never teaches
Exercise 4 asks the reader to rename `module.py` to `Module.py`,
predict what happens on a case-insensitive filesystem, and "look up
`PYTHONCASEOK` to confirm your explanation" (line 604).
`grep -rn "PYTHONCASEOK\|case-insensitive" Chapters/*.md` finds this
single occurrence in the whole book — the chapter's own prose never
mentions case-insensitive filesystems or `PYTHONCASEOK` before sending
the reader to look it up cold. Every other exercise in the chapter
applies material the chapter just taught; this one requires outside
research to even understand what's being asked, which is a different
kind of exercise from its five neighbors. Fix: either add a sentence
in the body introducing case-insensitive filesystems and
`PYTHONCASEOK`, or reframe the exercise as an open research question
rather than a "predict then confirm."

## Chapter 07 (Classes): 5 findings

### [does-not-work] Chapters/07_Foundations--Classes.md:553 — classmethod's core justification is never demonstrated
The section's whole point is that `cls(...)` beats hard-coding `Temperature(...)`: "Called on a subclass, `from_fahrenheit()` receives that subclass as `cls`... Naming the class directly would hard-code `Temperature` into every subclass." But `class_methods.py` (lines 530-551) defines no subclass of `Temperature` anywhere. I confirmed the claim is true (`Kelvin(Temperature)` through `from_fahrenheit` returns a `Kelvin`), but the chapter's own listing never proves it — a `@staticmethod` calling `Temperature(...)` directly would print identical output for everything the listing actually runs. Fix: add a one-line subclass and print `type(result)`.

### [could-be-better] Chapters/07_Foundations--Classes.md:220-259 — a full section teaches a technique it disavows
"Composing Methods with `import`" spends a header, two listings, and a paragraph on importing a function into a class body, then concludes "it is a curiosity more than a technique: a helper object or a module-level function is almost always the clearer choice." No exercise touches it either. A section whose last sentence retracts its own subject teaches a trick more than a technique. Better: show the two named alternatives side by side so the reader sees why they win, or fold this into a short aside rather than a standalone section.

### [missing] Chapters/07_Foundations--Classes.md:401 — the property/setter recursion trap is asserted, never shown
"`self.radius` inside the getter, or `self.radius = value` inside the setter, calls that same method again, and again, until the interpreter raises a `RecursionError`" is stated but never run, unlike every other trap in the chapter (`forgot_self.py`, `cached_property` staleness, the setter's `ValueError`). I ran the described mistake directly (getter returns `self.radius`, setter assigns `self.radius = value`): `RecursionError: maximum recursion depth exceeded` on construction, confirmed. This is a common real bug (`self.x = value` instead of `self._x = value`); the chapter has the listing and the room to show the failure, not just describe it.

### [missing] Chapters/07_Foundations--Classes.md:209 — the dropped-`super().__init__()` AttributeError is asserted, never shown
"If you remove the `super().__init__(text)` line, nothing creates `self.s`, so the first method that reads it raises an `AttributeError`" is central to why `super().__init__()` matters, but no listing runs it. I verified it by dropping the call from a copy of `Simple2.__init__`: calling `show()` then raises `AttributeError: 'Simple2' object has no attribute 's'`. The reader never sees this traceback, only the assertion. A few added lines to `simple2.py` demonstrating the failure would make "Python never calls a base constructor for you" concrete.

### [missing] Chapters/07_Foundations--Classes.md:205 — MRO conflict resolution has no example with a conflict to resolve
The chapter states "With several [bases], the MRO decides which base supplies a name that more than one of them defines," and three later chapters (27, 32, 37) link back here as the canonical MRO explanation. Every example here uses single inheritance, though; `Simple2.__mro__` is shown as the uncontested chain `(Simple2, Simple, object)`, which has nothing to conflict on. A reader following those links back to see how MRO resolves a name two bases both define finds no case that does.

## Chapter 08 (Static Types): 5 findings

### [missing] Chapters/08_Foundations--Static_Types.md:132 — narrowing's unsoundness on mutable state is never mentioned
The Narrowing section teaches `is not None` as proof, to the type checker, that a value is no longer `None`. It never states the limit: narrowing an *attribute* survives an intervening method call even when that call can reset the attribute, so `ty` accepts code that then crashes. Verified: a `Box` with `self.val: str | None` and a `reset()` that sets it to `None`; a function checks `if b.val is not None:`, calls `b.reset()`, then does `b.val.upper()`. `uv run ty check` on this: "All checks passed!" `uv run python` on it: `AttributeError: 'NoneType' object has no attribute 'upper'`. The chapter's own claim ("narrowing... proves... that the value is an X") is false in this common shape, and the chapter gives the reader no warning. Fix: add a sentence and a short counterexample showing narrowing is invalidated by any call the checker can't see through, or at least state the limitation.

### [missing] Chapters/08_Foundations--Static_Types.md:178 — Final's "still mutable" claim has no code to back it
"`Final` blocks rebinding the name, not mutation of the object" and "You can still append to a `Final[list[str]]`" are the single most likely misconception a reader has about `Final` (confusing it with immutability), yet `final_constants.py` never shows a list, only `int` and `str`. Every other near-miss concept in this chapter (the `Blob`/`paint()` case, the `list[Circle]`/`list[Shape]` variance case) gets a runnable counterexample; this one, arguably the most surprising, gets only a sentence. Fix: add `HISTORY: Final[list[str]] = []` to the listing and show `HISTORY.append(...)` succeeding.

### [missing] Chapters/08_Foundations--Static_Types.md:356 — "Any loses that connection" is asserted, never shown
The paragraph motivating generics claims `Any` "accepts any list, and the return type then says nothing about what the list holds," but no listing demonstrates the failure this produces (e.g., a non-generic `first(items: list) -> Any` where `first([10]).nonexistent_method()` passes `ty` silently). Without that counterexample, the reader takes the claim on faith rather than seeing the exact hole generics close. Fix: show the `Any`-typed version failing to catch a bad call, right before introducing `first[T]`.

### [missing] Chapters/08_Foundations--Static_Types.md:467 — the chapter's central claim about type-parameter defaults is proved only in an exercise
"Without the default, `words: Stack` leaves `T` unsolved and the type checker falls back to `Unknown`" is the whole point of the Type Parameter Defaults section, but `type_defaults.py` never removes the default to show it. That exact check is instead assigned as Exercise 5 ("Remove the `= str` default and run it again"). Verified the claim is true (`reveal_type` reports `Unknown` without the default), but a reader who skips exercises never sees the section's own payoff demonstrated. Fix: show the no-default case inline, even briefly, and let the exercise extend it.

### [missing] Chapters/08_Foundations--Static_Types.md:13 — `ty` is introduced with no acknowledgment that mypy and pyright exist
This is the reader's first exposure to Python type-checking tooling, and it names only `ty`, "this book uses Astral's `ty`," with no mention that mypy (the reference implementation) or pyright (the one most IDEs run) exist. An experienced reader who has used either gets no bridge and may wonder whether `ty`'s behavior is idiosyncratic. (Chapter 17 later says "type checkers such as ty, mypy, and pyright," so the omission isn't a book-wide policy, just this chapter's introduction.) Fix: one clause naming the alternatives and why this book picked `ty`.

## Chapter 09 (Class Attributes): 3 findings

### [missing] Chapters/09_Foundations--Class_Attributes.md:307 — the `type(self)`/`cls` fork hazard is never taught, though the chapter states the exact fact needed to predict it
Line 307 says "A subclass stands to its base class as an instance stands to its class," which is precisely the fact needed to predict a real hazard the chapter never raises: a base-class method that increments a `ClassVar` via the idiomatic `type(self).total += 1` (rather than the literal class name `class_var.py` uses) silently forks a separate counter per subclass, the same way `a.rating = 1` forked from `Stars`. Verified: with `type(self).total += 1` in `Base.__init__`, after one `Base()` and two `Sub()` constructions, `Base.total == 1` and `Sub.total == 3`, and `uv run ty check` reports no diagnostic at all. Chapter 37's `Trash.registry` pattern depends on readers already knowing to dodge this (it mutates via subscript assignment, never reassigns `cls.registry`), but chapter 09 never states the danger it's avoiding. A short example showing the fork would close the gap.

### [does-not-work] Chapters/09_Foundations--Class_Attributes.md:90 — "the bug surfaces far from the line that caused it" is asserted, never demonstrated
Line 90's claim is the chapter's core motivation for caring about this topic at all, but no listing embodies it. `class_attribute_confusion.py`, `shared_mutable.py`, and `class_var_inheritance.py` are each a tight, sequential trace where the shadowing assignment sits one or two lines above the `print()` that reveals it. None separates the write and the confused read by a function call, a module boundary, or even a few lines, which is what "far away" would look like in practice. The chapter proves the shadowing mechanism thoroughly but proves nothing about the debugging difficulty it explicitly claims motivates the whole chapter. Fix: add one example where the write and the surprising read sit in different functions.

### [missing] Chapters/09_Foundations--Class_Attributes.md:41 — the shadowing model silently assumes an ordinary `__dict__`; slotted classes (already shown in ch07) are never revisited
Line 41 ("An instance and its class each have their own attribute dictionary") is the chapter's entire model, stated with no qualification. But chapter 07 already told this same reader, two chapters earlier, that `@dataclass(slots=True)` classes have no instance `__dict__` (07:449). Confirmed by running: with `class Stars: __slots__ = (); rating = 5`, `a.rating = 1` raises `AttributeError: 'Stars' object attribute 'rating' is read-only` instead of shadowing, the opposite of the whole chapter's central lesson. Nothing in the chapter says the shadowing story stops working the moment a class opts into slots, which is exactly the limitation a reader who remembers `slots=True` from ch07 will wonder about. One sentence would state the boundary.

## Chapter 10 (Cleanup): 5 findings

### [missing] Chapters/10_Foundations--Cleanup.md:340 — weak-reference machinery silently fails on slotted/C-level objects
Both "reliable" weak-reference techniques (`finalize()`, `WeakValueDictionary`) require the target support weak references at all, and the chapter never says so. Verified: a class with `__slots__` that omits `__weakref__` raises immediately.
```
class Slotted:
    __slots__ = ("name",)
finalize(Slotted("x"), print, "closed")
# TypeError: cannot create weak reference to 'Slotted' object
```
Chapter 8 (Static Types) and elsewhere in the book use `__slots__` freely, so a reader who reaches for `weakref` on a slotted class hits this with no warning. Fix: one sentence noting the requirement, near `finalizer.py` or the `WeakValueDictionary` listing.

### [missing] Chapters/10_Foundations--Cleanup.md:408 — "never `__del__()`" ignores the stdlib's own hybrid pattern
The Rule states flatly "Never put resource release in `__del__()`," but `io.IOBase` (hence every file object) and `socket.socket` both define a `__del__()` that calls `close()` and emits a `ResourceWarning` as a diagnostic backstop. Verified:
```
f = open("pyproject.toml"); f.read(1); del f; gc.collect()
# ResourceWarning: unclosed file <...>
```
An expert reader who has seen "unclosed file" warnings will notice the chapter's absolute rule doesn't square with code they already rely on. A sentence acknowledging the warn-only backstop pattern, and why it differs from doing real release work in `__del__()`, would close the gap.

### [missing] Chapters/10_Foundations--Cleanup.md:218 — the recommended `close()` is not shown to be idempotent, unlike its own backstop
`closable.py`'s `Socket.close()` is presented as the primary reliable technique but is never guarded against being called twice (it would just print "closed" again). Contrast `finalizer.py`, three sections later, which explicitly earns idempotency as a stated feature ("The second `close()` does nothing... a finalizer runs at most once"). The chapter holds its backup technique to a higher engineering standard than the technique it recommends first, and a reader copying `closable.py`'s shape gets no guidance that real `close()` methods (like file objects') must guard re-entry themselves. Fix: a one-line note or a `self._closed` guard in `closable.py`.

### [missing] Chapters/10_Foundations--Cleanup.md:192 — no diagnostic technique for "why won't this object die"
The chapter spends two sections teaching that cycles and shutdown timing make `__del__()` unpredictable, but never gives the reader a tool for the situation this predicts they'll hit in real code: an object that should be freed but isn't, with no chapter-taught example of the debugging escape hatch. `gc.get_referrers()`, `sys.getrefcount()`, or even `gc.collect()` returning the count of unreachable objects it collected are the standard next step and go unmentioned. Fix: one paragraph or exercise pointing at `gc.get_referrers()` as how you'd actually locate the reference keeping something alive, rather than only demonstrating the mechanism in isolation.

### [missing] Chapters/10_Foundations--Cleanup.md:213 — partial-construction leak never addressed
`closable.py`'s `Socket.__init__` acquires the resource (prints "opened") before `__enter__` ever runs. This is the classic context-manager trap: if `__init__` raises after acquiring the resource but before the constructor returns, the `with` statement's target is never bound, `__enter__`/`__exit__` never run, and the resource leaks silently, exactly the kind of failure this chapter is otherwise built to warn about. Neither the prose nor an exercise raises this, despite it being a well-known reason experienced Python programmers separate resource acquisition (a factory function or `__enter__`) from object construction. A short note or a broken counterexample would close it.

## Chapter 11 (Testing): 5 findings

### [missing] Chapters/11_Techniques--Testing.md:358 — session-scope fixture risk is asserted, never shown breaking
Lines 358-359: "The reuse is the risk as well as the point: every test receives the same object, so one test that mutates it changes what the next test sees." The chapter states this failure mode but never demonstrates it — no listing shows a test mutating a session-scoped fixture (`bank_name` or similar) and a second test then observing the leaked state. This is exactly the counterexample the brief flags as the thing that "makes the concept stick": a warning without a demonstration is a rule to memorize, not a failure a reader has watched happen. A short two-test listing showing the leak would fix this.

### [missing] Chapters/11_Techniques--Testing.md:705 — mocks (call verification) named, never shown
Lines 703-707: "The standard library's `unittest.mock` builds stubs for you, along with *mocks* that also record the calls they receive, and it turns up in most existing code." `grep -rl "unittest.mock\|assert_called\|MagicMock" Chapters/` matches only this chapter, and only this prose sentence — no listing anywhere shows `Mock()`, `assert_called_with()`, or `call_count`. Every example in the chapter is a stub returning a canned value. A reader told mocks are common in existing code has nothing here to build interaction-testing from.

### [missing] Chapters/11_Techniques--Testing.md:22 — TDD introduced, never demonstrated
Lines 22-44 devote a section to TDD with three stated benefits ("Describe what the code should do...", "Provide a worked example...", "Get a clear definition of done"), but no listing in the chapter follows a test-first, red-green-refactor sequence. `account.py` appears before `test_account.py` (line 63 vs. 93), and every later example is code-first too. A reader gets the argument for TDD but never sees "when you write the tests first, you..." actually practiced anywhere in the chapter.

### [better] Chapters/11_Techniques--Testing.md:722 — meta section interrupts two teaching sections
"How This Book Runs Its Tests" (722-727) is four sentences about this book's own build tooling, sandwiched between "Property-Based Testing" (711) and "Making Code Testable" (729) — both teaching transferable technique. It teaches nothing a reader can apply to their own project, and it breaks the run from "here's a technique you haven't seen" into the chapter's capstone. Moving it to a footnote, or beside the book's other self-referential notes, restores the flow.

### [missing] Chapters/11_Techniques--Testing.md:542 — dependency injection's own cost never weighed
Lines 542-564 and 594-624 present passing the RNG/clock as an argument as strictly "cleaner still" than `monkeypatch`, with no downside stated. In a real codebase the clock or RNG is often needed several calls deep; injecting it means threading the parameter through every intervening function or introducing a context object — the kind of "well-known alternative... never weighed" the brief calls out. As written, a reader has no guidance for when injection's parameter-plumbing cost outweighs a `monkeypatch` at the boundary, only a claim that injection wins.

## Chapter 12 (Data Classes as Types): 5 findings

### [does-not-work] Chapters/12_Techniques--Data_Classes_as_Types.md:126 — the DbC demo's corruption is a chosen bug, not a property of mutable classes
`stars_class.py`'s `f1()` mutates `_number` first and validates after, so `Stars(8).f1()` leaves `damaged` holding `13`. The prose calls this inherent to encapsulation ("the object still mutates... so `f1()` must re-check the result"). It isn't: a validating `@number.setter` that checks before assigning prevents it entirely. I wrote that variant and ran it: `damaged.f1()` raises `TypeFailure` and `print(damaged)` still shows `Stars(8)`, never `Stars(13)`. The chapter's broader point (checks scatter across every mutating method) survives, but the specific "invalid state persists" claim only holds because the example validates in the wrong order. Fix: either order the check-then-set in `stars_class.py`, or say explicitly this is a chosen ordering bug, not mutation's inherent flaw.

### [missing] Chapters/12_Techniques--Data_Classes_as_Types.md:34 — never justifies `check()`+exception over a plain `assert`
`check()` is introduced and used everywhere without saying why it beats `assert 1 <= stars <= 10`. Any experienced Python reader knows `assert` is stripped under `python -O`/`-OO`, which would silently disable every validation in this chapter's central technique — exactly the failure mode the chapter exists to prevent. That's the single most obvious question an expert reader asks here, and it's never raised or answered. Fix: one sentence near `check()`'s introduction, noting `assert` is optimized away and a custom exception cannot be.

### [missing] Chapters/12_Techniques--Data_Classes_as_Types.md:1540 — no cost side to the trade the chapter itself flags
"That trade has a price, and the price is at the edges" only discusses where checks must move, not what they cost. Every value in this style becomes a wrapper object (`Stars`, `Day`, `Year`, `FullName`, `EmailAddress`) with a constructor call and attribute indirection at each boundary, and `copy.replace()` re-validates the whole object on every change. For hot paths or large nested structures (`Line` holding many `Point`s) this is a real, well-known trade-off of "parse, don't validate" that a performance-conscious reader would ask about, and the chapter never states it, even as a one-line caveat pointing to [Performance](18_Techniques--Performance.md).

### [better] Chapters/12_Techniques--Data_Classes_as_Types.md:562 — the A/B/C/D digression interrupts the type-safety narrative
"Comparing Ordinary Classes and Data Classes" (four subsections, ~200 lines) sits between "Composing Types from Types" and "Enums Are Types Too," breaking the chapter's through-line (validate once, freeze, compose). It reprises and extends [Class Attributes](09_Foundations--Class_Attributes.md)'s bare-annotation/`ClassVar` material but never connects back to the "type is a set of values" thesis — it's a `@dataclass`-mechanics deep dive, not a types-as-validation argument. It would read better moved earlier (right after "Data Classes" introduces `@dataclass`, before validation is layered on) or trimmed, since none of A/B/C/D touch validation at all.

### [missing] Chapters/12_Techniques--Data_Classes_as_Types.md:159 — DbC's "problem" is stated but no real alternative to frozen types is weighed for genuinely mutable domains
The chapter's fix is "make it immutable, validate once." It never addresses the case where a value truly must mutate in place over its lifetime (a counter, a connection's state, a running total) and can't be replaced with a fresh frozen instance each time. The reader is left to guess whether DbC-with-checks-in-every-setter is simply the accepted fallback there, or whether some other pattern (e.g., a validating property setter, checked at write time) is preferred — a natural "when NOT to use this" the chapter doesn't state.

## Chapter 13 (Pattern Matching): 5 findings

### [does-not-work] Chapters/13_Techniques--Pattern_Matching.md:143 — ruff does not actually catch the DEFAULT capture bug
The prose claims "`ruff` does notice, flagging `DEFAULT` under its `N806` rule."
Running `uv run ruff check build/examples/13_Techniques--Pattern_Matching/value_patterns.py`
reports "All checks passed!" — zero warnings, and `N` is selected in
`pyproject.toml` with only `N818` ignored. A minimal repro confirms N806 fires
on a plain `ast.Assign` (`DEFAULT = 1` inside a function) but not on a
`case DEFAULT:` capture target. The paragraph's claimed safety net does not
exist: a reader who trusts "ruff will catch this" gets silently burned. Fix:
drop the ruff claim, or state plainly that ruff misses match-case captures.

### [missing] Chapters/13_Techniques--Pattern_Matching.md:420 — bound-name leakage after a failed guard is asserted but never shown to matter
"the names stay bound" is stated as a neutral fact, but every case in
`guards.py` re-matches `Point(x, y)` anyway, so the fact has no visible
effect there. The real trap is a later case that does *not* rebind the name.
Verified: `case Point(x, y) if x > 100: ...` followed by `case _: return x`
against `Point(3, 4)` returns `leaked x=3` instead of a `NameError`. This is
exactly the "failure mode that would make the concept stick" that the
section never demonstrates. Fix: add a two-line repro proving the leak into
an unrelated case.

### [could-be-better] Chapters/13_Techniques--Pattern_Matching.md:480 — "Patterns Nest" nests different pattern kinds, never a pattern inside itself
Every example here combines two or three *different* forms (sequence, class,
alternation) at one level of depth. The signature use case for structural
pattern matching — recursively walking a self-referential type such as a
tree or AST — never appears, though it does surface later in Composite and
Interpreter (34, e.g. lines 330/409/450). This section gives no forward
pointer, so a reader asking "can a pattern nest inside itself?" right here
gets no answer and no signpost. Fix: one sentence pointing to chapter 34's
recursive `match`, or a small self-nesting example here.

### [missing] Chapters/13_Techniques--Pattern_Matching.md:446 — mapping patterns lose the type information class patterns preserve
`handle(event: dict[str, object])` binds `x`/`y` as `object`, unlike
`class_patterns.py`'s `Point(x, y)`, which binds `x`/`y` as `int` from the
dataclass's declared fields. Neither "Mapping Patterns" nor "When Not to
Match" names this: matching on raw dict shape is inherently untyped at the
value level, unlike matching on a dataclass built from that same JSON.
An expert reaching for `match` on JSON-shaped data will want this tradeoff
stated, plus the natural alternative (parse into a dataclass first, then
match). Fix: one paragraph naming the loss and the dataclass alternative.

### [missing] Chapters/13_Techniques--Pattern_Matching.md:166 — starred capture is shown only at the tail, leaving other placements unaddressed
`sequence_patterns.py`'s only starred example is `[first, *rest]`. The
chapter never says or shows that `*` can appear anywhere in a sequence
pattern. Confirmed working: `case [*init, last]:` against `[1, 2, 3, 4]`
returns `([1, 2, 3], 4)`. A reader generalizing from the single example shown
has no way to know `[*init, last]` or `[first, *middle, last]` are even legal
syntax. Fix: one line noting the star can appear anywhere (but only once),
with a second variant shown.

## Chapter 14 (Decorators): 6 findings

### [missing] Chapters/14_Techniques--Decorators.md:136 — decorators silently break on async functions
Every decorator in the chapter (`trace`, `repeat`, `count_calls`, the class forms) assumes a synchronous wrapped function; none is ever mentioned as a limitation. Applying `tracer.trace` to an `async def add` prints the wrong result and never awaits the wrapped call. Confirmed by running: `@trace` on `async def add(a,b): return a+b`, calling `await add(2,3)` under `asyncio.run`, prints `<- add = <coroutine object add at 0x...>` instead of `5` (the real `5` only surfaces later when the caller separately awaits it). Decorating async code is one of the first things an experienced reader tries; the chapter should say a wrapper over a coroutine function must itself be `async def` and `await func(...)`.

### [missing] Chapters/14_Techniques--Decorators.md:876 — pizza's list alternative is never weighed
"Consider a pizza shop. A class for every pizza-and-topping combination explodes... Instead, model the toppings as decorators." But the motivating problem (combinatorial subclasses) is just as well solved by giving `Pizza` a `toppings: list[Topping]` attribute and summing costs/joining descriptions — no wrapping, no `Protocol`, no recursive `__init__`. That's the standard "why decorator-pattern-for-pizza is overkill" objection, and it is a well-known alternative the chapter never raises or dismisses. Since cost and description here are purely additive (not order-sensitive polymorphic behavior), the list approach is arguably more idiomatic Python, and the chapter's payoff ("adding a topping means one class") doesn't show why that beats "adding a topping means one list entry."

### [missing] Chapters/14_Techniques--Decorators.md:1026 — exercise 5 requires a technique never taught
Exercise 5: "Write a `memo` decorator that works both with and without parentheses... Distinguish the two forms by checking whether the decorator's first argument is callable." The chapter teaches decorators-with-arguments and decorators-without-arguments as two separate, cleanly distinguished shapes (`repeat` vs `trace`), but never once discusses writing a single decorator that must inspect its first argument to decide which calling convention is in play — a common but non-obvious idiom (used by `pytest.fixture`, `click`, etc.). `grep -n "callable("` over the chapter returns nothing. This exercise tests a technique with no supporting example anywhere above it.

### [could-be-better] Chapters/14_Techniques--Decorators.md:289 — repeat()'s "call once, then loop times-1" buries the section's point
Three sentences justify `wrapper()`'s odd shape (call `func` unconditionally once, then loop `times - 1` more) on typing grounds: "so `result` always holds a value of type `R` to return." I checked this by running `uv run ty check` against a version using the plain `for _ in range(times): result = func(*args, **kwargs)` — it type-checks clean (`All checks passed!`), and since `repeat()` already rejects `times < 1` at decoration, `times >= 1` always holds by the time `wrapper()` runs, so the simple loop is also runtime-safe. The extra structure and its justifying paragraph add incidental complexity to a section whose actual point is decorator arguments, not defensive loop-shaping.

### [missing] Chapters/14_Techniques--Decorators.md:1004 — no limitation stated for stack traces or call overhead
The chapter covers `wraps`/`update_wrapper` for metadata fidelity in detail but never mentions the two costs every decorator imposes regardless: an extra stack frame per call (a traceback through a decorated function shows `wrapper`, not just the caller and the original body — even with `wraps`, since `wraps` copies metadata, not the call stack) and the per-call overhead of the extra Python-level call. `grep -in "traceback\|overhead"` over the chapter finds nothing. An experienced reader evaluating whether to reach for a decorator vs. inlining the behavior needs this trade-off named somewhere, and "Decorators You Already Know" (right before the exercises) is a natural place for one sentence on it.

### [could-be-better] Chapters/14_Techniques--Decorators.md:3 — opening states the mechanism, never the motivation
The chapter's first paragraph ("A decorator is a callable that you apply to a function or a class...") is pure mechanism with no "why would you want this" framing — no mention of cross-cutting concerns, avoiding repeated boilerplate, or the specific pain (logging/timing/validation code smeared across many functions) decorators exist to solve. The second paragraph moves straight to syntax ("To apply a decorator, put `@`..."). A reader meeting decorators for the first time gets the "what" before ever seeing the problem that made this feature worth adding to the language.

## Chapter 15 (Context Managers): 5 findings

### [missing] Chapters/15_Techniques--Context_Managers.md:218 — `__exit__()` raising and masking the original exception is never mentioned
"The `__exit__()` Arguments" explains all three arguments and the truthy-return suppression rule, but never says what happens when `__exit__()` itself raises during cleanup: it replaces the block's exception, and the original survives only as `__context__`. Verified:
```python
class Bad:
    def __exit__(self, *a): raise ValueError("cleanup error")
with Bad(): raise KeyError("original")
```
Output: `caught: ValueError('cleanup error')`, `context: KeyError('original')`. This is the most common real-world context-manager bug, a broken cleanup path hiding the real failure, and it fits naturally right after `enter_fails.py`, which already covers the mirror case (setup failing before cleanup is registered).

### [missing] Chapters/15_Techniques--Context_Managers.md:208 — partial-acquisition cleanup is asserted twice, demonstrated never
Line 208: "An `__enter__()` that acquires several things must clean up its own partial work before it raises an exception." Line 211: `ExitStack` "unwinds whatever it already entered when a later entry fails." Both are true — I ran a 3-manager `ExitStack` where the third's `__enter__` raises: `a` and `b`'s cleanup both fire, `c`'s never runs (`enter a / enter b / enter c (will fail) / exit b / exit a / caught: boom during enter`) — but no listing shows either case. `enter_fails.py` only has one manager failing outright; `exit_stack.py` never has a failing entry. The chapter's central safety claim about partial acquisition is taken on faith.

### [does-not-work] Chapters/15_Techniques--Context_Managers.md:770 — the pool's stated reason for using `Queue` is never exercised
"`Queue` is thread-safe, and `get()` blocks while the pool is empty... Hand the same pool to several threads, and it becomes the throttle that limits concurrent use, the way a real database connection pool does." Every listing and test (`object_pool.py`, `test_object_pool.py`) runs single-threaded; nothing ever blocks, nothing ever contends. The actual reason to use `Queue` over a plain list (thread safety and blocking under contention) is asserted, never shown, so the reader has no evidence `Pool` behaves any differently under concurrent load than a container the chapter never even names as the alternative it beats.

### [missing] Chapters/15_Techniques--Context_Managers.md:832 — no case for skipping a hand-written manager altogether
"Choosing a Form" picks among `contextlib`, generator, class, and `ContextDecorator`, but never considers not writing a manager at all: a plain `try`/`finally` inline, for setup/teardown used exactly once and never reused elsewhere. Every example in the chapter is a reusable, named manager, so a reader comes away believing the choice is only ever among manager flavors, never whether the `__enter__`/`__exit__` (or `@contextmanager`) indirection is worth it for a single, local block. One sentence weighing `try`/`finally` against the lightest `contextlib` form would close this.

### [missing] Chapters/15_Techniques--Context_Managers.md:709 — nothing stops a borrower from using a leased object after it's returned
"Lending is the dangerous half. Every borrower must return the object on every path out of their code... or the pool slowly drains." The chapter solves the drain but never raises the mirror bug: nothing in `Pool` or `lease()` stops a borrower from stashing `conn` outside the `with` block and calling `conn.query()` after it has been handed to a second borrower, corrupting whatever state the object holds. The "production pool" paragraph (line 818) lists lazy creation, validation, and timeouts as refinements but omits this one, arguably the more dangerous failure mode for a mutable pooled resource.

## Chapter 16 (Comprehensions): 4 findings

### [missing] Chapters/16_Techniques--Comprehensions.md:305 — the motivating problem has a one-line stdlib answer the chapter never weighs
`path_walk_comprehension.py` builds a tree, then uses a two-level comprehension
over `root.walk()` to collect every `.py` file. But the exact task it solves
("find every .py file under a tree") is what `Path.rglob()` exists for. Ran it:
`[p.relative_to(root).as_posix() for p in root.rglob("*.py")]` produces the
identical `main.py` / `pkg/util.py` result in one line, no `walk()`, no nested
`for`. The chapter never mentions `rglob()` or explains why the more general,
more verbose `walk()` comprehension is worth reaching for here instead. Fix:
either use a filter `rglob()` can't express (so the comprehension earns its
keep), or add a sentence dismissing `rglob()` for this simple case.

### [missing] Chapters/16_Techniques--Comprehensions.md:132 — the walrus's canonical comprehension use case is never shown
The scope section demonstrates `total := total + n` as a running-sum
accumulator, an unusual, rarely-seen pattern. The idiom PEP 572 itself uses to
justify walrus-in-comprehension, and the one working programmers actually
reach for, is avoiding a double computation in a filter/output pair:
`[y for x in data if (y := f(x)) is not None]`. That shape never appears
anywhere in the chapter. A reader who takes away only the accumulator trick
has learned the exception to comprehension scope but not the reason the
language added it. Fix: replace or supplement the running-sum example with
the filter-and-reuse idiom.

### [missing] Chapters/16_Techniques--Comprehensions.md:198 — the duplicate-value collision is asserted, never run
"Inverting assumes the values are unique. If two keys share a value, the
later entry wins" (lines 209-210) is stated as prose only; `invert_dict.py`'s
`seat_of` has no duplicate values, so the claim is never exercised. Confirmed
it's true (`seat_of = {"Arthur": 1, "Galahad": 2, "Robin": 1}` →
`{1: 'Robin', 2: 'Galahad'}`), but the chapter asks the reader to take the
important caveat on faith rather than seeing it happen, unlike almost every
other claim in the chapter, which does get a runnable demonstration. Fix: add
one duplicate-valued entry to `seat_of` and print the collision.

### [better] Chapters/16_Techniques--Comprehensions.md:255 — the one common beginner mistake in flattening has no counterexample
The chapter correctly states that in `[x for row in rows for x in row]` the
clauses "read left to right, in the order the equivalent nested loops would
appear," but never shows what happens when a reader gets the order backward,
which is the actual failure mode that trips people up. Ran the swapped form:
`[x for x in row for row in rows]` raises `NameError: name 'row' is not
defined` because `row` isn't bound yet when the first `for` clause is
evaluated. One line showing that error would make the ordering rule
memorable instead of just stated.

## Chapter 17 (Metaprogramming): 8 findings

### [does-not-work] Chapters/17_Techniques--Metaprogramming.md:224 — the lazy greenhouse builds all seven classes anyway, so laziness is never demonstrated
The prose motivates `greenhouse.py` with "The dict comprehension builds all seven classes whether the schedule uses them or not. Seven is cheap; hundreds would cost." But `schedule.txt` (line 319) names every one of the seven types, so the lazy version pays the full cost. `cd build/examples/17_Techniques--Metaprogramming && uv run python greenhouse.py` prints seven `Creating ...` lines — one per declared name. The reader gets a `dict` subclass, a sentinel, and a `__getitem__` override that demonstrably save nothing. Fix: drop four names from `schedule.txt` so the trace shows three classes built out of seven declared, which is the whole point.

### [does-not-work] Chapters/17_Techniques--Metaprogramming.md:206 — nothing in either generation example uses the generated classes as types
"Each generated class is a real type, not a label. `LightOn` and `WaterOff` are distinct subclasses of `Event`, so `isinstance()` tells them apart and you can later give either one behavior of its own." Neither listing does either thing: `grep -n "isinstance\|match " eager_event_classes.py greenhouse.py` finds nothing, and `run_events()` prints `e.action`, a string. The chapter concedes it at line 331 ("Calling `Event(class_name, hour, minute)` directly would print the same schedule"). So the section's own centerpiece works identically without the feature being taught. Fix: give one generated class overriding behavior (a `RingBell` that prints differently), or dispatch on type in `run_events()`.

### [missing] Chapters/17_Techniques--Metaprogramming.md:413 — classes built by `type()` or `exec()` cannot be pickled, and the `exec()` ones land in `builtins`
The `exec()` section warns only about injection. Two limitations that bite even with validated names go unstated. Running against the extracted listings: `pickle.dumps(commander.Command.make_class("Start")())` raises `PicklingError: Can't pickle <class 'Start'>: it's not found as builtins.Start`, because the private namespace has no `__name__` so `__module__` becomes `builtins`; and `inspect.getsource()` on that class raises `TypeError: <class 'Start'> is a built-in class` — a real cost in the chapter that later teaches `inspect`. The `type()` classes fail pickling too (not found as `eager_event_classes.LightOn`). Fix: two sentences plus a `__module__`/`__qualname__` note on both generators.

### [missing] Chapters/17_Techniques--Metaprogramming.md:1286 — the chapter's stated "whole case for a metaclass" never gets a listing worth keeping
Line 1286: "That is the whole case for a metaclass: the class object needs behavior." The intro promises the concrete instance twice — `EnumType` making `for c in Color` work (line 76), and "the `__iter__()` that lets `EnumType` make `for c in Color` work" (line 1230). No listing ever shows it. The two class-behavior demos are `singleton.py`, which the chapter immediately disowns ("heavier than the problem usually requires", line 1110), and `mixin.py`'s `helper()` returning `"hi"`. So the reader finishes without seeing one metaclass they would keep. Fix: a ten-line metaclass giving a class `__iter__`/`__len__`, the promised `for c in Color`.

### [missing] Chapters/17_Techniques--Metaprogramming.md:795 — descriptors get the mechanism with no reason to want one
`set_name.py`'s `Field` only prints and forwards: `__set__` stores, `__get__` reads back. It shows how the protocol fires but never why anyone writes a descriptor, so the reader learns a hook with no job. This matters more than usual because Decorators hands descriptors here explicitly ("The one piece of machinery left for later is the descriptor protocol those first four return; [Metaprogramming] takes it up", 14_Techniques--Decorators.md:1006), and this chapter never explains how `@property`/`@classmethod` are descriptors. The related failure mode is also absent: reading before writing raises `AttributeError: 'Point' object has no attribute '_x'`, leaking the storage key. Fix: make `Field` validate on `__set__` and handle the unset case.

### [better] Chapters/17_Techniques--Metaprogramming.md:1342 — "The `inspect` Module" spends 380 of its 430 lines on a tool's presentation layer
`inspect_tour.py` (15 lines, four `inspect` calls) is the chapter's entire treatment of the module. Everything from line 1342 to 1722 — 21% of the chapter — is `display.py`'s implementation plus three subsections explaining its options. Most of that listing is formatting: `_truncate`, `_format_method`, `_format_attribute`, `_shared`, the sentinel dunder modes, and a 45-line `ALL_DUNDERS` dump answered by "The rest is the bookkeeping every class carries." The `inspect` content inside it is four calls. Fix: keep `getmembers_static`/`signature`/`get_annotations` in the narrative, move the formatting helpers and the `dunder`/`exclude` option tour to an appendix or a reference section.

### [missing] Chapters/17_Techniques--Metaprogramming.md:1215 — the metaclass-conflict fix is named but never shown, and the listing hides the message that explains it
"The result is a metaclass conflict, and the fix is a metaclass for `C` that inherits both." No code follows, and `multiple_metaclass_inheritance.py` prints `type(error).__name__`, so the reader sees only `TypeError`. The suppressed message is the teaching: `metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases`. This is the one metaclass failure a reader will actually hit, since the chapter told them at line 72 that `abc.ABCMeta` is a metaclass they already use. Fix: add three lines showing `class MetaC(MetaA, MetaB)` and `class C(A, B, metaclass=MetaC)`.

### [better] Chapters/17_Techniques--Metaprogramming.md:1232 — the third "you still need a metaclass" bullet is one the chapter already solved without a metaclass
"Enforcing an invariant across an entire family of classes through their shared metaclass" is exactly what `init_subclass.py` (line 457) and `final_runtime.py` (line 587) do with `__init_subclass__`, which the chapter presents as the simpler replacement. The list of three is followed by "`__prepare__()` is the one with no simpler substitute", which quietly concedes the point for bullets one and three, yet the bullets stand as reasons. Fix: cut bullet three or qualify it (an invariant a base class cannot express because the family shares no base), and cross-reference `singleton.py`/`mixin.py` for bullet one instead of leaving it unillustrated here.

## Chapter 18 (Performance): 8 findings

### [does-not-work] Chapters/18_Techniques--Performance.md:729 — `heap_vs_hash.py` beats a strawman, and the obvious competitor beats the heap on the listing's own data
The listing times a heap against calling `min()` on a `set` 100 times, which nobody writes. The realistic competitor for "100 smallest" is `sorted(data)[:100]`, and on this listing's `data = list(range(n, 0, -1))` it wins: heap 0.0099s, sorted 0.0022s (`uv run python heapalt.py`, `min(timeit.repeat(..., number=50, repeat=3))`). Timsort detects the descending run. Only on shuffled data does the heap win (0.0167 vs 0.0535). Also `heapq.nsmallest()`, which line 659 recommends for exactly "top-N questions", is never used here and measures 0.1112s on this data. Time the heap against `sorted()[:k]` on shuffled input, and state the heap's real case: interleaved push/pop, where sorting cannot be amortized.

### [missing] Chapters/18_Techniques--Performance.md:157 — the chapter's own method (profile, fix, remeasure) is never performed, and the one profile shown is of a script that does not exist
Line 157 says "This one profiles a small script, `prof_demo.py`" and shows a `cProfile` table with rows for `slow`, `helper`, and a genexpr. `grep -rn prof_demo .` returns hits only in this chapter's prose: the script is nowhere in the repo, so the reader cannot run it, cannot see which code made the "one call burning six milliseconds" row, and cannot connect the table to a fix. `profiling.sampling` gets two invocation lines and no output at all. Every later section is an isolated micro-benchmark of a technique already known to win, so the closing claim (line 1460, "the bottleneck moves") is asserted and never shown. Add `prof_demo.py` as a real listing and carry one slow program through profile, fix, and remeasure.

### [missing] Chapters/18_Techniques--Performance.md:1443 — the CPU-bound / I/O-bound fork, the first question a profiler answers, is never named
`grep -n "CPU-bound\|I/O-bound"` on the chapter returns nothing. The "Choosing a Strategy" ladder is ordered by cost and puts concurrency at step 10, so a reader whose program spends 90% of its time waiting on a database is directed through eight steps (newer CPython, idiomatic loops, `bisect`, generators, caching, slots, NumPy, Rust) that cannot help before reaching the one that can. The chapter says only "When the slowdown comes from waiting on the outside world, use `asyncio`" (line 1431), buried in a section after Rust. Make "are you CPU-bound or waiting?" step 1.5, immediately after the profiler tells you, and branch the ladder on the answer.

### [missing] Chapters/18_Techniques--Performance.md:1004 — the Slots section recommends `slots=True` as a default and states one limitation; the chapter's own caching advice collides with it
Line 1004 says "prefer `slots=True`" and line 1018 calls frozen-plus-slots "the natural default", listing only "instances can no longer grow attributes". Five sections earlier, line 911 recommends `functools.cached_property`. The two cannot be combined: `@dataclass(slots=True)` with a `cached_property` raises `TypeError: No '__dict__' attribute on 'N' instance to cache 'total' property` (verified, `uv run python cp.py`). Three more limitations are absent: no `weakref` unless `__weakref__` is declared (`TypeError: cannot create weak reference`), `TypeError: multiple bases have instance lay-out conflict` on multiple inheritance from two slotted classes, and a subclass with no `__slots__` silently restores `__dict__` (currently only exercise 6). Add a "when slots does not fit" paragraph and cross-link it from line 911.

### [missing] Chapters/18_Techniques--Performance.md:917 — "Reduce Memory Overhead" opens on a performance claim and delivers only byte counts
The premise is "With millions of objects, per-object overhead can dominate performance", but no listing in the section holds millions of objects and none measures time. `slots_dataclass.py` sizes one instance (344 vs 48 bytes), `compact_array.py` sizes a 10,000-element container, `memory_view_size.py` sizes one slice. The mechanism that turns "smaller" into "faster" — fewer GC-tracked objects, cache locality, slot access as a fixed offset instead of a dict lookup — is never stated or measured, so the section's stated payoff never arrives. One added `timeit` over a large population of slotted versus dict-backed instances, or one sentence naming the mechanism, would close it.

### [missing] Chapters/18_Techniques--Performance.md:1069 — the `memoryview` section shows the mechanism, never a use, and omits the trap that bites first
`memory_view.py` slices `b"ABCDEF"` and `memory_view_size.py` compares `sys.getsizeof` of a slice against a view. Neither shows a view doing work (parsing a frame or header without copying), so the reader sees the saving without the situation that produces it. Two limitations are absent, both easy to hit with the chapter's own `bytearray` example: an open view blocks resizing (`data.append(1)` raises `BufferError: Existing exports of data: object cannot be re-sized`), and a view over `bytes` is read-only (`TypeError: cannot modify read-only memory`), though line 1079 writes through a view of a `bytearray` with no note of the difference. Both verified with `uv run python probes.py`.

### [better] Chapters/18_Techniques--Performance.md:1404 — "one baseline and three ways past it" reads as a ladder, but the chapter's own numbers show Numba beating Rust on both benchmarks
Lines 1404-1410 present NumPy, Numba, and Rust as escalating steps past the same baseline. The sample outputs say otherwise: Numba reports 15.9x (line 1194) and 54.4x (line 1256) on `count_primes` and `collatz_lengths`; Rust reports 12.2x (line 1382) and 34.3x (line 1395) on the same two functions. The Python baselines are equivalent — I timed the NumPy-indexed Collatz baseline against the list version at 0.326s vs 0.318s, a 2% difference — so the reader cannot dismiss it as a different baseline, and the numbers come from separate hand-copied runs with no way to tell. Say plainly that Numba matches or beats Rust on numeric loops, and that Rust buys no warm-up, no runtime dependency, and code Numba refuses to compile.

### [missing] Chapters/18_Techniques--Performance.md:34 — "Try a Faster Platform" omits the free-threaded build, then uses "free threading" as an undefined term
The section enumerates newer CPython, the JIT, PyPy, and hardware; step 2 of the strategy ladder (line 1448) repeats that list. The free-threaded build (PEP 703, separately installed since 3.13) is the largest platform-level speedup available to a parallel workload in 3.15 and appears nowhere in either list. It does appear once, at line 134, inside the PEP 836 discussion: "the JIT combined with free threading by 3.17", a term the chapter never defines and never links. [Concurrency](19_Techniques--Concurrency.md#the-gil-and-free-threading) covers it fully, so the fix is one sentence and one link in "Try a Faster Platform", plus the same link at line 134.

## Chapter 19 (Concurrency): 8 findings

### [does-not-work] Chapters/19_Techniques--Concurrency.md:1377 — the "Coordinating Threads with Queues" centerpiece has no consumer, and threads change nothing
Line 1370 promises "a thread-safe queue that hands each item to a single
consumer, with built-in locking," and line 1415 says "`get()` blocks until an
item is available, so an idle consumer waits." `priority_queue.py` shows
neither. Two producer threads `put()` four jobs; the `with` block joins them;
then the *main* thread drains. A `PriorityQueue`'s drain order depends only on
the multiset of items, so replacing the pool with two sequential `enqueue()`
calls prints the identical four lines. The listing demonstrates heap ordering,
not coordination, and the chapter then spends three paragraphs (1421-1428)
disclaiming its own drain loop. Fix: show a real consumer thread parked on
`get()`, the shape `async_queue.py` already shows for tasks.

### [missing] Chapters/19_Techniques--Concurrency.md:233 — the chapter never bounds a wait: `asyncio.timeout()` appears nowhere
`grep -n "timeout" Chapters/19_*.md` returns five hits, all inside
`async_deadlock.py` (2066) and its prose, where `wait_for()` is an escape
hatch so a demo doesn't hang. Timing out a hung network call is the most
common real requirement in the I/O-bound code this chapter is about, and the
chapter builds every prerequisite for it: `TaskGroup`, `except*`, and a full
treatment of `CancelledError` semantics at 353-360. The payoff never arrives.
`asyncio.timeout()` (3.11) is the modern cancel-scope form, composes with
`TaskGroup`, and its expiry converts a `CancelledError` into a
`TimeoutError` — exactly the mechanism 353-360 sets up. Fix: a short
subsection under `TaskGroup` showing `async with asyncio.timeout(...)`.

### [missing] Chapters/19_Techniques--Concurrency.md:1425 — the chapter asks how a blocking consumer stops, then never answers
"A live consumer does not poll `empty()`. It calls `get()` directly and lets
the block do the waiting." That raises the obvious question — how does a
consumer parked forever in `get()` ever shut down? — and the queue section
ends without answering it. No sentinel, no poison pill, no
`Queue.shutdown()`. Both `queue.Queue.shutdown()` and
`asyncio.Queue.shutdown()` exist on the pinned interpreter
(`uv run python -c "import queue,asyncio; print(hasattr(queue.Queue,'shutdown'),
hasattr(asyncio.Queue,'shutdown'))"` prints `True True`); they are 3.13
additions and are the modern answer. Bounded queues (`maxsize`, backpressure)
are absent for the same reason. Fix: end the section with `shutdown()` on the
consumer example.

### [missing] Chapters/19_Techniques--Concurrency.md:1245 — `threading.Lock` is named three times as "the fix" and never once shown
Lines 646, 683, and 1245 all promise it: "the same race between threads needs
a `threading.Lock`", "the same fix `threading.Lock` produces for threads",
"Threads that share mutable state need a lock." `gil_race.py` (1218)
demonstrates the thread race in full, and the chapter then walks away without
fixing it, while the asyncio half gets a dedicated before/after pair
(`async_race.py` → `async_locks.py`). The only `threading.Lock` in the
chapter's code space is exercise 13 (2329), which uses it *incorrectly* on
purpose. A reader who learns concurrency from threads sees the failure and
never sees the repair. Fix: a `gil_locks.py` sibling, four lines different
from `gil_race.py`.

### [missing] Chapters/19_Techniques--Concurrency.md:206 — a chapter about asynchronous I/O contains no I/O
"A real network request asks the loop to watch a socket for the reply" is the
mechanism the whole first half rests on, and it is asserted, never shown.
Every I/O listing in the chapter (`async_mechanics.py`, `fetch_demo.py`,
`peak_concurrency.py`, `blocking_the_loop.py`, `to_thread.py`,
`io_threads.py`, `mixed_await.py`) stands in `asyncio.sleep()` or
`time.sleep()` for the network. A reader finishes the chapter having never
seen an `await` on a real file descriptor, so "the loop watches a socket"
stays a story. Fix: one stdlib-only, deterministic listing —
`asyncio.start_server()` plus two concurrent `asyncio.open_connection()`
clients on localhost — replacing one of the redundant sleep-based demos.

### [better] Chapters/19_Techniques--Concurrency.md:1839 — "Measuring the Difference" does not measure the thread side
`task_vs_thread_memory.py` measures the task cost with `tracemalloc`, then
compares it against a number the listing supplied itself.
`threading.stack_size()` returns `0` by default (`uv run python -c "import
threading; print(threading.stack_size())"` → `0`); the listing sets
`STACK_SIZE = 1024 * 1024` at line 1860 and reads it straight back, so the
output `one thread's stack reservation: 1,048,576 bytes` (1896) and the
derived `tasks_per_stack` (776 on this machine) discover nothing about the
machine. Line 1913's "hundreds to one" compares reserved address space to
resident heap; a parked thread's actual footprint is far smaller. Fix: say
plainly that the thread figure is a stipulated reservation, not a
measurement.

### [better] Chapters/19_Techniques--Concurrency.md:1752 — the capstone listing blocks the event loop it teaches you never to block
`mixed_await.py` opens `with ProcessPoolExecutor() as pool:` *inside* `async
def main()`. `ProcessPoolExecutor` spawns its workers lazily from the calling
thread on first submit, and `__exit__` calls `shutdown(wait=True)`, joining
every worker process — both on the event-loop thread, which is exactly the
guideline at 2180 ("Never call a blocking function inside a coroutine") and
the failure `blocking_the_loop.py` exists to teach. It is measurable:
`uv run python build/examples/19_Techniques--Concurrency/mixed_await.py` takes
0.379s against a 0.094s bare-interpreter baseline, for 0.05s of awaited work.
Fix: build the pool before `asyncio.run()` and pass it to `main()`.

### [better] Chapters/19_Techniques--Concurrency.md:648 — the coordination primitives are split across 1,300 lines of unrelated material
"Locks" (648) introduces `asyncio.Lock` and then forwards to "Locks,
Semaphores, and Failure Modes" (1975), whose three listings
(`async_semaphore.py`, `async_deadlock.py`, `async_livelock.py`) are pure
asyncio and belong with the asyncio material they continue. Between the two
sit processes, Amdahl's Law, the GIL, free threading, subinterpreters, queues,
shared iterators, executors, and the task-vs-thread memory measurement. The
later section has to rebuild its own context from scratch (1976-1984 re-narrates
`async_race.py`). Fix: move Semaphores up beside Locks, and keep only
Deadlock/Livelock at the end, or move the whole block up and let the thread
and process material run uninterrupted.

## Chapter 20 (Rethinking Objects): 6 findings

### [missing] Chapters/20_Patterns--Rethinking_Objects.md:1088 — the pro-OOP case gets no code, everything else in the chapter gets three
Every anti-OOP claim in the chapter (leaky encapsulation, fragile base classes, protocol collisions, LSP violations) is backed by a runnable listing, several with a follow-up test file. "OOP Is Useful, Sometimes" (lines 1088-1106) is the one section that argues the other side, and it is pure prose: "A class is a clean namespace with dot-completion... you are passing the same data into every function, or bundling behavior with state." No listing shows a case where bundling behavior with state actually wins over a function-plus-data alternative. An expert reader who has just watched five sections dismantle OOP has no comparable evidence for when to reach for it. Fix: add one small listing where a class genuinely beats the functional alternative, argued with the same rigor as the rest of the chapter.

### [missing] Chapters/20_Patterns--Rethinking_Objects.md:255 — "encapsulation exists only because of mutability" ignores representation-hiding
"Encapsulation exists only because of mutability. If the data cannot change, you have nothing to protect." This is the premise for dropping getters entirely once a class is frozen. But classic encapsulation serves a second, independent purpose: hiding representation so it can change later without breaking callers. `immutable.py`'s `Immutable` exposes `numbers` and `bob` as public fields — frozen, but now permanently part of the API; switching `numbers` from a `tuple` to some other sequence type is a breaking change no property could have absorbed. The chapter never weighs this well-known cost of going public-fields-everywhere, only the mutation-protection angle. Fix: a sentence acknowledging that immutability removes the mutation reason for encapsulation but not the evolution reason.

### [missing] Chapters/20_Patterns--Rethinking_Objects.md:762 — protocols' discoverability cost is never weighed
Lines 762-774 argue structural typing beats nominal typing because "the type's author need not hear that your protocol exists." True, but that same property is a well-known criticism of structural/duck typing: nothing in `Invoice`'s class body (multi_protocol.py) says it participates in `Priced`, `Serializable`, or `Describable` — you cannot grep the codebase for "what implements Priced," the way you could for a base class or an explicit `implements` list. `protocol_collision.py`, two sections later, is a direct symptom of this cost (accidental structural matches), yet the chapter never states the general tradeoff: nominal typing costs you an inheritance graph but buys you discoverability, which structural typing gives back. Fix: one sentence naming this cost where protocols are first argued for.

### [missing] Chapters/20_Patterns--Rethinking_Objects.md:80 — no mitigation offered for what "no tool checks" leaves open
The LSP section states flatly that "no tool reads the behavior behind the signature" (line 80) and ends "The base class calls a method and trusts every subclass to stand in for the base" (line 73), with nothing between the diagnosis and moving on to the next promise. The standard mitigation — a shared conformance test suite run against every subtype, exactly the kind of thing this same chapter already demonstrates three times over (`test_plugged.py`, `test_immutable.py`, `test_newtype_boundary.py`) — is never mentioned here, even though it is the natural answer to "no tool checks this, so what do you do instead." Fix: a paragraph pointing out that a behavioral contract can be tested, even if it can't be checked statically, with a pointer to the pattern already used elsewhere in the chapter.

### [better] Chapters/20_Patterns--Rethinking_Objects.md:778 — "the interpreter must pick" overstates Python's diamond problem
"If two base classes trace back to a common ancestor, the interpreter must pick which version of an overridden method to call." Phrased this way, right after invoking "the diamond problem" (a term readers know from C++, where the choice is genuinely ambiguous and needs explicit disambiguation), it reads as if Python faces the same crisis. It doesn't: C3 linearization picks deterministically every time, and any reader who knows `super()` and MRO already knows this. The chapter is technically correct but leaves an experienced reader wondering what exactly protocols "avoid" that MRO didn't already resolve. Fix: name the mechanism (MRO/C3) so the sentence contrasts "deterministic but easy to get wrong" with "the question doesn't arise," instead of implying unresolved ambiguity.

### [better] Chapters/20_Patterns--Rethinking_Objects.md:347 — the one concrete advantage of methods is conceded 700 lines later, disconnected from the comparison
"Methods or Functions?" (line 347) shows `distance_to()` and `distance()` computing identically and states methods have "one advantage: it can live outside `Point`" (line 389) — all downside, no upside, for methods. The upside the chapter eventually grants methods — "a clean namespace with dot-completion" — doesn't appear until "OOP Is Useful, Sometimes" at line 1091, disconnected from the very comparison that raised the question. A reader working through the methods-vs-functions section gets a one-sided case with the balancing fact deferred to the very end of the chapter. Fix: a clause in "Methods or Functions?" itself noting the discoverability tradeoff, even briefly, so the comparison isn't purely one-sided where it's first made.

## Chapter 21 (Design Patterns): 3 findings

### [missing] Chapters/21_Patterns--Design_Patterns.md:225-289 — Design Principles list omits the Liskov Substitution Principle
"Design Principles" (lines 241-289) presents twelve principles as "at least
as important as design patterns" and worth holding "in your head while
analyzing a design," yet never mentions LSP. The immediately preceding
chapter builds an entire section around it
(`Chapters/20_Patterns--Rethinking_Objects.md:59` "## The Liskov
Substitution Principle"), and chapter 25 cites it as the pattern's
justification (`Chapters/25_Patterns--Template_Method.md:240,317`). An
expert reader who just read chapter 20 will look for LSP here and not find
it. Fix: add a bullet (or a pointer to `20_Patterns--Rethinking_Objects.md#liskov-substitution`)
alongside the other cross-referenced principles (immutability, pure
functions).

### [better] Chapters/21_Patterns--Design_Patterns.md:241-289 — Three-quarters of the listed principles are never used again
Of the twelve principles bulleted here, only three earn any later
mention: *Subtraction* (`grep`: also named in
`32_Patterns--Multiple_Dispatching.md`, and linked to
`37_Patterns--Pattern_Refactoring.md`), immutability, and pure functions
(both linked out to chapters that develop them). *Least astonishment*,
*Consistency*, *Law of Demeter*, *Independence/Orthogonality*, *Managed
Coupling*, *Simplicity before generality*, *Reflexivity*, and *Once and
once only* appear exactly once in the book, here, and are never invoked
by name again (checked with `grep -rl` for each term across
`Chapters/`). The chapter claims these are fundamental enough to keep in
mind while designing, but the book itself never puts nine of them to
work. Fix: either trim to the principles the book actually uses, or add
at least one callback per principle in a later pattern chapter.

### [missing] Chapters/21_Patterns--Design_Patterns.md:138-157 — The Strategy listing has no stated motivating problem, and its builtins were never candidates for the classic pattern
The section builds to "Here is the whole of a *Strategy* in Python"
(line 138) and the listing (verified: `uv run python
build/examples/21_Patterns--Design_Patterns/strategy_is_a_function.py`
prints `3 6`, matching the marker). But no problem is posed before the
listing — no scenario where a reader would reach for interchangeable
algorithm objects. The listing passes `max`/`sum` to `apply()`; nobody
would design a `Strategy` class hierarchy around calling a builtin, so
the example proves function-passing works without ever showing what the
classic three-part machinery (interface, one class per algorithm,
context) was *for*. Chapter 28's later `algorithms.py`/`strategy.py`
supply a real motivating case; a one-sentence pointer here ("chapter 28
works through a realistic case; this shows only the shape") would keep
the promise "the whole of a Strategy" from overstating what this listing
demonstrates.

## Chapter 22 (Data Transfer Objects): 5 findings

### [does-not-work] Chapters/22_Patterns--Data_Transfer_Objects.md:3 — chapter never teaches what a DTO is for
The chapter borrows Fowler's DTO name for "Messenger" but redefines it as
something that "carries a function's return values" (line 5). Fowler's DTO,
and the book's own catalog (`Chapters/39_Patterns--Pattern_Catalog.md:122`,
"Carry data between processes in one batched object"), exists to batch data
across a process/network boundary and cut round trips. Chapter 22 contains
zero occurrences of "process," "boundary," "network," or "batch" (checked
with `grep -in`); every example is a same-process attribute bag or return
value. The chapter teaches a real idiom well, just not the boundary-crossing
one its name and the catalog entry promise. Fix: add the missing
boundary-crossing motivation, or retitle the teaching claim.

### [does-not-work] Chapters/22_Patterns--Data_Transfer_Objects.md:265 — the cross-type `order=True` claim is asserted, never run
Lines 265-266 claim a comparison "between two different frozen types raises
[a `TypeError`] even" with `order=True` on both. `still_a_tuple.py` only
demonstrates the *no*-`order=True` case. I ran the untested half: two
`@dataclass(frozen=True, order=True)` classes of different shape,
`A(1,2,3) < B(1,2,4)`, raises `TypeError: '<' not supported between
instances of 'A' and 'B'` — the claim holds, but the chapter asserts its
least-obvious half (a reader could plausibly expect `order=True` to enable
cross-type comparison) without ever showing it, breaking the
demonstrate-then-explain pattern the rest of the chapter uses.

### [better] Chapters/22_Patterns--Data_Transfer_Objects.md:202 — `astuple()` copy semantics repeats ch12 with no link back
Lines 202-204 restate that `astuple()` recurses and "deep-copies every
other field rather than sharing it" — the same fact chapter 12 already
teaches with a full listing (`Chapters/12_Techniques--Data_Classes_as_Types.md:1230-1259`,
`asdict_astuple.py`: "`asdict()` and `astuple()` copy as they go"). Chapter
12 forward-links to chapter 22 for the equality difference (line 326),
showing the book's own convention is to link rather than re-explain
shared material; chapter 22 doesn't reciprocate here. Fix: replace the
restatement with a link to chapter 12's `#more-data-class-tools` anchor.

### [missing] Chapters/22_Patterns--Data_Transfer_Objects.md:301 — no exercise practices the chapter's actual decision framework
"Which Should You Use?" (lines 277-299) is the chapter's payoff: choosing
among `SimpleNamespace`, `@dataclass`, `NamedTuple`, `TypedDict` by whether
tuple behavior is wanted. All six exercises (301-326) instead ask for
small mechanical edits to earlier listings (add a field, mutate a list,
predict an equality) — none asks the reader to pick a type for a new
scenario and justify it. The chapter's central teaching goes unexercised.
Fix: add an exercise with 2-3 short scenarios (a config bag, a hashable
coordinate, a JSON payload) asking which type fits and why.

### [better] Chapters/22_Patterns--Data_Transfer_Objects.md:58 — one section covers three unrelated constructs
"The Standard-Library Versions" runs ~110 lines covering three separate
constructs under one heading naming none of them: `SimpleNamespace`
(60-90), `@dataclass` (91-110), `NamedTuple` (111-169). Each has its own
listing and teaching point (readable repr/equality; mutable typed record;
immutable typed record), and the split a reader wants — mutable vs.
immutable typed records — falls mid-section, not at a heading. Splitting
into "SimpleNamespace" and "Typed Records" (or three headings) would let
a reader jump straight to the comparison they need.

## Chapter 23 (Iterators): 4 findings

### [missing] Chapters/23_Patterns--Iterators.md:164 — the chapter's central memory claim for generators is never measured
"Generators are lazy... so it works on streams too large to hold in memory" (164-167) is the whole
motivation for preferring a generator over a list, yet no listing measures it. `tee.py` later
(291-321) goes to the trouble of `tracemalloc`-instrumenting a *cost* comparison (tee buffer vs.
list), so the tooling is already in the chapter's toolkit and unused for its own founding claim.
I measured it: `sum(squares_gen(1_000_000))` peaks at 436 bytes traced vs. 40,447,208 bytes for
the equivalent list (ratio ~92,769x). A short `tracemalloc` block placed right after line 167,
mirroring `tee.py`'s style, would turn the chapter's opening promise into evidence instead of
assertion.

### [does-not-work] Chapters/23_Patterns--Iterators.md:584 — `TypedIterator` never demonstrates the reason to choose it
Line 584 says "Use the class when the wrapper needs its own state or extra methods. Use the
generator when it does not," but `typed_iterator.py` (531-549) gives `TypedIterator` no state or
method beyond `imp`/`expected`, exactly what `typed()` closes over too (566-577). The two listings
differ only in which container type each accepts (`Iterator[object]` vs. `Iterable[object]`,
explained 588-593), which is a real distinction but not the one line 584 asserts. A reader who
wants to know when to reach for the class form sees no example that needs it: e.g. a
`rejected_count` field or a `retry()` method would cash out the claim; as written the class looks
strictly worse (more lines, same capability).

### [missing] Chapters/23_Patterns--Iterators.md:330 — `tee`'s actual payoff case is never shown, only assigned as an exercise
"Use `tee` when two consumers advance together, not when one finishes before the other starts"
(330-331) states tee's good case, but every run in `tee.py` (298-321) drains one branch to
completion before touching the other — the worst case for tee, which the chapter itself measures
at parity with a plain list (line 320's `True`). The lockstep case that would justify tee's
existence is pushed entirely into exercise 5 (803-806, "consume both branches in lockstep... predict
what happens to `buffered`"). Within the chapter body, tee is demonstrated only losing to the
alternative it's introduced to beat.

### [could-be-better] Chapters/23_Patterns--Iterators.md:421 — names four itertools functions, demonstrates two, with no pointer to where the rest live
"the generic iterator algorithms `chain()`, `islice()`, `groupby()`, `takewhile()`, and more" (421-422)
sets up `reusable_algorithms.py`, which only exercises `islice()` and `takewhile()` (430-443).
`chain()` and `groupby()` do get real treatment later, in `41_Functional--Toolkits.md` (`groupby`'s
sorted-input trap is even a named subsection there), so the omission is defensible — but nothing in
chapter 23 says so. Every other forward-looking claim in this chapter links to where the fuller
treatment lives (Generators, Concurrency, Effect Management); this is the one bare promise with no
such link, leaving an expert reader who checks `itertools` docs wondering why half the named list
never appears.

## Chapter 24 (Singleton): 5 findings

### [missing] Chapters/24_Patterns--Singleton.md:98 — the cached-factory footgun (arguments defeat it) is never named
Line 98 says a *zero-argument* constructor function is what makes `@cache`
turn a factory into a singleton, but never states the converse as a
warning: give the factory function even one parameter and `@cache` keys
on the arguments, silently producing one "singleton" per distinct
argument value. Confirmed: `settings("prod") is settings("dev")` is
`False` for `@cache def settings(env="prod"): return Settings()`. The
section otherwise catalogs subtle failure modes in detail (races, lock
placement, cache-clearing for tests) but skips the one a reader is most
likely to hit the moment they need a configurable factory. Fix: one
sentence stating that any parameter breaks the guarantee, since each
distinct argument tuple gets its own cache entry and its own instance.

### [missing] Chapters/24_Patterns--Singleton.md:171 — classic forms' test-isolation gap is named, never resolved
Note 1 states plainly: "The cached factory has an escape hatch the
classic forms lack." True, and left there — no fixture pattern, no
`monkeypatch`, no manual reset shown for `OnlyOne.instance`,
`SingletonClassVar.__instance`, `Borg._shared_state`, or the decorator's
`self.instance`. `test_singleton_borg.py` and `test_singleton_class.py`
each define at most one test that touches shared state, so neither test
file ever exercises the leak the prose warns about. "Which Should You
Use?" (line 654) still recommends Borg for real code without returning
to this gap. Fix: show one reset idiom (e.g., a pytest fixture that
clears `_shared_state`) for at least the form the chapter recommends.

### [missing] Chapters/24_Patterns--Singleton.md:293 — double-checked locking dismissed with an undemonstrated claim
"Double-checked locking works, but it asks the reader to reason about
what a free-threaded interpreter may reorder" is the only unproven
assertion in a section that otherwise proves every concurrency claim by
running code (`singleton_cached_race.py` shows the race;
`singleton_locked_settings.py` shows the fix). No listing shows the
reordering hazard, and chapter 19's own free-threading section
(`19_Techniques--Concurrency.md:1248`) never discusses memory-ordering
or reordering either, so the claim has no supporting example anywhere in
the book. Fix: either show the failure (a free-threaded repro, even if
unrun like the speedup number at ch19:1261) or cut the claim down to
what's demonstrated.

### [better] Chapters/24_Patterns--Singleton.md:88 — the stated goal is falsified one subsection later, uncorrected
"The goal is that every construction returns the same object" is stated
as the cached factory's payoff, but lines 122-165 ("Nothing Keeps the
Class Private") show that `Settings()` called directly bypasses the
cache entirely — the *factory function* returns one object, but
"every construction" does not. The chapter never walks the line-88
claim back to the weaker, actual guarantee ("every call to `settings()`
returns the same object"). A hostile reader has the rug pulled out from
under a promise made 30 lines earlier. Fix: soften line 88, or add one
clause there flagging that direct construction of the class is exempt.

### [better] Chapters/24_Patterns--Singleton.md:654 — Borg's advantage over "just use a module" is asserted, not argued
"If you really want many handles sharing one set of state, use Borg" is
the entire justification. But the module solution from the chapter's
own opening section already gives every importer a shared, mutable
namespace with no class at all — the case for choosing Borg's "many
objects, one `__dict__`" over that is never made (e.g., needing
instances that satisfy an existing class-based interface, support
`isinstance`, or get subclassed). Without that argument, a reader who
just finished being told "for almost everything, use a module" (line
649) has no reason to reach for Borg at all. Fix: name the concrete
situation (interface/polymorphism, not just data sharing) where Borg
earns its keep over a module.

## Chapter 25 (Template Method): 4 findings

### [does-not-work] Chapters/25_Patterns--Template_Method.md:313 — the interpreter guard never actually blocks an overridden `run()`
The chapter claims (lines 72-73 and 313-315) the `__init_subclass__()` technique "refuses ... whether the subclass overrides `run()` or misspells a hook." But `near_miss.py`'s check only fires on near-misses: an exact name match, including `run`, hits `if name in hooks: continue` and is skipped. Verified by running:
```
class BadOverride(ApplicationFramework):
    def run(self) -> None: print("hijacked")
BadOverride().run()
```
prints `hijacked` with no `TypeError` — `uv run python` against a script importing `near_miss.ApplicationFramework`. Fix: add an explicit `if name == "run": raise TypeError(...)`, the check line 73 already promises but the code never implements.

### [missing] Chapters/25_Patterns--Template_Method.md:145 — near-miss detection has false positives the chapter never mentions
The text shows `report()` passing as "an ordinary new method," implying any sufficiently distinct name is safe from the typo check. But `get_close_matches`'s heuristic also rejects legitimate methods that merely share letters with a hook name. Verified: adding `def customized_report(self) -> None: ...` to a subclass raises `TypeError: Weird.customized_report: did you mean customize2?`, though it is not a typo. The chapter never states this trade-off, a real helper method can be blocked by this mechanism, which a reader adopting the pattern needs to know before shipping it.

### [missing] Chapters/25_Patterns--Template_Method.md:286 — the function form's stated disadvantage is never demonstrated
Prose says "the function form must give each parameter a default of its own," implying an asymmetry with the subclass hooks' free `...` default, but `template_function.py` never shows the failure this describes. Running `run_framework(lambda: print("one"))` (omitting `customize2`) raises `TypeError: run_framework() missing 1 required positional argument: 'customize2'`, exactly the point being made, yet the listing never runs this case, so a reader never sees the asymmetry, only the assertion.

### [better] Chapters/25_Patterns--Template_Method.md:238 — Substitutability has no code, so the chapter's central risk stays abstract
"Substitutability" describes overrides that "raise an exception where the base would not" or "leave a step empty when the flow depends on it," but shows no listing, leaving the failure to the reader's imagination. Exercise 4 asks the reader to build exactly this case, so the concept's only concrete form is optional homework; a reader who skips exercises never sees it happen. A short runnable counterexample in the body, mirroring `near_miss.py`'s pattern, would land the LSP violation before the exercises rather than only within them.

## Chapter 26 (Surrogate): 4 findings

### [does-not-work] Chapters/26_Patterns--Surrogate.md:413 — "checks with `hasattr()`" claim is falsified by the chapter's own protection proxy
Lines 413-414 claim "Code that calls the method, or checks with `hasattr()`, works on a surrogate," offered as the reliable alternative to the broken `isinstance()` check just demonstrated. But `protection_proxy.py` (lines 493-496, earlier in this chapter) raises `PermissionError` from `__getattr__()` instead of `AttributeError`. Running `hasattr(guest, "erase")` against that exact class does not return `False`, it propagates `PermissionError: erase`, since `hasattr()` only swallows `AttributeError`. Confirmed by extracting `Guarded`/`Document` and calling `hasattr(guest, "erase")`: raises `PermissionError`. Fix: qualify the claim, or note that a surrogate raising anything but `AttributeError` from `__getattr__()` breaks `hasattr()` too.

### [missing] Chapters/26_Patterns--Surrogate.md:469 — "Virtual proxy" is named, claimed, and then pushed entirely into an unweighted exercise
Line 469 lists *Virtual proxy* (lazy initialization) as one of four canonical Proxy uses; line 576 asserts "the same few lines serve lazy initialization ... over any object"; but no listing ever builds one. *Protection* and *Smart reference* both get worked, tested code. *Virtual* proxy, arguably the most common real-world use of Proxy in Python (lazy-loaded attributes, deferred expensive construction), is left as Exercise 1 ("Create an example of the virtual proxy") with no guidance, no test, and no worked model to check against, unlike every other exercise here. The chapter's centerpiece claim about this use case is unexercised in the body. Fix: add a short worked lazy-init proxy alongside `protection_proxy.py` and `counting_proxy.py`.

### [missing] Chapters/26_Patterns--Surrogate.md:609 — State's `change_to()` swap is never flagged as unsafe under concurrent calls
The State section (609-720) presents `change_to()` as a plain attribute swap with no caveat about calling it while another thread is mid-call through the same surrogate — exactly the situation a connection-pool or request-handler State object would face. The book covers concurrency at length elsewhere, so an expert reader will ask this immediately, and nothing here answers it (not even a forward pointer). Fix: one sentence noting the swap is not safe under concurrent access, with a pointer to a synchronization mechanism (or to the State Machine chapter if it's handled there).

### [missing] Chapters/26_Patterns--Surrogate.md:156 — stdlib's own `weakref.proxy()` is never connected to a chapter about proxies
The "Forwarding with `__getattr__()`" section (156) and "What Proxy Solves" (463-477) survey real uses of proxying but never mention `weakref.proxy()`, the standard library's own transparent forwarding wrapper (literally named "proxy"), which chapter 10 (Cleanup) already uses `weakref.ref`/`WeakValueDictionary` from the same module without ever calling out `proxy()`. An expert reader who knows the stdlib will wonder why the chapter's hand-rolled `__getattr__()` proxy is never related to it. Fix: one sentence tying `weakref.proxy()` to the pattern, even just to note it solves a different problem (breaking reference cycles) with the same mechanism.

## Chapter 27 (Factory): 4 findings

### [missing] Chapters/27_Patterns--Factory.md:3 — motivating problem is asserted, never dramatized
The opening argues the pain factories solve: "the code that creates objects is distributed throughout your application, adding a type means finding and editing every place that names a concrete type" (line 11-12). No listing ever shows that "before" state — multiple call sites each naming `Circle()`/`Square()` directly, then edited one-by-one to add a type. `shape_factory1.py` (line 34) jumps straight to a single-call-site factory that already works. The reader is told what the alternative would have cost but never made to feel it. Fix: a short "naive" snippet with 2-3 scattered constructor calls, shown once, that the rest of the section replaces.

### [missing] Chapters/27_Patterns--Factory.md:781 — the one bug the chapter narrates in prose is the one thing left untested
Lines 781-792 describe a real defect in `PizzaBuilder`: `build()` doesn't clear `_toppings`, so a second `build()` on the same instance silently returns a pizza carrying the first one's toppings. I confirmed this by importing `pizza_builder` and calling `build()` twice (`basil` then `basil, olives`). Every other claimed behavior in this chapter (registration, prototype independence, shallow-copy aliasing) gets a `print()` or a `pytest` test proving it; this one, despite three paragraphs of explanation, gets neither in `test_pizza.py`. A `test_second_build_reuses_toppings` alongside the existing tests would make the hazard concrete instead of asserted.

### [missing] Chapters/27_Patterns--Factory.md:287 — the chapter demonstrates static-typing beats runtime errors, then never applies it to its own string-keyed factories
`test_unknown_name_raises` (line 287-289) treats `KeyError` from `make("Hexagon")` as the correct, accepted outcome. Later, `games2.py` makes exactly the opposite case: a Protocol lets the type checker "report the omission before the program runs" (line 594), earlier than a runtime error. That lesson is never carried back: `SHAPES`/`FACTORIES`/`Shape.registry` all key on plain `str`. I confirmed `Kind = Literal["Circle", "Square"]` on `make()`'s parameter makes `ty` reject `make("Hexagon")` at check time (`error[invalid-argument-type]`) instead of at `pytest.raises(KeyError)` time — a real option the chapter's own later argument recommends but never mentions for its earlier, still-live examples.

### [better] Chapters/27_Patterns--Factory.md:404 — true Factory Method is never shown standalone, only embedded inside Abstract Factory
Line 93-96 explicitly says `shape_factory1.py`'s static method is not the GoF pattern ("the smallest version of that idea"), and defers the real subclass-override form to "Abstract Factories." That section (line 404) never isolates it: `GameElementFactory.make_character()` appears only bundled with `make_obstacle()` inside the two-parallel-hierarchy Abstract Factory example. A reader never sees the minimal case — one hierarchy, one overridden creation method — separately from the matched-pair complexity Abstract Factory adds on top, making it harder to tell which part of `GameElementFactory` is "Factory Method" and which part is "Abstract Factory."

## Chapter 28 (Function Objects): 4 findings

### [does-not-work] Chapters/28_Patterns--Function_Objects.md:19 — Strategy's "classic class-based form" is promised but never shown
The intro states: "*Command* appears first as a function, then as the
classic class-based form, a contrast that holds for *Strategy* as
well" (line 19-20), setting up a code/code contrast like Command's
`command.py` vs `command_pattern.py`. But the Strategy section only
*describes* the classic form in prose (line 285-291: "Each algorithm
becomes a class deriving from a `FindRoot` interface... five classes
to produce the same three lines"). No `strategy_pattern.py`-equivalent
listing exists anywhere in `build/examples/28_Patterns--Function_Objects/`
(checked directory listing). The reader is told two forms will
contrast, and only sees one. Fix: either add the class-based listing,
or correct the intro's promise.

### [missing] Chapters/28_Patterns--Function_Objects.md:103 — Bound method, the second rung of the ladder, is never demonstrated in code
Lines 103-107 introduce the bound method as "a ready-made command"
that "a command list can hold ... alongside plain functions," and the
closing ladder (line 603) repeats it as option 2 of 5. Every other
rung has a runnable listing (`command.py`/`strategy.py`,
`configured_strategy.py`, `callable_command.py`, `command_pattern.py`),
but `account`/`account.deposit` is never defined or run anywhere in
the chapter. A reader cannot see a bound method sitting in the same
list as a plain function, the exact claim being made. Fix: add a short
listing mixing a bound method into `macro`.

### [missing] Chapters/28_Patterns--Function_Objects.md:336 — `functools.partial`-for-configuration and `Placeholder` are described but never coded
Lines 336-344 describe binding a trailing setting with `partial` and
introduce `Placeholder` for a positional-only parameter, both new
mechanisms in this chapter, entirely in prose, with a forward link to
Functional Foundations and zero listing. Every other configuration
technique in the section (`bisection_within`'s closure) gets a working
example (`configured_strategy.py`, verified: `uv run python
configured_strategy.py` -> `1.406250 1.414214`, matches the `#:`
markers). `Placeholder` is unfamiliar enough that a reader is asked to
trust an unillustrated mechanism. Fix: add a two-line `partial(...,
tolerance=...)` example alongside the closure one.

### [better] Chapters/28_Patterns--Function_Objects.md:578 — `test_no_handler_is_a_noop` checks two unrelated things in one test
```python
def test_no_handler_is_a_noop() -> None:
    bus = EventBus()
    bus.publish(Closed("done"))  # Must not raise
    # publish() reads with .get(): no stray entry appears
    assert Closed not in bus._handlers
```
This asserts an implementation detail (`bus._handlers`, a private
attribute) in the same test as the no-raise behavior, violating the
book's own stated rule in `.claude/skills/thinking-in-python/SKILL.md`
("One behavior per test; a test with two unrelated assertions hides
which one actually failed"). It also breaks encapsulation to test a
performance/hygiene detail rather than observable behavior. Fix: split
into two tests, or test hygiene through a public observation (e.g. a
second `publish` and confirming no extra handler runs).

## Chapter 29 (Changing the Interface): 5 findings

### [does-not-work] Chapters/29_Patterns--Changing_the_Interface.md:236 — Façade's motivating problem is asserted, never shown
Façade exists to hide "a confusing collection of classes and interactions" (line 221). `facade.py` has one trivial frozen dataclass and the comment `# Other classes that aren't exposed by the facade go here ...` (line 236) standing in for the actual mess. The reader never sees a collection worth hiding, so the listing demonstrates the mechanics of a static-method wrapper but not the reason anyone would reach for it. Contrast with `checkout.py` two sections later, which does hide three real classes. Fix: give `facade.py` two or three cooperating classes (even toy ones) so "confusing" has a referent before the module version supersedes it.

### [missing] Chapters/29_Patterns--Changing_the_Interface.md:16 — Adapter never gets a real-world motivating scenario
`WhatIHave`/`WhatIWant`/`WhatIUse` (lines 16-51) stay pure vocabulary through the whole Adapter section and into `getattr_adapter.py`; no listing says what real mismatch this stands for (a third-party library's method names, a legacy format, etc.). Façade, two sections later, gets `checkout.py`'s tax/discount engine as a concrete case. The only pointer to a real adapter is a cross-link to chapter 20's `PairCoord` (line 175), which this chapter doesn't show. An expert reader finishes Adapter knowing the shape but not a single situation where reaching for it beats just calling `g()`/`h()` directly.

### [missing] Chapters/29_Patterns--Changing_the_Interface.md:120 — The type-checker rejection behind the `Any` workaround is never demonstrated
Lines 118-124 assert that annotating `WhatIUse2.op()`'s parameter as `WhatIWant` (matching the base) makes `ty` report `invalid-method-override`, and that's why the listing uses `Any` instead. No listing shows this failure; the reader takes it on faith. I verified the claim is true (`uv run ty check` on a precisely-annotated variant does report `invalid-method-override`), but the chapter's own demonstration proves less than the four paragraphs built on it: the reader never sees the error the whole `Any` justification depends on.

### [missing] Chapters/29_Patterns--Changing_the_Interface.md:300 — No "when not to use Façade"
The chapter closes the Façade section with "A façade is an agreement about which names to call, not a lock on the rest" (line 300), which hints at a real limitation but never states it: a façade that hides names an advanced caller legitimately needs forces that caller to reach past the underscore convention anyway, or forces the façade's author to keep widening it. Every other technique in the chapter (the recursion trap, special-methods-bypass, Liskov violation in Approach 2) gets its failure mode spelled out; Façade alone gets none.

### [better] Chapters/29_Patterns--Changing_the_Interface.md:250 — The module façade example never scales past one file
"The cleaner Python façade is a module" (line 250) is demonstrated by `checkout.py`, three tiny dataclasses in a single module. GoF's Façade typically fronts a whole subsystem, several modules deep, which in Python usually means a package's `__init__.py` re-exporting a curated set of names from private submodules. That case (and the fact `__init__.py` is the idiomatic place to do it) is never mentioned, so the reader leaves with a façade recipe that looks like it stops working once the "confusing collection" outgrows one file.

## Chapter 30 (Observer): 5 findings

### [missing] Chapters/30_Patterns--Observer.md:378 — async unsubscribe-during-notification never demonstrated
The sync section earns its "list() copy" claim with a full runnable file,
`self_removing_observer.py` (line 248), whose `#:` output proves an observer
detaching mid-broadcast doesn't skip the next one. The async section makes
the same, trickier claim in prose only: "an observer that unsubscribes
mid-notification still hears this change" (line 381). Nothing exercises
this: `async_observers.py` never calls `unsubscribe()`, and there is no
`test_async_observers.py` in `build/examples/30_Patterns--Observer/`. A
reader takes the tuple-draining argument on faith where the sync version
let them watch it work. Fix: add an async counterpart to
`self_removing_observer.py`.

### [missing] Chapters/30_Patterns--Observer.md:393 — async exception/orphaned-task gotcha only described, never run
The prose says `gather()` re-raises the first exception immediately while
"the unfinished observers keep running with nobody awaiting them" (lines
393-395). I confirmed this is true (`uv run python` on a scratch
`gather(bad(), slow_ok())`: the exception surfaces at once, and `slow_ok`
still prints later, mid-`sleep`, after being silently orphaned). This is a
genuinely surprising async failure mode and exactly the kind of
counterexample the chapter needs to make it stick, but unlike the sync
section's dedicated demo file, it gets a paragraph and no listing. Fix: a
small runnable example (or fold into exercise 4) that raises from one
observer and prints the orphaned sibling finishing afterward.

### [better] Chapters/30_Patterns--Observer.md:407 — visual example's incidental complexity outweighs its Observer content
Lines 407-557 (~150 lines, over a quarter of the chapter) form the longest
section, but most of the code and prose teaches grid adjacency and
recoloring (`adjacent()`, `recolored()`, the flood-style logic covered by
`test_box_observer.py`), not Observer. The actual Observer content is the
same three lines already shown twice: subscribe, notify, copy-on-iterate.
An expert reader gets a grid-puzzle lesson wearing an Observer costume.
Fix: compress `recolored()`/`adjacent()` to a short description (or use a
simpler single-cell-recolor model) and spend the reclaimed length on the
undemonstrated async gotchas above.

### [missing] Chapters/30_Patterns--Observer.md:283 — re-entrant notify() gotcha stated, never shown breaking or fixed
"An observer that writes back to the observable re-enters `notify()` from
inside `notify()`," with two one-clause fixes ("conditional on the value
changing" / "a re-entry flag"), is two sentences with no listing (lines
283-287). This is a real, easy-to-hit bug in two-way bindings, which is the
chapter's own opening MVC framing (a view editing its model). Unlike
nearly every other gotcha in the chapter, this one gets no code at all, not
even a broken-then-fixed pair. Fix: a short runnable example showing the
infinite recursion, then one guard that stops it.

### [missing] Chapters/30_Patterns--Observer.md:167 — "asyncio events" named as an Observer alternative but isn't one
"Event-heavy programs have mature libraries (signal/slot systems, `asyncio`
events)" names an alternative without weighing it, and the analogy is
weak: `asyncio.Event` is a single set/clear/wait flag with no subscriber
list and no payload, so it doesn't do what this chapter's `Observable`
does (fan a value out to many independent callables). Pairing it with a
real pub-sub system like Qt's signal/slot suggests it is a drop-in
alternative when it solves a different problem. Fix: swap in a real async
pub-sub reference (e.g. a `Queue` per subscriber, or a library like
`blinker`), or cut the parenthetical.

## Chapter 31 (State Machines): 4 findings

### [does-not-work] Chapters/31_Patterns--State_Machines.md:379 — the "unexpected input" section proves nothing it claims
The section (379-395) says the two designs "answer differently": version 1
stays put and re-runs the current state's action, version 2 raises. Neither
behavior is ever shown running. I drove `mouse_trap.py`'s `next()` over every
line of `mouse_moves.txt` and logged whether each call matched an explicit
`case` or fell through to `case _`:
`uv run python -c "..."` over all 15 events -> every single one printed
`MOVE` (an explicit case), zero `STAY`. The input file was built so every
`case _` arm is dead code; `mouse_trap2.py`'s `RuntimeError` branch is
likewise never hit in the chapter (only a `pytest` for the *other* engine
covers `NoTransition`, at line 755). A reader is told about a behavior no
listing in the chapter ever produces. Fix: append one out-of-sequence event
to the demo, or add a two-line standalone snippet that triggers each path.

### [missing] Chapters/31_Patterns--State_Machines.md:397 — no real FSM library ever weighed
The chapter builds two state-machine engines from scratch and states its
reason for avoiding Java's `Condition`/`Transition` hierarchies (411-416:
"Python functions are first-class... those hierarchies vanish"), but never
mentions that mature Python FSM libraries exist (`transitions`,
`python-statemachine`) and offer guards, callbacks, and hierarchical states
for the price of a dependency. An expert reader building a real vending
machine will ask "why hand-roll this?" before reaching for `table_machine.py`.
One sentence in "Which Design Should You Use?" (854) naming the trade-off
(dependency vs. control, and that the homegrown design is what you reach for
when you can't take a dependency, or want to see the mechanism) would close
the gap.

### [missing] Chapters/31_Patterns--State_Machines.md:596 — row-priority-among-true-conditions is stated but never exercised
Lines 490-495 explain that rows are tried top to bottom and a later row can
be shadowed by an earlier one, which is the reason ordering matters. But the
vending machine's only two-condition group (596-602, `too_expensive` then
`sold_out`) never actually has both conditions true for the same event: I
traced the demo/tests and confirmed `sold_out` items are always priced at or
below the money inserted, so `too_expensive` never masks it. The one place
that could show why row order is a real design decision (not just a rule to
remember) instead shows two conditions that are always mutually exclusive in
practice. A slot priced above the inserted amount *and* sold out would make
the point concrete.

### [missing] Chapters/31_Patterns--State_Machines.md:854 — losing per-state entry actions is never named as a cost of the table design
Line 438 states "The states in this design do nothing. The table holds all
the behavior," moving from an entry-action-per-state model (`run()`) to a
transition-action-per-edge model. That is a real capability loss: if several
edges into the same state must share one action ("always chime on entering
COLLECTING"), the per-state design says it once in `run()`; the table design
must repeat it on every incoming row or add its own indirection. "Which
Design Should You Use?" (854-874) compares only readability and where a
state's transitions live, never this structural difference, so a reader
porting a real design between the two models has no warning.

## Chapter 32 (Multiple Dispatching): 7 findings

### [does-not-work] Chapters/32_Patterns--Multiple_Dispatching.md:165 — the double-dispatch centerpiece never shows why anyone would want it
All nine `eval_*()` methods in `paper_scissors_rock.py` ignore their `item`
argument; the prose concedes "This game ignores it, since the outcome depends
only on the two types." The chapter later states the two reasons to prefer this
version (line 317: "when it reads the object's own state, or when a subclass
should be able to override one combination and inherit the rest") and
demonstrates neither, while the table version is shown to be shorter, exactly
equivalent (both print the identical ten lines), and better typed. The reader
sees a mechanism plus a proof it is the wrong choice. Fix: give one `eval_*()`
a reason to read `item` (a damp `Paper` that loses to `Scissors` regardless), or
add a four-line subclass that overrides one combination and inherits the rest.

### [missing] Chapters/32_Patterns--Multiple_Dispatching.md:271 — "One Type or Many" never weighs `match` with class patterns
The section catalogs `singledispatch`, `singledispatchmethod`, and the
`isinstance()` ladder, but not `match (self, item): case (Paper(), Rock()): ...`,
which is the first thing a modern-Python reader will reach for on a two-type
decision. [Pattern Matching](13_Techniques--Pattern_Matching.md) teaches class
patterns and even contrasts them with dynamic binding, 19 chapters earlier, so
it is available. It also matches the way this chapter's `exact_match.py`
surprise wants: class patterns test with `isinstance`, so `Origami` would hit
the `Paper()` case that the table refuses. A paragraph placing `match` on the
same axis (exact vs. subclass-tolerant, closed vs. open) closes the gap.

### [better] Chapters/32_Patterns--Multiple_Dispatching.md:3 — the opening problem is not the problem the chapter solves
The chapter opens on `Number + Number` and declares at line 18 "The solution is
*Multiple Dispatching*", then spends 300 lines on a game whose shape is nothing
like operator overloading. The real answer to the opening question is
`__radd__()`, which arrives at line 385 and requires none of the `eval_*()` or
table machinery, and the expression system itself is handed off to chapter 34.
A reader who came for the opening problem learns four fifths of the way in that
Python already solved it. Fix: say up front that Python performs the second
dispatch itself for operators and that the game shows what you do when the
interaction is not an operator.

### [missing] Chapters/32_Patterns--Multiple_Dispatching.md:288 — `singledispatchmethod`, the stdlib's closest thing to double dispatch, gets no listing
Three paragraphs describe it as "the pair of dispatches the `eval_*()` family
hand-rolls" and end with a trap ("registering on a shared base gives every
subclass one dispatcher"). The trap is real: with `@Item.compete.register` for a
`Rock` argument on a base `Item`, both `Paper().compete(Rock())` and
`Rock().compete(Rock())` return the same answer, because `self`'s type never
enters the resolution. But nothing in the chapter lets the reader see this,
and the entry in Toolkits (ch. 41) is a two-class `Describer` that never touches
`self`-dispatch. A ten-line listing applying it to `Item` and showing the
collapse would be the chapter's most useful new example.

### [better] Chapters/32_Patterns--Multiple_Dispatching.md:490 — the closing synthesis calls the table a second dispatch, and it is not one
"The `eval_*()` family, the `OUTCOME` table, and `__add__()` with `__radd__()`
all take a type the first dispatch could not resolve and dispatch again on it."
The table version performs no dispatch at all: `compete()` is defined on `Item`
and no subclass overrides it, so `OUTCOME[type(self), type(item)]` is one lookup
on a pair of types with zero method resolution involved. Flattening the three
into "a second dispatch" erases the distinction the section exists to draw, and
it is the distinction that explains why the table alone scales to three or four
types. Fix: state that the table replaces both dispatches with a single lookup
keyed on the whole combination.

### [better] Chapters/32_Patterns--Multiple_Dispatching.md:75 — `duel()`'s `Any` is the case `Protocol` exists for
"`duel()` settles for `Any` because the two versions below define separate
`Item` hierarchies, and this file must serve both." Structural typing across
unrelated hierarchies is precisely a `Protocol`, taught in
[Static Types](08_Foundations--Static_Types.md). A two-member protocol in
`arena.py` (`compete(self, item: Any) -> Outcome` and `__str__`) types `duel()`
for both versions; I checked a probe of both class shapes with
`uv run ty check`, which reported "All checks passed!". The chapter mentions
`Protocol` only at line 173, and only for the four-method internal case, so a
reader is left thinking `Any` was forced. Fix: use the protocol in `arena.py`,
or say why a demonstration file declines it.

### [better] Chapters/32_Patterns--Multiple_Dispatching.md:548 — exercise 9 asks for something the chapter already built
"Can you keep the syntactic simplicity of the dispatch while using a table
underneath?" is what `paper_scissors_rock_table.py` already is: the call site
stays `item1.compete(item2)`, and the table sits inside `Item.compete()`. The
first half of the exercise ("When is the table lookup more appropriate?") is
also answered directly by "One Type or Many" at lines 300-318. As written the
exercise asks the reader to rediscover the listing on the facing page. Fix:
point it at something the chapter did not do, such as keeping the `compete()`
call site while making the table hold callables rather than `Outcome` values
(the possibility raised, and never exercised, at line 315).

## Chapter 33 (Visitor): 3 findings

### [does-not-work] Chapters/33_Patterns--Visitor.md:16 — the flagship example never adds an operation to an unchangeable hierarchy
Lines 16-18 promise the classic pattern "requires one method on the primary
class hierarchy, typically called `accept()`" — implying that's the one
hierarchy edit, ever. But `Flower` already defines `pollinate()` and `eat()`
natively (lines 34-37) before any Visitor code runs, and the chapter later
admits (172-179) that in Python every *new* operation also needs its own
method on `Flower`: "the primary hierarchy ends up carrying the operations
the pattern exists to keep out of it." So the demo never actually walks
through adding an operation to a hierarchy you can't touch — it dispatches
among bugs over operations that were already there. Fix: either add a third
operation live to show the hidden cost, or soften the line-16 claim up
front.

### [could-be-better] Chapters/33_Patterns--Visitor.md:21 — "each Visitor subclass is a new operation" doesn't match the 3-level hierarchy that follows
The listing builds `Bug -> Pollinator/Predator -> Bee/Fly/Worm`, where only
the middle layer defines an operation; `Bee` and `Fly` are both
`Pollinator`s and share one operation, not two. That's a reasonable design
(it avoids duplicating `visit()` bodies), but it contradicts the general
claim just made in prose, and nothing in prose reconciles it — only a code
comment ("# The middle layer names the operation," line 59) marks the
distinction. A reader who takes line 21 literally expects each leaf visitor
to be its own operation, and the listing quietly isn't built that way.

### [missing] Chapters/33_Patterns--Visitor.md:343 — the stated reason to still use Visitor is asserted, never shown
"*Visitor* still has a place: when the elements must drive the traversal
themselves from inside `accept()`" is the chapter's own case for keeping the
classic pattern at all, but no `accept()` in this chapter does that —
`flower_gen()` enumerates flowers externally, and `accept()` only forwards
to `visit()`. The one scenario offered for why `singledispatch` isn't a full
replacement is never demonstrated or even sketched, so the reader can't
check it against the taught material. A minimal recursive `accept()` (even
two lines) would let the claim be verified rather than taken on faith.

## Chapter 34 (Composite and Interpreter): 8 findings

### [does-not-work] Chapters/34_Patterns--Composite_and_Interpreter.md:308 — "overload all the ... comparison operators" is false for this design, and the chapter depends on that
"You can overload all the arithmetic, bitwise, and comparison operators, so an expression written with them builds nodes instead of computing." Not `==`. `@dataclass(frozen=True)` generates `__eq__` on every node class, shadowing anything on `Operators`:
`uv run python -c "...class Ops: __eq__ -> ('Eq',...); @dataclass(frozen=True) class Num(Ops)..."` prints `False`, not a tuple. Building an `Eq` node needs `eq=False` on all four nodes, which destroys the structural comparison the chapter relies on at line 348 and in eight test assertions. This is the exact friction SQLAlchemy and Polars live with (`col == 5`), and the sentence promises it works. Fix: qualify the sentence and add a paragraph on the `==` conflict.

### [missing] Chapters/34_Patterns--Composite_and_Interpreter.md:484 — the simplify demo writes `(Num(2) + 3)` to dodge a trap the chapter never names
`messy = 1 * x + 0 * Var("y") + (Num(2) + 3) * x`. Every expert reader asks why not `2 + 3`. Answer, run: with `(2 + 3)` the *unsimplified* rendering is already `(((1 * x) + (0 * y)) + (5 * x))` — Python computed 5 before any node existed, so the constant-folding rule this section exists to teach never fires. This is the defining limit of borrowing the host parser: an operation builds a node only when one operand is already one. Nothing in the chapter says so, and the listing's `Num(2)` looks like arbitrary noise. Fix: one sentence near line 289 or in the simplify commentary.

### [does-not-work] Chapters/34_Patterns--Composite_and_Interpreter.md:581 — the section titled "A Template Is a Tree" walks something it declares not a tree, and the real nesting case breaks
"The grammar is flat rather than nested, so the walk is a loop instead of a recursion." It nests: an interpolation value can be a `Template`. Run: `to_query(t"SELECT * FROM t WHERE {t'name={\"bob\"}'}")` returns `('SELECT * FROM t WHERE ?', [Template(strings=('name=', ''), ...)])` — a `Template` object bound as a SQL parameter, which no driver accepts. So the one section where the chapter claims Python ships its own composite uses a non-recursive walker and silently mishandles the composite case. Fix: three lines recursing into a nested `Template` in `to_query()`; the section then earns its title and shows the recursion in Python's own type.

### [missing] Chapters/34_Patterns--Composite_and_Interpreter.md:217 — "Python removes both costs" hides that the sentences must be Python source
Line 215-219 says Interpreter is heavy elsewhere because you need a class per construct and a parser, then: "Python removes both costs." The parser cost is not removed, it is avoided by restricting the language to expressions a Python programmer types into your source with operands that are already nodes. Line 307's limits paragraph covers only `and`/`or`/`not`. GoF Interpreter's usual motivation — a rules file, a config value, a query typed by a user — is unreachable here, and the chapter never says so or points at where a real parser would go. Fix: a "when this technique does not apply" sentence in that paragraph.

### [missing] Chapters/34_Patterns--Composite_and_Interpreter.md:148 — the exhaustiveness payoff, the whole justification for the union, is asserted and never shown
Lines 148-153 claim that adding `Symlink` makes "every function whose `case _` calls `assert_never()`" fail type checking, with the type checker naming each one. This is the chapter's central argument for a union over a base class, and the reader sees no diagnostic. The book quotes `ty` errors elsewhere (`grep -rn "error\[" Chapters/ Solutions/`), so the house style permits it. Exercise 2 pushes the demonstration onto the reader, which means anyone who skips exercises takes the load-bearing claim on faith. Fix: add the `Symlink` line and quote the two-line `ty` error inline.

### [better] Chapters/34_Patterns--Composite_and_Interpreter.md:22 — the classic/data-class comparison changes four variables at once
`filesystem_classic.py` differs from `filesystem.py` in ABC-with-methods vs. functions, hand-written `__init__` vs. `@dataclass`, varargs vs. tuple, and rebindable vs. frozen. Line 142 then attributes the improvement to one of them: "What changed is where operations live." Three of the four differences are free to the classic version — it could be a frozen dataclass hierarchy with `size()` methods and lose nothing — so the comparison overstates the case and lets a skeptical reader dismiss it as boilerplate accounting. Fix: write the classic version as frozen dataclasses with methods, isolating the variable the chapter is actually arguing about.

### [better] Chapters/34_Patterns--Composite_and_Interpreter.md:74 — "A Composite of Data Classes" re-derives chapter 20 instead of teaching what is new here
Lines 141-153 and 199-205 restate [Rethinking Objects](20_Patterns--Rethinking_Objects.md#polymorphism-without-inheritance) at nearly the same depth: frozen dataclasses, a union, `assert_never()`'s payoff, add-a-type vs. add-an-operation, closed vs. open sets. What is genuinely new is the self-reference — `Directory` holds `tuple[Node, ...]`, so the union is recursive — and it gets three lines (131-139). The section also never names the expression problem, which chapters 13, 20, and 37 all name, leaving the reader without the term for the trade being described. Fix: compress the recap, expand the recursion, name and link the trade.

### [better] Chapters/34_Patterns--Composite_and_Interpreter.md:329 — the `**env` environment costs a paragraph, a test, and a dict rebuild per node, and buys ergonomics only
`def evaluate(e: Expr, /, **env: int) -> int` forces `evaluate(left, **env)`, building a fresh dict at every recursive call, which is O(depth x |env|) on the exact structure the closing section says can get thousands of levels deep (line 563). It also creates the name collision that lines 364-366 and `test_e_is_available_as_a_variable` exist solely to patch. A `dict[str, int]` parameter passes by reference and needs neither the `/` nor the explanation. Fix: either use a dict, or say plainly that the kwargs form is an ergonomic choice with these two costs.

## Chapter 35 (Flyweight): 4 findings

### [missing] Chapters/35_Patterns--Flyweight.md:457 — decision guide hides that its own branches combine
"Which Pool Should You Use?" reads as an if/elif/else chain: known values → `Enum`,
else need `C(...)` syntax → `__new__` interning, else unbounded growth →
`WeakValueDictionary`, else `@cache`. But Exercise 5 (line 498) has the reader
rewrite `interned_color.py` (chosen for constructor syntax) to also use the
weak-pool technique — combining two "branches" the guide presents as
alternatives. The three questions (syntax? boundedness? known at compile
time?) are orthogonal, not mutually exclusive, so a reader who needs
constructor syntax *and* leak-safety is left unserved by the guide and only
discovers the combination exists by doing the exercise. Fix: present the
axes as independent questions, or say explicitly that `__new__` interning and
weak references compose.

### [missing] Chapters/35_Patterns--Flyweight.md:286 — the tile()-vs-Color() guarantee is asserted, never run
Lines 286-292 claim `Tile("~", "water", False)` "bypasses" `tile()`, building
an object "equal to the pooled water tile" but not the same one, while
`Color(...)` guarantees `is`. Confirmed true by running it directly
(`Tile("~","water",False) == tile("~")` is `True`, `is` is `False`), but
neither `test_tile_map.py` nor the chapter's listings ever show this pair.
Every other claim in the chapter is backed by a printed `#:` result; this is
the one load-bearing claim a reader must take on faith. Fix: add
`assert Tile("~", "water", False) is not tile("~")` (and `==`) to
`test_tile_map.py`.

### [better] Chapters/35_Patterns--Flyweight.md:158 — "Typing the Symbol Set" is a static-typing digression, not a Flyweight lesson
The ~19-line section (158-177) re-teaches type-narrowing-through-a-guard
versus `cast()`, already covered in [Static Types](08_Foundations--Static_Types.md#typing-decorators-and-directives).
It's tied to `to_symbol()`, but the payoff is about the type checker, not
about sharing objects — nothing here advances intrinsic/extrinsic state or
pooling, the chapter's actual subject. It sits between the tile pool listing
and the "freezing hides sharing" payoff (198), interrupting that line of
argument. Fix: compress to a sentence plus the existing cross-reference, and
move the freezing discussion to follow the tile listing directly.

### [missing] Chapters/35_Patterns--Flyweight.md:450 — "exhaustive match" is claimed for the Enum but never shown, here or at its cross-reference
Line 450 lists "exhaustive `match`" as a benefit `tile_enum.py` "brings," but
no listing matches on `Tile` at all. The chapter points to
[State Machines](31_Patterns--State_Machines.md#table-driven-state-machine)
(454) for "the same property," but every `match` there (checked: lines
157-201) ends in a `case _:` wildcard, which is exhaustive by catch-all, not
by the type checker verifying every member is covered. The specific claim —
that a type checker flags a forgotten `Tile` member — is asserted nowhere and
demonstrated nowhere in the book. Fix: either drop the claim or add a `match`
with no wildcard and show `ty` accepting it (or rejecting it when a member is
missing).

## Chapter 36 (Memento): 5 findings

### [missing] Chapters/36_Patterns--Memento.md:272 — the caretaker never serves the classic Memento, and the pivot into it misstates the pattern

"With states as immutable values, the caretaker no longer needs to know anything about them" implies the classic caretaker needed to. It never did: opacity is the pattern's whole selling point, and `History[S]` works unchanged on the frozen `Memento` from `sketch.py`. From `build/examples/36_Patterns--Memento`, `uv run python -c "from sketch import Sketch; from history import History; s=Sketch(); h=History(s.save()); s.draw('circle'); h.do(s.save()); s.draw('beak'); h.do(s.save()); s.restore(h.undo()); print(s)"` prints `circle`. So lines 248-254, which argue the classic form survives for large states and states you do not own, leave exactly those readers with a bare `checkpoint` local and no undo stack. Fix: three lines showing `History[Memento]` driving the mutable originator.

### [does-not-work] Chapters/36_Patterns--Memento.md:234 — "snapshots stay cheap" is undercut by the chapter's own running example

`(*self.strokes, stroke)` is O(n), so k edits held in a `History` cost O(k^2) pointers. Measured in `build/examples/36_Patterns--Memento` with `uv run python -c` building a 2000-edit history of one-character strokes: `states: 2001 total tuple bytes: 16104048`, against `one final tuple bytes: 16048` — a thousandfold. The hedge at 234-235 ("a state whose changed field is large pays for that field on every edit") reads as a different, hypothetical case, but `strokes` becomes that field by accretion. It is also the basis for "Try snapshot-based undo first, because immutable states make snapshots inexpensive" (381-382) and for the Command dismissal. Fix: state the per-edit and per-history costs, and name the escapes (bounded depth, coalesced edits, a persistent structure, or Command).

### [does-not-work] Chapters/36_Patterns--Memento.md:44 — the deepcopy half of `nested_mutation.py` shows neither a difference nor a cost

`uv run python nested_mutation.py` prints `[['eggs', 'milk', 'cheese'], ['bread']]` twice. `todo` is never printed, so nothing on screen distinguishes the deep copy from the shallow one; the reader must carry `todo`'s state in their head to see that `deep` lacks `"jam"`. Worse, line 78 sends the reader back for "the cost the previous section showed," and the section shows no cost: it shows mechanism ("walks the whole structure and rebuilds every nested container"), with no size, no timing, and no cycle or `__deepcopy__` caveat. Fix: print `todo` beside `deep`, and either state deepcopy's cost in that section or drop the backreference.

### [missing] Chapters/36_Patterns--Memento.md:126 — the Memento-class-versus-alias argument is thirteen lines of assertion, in a chapter that demonstrates everything else

Lines 126-138 weigh `type Memento = ...`, `NewType`, and the one-field data class entirely in prose, with no listing. The claim at 135-136 also over-reaches: "The only way to see the strokes is through `.strokes`, so reaching inside becomes visible in the code." A caretaker can still read `checkpoint.strokes[0]`, unpack it, and forge `Memento(("fake",))` — the same three liberties the passage holds against `NewType`. The genuine gains are the runtime type and the `FrozenInstanceError` on reassignment. Fix: a short listing where a caretaker parameter typed `tuple[str, ...]` swallows an unrelated tuple while the `Memento` version rejects it, plus the reassignment that fails.

### [better] Chapters/36_Patterns--Memento.md:331 — `History` names a hazard it could design away

"Every change must go through `do()`. Build a new state from `history.present` and keep it without handing it back, and the history omits it." The chapter then repeats the hazardous idiom at every call site: `history.do(history.present.draw("circle"))` at 317-318, and four times in `partial_restore.py` (401-405, 408). One method closes the hole: `def apply(self, edit: Callable[[S], S]) -> S: self.do(edit(self.present))`, called as `history.apply(lambda d: d.draw("circle"))`. Since the section's argument is that immutable states let the caretaker be fully generic, the generic edit operation is the natural place to land it. Fix: add `apply()`, or state why the explicit two-step reads better.

## Chapter 37 (Pattern Refactoring): 7 findings

### [does-not-work] Chapters/37_Patterns--Pattern_Refactoring.md:359 — the dictionary sorter is never shown fixing the failure it exists to fix
`plastic_dropped.py` ends on "parsed 4, binned 2" (line 337), the chapter's one piece of hard evidence. `recycle_dict.py` then runs on `trash.dat`, which contains no plastic, so its output is byte-identical to the flawed `recycle_rtti.py`:

    cd build/examples/37_Patterns--Pattern_Refactoring
    uv run python recycle_rtti.py > a; uv run python recycle_dict.py > b; diff a b   # no output

Thirty lines of markers (372-401) repeat lines 234-263 exactly and demonstrate nothing. The payoff is deferred to exercise 1. Fix: run the dict sorter on `plastic.dat` with the same counter. It prints a `--- Plastic --- / Total value = 9.00` bin and "parsed 4, binned 4" — twelve lines that close the loop the chapter opened.

### [missing] Chapters/37_Patterns--Pattern_Refactoring.md:270 — the one-line rescue for `match` is never considered, so the argument for the table is weaker than it should be
The case against `recycle_rtti.py` rests entirely on silence: "Each one you miss silently drops trash on the floor" (line 270), "The `match` alone loses trash silently" (line 352). The chapter contains the string `case _` zero times. Every reader who knows `match` asks immediately: add `case _: raise ValueError(f"unsorted {type(t).__name__}")` and the silence is gone, with no redesign. Answering that is what makes the table win on its real merit rather than on loudness: the wildcard converts a wrong total into a crash, but you still edit the `match` for every new material, while `bins[type(t)]` needs no edit at all. Add that dismissal before the redesign.

### [missing] Chapters/37_Patterns--Pattern_Refactoring.md:424 — the second vector of change arrives by assertion, and the summary claims otherwise
The first half earns its redesign with a stated method: flaw, then "That is the argument. Here is the requirement that makes it concrete" (line 284), then `plastic_dropped.py` losing sixty pounds. The Visitor section drops that method entirely. No new requirement arrives, no failure is run, and `recycling_note.py` only shows the mechanism working. Nothing establishes why `Trash` growing a `note()` method is a problem, because no second and third operation ever appears. The summary then claims "This chapter discovered its two vectors one requirement at a time" (line 524), which the second half did not do. Fix: give the operations vector a concrete requirement and a demonstrated cost, matching the first half's shape.

### [missing] Chapters/37_Patterns--Pattern_Refactoring.md:430 — `singledispatch` is never weighed against simply overriding a method
The whole rebuttal to the obvious design is one asserted sentence: "`Trash` should not grow a method for every question the plant learns to ask... none of them belongs in `trash.py`" (lines 430-433). But every material in this chapter lives in `trash.py` and is under the author's control, so a `note()` method overridden per subclass is genuinely the lighter construct here, by the chapter's own criterion at line 523 ("choosing the lightest construct that isolates it"). A chapter that closes on "choose the lightest construct" cannot skip the comparison that decides this case. State the condition that flips it: the method wins when you own the hierarchy and the operations are few; `singledispatch` wins when you do not, or when operations outnumber materials.

### [better] Chapters/37_Patterns--Pattern_Refactoring.md:71 — `sum_value()`'s per-piece logging buries both sorters under output that is not the point
`sum_value()` prints `weight of Glass = 54.0` for every piece, so each sorter listing carries 30 lines of markers of which 4 matter. The book's own style rule (`.claude/skills/thinking-in-python/SKILL.md`, "Demos and tests") says a demo makes its point once and stops, and to keep step-by-step output only when the growth is itself the point. Here the growth is noise, and it is what makes the identical-output problem in finding 1 invisible on the page. Drop the per-piece line (or guard it), leaving four `--- Kind --- / Total value = ...` pairs per run. Sixty chapter lines shrink to eight, and a plastic bin appearing becomes visible at a glance.

### [better] Chapters/37_Patterns--Pattern_Refactoring.md:434 — the Visitor section re-argues chapter 33 before saying anything new
Lines 434-447 and 496-498 restate the case chapter 33 already makes in full: the `Visitor` base with one overload per element, `accept()`, double dispatch, no method overloading in Python, `singledispatch` as the one-call replacement. Lines 482-489's warning about the silent default duplicates 33's line 258/298. Chapter 33's headings ("The Price of the Empty Base", "One Dispatch Is Enough") cover it. What is new here is lines 500-514: the chapter now holds two dispatch mechanisms that disagree about subclasses, `bins[type(t)]` exact-keyed and `singledispatch` MRO-following. Cut the re-argument to a sentence and a link, and let the disagreement be the section.

### [better] Chapters/37_Patterns--Pattern_Refactoring.md:17 — the opening promises successive redesigns; the chapter delivers one
"an initial solution, then successive redesigns as new requirements appear" (lines 17-18) and the Fowler framing (lines 4-7) set up an iterated transformation. What follows is two independent finished listings plus an unrelated operation-adding demo. The chapter never names the transformation it performs (replacing conditional dispatch with a table) or shows it as a step, and line 417 concedes the point: "Swapping the `match` for the dictionary is a redesign, not a rename." One redesign is enough for the teaching, but the opening should promise what the chapter does: one design, one requirement that breaks it, one reshaping, then the second axis of change.

## Chapter 38 (Simulation): 7 findings

### [does-not-work] Chapters/38_Patterns--Simulation.md:168 — the atomic `claim()` the chapter calls "the heart of the program" is never exercised
Line 170 claims `claim()` ensures "a single rat gets each cell even when several reach it," but in `amaze.txt` several never do. Instrumenting the shipped run (`uv run python -c` over `maze.py`/`blackboard.py` in `build/examples/38_Patterns--Simulation/rats_and_mazes`) gives `open cells 139, adjacency edges 138 -> cycles: 0` and `{'true': 139, 'wall': 280, 'taken': 138}` — exactly 139-1 rejections, i.e. every rejection is a rat looking back at its own parent cell. Zero inter-rat contention ever occurs, and the chapter says so only in exercise 3 (line 1248, "`amaze.txt` is a perfect maze"). Ship a maze with at least one loop, or a second small looped one, so the demo actually shows two rats reaching one cell.

### [does-not-work] Chapters/38_Patterns--Simulation.md:958 — the emergent figure *is* a line of the code
"Its result appears in no line of its code" (958) and "Nothing in the code knows the pattern exists" (985) overclaim. The figure is the zero set of `amplitude()`, and three lines reproduce it directly: printing `'#' if amplitude(x, y, (2,3)) < 0.06 else ' '` over a 57x30 grid yields the same curves as the settled grains at line 1080. What is genuinely emergent is the *trapping mechanism* (noise carries a grain in and cannot carry it out), which the chapter states well at 1117-1121 but then credits the wrong thing. Draw the zero set beside the settled grains as a control, and claim emergence for the concentration, not the shape.

### [better] Chapters/38_Patterns--Simulation.md:454 — the robot section fails the chapter's own definition of simulation, and is the longest section
Line 3 defines a simulation as "objects that act on their own and interact through shared state." The robot acts on nothing of its own: `run(solution)` (line 722) replays a hard-coded 200-character move string (752-757), there is one agent, and there is no shared state. The chapter then admits the section's ideas are review: "Three ideas from earlier chapters carry the design" (937-944), naming chapters 20 and 27. At ~495 lines it is the chapter's largest block, and the one thing that would make it a simulation, a robot that chooses, is exiled to exercise 5 and a Reynolds link (948). Move a search into the main text, or cut the section hard.

### [does-not-work] Chapters/38_Patterns--Simulation.md:825 — the teleport-pairing idiom silently mispairs, and is taught without its precondition
Lines 826-831 present `teleports.sort(key=target)` plus `zip(pairs, pairs)` as an idiom to imitate, warning only against `zip(teleports, teleports)`. It is correct only when every letter appears exactly twice. With three `a`s and two `b`s (`GameBuilder("R_a_a_a_b_b")`) it pairs the third `a` with a `b` and leaves one `b` unpaired; walking into it gives `AttributeError: 'Teleport' object has no attribute 'target_room'`. Since `item_factory()` turns *any* unknown character into a `Teleport` (565), one typo in the maze does this, and exercise 4 has readers edit the maze. Group by letter and assert each group has two.

### [missing] Chapters/38_Patterns--Simulation.md:1114 — nothing tells the reader which parts of the picture are physics and which are the diffusion rule
The chapter closes with "When behavior emerges, reading the code is not enough. Run it." (1225-1226) and never says how to tell an emergent result from a modelling artifact — the one question this example makes urgent, since the amplitude formula is handed over as "treat it as given" (977). The model freezes: mean displacement per grain per step falls from 2.8e-3 at 100 steps to 1.7e-8 at 20,000, so the nodal lines keep thinning forever and their width is set by how long you ran, not by the plate. Real bowed sand reaches a moving steady state. State the model's limits, and name varying the rule (exercise 7) as the check.

### [missing] Chapters/38_Patterns--Simulation.md:456 — what the task-per-rat shape buys is never stated, and the obvious alternative is never weighed
"Concurrency is one way to build a simulation. Object-oriented design is another" compares the two *examples*, never the two implementations of the *rats*. The run is fully deterministic (round-robin `await asyncio.sleep(0)`, fixed `#:` markers), single-threaded, and buys no speedup; a plain worklist DFS produces the identical 139 cells. An expert reader's first question, "why asyncio here at all?", goes unanswered. The real answer is worth one paragraph: each rat's control flow stays a local `while` loop instead of an explicit stack of frontiers, which is what makes the code read like the domain. Say it, and say the cost.

### [better] Chapters/38_Patterns--Simulation.md:374 — two of the three GUI views re-render what the models already print
`rats_view.py` (391-450) and `maze_view.py` (885-935) are ~110 lines of tkinter that show what `Blackboard.render()` (228) and `show_maze()` (709) already produce in the demos, and the harness runs neither (`norun.txt`). Only `chladni_view.py` earns its place, because mode switching demonstrates something no text output can (1155-1159: the old figure bursting apart on a new field). `rats_view` also colors every claimed cell the same green, so the pack it is supposed to show is indistinguishable from a coverage map. Keep the Chladni view; reduce the other two to a sentence and a file pointer.

## Chapter 39 (Pattern Catalog): 5 findings

### [missing] Chapters/39_Patterns--Pattern_Catalog.md:172-198 — the catch-all table breaks the chapter's own organizing rule
Lines 17-18 promise "the tables follow each source's own grouping, so
each name sits where its source puts it," and every other table keeps
one source (GoF, POSA, Fowler, Hohpe/Woolf, Distributed/Cloud). "Other
Patterns and Idioms" has no such source: it mixes C++/Java language
idioms (CRTP, Pimpl, Marker Interface), functional-programming concepts
(Monad, Function Composition, Partial Application, Memoization), and
DI-family patterns (Dependency Injection, Service Locator, Inversion of
Control) in one flat 24-row alphabetical list. The chapter states a
principle and then its largest table violates it with no
acknowledgment. Fix: either sub-group this table (language idioms /
functional / DI-family) or state explicitly that it's the grab-bag
exception to the rule.

### [missing] Chapters/39_Patterns--Pattern_Catalog.md:32-44 — the problem-finder skips the two categories that need it most
The "Finding a Pattern by Problem" table indexes most GoF and
Distributed/Cloud names well, but of Fowler's 18 Enterprise patterns
(lines 118-137), roughly ten never appear in the finder table (Active
Record, Domain Model, Front Controller, Lazy Load, Money, Repository,
Service Layer, Table Module, Transaction Script, Special Case), and of
the 11 Messaging patterns (lines 141-153), eight are absent (Aggregator,
Content-Based Router, Message, Message Channel, Message Endpoint,
Message Router, Point-to-Point Channel, Splitter). These are exactly
the names an expert in one domain but not enterprise/messaging jargon
would need a problem-based lookup for. Fix: add rows (or extend
existing ones) covering persistence and messaging problems.

### [missing] Chapters/39_Patterns--Pattern_Catalog.md:12 — "many overlap, some compete" is never cashed out
The opening asserts overlap and competition among the cataloged
patterns but names no instance anywhere in the chapter. A concrete case
sits right in the tables: State (line 79, linked to
26_Patterns--Surrogate.md#state) and State Machine (line 197, linked to
31_Patterns--State_Machines.md) have intents close enough ("change
behavior when state changes" vs. "drive through a fixed set of states")
that a reader has to guess whether they're the same idea twice or
genuinely distinct, and the chapter gives no cross-reference or
contrast note for this or any other pair. Fix: point to at least one
concrete overlapping/competing pair, ideally State vs. State Machine,
with a one-line disambiguation.

### [better] Chapters/39_Patterns--Pattern_Catalog.md:35 — problem-table rows with many names don't discriminate
The table's stated job is "use this one when you know the problem but
not the name" (line 30), but several rows just list every candidate
with no way to choose among them: "Making one object stand in for
another" → Proxy, Decorator, Adapter, Façade, Ambassador, Sidecar (six
names, line 35); "Choosing behavior at runtime" → seven names (line
36). For these rows the table saves no work over reading the alphabetical
tables directly, since the reader must still open six entries to find
the right one. Fix: split the widest rows into narrower problem
statements, or add a short discriminator per name.

### [better] Chapters/39_Patterns--Pattern_Catalog.md:44 — a principle is listed as a peer of the patterns that implement it
Line 44's row, "Supplying a collaborator from outside," lists
"Dependency Injection, Service Locator, Inversion of Control, Strategy"
as four parallel options. But 25_Patterns--Template_Method.md (linked
from the Inversion of Control entry, line 183) calls IoC "the general
name for this reversal," i.e., the umbrella principle that DI and
Service Locator each realize, not a fourth technique alongside them.
Flattening the two into one list obscures that relationship instead of
teaching it. Fix: either drop IoC from this row (it's the reason the
row exists, not an entry in it) or note in the row that DI/Service
Locator implement it.

## Chapter 40 (Foundations): 5 findings

### [does-not-work] Chapters/40_Functional--Foundations.md:262 — dispatch.py demo proves less than the prose claims
"A dictionary of functions replaces a long `if`/`elif` chain" (262) and
"Supporting a new operator means adding a row to the table. The
dispatch code never changes" (283-284). `dispatch.py` has exactly two
entries (`+`, `-`); a two-branch `if`/`elif` is not "long," so the demo
doesn't earn the claim it's making — the reader has to take the payoff
on faith. Neither claim is shown: no operator is ever added at runtime
or import time (that's pushed to exercise 2), and the chapter never
shows what `operations["?"]` does on a missing key (a plain `KeyError`,
worse than an `if`/`elif`'s natural `else`). Fix: grow the table to 4-5
entries and add one from outside the literal, or show/discuss the
missing-key failure mode.

### [missing] Chapters/40_Functional--Foundations.md:602 — the chapter's synthesis example is the only one never exercised
"Putting the Pieces Together" (602) is explicitly billed as the
chapter's payoff: "Every section above showed one construct on its
own. Here they work together" (604-605), combining five ideas in
`pipeline.py`. None of the eight exercises (650-679) touch it — they
each drill one isolated construct (`pure_functions.py`, `dispatch.py`,
`closures.py`, etc.), so the reader never has to extend the one example
that shows the constructs composing, e.g. add a `colder_than` stage or
a second `map()` step to `report()`. This is the chapter's centerpiece
going unexercised, which the brief for this review names as the one
exercise-shaped thing worth reporting.

### [missing] Chapters/40_Functional--Foundations.md:121 — immutability's cost is never named
Lines 121-124 and 196-201 present immutability as pure upside: no
coordination, a stable hash, sharing with no defensive copy. The chapter
never states the standard counterweight — Python's built-in immutable
types have no structural sharing, so "build a new object instead of
mutating" means a full copy every time a large tuple or frozen
structure needs one field changed, not a cheap in-place update. An
expert reader's first question ("what's the catch?") goes unanswered,
and a search of the whole book (`grep -rl "structural sharing"
Chapters/`) finds nowhere else it's raised either.

### [better] Chapters/40_Functional--Foundations.md:298 — Lambdas has no listing of its own and only points forward
The entire section (298-313) is prose with a single inline expression
(`sorted(words, key=lambda w: w.lower())`, 308), no `#: `-checked code
block. It says so itself: "The higher-order functions below take them
as inline arguments, where they fit best" (302-303) — it exists to
introduce lambdas for the section that follows, breaking the pattern
every other section in this chapter uses (a claim backed by a runnable
listing). Fold it into Higher-Order Functions as an opening paragraph
rather than a standalone `##` section with nothing to run.

### [better] Chapters/40_Functional--Foundations.md:512 — Placeholder needs two type-checker workarounds to demonstrate one idea
"Leaving a Gap with `Placeholder`" teaches partial application with a
positional gap, but the listing needs `# type: ignore` twice (530, 531)
because `ty` misreads the call shape entirely — the prose has to spend
a full paragraph (547-551) explaining that the type checker is simply
wrong here. For a feature this new (Python 3.14) introduced this early
in a chapter titled "Foundations," the workaround explanation competes
with the concept itself for the reader's attention. Consider moving
this subsection later (e.g. Toolkits) once the reader has more slack,
or flagging up front that the annotations, not the code, are what's
broken.

## Chapter 41 (Toolkits): 6 findings

### [does-not-work] Chapters/41_Functional--Toolkits.md:65 — fib() is the wrong poster child for "cache makes recursion pay off"
The chapter's central case for both `@cache` (line 61-68) and Recursion
("Recursion pays off once the problem branches rather than repeats,"
line 823) is recursive Fibonacci sped up by caching. Fibonacci has a
trivial O(1)-space iterative form (`a, b = b, a+b`) needing neither
recursion nor a cache, and the book already shows an iterative
generator Fibonacci in `23_Patterns--Iterators.md:89-93`. Chapter 18
uses the same recursive+cached fib (line 868-891) with the identical
gap. An expert reader's first question — "why not just loop?" — is
never raised or answered. Fix: swap in a problem with genuine
overlapping-subproblem branching that has no simple iterative form
(e.g. counting paths, edit distance), or add one sentence conceding
fib's iterative alternative and explaining why the book still uses it
for exposition.

### [better] Chapters/41_Functional--Toolkits.md:833 — the Recursion section's own reasoning doesn't reach its example
Line 823-831 build a specific causal case: recursion pays off when
branches overlap and recompute a shared subproblem (fib), which is
why `@cache` matters. Line 833 then pivots — "Recursion suits problems
that are naturally self-similar, such as walking a tree" — into
`deep_sum()` (`nested_sum.py`), where no subproblem is ever shared or
recomputed; every sublist is visited exactly once. The reasoning that
justifies fib's recursion (repeated subproblems, solved by caching)
does not apply to the very next example, and the section never says
so, leaving two different justifications for recursion presented as
one continuous argument. Fix: mark the pivot explicitly ("a different
reason to recurse: ...") instead of "as the next example shows."

### [missing] Chapters/41_Functional--Toolkits.md:199 — cached_property's thread-safety caveat is the one caution this section skips
The "Be careful with caching" paragraph (line 199-203) only warns
about stale reads after mutation. `inspect.getsource(functools.cached_property)`
confirms there is no lock in `__get__`: two threads racing on first
access can both see `_NOT_FOUND` and both call `self.func(instance)`,
so a property with side effects (or an expensive computation) can run
twice. This is the same class of concurrent-access hazard the `tee()`
section states explicitly two subsections later ("`tee()` shares one
unlocked buffer... corrupts it," line 664-665). Fix: add one sentence
noting first access is not thread-safe (the lock CPython once had was
removed).

### [missing] Chapters/41_Functional--Toolkits.md:288 — total_ordering's real cost is never named
Line 288-292 gives one reason to prefer `@dataclass(order=True)` over
`@total_ordering`: it "generates all six comparisons from the field
order." `inspect.getsource(functools.total_ordering)` shows the actual
mechanism: each synthesized comparison is a wrapper function calling
the user-written one, adding a Python-level call per comparison versus
a directly generated method — the documented reason CPython's own docs
give for preferring hand-written or dataclass-generated methods where
it matters. The chapter states a stylistic reason (field order) and
omits the performance one, which is the one an expert reader
checking "why not always use this" would ask for.

### [better] Chapters/41_Functional--Toolkits.md:686 — three consecutive entries are pure reference-page filler
`permutations` (686-696), `combinations` (698-708), and
`combinations_with_replacement` (710-720) each give one sentence of
definition and one `list(...)`-wrapped demo with no gotcha, contrast,
or "why this over a comprehension" — unlike nearly every neighboring
entry (`pairwise` avoids an off-by-one, `batched` explains remainder
logic, `zip_longest` compares three strategies, `groupby` explains the
sorted-input requirement). The brief's own framing asks to judge this
chapter "as a teaching instrument, not as a reference page," and this
cluster reads as the latter. Fix: fold the three into one entry
contrasting them (order matters vs. not, repeats allowed vs. not)
instead of three flat, near-identical subsections.

### [better] Chapters/41_Functional--Toolkits.md:881 — the case study's title names a technique the shown code never implements
"Pairing Rotations" describes the circle method (line 881-891): fix
one player, rotate the rest, read off pairs — a real rotation. The
shown code, `student_pairs.py`, implements a different algorithm
(shuffle + greedy minimum-meetings fill) that contains no rotation of
any kind, for pairs or larger groups. The circle method is discussed
only in prose and never coded, so a reader who reads the section title
and expects to see rotations in the listing gets a greedy scheduler
instead, with the connection between title and code never stated. Fix:
retitle to name the greedy method ("Case Study: Fair Group Scheduling")
or show a short circle-method listing before generalizing away from it.

## Chapter 42 (Error Handling): 8 findings

### [does-not-work] Chapters/42_Functional--Error_Handling.md:551 — "Matching on the Error" shows nothing `try`/`except` doesn't already do
`describe()` calls `parse(text).bind(reciprocal)` and immediately matches
`Err(ValueError())` / `Err(ZeroDivisionError())`. The exception version is
shorter and equally safe: `try: return f"{text}: {1/int(text)}"` with two
`except` clauses. The `Result` never leaves the function, so none of the
chapter's stated benefits (failure visible in a signature, storable as data,
survives past a frame) are exercised. The section is presented as a payoff of
returning errors as values but demonstrates only `isinstance` dispatch that
Python has always had. Fix: make the `Result` cross a boundary (collect several
into a list, or return it and match in the caller) so the value-ness matters.

### [missing] Chapters/42_Functional--Error_Handling.md:510 — `@safe` erases the type-level failure information the chapter is selling
The thesis is "Failure appears in the return type" (line 17). `@safe` types
every wrapped function as `Result[A, Exception]`, so the signature says only
"can fail somehow" — exactly what a bare `except Exception` says, and strictly
less than a documented `raise`. Lines 521-530 discuss the catch-all only as a
defect-vs-outcome problem, never as the collapse of the chapter's own type
argument. Every static claim made for `Result[int, str]` stops holding the
moment `@safe` appears, and `matching_errors.py` gets no exhaustiveness help
from `ty`. Fix: state the trade where `@safe` is introduced, and show the
narrower `Result[int, ValueError]` a hand-written wrapper gives.

### [does-not-work] Chapters/42_Functional--Error_Handling.md:685 — the promised do-notation payoff never arrives
Line 434-436 tells the reader that nested binds get worse with each input and
that "[The returns Library] at the end of this chapter has do-notation, which
writes the same combination flat." The section it points at is five lines of
prose with no code, no do-notation, and not even a sketch of the flat form;
`returns` is not a dependency (`grep returns pyproject.toml` is empty). The
chapter raises a real problem, defers its solution by name, and then does not
deliver. Fix: either show the flat form (a `returns` snippet, run or not), or
drop the forward promise at 434 and let the section be a pointer.

### [missing] Chapters/42_Functional--Error_Handling.md:228 — the exception baseline for the composed chain is never shown
"Composing by Hand" and "Composing With bind" build two versions of `composed()`
without ever writing the third, the one every reader already knows:
`return func_c(func_b(func_a(i)))` with one `try` at the top. That version is
shorter than both, and shorter still than `result.py` plus every `Ok(...)`
wrapper. The intro asserts the costs of exceptions in the abstract (lines
10-23) but the chapter never puts the two implementations of *this* example
next to each other, so the reader cannot weigh what the discipline buys. Fix:
add the exception version of `composed()` and name what it cannot do (report
which step failed as data, survive into a list).

### [does-not-work] Chapters/42_Functional--Error_Handling.md:429 — the opening motivation is reversed by `bind` and never reconciled
The chapter opens on exceptions discarding partial calculations (line 28-58)
and `sum_type.py` fixes it: all five results survive. "Combining Multiple
Results" then runs three *independent* inputs through nested binds where "An
`Err` anywhere short-circuits to the end" — for `(1, 5)` the output is
`Err('func_a(1)')` and the reader never learns whether `func_b(5)` would have
succeeded. That is the opening complaint, reinstated by the chapter's own
machinery, unacknowledged; collecting all failures is exiled to exercise 3.
Fix: name the split explicitly (dependent chains want short-circuiting,
independent inputs want accumulation) where `combining.py` lands.

### [missing] Chapters/42_Functional--Error_Handling.md:150 — error types must unify across a `bind` chain, and nothing says so
Chaining a `@safe` function into a hand-written one is the first thing a reader
tries after the `@safe` section, and it does not produce a `Result`. Probe in
`build/examples/42_Functional--Error_Handling` (`uv run ty check`):
`parse("4").bind(to_str)` where `parse` is `@safe` and `to_str` returns
`Result[str, str]` reveals `Ok[str] | Err[str] | Err[Exception]` — a type no
`Result[A, E]` annotation names, so annotating the chain fails. Every listing
keeps error types homogeneous, which hides the constraint. Fix: one sentence
after `result.py` saying a chain's steps must share an error type (or that the
union widens and you must annotate the widened form).

### [missing] Chapters/42_Functional--Error_Handling.md:223 — the biggest hole in the chapter's promise gets prose but no listing
Lines 223-226 admit "a statement that calls the function and discards the
`Result` passes the checker" and that totality is "a discipline the function's
author keeps". These are the two failure modes that decide whether the
technique is worth adopting, and both are asserted rather than shown, while
the much smaller point that `.unwrap()` fails the checker gets a whole listing
(`must_unwrap.py`). A reader remembers the demonstration and forgets the
caveat. Fix: two lines in `must_unwrap.py` showing a discarded `Result` and a
`Result`-returning function that raises anyway, both passing `ty`.

### [better] Chapters/42_Functional--Error_Handling.md:182 — `unwrap()` earns nothing over the `Ok.answer` field it duplicates
"`unwrap()` makes that literal: only `Ok` defines it" is equally true of
`answer`, which `Ok` also defines and `Err` does not. Substituting it in my
probe gives the same static error (`error[unresolved-attribute]: Attribute
`answer` is not defined on `Err[str]` in union `Result[int, str]`) and the same
runtime `AttributeError`, so `must_unwrap.py` proves the same thing with no
method at all. The chapter itself reads `Err.error` directly (line 666) and
uses positional matching `Ok(answer)` elsewhere, so the getter is inconsistent
as well as redundant. Fix: keep `unwrap()` but say it is a Rust-borrowed name
for the field access, not a mechanism.

## Chapter 43 (Confidence): 7 findings

### [does-not-work] Chapters/43_Functional--Confidence.md:102 — the parallelism listing is ~2.7x *slower* in parallel, and the prose claims the opposite
"`count_primes()` is pure, and each call does enough work to spread across cores" is false at the sizes used. Timing the extracted `parallel_pure.py`'s two halves (serial `map` vs `pool.map`, four runs): `serial 0.065s parallel 0.178s speedup 0.37x`. The whole serial workload is 65ms; process spawn and pickling dominate. So a section titled "Automatic Parallelism" ships a listing where parallelism loses, and never measures anything — its only check is `assert parallel == serial`, which tests equality, not parallelism. A reader who times it learns the reverse of the lesson. Fix: raise the limits until the serial run takes seconds, and print a measured speedup so the payoff is visible.

### [missing] Chapters/43_Functional--Confidence.md:259 — the Hypothesis-beats-the-hand-loop claim is never demonstrated
The chapter argues Hypothesis "reaches inputs the loop cannot produce, such as unusual Unicode." Then both codec listings pass (`property_check.py` prints `1000 random cases passed`; `uv run pytest test_property.py` → `1 passed`), and `shrinking.py` switches to an unrelated space/underscore codec whose bug has nothing to do with Unicode or with strategy breadth. The hand loop and Hypothesis never once disagree, so the central comparison is asserted and never earned. Exercise 4 (line 383) asks the *reader* to run the Unicode falsification the chapter owes. Fix: give the hex codec a Unicode-sensitive bug (encode UTF-8, decode latin-1) so the five-letter loop passes and `strategies.text()` fails.

### [missing] Chapters/43_Functional--Confidence.md:79 — the `lru_cache` claim has no counterexample, and it is the chapter's one practical consequence of referential transparency
"Referential transparency is also what makes `lru_cache` safe. A memoizer can hand back a stored result because the call is interchangeable with its value." The chapter has an impure function three listings up (`withdraw()`), and never puts the two together. The failure mode that makes the concept stick — `@lru_cache` on `withdraw()` returning a stale balance and silently skipping the mutation — is a two-line demo the chapter does not do, so the safety claim stays abstract. Fix: cache `withdraw()` and print the wrong sequence of balances.

### [missing] Chapters/43_Functional--Confidence.md:209 — the spectrum ranks property testing above type checking without naming the axis it orders on
Rung 3 (types) is a universal claim over all inputs, but shallow: it proves only what the annotations express. Rung 4 (property testing) is a deep claim, but sampled: 100 cases is evidence, not a guarantee, and the chapter says so at line 213. So going 3→4 trades a universal guarantee for an expressive one — a sideways move, not a step up — yet the list presents a single linear ladder with "Above that." An expert reader stalls here. Fix: state the two axes (strength of guarantee vs. expressiveness of the claim), and say the rungs are ordered by expressiveness with the guarantee weakening at rung 4.

### [better] Chapters/43_Functional--Confidence.md:149 — Declarative Style is the only section with no listing, and its link to confidence is one unargued sentence
Everything in the section is recap: comprehensions point at chapter 16, `match` at chapter 13, and the `Result` example at chapter 42. Its one contribution to *this* chapter's thesis is "A description of the result is also easier to check than a sequence of steps, because less of it can be wrong" (line 160), which is asserted and never shown. The section then closes on two negatives — the win "is in the reading rather than in what a type checker can prove," and "It does not extend what the type checker knows" — so the payoff arrives as a retraction. Fix: cut it to a paragraph inside the spectrum, or show one law that is checkable on the declarative form and not on the loop.

### [missing] Chapters/43_Functional--Confidence.md:52 — every impurity shown uses `global`, the one case nobody gets wrong
`not_transparent.py` breaks transparency with `global balance`. That is the easiest case to spot. The cases that actually bite — reading the clock, reading `os.environ`, mutating a passed-in list, depending on `dict` iteration order or `id()` — are all deferred to exercise 6 (line 395). A reader can finish the section believing "no `global` means pure." Fix: add one three-line listing where a function mutates its argument, since it takes no globals and still breaks substitution.

### [better] Chapters/43_Functional--Confidence.md:245 — the hand-written loop's most obvious defect goes unnamed, weakening the case for Hypothesis
`assert decode(encode(sample)) == sample` in a plain script reports nothing about the failing input: CPython prints the assert source and `AssertionError`, no value (verified: a bare failing `assert sample.upper() == sample` prints the expression and `AssertionError` only). So the hand loop's first problem is not that its counterexample is un-shrunk — it is that you get no counterexample at all. The chapter jumps straight to shrinking (line 284), skipping the cheaper argument. Fix: one sentence noting the bare `assert` loses the input, so shrinking is the second improvement, not the first.

## Chapter 44 (Effect Management): 8 findings

### [missing] Chapters/44_Effects--Effect_Management.md:477 — the chapter's core claim, that hand-passing does not scale, has no listing
The whole four-chapter arc rests on lines 477-486: "Every function that calls `greet()` must accept an `Ask` and a `Tell`... Parameters accumulate at every level of the call stack." No code shows that. `ask_tell.py` calls `greet(Scripted(), captured)` at module level (line 458), zero intermediate frames, so the listing demonstrates only that delayed binding is pleasant. The pain is asserted and outsourced to Exercise 2. Line 787-790 does the same for `async`'s virality (asserted; outsourced to Exercise 5). Fix: add ~15 lines threading `ask`/`tell` through `main`/`menu`/`session`, then adding `Log`, so the reader sees five signatures change.

### [does-not-work] Chapters/44_Effects--Effect_Management.md:193 — `slope_catch.py`'s "unanticipated" exception is four lines above `slope()`
The prose claims `validate()` "raises `ValueError` for a negative `run`, an exception `slope()` never anticipated," and that "knowing every one of them is the tracking problem an Effect Management System exists to solve." But `validate()` is defined in the same nine-line listing (lines 170-173), its whole body is one `raise`, and `slope()`'s author wrote the call. The demonstration shows a careless author, not a scaling problem. The chapter's own thesis is that you must read every callee; here that is two visible lines. Fix: import the raising helper from an outside module, or state that the listing compresses distance the real case supplies.

### [better] Chapters/44_Effects--Effect_Management.md:714 — "Custom AI Languages with Effects" is 23 lines of links carrying two sentences of teaching
Lines 727-749 list ten brand-new, unadopted languages with one-line blurbs and URLs. The teaching content is lines 722-725 (AI languages usually implement tracking only, because interface separation and delayed binding would weaken a host's guarantee) and 751-753 (Pact and Lumen are exceptions). Ten links do not strengthen a claim two examples establish. The section also sits between "Library Effect Management" and "Effect Management for Python?", interrupting the arc that has been building toward Python since line 606, and its content will date within a year. Fix: keep the two sentences plus Pact and Lumen; drop the catalog.

### [missing] Chapters/44_Effects--Effect_Management.md:118 — the three-kind taxonomy rests on a criterion switch the chapter never reconciles
Line 42 defines the term: "An *Effect* causes impurity." The chapter then grants that formal theory backs calling exceptions pure (lines 98-103), and resolves with a different criterion, propagation: "If you write a function `a()` that calls a function `b()` that raises... `a()` also raises that exception" (114-115). "Effects therefore come in three kinds" follows from the second criterion, not the stated definition, so the definition given at the top excludes one of its own three members. Fix: define an Effect once, in propagation terms (what a caller inherits and the signature does not show), which covers all three kinds and makes the exception case fall out instead of being stapled on.

### [missing] Chapters/44_Effects--Effect_Management.md:248 — the three-way comparison names `try`'s weakness and hides `Result`'s
Lines 246-256 weigh the three conversions. Catching by hand gets its cost stated ("a blind spot for an exception nobody thought to catch") plus a full paragraph and the C++/Java exception-specification history. `Result` gets only "makes every caller handle failure explicitly." Its real cost in this listing is unstated: `@safe` catches `Exception` blanket-wide, so `slope_result.py` returns `Result[float, Exception]`, and a caller cannot distinguish `ZeroDivisionError` from a `TypeError` bug. Chapter 42 names this at its line 521, so line 156's "`slope()` is now total" reads as an unqualified win here. Fix: one clause recalling the blanket-catch cost so the comparison is symmetric.

### [missing] Chapters/44_Effects--Effect_Management.md:246 — the three techniques are presented as mutually exclusive, never composed
"Here are three ways to do it" (124) and "All three approaches... differ in how many functions must know about it" (256) frame the conversions as a menu. The standard practice combines two of them: parse untrusted input at the boundary with a `Result`-returning constructor, then everything downstream takes the restrictive type and is total. The chapter has both halves on the page and never joins them, so the obvious expert question is left open: how do I build a `NonZero` from user input, given that `NonZero(0)` raises (line 228)? Fix: one paragraph showing `@safe`-wrapped construction returning `Result[NonZero, Exception]` at the edge.

### [better] Chapters/44_Effects--Effect_Management.md:282 — `pure_and_pointless.py` spends a benchmark on a truism, and one call prints nothing
The section argues a pure program is unobservable from outside the process, then observes it from outside with a clock and a `print()` to establish that a 2,000,000-iteration loop takes longer than `pass`. No reader doubts this, and the prose already says it (lines 288-293). Worse, `report(busy_loop=busy, empty_function=idle)` at line 282 emits nothing without `--numbers`: `PYTHONPATH=build/examples/utils uv run python build/examples/44_Effects--Effect_Management/pure_and_pointless.py` prints only `burned real CPU time for nothing: True`. A reader sees a call with no result. Fix: cut the timing machinery, or make the two measurements visible so the listing earns its place.

### [better] Chapters/44_Effects--Effect_Management.md:344 — the opening story is retold with the same details 340 lines later
Lines 3-7 open with the intermittent test, the currency-formatting helper three calls down, the configuration read and audit-log write, and "None of that is in any signature on the path." Lines 344-355 retell all of it (adding only an exchange-rate call) before reaching the new material, the four questions at 360-363. The callback is justified; repeating its content is not, and by line 344 the reader has just spent 200 lines on exception conversion and needs the four questions, not the anecdote again. Fix: compress 344-355 to the one-sentence callback already present at line 344 and go straight to the questions.

## Chapter 45 (Generators): 3 findings

### [missing] Chapters/45_Effects--Generators.md:552 — throw()/close() described, never run
Lines 552-555 and 634 tell the reader a driver "can also `throw()` an
exception into a generator or `close()` it," and that `yield from` relays
both, but none of the chapter's 11 listings ever calls either method. I
grepped `build/examples/45_Effects--Generators/*.py` for `.throw(` / `.close(`
and found zero hits. This is the one place the mechanism could connect to
something the reader already has: chapter 15 showed the identical behavior
("Python resumes the generator by raising the block's exception at the
`yield`", ch15:84) without naming it either. Neither chapter demonstrates the
`close()`/`GeneratorExit` gotcha (`RuntimeError: generator ignored
GeneratorExit`) that matters for a driver like the one this chapter builds
toward. Fix: one short listing calling `.throw()`/`.close()` on a live
generator, naming the ch15 connection.

### [missing] Chapters/45_Effects--Generators.md:633 — the combined loop is asserted, never built
Line 633 calls the chapter's mechanism "`task_runner()`'s turn-taking and
`drive()`'s question-answering, in one loop" and says that pairing is what
`await`/the event loop actually does. But `task_runner.py` (578-616) only
ever calls `next()` — I checked, it never calls `.send()` — so it shows
turn-taking alone; no listing rotates between generators *and* answers what
each one yields. The chapter's own capstone claim (this pairing IS asyncio's
mechanism) is stated, not demonstrated, so the payoff of "The Driver You
Already Use" arrives only in prose. Fix: extend `task_runner()`, or add one
listing, where a task yields a request and the runner supplies an answer via
`send()`, closing the loop the text describes.

### [better] Chapters/45_Effects--Generators.md:213 — walrus operator with no genuine expression to shorten
`print(f"{type(c := conversation)}: {c.__name__}")  # type: ignore` in
`two_way_generator.py` binds `c` only to save typing `conversation` twice
inside one f-string; there is no assignment-inside-expression being
collapsed, no loop condition, no duplicated call. The book's own style skill
(`.claude/skills/thinking-in-python/SKILL.md:266`) says to use `:=` "for a
genuine assignment-inside-expression... skip it when a plain two-line
assignment-then-check reads just as clearly; it isn't a compactness
contest." `print(f"{type(conversation)}: {conversation.__name__}")` reads
the same with no walrus, no incidental syntax to parse in an example whose
point is generator identity, not `:=`.

## Chapter 46 (Stateless): 7 findings

### [does-not-work] Chapters/46_Effects--Stateless.md:1458 — the `try`/`except`-inside-an-Effect rule is false whenever a handler sits between it and `run()`

"Because the driver throws the failure back in, an ordinary `try`/`except` around a `yield from` catches it... comes back down into the innermost suspended frame, where the `except` clause runs." That holds only for `except_vs_catch.py`, where `run()` drives `guarded()` directly. `Handler.__call__`'s loop (`handler.py:82`) does `case Exception() as error: yield error` without resuming, so `run_async`'s `effect.throw()` lands in the handler's frame, not the Effect's. Probe: `run(supply(Console())(guarded_with_console)('Carol'))` printed `escaped: KeyError 'Carol'` and never ran the inner `except`. `catch_score.py`'s `report()`, 100 lines later, has exactly that shape. State the restriction, or drop the claim.

### [does-not-work] Chapters/46_Effects--Stateless.md:684 — "One Effect, Many Environments" concedes its own listing proves nothing

`nailer.py`/`test_nailer.py` spend 70 lines on a single flat function, and line 745 admits "Dependencies as parameters serve this test as well, because `holds(material, nailer)` is easy to call four times." The claimed advantage is then asserted, never shown: "The two diverge when the dependency sits three calls deep" (749). No listing shows that case, so the section's payoff never arrives. `audit_log.py` already has a `Need[Log]` two levels deep and could carry the parametrized test instead, making the varied environment reach past intermediate signatures that never mention it.

### [missing] Chapters/46_Effects--Stateless.md:951 — the DI comparison answers only the service-locator form, then generalizes to all DI

`dependency_injection.py` is a global registry read from inside the body (`get(Console)`), the form most Python teams already treat as an anti-pattern. Line 959 calls it "Conventional DI", and line 1030 concludes "it relocates a side cause rather than declaring one, so the type checker never validates the dependency." Constructor injection does put the dependency in a signature and is statically checked; FastAPI's `Depends`, the form most production Python actually uses, likewise. Neither is named anywhere in 44-47. Name and dismiss the strong version (it binds only at the endpoint, so intermediate helpers still thread parameters by hand); otherwise the section beats a straw man.

### [missing] Chapters/46_Effects--Stateless.md:1285 — `run()`'s cost is never stated, though the chapter just showed the line that causes it

"its entire body is `return asyncio.run(run_async(effect))`" is presented purely as an explanation of why `run()` fails inside `async def`. It also means every `run()` builds and tears down an event loop, even for an Effect with no `Async` at all. Measured: `uv run python -c "timeit.timeit(lambda: run(success(42)), number=50)"` gives 655 us per call versus 0.04 us for the equivalent plain call. That number is the real justification for "A synchronous program calls it once, at the outermost edge" (line 93), and it matters for `test_nailer.py`, which pays it per parametrized case. One sentence with the measurement would close it.

### [missing] Chapters/46_Effects--Stateless.md:185 — nothing says what keeps the two channels apart once they collapse into one union

"The `Generator` yields either an Ability `A` or an exception `E`" and "`A` and `E` share the first type parameter" (193) raise the obvious question and leave it. The answers exist and are short: statically the library bounds `A` to `Ability[Any]` and `E` to `Exception` (the chapter states the first only at line 1162, as a rule about `Depend[Console, None]`, never the second); at runtime `run_async` discriminates with `case Exception() as error`. Without this the reader cannot predict what a custom Ability that also subclasses `Exception` does, nor why chapter 47's `catch_all` is `catch(Exception)`.

### [better] Chapters/46_Effects--Stateless.md:1055 — handler layering, a core compositional property, is taught as bullet 2 of a DI comparison

"Handlers also layer. An Ability a handler cannot answer travels further out, so `supply(Log())(greet_all)` still has the type `(list[str]) -> Depend[Need[Console], None]`" is the first and only statement of partial supply, and its demonstration is the subsection "A Default Binding" (1084). Layering is what makes `supply()` compose (bind near the Effect, bind the rest at the edge, with the type recording what each layer left) and it is independent of the DI argument. It deserves its own section next to "Supplying the Dependency", with defaults as the corollary rather than the vehicle.

### [better] Chapters/46_Effects--Stateless.md:753 — "Builtin Dependencies" arrives 620 lines after the chapter starts hand-rolling a `Console` the library ships

Line 780 finally says "For illustration, this chapter builds a `Console` rather than using the one from Stateless." By then the reader has met `greeter.py` (133), `greet_all.py`, `audit_log.py`, `console_protocol.py` and `default_console.py`, each redefining `Console`, with no reason given. The section also uses none of the three builtins it lists, and its real content (a concrete class forces inheritance on doubles, so a double overriding only `print()` reads live stdin) is the setup for "Supplying an Interface", which restates it. Move the one-line rationale to `greeter.py` and fold the inheritance cost into the next section.

## Chapter 47 (Stateless in Practice): 7 findings

### [missing] Chapters/47_Effects--Stateless_in_Practice.md:1784 — `fork()` silently erases the error channel, and nothing in the chapter says so

"The type checker enforces one restriction. A forked Effect must have nothing left to supply." That is not the only thing `fork()` does to the type. Every one of its four overloads returns `Depend[Need[Executor], Task[R]]`, dropping `E`. With `def bad(n: int) -> Try[Boom, int]`, `uv run ty check` reveals `fork(bad)` as `(n: int) -> Generator[Need[Executor], Any, Task[int]]` — no `Boom`. At runtime the failure escapes `wait()` as a raised exception (I ran it: `escaped: Boom 1`), past any `catch()`. This is a hole in the two-channel guarantee the chapter is built on, and neither this section, nor the toolkit row (line 1836, "Adds `Need[Executor]`; the result becomes `Task[R]`"), nor the five limits mentions it. State it here and add it to "Where the Guarantee Stops."

### [missing] Chapters/47_Effects--Stateless_in_Practice.md:1040 — the promised "retry the whole pipeline" is never cashed, and `retry()` cannot be selective

"a second caller can catch the same three failures and choose different messages, retry the whole pipeline, or let one failure through to the edge, without touching the pipeline." The chapter then retries `save_user()`, never `research()`, and never says `retry()` retries *every* declared failure. It cannot discriminate: its body is `catch_all(f)` plus "was it an `Exception`?". Retrying `research()` under `WEATHER` therefore re-fetches three times for a `NotInteresting` that is deterministic (`RetryError ['NotInteresting','NotInteresting','NotInteresting']`, three `feed: fetching` lines). Only exercise 7 reveals this, as a question. Limit 5's operator inventory (no timeout, no race, no backoff) should name "no error-selective retry" too, and the body should say retry is all-or-nothing over `E`.

### [missing] Chapters/47_Effects--Stateless_in_Practice.md:1710 — `memoize()` keys on arguments alone, so it ignores the supplied environment

"`memoize()` caches by argument the way `functools.lru_cache` does" is accurate and, in a dependency-injection library, is the whole danger. `memoize` is `lru_cache` wrapped around the *undecorated* function, so the environment supplied outside it is not in the key. Running `m = memoize(save_user)` then `run(supply(db1)(m)("Morty"))` and `run(supply(db2)(m)("Morty"))` prints `Morty saved` twice with `db1.attempts 1, db2.attempts 0`: the second database was never touched and returned the first one's answer. In a chapter whose thesis is that the environment is swappable, that deserves the same one-paragraph caution the retry section gives non-idempotent work.

### [missing] Chapters/47_Effects--Stateless_in_Practice.md:1851 — the toolkit gives the `run`/`run_async` rule without the reason, and never mentions the cost

The table says `run(effect)` is "From synchronous code" and `await run_async(effect)` is "From inside a running event loop", with no explanation. The reason is that `run()` *is* `asyncio.run()`: it builds and tears down a fresh event loop per call. Two consequences an expert reader will hit and cannot deduce from the table. Calling `run()` inside a loop raises `RuntimeError: asyncio.run() cannot be called from a running event loop` — the first thing that happens in any async web handler. And it costs: measured here, `run(bound(1))` is 672 µs/call while the same Effect through `run_async` inside one loop is 1.31 µs/call. One sentence naming `asyncio.run()` fixes both.

### [better] Chapters/47_Effects--Stateless_in_Practice.md:738 — the State section asserts its testability payoff instead of showing it, and the listing on the page uses the global it says you avoid

"A test builds its own pair from a fresh `Cell`, the way `at()` builds a clock from a moment, and asserts on what remains, with no global to reset between tests." No such code appears. Meanwhile `wallet.py` (line 670) binds `cell = Cell(100)` at module level and closes `read()`/`write()` over it, so the listing demonstrates the one shape the paragraph disowns. The clock section did this right: it showed `at()`, then `test_timekeeping.py` using it. Give `wallet.py` a `ledger(cell)` factory returning the handler pair, and add three lines asserting `cell.amount == 10` from a fresh cell.

### [better] Chapters/47_Effects--Stateless_in_Practice.md:1933 — limit 2 spends its evidence on the case that works, and asserts the case that fails

"2. The type checker can give up quietly" opens by establishing that partial handling *works*, with a full listing (`partial_handling.py`) and a full `ty` diagnostic block, roughly 50 lines. The actual limit gets eight lines and no evidence: "If you write `handle(scripted)(handle(capture)(greet))`, `ty` gives up on the nested inference and infers `Unknown`". That inferred `Unknown` is the dangerous case, the one the section warns is "permissive enough to hide a genuinely missing handler", and it is the only claim here with no output shown. Swap the emphasis: show the `Unknown` reveal, and compress the working partial-handling demo to the paragraph it needs.

### [better] Chapters/47_Effects--Stateless_in_Practice.md:1310 — "Supplying a Whole Cast" spends about 115 lines of listing on two new ideas

`quest.py`, `casts.py`, and `two_games.py` carry five Protocols, eight one-line implementation classes, and a four-run driver. Two things here are new: the Abstract Factory comparison (matched families are lost, "a `Kitty` bats at a `Weapon`"), and `supply()`'s nine-overload ceiling. Everything else re-runs "Composing a Program": a boundary function that upcasts, a swapped implementation, a recorder standing in for `print` (`Script` after `Wire`/`Library`, after ch46's `Recorder`). Three actors instead of five make both new points at half the reading cost, and the ceiling paragraph does not need a wide cast on the page to be stated.

---

## Appendix A: the brief every agent received


You are reviewing one chapter of *Thinking in Python*, a book teaching
modern Python (3.15) to experienced programmers. Your job is the one
review dimension no prior pass has covered: **what does not work, what
is missing, and what could be better**. Read the chapter the way a
hostile expert reviewer would: someone who knows Python deeply, teaches
it, and is looking for reasons the chapter fails its reader.

This is structural review, run before hand-polish. Findings should be
worth fixing before anyone polishes sentences.

## What is already covered elsewhere (do NOT report)

Three book-wide passes just finished. Do not duplicate them:

- **Factual correctness.** Every checkable claim was verified against
  its listing book-wide; 56 errors were fixed. Do not re-audit claims
  line by line. (If a claim you happen to check while evaluating an
  example is false, report it, but that is not your assignment.)
- **Exercises.** Every exercise was performed cold and diffed against
  its solution; 75 findings were fixed. Skip the exercise section
  unless an exercise is structurally wrong for the chapter (tests
  something never taught, or the chapter's centerpiece goes
  unexercised).
- **Cross-chapter consistency and self-reference.** Gated now.

Also out of scope: prose style, word choice, AI tells, sentence-level
polish. Later passes handle those. A sentence only matters here if its
problem is structural (the concept it introduces is wrong-shaped or
misplaced), not verbal.

## What TO look for

- **Does not work:** an example that fails to demonstrate the point the
  prose makes of it (it would work the same without the feature being
  taught, or it shows the mechanism without showing why anyone wants
  it); a motivating problem the shown solution doesn't actually solve;
  a demonstration that proves less than the prose claims; a section
  whose payoff never arrives.
- **Missing:** the obvious question an expert reader asks that the
  chapter never answers; the failure mode or counterexample that would
  make the concept stick, absent; a well-known alternative approach
  never weighed or dismissed; a limitation of the taught technique
  never stated; a "when NOT to use this" that the chapter needs.
- **Could be better:** a concept used before it is taught (within this
  chapter; cross-chapter ordering is settled); a section that runs long
  past its teaching value, or repeats an earlier section's work; an
  example whose incidental complexity buries the point; a listing
  whose design a good Python programmer would object to on grounds the
  book itself teaches elsewhere (the book's own style skill is
  `.claude/skills/thinking-in-python/SKILL.md` if you need it); two
  sections that should be one, or one that should be two; a weak
  opening that doesn't tell the reader why the chapter exists.

Judge the chapter as a teaching instrument, not as a reference page.

## Method requirements (non-negotiable)

- **Report-only. Edit nothing.** The only file you write is your
  report, `adversarial_reports/NN.md` (NN = your chapter number).
  `git status` must show nothing else new.
- Read the whole chapter before reporting anything.
- When a finding depends on what code does, **run it**: the extracted
  listings live in `build/examples/<chapter-dir>/`, run via
  `uv run python <file>` from the repo root. Never bare `python` (it is
  a different, older interpreter on this machine). Never create scratch
  copies of listings; run the extracted files.
- A `#:` output marker that differs from your standalone run is NOT a
  finding. Markers are claims about the gate's process (which runs all
  blocks in one process); timing/memory values legitimately differ
  standalone. Report a marker only if it is wrong in kind, not value.
- Everything in the foreground: no background jobs, no monitors. Your
  final message is the finished report, with nothing still running.
- Do not run any `make` target. No `make verify`, no `make gate`,
  nothing that mutates. `uv run python`, `uv run ty check`, and
  read-only inspection are all you need.

## Report format

Write the report to `adversarial_reports/NN.md` AND return the same
text as your final message (your final text is the return value read by
the orchestrator, not a message to a human).

Header: `Chapter NN (<title>): <n> findings` — or `Chapter NN
(<title>): clean` if you have none. Clean is a respectable answer;
do not invent findings to fill space.

Then at most **8 findings**, strongest first, each:

```
### [does-not-work|missing|better] Chapters/NN_...md:<line> — <one-line summary>
<At most 120 words: the problem, the evidence (quote the prose or
name the listing and what it actually does), and, in one sentence,
what a fix would look like. If you ran code to establish this,
include the command and the relevant output line.>
```

Anchor every finding to a current line number. Any claim you make about
what a listing does must have been checked against the listing or by
running it; a finding that misreads the code is worse than no finding.
