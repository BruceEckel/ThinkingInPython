<!-- outside review of Chapters/47_Effects--Stateless_in_Practice.md, model gemini-3.8-flash-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `47_Effects--Stateless_in_Practice.md` chapter:

**1. Section: Abilities Are Not Special (directional correction in code reference)**

* **Target Text:** "the `answer: str` binding inside `ask()`, one line above the `Depend[Ask, str]` that repeats it to callers."
* **Issue:** In `ask_tell_stateless.py`, the return type annotation `Depend[Ask, str]` is declared on line 14 in the function signature `def ask(prompt: str) -> Depend[Ask, str]:`. The `answer: str = yield from Ask(prompt)` binding is on line 15 inside the function body, which is one line below the signature rather than one line above it.
* **Instruction:** Change "one line above the `Depend[Ask, str]` that repeats it to callers." to "one line below the signature's `Depend[Ask, str]` that repeats it to callers."

**2. Section: Composing a Program (clarification of trace output vs. return values)**

* **Target Text:** "Every printed line in that trace comes from a supplied implementation, because the pipeline holds no output of its own, so the trace also records where each run stopped." and "The run at `[4]` prints no trace, since `DeadWire.latest()` raises `Unavailable` without printing anything."
* **Issue:** In `scenarios.py`, the final line of each run (`a history`, `nothing worth researching`, `no article on that topic`, `no headline today`) is the outcome string returned by `report()` and printed by the caller via `print(outcome(...))`. Only the intermediate progress lines (`feed: fetching`, `library: looking up ...`) are printed by the supplied implementations, and claiming run `[4]` "prints no trace" contradicts the output block showing `#: no headline today`.
* **Instruction:** Distinguish the implementations' intermediate progress logging from the returned outcome strings:
  "Every intermediate line in that trace comes from a supplied implementation, because the pipeline holds no progress logging of its own, while the final line is the outcome string returned by `report()`. ... The run at `[4]` prints no intermediate fetching line, since `DeadWire.latest()` raises `Unavailable` without printing anything."

**3. Section: Running Effects in Parallel (channel correction in overload description)**

* **Target Text:** "`fork()`'s four overloads accept an Effect whose Ability channel holds `Never`, an exception type, or `Async`, because `fork()` runs the Effect with `run()` inside the worker."
* **Issue:** Exception types belong to the error channel (`E`), not the Ability channel (`A`). For a forked Effect, the Ability channel is restricted to `Never` or `Async` because dependencies must already be supplied, while the error channel may hold `Never` or an exception type across the four overloads.
* **Instruction:** Update the sentence to separate the channels:
  "`fork()`'s four overloads accept an Effect whose Ability channel holds only `Never` or `Async` (with nothing left to supply), while its error channel holds `Never` or an exception type, because `fork()` runs the Effect with `run()` inside the worker."

**4. Section: The Toolkit (reconciliation of `@throws` behavior)**

* **Target Text:** "`@throws` is an entry point rather than a transformation. It decorates an ordinary function that raises exceptions, turning it into one that returns an Effect."
* **Issue:** This claim contradicts `fetch_effectful.py` in "Composing a Program", where `@throws(Unavailable)` decorates an existing generator function returning `Depend[Need[Feed], str]` to transform its error channel into `Effect[Need[Feed], Unavailable, str]`. It also contradicts Table 2's own description of `@throws(*E)` as adding each `E` to the error channel.
* **Instruction:** Qualify the caveat to acknowledge both usages:
  "`@throws` often acts as an entry point decorating an ordinary function that raises exceptions, but as `fetch_effectful.py` showed, it can also transform a generator function that already returns an Effect by adding exceptions to its error channel."

## Verdicts

Second run, on the Flash model. Applied in commit bb1d1929, after each item was tested against the chapter and run under `uv run`.

1. Applied. In `ask_tell_stateless.py` the signature `def ask(prompt: str) -> Depend[Ask, str]:` comes first and the `answer: str` binding sits on the line after it, so "one line above" was backward; the sentence now says the binding sits one line below the signature's `Depend[Ask, str]`, which states the same type to callers.
2. Applied, with a different fix. The marker shows each run's last line (`a history`, `no headline today`, and so on) printed by `print(outcome(...))`, so "every printed line comes from a supplied implementation" and "`[4]` prints no trace" both contradicted the output beneath them. The paragraph now says each run's last line is the outcome `report()` returns and the lines above it come from the supplied implementations, and that the run at `[4]` prints its outcome alone.
3. Applied. The four overloads in `stateless/async_.py` take `Success[R]`, `Try[E, R]`, `Depend[Async, R]`, and `Effect[Async, E, R]`, so the exception type belongs to the error channel the chapter names separately elsewhere; the sentence now gives the Ability channel as `Never` or `Async` and the error channel as `Never` or an exception type, without the reviewer's "only".
4. Applied, with a different fix. `Throws.__call__` has overloads for both an Effect-returning function and a plain `Callable[P, R]`, and a probe confirmed both: `@throws(KeyError)` on a plain function returned a generator that `ty` reveals as `Generator[KeyError, Any, int]`, while the chapter's own `fetch_effectful.py` shows the Effect case. The caveat now says `@throws` also accepts an ordinary function, so it serves as an entry point as well as a transformation, and that on `fetch_effectful.py`'s kind of function it adds each `E` to that Effect's error channel.
