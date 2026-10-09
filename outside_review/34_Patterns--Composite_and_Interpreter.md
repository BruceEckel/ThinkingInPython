<!-- outside review of Chapters/34_Patterns--Composite_and_Interpreter.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `34_Patterns--Composite_and_Interpreter.md` chapter:

**1. Simplification Rewrites the Tree (idiomatic pattern guard)**
* **Target Text:** 
```python
                case _:
                    if lhs is left and rhs is right:
                        # Share the unchanged subtree
                        return e
                    return Add(lhs, rhs)
```
and
"The `is` guard in each `case _` returns the node it received when both children simplified to themselves."
* **Issue:** The code uses a standard `if` statement inside the `case _` block, but the text calls it a "guard". In Python's pattern matching, a true guard is a condition attached directly to the `case` clause, which is the idiomatic way to express this logic and avoids the nested branching.
* **Instruction:** Replace the nested `if` blocks in both `Add` and `Mul` with pattern guards. For example, in `Add`:
```python
                case _ if lhs is left and rhs is right:
                    # Share the unchanged subtree
                    return e
                case _:
                    return Add(lhs, rhs)
```
Then, update the text to match: "The `is` guard on the first `case _` returns the node it received when both children simplified to themselves."

**2. Operators That Build Nodes (operator dispatch sequence)**
* **Target Text:** "`ty` reports `"a" + x` as `unsupported-operator` in source it checks, but at runtime `Var.__radd__()` runs before `str` tries to concatenate, and the result is `Add(Num("a"), x)`, an ill-typed tree whose error waits for `evaluate()` to add the `"a"`."
* **Issue:** The reflected method `Var.__radd__()` does not run *before* `str` tries to concatenate. Python evaluates `"a" + x` by first calling `str.__add__("a", x)`, which actively attempts the concatenation, fails, and returns `NotImplemented`. Only after this failure does Python fall back to `Var.__radd__("a")`.
* **Instruction:** Change the text to: "`ty` reports `"a" + x` as `unsupported-operator` in source it checks, but at runtime `str` returns `NotImplemented` for the concatenation and `Var.__radd__()` runs, so the result is `Add(Num("a"), x)`, an ill-typed tree whose error waits for `evaluate()` to add the `"a"`."

**3. Simplification Rewrites the Tree (empty class patterns)**
* **Target Text:** `case Num(_) | Var(_):`
* **Issue:** When you only want to match the type of an instance and do not need to bind or inspect any of its fields, an empty class pattern (`Class()`) is the idiomatic form. It matches regardless of how many fields the record has, making the wildcard (`_`) unnecessary.
* **Instruction:** Change the line to: `case Num() | Var():`

## Verdicts

Applied in commit 1735c423, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. The prose did misname the construct: the identity test sits in an `if` inside the `case _` body, and in pattern matching a guard is the `if` on the `case` line. The listing is correct as written, so the prose now says "The `if` inside each `case _`" and "That `if` tests identity" instead of changing both `simplify()` branches to guarded cases.
2. Rejected. Against the extracted `expr.py`, `"a" + x` returned `Add(left=Num(value='a'), right=Var(name='x'))`, while `"a".__add__(x)` raises a `TypeError` ("can only concatenate str (not "Var") to str") and never returns `NotImplemented`. A probe class whose `__radd__()` prints and returns `NotImplemented` printed "radd ran" before the `str` `TypeError`: CPython tries the numeric slots, which reach `__radd__()`, before `str`'s sequence concatenation, so the chapter's order is right.
3. Rejected. A style comment: run against `Num(3)` and `Var("y")`, `case Num() | Var():` and `case Num(_) | Var(_):` matched both, so the two forms behave identically for these one-field records.
