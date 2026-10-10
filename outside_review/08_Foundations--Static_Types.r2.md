<!-- outside review of Chapters/08_Foundations--Static_Types.md, model gemini-3.8-flash-high, 2026-10-10 -->

Please apply the following technical and structural refinements to the `08_Foundations--Static_Types.md` chapter:

**1. Section: Narrowing (Misdescribed control flow)**

* **Target Text:** "Inside the `if`, the type checker *narrows* `text` from `str | None` to `str`, so `.upper()` needs no cast. Outside the `if`, `text` is still the full `str | None`."
* **Issue:** In `narrowing.py`, the `if` body contains an unconditional return (`return text.upper()`). Under control-flow analysis, the type checker narrows `text` to `None` on the fallthrough rather than leaving it as `str | None`.
* **Instruction:** Correct the second sentence to reflect that the branch exits: "Outside the `if`, because that branch returns, the type checker narrows `text` to `None`; it would remain `str | None` only if the `if` block did not exit."

**2. Section: Generic Functions and Classes (Invalid syntax for type constraints)**

* **Target Text:** "A *constraint* lists unrelated choices: with `[T: (int, str)]`, `T` is `int` or `str`, and an argument of a subclass of `int` binds `T` to `int`."
* **Issue:** PEP 695 type parameter syntax (`class Box[T]`, `def f[T]`) does not support constraints. The expression following the colon specifies only an upper bound, and type checkers reject a tuple like `(int, str)` as an invalid bound. In modern Python (including Python 3.15), type constraints must still be declared using `typing.TypeVar`.
* **Instruction:** Replace the sentence with: "PEP 695 bracket syntax supports bounds but not constraints; to restrict a type parameter to specific unrelated choices, declare a constrained `TypeVar` instead: `T = TypeVar("T", int, str)`."

**3. Section: Variance (Conflation of generic parameter with concrete base class)**

* **Target Text:** "Annotating a parameter `Sequence[T]` instead of `list[T]` declares that the function reads its argument and leaves it as it was, so the function accepts arguments that a `list[T]` parameter rejects. A `list[T]` is *invariant* in `T`, and a `Sequence[T]` is *covariant*."
* **Issue:** In `variance.py`, the functions are not generic in `T`; they take `Sequence[Shape]` and `list[Shape]`. Stating that `list[T]` rejects arguments is misleading because a generic function with a parameter `shapes: list[T]` accepts `circles` by binding `T` to `Circle`; the rejection occurs only when `list` is annotated with a concrete base type.
* **Instruction:** Change `Sequence[T]` and `list[T]` in this explanation to `Sequence[Shape]` and `list[Shape]` (or `Sequence[Base]` and `list[Base]`) to match `variance.py` and avoid conflating generic parameter binding with subtyping invariance.

**4. Section: `**P` and the Older `TypeVar` Syntax (Incomplete reason for `TypeVar`'s persistence)**

* **Target Text:** "Before Python 3.12 you wrote type parameters with `TypeVar` and `Generic`, which you still see in older code."
* **Issue:** This implies `TypeVar` is strictly legacy syntax superseded by PEP 695. Because PEP 695 deliberately omitted constraint syntax, `TypeVar` remains the only mechanism in modern Python to define constrained type parameters.
* **Instruction:** Clarify the ongoing role of `TypeVar`: "Before Python 3.12 you wrote all type parameters with `TypeVar` and `Generic`. While bracket syntax replaces them for standard generics and upper bounds, `TypeVar` remains necessary in modern Python when defining constrained type parameters."

## Verdicts

Second run, on the Flash model. Applied in commit 63c60943, after each item was tested against the chapter and run under `uv run` on 3.15.0rc2 and `ty` 0.0.84.

1. Applied, with a different fix. A `reveal_type(text)` placed after the `if` in a copy of `narrowing.py` showed `None` under `ty` (and Pyright), since the branch returns for every `str`, so "still the full `str | None`" misdescribed its listing. The sentence now says `text` is `None` after the `if` because the branch returned for every `str`, and that without that `return` it would be `str | None` again.
2. Rejected. PEP 695 supports constraints: `def pick[T: (int, str)](a: T, b: T) -> T` compiled, `pick.__type_params__[0].__constraints__` is `(<class 'int'>, <class 'str'>)`, and `ty` revealed `pick(Flag(1), Flag(2))` as `int` for a `Flag(int)` subclass, the binding the chapter describes. The reviewer's "bounds but not constraints" claim is false for this Python and this checker.
3. Applied. In a probe, a generic `def total[T](shapes: list[T])` accepted `circles` (`T` bound to `Circle`) with no diagnostic, while `shapes: list[Shape]` drew `invalid-argument-type: Expected list[Shape], found list[Circle]`, so "a `list[T]` parameter rejects" was wrong and `variance.py` uses `Shape` anyway. The sentence now names `Sequence[Shape]` and `list[Shape]`; the next sentence, which defines invariance and covariance of `list[T]` and `Sequence[T]` as type constructors, stands.
4. Rejected. Its premise is item 2's, that PEP 695 lacks constraints, which the probe disproved; bracket syntax covers bounds, constraints, defaults, and inferred variance, so `TypeVar` and `Generic` are the older form the sentence says they are.
