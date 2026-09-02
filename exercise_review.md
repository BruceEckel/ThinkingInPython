When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

# Whole-book exercise pass: the decision queue

RECOMMENDATIONS item 1, run 2026-09-02.
Scope was every exercise in the book: 45 chapters, roughly 320 exercises,
each performed cold from the chapter alone and then diffed against
`Solutions/`.

Like `archive/~correctness_review.md`, this is deliberately **not** in a
per-chapter review file. It spans thirty chapters, so `do-reviews` cannot
apply it. Applying it is a hand job.

**Method.** One fresh agent per chapter, report-only, briefed to perform
each exercise before reading its solution, on the reasoning that reading
the solution first makes you agree with it. Sonnet for the 32 chapters
whose exercises are mechanical, Opus for the 13 dense ones (17, 18, 19,
32, 34, 36, 37, 38, 42, 43, 44, 46, 47). Chapters 18 and 19 ran last and
were briefed separately about wall-clock booleans, `tools/data/timing.txt`,
and the asyncio task cliff; both returned zero timing findings and said so
explicitly, which is the outcome that brief was written to produce.

**Numbers.** 75 findings across 30 chapters. Fifteen came back clean: 02,
03, 04, 06, 07, 11, 14, 15, 21, 23, 24, 25, 26, 33, 45. By severity:
**0 blocking, 27 wrong, 15 drift, 33 minor**. Nothing here is
gate-detectable; `make sweep` was green before this pass and is green now.

**Verification status.** RECOMMENDATIONS says verify before applying, and
the correctness sweep reproduced every finding before anything landed.
I reproduced seven of these myself, marked **[reproduced]** below. The
rest carry the agent's own reproduction (command and output) in its
report, but a second pair of eyes has not seen them. Treat an unmarked
finding as credible and unconfirmed.

---

## The one systemic cause

**Ten of the 27 `wrong` findings are stale `ty` output quoted in
`Solutions/`, and every single one of them is in `Solutions/`. Not one
is in `Chapters/`.**

08, 13, 17, 36, 42, 43, 46 (three separate ones), 47. The failures are
wrong line numbers, wrong diagnostic codes, wrong message text, and in two
cases a claim built on the wrong wording that inverts the point being
taught.

CLAUDE.md already says a `ty` upgrade is "a book-wide event, not a tooling
detail," and lists the 0.0.58→0.0.63 and 0.0.70→0.0.75 fallout chapter by
chapter. The evidence here says those sweeps went through `Chapters/` and
stopped there. Nothing catches it: `solutions-output-check` validates `#:`
markers, but a `ty` diagnostic quoted in prose is not a `#:` marker.

The fix is procedural, and it belongs in CLAUDE.md's `ty`-upgrade entry:
**after a `ty` upgrade, re-capture every quoted diagnostic in `Solutions/`
as well as in `Chapters/`.** There are 31 `error[...]` codes book-wide, so
the sweep is small once someone remembers to run it.

---

## Part 1: the chapter is wrong about its own listing

A reader following these is stopped, or is told something the listing
disproves. Highest value in the pass.

### 1.1 Chapter 37, exercise 1: edit the file it says needs no edits **[reproduced]**

`Chapters/37_Patterns--Pattern_Refactoring.md:536-538`.
"Add a `Plastic` material to `trash.py`, then run `recycle_dict.py` over
`plastic.dat`. Confirm that `recycle_dict.py` and `parse_trash.py` need no
changes."

`recycle_dict.py` line 8 is `for t in parse("trash.dat"):`. No argv, no
other entry point. The reader must edit the file the next clause says needs
no edit. **The prior sweep found this and it is still present verbatim.**

The claim is true of the *sorting loop* and false of the *script*, so the
cheapest fix scopes it: "…then point `recycle_dict.py` at `plastic.dat` and
run it. Confirm that its sorting loop and `parse_trash.py` need no other
changes…". The rest of the exercise checks out (60 lb of plastic, $9.00,
`test_subclasses_self_register` is the failing test).

### 1.2 Chapter 37, exercise 4: "over data" for a listing that reads none **[reproduced]**

`Chapters/37_Patterns--Pattern_Refactoring.md:546`. "run both
`recycle_dict.py` and `recycling_note.py` over data containing it."

`recycling_note.py` opens no file. Its driver is
`for cls in Trash.registry.values():`. A `CrushedAluminum` reaches it purely
by having its `class` statement execute. The stated outcome does hold; only
the framing is false. Fix: "…add it to the data `recycle_dict.py` reads, and
run both that and `recycling_note.py`."

### 1.3 Chapter 16, exercise 2: "3 by 3" against a `SIZE = 6` listing **[reproduced]**

`Chapters/16_Techniques--Comprehensions.md:680-682`; listing at `:220-234`;
solution at `Solutions/16_Techniques--Comprehensions.md:21-33`.

The listing sets `SIZE: Final[int] = 6` and prints six rows. The exercise
says 3 by 3. The solution discards `SIZE` and hardcodes `range(3)` — and
then its own prose says "Only the literal in the conditional expression
changes, from `1` to `2`", which is false, because the size changed too.
Three-way disagreement.

Cheapest fix: change the exercise to "6 by 6" and the solution to
`range(SIZE)`. That needs no code change and makes the solution's
"only the literal changes" sentence true for the first time.

### 1.4 Chapter 43, exercise 1: the named edit fails the listing's own assert

`Chapters/43_Functional--Confidence.md:373`, listing at `:104-127`.
"Change `count_primes()` to return `(count, os.getpid())`."

`parallel_pure.py` computes `serial` in the parent and `parallel` in
workers, then asserts they are equal. Once the PID rides in the tuple, the
assert fails. The exercise never says it must go. The solution silently
drops both `serial` and the assert. Fix: add "…and narrow the `assert` to
compare only the counts."

### 1.5 Chapter 17, exercise 9: every natural payload is a `SyntaxError`

`Chapters/17_Techniques--Metaprogramming.md:1840-1843`.
`make_class()` splices `class_name` in twice, the second time inside a
string literal, so a bare newline is an unterminated string. Three natural
payloads all died before executing; only one that ends by opening a
triple-quoted string works. The solution uses exactly that trick and says
why. The chapter's half is the one missing the information.

Fix: add the clause. "…(note that `make_class()` splices the name in twice,
the second time inside a string literal, so a bare newline is a
`SyntaxError`)…"

### 1.6 Chapter 36, exercise 7: the second half shows nothing

`Chapters/36_Patterns--Memento.md:617-621`. Every `Drawing` the chapter
builds has a nonempty title, so loading old bytes under a class with a
`__post_init__()` that rejects empty titles is indistinguishable from
loading them without it. The solution quietly pickles a second object the
exercise never mentions (`Drawing("", ("circle",))`).

Fix: name the empty title in the first sentence. "Save two `Drawing`s with
`pickle`, one of them with an empty title."

### 1.7 Chapter 44, exercise 3: asks for a conversion the chapter says does not apply

`Chapters/44_Effects--Effect_Management.md:926-927`. The exercise asks
which of the three conversions from *Converting Effectful to Pure* applies
to a side effect and a side cause. The chapter states at `:419-421` that
"every technique in [Converting Effectful to Pure] manually manages one
Effect, the exception," and assigns side effects and side causes to a
different technique entirely (pass the implementation as a parameter,
`:422-428`). Four of the six rows have no answer among the three.

The solution answers "Return a result type" for all four, then describes
plain parameter threading, using no `Result`, `Ok`, `Err`, or `@safe`.

Fix is a judgment call: narrow the question to the exceptions and point the
others at *Effects by Hand*, or widen it to "which by-hand technique from
this chapter". Either way the four rows must change.

### 1.8 Chapter 42, exercise 6: one half of the question is always empty

`Chapters/42_Functional--Error_Handling.md:733-735`. Converting only
`func_a()`, as instructed, collapses nothing (all three failures stay
distinguishable). Converting the whole chain, which is what the solution
silently does, collapses all three. So "which can the caller still tell
apart" and "which have collapsed" never both have answers.

Fix: make the exercise say what the solution does and ask the one question
it answers. Alternative in the report converts `func_a` and `func_b` only,
which keeps the two-part shape but is a larger rewrite.

### 1.9 Chapter 19: the chapter and its solution name different Python versions **[reproduced]**

`Chapters/19_Techniques--Concurrency.md:1209` says "Since 3.10 the
interpreter switches threads only at a function call or at the jump that
closes a loop iteration". `Solutions/19_Techniques--Concurrency.md:342`
says "Since 3.11, the interpreter only considers switching". Same
mechanism, two releases, and exercise 7 sends the reader at that sentence.

One is false. **Do not take the number from this file.** The agent judged
3.10 the likelier one but did not reproduce the version boundary, and
neither did I.

### 1.10 Chapter 47, exercise 8: the literal edit dies, and the fix is in another chapter

`Chapters/47_Effects--Stateless_in_Practice.md:2192-2195`. Swapping
`ThreadPoolExecutor` for `ProcessPoolExecutor` in `parallel.py` dies in a
`BrokenProcessPool` cascade without an `if __name__ == "__main__":` guard,
which appears nowhere in chapter 47 (only chapter 19). The solution carries
the guard without saying it was needed.

### 1.11 Chapter 46: three exercises that cannot run as written

- **Exercise 6** (`:1746-1749`): "Run it against `greet()`" right after
  naming `default_console.py`, whose `Console` requires a `tag`, so
  `ability.t()` raises a `TypeError`. Works against `greeter.py`'s `greet()`.
- **Exercise 10** (`:1778-1785`): asks for a name that triggers the
  `ValueError`, but `scores.py`'s `SCORES` holds no negative score and the
  exercise never says to add one. The solution silently redefines the
  scoreboard with `"Cyd": -3`.
- **Exercise 9** (`:1771-1777`): importing `stateless_coroutine.py` runs its
  unguarded top-level `print(run(...))`, so an unrelated line prints first.

### 1.12 Chapter 46, exercise 11: the stated outcome does not hold

`Chapters/46_Effects--Stateless.md:1786-1792`. The exercise has the reader
create an ambiguity, then claims the fix makes it a type error. Two
recorders sharing `record()`, declared as two Protocols, stay ambiguous by
argument order with `ty` clean. The solution drops the third implementation
from its listing and concedes the point in prose.

### 1.13 Chapter 40, exercise 7: the second instruction has no referent

`Chapters/40_Functional--Foundations.md:669-673`. Replace the
`map()`/`filter()` calls with comprehensions, *then* "delete the `list()`
around the `map()` call" — after the first edit no `map()` call remains.
The solution silently restarts from the pre-comprehension code without
signalling that it is a separate branch.

---

## Part 2: the solution states something false

### 2.1 Stale `ty` output (the systemic group)

Each of these needs the quoted block regenerated from a real
`uv run ty check`, the way the correct ones in the same files were made.

| Where | What is wrong |
|---|---|
| `Solutions/08...md:196-202` | Cites line 14 (real: 12) and claims `ty` spells the `Literal[...]` union out in full. `ty` 0.0.75 reports `Expected \`Color\`` — the alias name. The solution's prose ("the alias costs nothing in the error message") is built on the wrong wording and says the opposite of what the tool does. |
| `Solutions/13...md:157-166` | Quotes `error[invalid-argument-type] ... Expected \`Never\`, found \`Webhook\``. Real: `error[type-assertion-failure] ... Inferred type of argument is \`Webhook & ~Email\``. Different code, different text. Exercise 2's block in the same file is correct, which is the model to copy. |
| `Solutions/17...md:226-258` | Quotes a `with ignore(TypeError):` version of `metaclass_layout_conflict.py` the chapter no longer has (it uses `try`/`except`), cites `:6:11` (real `:5:11`), and says the program prints `TypeError('...')` when it prints the bare message. The `repr` form is what `ignore` would print. |
| `Solutions/36...md:253-257` | "a `Drawing` built with a `list` there fails `ty check`" — `json.loads()` returns `Any`, so `ty` passes. True of a statically-typed list, false at the call site described. The runtime consequences it also cites are real. |
| `Solutions/42...md:222-231` | "`ty` reports that gap as an error" is the whole justification for abandoning `Ok`/`Err`. `ty` 0.0.75 narrows the pattern fine. See 3.1. |
| `Solutions/43...md:457-467` | "`result.answer` comes back as `object`". Real: `float \| Unknown`. |
| `Solutions/46...md:724`, `:736` | Cites `exercise_10.py:21:28` with gutter 19/20/21; real is `28:28` with 26/27/28. The prose repeats "line 21". Off by seven, consistent with an older, shorter listing. |
| `Solutions/46...md:804` | Cites `exercise_11.py:31:30` for a line not in the 39-line listing. Line 31 is something else. Appending the quoted call makes it line 40, where it reproduces verbatim. |
| `Solutions/46...md:92`, `:487`, `:494` | Three diagnostics one line short, because the listing's `# name.py` header comment is not counted. `6:20`→`7:20`, `7:25`→`8:25`, `9:5`→`10:5`. The chapter body quotes the same `undeclared_need.py` error *correctly*, so the two files disagree about one file. |
| `Solutions/47...md:594-596` | "`assert_never()` reports the new member as an unhandled branch in `report()`". Real next diagnostic is `invalid-yield` at the `yield from`; `assert_never` fires only after two further edits. |

### 2.2 Chapter 32: the solution's own code is broken **[reproduced]**

`Solutions/32_Patterns--Multiple_Dispatching.md:511-541` (`exercise_8.py`),
same formula in `exercise_10.py` at `:627+`.

`weapon_outcome()` is not antisymmetric. With six weapons,
`diff = (ia - ib) % 6` has five non-draw values and the rule accounts for
four (1, 2 → win; 4, 5 → lose). `diff == 3`, the antipodal pair, falls
through to `LOSE` **in both directions**, so all three antipodal pairs have
both combatants losing:

```
Jargon vs SellImaginaryProduct: lose / lose
Play vs Edict:                  lose / lose
InventFeature vs Schedule:      lose / lose
```

This is structural, not a typo. A cyclic "beats the next k" tournament is
antisymmetric only when the count is **odd** (`2k + 1 == len(WEAPON_ORDER)`).
So the solution's claim at `:506` — "the same shape `paper_scissors_rock.py`
uses for three items, extended to six" — describes something that cannot
exist. Three items work precisely because nothing is left over.

Three more findings in the same file follow from it or sit beside it:

- **`:600-603`** "no group can count on winning" is false. `meeting(5)`
  returned `Troll` on 200/200 seeds, `meeting(20)` on 50/50. Two of the
  three cross-kind matchups are decided on all four weapon combinations.
  The `#: Troll` marker is not one sampled outcome, it is the only one,
  so it cannot catch a regression here either.
- **`:532-533`** the in-code docstring says a weapon beats the **next** two;
  the code and the surrounding prose both say the **previous** two.
- **`:442-447`** "A `Lizard` whose rows you forgot to write no longer raises
  `KeyError`" is false for the chapter's `Lizard`, which is `Lizard(Item)`,
  a direct subclass of the base with no row keyed on `Item`. It still
  raises. Only a subclass of a *concrete* item inherits answers. Fix:
  use `WetPaper(Paper)`, which the same section's last paragraph already
  uses.

Findings 2.2's first two must be fixed together: repairing the ranking
changes solution 8's `#: Troll` marker and solution 10's generated table.

### 2.3 Chapter 28: the canned failure message is wrong for the case shown

`Solutions/28...md:128-139`, `:149-155`. `solve()` prints
`"{finder.__name__} failed: could not converge"` for every failure. But
`bisection(f, 1.0, 1.3)` has `f(1.0)*f(1.3) = 0.31 > 0`, so it returns
`None` on its first line and never iterates. It did not fail to converge;
it failed a precondition. The exercise also asked that "each handler
reports why it failed", which the solution declines to build and says so.

### 2.4 Chapter 18: the wrong profile row

`Solutions/18...md:287-290`. Solution 8 names the generator expression
inside `inner()` as the largest `tottime`. It is `{built-in method
builtins.sum}`, 0.020 vs 0.015 in 7 of 7 runs — cProfile charges the C
`sum` frame with the cost of driving the generator, so this is structural,
not noise. The `cumtime` half is correct.

### 2.5 Chapter 43: a Hypothesis counterexample that never appears

`Solutions/43...md:320-332` quotes `names=['a', 'b', 'c'], size=2` and calls
it "the simplest such roster the alphabet allows". Eight runs (three warm,
five with `.hypothesis/` deleted) gave only `['a', 'b', 'aa'], size=2` (5)
and `['a', 'aa'], size=3` (3). Hypothesis shrinks to `'aa'`, not `'c'`.

### 2.6 Chapter 47: a `StopIteration` that does not happen

`Solutions/47...md:915`. "A fifth attempt would raise a `StopIteration`
from `read()`." It does not: the exhausted iterator ends the Effect
silently and `run()` returns `None` instead of the count, so `spree()`'s
`return bought` never runs. Verified with a bare `except BaseException`.
The silent truncation is a better point than the one the sentence makes.

---

## Part 3: the solution answers a different question (15 drift findings)

Not false, but the reader who does the exercise as written cannot match
their result to the answer. `tools/check_solutions.py` already gates
numbering, and its docstring names this gap exactly: "What it cannot see is
a solution that answers the wrong exercise under the right number; that
still needs a human reading the two side by side." This pass is that read.

| Where | Drift |
|---|---|
| 13 ex 4 (`Ch:850`) | Solution drops `Sms` and `Push` from the `Notification` union and never shows the `cost()` case the exercise asks for. Extending the real 3-channel file gives two `ty` diagnostics, not one. |
| 13 ex 6 (`Ch:858-861`) | Exercise says "write `act()`"; no function named `act()` exists in the solution, which reuses `broken()`. |
| 20 ex 3 (`Ch:1133-1139`) | Exercise asks for three return-type annotations. Solution also deletes `Package`'s `weight_kg` and its `frozen=True`, hardcodes `2.5` for `4.5`, and makes `charge()` return a `$`-string. The minimal edit reproduces the quoted `ty` error exactly. |
| 27 ex 3 (`Ch:902-905`) | Solution omits the entire `games2.py` half, including the Protocol version and the type-checker error the exercise builds to. Doing the missing half works. |
| 27 ex 6 (`Ch:913-916`) | Exercise says three times to edit `registry.py`; solution invents `shape_registry.py` instead, unexplained. |
| 31 ex 5 (`Ch:890-892`) **[reproduced]** | Exercise names `state_machine.py`, "the first design, where each state decides the next one". Solution 5 is titled "rebuilt on `table_machine.py`" — the table-driven design that exercise 6 asks for. |
| 31 ex 9 (`Ch:905-908`) | Exercise says to add `Nickel` to `vending_machine.py`; the solution invents a two-state toy and never imports it, though its own prose cites that file's `FirstDigit`/`SecondDigit`. |
| 32 ex 6 (`Ch:527-529`) | Exercise asks to walk `type(self).__mro__` and name which *one* of two properties is given up; the solution walks both operands and says both. |
| 34 ex 5 (`Ch:664`) | Solution rewrites `to_infix()` to drop all parentheses, so its printed output is unreachable from the chapter's `infix.py`. |
| 34 ex 6 (`Ch:668-672`) | Solution also guards `__add__()`/`__mul__()`, unasked and unmentioned; the two named r-methods alone give the stated `TypeError`. |
| 34 ex 3 (`Ch:657-660`) | Exercise asks for three updates; solution codes one, leaves two in prose, and adds an unrequested `__rtruediv__()`. |
| 38 ex 4 (`Ch:1259-1260`) | Exercise asks two questions; solution answers one, never addressing what happens if `Coin` derives from `Food` (`item_factory("$")` returns a `Teleport` and the robot never finishes). |
| 41 ex 6 (`Ch:1063-1066`) | Exercise names the case study's `group_rounds()` with its `met()`/`history` greedy algorithm; the solution shows a naive shuffle-and-chunk function of the same name. The stated conclusion still holds. |
| 46 ex 11 | See 1.12. |
| 47 ex 8 | See 1.10. |

---

## Part 4: minor (33)

One line each, grouped by shape. All locations are in the per-chapter
reports; the ones worth a glance are marked.

**Solution renames or rewrites something unasked** (the commonest shape,
and arguably one decision rather than nine): 05 ex 2 rewrites `get()`'s
missing-key branch to raise where the chapter returns the sentinel · 10 ex
6 renames `self_link()` to `pair_link()` · 13 ex 3 renames the catch-all
case · 17 solutions 8 and 10 rebuild the listing under new names
(`Built`→`Demo`, `NoDuplicates`→`KeepFirst`) · 19 solutions 1, 7, 8 answer
a restructured listing, so the reader's trace has a line the solution's
`#:` block lacks · 22 ex 4 renames `tags` to `b` · 35 ex 8 uses
`time.sleep(0.1)` where the exercise says `0.05` (0.05 is just as reliable,
5/5) · 38 ex 4 uses a three-line toy maze where the exercise says "the
robot maze" (which works: five `$` gave `finished: True coins: 5`) · 32 ex
8 and ex 10 say "modify the above example" and rebuild parts instead.

**The exercise needs something the chapter never showed**: 09 ex 5 uses
`field(default_factory=list)` while the chapter at `:122-123` explicitly
defers `default_factory` to chapter 12 · 30 ex 3 and 4 need
`raise ExceptionGroup("msg", failures)`, and `ExceptionGroup(` appears zero
times book-wide — chapter 19 only shows *catching* one via `except*`.

**The exercise's wording does not match the listing**: 29 ex 3 says "its
classes" (plural) where `facade.py` has one, and the solution invents a
second to make the plural true, which undercuts its own closing claim · 19
ex 5 says to write `lock = asyncio.Semaphore(1)` then to call
`semaphore.release()`; taken literally that is a `NameError` · 12 ex 6 says
to verify "with `display_object()`" and the solution uses
`inspect.signature()` instead (`display_object()` does work here) · 17 ex
10 asks the reader to confirm which `on_open` runs, where both bodies are
`...` · 34 ex 4 says "only the parentheses that precedence requires" and
the solution's `prec + 1` rule emits some it does not, candidly · 44 ex 2
asks for a count the solution reaches differently (four edits vs "five
signatures") · 44 ex 3 names `Thermometer` in chapter 30, where three
classes carry that name and the first holds no state · 47 ex 14
presupposes the two functions lack a shared signature; both are already
`(narrator: Narrator) -> None`, and the solution opens by correcting it.

**Solution prose slightly off**: 17 solution 9 contradicts itself about
when the injected statement runs (`:405` vs `:417`) · 18 solution 3 binds
`peak` from `tracemalloc` and never prints it, so the "roughly half" claim
is right but unshown · 18 solution 7 justifies its answer with "CPython
implements `print()` and `sum()` in C" where the program never calls
`sum()` · 43 solution 7 calls two `describe()` versions "the same length in
statements" (12 vs 9 lines, 7 vs 9 AST statements) where the exercise says
to count lines · 47 solution 12 quotes a `ValueError` naming `'scripted'`
where the library interpolates the full function repr · 47 solution 14 says
one edit where two are needed, plus four `#:` markers shift.

**Nondeterminism presented as determinate**: 43 ex 4's "the minimal
counterexample" `'µ'` came up 7 of 12 runs, `'ß'` 4, `'ﬀ'` 1 · 35
solution 2's committed marker says `9.9` and four runs gave `9.8`
(sizes 100 and 200 match, so only the size-50 line drifts) · 42 ex 1 asks
to confirm short-circuiting that the solution's arrangement cannot show,
since `func_e` ends up last with nothing left to skip; mid-chain it works.

---

## Part 5: already fixed, recorded so nobody re-proposes them

- **Chapter 38** is clean of the prior sweep's defects. Exercise 3 now
  reproduces exactly: `amaze.txt` verified a tree (139 open cells, 138
  adjacencies), 30 consecutive async-`claim()` runs gave zero
  disagreement, the looped `LAYOUT` gave 25 successes vs 24 visited every
  run, and `test_rats_and_mazes.py` still passes against the broken
  `claim()`. No exercise here has a stated outcome `Solutions/38`
  contradicts. Every one of the eight reproduces.
- **Chapter 10, exercise 5** no longer names one edit where the solution
  makes three; `e4a4e6cd` fixed it, and performing it cold gives the
  solution's output exactly.
- **Chapter 32's exercise text** is clean throughout. All seven of its
  findings are in `Solutions/`.

---

## Part 6: a gate hole, and what a gate could not do

### 6.1 `Solutions/40` and `Solutions/41` sit outside four gates **[reproduced]**

Neither chapter appears in `build/solutions/`. The cause: of their 16
```python blocks, **zero** carry a `# slug.py` first line, so
`extract_solutions.py` writes nothing. Every other Solutions file slugs
most of its blocks.

Consequence: those 16 listings are never type-checked (`solutions-ty`),
never linted (`solutions-lint`), never run (`solutions-run`), never
pytest'd. `#:` markers *are* still checked, because `validate_output.py`
reads the `.md` directly — it reported "2 ok" on both files.

I ran all 16 by hand. All execute; `ruff` at the book's 60 columns passes;
`ty` reports 4 diagnostics, all consistent with deliberate demonstrations
of failure (a `Final` reassignment, an unhashable argument to `@cache`, a
positional-only `partial`). So nothing is currently broken there — but
nothing would tell you if it broke, and the two chapters' agents had to
source their code from the Markdown.

Fix: give those blocks slugs, then decide whether the four intentional
diagnostics need `# type: ignore` pragmas the way the rest of the book
does. That is a real decision, not a mechanical one, which is why it is
here rather than done.

### 6.2 What a new gate would and would not catch

Worth writing down so nobody builds the wrong one.

- **Numbering is already gated** and works. Every one of the 45 agents
  confirmed exercise and solution counts match. All the drift lives
  exactly where `check_solutions.py`'s docstring predicted it would.
- **A referent gate** — every `foo.py` an exercise names must be a listing
  slug in that chapter — would run at **5** hits book-wide, all of them
  files the reader is told to *create* (ch06's `Module.py`, `module5.py`,
  `module6.py`, `noisy2.py`; ch27's `extra_shapes.py`). Cheap and nearly
  green. **It would have caught none of these 75 findings**, because the
  failures are false claims about files that do exist. Do not build it
  expecting help here.
- **The `ty`-quote problem is procedural, not gateable** in any cheap way,
  since verifying a quoted diagnostic means knowing which file it belongs
  to and running the tool on it. The 31 `error[...]` codes book-wide make a
  manual sweep small. Put it in the CLAUDE.md `ty`-upgrade entry.

---

## Part 7: clean chapters (15 of 45)

02, 03, 04, 06, 07, 11, 14, 15, 21, 23, 24, 25, 26, 33, 45.

Each had every exercise performed and every solution listing run. Chapter
45 carries two notes rather than findings (a missing `/` positional-only
marker in a quoted typeshed signature, and exercise 2's "say what it
returns" against a solution driver that raises).

---

## Suggested order of application

1. **Part 1** — the reader-facing breakage. 1.1 and 1.2 first: they are
   reproduced, the prior sweep already flagged 1.1, and both are one-clause
   rewordings.
2. **Part 2.1 as one batch** — regenerate all ten quoted `ty` blocks in one
   sitting with `uv run ty check`, then add the procedural note to
   CLAUDE.md so the next upgrade sweeps `Solutions/` too.
3. **Part 2.2** — chapter 32's ranking. It is the only finding here that is
   a genuine algorithm bug, it changes two `#:` markers, and it needs a
   design decision (odd weapon count, explicit antipodal case, or hand-built
   table).
4. **Part 3** — the drift, chapter by chapter. Mostly a choice between
   rewording the exercise and rewriting the solution; the reports argue
   each one.
5. **Part 6.1** — slug the two Solutions chapters back under the gates.
6. **Part 4** — minor, last, and several could reasonably be declined.

Reproduce before applying anything not marked **[reproduced]**. The
per-chapter reports, with the full command and output behind every
finding, are in `exercise_review_reports/NN.md`, one file per chapter
including the fifteen clean ones. Delete that directory along with this
file when the queue is applied.
