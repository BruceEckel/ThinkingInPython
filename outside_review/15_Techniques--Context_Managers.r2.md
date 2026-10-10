<!-- outside review of Chapters/15_Techniques--Context_Managers.md, model gemini-3.8-flash-high, 2026-10-10 -->

Please apply the following technical and structural refinements to the `15_Techniques--Context_Managers.md` chapter:

**1. Section: The `expect()` Function (Misdescribed async invocation)**

* **Target Text:** "`aexpect()` is the `async` form. It awaits the call instead of making it, for a coroutine function whose failure is the demonstration."
* **Issue:** `aexpect()` does not await the call "instead of making it". In `await fn(*args, **kwargs)`, calling `fn` is necessary to invoke the coroutine function and obtain the awaitable object, which is then awaited.
* **Instruction:** Clarify that the call is made and its returned coroutine is awaited: "`aexpect()` is the `async` form. It calls `fn` and awaits the returned coroutine, for a coroutine function whose failure is the demonstration."

**2. Section: The Async Protocol (Misleading listing introduction)**

* **Target Text:** "`contextlib.asynccontextmanager` builds such a manager from an async generator, the same way `@contextmanager` builds the synchronous form, and `AsyncExitStack` is the `ExitStack` equivalent:"
* **Issue:** The sentence ends with a colon introducing `async_manager.py`, but that listing only demonstrates `@asynccontextmanager` and never imports or uses `AsyncExitStack`. Mentioning `AsyncExitStack` immediately before the colon misleads the reader into expecting it in the listing below.
* **Instruction:** Separate the introduction of `asynccontextmanager` from `AsyncExitStack`: "`contextlib.asynccontextmanager` builds such a manager from an async generator, the same way `@contextmanager` builds the synchronous form (and `AsyncExitStack` is the `ExitStack` equivalent):" or move the `AsyncExitStack` mention after `async_manager.py`.

**3. Section: The Async Protocol (Imprecise protocol terminology)**

* **Target Text:** "`async with` calls `__aenter__()` and `__aexit__()`, which are coroutines, so the setup and the cleanup can both await."
* **Issue:** Under the asynchronous context manager protocol (PEP 492), `__aenter__()` and `__aexit__()` are methods that return awaitables (such as coroutine objects); they are not coroutines themselves.
* **Instruction:** Adjust the wording to state that the methods return awaitables that are awaited: "`async with` calls `__aenter__()` and `__aexit__()` and awaits their returned awaitables, so the setup and the cleanup can both await."

## Verdicts

Second run, on the Flash model. Applied in commit 42e90972, after each item was tested against the chapter and run under `uv run` on 3.15.0rc2.

1. Applied, with a different fix. `utils/exceptions.py`'s `aexpect()` runs `await fn(*args, **kwargs)`: the call is made and its coroutine awaited, so "instead of making it" misdescribed the helper. The sentence now reads "It calls `fn` and awaits the coroutine the call returns", naming what the call returns rather than "the returned coroutine".
2. Applied, with a different fix. `async_manager.py` imports `asynccontextmanager` alone and never names `AsyncExitStack`, so the colon promised a listing that shows it. The intro sentence now ends at the `@contextmanager` comparison, and `AsyncExitStack` moves to the paragraph after the listing, beside the Concurrency chapter's `async with` objects, rather than into a parenthesis before the colon.
3. Applied, with a different fix. PEP 492 defines `__aenter__()` and `__aexit__()` as methods returning awaitables, and the generated manager's are `async def` methods whose calls return coroutines, so "which are coroutines" named the result rather than the methods. The sentence now says `async with` "calls `__aenter__()` and `__aexit__()` and awaits what they return", shorter than "awaits their returned awaitables".
