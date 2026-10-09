<!-- outside review of Chapters/46_Effects--Stateless.md, model gemini-3.8-flash-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `46_Effects--Stateless.md` chapter:

**1. Section: An Effect Runs Once (API mechanism refinement)**

* **Target Text:** "`catch()`, `throws()`, and `supply()` take functions for the same reason."
* **Issue:** Neither `catch()`, `throws()`, nor `supply()` takes a function directly as its parameter. Each is a decorator factory that takes exception types or dependency instances (e.g., `catch(KeyError)`, `@throws(KeyError)`, `supply(Console())`), and returns a decorator that accepts the function.
* **Instruction:** Change the sentence to: "The decorators that `catch()`, `throws()`, and `supply()` return take functions for the same reason."

**2. Section: One Effect, Many Environments (Test matrix description correction)**

* **Target Text:** "A new `Material` is a new row."
* **Issue:** In [test_nailer.py](file:///C:/git/ThinkingInPython/Chapters/46_Effects--Stateless.md#L817-L835), the parametrized table tests combinations of `Material` and `Nailer` (2 materials × 2 nailers = 4 rows). Adding a new material requires pairing it with each nailer, adding two rows to the matrix rather than one, as Exercise 5 confirms.
* **Instruction:** Change "A new `Material` is a new row." to "A new `Material` is two new rows, one per nailer."

**3. Section: Built-in Dependencies (Clarification of accessor terminology)**

* **Target Text:** "`read_file()` is also the library's own example of both channels at once. Its accessor carries `@throws(FileNotFoundError, PermissionError)` on a function that already returns an Effect,"
* **Issue:** `read_file()` is itself the accessor function for the `Files` dependency, parallel to `print_line()` and `read_line()` for `Console`. Referring to "Its accessor" suggests that `read_file()` owns or wraps an accessor rather than being one.
* **Instruction:** Change "Its accessor carries `@throws(FileNotFoundError, PermissionError)` on a function that already returns an Effect," to "That accessor carries `@throws(FileNotFoundError, PermissionError)` on a function that already returns an Effect,".

**4. Section: Emptying the Channels (Type subtraction precision)**

* **Target Text:** "`supply()` removes an Ability and leaves `Never` in its place. `catch()` removes an error and moves it into the result, where a `match` must account for it."
* **Issue:** When an Effect carries multiple Abilities or errors (as shown in [audit_log.py](file:///C:/git/ThinkingInPython/Chapters/46_Effects--Stateless.md#L714-L744) and [catch_subset.py](file:///C:/git/ThinkingInPython/Chapters/46_Effects--Stateless.md#L1326-L1353)), handling one Ability or catching one error subtracts it from the union and leaves the remaining Abilities or errors in the channel. The type parameter reduces to `Never` only when the channel's final requirement is discharged.
* **Instruction:** Change the text to: "`supply()` subtracts an Ability from the union, leaving `Never` once all Abilities are answered. `catch()` removes an error and moves it into the result, leaving `Never` in the error channel once all errors are caught."

## Verdicts

Second run, on the Flash model. Applied in commit 3572bcd2, after each item was tested against the chapter and run under `uv run`.

1. Applied. Under `uv run ty`, `catch(KeyError)` reveals `Catch[KeyError]`, `throws(KeyError)` reveals `Throws[KeyError]`, and `supply(...)` reveals a `Handler`, each a callable that takes the function, so "take functions" misstated them beside the precise `repeat()`/`retry()` sentence above it; the sentence now reads "`catch()`, `throws()`, and `supply()` return decorators over functions for the same reason."
2. Applied, with a different fix. `test_nailer.py` crosses two materials with two nailers, and exercise 5 asks for `Metal`'s "two rows", so "A new `Material` is a new row" undercounted; it now reads "A new `Material` adds one row for each nailer."
3. Applied, with a different fix. `stateless/files.py` defines both a `Files.read_file()` method and the module-level `read_file()` accessor that carries `@throws(FileNotFoundError, PermissionError)`, so "`read_file()` ... Its accessor" pointed at the wrong one; the paragraph now opens "The `read_file()` accessor in `stateless.files` is also the library's own example of both channels at once. It carries ...".
4. Applied, with a different fix. A `ty` probe revealed `supply(Material(strength=5))(holds)` as `() -> Generator[Need[Nailer], Any, bool]`, so supplying one of two Abilities leaves the other in the channel, not `Never`; the `supply()` sentence now reads "removes an Ability from the union, and the channel reads `Never` once the last Ability is answered." The `catch()` sentence makes no `Never` claim and stays as written.
