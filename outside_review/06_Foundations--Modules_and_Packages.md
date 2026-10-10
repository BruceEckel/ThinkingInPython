<!-- outside review of Chapters/06_Foundations--Modules_and_Packages.md, model gemini-3.1-pro-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `06_Foundations--Modules_and_Packages.md` chapter:

**1. Section: Modules and Packages (misleading timing in `sys.modules`)**
* **Target Text:** "The first `import` stores the finished module object in `sys.modules`, a dict keyed by dotted module name."
* **Issue:** This contradicts the later, correct explanation in the "Circular Imports" section that Python places the module in `sys.modules` *before* its body finishes. If Python waited until the module was "finished" to store it, circular imports would loop infinitely instead of finding a partially initialized module object.
* **Instruction:** Change the sentence to: "The first `import` creates a module object, stores it in `sys.modules` (a dict keyed by dotted module name), and then runs the file's body into it."

**2. Section: Circular Imports (incorrect error condition)**
* **Target Text:** "When the file sits in that directory (`sys.path[0]`), the usual case for two modules beside your script, Python suspects a name collision with a library instead of a cycle: `ImportError: cannot import name 'f' from 'modx' (consider renaming '.../modx.py' if it has the same name as a library you intended to import)`."
* **Issue:** Python only appends the "consider renaming" hint when the module shares a name with a standard library module (i.e., its name is in `sys.stdlib_module_names`), not just because it sits in `sys.path[0]`. For ordinary circular imports between two custom files like `mod1.py` and `mod2.py` in the same directory, Python still correctly appends "(most likely due to a circular import)".
* **Instruction:** Replace the sentence with: "If your module shares a name with a standard library module and you import from it, Python suspects a name collision instead of a cycle: `ImportError: cannot import name 'f' from 'math' (consider renaming '.../math.py' if it has the same name as a library you intended to import)`."

**3. Section: Circular Imports (misleading claim about runtime annotations)**
* **Target Text:** "The annotations still work at runtime, because Python does not evaluate them at import time."
* **Issue:** While deferred evaluation (PEP 649 in Python 3.14+) prevents a crash at *import time*, the annotations do not fully "work" at runtime. If any tool (like `typing.get_type_hints()`, FastAPI, or Pydantic) tries to evaluate them later, it will raise a `NameError` because the name was never imported into the module's runtime namespace.
* **Instruction:** Replace the sentence with: "The module imports successfully because Python does not evaluate annotations at import time, though tools that inspect those annotations at runtime may still fail with a `NameError`."

## Verdicts

Applied in commit f7658560, after each item was tested against the chapter and run under `uv run`.

1. Applied. "The finished module object" contradicted the Circular Imports section's "places the first one to load in `sys.modules` before its body finishes", which is the order that lets a cycle find a partially initialized module. The sentence now says the first `import` creates the module object, stores it, and then runs the file's body to fill it.
2. Rejected. A probe on 3.15.0rc2 with `modx.py` and `mody.py` importing each other beside `main.py` gave "cannot import name 'f' from 'modx' (consider renaming '...\modx.py' if it has the same name as a library you intended to import)", with no standard-library name involved, and the same pair inside a package gave "(most likely due to a circular import)". The chapter's `sys.path[0]` condition is the one Python applies; the reviewer's stdlib-name condition is a different hint.
3. Applied, with a different fix. A probe module with `from decimal import Decimal` under `TYPE_CHECKING` and `def price(x: Decimal)` imported and ran, but `price.__annotations__` and `typing.get_type_hints(price)` both raised `NameError: name 'Decimal' is not defined` (the `STRING` format of `annotationlib.get_annotations()` still returns the names). "Still work at runtime" overstated it; the sentences now say the module still imports because an annotation is evaluated only when read, that reading one raises a `NameError`, and that the guard suits names used in annotations alone, which the next sentence's "every use of the name is an annotation" already relied on.
