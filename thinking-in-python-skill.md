---
name: thinking-in-python
description: Write Python the "Thinking in Python" way. Modern Python 3.15+ idioms, precise static typing, dense readable listings, and disciplined design-pattern usage. Use when writing, reviewing, or refactoring Python code.
---

# Programming Python: The Thinking in Python Way

This skill distills the conventions developed while writing the book
*Thinking in Python*. Apply them to all Python you write, review, or
refactor. The style targets modern Python (3.15+) and assumes every
file passes a strict type checker and linter.

## Core stance

- Write modern Python. Use `match`, PEP 695 generics (`def f[T]`,
  `class C[T]`, `type Alias = ...`), dataclasses, protocols, and
  comprehensions where they fit.

- Every example must type-check and lint clean. Precision is not
  optional polish. It is part of correctness.

- Prefer composition, protocols, and functions over inheritance
  hierarchies. Subclass only when runtime dispatch through a shared
  base actually earns its keep.

- Keep code dense and direct. Cut scaffolding, null checks, and
  repeated demonstration.

## Static typing

**Prefer precise types over `Any`.**

- Use a `Protocol` for duck-typed conformance with no base class.
  Prefer it over both `Any` and ABCs.

- Use `type[C]` when a class object is passed or stored.

- Use type parameters (`def f[T](...)`, `class C[T]`) when a function
  or wrapper should carry the element type through.

- A generic type alias can confine unavoidable erasure: use
  `Handler[E]` in public signatures and `Handler[Any]` only for a
  heterogeneous store, so the `Any` is explicit and localized.

- The one legitimate `Any`: dynamic metaprogramming that adds or swaps
  attributes on class objects (metaclasses, class decorators). There,
  funnel through one `Any`-typed name (`klass: Any = cls`) rather than
  scattering `# type: ignore`. Escapes, narrowest first:
  `setattr(cls, "name", value)`, a localized `# type: ignore`, then
  `Any`.

**Pick the strongest construct that fits.**

- Closed set of constants with behavior attached: `Enum`/`StrEnum`,
  not `Literal[...]`. An enum carries identity and methods.

- A primitive standing in for a domain concept: a validated frozen
  dataclass (with a checking `__post_init__`), not `NewType`.
  `NewType` only satisfies the checker; the dataclass also enforces
  the invariant at runtime.

- `type X = ...` aliases are for compound shapes (tuples, dicts,
  callables, unions), never a bare scalar rename like
  `type Symbol = str`. The right side is lazily evaluated (PEP 695),
  so it can name a class defined later in the file without quotes.

- For a generator function whose yield type carries a guarantee you
  want verified, write the `Generator[...]` annotation out in full:
  the yield type is the information, and it stays visible at the
  point of use. Under `ty` 0.0.91 a `type` alias checks the same (a
  wrong `yield` draws `invalid-yield` through the alias), but confirm
  that with your own checker before aliasing such a signature.

**Constants.**

- Named constants get the full typed `Final` form:
  `TOLERANCE: Final[float] = 1e-12`. Not bare `Final`.

- Module-level lookup tables that act as constants are `UPPER_CASE`
  with `Final[...]`.

- Enum members are never annotated `Final` (it breaks the enum).

**Attribute declarations signal their nature.**

- Shared class constant: `symbol: ClassVar[str] = ""` on the base.
  Subclass overrides (`symbol = "R"`) do not repeat `ClassVar`.

- Per-instance state with a value from birth: assign in `__init__`
  (`self.finished = False`). Never leave it as a bare class-body
  assignment, which is shared state that reads like a dataclass field.

- Attribute set later by a builder or factory: a bare annotation with
  no value (`room: Room`). This stores nothing at runtime and keeps
  the type precise.

**Avoid `T | None = None` plus asserts.**

- Do not seed an attribute with `None` because its real value arrives
  later, then guard every use with `assert x is not None`. That is a
  Java-style null pattern.

- If a builder always sets it before anything reads it, use a bare
  annotation (`room: Room`).

- If `None` means "nothing there," use one shared null-object
  sentinel (`neighbors.get(urge, EDGE)`), not `None` checks.

**Use the `sentinel` builtin when a marker must be distinct from every
legal value** (PEP 661, Python 3.15+).

- `MISSING = sentinel("MISSING")` prints as `MISSING` in a repr or a
  traceback. A bare `object()` prints `<object object at 0x...>` and
  names nothing.

- Use it for a default that must detect absence (telling a missing key
  from a stored `None`), a `next(it, DONE)` probe, a not-yet-created
  placeholder, or a flag meaning "all of them."

- Keep `None` when it cannot collide with a legal value. `None` is
  still the right default for an ordinary optional, and a sentinel
  there is ceremony.

- Create each sentinel once and share that name. Two `sentinel("X")`
  calls build two unequal objects, even in one module, so an `is`
  check against a freshly made one silently fails.

- When a parameter takes either a sentinel or a real value, annotate
  the union with the specific sentinel value (`Sequence[str] | ALL`),
  never the generic `sentinel` class, so the checker narrows to the
  real type once the sentinel is ruled out.

**Annotations are lazy (PEP 649, Python 3.15+).**

- Forward references need no quotes and no
  `from __future__ import annotations`.

- Types imported only under `if TYPE_CHECKING:` are safe in any
  annotation, including bare class-body declarations. Use this to
  break import cycles.

**Two-way generators get the full three-parameter annotation.**

- `Iterator[T]` fits a generator that only produces values. One that
  also receives or returns gets
  `Generator[YieldType, SendType, ReturnType]`.

- When the channels share a base type (three `str`s), wrap each in a
  `NewType` (`Question`, `Answer`, `Result`) so a transposed
  annotation fails the checker instead of unifying silently.

- Prime with `next(g)`, not `g.send(None)`. The two are equivalent at
  runtime, but a declared SendType rejects the `None`, so only the
  `next()` form type-checks.

**Union syntax.**

- Write `X | None` and `X | Y`, never `Optional[X]` or `Union[X, Y]`
  (PEP 604). Watch for a leftover `Optional`/`Union` import slipping
  in from habit or a pasted snippet.

**`@override`.**

- Decorate methods that override a method declared on a user-defined
  base, implement an abstract method from an ABC, or override a
  stdlib method meant to be overridden (`JSONEncoder.default`).

- Do not decorate `__init__`/`__new__`, dunders that merely override
  `object`/`type`/`Enum` infrastructure defaults (`__repr__`,
  `__str__`, `__eq__`, ...), or methods on Protocol-satisfying
  classes (structural, not inheritance).

## Structure and idiom

- **Dispatch on a literal with `match`/`case`,** with a `case _:`
  default, not an `if`/`elif` chain. It reads as one decision on one
  value and makes the unknown branch explicit.

- **Never name identifiers after soft keywords.** No functions,
  parameters, or variables named `match`, `case`, or `type`. Pick a
  domain word (`duel()` instead of `match()`).

- **Exception names need no `Error` suffix.** `InsufficientFunds` and
  `TypeFailure` are fine. Ignore lint rule N818.

- **A frozen data class is frozen and slotted, written `@record`.**
  `utils/record.py` (chapter 18) is
  `dataclass(frozen=True, slots=True)` under
  `dataclass_transform(frozen_default=True)`. From that section on,
  a listing writes `@record` with `from record import record`, and
  the prose noun is "record". `frozen=True` on its own rejects every
  assignment through `__setattr__`, so the slots are for the memory
  and access-speed win (the dropped `__dict__`), not to prevent
  attribute growth. The rulings around it:
  - A base the book owns gets an empty `__slots__ = ()` so its
    frozen subclasses are records.
  - A class whose base is a library's and declares no `__slots__`,
    or a listing that reads the instance `__dict__` or pickles
    across versions, writes `@record(slots=False)`. The flag makes
    dropping slots a visible choice; a bare `@record` under an
    unslotted base lets the base take the slots back.
  - A class that needs an option `record()` lacks keeps `@dataclass`
    written out: `order=True`, `weakref_slot=True`, a
    `cached_property`.
  - A mutable `@dataclass` whose instances the program reads and
    leaves unchanged is a record. One whose state grows (a test
    double accumulating into a list field) or whose identity is the
    point (a Singleton) stays a data class.
  - A sentence that names `frozen=True` about a converted class says
    "record" instead. The long form stays where `frozen=True` is the
    listing's subject.

- **A class whose `__init__()` only assigns parameters or defaults to
  fields is a `@dataclass`** (frozen unless mutation is the point).
  Write the manual form only when the code is teaching it (an
  interning `__new__()`, a `__dict__` trick), and then say why in an
  adjacent comment or prose: a deviation from this idiom is part of a
  lesson, never an accident.

- **Prefer a context manager wherever paired begin/end calls bracket
  a span**: enter/leave, acquire/release, start/stop, open/close.
  Replace the pair with `__enter__`/`__exit__` (or
  `@contextmanager`) and a `with` block, so the end call cannot be
  forgotten and runs even when the body raises an exception. A manual pair
  survives only when the span crosses scopes, with the release
  happening in a different method, object, or task than the acquire.

- **Polymorphism is broader than method dispatch.** It means one
  function accepting more than one argument type: ad hoc
  (overloading), parametric (generics), and subtype (inheritance
  dispatch). Never write that polymorphism happens only through
  method calls.

- **Follow standard naming.** `snake_case` for functions and
  variables, `PascalCase` for classes, short lowercase names for
  modules and packages. A single leading underscore (`_helper`) marks
  a name internal; a trailing underscore (`type_`) dodges a keyword
  clash; a double leading underscore is reserved for class-attribute
  name mangling, not general "privacy." Never name a variable `l`,
  `O`, or `I`; in many fonts they are indistinguishable from `1`/`0`.

- **A name only its own class uses takes a leading underscore.** A
  helper method or state attribute that no code outside the class
  reads is `_responders` or `_slot()`, so the reader can tell the
  class's interface from its internals. These stay public: record,
  dataclass, and NamedTuple fields (constructor parameters and repr
  content), a constructor parameter stored on `self` as data, a name
  a dispatch table or the prose cites, the second leg of a double
  dispatch called on another object, and an introspection demo whose
  point is the visible method. When a lazily built list must live in
  the instance `__dict__` under the accessor's name, make the
  accessor a getter-only `@property`: a data descriptor outranks the
  dict entry, where a plain method is shadowed after the first call.

- **Prefer absolute imports** over relative ones, except within a
  package's own submodules, and avoid wildcard imports
  (`from module import *`), which hide where a name came from. A
  circular import is a design signal to resolve, not something to
  route around by default with `TYPE_CHECKING`; confirm the cycle is
  structurally necessary before reaching for the deferred-import
  pattern (see "Annotations are lazy" above).

- **Prefer EAFP over LBYL** for an operation that can fail: a dict
  lookup, an attribute access, a file open. Wrap only the call that
  can fail in a narrow `try`, never use a bare `except:`, and catch
  the specific exception type(s) you can handle. When raising a
  different exception in response to one you caught, use
  `raise NewException(...) from original` to preserve the chain.

- **Derive related values from one reading of a changing source.** A
  function that reads the clock twice to build two parts of one
  result has a window where the parts disagree: a file named for one
  day holding an entry stamped the next. Read once, bind the value,
  derive everything from it. The same applies to any non-repeatable
  read (an RNG, a counter, file state), and injecting the source
  (parameter, ability, fixture) is what makes the disagreement window
  testable at all.

- **Default a mutable argument to `None`,** then build the object
  inside the function body. A default argument is evaluated once, at
  function-definition time: `def f(items: list[int] = []):` shares
  one list across every call that doesn't pass its own, unless the
  shared state is a deliberate memoization cache that says so in a
  comment.

- **Prefer a comprehension** over a `for` loop with `.append()` for a
  simple one-to-one transformation or filter, but drop to a loop or a
  named helper once it nests more than one level or a condition spans
  multiple clauses. Readability outranks compactness once a
  comprehension needs its own explanation.

- **Prefer f-strings** (`f"{x:.2f}"`) over `str.format()` or
  `%`-formatting when building a string from values.

- **Prefer `pathlib.Path`** over `os.path` string manipulation.
  `Path(filepath).stem` reads clearer than
  `os.path.splitext(os.path.basename(filepath))[0]`, and
  `base / "config" / "settings.ini"` reads left-to-right instead of
  nesting `os.path.join()` calls.

- **Use the walrus operator (`:=`) for a genuine
  assignment-inside-expression,** e.g.
  `while (line := f.readline()):` or
  `if (match := pattern.search(s)):`, where it removes a duplicated
  call. Skip it when a plain two-line assignment-then-check reads
  just as clearly; it isn't a compactness contest.

- **Put any resource that needs cleanup** (a file, a lock, a DB
  connection, a socket) in a `with` block, not a manual
  acquire/release pair wrapped in `try`/`finally`. For a simple
  custom context manager, prefer a generator function decorated with
  `@contextlib.contextmanager` over a full class with
  `__enter__`/`__exit__`, unless the class already exists for other
  reasons.

## Security

- Never call `eval()`/`exec()` on untrusted or user-supplied input.
  `ast.literal_eval()` safely parses a literal (dict, list, number,
  string) from text without executing arbitrary code.

- Never unpickle data from an untrusted source. `pickle.loads()` can
  execute arbitrary code during deserialization; prefer `json` for
  data interchange.

- Never pass untrusted input to `subprocess` with `shell=True` or to
  `os.system()`. Pass a list of arguments with `shell=False` (the
  default), and use `shlex.quote()` if a shell is genuinely
  unavoidable.

## Formatting and comments

- **Listings stay dense.** At most one blank line anywhere: a single
  blank between top-level defs/classes, a single blank after the
  import block, no blank lines between import groups. Imports stay
  grouped and sorted (stdlib, third-party, local) but contiguous. Do
  not run a formatter that re-expands to two blanks (Black-style).

- **Expected output goes in `#:` markers, next to the code that
  produced it.** A listing records what it prints as `#:` comment
  lines, one per line of stdout, and the build verifies them against a
  real run. Each run of markers sits directly after the statement that
  produced that output, never gathered at the end of the listing: the
  reader should see a result beside the code responsible for it. A
  single run of many `#:` lines is still right when one statement
  produced all of it (a `for` loop, one multi-line `print()`), so do
  not split those.

- **A marker for output an `import` produced is the exception.**
  Placed directly after the last import, it sits inside the import
  block and trips ruff's `I001`. Close the import block with its blank
  line first, then put the marker below it, still directly above the
  code it precedes:

      import a_package

      #: initializing a_package
      print(hasattr(a_package, "module1"))

- **Line length is 60,** so listings fit small screens without
  wrapping. Long inline comments are the usual culprit: move the
  comment to its own line or wrap the statement. The one sanctioned
  overflow is a trailing `# type: ignore` pragma. Output must fit
  too: shorten what the program prints rather than letting a `#:`
  marker run past 60. A name is never the thing to shorten: a
  parameter is named for its role (`callback`, not `use`), and a
  signature the name pushes past 60 wraps across lines, the
  parameters on their own indented line between `def f(` and
  `) -> None:`, as chapter 11's test signatures and chapter 45's
  `fibonacci_callback.py` do.

- **Prose that walks a listing points with tags, not positions.** A
  line the prose refers to carries a trailing `# [1]`, `# [2]`, ...
  comment, numbered from 1 in order within the listing, and the
  prose cites it as a code span, `` `[1]` ``, never bare. "The
  second `print()`" makes the reader count, and "the `for` loop"
  fails when the listing has two. Name the construct when the
  listing has one of it and the prose mentions it once; tags are for
  an ordered walk. A tag counts toward the 60-column width, so a
  tagged line near the limit is split or carries the tag on its own
  line above it, which refers to the line below.

- **Comment capitalization:** start with a capital when the first
  word is prose. Leave the case alone when the comment begins with a
  code identifier (`# os.path.join handles this`).

- **Comment periods:** a one-line comment ends without a period. Only
  a multiline comment block (two or more consecutive full-line `#`
  comments) reads as sentences and keeps its periods.

- **New descriptions belong in prose, not comments.** When writing or
  adding to an example, a comment that explains what it does, why, or
  a design choice behind it goes in the chapter prose after the code
  block, not in the code — this applies to the header comment and to
  inline comments anywhere else in the body. Comments stay in the
  code only for a tool directive (`# type: ignore`, `# noqa`), the
  single-line `# path/slug.py` file marker, or when specifically
  requested. Never narrate what the next line does. This rule is
  about comments you are about to write, not a license to edit
  comments already sitting in existing example code — leave those
  alone unless asked about that specific comment, even if you're
  mid-edit on the same block for an unrelated reason.

- **Docstrings live outside chapter listings.** A chapter listing
  explains itself in the surrounding prose, not a docstring (see
  "New descriptions belong in prose, not comments" above). A `tools/`
  helper module or other code outside a listing gets a real one:
  PEP 257 triple double-quotes, a one-line summary ending in a
  period, and, if more is needed, a
  blank line followed by parameters, return value, and exceptions
  raised.

## Demos and tests

- **A demo makes its point once and stops.** Collapse repeated prints
  into one combined `print(...)` that shows the key result
  (`print(x.val, x is y is z)`). Keep step-by-step output only when
  the growth is itself the point.

- **Tests live beside the code they exercise,** in their own
  `test_*.py` file, one focused file per example rather than one
  combined test module. When a test carries the verification, the
  inline demo can stay short.

- **A module another listing imports carries no top-level demo.**
  `#:` markers are validated as top-level chunks, so a demo under
  `if __name__ == "__main__":` cannot carry them. Split instead: a
  library listing with classes and functions and no import-time
  effects, plus a separate demo listing that imports it and holds
  the markers (chapter 31's `observers.py` and `thermometer.py`). A
  listing nothing imports, with a few lines of demo, stays whole.
  The `__main__` guard survives for a demo that carries no markers,
  such as a multiprocessing listing whose output lives in prose.

- **A demonstrated exception goes through `expect()`.** When a
  listing shows that a call raises an exception, write
  `expect(ExcType, fn, *args)` from `utils/exceptions.py`
  (`from exceptions import expect`); its marker reads
  `#: [TypeError] message`. `expected(ExcType)` is the context
  manager for a statement that cannot be passed as a call, and
  `aexpect()` the form for an awaited call. A `try`/`except` that
  prints the message is for a chapter teaching `try`/`except`, a
  handler that returns or continues, or a listing whose point is
  that `ty` flags the call, since through `expect()` the checker
  sees nothing. One trap: `expect()` evaluates its arguments before
  its own `try`, so an exception raised while building the argument
  list (`Proxy(x).f`, a failing constructor) escapes it; use
  `expected` there.

- **Nondeterministic output needs taming** before it can be asserted
  or displayed: round floats (`f"{x:.6f}"`), print
  `type(e).__name__` instead of a message, or prefer deterministic
  measures (`sys.getsizeof()`) over wall-clock timings.

- **Benchmarks warm up outside the timed region.** Create the pool or
  trigger the JIT before the `timeit` call, or setup cost hides the
  real speedup.

- **`print()` stays inside chapter listings.** Demo code deliberately
  prints, per the marker convention above. A `tools/` script meant to
  run unattended should use the `logging` module instead, for
  timestamps, severity levels, and output that can be redirected or
  silenced without touching call sites.

- **Structure each test as Arrange, Act, Assert:** build the fixture
  state, perform the one action under test, then check the result.
  One behavior per test; a test with two unrelated assertions hides
  which one actually failed.

- **Collapse near-duplicate test functions** that only vary by
  input/expected-output into one `@pytest.mark.parametrize` test, so
  pytest reports each case independently rather than a single test
  hiding after the first failing input.

## The listing serves the chapter

A listing can type-check, run, and match its prose and still be the
wrong listing for its section. Ask these of each one you write or
revise:

- **Which lines show the subject?** Sort the lines into the ones
  that show the pattern or construct the section teaches and the
  ones that exist so the demo can run: reading a file, parsing
  input, building fixtures, formatting. Incidental code that
  outgrows the subject code, repeats in a second listing, or needs
  sentences of prose moves to a helper module, becomes a literal of
  typed objects, or goes.

- **What does it check at runtime that the checker could check?** A
  string that must match a member, a dict keyed by the names of
  things the module defines, a lookup that raises a `KeyError` for a
  misspelling, an `isinstance()` chain over a known set of classes:
  an `Enum`, a record, a `Protocol`, or a generic lets the checker
  report the mistake before the program runs. Keep the runtime check
  when the boundary where untrusted input arrives is the subject, or
  when the dynamic form is (a registry, a plugin table).

- **Does the trace show the subject?** A state machine's trace shows
  the transition (from, input, to) on one line; an observer demo
  shows who was notified of what; a cache demo shows hits and
  misses; a timing demo puts the two numbers side by side. A trace
  that prints the input on one line and the resulting action on the
  next makes the reader assemble the transition.

- **Do the names match the prose?** A parameter named `event` under
  prose that says "input", a method `handle()` the prose calls
  "dispatch": each makes the reader translate. Use the prose word in
  the code, with the usual escape (`input_`, `class_`) when a
  builtin or keyword takes it.

- **Does an output line repeat its neighbor?** A state name one line
  prints as a prefix and the next prints as the current state, a
  message echoed by a wrapper and again by the callee: drop the copy
  that carries less, and check that the first and last lines of the
  trace still identify themselves.

- **When several listings vary one component, hold the rest
  identical.** Chapter 45's `fibonacci_callback.py`,
  `fibonacci_list.py`, and `fibonacci_class.py` show three shapes of
  one producer, so each is driven by the same running-total consumer
  over the same seven values, and the reader compares producers
  alone. What each prints follows its subject: a listing whose
  subject is a shape prints its result once (`total=20`), and a
  listing whose subject is state across calls keeps the per-call
  trace that shows the state surviving.

## Design patterns

- **Name a pattern only when the structure earns it.** A staged
  constructor is not "the Builder pattern." Before writing "this is
  the X pattern," confirm the code has the pattern's defining
  structure. Otherwise describe the technique plainly.

- **Capitalize pattern names and set them in italics on every
  mention,** in prose and in link text: *Template Method*, *Factory
  Method*, *Observer*. Headings stay plain, and the lowercase word
  keeps its ordinary sense ("an observer registers").

- Many classic patterns dissolve in Python. First ask whether a
  function, a dataclass, a protocol, or a closure already solves the
  problem before building the class hierarchy the pattern's C++/Java
  form prescribes.

## Concurrency and low-level footguns

- `time.sleep(0)` no longer forces a GIL handoff on current Python.
  Thread race demos need a tiny nonzero sleep
  (`time.sleep(0.000_001)`). In asyncio, `await asyncio.sleep(0)`
  still yields deterministically.

- CPython's small-int cache extends well past the textbook `-5..256`
  on recent builds. An "uncached" int demo needs a value of 100000 or
  more, or it silently proves the opposite.

- Object immortality (PEP 683) shipped in 3.12 for every build. It is
  not a free-threading-only feature; free threading just makes it
  matter more.

- `Path.write_text()`/`open()` for writing translates every `\n` to
  the platform's line separator by default, `\r\n` on Windows, even
  with `encoding=` set explicitly. Pass `newline="\n"` whenever the
  file must stay LF-only, such as a script rewriting a tracked source
  file in place.

- A generator object is single-use, and exhaustion is silent. A
  second `for` loop over a spent generator runs zero iterations, and
  a driver that reads `StopIteration.value` from one gets `None`, in
  both cases with no exception. When something must iterate or run
  twice, materialize with `list()` or rebuild by calling the
  generator function again; a hidden instance of this rule is any
  API that accepts a generator and may traverse it more than once.

- A module already in `sys.modules` is never re-resolved from
  `sys.path`, even when a later `import` of the same name happens
  from a directory that would otherwise come first on the path. A
  shared utility module named something generic (`config.py`,
  `utils.py`) can silently shadow an unrelated same-named file loaded
  dynamically elsewhere in the same process, such as an `exec()`'d
  script or a plugin. Give a widely-imported shared module a
  distinctive name instead of a common one.

- Never call a blocking synchronous function (`time.sleep`,
  `requests.get`, plain file I/O) inside an `async def`; it freezes
  the whole event loop, not just the calling coroutine. Use the
  `asyncio` equivalent (`asyncio.sleep`, an async HTTP client)
  instead.

- For concurrent awaits, prefer `asyncio.TaskGroup` (3.11+) over
  `asyncio.gather()`. A `TaskGroup` cancels its siblings and reports
  every failure on an unhandled exception; `gather()` without
  `return_exceptions=True` can leave sibling tasks running after one
  fails.

- Offload CPU-bound work to `asyncio.to_thread()` rather than
  awaiting it directly; `await` alone never yields the event loop to
  another coroutine during CPU-bound computation.

- An asyncio demo whose output depends on the order in which
  deadlines fire needs 5-10x gaps between competing sleeps
  (0.01/0.05/0.25), widest where a cancellation must propagate.
  Windows timers tick at about 15 ms, so 0.01/0.02/0.03 lets a task
  finish inside the tick that was meant to cancel it, and a
  self-healing marker then records the opposite of what the prose
  says.

- `slots=True` makes `dataclass()` create and return a new class,
  since a class's slots are set at creation. A decorator that
  registers a class must register what `dataclass()` returns:
  `EVENTS.add(cls)` before the call files a class no instance
  belongs to, and a registering decorator stacked under `@record`
  sees the pre-slots class the same way. Separately, `ty` mistypes
  `record(cls)` on a `type[E]` parameter, so such a decorator calls
  `dataclass(frozen=True, slots=True)(cls)` directly (chapter 27's
  `tagged_bus.py`).

- A seeded simulation can still print differently across platforms.
  The seed holds the random draws still, but the C library's `cos`
  differs in the last bit between Windows and glibc, and a chaotic
  run multiplies that bit each step until a three-decimal reading
  moves. Print two decimals from such a run; leave the seed alone.

- A warning goes to stderr, and a `#:` marker captures stdout alone. A
  listing that must show one records it with
  `warnings.catch_warnings(record=True)` and
  `simplefilter("always")`, then prints the category and message
  under `#:`.
