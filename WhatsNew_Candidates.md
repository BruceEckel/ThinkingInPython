# "What's New" Candidates for the Book

A pass through the CPython "What's New" pages from 3.15 back to 3.0,
filtered against what `Chapters/` already covers.
Each entry says what the feature is, where it would go, and how it would earn its place.

This document lists only recommendations.
Features that are out of scope (tooling, platform support, niche stdlib corners)
and features the book already covers adequately have been removed,
so an empty-looking release means that release had nothing worth acting on,
not that it went unread.
An entry survives when it carries an action, including "verify this" and "update this."

3.15 is a different kind of section from the rest.
It is the book's pinned target (`requires-python = ">=3.15"`),
so its features are the baseline rather than a compatibility question.
It is also still in development, so its "What's New" page will grow before release.

Verdicts:

- **Add** means a real gap in material the book already claims to teach.
- **Consider** means it would improve a chapter but nothing is currently wrong.
- **Mention** means one sentence or a footnote, not a section or a listing.

Coverage claims come from grepping `Chapters/`.
A "not covered" note means the term appears nowhere in the book's prose or listings.

---

## Top picks


---

## Python 3.15

The book's target version, so everything here is available to every listing without qualification.
`frozendict`, lazy imports, comprehension unpacking, `sentinel`, and the `profiling` package
are all in use in the book already and are not repeated below.

- **`threading.synchronized_iterator()`, `serialize_iterator()`, and `concurrent_tee()`.** **Add.**
  Not covered.
  Iterators have never been thread-safe, and the standard advice was a hand-rolled lock
  wrapper that most people get wrong.
  `synchronized_iterator()` wraps one so concurrent `next()` calls are serialized,
  and `concurrent_tee()` is the thread-safe `itertools.tee()`.
  Chapter 23 teaches iterators, chapter 45 teaches generators, and chapter 19 teaches
  threads; the intersection currently has no answer.
  Chapter 19 is the natural home, with a pointer from 23 or 45.
- **`functools.singledispatchmethod()` dispatching on the second argument.** **Add** to chapter 32.
  Not covered.
  Chapter 32 is Multiple Dispatching, and its whole subject is that Python dispatches on
  one argument.
  Being able to dispatch a method on its second argument changes what the chapter can build,
  and the chapter should at minimum say the limitation moved rather than disappeared.
  The same change lets `singledispatchmethod()` wrap non-descriptor callables.
- **`contextlib.ContextDecorator` keeping the context open across iteration and `await`.**
  **Add** to chapter 15, and cross-reference from 14.
  Both chapters cover `ContextDecorator`.
  Before 3.15, decorating a generator function with a context manager closed the context
  when the generator first yielded, which is a subtle bug with no visible symptom until
  the resource was needed later.
  The fix is worth stating because the old behavior explains code readers will still meet.
- **`TypeForm[T]` (PEP 747).** **Consider** for chapter 8.
  Not covered.
  It types a parameter that receives a type expression rather than an instance,
  which is the signature of every runtime-validation or conversion helper the book writes.
  Chapter 8 already distinguishes `type[C]` from a type expression; `TypeForm` is the annotation
  for the second one.
- **Closed `TypedDict` with `closed=` and `extra_items=` (PEP 728).** **Consider** for chapter 8,
  next to the existing `Required`/`NotRequired`/`ReadOnly` material.
  A closed `TypedDict` rejects unknown keys, which is what most people assume the default does.
- **`asyncio.TaskGroup.cancel()`.** **Consider** for chapter 19.
  Cancelling a whole group from outside was previously awkward,
  and the chapter's structured-concurrency argument is stronger with it.
- **`@disjoint_base` (PEP 800).** **Mention** in chapter 17 or 8.
  It tells a type checker that two classes cannot have a common subclass,
  which is what makes exhaustive narrowing work on class hierarchies.
- **`math.integer` (PEP 791).** **Mention.**
  The integer-only functions (`gcd`, `lcm`, `isqrt`, `comb`, `perm`, `factorial`) now live
  in one namespace.
  Worth a clause anywhere the book uses one of them, since the old `math` names still work.
- **`Counter.__xor__()` for symmetric difference.** **Mention** in chapter 3,
  which already teaches `Counter` and set operations.
- **`re.prefixmatch()`, with `re.match()` soft deprecated.** **Mention.**
  The rename exists because `re.match()` matching only at the start surprises everyone,
  and the confusion with the `match` statement makes the old name worse.
  One sentence wherever regular expressions appear.
- **`__slots__` relaxations: `__dict__` and `__weakref__` allowed in any class,
  and any `__slots__` on `tuple` subclasses.** **Mention** in chapter 18,
  where `slots=True` is discussed, or chapter 9.
- **`slice` is now subscriptable as a generic type.** **Mention** in chapter 8 or 23 if
  a slice-taking signature comes up.
- **UTF-8 as the default encoding (PEP 686).** **Mention** in chapter 6 or 11.
  `open()` no longer depends on the system locale, which removes a class of
  works-on-my-machine failures that older code guards against with explicit `encoding=`.
  The book should say whether to keep writing `encoding="utf-8"` anyway.
- **`timeit --target-time`.** **Mention** in chapter 18 if any benchmark listing tunes its run count.
- **JIT improvements and the tail-calling interpreter on 64-bit Windows.** **Mention** in
  chapter 18 as a measurement caveat.
  The book's numbers are produced on Windows, so this changes the baseline.
- **`sys.monitoring` per-code-object control and `DISABLE`.** Fold into the 3.12 `sys.monitoring`
  item rather than treating it separately.
  If that item is adopted, write it against the 3.15 API.

One task rather than a candidate:
**3.15 removes a batch of long-deprecated APIs** across `ast`, `collections.abc`, `ctypes`,
`datetime`, `glob`, `http.server`, `importlib.resources`, `pathlib`, `platform`,
`sysconfig`, `threading`, `types`, `typing`, and `zipimport`,
and `importlib.metadata` now raises `MetadataNotFound` where it used to be quieter.
The gates run on 3.15, so anything the book uses would already fail,
but prose that names a removed function would not.
Worth one grep pass over `Chapters/` against the removal list before release.

## Python 3.14

The release with the most that the book has no equivalent for.

- **Template strings, PEP 750** (`t"..."`, `string.templatelib.Template`). **Add.**
  A `t`-string evaluates to a `Template` holding the literal parts and the
  `Interpolation` objects separately, so the consumer decides how each value is rendered.
  Two placements, and they reinforce each other:
  a short introduction beside f-strings early (chapter 2 or 3),
  then a real use in chapter 34, where the Interpreter pattern already builds structure from text.
  It also gives chapter 29 a clean example of changing an interface without changing the call site.
- **PEP 649 and 749 deferred annotations plus `annotationlib`.** **Add** the introspection half.
  The book already relies on PEP 649 semantics (project memory records this),
  but `annotationlib.get_annotations()` and its three formats
  (`VALUE`, `FORWARDREF`, `STRING`) appear nowhere.
  Chapter 17 reads annotations at runtime and should use the supported API rather than
  poking at `__annotations__`.
- **`functools.Placeholder` for `partial()`.** **Add.**
  `partial(f, Placeholder, 3)` fixes the second argument and leaves the first open.
  Chapter 28 (Function Objects) and chapter 41 (Functional Toolkits) both discuss partial
  application; without `Placeholder` the only honest statement is "you can bind leading
  arguments," which is no longer true.
- **`concurrent.interpreters`, PEP 734.** **Consider.**
  Chapter 19 mentions `InterpreterPoolExecutor` once.
  The underlying module is now the third real concurrency model in the stdlib,
  alongside threads and processes, and the chapter's comparison table is incomplete without it.
  A short section contrasting its isolation with a process pool's cost would fit the existing structure.
  The 3.12 per-interpreter GIL (PEP 684) is the groundwork for this and belongs in the same passage.
- **`map(strict=True)`.** **Consider**, paired with `zip(strict=)` from 3.10 (below).
  Teaching both together in chapter 16 makes the point once: silent truncation is a bug source.
- **PEP 765: `SyntaxWarning` for `return`/`break`/`continue` leaving a `finally`.** **Consider.**
  This is a genuine trap with a now-visible warning, and chapter 15 or chapter 4 is the place to name it.
  Worth a short listing showing the swallowed exception.
- **`functools.reduce(initial=...)` keyword.** **Mention** in chapter 41, next to `reduce()`.
- **`operator.is_none()` and `is_not_none()`.** **Mention** in chapter 41.
  They exist so a filter predicate need not be a lambda, which is a point that chapter already makes.
- **PEP 758: `except A, B:` without brackets.** **Mention** in chapter 4.
  One sentence, since a reader will see both forms in the wild.
- **`pathlib.Path.copy()`, `copy_into()`, `move()`, `move_into()`, and `Path.info`.** **Mention.**
  The book uses `pathlib` in eight chapters; a reader who would otherwise use `shutil`
  should know these exist.
- **Free-threaded mode with the adaptive specializer enabled.** **Mention** in chapter 18.
  It changes the single-threaded baseline, which matters to the chapter's measurements.

## Python 3.13

- **PEP 696, type parameter defaults.** **Add** to chapter 8.
  `class Box[T = int]` and the `type` alias form both matter for library-facing generics,
  and chapter 8 already enumerates every other type-parameter kind.
- **`warnings.deprecated()`, PEP 702.** **Add** to chapter 29.
  One decorator marks a function, class, or overload as deprecated for a type checker
  and optionally at runtime.
  Chapter 29's whole subject is evolving an interface without breaking callers.
- **`copy.replace()` and the `__replace__()` protocol.** **Add.**
  Chapter 12 teaches frozen dataclasses and currently points at `dataclasses.replace()`.
  `copy.replace()` is the generic version, works on `namedtuple`, `datetime`,
  `SimpleNamespace`, and anything defining `__replace__()`, and is the natural
  operation for chapter 36's Memento (restore with one field changed).
  Defining `__replace__()` on a custom immutable class is a good short exercise.
- **Free threading, PEP 703.** Covered in chapter 19, but **update** the status:
  3.13 was experimental, and 3.14 made it officially supported (PEP 779).
- **PEP 667, `locals()` returns an independent snapshot.** **Consider** for chapter 17.
  The old behavior (mutating the dict sometimes worked, sometimes not) was a classic
  source of confusion, and the new rule is short enough to state precisely.
  `FrameType.f_locals` now gives a write-through proxy, which is the supported way to do it.
- **`typing.is_protocol()` and `get_protocol_members()`.** **Consider** for chapter 17.
  Chapter 21 uses `Protocol` heavily; introspecting one at runtime currently has no shown API.
- **`ReadOnly` for `TypedDict`, PEP 705.** **Consider** for chapter 8,
  beside the existing `Required`/`NotRequired` material.
- **The new REPL** (multiline editing, history, paste mode, color). **Mention** in chapter 1 or 2
  if you describe the interactive interpreter at all.
  It changes what a reader sees on first launch.

## Python 3.12

- **PEP 692, `Unpack[TypedDict]` for `**kwargs`.** **Add** to chapter 8 or 14.
  Not covered.
  It is the only way to type a `**kwargs` forwarding wrapper precisely,
  which is a problem chapter 14's decorators run into directly.
- **PEP 669, `sys.monitoring`.** **Add** to chapter 18, or chapter 17 if you prefer the
  introspection angle.
  The book measures with timers; this is the mechanism profilers use, with near-zero cost
  when no callback is registered.
  A small listing that counts calls to one function without touching its source would sit well
  next to the decorator material.
  Write it against the 3.15 API, which adds per-code-object control.
- **PEP 709, comprehension inlining.** **Mention** in chapter 16.
  Comprehensions no longer create a separate frame, which is roughly a 2x speedup
  and also explains why a comprehension's scope behavior changed.
  Chapter 16 makes performance claims and this is the current mechanism behind them.
- **PEP 701, f-string formalization.** **Mention** in chapter 2 or 3.
  Quote reuse (`f"{d["key"]}"`), backslashes, and multi-line expressions are all legal now.
  Worth one sentence because the old restrictions still shape how people write f-strings.
- **PEP 695 type parameter syntax.** Used throughout the book already.
  **Mention** in chapter 8 that the older `TypeVar` form is what a reader will meet
  in existing code.
- **`types.get_original_bases()`.** **Mention** in chapter 17 if generic introspection comes up.

## Python 3.11

- **PEP 678, `BaseException.add_note()`.** **Add.**
  Not covered anywhere.
  Best placement is chapter 42, which argues about carrying error information through a
  computation; `add_note()` is the answer for the exception-based half of that argument.
  Chapter 10 is a second option.
- **`asyncio.timeout()`.** **Add** to chapter 19. Not covered.
  It replaces `wait_for()` for most uses and composes as a context manager,
  which fits the chapter's structured-concurrency framing.
- **PEP 654, exception groups and `except*`.** Partially covered
  (`ExceptionGroup` in chapter 30, `except*` in chapter 19).
  **Consider** giving it a proper introduction in one place rather than two partial ones,
  since `TaskGroup` is the reason most readers meet it,
  and the "one handler runs per matching type, and may run more than once" rule is not obvious.
- **`contextlib.chdir()`.** **Consider** for chapter 15.
  A short, real context manager from the stdlib, useful as a contrast with a hand-written one.
- **PEP 681, `@dataclass_transform`.** **Consider** for chapter 17.
  This is how a decorator or metaclass tells a type checker "instances of this behave like a
  dataclass," and chapter 17 builds that kind of machinery.
  It is advanced, so a footnote-scale treatment may be right.
- **`enum` additions: `verify()`, `member()`, `nonmember()`, `ReprEnum`, `enum.property`.**
  **Consider** `verify()` (catching duplicate or non-contiguous values) and
  `nonmember()` (the fix for "my constant became an enum member by accident"),
  both of which prevent real mistakes.
  `StrEnum` is already used in three chapters.
- **PEP 657, fine-grained error locations.** **Mention** in chapter 1 or 2.
  The caret now points at the failing sub-expression, which changes how a reader debugs.
  Pair it with the 3.10/3.12/3.13/3.14 error-message improvements as one short passage
  rather than five separate notes.
- **`asyncio.Runner` and `asyncio.Barrier`.** **Mention** in chapter 19.
- **`operator.call()`.** **Mention** in chapter 41.

## Python 3.10

- **PEP 618, `zip(strict=True)`.** **Add** to chapter 16 or 3.
  Not covered.
  Silent truncation when zipping unequal sequences is a bug the book should name,
  and teaching it with `map(strict=)` from 3.14 makes one lesson instead of two.
- **Parenthesized context managers.** **Consider** for chapter 15.
  Multi-line `with (A() as a, B() as b):` is the readable form for several managers,
  and the chapter shows `ExitStack` for the dynamic case already.
  Fold in the 3.1 change that allowed several managers in one `with` at all.
- **`dataclasses`: `slots=True`, `KW_ONLY`, keyword-only fields.**
  `kw_only` and `KW_ONLY` appear in chapter 12, `slots=True` in chapter 18.
  **Consider** consolidating: chapter 12 is where a reader decides which options to use,
  and project memory already records the frozen-plus-slots interaction.
- **PEP 613, `TypeAlias`.** Superseded by PEP 695 `type`.
  **Mention** only as history, since older code uses it.
- **`contextlib.aclosing()` and `AsyncContextDecorator`.** **Mention** in chapter 15
  if async context managers get more than a passing treatment.

## Python 3.9

- **PEP 584, `dict | dict` and `|=`.** **Add** to chapter 3. Not covered.
  Chapter 3 teaches dictionaries and should show the merge operator next to `update()`,
  including the "right side wins" rule and the fact that `|` produces a new dict
  while `|=` mutates.
- **PEP 616, `str.removeprefix()` and `removesuffix()`.** **Add** to chapter 3.
  Not covered.
  Small, but they replace the `if s.startswith(p): s = s[len(p):]` idiom that is easy to
  get subtly wrong, and the book uses string manipulation in several listings.
- **PEP 614, relaxed decorator grammar.** **Consider** for chapter 14.
  Any expression can now be a decorator, so `@handlers[name]` and `@config.decorator`
  are legal.
  This matters to chapter 14's registry examples.
- **`graphlib.TopologicalSorter`.** **Consider** for chapter 34 or 38.
  Not covered.
  Dependency ordering is a real problem and the stdlib solution is unknown to most readers.
  It would give the Composite chapter a non-toy task, or the Simulation chapter a scheduler.
- **`ast.unparse()`.** **Mention** in chapter 17 if the metaprogramming chapter builds or
  inspects an AST; it makes generated code printable.

## Python 3.8

- **f-string `=` specifier (`f"{value=}"`).** **Add.** Not covered.
  This is the fastest debugging idiom in Python and belongs in chapter 2, chapter 11,
  or both.
  One line replaces `print("value:", value)`.
- **`unittest.IsolatedAsyncioTestCase` and `AsyncMock`.** **Consider** for chapter 11.
  The chapter introduces `unittest` before moving to `pytest`,
  so a sentence on testing coroutines fits the `unittest` half;
  the `pytest` equivalent is `pytest-asyncio`, which is a dependency, not a language feature.
- **`itertools.accumulate(initial=)`.** **Mention** in chapter 41 next to the existing
  `accumulate()` material.
- **Reversed dict iteration (`reversed(d)`).** **Mention** in chapter 3.
- **`math.isqrt()`, `comb()`, `perm()`, `dist()`.** **Mention** in chapter 41 if a numeric
  example needs one. `math.prod()` already appears once.

## Python 3.7

- **`contextvars` (PEP 567).** **Add.** The largest single gap found in this pass.
  Not covered anywhere.
  A `ContextVar` is state that follows a logical call chain, including across `await`,
  without threading a parameter through every function.
  It belongs in chapter 19 as the async-correct alternative to `threading.local`,
  and it should be referenced from Part V, where "how does context get to the effect handler"
  is the recurring question.
  The 3.14 addition of the `Token` context manager protocol makes reset-on-exit clean,
  so the example can be short.
- **Module `__getattr__()` and `__dir__()` (PEP 562).** **Add** to chapter 6.
  Not covered.
  This is how a package deprecates a name, lazily imports a submodule, or presents a
  curated public surface.
  Chapter 6 is about modules and packages and currently has no answer to "how do I make
  `mypkg.Thing` work without importing it eagerly."
  It also connects to chapter 29's interface-evolution theme.
- **`__class_getitem__()` (PEP 560).** **Consider** for chapter 17.
  Not covered.
  It explains how `list[int]` works at all, and how a custom class becomes subscriptable
  without a metaclass, which is a question chapter 17 is positioned to answer.
- **Dict insertion order guaranteed.** **Mention** in chapter 3, with the 3.6/3.7 history,
  because it explains why `OrderedDict` still exists and when you would still use it
  (equality that respects order, `move_to_end()`).
- **PEP 563, postponed annotation evaluation (`from __future__ import annotations`).**
  **Mention** as history in chapter 8 or 17.
  Readers will see the future import in existing code and should know PEP 649 replaced it,
  and that the future import is not needed on the book's target version.
- **`breakpoint()` (PEP 553).** **Mention** in chapter 11 or 18.
  One sentence, since `sys.breakpointhook()` makes it configurable.
- **`time.*_ns()` functions.** **Mention** in chapter 18 if timing precision matters
  to a benchmark listing.

## Python 3.6

- **PEP 525 and 530, async generators and async comprehensions.** **Consider** for
  chapter 45 or 19, depending on where async iteration is taught.
  Chapter 45 is a generators chapter, and async generators are the piece most readers
  never learn.
- **PEP 519, `os.PathLike` and `__fspath__()`.** **Consider** for chapter 29 or 7.
  Not covered.
  It is a compact, real example of retrofitting a protocol onto a type so existing
  functions accept it, which is chapter 29's subject stated in one dunder.
- **`enum.Flag` and `IntFlag`.** **Consider** where bit-set state comes up,
  such as chapter 31's state machines.
- **PEP 515, underscores in numeric literals (`1_000_000`).** **Mention** in chapter 2 or 3.
  Trivial to teach and it improves several existing listings that use large constants.
- **PEP 520, class attribute definition order.** **Mention** in chapter 17.
  It is why a metaclass or `__init_subclass__` can see fields in source order,
  which several patterns depend on.
- **f-strings (PEP 498).** Used everywhere, but the term "f-string" appears in only two chapters.
  **Verify** that whichever chapter introduces string formatting names it.

## Python 3.5

- **PEP 479, `StopIteration` inside a generator becomes `RuntimeError`.** **Add a cross-reference.**
  Chapter 23 names PEP 479; chapter 45 (Generators) does not,
  and it is the generator chapter where the rule matters most.
  A reader who writes `next(it)` inside a generator body needs this.
- **`math.isclose()` (PEP 485).** **Add** to chapter 11.
  Not covered.
  Comparing floats with `==` in a test is a standard mistake and the stdlib has the fix.
- **PEP 465, the `@` matrix multiplication operator.** **Consider** for chapter 7.
  Not covered.
  It is the clearest case study in the language for "when does a new operator deserve to
  exist," and it gives the operator-overloading discussion a real answer to
  "which operators can I define?"
  `__matmul__` and `__rmatmul__` are also a fine exercise for reflected operations,
  a thread project memory notes runs across chapters.
- **PEP 448, additional unpacking generalizations
  (`[*a, *b]`, `{**d1, **d2}`, multiple `*args` in a call).** **Consider** for chapter 5 or 3.
  Partially implied by existing listings but not taught directly.
  `{**d1, **d2}` also pairs with the 3.9 `|` merge operator: same result, different history.
- **PEP 484, type hints and the `typing` module.** Covered in chapter 8.
  **Mention** the history: annotations existed from 3.0 (PEP 3107) with no meaning,
  and 3.5 gave them one.
  That is a good framing sentence for chapter 8's opening.

## Python 3.4

- **`contextlib.redirect_stdout()`.** **Consider** for chapter 11 or 15.
  Not covered, though `suppress()` from the same release is covered in four chapters.
  Capturing output is a real testing need and a compact context-manager example.
- **`tracemalloc` (PEP 454).** **Consider** for chapter 18, which measures performance.
  It answers "where did the memory go" the way timers answer "where did the time go."
- **`min()`/`max()` with `default=`.** **Mention** in chapter 5 or 16.
  Not covered.
  It removes a `try`/`except ValueError` around an empty-sequence case,
  which fits the book's preference for expressing intent directly.
- **`functools.partialmethod()`.** **Mention** in chapter 28 beside `partial`.
- **`functools.singledispatch()` (PEP 443).** Covered in eight chapters.
  **Mention** in chapter 32 or 41 that it arrived in 3.4 and the method form
  (`singledispatchmethod`) only in 3.8.

## Python 3.3

- **`raise ... from None` (PEP 409).** Chapter 4 mentions it.
  **Consider** expanding wherever exception chaining is taught,
  since `__cause__` versus `__context__` is a distinction most readers never learn
  and it changes what a traceback says.
  Fold in the 3.0 origin of chaining (PEP 3134) so it is one passage.
- **`collections.ChainMap`.** **Consider** for chapter 3 or 17.
  Not covered.
  It is the data structure that models scope lookup, so it pairs well with any discussion
  of name resolution, and it is a better answer than merging dicts when the layers must stay separate.
- **`__qualname__` (PEP 3155).** **Consider** for chapter 17.
  Not covered.
  Decorators and registries that key on a function's name usually need the qualified one.
- **PEP 3151, the `OSError` exception hierarchy.** **Consider** a short note wherever
  exception handling is taught.
  Catching `FileNotFoundError` rather than checking `errno` is the modern form
  and readers still write the old one.
- **`unittest.mock`.** **Consider** for chapter 11 if mocking is discussed at all.
- **Implicit namespace packages (PEP 420).** Chapter 6 mentions namespace packages.
  **Verify** it says why they exist and what goes wrong when a directory silently becomes one,
  which is a common confusion.
- **`inspect.signature()` (PEP 362).** **Verify** coverage.
  Chapters 14 and 17 both benefit from it, and it is the supported alternative to
  reading `__code__` attributes.

## Python 3.2

- **`@functools.total_ordering`.** **Consider** giving it a real place in chapter 7 or 12.
  It appears in only one chapter, and defining `__eq__` and `__lt__` to get the rest
  is a decision readers face.
- **`str.format_map()`.** **Mention** if t-strings or formatting get a section;
  it is the mechanism that makes a custom mapping drive `format()`.
- **`abc.abstractclassmethod` and `abstractstaticmethod`.** **Mention** one clause
  if the book shows abstract classes.
  Both are deprecated in favor of stacking `@classmethod` with `@abstractmethod`,
  but the deprecated forms still appear in older code.

## Python 3.1

- **`collections.OrderedDict` (PEP 372).** **Mention** with the 3.7 dict-ordering item.
  The interesting question now is when it is still the right choice.
- **Thousands separator in format specs (PEP 378, `f"{n:,}"`).** **Mention** in chapter 2 or 3.
  3.14 extended separators to the fractional part, so the two notes can be one.

## Python 3.0

Almost everything here is simply Python now, and the Python 2 comparison would only date the text.
The value is historical framing on three items:

- **Function annotations (PEP 3107).** They arrived in 3.0 with no defined meaning
  and got one in 3.5 (PEP 484), then lazy evaluation in 3.14 (PEP 649).
  That arc is a good opening for chapter 8:
  the syntax was deliberately left undefined for seven years.
- **Exception chaining (PEP 3134, `raise ... from`, `__cause__`, `__context__`).**
  See the 3.3 `raise ... from None` item; these belong in one passage.
- **Extended unpacking (PEP 3132, `a, *rest, b`).** **Verify** it is shown somewhere.
  Chapter 5 covers keyword-only parameters (PEP 3102) already,
  and extended unpacking is used casually in modern code.

---

## One structural suggestion

Several of these items are historical rather than instructional:
when annotations got meaning, why `OrderedDict` still exists, why `TypeAlias` gave way to `type`,
why the future import for annotations is no longer needed.
Scattering them through chapters adds noise to each one.

An alternative is a short appendix, roughly "How Python Got Here,"
tracing the features the book depends on back to the release that introduced them.
It would give you one place for the version-history sentences,
let each chapter stay focused on the current form,
and give a reader a map for the older code they will meet outside the book.
It also ages well: a new release adds a row rather than forcing edits in ten chapters.
