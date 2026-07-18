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

**Annotations are lazy (PEP 649, Python 3.15+).**

- Forward references need no quotes and no
  `from __future__ import annotations`.

- Types imported only under `if TYPE_CHECKING:` are safe in any
  annotation, including bare class-body declarations. Use this to
  break import cycles.

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

- **`@dataclass(frozen=True)` already blocks new attributes** (its
  `__setattr__` rejects every assignment). Pair it with `slots=True`
  for the memory and access-speed win (the dropped `__dict__`), not
  to prevent attribute growth.

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
  forgotten and runs even when the body raises. A manual pair
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

- **Line length is 70.** Long inline comments are the usual culprit.
  Move the comment to its own line or wrap the statement.

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

- **Importable modules carry no top-level demo.** If a module is both
  a library and a demonstration, split it: a demo-free library module
  plus a separate runnable file that imports it and holds the demo.

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

## Design patterns

- **Name a pattern only when the structure earns it.** A staged
  constructor is not "the Builder pattern." Before writing "this is
  the X pattern," confirm the code has the pattern's defining
  structure. Otherwise describe the technique plainly.

- **Capitalize pattern names** as proper nouns: Template Method,
  Factory Method, Observer.

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
