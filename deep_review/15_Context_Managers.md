# Deep review: 15_Context_Managers.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Show what a `@contextmanager` generator does without `try`/`finally`

**Kind:** teaching
**Where:** section "A Basic Context Manager" (line ~46), just after "The `finally` makes the cleanup dependable"
**Problem:** This is the single most common mistake with `@contextmanager`, and the chapter states the rule without showing the failure. The reader is told the `finally` "makes the cleanup dependable" and can easily read that as a stylistic nicety rather than a requirement. Every following generator-based listing (`banner`, `tag`, `Pool.lease`) uses `try`/`finally`, so the reader sees the habit but never sees what its absence costs. Meanwhile the class-form half of the chapter gets an entire section ("Cleanup Is Guaranteed") demonstrating exactly this guarantee for `__exit__`, so the generator form is the weaker-taught of the two on the chapter's central point.

**Proposal:** Add a short listing and two sentences of prose. Verified: it runs and type-checks as written.

    ```python
    # no_finally.py
    from collections.abc import Iterator
    from contextlib import contextmanager

    @contextmanager
    def careless(name: str) -> Iterator[str]:
        print(f"enter {name}")
        yield name
        print(f"exit {name}")

    try:
        with careless("A"):
            raise ValueError("boom")
    except ValueError as error:
        print("caught:", error)
    #: enter A
    #: caught: boom
    ```

Prose after it:

> Without the `try`/`finally`, an exception in the block resumes the generator by raising at the `yield`,
> so the code after the `yield` never runs and `exit A` never prints.
> Nothing warns you: the cleanup is skipped silently on the one path where it matters most.
> Wrap the `yield` in `try`/`finally` in every `@contextmanager` generator, without exception.

**Cost:** One new listing and one new example file. Placement matters: putting it inside "A Basic Context Manager" before "The Protocol" keeps the failure next to the rule, but it does lengthen the chapter's opening section. The alternative is to put it in "Cleanup Is Guaranteed" as the generator-form counterpart of `exit_on_error.py`, which pairs the two forms but delays the warning past two sections in which the reader may have already written the buggy version.

---

## 2. Teach exception suppression in the generator form

**Kind:** teaching
**Where:** section "The `__exit__()` Arguments" (line ~144), after "A truthy value *suppresses* it"
**Problem:** The chapter says the generator form "is usually the clearest choice," then teaches suppression only through `__exit__`'s return value. A reader who has taken that advice and writes generator managers has no idea how to suppress from one, and nothing in the chapter connects `return True` to any generator construct. The obvious guess (`yield` inside a `try`, then `return True` from the generator) does not work, so the gap is not one a reader closes by experiment.

**Proposal:** Add a listing and a paragraph immediately after the `return True` explanation, before `contextlib.suppress`. Verified to run and type-check:

    ```python
    # suppress_in_generator.py
    from collections.abc import Iterator
    from contextlib import contextmanager

    @contextmanager
    def ignoring(kind: type[BaseException]) -> Iterator[None]:
        try:
            yield
        except kind as error:
            print(f"swallowed {error!r}")

    with ignoring(ZeroDivisionError):
        print("before")
        1 / 0
        print("after")
    print("survived")
    #: before
    #: swallowed ZeroDivisionError('division by zero')
    #: survived
    ```

Prose:

> In a generator manager there is no return value to set.
> The exception arrives at the `yield`, so catching it there and not re-raising is the equivalent of `__exit__()` returning `True`.
> Letting it out of the `except` clause, or omitting the clause, is the equivalent of returning a falsy value.

**Cost:** One new listing. It sits in a section named for `__exit__()`'s arguments, so the section may want a slightly broader heading, or the listing may belong in "A Basic Context Manager" alongside proposal 1. Recommending the `__exit__()` section, since suppression is the topic there.

---

## 3. Warn that `__exit__()` does not run when its own `__enter__()` raises

**Kind:** teaching
**Where:** section "Cleanup Is Guaranteed" (line ~131), after "This is the same guarantee a `try`/`finally` gives"
**Problem:** The section title asserts an unqualified guarantee and the numbered protocol list says `__exit__()` is called "no matter how the block finished." Both are true of the *block* and false of `__enter__()`: if `__enter__()` raises after acquiring half its resources, `__exit__()` never runs and whatever it acquired leaks. A reader who has just been sold the guarantee will write acquisition code in `__enter__()` on that assumption. Verified on the pinned build: `__exit__` does not run, and in a multi-manager `with`, managers that already entered successfully do exit.

**Proposal:** Add a short listing and a paragraph. Verified to run and type-check:

    ```python
    # enter_fails.py
    class Fragile:
        def __enter__(self) -> None:
            print("enter fails")
            raise RuntimeError("no resource")

        def __exit__(self, *exc: object) -> bool:
            print("exit runs")
            return False

    try:
        with Fragile():
            print("body")
    except RuntimeError as error:
        print("caught:", error)
    #: enter fails
    #: caught: no resource
    ```

Prose:

> The guarantee covers the block, not the setup.
> `exit runs` never prints, because Python only registers the cleanup once `__enter__()` returns.
> An `__enter__()` that acquires several things must clean up its own partial work before it raises an exception.
> In a `with` naming several managers this is per-manager: the ones that entered successfully still exit, and only the failing one is left unwound.

**Cost:** One new listing in a section that currently holds one. If this feels like too much for the section, the prose alone (without `enter_fails.py`) still closes the gap, at the cost of asserting the behavior instead of showing it.

---

## 4. `nullcontext_demo.py` has a function close a stream it did not open

**Kind:** code
**Where:** section "The `contextlib` Toolkit" (line ~449), `nullcontext_demo.py`
**Problem:** The example inverts the conventional direction of `nullcontext`. As written, `emit()` closes a `StringIO` the caller created and passed in, and the demo then shows the caller's buffer being unusable afterward as if it were the desired outcome. Closing a resource you did not open is a real bug pattern (the caller may want to write more, or read the value), and this is the one listing in the chapter a reader is most likely to copy into working code. The standard `nullcontext` idiom, including the one in Python's own documentation, runs the other way: the function closes only what it opened, and wraps a caller-supplied object in `nullcontext` so the `with` leaves it alone.

**Proposal:** Invert it. Replace the listing with the version below (verified: runs, produces these markers, and passes `ty`), and rewrite the surrounding prose so the rule stated is "close what you opened, leave alone what you were handed."

    ```python
    # nullcontext_demo.py
    import sys
    import tempfile
    from contextlib import AbstractContextManager, nullcontext
    from io import StringIO
    from pathlib import Path
    from typing import IO

    def emit(lines: list[str], out: IO[str] | Path | None = None) -> None:
        manager: AbstractContextManager[IO[str]]
        match out:
            case Path():
                manager = out.open("w")
            case None:
                manager = nullcontext(sys.stdout)
            case _:
                manager = nullcontext(out)
        with manager as stream:
            for line in lines:
                print(line, file=stream)

    emit(["alpha", "beta"])  # Default: stdout, left open
    #: alpha
    #: beta
    buffer = StringIO()
    emit(["gamma"], buffer)  # Caller's stream, left open
    print(buffer.getvalue().strip(), buffer.closed)
    #: gamma False
    path = Path(tempfile.gettempdir()) / "emit.txt"
    emit(["delta"], path)  # emit() opened it, so emit() closes it
    print(path.read_text().strip())
    #: delta
    path.unlink()
    ```

Replacement prose:

> `emit()` closes only the file it opened.
> A stream the caller handed over stays open, which is what the caller expects;
> the `nullcontext` wrapper is what lets one `with` block serve both cases without an `if` around the whole body.

Alternative, if the new listing is too large: keep the current two-case shape but swap which case gets the `nullcontext`, so the caller-supplied stream is the one left open and the default is a file `emit()` opens.

**Cost:** Rewrites one listing, its `#:` markers, and the two paragraphs around it. It introduces `AbstractContextManager` (used as an annotation only) and `match` on class patterns, neither of which the chapter uses elsewhere. Nothing else in the book imports `nullcontext_demo`.

---

## 5. "Recreates its generator on each use" reads as a contradiction of the single-use caution

**Kind:** prose
**Where:** section "Context Manager as Decorator" (line ~308)
**Problem:** Section 1 tells the reader a generator manager object is single-use and a second `with` on the same object raises an exception. Section 5 says "A generator-based manager recreates its generator on each use." Both are describing real behavior, but "on each use" is the wrong span: the manager object does not recreate anything. `ContextDecorator`'s wrapper builds a *fresh manager* on each call of the decorated function, which is why the decorated function is reusable while the manager object is not. A reader who notices both sentences has to guess which one is wrong.

**Proposal:** Replace lines ~308-310 with:

> Each call of the decorated function builds a fresh manager, so `report()` can be called any number of times, each with its own enter and exit.
> The single-use caution from earlier still holds for the manager object you name in a `with`.

**Cost:** none.

---

## 6. Move and trim the `type[BaseException]` paragraph

**Kind:** prose
**Where:** section "The `__exit__()` Arguments" (lines ~208-230)
**Problem:** The five paragraphs between `utils/exceptions.py` and `demo_exceptions.py` explain the same two facts twice. Line ~208 says `exc_type` is the raised exception's class or `None`; lines ~228-230 say it again ("`exc_type` is that class, and `issubclass(exc_type, self.types)` checks it against `self.types`"), after the `issubclass` explanation has already said it a third time. The genuinely new content in the last paragraph is the `type[...]` cross-reference and the gloss "the exception class, such as `ZeroDivisionError`, not an instance of it," and that arrives four paragraphs after the annotation it explains was first used.

**Proposal:** Fold the new content into the paragraph at line ~208 and delete the rest of the closing paragraph. Result:

> `__exit__()` receives `exc_type: type[BaseException] | None` because Python passes it the raised exception's class,
> or `None` when the block finished cleanly.
> [`type[...]`](08_Static_Typing.md#classes-as-values-type) means the class, such as `ZeroDivisionError`, not an instance of it.

Then delete lines ~224-230 entirely.

**Cost:** none. The `08_Static_Typing.md#classes-as-values-type` link survives the move.

---

## 7. The book never explains async context managers

**Kind:** teaching
**Where:** section "The `contextlib` Toolkit" (line ~448), as a closing paragraph
**Problem:** `async with` appears eleven times in chapter 19 (`asyncio.TaskGroup`, `asyncio.Lock`, `Semaphore`) with no definition anywhere in the book. `__aenter__`, `__aexit__`, `@asynccontextmanager`, and `AsyncExitStack` appear nowhere at all. Chapter 15 is the only place a reader would look, and it is the chapter that teaches the protocol the async form mirrors. Right now a reader arriving at chapter 19's `async with asyncio.TaskGroup() as tg:` has to take it as unexplained syntax.

**Proposal:** Add a short paragraph, no listing:

> Coroutines need setup and cleanup that can `await`, which the synchronous protocol cannot express.
> The async counterpart replaces the two methods with `__aenter__()` and `__aexit__()`,
> the decorator with `@contextlib.asynccontextmanager`, `ExitStack` with `AsyncExitStack`,
> and `with` with `async with`.
> Everything in this chapter carries over unchanged apart from the names.
> [Concurrency](19_Concurrency.md) uses `async with` for task groups and locks.

**Cost:** Adds a forward reference to chapter 19 from chapter 15. Nothing depends on the section's current ending.

---

## 8. Three classes hand-write a parameter-assigning `__init__()`

**Kind:** code
**Where:** `trace_cm.py` (line ~72), `utils/exceptions.py` (line ~183), `banner_cm.py` (line ~323)
**Problem:** The house style in `thinking-in-python-skill.md` says a class whose `__init__()` only assigns parameters to fields is a `@dataclass`, and that writing the manual form is allowed when the code is teaching it but the prose must say why. All three classes here assign one parameter and nothing more, and none of the three says why. Chapter 12 has already taught dataclasses, so a reader who took that chapter seriously will notice.

**Proposal (recommended):** Keep the manual `__init__()`s and add the missing justification, one clause in the prose at line ~65. Change "Writing the class by hand shows the machinery directly:" to:

> Writing the class by hand shows the machinery directly.
> `__init__()` stays in its longhand form here rather than becoming a `@dataclass`,
> so nothing between the class statement and the two protocol methods needs decoding:

Alternative: convert all three to `@dataclass`. `Trace` becomes `@dataclass class Trace: name: str`, `banner` becomes `@dataclass class banner(ContextDecorator): title: str`, and `ignore` becomes `@dataclass class ignore: types: Types | ALL = ALL`. This is more consistent with the rest of the book but adds a decorator to every listing in a chapter whose point is two other dunders. Not recommended.

**Cost:** The recommended option costs nothing. The alternative touches `utils/exceptions.py`, which chapters 17, 18, 36, 40, and 44 import; the behavior is identical, but it is a wider blast radius than a chapter-15 review should take on unilaterally.

---

## 9. The `ExitStack` example is not dynamic

**Kind:** code
**Where:** section "Combining Context Managers" (line ~406), `exit_stack.py`
**Problem:** The motivating sentence is "When you do not know the number of managers until runtime," and the listing then hard-codes `("a", "b", "c")` at module level. The reader sees a comma-separated `with` written a longer way. Nothing in the listing could not be written as `with tag("a"), tag("b"), tag("c"):`, so the reason `ExitStack` exists is stated but not shown.

**Proposal:** Put the loop inside a function that takes the names, and call it twice with different lengths:

    ```python
    # exit_stack.py
    from collections.abc import Iterator
    from contextlib import ExitStack, contextmanager

    @contextmanager
    def tag(name: str) -> Iterator[str]:
        print(f"open {name}")
        try:
            yield name
        finally:
            print(f"close {name}")

    def wrap(names: list[str]) -> None:
        with ExitStack() as stack:
            open_tags = [stack.enter_context(tag(n)) for n in names]
            print("using", open_tags)

    wrap(["a", "b"])
    wrap(["a", "b", "c"])
    ```

with markers updated to the two runs.

**Cost:** Rewrites one listing and its markers. Exercise 3 refers to `multiple.py`, not this file, so the exercises are unaffected.

---

## 10. `*exc: object` in `banner_cm.py` is never explained

**Kind:** teaching
**Where:** section "Context Manager as Decorator" (line ~329)
**Problem:** `trace_cm.py` and `utils/exceptions.py` both spell the three `__exit__()` parameters out, then `banner_cm.py` silently switches to `def __exit__(self, *exc: object) -> bool`. A reader who has been taught that `__exit__()` takes three specific arguments now sees a signature that does not have them and no word about it. The two forms are a lookalike pair the chapter uses without contrasting.

**Proposal:** Add one sentence to the paragraph at line ~349:

> `__exit__(self, *exc: object)` collects the three arguments into a tuple that is never read,
> which is the shorter way to write a cleanup that does not care why the block ended.

**Cost:** none.

---

## 11. The tests listing arrives on a colon belonging to a different sentence

**Kind:** prose
**Where:** section "An Object Pool" (lines ~560-566)
**Problem:** The paragraph contrasting the pool with Flyweight ends "and the lease exists to take it back:" and the colon then introduces `test_object_pool.py`. The colon promises the tests will demonstrate the Flyweight contrast, and they do not; they test lease/return, the exception path, and object identity. The reader reaches the listing expecting one thing and finds another.

**Proposal:** End the Flyweight paragraph with a period, and give the listing its own lead-in:

> Three tests pin down what the lease guarantees: the item leaves the pool and comes back, it comes back even when the block raises an exception, and the pool hands out the same object rather than a new one.

**Cost:** none.

---

## 12. Nothing exercises `ExitStack`, `nullcontext`, or writing a suppressing `__exit__()`

**Kind:** exercise
**Where:** section "Exercises" (line ~598)
**Problem:** Five exercises cover `Trace` nesting, `ignore` with a tuple, `multiple.py`, the pool, and stacked `@banner`. Two of the chapter's eight sections get nothing: "Combining Context Managers"'s `ExitStack` half and the whole `contextlib` toolkit section, including `nullcontext`. Suppression is exercised only by changing an argument to an existing manager, never by writing a `__exit__()` that returns `True`.

**Proposal:** Add two exercises:

> 6.  Write a context manager `retrying` whose `__exit__()` suppresses only `KeyError` and lets everything else through,
>     without using `contextlib.suppress`.
>     Test it with a block that raises a `KeyError` and a block that raises a `ValueError`.
> 7.  Rewrite `exit_stack.py` to take its names from `sys.argv[1:]`,
>     run it with no arguments and with three,
>     and confirm the close order reverses the open order in both cases.

**Cost:** If proposal 9 is rejected, exercise 7 needs rewording against the current fixed-tuple listing.

---

## 13. Small prose corrections

**Kind:** prose
**Where:** throughout
**Problem:** Individually minor, listed together so they can be accepted or rejected as one.

**Proposal:**

- Line ~9: "A context manager marks out a span of execution that determines when initialization and cleanup happen." A span does not determine anything; its two edges are where the setup and cleanup run. Replace with: "A context manager marks out a span of execution, running setup at its start and cleanup at its end."
- Line ~48: "and `finally` runs the cleanup anyway, before the exception propagates" to "and `finally` still runs the cleanup before the exception propagates."
- Line ~131: "so the cleanup happens on the way out" to "so the cleanup runs on the way out."
- Line ~171: "A version with more features" does not say a version of what. Replace with "A fuller version of the same idea reports which exception it swallowed, and accepts no argument to mean 'ignore everything.'"
- Line ~206: "You can still use `as` but it will just bind to `None`." to "You can still write `as`, but it binds `None`."
- Line ~311: "The machinery even applies `functools.wraps`" to "The machinery applies `functools.wraps`."
- Line ~594: "adds refinements on this skeleton" to "adds refinements to this skeleton"; drop the italics on "production pool," which is not a term the book defines.

**Cost:** none. Re-run `make reflow CH=15` after applying.

---

## 14. The first listing uses `yield` eight chapters before generators are taught

**Kind:** structure
**Where:** section "A Basic Context Manager" (lines ~15-51)
**Problem:** Generators are taught in [Iterators](23_Iterators.md#generators). The reader's only prior exposure to a bare `yield` is the pytest fixture in chapter 11. The chapter does connect the two and does forward-link chapter 23, but at line ~49, after the listing and after four paragraphs of explanation. A reader who stalls does so at line ~27, on `yield name`, with the reassurance still a screen away.

**Proposal:** Move the two sentences at lines ~49-51 up to just before the listing, rephrased as an entry point rather than a footnote:

> The `yield` here works the way it does in a `pytest` fixture that [`yield`s its value](11_Testing.md#fixtures-replace-setup-and-teardown):
> everything before it is setup, everything after it is teardown.
> [Iterators](23_Iterators.md#generators) covers generators in full;
> nothing beyond that shape is needed here.

**Cost:** Leaves the paragraph at lines ~45-48 as the section's closing explanation, which reads fine on its own. Alternative, larger: swap the order of "A Basic Context Manager" and "The Protocol" so the class form comes first and needs no forward reference. Not recommended, since the class form is the heavier of the two and opening on it costs more than the forward reference does.

---

## 15. The chapter ends on refinements it does not show

**Kind:** structure
**Where:** section "An Object Pool" (lines ~594-596)
**Problem:** The last words before the exercises are a list of three things a production pool would add, none of which the chapter demonstrates. The reader closes the chapter on what it did not do. Nothing names the capability gained, which is a real one: the reader can now guarantee a paired operation completes on every exit path, including the exception path, and can package that guarantee for other people to use.

**Proposal:** Keep the production-pool sentence and add a short closing paragraph after it:

> Each of those refinements is a change inside `lease()`, invisible to every `with pool.lease()` in the codebase.
> That is what the protocol buys: the borrower's contract is two lines long and cannot be got wrong,
> and everything hard about custody lives on the other side of the `yield`.

**Cost:** none. If a titled closing section is preferred over a trailing paragraph, this text works under a heading such as "What the `with` Block Buys."

---

## Already fixed directly (no decision needed)

- line ~610 (exercise 4): the exercise said "In `object_pool.py`, add a test (alongside the ones in `test_object_pool.py`)," naming the implementation file as the place to add a test and the test file only parenthetically. Changed to "In `test_object_pool.py`, add a test that leases both connections at once, ...".

## Verification run before editing (all clean)

- `uv run ruff check build/examples/15_Context_Managers` — passed.
- `(cd build/examples && uv run ty check 15_Context_Managers)` — passed.
- `uv run pytest build/examples/15_Context_Managers` — 3 passed.
- Every listing executed directly; all `#:` markers match stdout, including `demo_exceptions.py` with `utils/` on `PYTHONPATH`.
- All twelve cross-reference anchors resolve to real headings.
- No em-dashes, no banned phrases.
