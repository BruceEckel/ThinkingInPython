<!-- outside review of Chapters/23_Patterns--Iterators.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `23_Patterns--Iterators.md` chapter:

**1. The Costs of Laziness (Excluding safe custom iterables)**

* **Target Text:** "`Collection[T]` and `Sequence[T]` also require `__len__()`, which no generator has, so the type checker rejects the generator at the call instead of letting it run wrong."
* **Issue:** While requiring `Collection[T]` correctly stops exhausted generators from passing type checks, it also inadvertently rejects safe custom iterables like the chapter's own `Countdown` class, which lacks `__len__()` and `__contains__()`. Because Python's type system lacks a built-in `Reiterable` protocol, using `Collection[T]` forces callers to implement unrelated methods just to satisfy the type checker.
* **Instruction:** Add a caveat immediately following this sentence: "However, this also rejects custom iterables like `Countdown` that are safe to walk twice but lack `__len__()` and `__contains__()`. Because Python has no `Reiterable` protocol, you must weigh type safety against forcing callers to implement unrelated methods."

**2. Delegating with `yield from` (Retrieving the dropped return value)**

* **Target Text:** "The `yield from` expression, however, has a value. `result = yield from inner()` binds whatever `inner()` returned when it stopped. The hand-written loop drops that value."
* **Issue:** The text explains that the `for` loop silently drops the return value of a delegated generator, but leaves unnamed the actual mechanism to retrieve it manually. A reader who needs to inspect the return value without using `yield from` needs to know that this value is attached to the `StopIteration` exception.
* **Instruction:** Add an explanation after this sentence: "To catch that value without `yield from`, you must abandon the `for` loop, call `next()` manually inside a `try`/`except StopIteration` block, and read the exception's `value` attribute."

**3. Reusable Algorithms (`takewhile` boundary item consumption)**

* **Target Text:** "`takewhile()` stops at the first failure. Skipping and stopping look the same on finite data and behave nothing alike on infinite data."
* **Issue:** Because "Asking Consumes an Item" (as explained later in the chapter), `takewhile()` must pull the first failing item from the iterator to evaluate its condition, permanently discarding it. If a programmer uses `takewhile()` on a stream and then continues reading from that same stream, the boundary item is silently missing, which is a common and dangerous trap.
* **Instruction:** Add a caveat following this text: "However, `takewhile()` must pull and discard the first failing item to test it. If you continue reading from the same iterator after `takewhile()` finishes, that boundary item is permanently lost."

**4. A Type-Checking Iterator (Runtime failure with generic types)**

* **Target Text:** "Both take `expected: type[T]`, so the type checker carries the element type through."
* **Issue:** Because the wrappers use `isinstance()` internally, passing a parameterized generic type like `list[int]` as the `expected` argument will raise a `TypeError` at runtime (e.g., `TypeError: isinstance() argument 2 cannot be a parameterized generic`). The implementation only works at runtime for bare classes or union types, not subscripted generic types.
* **Instruction:** Add a cautionary sentence after this one: "Be aware that because this relies on `isinstance()` at runtime, `expected` must be a bare class (like `list`) or a union type. Passing a parameterized generic like `list[int]` will raise a `TypeError` at runtime."

## Verdicts

Applied in commit 37dd744a, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. `ty` rejects `twice_collection(Countdown(3))` ("protocol member `__contains__` is not defined on type `Countdown`") while the call returns `(6, 6)` at runtime, so the advice to annotate with `Collection[T]` excludes the reiterable class the chapter recommends two paragraphs earlier. A new paragraph after the `total()` sentence names the cost: `Countdown` lacks `__len__()` and `__contains__()`, `collections.abc` has no "iterable more than once" protocol, and a reiterable class passes by adding the two methods.
2. Rejected. The chapter links [Generators](45_Effects--Generators.md#yield-from-composes-descriptions) for the return channel, and that chapter says it ("the `Result` arrives as that exception's `value`... To read the `ReturnType`, catch the exception yourself"), with `except StopIteration as stop: result = stop.value` in `interview_generator.py`; a second explanation here duplicates it.
3. Rejected. Neither `reusable_algorithms.py` nor `test_endless.py` reads a source after `takewhile()` finishes, and [Functional Toolkits](41_Functional--Toolkits.md#the-itertools-toolkit), which this chapter links in the same section, demonstrates the lost boundary item in `itertools_pipeline.py` (the source resumes at 16, not 13, because `takewhile()` pulled and discarded the 590 total).
4. Applied, with a different fix. `typed([[1]], list[int])` raises `TypeError: isinstance() argument 2 cannot be a parameterized generic`, and `ty` accepts the call for both `typed()` and `TypedIterator`. The reviewer's "or a union type" is wrong for the type checker: `typed([1, "a"], int | str)` draws `invalid-argument-type` ("Expected `type[Unknown]`, found `<types.UnionType ...>`"). A new paragraph says `expected` must be a class and that a parameterized generic passes the type checker and raises a `TypeError` at the first item.
