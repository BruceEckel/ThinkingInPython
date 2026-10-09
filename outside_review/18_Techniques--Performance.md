<!-- outside review of Chapters/18_Techniques--Performance.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `18_Techniques--Performance.md` chapter:

**1. Measuring One Function with `sys.monitoring` (Fictional Constant)**

* **Target Text:** `NO_EVENTS: Final[int] = monitoring.events.NO_EVENTS`
* **Issue:** `sys.monitoring.events` does not define a `NO_EVENTS` attribute. The PEP 669 specification uses `0` as the event bitmask to disable all events. This line will raise an `AttributeError`.
* **Instruction:** Replace the line with `NO_EVENTS: Final[int] = 0` in both `monitoring_counts.py` and `monitoring_coverage.py`.

**2. Measuring One Function with `sys.monitoring` (Invalid Disable)**

* **Target Text:** `return monitoring.DISABLE`
* **Issue:** According to PEP 669, returning `sys.monitoring.DISABLE` only works for location-based events (like `LINE` or `INSTRUCTION`). `PY_START` lacks a specific location and cannot be disabled this way, so the callback will continue firing for every call. 
* **Instruction:** Replace `return monitoring.DISABLE` with `monitoring.set_local_events(TOOL, code, 0)` to dynamically disable the event for that code object, and change the function's return type hint from `object` to `None`.

**3. Measuring One Function with `sys.monitoring` (Trace Behavior)**

* **Target Text:** "since its trace function runs on each call and then on each line:"
* **Issue:** A `sys.settrace()` global trace function only runs on each line if it explicitly returns a local trace callback for that frame. If the global callback returns `None`, the interpreter entirely skips line events for that call.
* **Instruction:** Change to "since its trace function runs on each call, and then on each line unless it explicitly returns `None`:"

**4. Benchmark Alternatives with `timeit` (Lambda Overhead)**

* **Target Text:** "That first argument is a `lambda` here rather than a string of code, since a `lambda` can close over `target`, `as_list`, and `as_set`, with no separate `setup` argument needed to build them."
* **Issue:** A `lambda` introduces Python function-call overhead on every single iteration. In microbenchmarks measuring nanosecond operations like a `set` lookup, this severely distorts the resulting ratio. Passing a string of code alongside `globals=globals()` avoids both the lambda overhead and the `setup` argument.
* **Instruction:** Change to "A string of code passed with `globals=globals()` is faster. This `lambda` avoids a `setup` argument but adds function-call overhead to every iteration, which is acceptable here only because the list scan dominates the time."

## Verdicts

Applied in commit 7131e164, after each item was tested against the chapter and run under `uv run`.

1. Rejected. On 3.15.0rc2, `"NO_EVENTS" in dir(sys.monitoring.events)` is `True` and its value is `0`, and both listings run clean under `tip verify-ch` with their committed markers.
2. Rejected. A probe that returns `monitoring.DISABLE` from a `PY_START` callback under `set_events()` saw one callback for 1,000 calls of the function, and the listing's own marker `1 0` shows the same; `PY_START` is a per-location event that `DISABLE` turns off.
3. Applied, with a different fix. A global trace function that returns `None` received `['call']` alone for a three-line function, so line events come from the local trace function it returns. The sentence now says the trace function runs on each call and the local trace function it returns runs on each line.
4. Applied, with a different fix. Timing `target in as_set` gave about 20 ns per call through the lambda and 13 ns as a string with `globals=globals()`, while the list scan was the same either way, so the lambda inflates `t_set` and the ratio understates the set's lead; the listing's `100x` claim holds either way, and the proposed wording blamed the list side. A new paragraph after the `number` paragraph says so and names the string form for snippets that small.
