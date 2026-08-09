# Annealing review

A settling pass over every chapter, run sequentially after the deep-review and
readability reviews were applied.
Normally `/annealing` writes no file and reports in chat;
this run records every applied change here instead, one section per chapter.

Everything recorded here is **already applied** to `Chapters/`.
Revert anything you dislike from `git diff Chapters/`.
Findings that did not clear the confidence bar were discarded unreported,
per the skill.
Structural change (cutting, reordering, pacing) stayed out of bounds throughout.

Started from a clean tree at `e6642ba`.
No unapplied `deep_review/` file exists for any chapter, so nothing was blocked.

## Progress

| Chapter | Status | Applied |
|---|---|---|
| 01_Introduction | done | 1 |
| 02_Tour | done | 1 |
| 03_Containers | done | 1 |
| 04_Control_Flow | done | 2 |
| 05_Functions | done | 0 (annealed clean) |
| 06_Modules_and_Packages | done | 2 |
| 07_Classes | done | 1 |
| 08_Static_Typing | done | 0 (annealed clean) |
| 09_Class_Attributes | done | 2 |
| 10_Cleanup | done | 1 |
| 11_Testing | done | 2 |
| 12_Data_Classes_as_Types | done | 0 (annealed clean) |
| 13_Pattern_Matching | done | 0 (annealed clean) |
| 14_Decorators | done | 0 (annealed clean) |
| 15_Context_Managers | done | 1 |
| 16_Comprehensions | done | 0 (annealed clean) |
| 17_Metaprogramming | done | 0 (annealed clean) |
| 18_Performance | done | 1 |
| 19_Concurrency | done | 4 |
| 20_Rethinking_Objects | done | 3 |
| 21_The_Pattern_Concept | done | 0 (annealed clean) |
| 22_Data_Transfer_Objects | done | 1 |
| 23_Iterators | done | 2 |
| 24_Singleton | done | 0 (annealed clean) |
| 25_Template_Method | done | 0 (annealed clean) |
| 26_Surrogate | done | 0 (annealed clean) |
| 27_Factory | done | 2 |
| 28_Function_Objects | done | 2 |
| 29_Changing_the_Interface | done | 0 (annealed clean) |
| 30_Observer | done | 1 |
| 31_State_Machines | done | 2 |
| 32_Multiple_Dispatching | done | 2 |
| 33_Visitor | done | 2 |
| 34_Composite_and_Interpreter | done | 2 |
| 35_Flyweight | done | 1 |
| 36_Memento | done | 4 |
| 37_Pattern_Refactoring | done | 0 (annealed clean) |
| 38_Simulation | done | 0 (annealed clean) |
| 39_Pattern_Catalog | done | 0 (annealed clean) |
| 40_Functional_Foundations | done | 4 |
| 41_Functional_Toolkits | done | 4 |
| 42_Functional_Error_Handling | done | 1 |
| 43_Functional_Assurance | done | 4 |
| 44_Effect_Management | done | 2 |
| 45_Generators | done | 3 |
| 46_Stateless | done | 2 |
| 47_Stateless_in_Practice | done | 5 |
| 06_Modules_and_Packages (revisited) | done | 1 |

**The book is annealed end to end.** Every chapter has been through the pass.

These stayed declined throughout, as established book vocabulary rather than
slips:

- "earns its keep" / "earns its place" — 12 uses book-wide. Leave.
- `spell` / `spelling` — 10 uses across nine chapters. Leave.

The two open items carried forward for chapter 19 were both resolved: the three
"reaches for" uses became "tries to acquire" / "asks for" (the surrounding text
already says "acquire"), and `19:845`'s "is what turns" lost the cleft.

---

## 17_Metaprogramming

**Annealed clean** across 1,739 lines.

Two things independently confirm the traps recorded in `CLAUDE.md`, so leave them
alone: `greenhouse.py` and `utils/display.py` both annotate unions as
`EventMaker | NOT_CREATED` and `Sequence[str] | ALL_DUNDERS | REDEFINED_DUNDERS`,
naming the specific sentinel **values** rather than the generic `sentinel` class,
which is what makes `ty` narrow the other branch; and `_redefined()` restricts its
comparison to `INTERESTING_DUNDERS` with a comment explaining that every class
carries bookkeeping dunders differing from `object`'s.

---

## 18_Performance

**Verified clean:** every threshold boolean has a wide margin (100x, 3x, 10x, 5x,
2x against real order-of-magnitude gaps), so none is at risk of the silent flip
`CLAUDE.md` warns about. The NumPy, Numba and combined listings are indented
blocks rather than fenced ones, deliberately un-run because neither package
installs on the pinned 3.15 — matching the project-memory note, with `TODO(py315-deps)`
comments marking the conversion.

**Applied:**

- **Bisect.** "but only `bisect_left()` lands on an existing value" → "points at
  an existing value." "lands" is on the don't-use list; "points at" is the book's
  own word for this (chapter 14 uses it for `__wrapped__`).

---

## 01_Introduction

**Verified clean:** the five-part structure matches `build_site.py` `PARTS`
(I/02, II/11, III/20, IV/40, V/44), and each part's prose description matches the
chapters it actually spans.
`Examples/14_Decorators/tracer.py` and `Examples/utils/result.py` both exist as
named.
"Most chapters end with a short Exercises section" holds: 45 of 47.
The `14_Decorators.md#maintaining-the-wrapped-interface` anchor resolves.

**Applied:**

- **The Examples, output-marker paragraph.** "appears in the run of markers below
  the block" → "after the loop or the `import`". The chapter establishes "block"
  two paragraphs earlier as the whole fenced listing ("Every code block that
  begins with a filename comment"), so "below the block" read as *at the end of
  the listing*, which contradicts the markers-hug-their-code convention the
  sentence is there to explain. Naming the loop and the `import` removes the
  collision.

---

## 02_Tour

**Verified clean:** floor division and remainder signs (`-7 // 2` is `-4`,
`-7 % 2` is `1`, sign of `%` follows the divisor); banker's rounding in both
`round()` and the f-string format spec, which is what makes `{score:.0f}` on
`91.5` print `92`; `~x == -x - 1` and the `bin()` sign-and-magnitude rendering;
the `Template` piece sequence in `tstrings.py` (`('', ' scored ', '%')`, empty
literal skipped on iteration, `shout()` output).
All five exercises name variables and files that exist.

**Applied:**

- **Naming Conventions.** "The one exception is class names, which are
  `CapWords`" → "Class names are `CapWords`". The count was wrong: constants
  (`THIS_IS_A_CONSTANT`) are described in the immediately preceding paragraph and
  are already a departure from `snake_case`, and the *following* paragraph adds
  callable-style classes that use `snake_case` after all. Dropping the count
  loses nothing and stops the section contradicting its neighbors.

---

## 03_Containers

**Verified clean:** every set-algebra result and its method equivalent; the
`Counter` repr ordering; `deque(maxlen=3)` window contents; the live
`MappingProxyType` view; shallow-immutability behavior (`hash()` on a tuple
holding a list raises `TypeError`); dict `|` asymmetry.
Both threshold booleans have wide margins (`set_time * 100 < list_time` on an
O(n) vs O(1) scan at n=200,000; `deque_time * 20 < list_time` on O(n²) vs O(n)),
so neither is at risk of the flip described in `CLAUDE.md`.
All 23 example files exist, and `report()` resolves to `Examples/utils/benchmark.py`.

**Applied:**

- **Lists, before `list_traps.py`.** "Two ways of building a `list` produce
  surprises." → "Two list operations produce surprises." The promised pair is the
  `*` repetition trap and removing-while-iterating, and the second is not a way of
  *building* a list. The listing's other half (`[[0] for _ in range(3)]`) is the
  fix, not a second surprise, so the original sentence had no honest referent for
  its count.

---

## 04_Control_Flow

**Verified clean:** the Collatz trace in `while_loop.py` (six printed values, six
steps); the `zip(strict=True)` message text; the list-mutation skip in
`mutating_while_looping.py` (one of the two `2`s survives) and the dict's
`RuntimeError`; all three exception-chaining joining lines; the `isdigit()` /
`int()` disagreement running in both directions (`"-5"` rejected by one, `"²"`
accepted by one). Every exercise names a listing that exists.

**Applied:**

- **Placeholders, first paragraph.** "you have none to run yet**:**" → "yet**.**"
  The colon promised the listing, but a whole paragraph about `...` intervened
  before any code arrived. This is an edit seam: the `...` paragraph was clearly
  added between the `pass` sentence and its example, and the original colon was
  left pointing at nothing. The second paragraph's colon already introduces the
  listing correctly.
- **Loops, after `looping.py`.** "re-looks-up the item on every line that needs
  it" → "looks the item up again on every line that needs it." "re-looks-up" is
  not a construction English supports; the replacement preserves the meaning
  exactly.

---

## 05_Functions

**Annealed clean.** No finding cleared the bar.

One claim was worth verifying rather than trusting, and it survived: the chapter
states that each `sentinel()` call builds a new object even for the same name, so
`default is sentinel("MISSING")` is always false. PEP 661 sentinels are widely
described as caching per name and module, which would have made this wrong. Run
against the pinned interpreter (3.15.0rc1), `sentinel('MISSING') is
sentinel('MISSING')` is `False` and the repr is the bare name, so both the prose
and the `#: MISSING` marker are right as written. Recorded here so a later pass
does not "fix" a correct sentence.

Also verified: `bad_append.__defaults__` printing `([1, 2],)`, the `tally()`
positional/keyword split, the `all_markers.py` binding, and both `sorted()` key
orderings in `lambdas.py`.

---

## 06_Modules_and_Packages

**Verified clean:** the `from`-snapshot behavior in `from_snapshot.py`; the
`sys.modules` identity claims; every package listing's load-order markers.
`sys.lazy_modules` is real on the pinned build and reports deferred names, so the
PEP 810 paragraph is accurate.

**Applied:**

- **`PYTHONPATH` section.** The `-P` clause was moved out of the middle of the
  `sys.path` ordering into its own sentence at the end. The paragraph enumerates
  the search order (script directory, then `PYTHONPATH`, then installed
  packages), and the `-P` aside was spliced between the first and second items,
  so the reader lost the list mid-count. Every fact is retained.
- **`package_only.py`** (code block). `#: initializing a_package` moved from the
  clump at the listing's end up to the `import a_package` line that produces it.
  Every neighboring package listing in this chapter already hugs its markers this
  way; this one was the outlier. Re-synced and re-validated (`1 ok, 0 failed`).

---

## 07_Classes

**Verified clean:** the full `Simple2` override chain in `demo_simple2.py`
(including the four-line `show_twice()` trace); `cached_property` staleness and
the `del`-then-recompute sequence; `Circle(10).area` at 314.159 through both the
plain-attribute and validated-property versions; the `from_fahrenheit(212)`
conversion.

**Applied:**

- **`@override` at run time.** "It tries to set an `__override__` attribute on the
  method (some callables refuse it), for anything that wants to find overrides by
  introspection, and returns the same function object." → main clause first ("It
  returns the same function object"), with the attribute-setting subordinated and
  the purpose clause reattached to what it modifies. The original stranded "for
  anything that wants to find overrides" behind a parenthetical, so the sentence
  needed a second reading; it also used "wants" for a non-agent.

---

## 08_Static_Typing

**Annealed clean.** No finding cleared the bar.

Two things worth recording so a later pass does not undo them:

- **"where they earn their keep" (Gradual Typing) stays.** It looked like a
  candidate, since the chapter-26 deep review removed "earns its keep" from that
  chapter's conclusion at your instruction. But the figure appears **12 times**
  across the book (9 in `Chapters/`, 3 in `Solutions/`: 16, 21, 34, 40 twice, 41
  twice, 47, and this one). That makes it established vocabulary rather than a
  slip, and rewriting one instance would be a voice change, which annealing puts
  out of bounds. The chapter-26 removal was local to that chapter's conclusion.
- **The missing blank line after `# area.py` is load-bearing.** House style would
  suggest adding one, but the chapter quotes `ty`'s diagnostic verbatim including
  `--> area.py:6:12`, and the call sits on line 6 only because that blank line is
  absent. Adding it would silently falsify the quoted error block.

---

## 09_Class_Attributes

**Applied:**

- **A `@dataclass` reads annotations.** "The annotation is what marks a field." →
  "The annotation marks a field." A cleft with the verb right behind it; deleting
  the words changes nothing.
- Same paragraph: "Write `x = 100` with no `x: int` and `@dataclass` sees
  nothing:" → "If you write `x = 100` with no `x: int`, `@dataclass` sees
  nothing:" (imperative-plus-consequence; the listing below is the demonstration,
  so this was a hypothetical, not an instruction).

**Declined:** "write the spelling that says so" (Which Dictionary?) stays. The
global rule bans the noun, but the book uses `spell`/`spelling` 10 times across
nine chapters, so it is vocabulary; changing one instance would be inconsistent.

---

## 10_Cleanup

**Applied:**

- **`finalize_trap.py` commentary.** "keeps the question to the one being asked" →
  "narrows the listing to the question being asked". A question cannot be kept to
  itself; the sentence needed a second reading.

---

## 11_Testing

**Verified clean:** `test_account.py:11` in the quoted pytest failure really is
the assert line. Both numeric claims check out against the pinned interpreter:
five 5% applications land on `127.62815624999999`, and `random.Random(0).randint(1, 6)`
is `4` (so the chapter's note that its agreeing with the stubbed `4` is a
coincidence is itself correct).

**Applied:**

- **"instead of reaching for it"** → "instead of going looking for it". "reach
  for" is in `tools/data/banned_phrases.txt`, but the gate matches **literally**,
  so the inflected form passes it. The replacement is the chapter's own idiom for
  this exact idea, used twice elsewhere ("goes looking for the clock"). A
  book-wide sweep for inflected forms found only three others, all in chapter 19
  and all the literal sense (a task trying to acquire a lock).
- **Before the quoted pytest failure.** "Change the expected value ... and the
  report names the line" → "If you change the expected value ..., the report
  names the line" (imperative-plus-consequence).

---

## 12_Data_Classes_as_Types

**Annealed clean.** Nothing cleared the bar across 1,533 lines.

---

## 13_Pattern_Matching

**Annealed clean.**

---

## 14_Decorators

**Annealed clean.**

---

## 15_Context_Managers

**Verified clean:** `utils/exceptions.py` annotates `types: Types | ALL = ALL`,
naming the specific sentinel value rather than the generic `sentinel` class,
which is what `CLAUDE.md`'s narrowing trap requires; the prose explaining that
narrowing is correct.

**Applied:**

- **After `nullcontext_demo.py`.** "the `nullcontext` wrapper is what lets one
  `with` block serve both cases" → "the `nullcontext` wrapper lets one `with`
  block serve both cases." Cleft with the verb right behind it.

---

## 16_Comprehensions

**Annealed clean.** The note that `filter()` narrows only with a named
`TypeIs[int]` predicate matches the `ty` behavior recorded in `CLAUDE.md`.

---

## Verification

`make reflow` on 01 through 16 (one paragraph rewrapped in 02 and one in 07, both
from the edits), `heading_links.py` → "Anchor links OK", `banned_phrases.py` →
"No banned phrases found".
The one code-block edit (06) was re-extracted and re-validated against a real run.
`heading_links.py` → "Anchor links OK", `banned_phrases.py` → "No banned phrases
found".
No fenced ```python block and no `#:` marker was touched in any of the three, so
the example tree is unaffected.

---

## 19_Concurrency

**Applied:**

- **Cancellation cleanup.** "If a task must clean up on the way out" → "as it
  stops". "the way out" is on the don't-use list, and the replacement names what
  is actually happening.
- **`pool.map()`, note 3.** "The `list(...)` around the call is what turns a
  failure ... into an exception here" → "turns a failure ...". A cleft with the
  verb right behind it.
- **`async_deadlock.py` commentary.** Three uses of "reaches for" became "tries
  to acquire" / "asks for", matching the section's own vocabulary ("acquire
  shared locks in the same global order" four paragraphs below).
- **Barriers bullet.** "a rendezvous point the running code reaches and blocks on
  itself" → "that the running code reaches and blocks at". The original read as
  code blocking on itself.

---

## 20_Rethinking_Objects

**Applied:**

- **LSP definition.** "An override may accept more than the base does but never
  less, returns a result ..., and raises ..." split into two sentences. The modal
  in the first clause did not carry into the two indicative ones, so the list
  read as broken parallelism.
- **`NewType` section.** "A caller who passes a raw `int` ... raises no
  exception" → "Passing a raw `int` ... raises no exception." A caller does not
  raise; the call does.
- **Exercise 2.** "`hash(immutable)` now raises" → "raises a `TypeError`."
  Objectless "raises"; `frozen_leaky.py` names the type two sections earlier.

---

## 21_The_Pattern_Concept

**Annealed clean.**

---

## 22_Data_Transfer_Objects

**Applied:**

- **`SimpleNamespace` intro.** "attributes that land in the instance's
  `__dict__`" → "attributes in the instance's `__dict__`". "land" is on the
  don't-use list and the sentence loses nothing.

**Declined:** "become a dict on the way out" (Which Should You Use?) stays. There
the phrase is directional and literal, and every replacement read worse.

---

## 23_Iterators

**Applied:**

- **The Costs of Laziness, opening.** "Two of those consequences are surprising"
  → "Laziness has two surprising consequences". "those consequences" had no
  antecedent noun; the section heading was carrying the reference.
- **Exercise 10.** "`typed()` raises on the first item of the wrong type" →
  "raises a `TypeError` on the first item".

---

## 24_Singleton, 25_Template_Method, 26_Surrogate

**Annealed clean.** In 25 and 26, "hook" is a defined term (an optional step, and
`__getattr__`'s fallback), so it stays; the casual uses elsewhere in the book did
not.

---

## 27_Factory

**Applied:**

- **`games2.py` commentary.** "`BrokenFactory` is the near-miss. It supplies
  `make_character()` and forgets ..." merged into one sentence. "near-miss" is on
  the don't-use list, and the sentence it opened only restated the next one.
- **Abstract Factory commentary.** "no hook for varying the rules of play" → "no
  place to vary the rules of play".

---

## 28_Function_Objects

**Applied:**

- **Chain of Responsibility.** "not quite the same as landing on a root" →
  "reaching a root".
- **`test_event_bus.py`** (code block). `# Must not raise` → `# Must not raise
  anything`, an objectless "raise" in a comment. Re-synced and re-run.

---

## 29_Changing_the_Interface

**Annealed clean.**

---

## 30_Observer

**Applied:**

- **`test_observers.py`** (code block). The same `# Must not raise` → `# Must not
  raise anything`, so the two listings stay consistent. Re-synced and re-run.

---

## 31_State_Machines

**Applied:**

- **After `mouse_trap2.py`.** "`next()` raises `from None` rather than chaining"
  → "raises its `RuntimeError` `from None`". The object was missing.
- **The engine's exact-type lookup.** "define a further subclass of an event type
  and it matches none of its parent's rows" → "if you define a further subclass
  ..., it matches none". Imperative-plus-consequence.

---

## 32_Multiple_Dispatching

**Applied:**

- **`double_dispatch` image alt text.** "landing execution inside
  `Paper.eval_scissors()`" → "putting execution inside".
- **Following the duel.** "landing in `Paper.eval_scissors()`" → "arriving in".

---

## 33_Visitor

**Applied:**

- **Two uses of "the `accept()` hook"** → "the `accept()` method". `accept()` is
  required rather than optional, so "method" is both plainer and more accurate.

---

## 34_Composite_and_Interpreter

**Applied:**

- **After `infix.py`.** "needs no `accept()` hook" → "needs no `accept()`
  method", matching chapter 33.
- **Exercise 9.** "A plugin package wants to add its own entry types" → "needs to
  add". A package is not an agent.

---

## 35_Flyweight

**Applied:**

- **After `tile_enum.py`.** "Name, symbol, and attribute access all land on the
  same shared member" → "all reach the same shared member".

---

## 36_Memento

**Applied:**

- **The caretaker's restraint.** "an honest mistake (swapping the snapshot's
  strokes ...)" → "an accidental edit", which is what the parenthetical
  describes.
- **Pickle drift setup.** "keeps the simulation honest" → "keeps the simulation
  faithful".
- **Drift in the other direction.** "Delete a field and the old bytes load with
  no error anywhere" → "If you delete a field, ...". Imperative-plus-consequence.
- Same paragraph: "never raises an exception at all" → "never raises an
  exception".

---

## 37_Pattern_Refactoring, 38_Simulation, 39_Pattern_Catalog

**Annealed clean.** 39's completed review carries an `[X] Reject` on adding a
conclusion or exercises to it, so that was left alone.

---

## 40_Functional_Foundations

**Applied:**

- **Pure Functions.** "That is what makes `functools.cache` safe" → "That makes
  `functools.cache` safe". A cleft with the verb behind it.
- **Immutability.** "`frozen=True` is what lets a dataclass keep ..." →
  "`frozen=True` lets a dataclass keep ...". Same construction.
- **Closures.** "Delete the `nonlocal` line and `ty` reports ..." → "If you
  delete the `nonlocal` line, `ty` reports ...", and "before the program runs at
  all" → "before the program runs".
- **Closing sentence.** "that single property is what the chapters ahead build
  on" → "the chapters ahead build on that single property", which also removes a
  stranded preposition.

---

## 41_Functional_Toolkits

**Applied:**

- **`wraps`.** "Delete the `@wraps(func)` line and that same `print()` reports
  ..." → "If you delete the `@wraps(func)` line, ...".
- **`islice`.** "give it an iterator rather than a list, and that iterator
  resumes ..." → "if you give it an iterator rather than a list, that iterator
  resumes ...".
- **`singledispatchmethod`.** "exactly as the plain function above does" → "the
  same way the plain function above does". "exactly" as an intensifier.
- **Lazy Evaluation.** "Slice lazily and the source can be infinite; slice a list
  and the source has to end" → "Slicing lazily lets the source be infinite;
  slicing a list requires a source that ends." Two imperative-plus-consequence
  clauses in one sentence; the gerund form reads better than two conditionals.

---

## 42_Functional_Error_Handling

**Applied:**

- **`@safe`'s breadth.** "Misspell a name inside the wrapped function and the
  resulting `NameError` arrives as an ordinary `Err`" → "If you misspell a name
  ...".

---

## 43_Functional_Assurance

**Applied:**

- **An Assurance Spectrum.** "Functional programming's honest answer" →
  "Functional programming's answer".
- **The property-shape family.** "which is exactly what `parallel_pure.py`'s
  assert already claimed" → "which is what ... already claimed".
- **Shrinking.** "a real test wants neither" → "needs neither".
- **Two caveats.** "Two caveats keep this honest" → "Two caveats keep the claim
  from overreaching", which also says what the caveats do.

---

## 44_Effect_Management

**Applied:**

- **Effect Management Systems.** "and it is what makes code hard to understand" →
  "and it makes code hard to understand".
- **AI languages.** "a host that pins the implementations itself can guarantee
  ..." → "a host that pins the implementations can guarantee ...". The "itself"
  could attach to either noun and changed nothing.

---

## 45_Generators

**Applied:**

- **Running to Exhaustion.** "The `from` is what makes this delegation" → "The
  `from` makes this delegation".
- **All Three Channels.** "arrives as the value of the `yield` expression and
  lands in `answer`" → "and is bound to `answer`".
- **Composing Is Not Interpreting.** "Stack delegations as deep as you like and
  the number of drivers stays at one" → "However deep you stack delegations, the
  number of drivers stays at one."

---

## 46_Stateless

**Verified clean:** the `type`-alias warning in Retrofitting an Effect matches
the `ty` behavior recorded in `CLAUDE.md`, and the spelled-out unions elsewhere
are deliberate, so no Effect signature was "cleaned up" into an alias.

**Applied:**

- **Emptying the Channels, item 3.** "An Ability the driver answers itself needs
  no vocabulary at all" → "An Ability that the driver answers on its own needs no
  vocabulary." The original read as the Ability answering itself.
- **Declaring Is Not Handling.** "so the inner `except` never runs at all" → "so
  the inner `except` never runs."

---

## 47_Stateless_in_Practice

**Applied:**

- **Abilities Are Not Special.** "the type bound is what makes that more than a
  convention" → "the type bound makes that more than a convention".
- Same section: "Leave the annotation off and `handle()` raises a `ValueError`" →
  "If you leave the annotation off, `handle()` raises a `ValueError`".
- **The scripted-handler trap.** "Ask `count_heads()` for six tosses ... and
  `run()` produces `None`" → "Asking `count_heads()` for six tosses ... makes
  `run()` produce `None`".
- **Running Effects in Parallel.** "Fork and wait inside a single loop and each
  `wait()` blocks ..." → "Forking and waiting inside a single loop makes each
  `wait()` block ...".
- **Exercise 14.** "where a cast is wanted" → "where a cast is expected".

---

## 06_Modules_and_Packages (revisited)

The previous pass moved `#: initializing a_package` up to hug its `import` in
`package_only.py`, which left `make verify` red: ruff's `I001` wants a blank line
after an import block, and the marker was sitting inside one. Both neighboring
listings (`using_packages.py`, `from_packages.py`) already put a blank line after
their imports and the markers below it, so `package_only.py` now matches them.
The marker still sits directly above the code it belongs to.

---

## Verification (chapters 19-47)

`make reflow` on every touched chapter (five paragraphs rewrapped, in 31, 40, 41,
42 and 47), then a green `make verify`: markers refreshed, tree synced,
`heading_links.py` OK, `banned_phrases.py` clean, `ty` and `ruff` clean over
`build/examples`, 256 tests passing, and every runnable example executed.

No `#:` output marker changed value anywhere in `git diff`, so no timing boolean
flipped. The only code touched was two test comments (28 and 30) and the blank
line in 06; all three are re-synced into `Examples/`.
