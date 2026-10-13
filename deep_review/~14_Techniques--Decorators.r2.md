> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 14_Techniques--Decorators (2026-10-13)

No live blocks.
I read the chapter and its Solutions file against `deep_review_db.md` and the completed review `~14_Techniques--Decorators.md`, and re-probed every checker claim on `ty` 0.0.86 and Pyright 1.1.414 under Python 3.15.0 (uv's managed build).
All of the chapter's `ty` claims still hold: `unresolved-attribute` on `func.__name__` for a `Callable`, both diagnostics for the unparenthesized `@repeat`, `missing-argument` plus `invalid-argument-type` for `trace_class.trace` on a method, `Any` for `Espresso()` under `(cls: type) -> type`, `Unknown` for the `@lambda` result, `invalid-return-type` for a wrapper missing its `return`, and `unresolved-attribute` on a function attribute.
Each Solutions near-miss also checks out when run: exercise 1's `invalid-return-type`, exercise 4's `invalid-attribute-access` and its `2 1 0`, exercise 5's unhashable-`dict` `TypeError`, and exercise 6's `invalid-return-type` for the bare-`raise` version.
`functools.WRAPPER_ASSIGNMENTS` matches the prose, and the coroutine trace line prints as quoted.
mypy is not installed, so I could not re-check "Pyright and mypy both accept the attribute here".
`tip verify-ch CH=14 ISOLATED=1` passed 27 of 27 before and after the edits.

## Applied directly

Chapter, corrections and teaching:

- "Decorators You Already Know": `@property`, `@cached_property`, `@staticmethod`, and `@classmethod` "wrap a function the same way `trace` does, but return a descriptor". All four are classes whose instance holds the function (checked at runtime), which is the class form, not `trace`'s closure. The sentence now calls them class-form decorators like `trace_class.trace` that also implement `__get__()`, which ties back to the `logged` limitation.
- "A Limitation: Methods Need a Descriptor": "the descriptor protocol, which a class-based decorator must implement to work on methods" contradicted the same section's `repeat_class.repeat`, which works on methods with no `__get__()`. Now "the `__get__()` that `logged` would need to work on methods."
- Same section: "`trace_class.py` and `count_calls.py` decorate bare functions on purpose:" led into a listing about a different class. Now says those two decorate module-level functions for that reason, and that `logged` has the same shape and fails on a method.
- "Decorators With Optional Parentheses": the `callable(func)` paragraph gave its reason last, after a semicolon, and the reason applied to keyword-only arguments, not to the recommended test. Rewritten in order: what breaks the assumption (a callable decorator argument passed positionally), why neither test can catch it, and what such a decorator does (keyword-only arguments, `func is None`). Same advice; the listing change is recorded below.
- `@lambda`: added what Pyright does. It keeps the `def`'s type, `() -> list[int]`, so it accepts `fib_table()` (a runtime `TypeError`) and rejects `fib_table[0]` (which works). The project rule is that a sentence true of `ty` alone names `ty` and says what the other checkers do; mypy was not available to check.
- The overhead paragraph (an extra frame and an extra call per wrapper) moved from the end of "Decorators You Already Know", where it sat outside the section's topic, to "Stacking Decorators", after "the layers compose to any depth". It now says a traceback shows one `wrapper` frame per layer, and the chapter closes on the forward pointer to the descriptor protocol.
- The *Singleton* paragraph ("A decorator can replace a class the same way") moved up to follow the `run_once` paragraphs. The `@lambda` material had been inserted between them, so "the same way" pointed at `@lambda`.
- "Decorators as Classes": "The class form is a better choice when the decorator takes arguments" and, 40 lines later, "the class form is typically easier to reason about" said the same thing. The second sentence was cut. The first now reads "easier to follow than the function form" and carries the link to the function-form section, since "Function Form or Class Form?" calls the choice mostly taste.
- `optional_parens.py` now tests `func is None` instead of `callable(func)`, matching Solutions exercise 5 and chapter 18's `record`; the walkthrough and the following paragraph are rewritten around the stricter test, with the `@label("TAG")` case showing what `callable()` lets through (session decision, 2026-10-13).

Chapter, prose:

- The first mention of the *Decorator* pattern now links its section in this chapter.
- "collects the call with `*args, **kwargs` and forwards it" is now "collects the arguments ... and forwards them".
- "`add_behavior` is limited to functions that take none" (passive) is now "works only on functions that take none".
- Paragraph splits at the seams: what `wraps` copies vs. `__wrapped__`; what goes wrong with a coroutine function vs. the `async` wrapper that fixes it; why the function form works on methods vs. what the type checker reports for the class form; why to avoid `@lambda` vs. what the checkers make of it.

Solutions:

- Exercise 7: "the `TypeError` `method_decoration.py` shows" implied the same message, but `counter.peek()` reports a missing `self` where `method_decoration.py` reports a missing `x`. Now names it as the same failure with a different missing argument.
- Exercise 6: "`@wraps(func)` keeps the identity" restated its bold label. Now says what `wraps` copies and that `flaky.__name__` reports `flaky`. Rewrapped to the file's width.
- Exercise 5: "since `add(1, 2)` and `add(a=1, b=2)` are different keys and both are legal calls" put the consequence before the cause. Now gives the cause (a caller can pass an argument either way) and then the result.
- Exercise 3: the `Decaf` paragraph also held the add-a-fourth-extra point; split into two paragraphs.

## Considered and declined

- "Since Python 3.9 (PEP 614)" is a language-version note in a 3.15 book, but chapters 03, 08, and 26 use the same form, and it dates a language feature, not a tool caveat.
- "The nesting stops at two levels, matching the two nested `def`s in the source" ties two things loosely: the two decorator applications and the two inner `def`s. It is not wrong, and cutting it would leave the reader asking whether `wraps` recurses.
- "A class for every pizza-and-topping combination explodes" is figurative, but the next sentence ("Each new topping doubles the menu") states the mechanism.
- Vale's remaining passives, "is applied bare" (the `trace` versus `repeat` contrast) and "must be handed elsewhere as a `Pizza`", read naturally, and each has a real subject.
- `count_calls.py` has an explanatory comment ("The state lives on the decorator instance"), and `trace_class.py` has "Copy __name__, __doc__, etc". Both are short, they sit beside the line they explain, and an earlier review left them.

## For the session

- `tip grounding-triage` was not run. Two edited sentences link chapter 17 (`#learning-a-name-with-__set_name__`, now "the `__get__()` that `logged` would need") and chapter 24 (the moved *Singleton* paragraph, text unchanged).
- `tip prose CH=14` reports one stale `internal_names` baseline entry outside this chapter: `Examples/15_Techniques--Context_Managers/banner_cm.py::banner.title`.
- mypy is not installed in the project environment, so the chapter's "Pyright and mypy both accept the attribute here" was not re-verified for mypy (Pyright 1.1.414 accepts it).
