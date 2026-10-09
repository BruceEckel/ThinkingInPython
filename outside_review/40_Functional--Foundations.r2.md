<!-- outside review of Chapters/40_Functional--Foundations.md, model gemini-3.8-flash-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `40_Functional--Foundations.md` chapter:

**1. Section: Higher-Order Functions (clarification of iterator exhaustion)**

* **Target Text:** "`print(map(...))` therefore shows `<map object at 0x...>` instead of values, and a second pass over the same object silently produces nothing."
* **Issue:** Calling `print(map(...))` merely outputs the iterator's `repr` (`<map object at ...>`); it does not iterate over or consume the object. Describing the subsequent traversal as a "second pass" that "silently produces nothing" implies that `print()` performed an initial traversal, whereas an actual first pass (such as `list(...)`) following `print()` still yields all values.
* **Instruction:** Clarify that printing displays the unconsumed iterator and that exhaustion occurs only after a true initial traversal: "`print(map(...))` therefore shows `<map object at 0x...>` instead of values, because `map()` evaluates lazily. Once an initial pass consumes the iterator, a second pass over the same object silently produces nothing."

**2. Section: Closures (distinction between lexical scoping and naming conventions)**

* **Target Text:** "Like the single leading underscore, a closure states an intention that the language does not enforce."
* **Issue:** A leading underscore is a conventional marker on attribute names that Python syntax does not restrict (`obj._field` is always valid). In contrast, lexical scoping is strictly enforced by Python's compiler and runtime: outside code cannot access or rebind `count` by name, and modifying `tally.__closure__[0].cell_contents` manipulates runtime implementation details rather than bypassing an unenforced convention.
* **Instruction:** Replace the sentence with: "Unlike attribute encapsulation, which relies on the single-underscore convention, lexical scoping is enforced by the language: outside code cannot access captured variables by name without inspecting internal cell objects."

**3. Section: Immutability in Annotations (concurrency hazard with mutable backing collections)**

* **Target Text:** "The caller keeps its `list` and can append to it at any time, including from another thread while `total()` is running."
* **Issue:** Annotating a parameter as `Sequence[int]` restricts `total()` from mutating the argument through that reference, but it does not make the caller's underlying list immutable or thread-safe. Appending to a `list` from another thread while `total()` iterates over it (`sum(values)`) is a data race that can raise `RuntimeError: list changed size during iteration` (especially on Python 3.13+ free-threaded builds).
* **Instruction:** Clarify that concurrent mutation remains unsafe: "The caller keeps its `list` and can append to it later, but mutating it from another thread while `total()` is running creates a data race. `Sequence` restricts `total()`'s operations, not the caller's underlying object."

**4. Section: Putting the Pieces Together (discrepancy between inspected record and transformation)**

* **Target Text:** "The `print()` at `[1]` shows what the discipline gives you. The input list stays unchanged, so you can recompute the whole report, cache it, or run it on another core with no coordination."
* **Issue:** Line `[1]` prints `data[0]`, which holds `Reading("a", 18.0)`. Because `18.0 > 20.0` is `False`, `data[0]` was filtered out by `warmer_than` and never reached `to_fahrenheit`. Checking `data[0]` does not demonstrate that the transformation avoided mutating input records in place; to demonstrate that, the check must inspect a record that actually passed through `to_fahrenheit`, such as `data[1]`.
* **Instruction:** In `pipeline.py`, change line `[1]` to `print(data[1])  # [1]` and its marker to `#: Reading(sensor='b', celsius=25.0)`. In the prose, update the description: "The `print()` at `[1]` shows what the discipline gives you: `data[1]` was converted to Fahrenheit for the report, yet the original record in `data` remains untouched at 25.0 Celsius."

## Verdicts

Second run, on the Flash model. Applied in commit c8fc0056, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. `print()` leaves a `map` object unconsumed (`list(m)` after printing it still gave every value, and a second `list(m)` gave `[]`), so "a second pass" had no first pass in its sentence. The sentence now says `print()` displays the iterator's `repr()` and leaves its values uncomputed, and that a second pass comes up empty once a `list()` call or a `for` loop has consumed the iterator.
2. Applied, with a different fix. "a convention" was wrong for a closure: no outside code can name `count`, while any code can write `obj._field`; introspection still reads and rewrites it (`getclosurevars()` gave `{'count': 3}`, and after `cell_contents = 100` the next call returned 101). The paragraph now says a closure's privacy is stronger than a leading underscore's and still short of a guarantee, says why, and keeps the two introspection examples; the underscore comparison sentence went.
3. Rejected. A list raises no `RuntimeError` when it grows during iteration: a `for` loop appending to its own list ran to completion, and `sum()` over a two-million-element list while another thread appended to it printed "sum ok"; "changed size during iteration" is the `dict` and `set` error. The chapter already says "The `Sequence[int]` constraint governs `total()`, not the caller," and the target sentence states the concurrent-append case.
4. Applied. `data[0]` (18.0) is filtered out before `to_fahrenheit()`, so `[1]` showed a record the conversion never touched. `pipeline.py` now prints `data[1]`, marker `Reading(sensor='b', celsius=25.0)`, and the prose says sensor `"b"` appears as 77.0 in the report while its record in `data` still holds 25.0 Celsius.
