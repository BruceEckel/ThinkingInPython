<!-- outside review of Chapters/B_An_Effect_Checker.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `B_An_Effect_Checker.md` chapter:

**1. Facts About a Function (Type aliases evaluate lazily)**

* **Target Text:** `top = [node for node in tree.body if not is_def(node)]`
* **Issue:** Python 3.12 type aliases (`ast.TypeAlias`) evaluate lazily (PEP 695) and do not execute their right-hand side when the module is imported. Keeping them in `top` incorrectly adds any calls within the alias (if one were present) to the module's edge row.
* **Instruction:** Exclude type aliases here just as `module_scope()` does:
```python
    top = [
        node
        for node in tree.body
        if not is_def(node)
        and not isinstance(node, ast.TypeAlias)
    ]
```

**2. Facts About a Function (Positional-only `self`)**

* **Target Text:** 
```python
    if owner and args.args:
        types[args.args[0].arg] = owner
```
* **Issue:** In modern Python, a method's first parameter can be positional-only (`def method(self, /):`). If it is, `args.posonlyargs` holds it and `args.args` either points to the second parameter or is empty, which gives the class type to the wrong variable.
* **Instruction:** Check `posonlyargs` first:
```python
    if owner:
        if args.posonlyargs:
            types[args.posonlyargs[0].arg] = owner
        elif args.args:
            types[args.args[0].arg] = owner
```

**3. Facts About a Function (Chained assignments)**

* **Target Text:** 
```python
            case ast.Assign(targets=[target], value=value):
                values[target] = scope.type_of(value)
```
* **Issue:** This pattern matches only assignments with exactly one target. A chained assignment like `a = b = 1` puts multiple targets in the AST list, causing it to fail the match and leaving the variables unresolved even when the right side has an evident type.
* **Instruction:** Replace the single-target pattern with a loop over all targets:
```python
            case ast.Assign(targets=targets, value=value):
                for target in targets:
                    values[target] = scope.type_of(value)
```

## Verdicts

Applied in commit 9f96adb1, after each item was tested against the chapter and run under `uv run`.

1. Rejected. The over-count is real but conservative and outside the chapter's input: a probe module holding `type T = Annotated[str, Path("x").unlink()]` reports `m.<module> ['FileSystem']` for a call that never runs, while no checked file has a call inside a `type` statement. The proposed filter is also partial, since a function-local `x: Annotated[str, Path("x").unlink()] = "a"` puts `FileSystem` in that function's row the same way: every annotation, not only an alias, is the case.
2. Applied, with a different fix. In a probe class, `def keep(self, /, p)` gave `p` the class's type, so `p.write()` resolved to the class's pure `write()` and the row came back empty, a silent false negative that contradicts the prose's "the first parameter of a method." `parameters()` now builds `positional = args.posonlyargs + args.args` and types `positional[0]`, so `keep` reports `['Unknown']` and `save(self, /, p: Path)` reports `['FileSystem']`; the `check_files.py`, `greeting_check.py`, and `third_party_stub.py` markers are unchanged.
3. Rejected. `a = b = Path("x")` followed by `a.unlink()` reports `m.f ['Unknown']`, so the missed case appears in a row instead of going unreported, which is the chapter's stated rule for its first list of limits. No listing or test input uses a chained assignment, and widening the pattern adds code to a teaching listing for a case the chapter never exercises.
