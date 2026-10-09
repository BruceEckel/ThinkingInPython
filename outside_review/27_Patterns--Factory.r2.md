<!-- outside review of Chapters/27_Patterns--Factory.md, model gemini-3.8-flash-high, 2026-10-08 -->

**Please apply the following technical and structural refinements to the `27_Patterns--Factory.md` chapter:**

**1. Section: Explicit Registration with a Protocol (PEP 695 type parameter bounds)**

* **Target Text:** `"A generic factory would need register()'s bound to name the factory's own type parameter, and the type checker rejects a type variable's bound that is generic."`
* **Issue:** In Python 3.12+ (PEP 695), type parameter bounds can be generic types (such as `[T: Sequence[int]]`). What PEP 695 and type checkers actually reject is a type parameter bound that references another type parameter, such as `[S: T]` referencing the enclosing class's type parameter `T`.
* **Instruction:** Clarify that the restriction is referencing an outer type parameter rather than using a generic bound: `"A generic factory would need register()'s bound to name the factory's own type parameter, and the type checker rejects a type parameter bound that references another type parameter."`

**2. Section: Builder (Test assertion description)**

* **Target Text:** `"Testing confirms that the two forms produce the same pizza, that replace() changes one field of a copy and keeps the rest, and that a builder is single-use:"`
* **Issue:** The third test in [test_pizza.py](file:///c:/git/ThinkingInPython/Examples/27_Patterns--Factory/test_pizza.py) is [`test_second_build_reuses_toppings()`](file:///c:/git/ThinkingInPython/Examples/27_Patterns--Factory/test_pizza.py#L22-L28), which asserts that a second `build()` call succeeds and accumulates toppings (`assert second.toppings == ("basil", "olives")`). The test demonstrates state retention across builds rather than asserting that the builder is single-use.
* **Instruction:** Update the introductory sentence to match what the test actually verifies: `"Testing confirms that the two forms produce the same pizza, that replace() changes one field of a copy and keeps the rest, and that a second build reuses previously accumulated toppings:"`

**3. Section: Factory Objects (Safe dispatch vs type safety)**

* **Target Text:** `"Using the dictionary lookup gives you type safety. You get either a factory or a KeyError."`
* **Issue:** Looking up an unconstrained `str` key at runtime and raising `KeyError` provides defensive dispatch against arbitrary code execution (contrasted with `eval()`), but it is not type safety. Calling a runtime `KeyError` "type safety" also contradicts the earlier distinction in `shape_table.py`, which contrasted check-time type safety via `Literal` with runtime `KeyError`.
* **Instruction:** Change "type safety" to describe execution safety or safe dispatch: `"Using the dictionary lookup gives you safe dispatch against arbitrary code execution: you get either a registered factory or a KeyError."`

## Verdicts

Second run, on the Flash model. Applied in commit acb67ef8, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. A probe under `uv run ty check` accepted `[T: Sequence[int]]` and reported `invalid-type-variable-bound` ("TypeVar upper bound cannot be generic") on `register[S: P]` inside `class Factory[P: Shape]`, on `[S: list[P]]`, and on `def f[T, S: list[T]]`, so the rejected case is a bound that contains a type parameter, not a generic bound. The sentence now reads "the type checker rejects a bound that contains another type parameter."
2. Applied, with a different fix. `test_second_build_reuses_toppings()` asserts that a second `build()` succeeds and returns `("basil", "olives")`, the hazard the chapter calls single-use, not a failure on reuse. The lead-in now says the test confirms "that a second `build()` on the same builder carries the first pizza's toppings", which names what the assertion checks.
3. Applied, with a different fix. `reveal_type(eval("1"))` under `ty` shows `Any`, while `FACTORIES[kind]` is a `ShapeMaker`, so the lookup does carry a type, but the paragraph argues about running arbitrary code and "type safety" named neither point. The two sentences now say the lookup runs no code from the string, yields a factory or a `KeyError`, and gives the type checker a `ShapeMaker` where `eval()` returns `Any`.
