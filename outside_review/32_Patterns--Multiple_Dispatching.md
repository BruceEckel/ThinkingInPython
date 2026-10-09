<!-- outside review of Chapters/32_Patterns--Multiple_Dispatching.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `32_Patterns--Multiple_Dispatching.md` chapter:

**1. Operators Dispatch Twice (Factually incorrect type system claim)**

* **Target Text:** "It can do that because it gives `NotImplemented` a type that inherits from `Any`. Returning the sentinel then satisfies any declared return type."
* **Issue:** `NotImplemented` has type `NotImplementedType`, which does not inherit from `Any`. Type checkers allow magic methods to return it because PEP 484 dictates a special hardcoded rule that implicitly permits it, regardless of the method's declared return type.
* **Instruction:** Replace with "It can do that because type checkers have a special rule for magic methods: they silently allow `NotImplemented` as a return value regardless of the declared return type."

**2. Operators Dispatch Twice (Incorrect explanation of type checker operator resolution)**

* **Target Text:** "Pyright and mypy accept the access, because that inheritance from `Any` makes any attribute access on the sentinel branch type-check."
* **Issue:** Type checkers do not use inheritance from `Any` to accept this. Pyright and mypy accept the access because their operator resolution logic correctly models the interpreter's behavior and automatically strips `NotImplementedType` from the expression's final evaluated type.
* **Instruction:** Replace with "Pyright and mypy accept the access because they know how the `+` operator evaluates, and they automatically strip `NotImplementedType` from the expression's final type."

**3. Operators Dispatch Twice (Method annotation vs operator expression type)**

* **Target Text:** "The sentinel is a signal to the interpreter, and no `+` expression evaluates to it, so an annotation that names it describes the wrong thing."
* **Issue:** A method annotation describes the literal return value of the method itself (which can be `NotImplemented` when called directly as `a.__add__(b)`), not the evaluated result of the `+` operator. Naming it is technically accurate for the method; it is omitted purely because PEP 484 instructs type checkers to implicitly assume it.
* **Instruction:** Replace with "The sentinel is a signal to the interpreter, and since type checkers automatically assume magic methods can return it, explicitly adding it to the annotation is redundant."

## Verdicts

Applied in commit 5a7d342a, after each item was tested against the chapter and run under `uv run`.

1. Rejected. Typeshed declares `class NotImplementedType(Any): ...` in `types.pyi` (Pyright's bundled copy, line 720), so the sentinel's type does inherit from `Any`; a probe with `def plain() -> int: return NotImplemented`, an ordinary function and no dunder, passes `ty`, Pyright, and mypy alike, so no magic-method rule is involved.
2. Rejected. With `__add__()` annotated `-> Meters | NotImplementedType`, Pyright and mypy both reveal `Meters(1) + Meters(2)` as `Meters | NotImplementedType`, so neither strips the sentinel from the `+` expression; both also accept `.n` on a variable of that union assigned with no operator, and `.whatever` on `NotImplemented` directly, which is the `Any` inheritance the chapter names.
3. Applied, with a different fix. The reviewer is right that a direct call returns the sentinel (`Meters(3).__add__("four")` printed `NotImplemented` against the extracted `radd_dispatch.py`), but the proposed wording repeats item 1's error, and naming the sentinel is not redundant, since `ty` then rejects `.n`. The sentence now concedes the direct call and says the type checker uses the annotation as the type of the `+` expression, which never evaluates to the sentinel.
