# Features Used But Not Introduced

A candidate list of Python features that appear in the book's code or prose
without a chapter that teaches them. The book is pitched as intermediate and
builds chapter to chapter, so each of these is a place a reader might hit a
feature cold.

How to use this file: keep the features you want introduced somewhere and
delete the rest (for the deleted ones you are judging that the reader can figure
it out, or already knows it). Chapter numbers are the current `NN` stems.

Method: a script found where each feature is first used in code, in chapter
order; then each was reviewed by hand to decide whether any chapter actually
introduces it (teaches it) versus merely uses it in passing. "Introduced" means
taught, not just mentioned.

## Clear gaps (used, with no introduction anywhere)

- **`async` / `await` / asyncio** (`asyncio.run`, `create_task`, `gather`, `sleep`). First and only use is Simulation (`31`, the rats). There is no concurrency or async chapter, so the example assumes the reader knows cooperative async tasks.
- **PEP 695 type parameters** (generic functions and classes: `class Success[A]`, `def bind[B, E]`, and the `[**P, R]` ParamSpec form). First in Functional Error Handling (`12`); also Decorators (`13`, the `[**P, R]` form) and Function Objects (`25`). Static Type Checking (`08`) covers hints and Protocols but never how to declare a type parameter.
- **`type X = ...` alias statement** (PEP 695). First in Pattern Matching (`11`, `type Shape = Circle | Square`); recurs in several chapters (`type Line`, `type Grid`, `type Result`). The `type` statement itself is never explained.
- **Walrus operator `:=`**. Simulation (`31`, `while pending := [...]`). Not introduced.
- **`typing.TYPE_CHECKING`** (the import-guard pattern for forward references). Simulation (`31`, `items.py`). Not introduced.
- **`typing.Self` return type**. Simulation (`31`, `Maze.from_text(...) -> Self`). Not introduced.

## Brief in-context mention only (you may judge these sufficient)

- **`StrEnum`**. State Machines (`22`) explains it in one line ("each member is its string value"). The `Enum` base is introduced in Data Classes (`10`).
- **`functools.wraps`**. Used in Functional Error Handling (`12`, the `@safe` decorator) one chapter before Decorators (`13`) explains it. An ordering issue more than a true gap.
- **`@cache` / `functools.cache`**. Singleton (`19`) uses it for a cached factory, with only a passing note.
- **`itertools.count`**. Simulation (`31`, handing out rat numbers). `itertools` is named in Iterators (`23`), but `count` is not shown there.
- **`dataclasses.field` / `default_factory`**. Data Classes (`10`) and Metaprogramming (`15`). Data classes are introduced, but `field` and `default_factory` specifically may not be spelled out.

## Standard names used throughout, never formally introduced

Probably fine for an intermediate reader, listed for completeness.

- **`collections.abc` annotations: `Callable`, `Iterator`, `Iterable`, `Sequence`, `Mapping`**. Used as type hints from Pattern Matching (`11`) onward. Static Type Checking (`08`) covers typing in general but not these names.
- **`typing.Any`**. Used in roughly 15 chapters. Gradual typing in Static Type Checking (`08`) touches the idea, so `Any` is arguably introduced there.
- **`pathlib.Path` for reading files** (`Path(...).read_text()`). From Containers (`03`) onward. Never introduced; the book deliberately skips tooling, but reading a file shows up in examples.

## Checked and confirmed already introduced (not action items)

Listed so you can see the scan's coverage: Protocol and `Final` (`08`); `Enum`,
frozen data classes, `asdict` / `astuple` / `replace` / `KW_ONLY` / `__post_init__`
(`10`); `match` (`03`, `11`); decorators (`13`); comprehensions (`14`);
`__init_subclass__` / `__set_name__` / metaclasses (`15`); generators and `yield`
(`23`, `24`); properties, `@staticmethod` / `@classmethod` (`06`); `*args` /
`**kwargs`, keyword-only and positional-only parameters, lambdas (`04`); context
managers and `with` (`03`); `weakref` and `__del__` (`07`); `__subclasses__()`
(`24`); `functools.singledispatch` (`29`, `30`); `assert_never` (`11`);
f-strings (`02`).
