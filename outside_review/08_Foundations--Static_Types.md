<!-- outside review of Chapters/08_Foundations--Static_Types.md, model gemini-3.1-pro-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `08_Foundations--Static_Types.md` chapter:

**1. Type Hints (Mechanism clarification)**
* **Target Text:** "The `...` in `tuple[int, ...]` means any number of `int`s."
* **Issue:** "Any number" can be ambiguous, leaving readers to wonder if a variable-length tuple requires at least one element. It is worth being explicit that it includes the empty tuple.
* **Instruction:** Change to "The `...` in `tuple[int, ...]` means any number of `int`s, including zero."

**2. Classes as Values: type[C] (Caveat)**
* **Target Text:** "Passing `Circle` works because `Circle` is a subclass of `Shape`. Calling `kind()` then produces an instance."
* **Issue:** When using `type[SomeType]`, the type checker assumes the subclass constructor has the same signature as the base class. If a subclass overrides `__init__` to require new arguments, passing it will satisfy the type checker but fail at runtime when instantiated.
* **Instruction:** Add a caveat after this sentence: "However, this assumes the subclass constructor takes the same arguments as the base. If a subclass overrides `__init__` to require new arguments, `kind()` will fail at runtime."

**3. Type Parameter Defaults (Mechanism clarification)**
* **Target Text:** "words: Stack = Stack()  # No brackets, so T is str"
* **Issue:** Readers might assume the default also applies to instantiation if the annotation is omitted entirely (i.e., `words = Stack()`). However, type checkers apply type parameter defaults when the class is used as an annotation; an unannotated call to `Stack()` with no constructor arguments to infer from still leaves `T` as `Unknown`.
* **Instruction:** Add a sentence after the code block: "The default applies because `Stack` is used in a type annotation; if you write `words = Stack()` with no annotation and no constructor arguments to infer from, `T` remains unsolved."

**4. Constants with Final (Best Practice)**
* **Target Text:** "The word suggests immutability, but the object stays mutable."
* **Issue:** The text correctly points out that `Final` only prevents rebinding, but it leaves readers without a mechanism to actually lock down a constant collection statically.
* **Instruction:** Add a sentence after this: "To enforce immutability statically, combine `Final` with a read-only type, as in `HISTORY: Final[Sequence[str]] = []`."

## Verdicts

Applied in commit 83274c05, after each item was tested against the chapter and run under `uv run` with `ty` 0.0.84.

1. Applied, with a different fix. `empty: tuple[int, ...] = ()` checks clean, so the empty tuple is included. The sentence now reads "zero or more `int`s", which says so in fewer words than "any number, including zero".
2. Rejected. The listing defines no subclass whose `__init__()` takes arguments, so the failure is a case it never runs (the review rules name "a subclass no listing defines" as the shape to leave out). The gap is real: a probe `Labeled(Shape)` with `__init__(self, label: str)` passed `make(Labeled)` under `ty` with no diagnostic, and `kind()` would raise a `TypeError` at runtime.
3. Rejected. Under `ty` 0.0.84 the claim is false: `words = Stack()` with no annotation and no constructor argument reveals `Stack[str]`, the same as the annotated form, so the default applies to the bare call too and `T` is solved.
4. Rejected. A probe `HISTORY: Final[Sequence[str]] = []` followed by `HISTORY.append("first")` checks clean under `ty`, since the checker narrows the name to the assigned `list[str]` for the rest of the module, so the proposed guard would change nothing in this listing. `Sequence` is also introduced three sections later, in Variance, as the read-only shape, with its own listing.
