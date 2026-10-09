<!-- outside review of Chapters/A_Effect_Tracking.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `A_Effect_Tracking.md` chapter:

**1. What a Checker for the Row Must Do (AST Limitations)**
* **Target Text:** "The `ast` module finds `tell(message.upper())` in `shout()`, and the name `tell` resolves in the module's scope."
* **Issue:** The `ast` module only parses Python code into an abstract syntax tree; it performs no scope analysis or name resolution natively. A static tool cannot rely on `ast` to know that `tell` binds to the module scope; it must implement its own scope rules or use a module like `symtable`.
* **Instruction:** Replace the sentence with: "The `ast` module finds the call to `tell(message.upper())` in `shout()`, but the tool must implement its own scope analysis to resolve the name `tell` in the module's scope."

**2. A Row Inside Annotated (Fragile Introspection API)**
* **Target Text:** `for extra in getattr(result, "__metadata__", ())`
* **Issue:** Since Python 3.9, the officially supported runtime introspection API for generic types and `Annotated` is `typing.get_origin()` and `typing.get_args()`. Relying on the `__metadata__` dunder attribute directly is discouraged and fragile, as the internal layouts of `typing` constructs can change across Python versions.
* **Instruction:** Import `Annotated`, `get_args`, and `get_origin` from `typing`, and replace the target line with: `for extra in (get_args(result)[1:] if get_origin(result) is Annotated else ())`

**3. Find a Place to Run (Runtime Checker False Positive on Handlers)**
* **Target Text:** "On each decorated call, the decorator compares the two rows and raises an exception when the callee's is not a subset of the caller's."
* **Issue:** A function's declared row intentionally omits the effects it handles, but its body still legitimately performs them. A runtime check that strictly requires the callee's row to be a subset of the caller's *declared* row will crash when the body performs an effect the caller handles, completely breaking handler scopes.
* **Instruction:** Replace the sentence with: "On each decorated call, the decorator compares the two rows, but must raise an exception only if the callee performs an Effect that the caller neither declares nor handles. This requires tracking active handlers at runtime, not just declared rows."

## Verdicts

Applied in commit b09bc1c5, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. The old sentence named no actor for the resolution, and `ast` binds no names (Appendix B's `Scope` does that work), but "must implement its own scope analysis" overstates the easy case the paragraph describes. The prose now says `ast` leaves name binding to the tool, which looks `tell` up in `shout()`'s locals and then at the module's top level.
2. Rejected. `__metadata__` is the documented access path: `typing.Annotated.__doc__` on 3.15.0rc2 says "Access the metadata via the ``__metadata__`` attribute" with `assert Annotated[int, '$'].__metadata__ == ('$',)`, and the probe printed `('m', 3)` for `Annotated[int, "m", 3]`. The rewrite returns the same tuple through a longer expression.
3. Applied, with a different fix. A probe decorator that compares the callee's row with the caller's declared row raised an exception (`greet ['Ask']`) for `greet()` called inside `handling(Ask)` within a function whose row is `Tell`; adding the handled Effect to the allowed set made the run pass. The `ContextVar` now holds the running function's row plus the Effect of each enclosing `handling` block, and one sentence says why the `greet()` call needs that term.
