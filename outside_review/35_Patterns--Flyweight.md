<!-- outside review of Chapters/35_Patterns--Flyweight.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `35_Patterns--Flyweight.md` chapter:

**1. Section: Typing the Symbol Set (Type checker and `@cache`)**
* **Target Text:** "`tile()` declares its parameter a `Symbol`, but `@cache` hides that declaration from callers. The decorated `tile` is a `functools._lru_cache_wrapper`, whose call accepts any hashable arguments, so the type checker passes `tile("?")`, and the mistake surfaces at runtime as a `KeyError` from `SPECS`."
* **Issue:** Modern type checkers (including `ty`/Pyright) use `ParamSpec` to model `functools._lru_cache_wrapper` in `typeshed`, which perfectly preserves the decorated function's parameter types. The type checker will not pass `tile("?")`; it will correctly flag `"?"` as an incompatible argument type for `Symbol`.
* **Instruction:** Rewrite to acknowledge that the type checker preserves the signature and catches the error. For example: "`tile()` declares its parameter a `Symbol`, and modern type checkers preserve this signature through the `@cache` decorator, catching a direct mistake like `tile("?")`. However, when a dynamic string from a map file bypasses the type checker, the boundary function `to_symbol()` is still needed, raising a `KeyError` if the character is outside `SPECS`."

**2. Section: Typing the Symbol Set (Type narrowing on dict keys)**
* **Target Text:** "The type checker narrows on the same guard. `SPECS` has key type `Symbol`, so past the guard `char` is a `Symbol`, and `return char` satisfies the declared return type as written."
* **Issue:** Standard type checkers like `ty` (Pyright) and Mypy do not narrow a variable's type from `str` to a `Literal` based solely on dictionary key membership (`char in SPECS`). They will still evaluate `char` as a `str` after the guard, flagging `return char` as an invalid return type.
* **Instruction:** Acknowledge this limitation and add a `cast()`, or change the guard to check against a tuple of literals. To use `cast()`, change the text to: "The type checker cannot narrow `char` just from membership in `SPECS`, so `return cast(Symbol, char)` is needed to satisfy the return type." Alternatively, define a tuple of valid literals, check against that to enable narrowing, and update the text to reflect this.

**3. Section: Python Uses Flyweights (`SyntaxWarning` clarification)**
* **Target Text:** "Because the result of `is` on a literal depends on details like this pooling, Python emits a `SyntaxWarning` for it."
* **Issue:** This sentence immediately follows an example comparing variables (`high is high2`), which might mislead readers into expecting that specific code to trigger a warning. Python only emits a `SyntaxWarning` when a literal itself is directly an operand of `is` (e.g., `x is 100000`).
* **Instruction:** Clarify the wording so it explicitly refers to direct literal comparison. Change the sentence to: "Because the result of `is` depends on details like this pooling, Python emits a `SyntaxWarning` if you use `is` directly with a literal (like `x is 100000`)."

## Verdicts

Applied in commit 1b195122, after each item was tested against the chapter and run under `uv run`.

1. Rejected. A probe beside the extracted `tile_map.py` revealed `tile` as `_lru_cache_wrapper[Tile]`, and both `ty` 0.0.84 and Pyright 1.1.414 passed `tile("?")` and `tile(3)` with no diagnostic. Typeshed declares `_lru_cache_wrapper.__call__(self, *args: Hashable, **kwargs: Hashable)`, with no `ParamSpec`, so the chapter's account is right.
2. Rejected. In the same probe, `reveal_type(char)` after `if char not in SPECS: raise KeyError(char)` showed `Literal[".", "~", "#"]` under both `ty` and Pyright, and the extracted listing type-checks clean in `tip verify-ch`, so the narrowing the chapter describes holds and no `cast()` is needed.
3. Applied. Compiling `high, high2 = 100000, 100000` then `high is high2` produced no warning, while `x is 100000` produced `SyntaxWarning: "is" with 'int' literal`. The sentence followed the example that draws no warning, so it now says the warning fires when a literal is an operand of `is`, as in `high is 100000`.
