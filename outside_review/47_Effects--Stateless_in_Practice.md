<!-- outside review of Chapters/47_Effects--Stateless_in_Practice.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `47_Effects--Stateless_in_Practice.md` chapter:

**1. Section: Switching Implementations Mid-Run (Context managers inside generators)**
* **Target Text:** "since the block opens and closes between two `yield from` expressions in the same function."
* **Issue:** Yielding inside a `with` block has a known caveat in Python: if the generator is abandoned before exhaustion (e.g., if the driver drops it due to an error elsewhere) and `.close()` is not explicitly called, the context manager's `finally` block will not execute until the generator is garbage collected.
* **Instruction:** Add the following sentence after the target text: "One caveat applies: if the driver abandons the generator without calling `.close()`, the context manager's exit logic might not execute until garbage collection."

**2. Section: What Retry Costs the Signature (`ExceptionGroup` vs custom wrappers)**
* **Target Text:** "and `outcome.errors` raises `AttributeError`."
* **Issue:** Since the book targets Python 3.15, readers should be aware that Python 3.11 introduced `ExceptionGroup` natively for this exact purpose. Pointing this out highlights the gap between older library designs and modern Python error-handling standards.
* **Instruction:** Add the following sentence: "In modern Python, you would expect a system to wrap repeated failures in an `ExceptionGroup` so you can handle them with `except*`, but this library relies on its own exception class."

**3. Section: Running Effects in Parallel (Picklability of forked Effects)**
* **Target Text:** "Supplying a `ProcessPoolExecutor` moves the same work into processes, and `squares()` stays as written."
* **Issue:** `ProcessPoolExecutor` uses `pickle` to send tasks across process boundaries. If the `@fork` decorator creates an unpicklable closure, or if the arguments passed to the Effect cannot be serialized, the process pool will crash. This is a critical technical caveat when migrating from threads to processes in Python.
* **Instruction:** Add the following sentence after the target text: "Note that processes require the forked function to be picklable. If the `@fork` decorator or the Effect's arguments cannot be serialized by Python's `pickle`, the pool will crash."

**4. Section: `run()` Builds a Loop per Call (Environments with persistent loops)**
* **Target Text:** "`asyncio.run()` raises a `RuntimeError` before your Effect runs:"
* **Issue:** Many readers run and test code interactively in Jupyter notebooks or IPython REPLs. These environments run a persistent `asyncio` event loop in the background, meaning `run()` will immediately hit this error on the very first try unless they apply a workaround.
* **Instruction:** Add the following sentence after the target text (before the `run_cost.py` trace): "If you run this in a Jupyter notebook, an event loop is already active in the background, so `run()` will hit this error immediately unless you use `nest_asyncio`."

## Verdicts

Applied in commit 9ab0c5ed, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. Stateless's `run()` throws a yielded error back into the generator, so a `with` block's exit runs, but `handle()` lets a handler's exception propagate past the suspended generator: a probe whose handler raised an exception while a `with` block was open printed "close" only at `gc.collect()`, after the `except` clause and the enclosing function had finished. `microgrid.py` never reaches that case (`plug()` sits outside the `with` block, and a probe run ending in `Blackout` printed "Solar offline" first), so a new paragraph after the `Blackout` paragraph says so and states the general case for a handler that raises an exception inside an open block.
2. Rejected. A style comment about library design rather than a correction: `RetryError` subclasses `Exception` (its MRO is `RetryError, Exception, BaseException, Generic, object`), which the paragraph already treats as the library's own class, and the proposed sentence attributes an expectation to the reader rather than stating a mechanism.
3. Rejected. `fork()` serializes the function, its arguments, and its result with `cloudpickle`, which handles closures, so the decorator is not the risk; a probe running `squares()` under a `ProcessPoolExecutor` printed `[0, 1, 4, 9, 16]`, and forking with a `threading.Lock()` argument raised a `TypeError` ("cannot pickle '_thread.lock' object") in the driver at the `fork()` call while the pool went on to serve the next run. The listing's arguments are `int`s, and exercise 8 already covers the switch to processes and the `__main__` guard.
4. Rejected. The chapter already states the rule this case falls under: `run()` raises a `RuntimeError` "from inside a running loop", and the table directly above says to call `await run_async(effect)` there, which works in a notebook's top-level `await`; recommending the third-party `nest_asyncio` patch is tooling outside the book's scope.
