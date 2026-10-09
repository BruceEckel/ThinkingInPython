<!-- outside review of Chapters/42_Functional--Error_Handling.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `42_Functional--Error_Handling.md` chapter:

**1. Return the Error as a Value (Syntax error in built-in matching)**

* **Target Text:** 
  ```python
          case int(answer):
              print(f"answer = {answer}")
          case str(error):
              print(f"error = {error!r}")
  ```
* **Issue:** Built-in types like `int` and `str` do not have a `__match_args__` attribute and do not accept positional sub-patterns in a `match` statement. Using `case int(answer):` or `case str(error):` is invalid syntax and raises a `TypeError` at runtime (`int() accepts 0 positional sub-patterns`). The correct syntax uses the `as` keyword to bind the matched object.
* **Instruction:** Replace the `case` clauses to use the `as` pattern syntax:
  ```python
          case int() as answer:
              print(f"answer = {answer}")
          case str() as error:
              print(f"error = {error!r}")
  ```

**2. Return the Error as a Value (Syntax error in prose)**

* **Target Text:** "If a successful answer is also a string, `case str(error)` matches it and reports it as an error."
* **Issue:** As with the listing, the prose uses an invalid positional sub-pattern for a built-in type. It must use the `as` syntax to be valid Python.
* **Instruction:** Change the sentence to use the correct pattern: "If a successful answer is also a string, `case str() as error` matches it and reports it as an error."

**3. A Result Type (Class vs. method type parameters)**

* **Target Text:** "`A`, `B`, `E`, and `F` are [type parameters](08_Foundations--Static_Types.md#type-parameters):
placeholders that take concrete types when you use the class."
* **Issue:** `A` (in `Ok`) and `E` (in `Err`) are type parameters of the classes, but `B`, `F`, and the `E` in `Ok.bind` are type parameters of the `bind()` methods. Method type parameters take concrete types when you call the method, not when you use the class.
* **Instruction:** Clarify the scoping distinction by changing the text to: 
  "`A` and `E` are class type parameters, while `B` and `F` are method type parameters. They act as placeholders that take concrete types when you use the class or call the method."

**4. Combining Multiple Results (Demonstrating answer scoping)**

* **Target Text:** `            lambda b: func_c(i + j).bind(`
* **Issue:** The code passes the original function arguments `i + j` to `func_c`, missing the opportunity to demonstrate how nesting keeps earlier step answers (`a` and `b`) in scope for later dependent steps. Using `a + b` makes the pedagogical point of the nested lambda structure much clearer, while preserving the exact same behavior and test outcomes.
* **Instruction:** Change `func_c(i + j)` to `func_c(a + b)`:
  ```python
              lambda b: func_c(a + b).bind(
  ```

## Verdicts

Applied in commit 933eb672, after each item was tested against the chapter and run under `uv run`.

1. Rejected. `int`, `str`, and the other built-in types in PEP 634's special list accept one positional sub-pattern that matches the whole subject, so `case int(answer):` is valid: a probe matching `0` and `"x"` printed `answer 0` and `error 'x'` with no `TypeError`, and `ty` passes it. Chapter 13's "Built-in Types and Subclasses" section, which the sentence after the listing links, teaches this form, and the gate runs `sum_type.py` against its markers.
2. Rejected. `case str(error)` is valid for the reason given in item 1, so the prose matches the listing as written.
3. Applied. `Ok.bind[B, E]` and `Err.bind[B, F]` declare their own type parameters, bound at each call, while the paragraph said all four take concrete types "when you use the class." The paragraph now says `Ok[A]` and `Err[E]` declare `A` and `E` on their classes, and each `bind()` declares `B`, `F`, and a separate `E` of its own that take concrete types at each call.
4. Rejected. Since `func_a()` and `func_b()` return their input, `a + b` equals `i + j` and the output would not change, but the change would make `func_c()` depend on the earlier answers. The chapter states that the three steps "take independent inputs," which is why short-circuiting discards findings, and exercise 3's solution says "That independence is why `func_c()` here takes `i + j` rather than a value produced by `func_a()` or `func_b()`."
