<!-- outside review of Chapters/B_An_Effect_Checker.md, model gemini-3.8-flash-high, 2026-10-09 -->

**Please apply the following technical and structural refinements to the `B_An_Effect_Checker.md` chapter:**

**1. Section: The Restriction (Scope of Resolution)**

* **Target Text:** "The largest remaining group is a method called on a local variable with no annotation, and [From a Call to a Name](#from-a-call-to-a-name) recovers part of that group."
* **Issue:** Section [From a Call to a Name](#from-a-call-to-a-name) only defines `Scope` lookups over AST literals and calls; it is `assigned()` in [Facts About a Function](#facts-about-a-function) (via `local_types.py`) that actually tracks plain assignments (`values[target] = scope.type_of(value)`) and populates `scope.types` for unannotated locals. Pointing solely to [From a Call to a Name](#from-a-call-to-a-name) skips the mechanism that extracts those local variable types.
* **Instruction:** Clarify that resolving unannotated locals requires both the expression type resolution from [From a Call to a Name](#from-a-call-to-a-name) and the assignment tracking implemented in [Facts About a Function](#facts-about-a-function). Change the sentence to: "The largest remaining group is a method called on a local variable with no annotation, and the assignment tracking in [Facts About a Function](#facts-about-a-function) combined with [From a Call to a Name](#from-a-call-to-a-name) recovers part of that group."

**2. Section: Facts About a Function (Handling of Unannotated Return Types)**

* **Target Text:** "For a function with no such annotation, `marked()` returns `None`, which means "inferred.""
* **Issue:** The phrase "no such annotation" can be read as applying only to functions lacking `Annotated`, but in fact `marked()` also returns `None` for functions with conventional return annotations (such as `def f() -> None:` or `def f() -> int:`) as long as they omit `Annotated[..., performs(...)]`. Without clarification, a reader may wonder whether an explicit non-`Annotated` return type triggers an error or requires special handling.
* **Instruction:** Clarify that any function lacking a `performs()` row inside an `Annotated` return type—whether completely unannotated or annotated with a plain type like `None`—evaluates to `None` and is inferred. Change the sentence to: "For a function with no row declaration—whether unannotated or returning a plain type like `int`—`marked()` returns `None`, which means "inferred.""

**3. Section: What the Checker Resolves, and What It Cannot See (Description of Method Receivers)**

* **Target Text:** "A method on a receiver whose type the source writes out: an annotated parameter, an annotated assignment, the first parameter of a method, a module-level constant (through `Final[...]`), or a `type` alias defined in the same module."
* **Issue:** A `type` alias cannot itself be a method receiver (e.g., `Names.sort()` is invalid); rather, a receiver whose annotated type refers to a local `type` alias (such as `names: Names` where `type Names = list[str]`) is what resolves. Listing "or a `type` alias defined in the same module" directly alongside receivers conflates the receiver with its type annotation.
* **Instruction:** Rephrase the list item to make clear that the alias specifies the receiver's type. Change the bullet to: "- A method on a receiver whose type the source writes out: an annotated parameter, an annotated assignment, the first parameter of a method, a module-level constant (through `Final[...]`), or a parameter/variable annotated with a `type` alias defined in the same module."

**4. Section: What the Checker Resolves, and What It Cannot See (Chained Pattern Matching Limitation)**

* **Target Text:** "`p.with_suffix(".bak").write_text(text)` resolves to `pathlib.Path.with_suffix.write_text`, which the `with_*` pattern matches."
* **Issue:** In `STDLIB`, `"pathlib.Path.with_*": PURE` uses `fnmatchcase`, where `*` matches across dots. While the text accurately explains that this makes the chained call appear pure, readers coming from globbing in other contexts may not realize that shell glob matching does not treat dots as path segment boundaries. Explicitly noting that `fnmatch` wildcard matching crosses dots clarifies why the downstream `.write_text` method is masked by `with_*`.
* **Instruction:** Add a brief reminder of `fnmatch`'s dot-crossing behavior to the sentence. Change it to: "`p.with_suffix(".bak").write_text(text)` resolves to `pathlib.Path.with_suffix.write_text`, which the `with_*` pattern matches because `fnmatch` wildcards cross dots."

## Verdicts

Second run, on the Flash model. Applied in commit ed793d38, after each item was tested against the chapter and run under `uv run`.

1. Rejected. The linked section already states the recovery the intro points to: [From a Call to a Name](#from-a-call-to-a-name) says "`p = Path(name)` therefore gives `p` the type `pathlib.Path`, and `p.read_text()` becomes `pathlib.Path.read_text`," and introduces `types` as the map from a variable to its type. The intro sentence is a forward pointer, and `assigned()` follows two sections later where the reader meets it in order.
2. Rejected. A probe through `read_module()` gave `declared` `None` for `def a() -> int`, `def b()`, and `def c() -> Annotated[int, "doc"]`, and `frozenset()` for `performs()`, so the sentence is true as written. "No such annotation" refers to the `Annotated[T, ...]` form the previous paragraph describes, and `-> int` is not that form, so the reader's question the item raises has its answer in the sentence.
3. Applied. A `type` alias is the receiver's written type, not a receiver; a probe confirmed that both `def e(names: Names)` and `q: P = Path("x")` in a function resolve through same-module aliases (`builtins.list.sort`, `pathlib.Path.unlink`). The bullet now ends "or a parameter or variable annotated with a `type` alias defined in the same module," which also parallels the limits list's "a `type` alias imported from another module."
4. Rejected. The chapter already says it where the table is introduced: "A key is an `fnmatch` pattern, the wildcard notation of a shell, in which `*` matches any run of characters, dots included." `fnmatchcase("pathlib.Path.with_suffix.write_text", "pathlib.Path.with_*")` returns `True`, as the limits bullet states.
