<!-- outside review of Chapters/A_Effect_Tracking.md, model gemini-3.8-flash-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `A_Effect_Tracking.md` chapter:

**1. Section: A Row Inside `Annotated` (Clarification of metadata type domain)**

* **Target Text:** "The arguments after it are *metadata*, and they are values, not types."
* **Issue:** PEP 593 allows arbitrary Python objects as metadata, including classes and types (such as `Ask` and `Tell` passed into `performs(*effects: type)` in this chapter, or direct class references in libraries like Pydantic and FastAPI). The distinction PEP 593 draws is not that metadata cannot be types, but that type checkers treat metadata arguments as uninterpreted runtime objects rather than type expressions to enforce. Stating that they "are values, not types" risks confusing readers who observe types being passed directly into metadata expressions.
* **Instruction:** Clarify that metadata expressions are treated by type checkers as runtime values rather than type expressions, even when the metadata contains types.
Proposed wording: "The arguments after it are *metadata*; type checkers treat them as runtime values rather than type constraints, even when the metadata contains types."

**2. Section: A Row Inside `Annotated` (Consistency with yield-channel effect tracking)**

* **Target Text:** "Stateless and ZIO put their rows in the same place."
* **Issue:** In the preceding sentences, the text argues that the row belongs in the return annotation because "every call produces the return value." However, the table in *The Tracking Problem* and the later analysis in *Tracking Is Not Management* explicitly emphasize that Stateless places its row in the generator's *yield type* (`A` in `Depend[A, R]`), while the return type `R` carries the completed computation's value (e.g., `None` in `Depend[Need[Console], None]`). Saying Stateless puts its row in the same place as ZIO (which uses a standard return type) blurs the yield-versus-return distinction that Stateless relies on for type-checking effects at `yield from`.
* **Instruction:** Clarify that while both place rows in the signature's return annotation, Stateless tracks effects specifically through the generator's yield channel.
Proposed wording: "ZIO puts its row in the return type, and Stateless embeds its row in the return annotation by tracking Abilities through the generator's yield type."

**3. Section: Find a Place to Run (Omission of runtime context restoration)**

* **Target Text:** "On each decorated call, the decorator raises an exception when the callee's row holds an Effect outside that set."
* **Issue:** For the described runtime check to maintain soundness across nested calls, checking the callee's row against the caller's permitted set is only the first step. If the callee is permitted, the decorator must also bind the `ContextVar` to the callee's own declared row (plus any local handlers) for the duration of the callee's execution, and restore the caller's set on exit. Without updating the `ContextVar` during the call, any sub-callee invoked by the callee would mistakenly inherit the outer caller's permitted Effects rather than being bounded by the callee's row.
* **Instruction:** Add a brief mention that the decorator pushes the callee's declared row into the `ContextVar` for the duration of the call.
Proposed wording: "On each decorated call, the decorator raises an exception when the callee's row holds an Effect outside that set, and otherwise scopes the `ContextVar` to the callee's row for the duration of the call."

## Verdicts

Second run, on the Flash model. Applied in commit dd4a1738, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. A probe with `def f() -> Annotated[int, Ask]` showed `__metadata__` holding the class `Ask` itself, and `ty` revealed `def f() -> int`, so "values, not types" was false for a class in the metadata. The sentence now says the type checker reads each piece of metadata as a value, even when it is a class; the PEP's ignore rule stays in the next paragraph, where the chapter already states it.
2. Applied, with a different fix. `stateless/effect.py` defines `Depend: TypeAlias = Generator[A, Any, R]`, so a Stateless row does sit in the return annotation and "the same place" was true, but it read against the table's "The generator's yield type". The sentence now says both libraries put the row in the return annotation, and a second sentence says `Depend[A, R]` is a `Generator` whose yield type is the row `A`.
3. Applied. A probe decorator that checked the callee's row and left the `ContextVar` alone let `sneaky()` (row `Tell`) call `log()` (row `Log`) because the caller's wider set was still in force; setting the `ContextVar` to the callee's row for the call raised an exception (`log ['Log']`), and the `greet()` call inside `handling(Ask)` still passed. The sentence now says the decorator otherwise sets the `ContextVar` to the callee's row until the call returns, and one sentence says that step bounds the callee's own calls by its row.
