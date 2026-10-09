<!-- outside review of Chapters/23_Patterns--Iterators.md, model gemini-3.8-flash-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `23_Patterns--Iterators.md` chapter:

**1. Section: An Exhausted Generator Is Silently Empty (technical accuracy regarding iterator exhaustion)**

* **Target Text:** "An exhausted generator produces nothing and raises nothing, so the empty `list(sq)` leaves no error to point at the bug."
* **Issue:** An exhausted generator does not "raise nothing"; calling `next()` on it raises `StopIteration`. The call `list(sq)` returns an empty list without error because `list()` catches and absorbs `StopIteration` as the normal termination signal, exactly as a `for` loop does.
* **Instruction:** Clarify that the generator raises `StopIteration` and `list()` absorbs it: "An exhausted generator raises `StopIteration` immediately, which `list()` absorbs as normal termination, leaving no error to point at the bug."

**2. Section: What tee() Buffers (correction of non-existent standard library symbol)**

* **Target Text:** "[Concurrency](19_Techniques--Concurrency.md#sharing-an-iterator-between-threads) covers `threading.concurrent_tee()`, the thread-safe version, along with what goes wrong when two threads call `next()` on the same iterator."
* **Issue:** Python's standard `threading` module does not provide a `concurrent_tee()` function. Referring to `threading.concurrent_tee()` presents it as a standard library function alongside `itertools.tee()`, whereas it is a custom helper introduced in the linked concurrency chapter.
* **Instruction:** Remove the `threading.` module prefix from the reference: change "`threading.concurrent_tee()`" to "`concurrent_tee()`".

**3. Section: Reusable Algorithms (factual precision on skipping versus stopping)**

* **Target Text:** "Skipping and stopping look the same on finite data and behave nothing alike on infinite data."
* **Issue:** Skipping (`filter()` or a comprehension `if` clause) and stopping (`takewhile()`) only yield identical results on finite data when matching items precede all non-matching items (such as pre-sorted or monotonic data). On unsorted finite data (for example, `[1, 5, 2]` with predicate `< 3`), skipping produces `[1, 2]` while `takewhile()` stops at `5` and produces `[1]`.
* **Instruction:** Qualify the condition under which they yield identical results: "Skipping and stopping look the same on sorted or partitioned finite data, but behave nothing alike on infinite data."

**4. Section: A Type-Checking Iterator (type checker handling of parameterized generics)**

* **Target Text:** "The type checker also accepts a parameterized generic such as `list[int]`, but `isinstance()` raises a `TypeError` when it receives one, so either wrapper fails at the first item."
* **Issue:** A parameter typed as `expected: type[T]` requires an actual class object (`type`). A parameterized generic like `list[int]` is a `types.GenericAlias`, which static type checkers reject when passed to a `type[T]` parameter (confirm with a `ty` run).
* **Instruction:** Update the sentence to state that type checkers reject parameterized generics for `type[T]`: "The type checker rejects a parameterized generic such as `list[int]` because `type[T]` requires a concrete class, and `isinstance()` would raise a `TypeError` on it at runtime in any case."

## Verdicts

Second run, on the Flash model. Applied in commit db196455, after each item was tested against the chapter and run under `uv run`.

1. Applied. A probe showed `next()` on the drained `sq` raises `StopIteration` while `list(sq)` returns `[]`, so "raises nothing" was wrong about the protocol the chapter opens with (line 50: "A loop absorbs `StopIteration` as the normal end"). The sentence now says the exhausted generator raises `StopIteration` at the first `next()` and `list()` absorbs it as the normal end.
2. Rejected. `uv run python -c "import threading; print(threading.concurrent_tee)"` prints `<function concurrent_tee ...>` on 3.15.0rc2: the function is in the standard library, new in 3.15, and chapter 19's `concurrent_tee.py` calls `threading.concurrent_tee(numbers(100), READERS)` and says it "arrived in 3.15".
3. Applied, with a different fix. `[x for x in [1, 5, 2] if x < 3]` gives `[1, 2]` and `takewhile()` gives `[1]`, so "look the same on finite data" overreached; the condition that matters is values that stop matching for good, which the paragraph's "once values stop matching" already sets up, rather than the reviewer's "sorted or partitioned". The sentence now reads "On finite data whose values stop matching for good, as the rising squares do, skipping and stopping give the same result. On infinite data they behave nothing alike."
4. Rejected. `ty` reports "All checks passed!" on `typed([[1]], list[int])` and `TypedIterator(iter([[1]]), list[int])` against the extracted listings, so the type checker accepts the parameterized generic, as the chapter says; the first round's item 4 verdict found the same and added the sentence the reviewer would reverse.
