> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 14_Techniques--Decorators (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I checked each claim against its listing, against the sections the chapter links (chapters 5, 7, 8, 12, 15, 17, 18, 19, 24, 27, 29, 40), with runtime probes on the pinned 3.15.0rc2, and with `ty` 0.0.84, Pyright, and mypy probes.
Every checker claim in the chapter holds today: `ty` rejects `func.__name__` on a `Callable` while Pyright and mypy accept it, `ty` reports both diagnostics for the unparenthesized `@repeat` and for `trace_class.trace` on a method, and `ty` and Pyright both reveal `Any` for `Espresso()` under a `(cls: type) -> type` decorator.
`tip verify-ch CH=14` passes 24 of 24, and `tip verify` and `tip exercise-refs` pass in the worktree.

## Applied directly

Chapter, corrections:

- "What `@` Does": "`announce` runs while Python is still executing the `def` above `cheese`" pointed at a `def` that is not above `cheese`; it is the `def` for `cheese()`. Now "runs when Python executes the `def` for `cheese()`, before any call."
- "Decorators You Already Know": "the descriptor protocol those first four return" said a decorator returns a protocol. Now "implement".
- Same section: `functools.cache` and `lru_cache` "wrap a function in the same closure-plus-`func` shape as `add_behavior`". CPython's `lru_cache` returns a C `_lru_cache_wrapper` object, not a closure. Now "wrap a function the way `add_behavior` does, in a wrapper that holds `func` and calls it", which is true of both implementations.
- "What `@` Does Not Require": "The name that follows `class` then refers to an object, not a type" (a type is an object too). Now "refers to that callable object, not to a class."
- "The Decorator Pattern": "The list stores toppings; the decorator chain *is* one" had italics for emphasis and an "one" with two candidates (a topping, a pizza). Now two sentences: a list of toppings is data a pizza holds, and a decorator chain is a pizza.

Chapter, teaching:

- `test_tracer.py` and its lead-in moved up to the end of "`wraps` Keeps the Runtime Interface". Both assertions are runtime facts (the name, the result), and the test sat three topics away from `tracer.py`.
- New subheading "A Coroutine Function Needs an `async` Wrapper" (`{#coroutine-needs-async-wrapper}`) over the `async def` paragraph, which was filed under "`**P` and `R` Keep the Static Interface" and is about runtime behavior.
- Near-miss added to the `**P` and `R` section: a wrapper that calls `func` without returning the result makes every decorated function return `None`, and `-> R` lets the checker report it (`ty`: `invalid-return-type`; Pyright agrees).
- The forgotten `return wrapper` paragraph now names the symptom the reader will see, a `TypeError` saying a `NoneType` object is not callable.
- "A Class Decorator with State": a reader could conclude that only the class form holds state. Added that the function form keeps a count in a closure variable (link to chapter 40's Closures, which shows `nonlocal`), visible only inside the closure, while `hello.count` is readable by any caller.
- "A Class Decorator with Arguments": `repeat_class.py`'s `wrapper()` differs from `repeat.py`'s (first call before the loop) with no explanation. One sentence now says why.
- Exercise 7 added, with its solution (`decorated_methods.py`). The chapter asserts that `repeat_class.repeat` works on methods and never shows it; the method limitation is "the one hard reason to choose the function form" and had no exercise. The solution decorates one method with `repeat` and one with `logged` and prints what the class stores under each name. `pyproject.toml` gained one `N801` per-file ignore for the listing, as the other lowercase decorator classes have.

Chapter, prose:

- "cross-cutting concerns" is introduced in the first paragraph; now italic.
- "The `# type: ignore` comments mark where `ty` cannot follow" described a correct diagnostic as a limitation. Now says the comments silence a `ty` diagnostic, and why `ty` reports it.
- "tell the type checker the same story the runtime branch tells" is now "state for the type checker what the runtime branch does".
- "`@` constrains the statement below it and nothing else": tag removed, since the next three sentences spell out the exclusion.
- "Classes collapse the same way" is now "A decorator can replace a class the same way."
- "Because that check already guarantees": "already" removed.

Solutions:

- Exercise 1: the prose said a decorator that returns its argument cannot change the class, then offered `@dataclass` as one that "does change it, returning a class with generated methods". `@dataclass` returns the class it received, which the chapter says in "Decorators You Already Know". Rewritten around what the decorator does to its argument and what it returns, with a link for `@singleton`.
- Exercise 1: `announce[T: type](cls: T) -> T` is now `announce[T](cls: type[T]) -> type[T]`, the form `register.py` teaches.
- Exercise 2: the four-line comment inside `timing` repeated the parenthetical in the prose below it. Removed.
- Exercise 5: "is what keeps the two calls unambiguous" is now "keeps"; "lands in `func`" is now "binds to `func`".
- Exercise 6: "rather than re-raising a copy" was wrong, since a bare `raise` re-raises the same exception object. Now "with no handler in its way", and the type-checker sentence says what `ty` reports (`wrapper()` can implicitly return `None`), verified with a probe.
- Exercise 4: "the `trace_counting` class itself" lost "itself".

## Considered and declined

- `repeat.py` returns a `result` bound inside the loop, which Pyright reports as possibly unbound (it is in `pyright_baseline.txt`). `ty` accepts it, the prose states the guarantee, and `repeat_class.py` shows the other form, so both stay.
- `Margherita` and `Hawaiian` hold `cost` and `description` as unannotated class attributes while `Topping.add_cost` is `ClassVar[float]`. Annotating them would add a second topic to the paragraph that explains how a class attribute satisfies a read-only `Protocol` property.
- An `async`-aware `trace` listing. `asyncio` is taught in chapter 19, and the paragraph is a forward pointer.
- Decorator names written bare in prose (`trace`, `repeat`, `hijack`) where function references elsewhere take `()`. The chapter names a decorator as it appears after `@`, consistently.
- `functools.partial` in the list of lowercase classes is not a decorator, but it is a class used like a function, which is the reason the sentence gives.
- PEP 614 (any expression after `@`) would fit "What `@` Does Not Require", but no listing in the book needs it.
- Exercise 2's solution carries a shortened `trace` that prints the `args` tuple. It serves the ordering question the exercise asks.
