<!-- outside review of Chapters/17_Techniques--Metaprogramming.md, model gemini-3.8-flash-high, 2026-10-08 -->

**Please apply the following technical and structural refinements to the `17_Techniques--Metaprogramming.md` chapter:**

**1. Section: The Core Functions (PEP 649 dunder naming)**

* **Target Text:** "`__annotate_func__` is the code that computes the annotations, and `__annotations_cache__` holds the result after the first request."
* **Issue:** In PEP 649 (implemented in Python 3.14 and targeting 3.15), the compiler-generated deferred annotation function is stored on functions, classes, and modules under the attribute name `__annotate__`, not `__annotate_func__`. The corresponding output marker in `demo_display_object.py` also mistakenly expects `#:   • __annotate_func__(format, /)` instead of `#:   • __annotate__(format, /)`.
* **Instruction:** Replace "`__annotate_func__`" with "`__annotate__`" in the prose, and update the method output marker in `demo_display_object.py` to `#:   • __annotate__(format, /)`.

**2. Section: Attributes on a Function (scope of `__dict__` in Python's type system)**

* **Target Text:** "Every object's type declares `__dict__` as a `dict[str, Any]`, so indexing it type-checks."
* **Issue:** This claim is inaccurate at both runtime and type-check time. Many objects in Python (including `object()`, built-in types like `int` and `str`, and classes using `__slots__`) do not have an instance dictionary, nor does `object` declare `__dict__` in `typeshed` (a distinction the section itself relies on when noting `__module__` has no `__dict__`). It is `types.FunctionType` (along with modules and standard classes) that declares `__dict__: dict[str, Any]` to type checkers.
* **Instruction:** Replace the target sentence with: "A function's type declares `__dict__` as a `dict[str, Any]`, so indexing it type-checks."

**3. Section: When You Still Need a Metaclass (unnamed special method lookup mechanism)**

* **Target Text:** "A class decorator cannot make `for c in Color` work.
It can add methods that instances see,
but not a protocol method the class object must answer,
which is why `Color` needs a metaclass, not a decorator."
* **Issue:** Programmers coming from C++ or Java often expect that dynamically assigning `Color.__iter__ = ...` on the class object would make `for c in Color` work, since `Color` is a runtime object. The text asserts that a decorator cannot supply protocol methods to a class object, but leaves the underlying Python mechanism unnamed: special method lookup for protocol dunders bypasses instance dictionaries entirely and queries the object's type (`type(Color)`).
* **Instruction:** Add after the target text: "Python resolves special methods like `__iter__()` by querying the object's type (`type(Color)`), bypassing the object's own namespace. Because `Color`'s type is its metaclass, a class-level protocol method must live on that metaclass."

**4. Section: Attributes on a Function (handler inheritance in subclasses)**

* **Target Text:**
```python
    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        cls.handlers = {
            attr.__dict__["event"]: attr
            for attr in vars(cls).values()
            if "event" in getattr(attr, "__dict__", {})
        }
```
* **Issue:** Because `cls.handlers` is overwritten by inspecting only `vars(cls).values()`, any subclass of `Button` (for example, `class IconButton(Button): pass`) will reset `handlers` to `{}` on the subclass, breaking event dispatch for all inherited handlers. In practice, dispatch registries populated in `__init_subclass__()` need to merge with the parent class's registry.
* **Instruction:** Update the dictionary construction in `marked_methods.py` to merge with existing handlers:
```python
        cls.handlers = getattr(cls, "handlers", {}) | {
            attr.__dict__["event"]: attr
            for attr in vars(cls).values()
            if "event" in getattr(attr, "__dict__", {})
        }
```
and note in the following paragraph that merging `getattr(cls, "handlers", {})` preserves handlers defined on superclasses.

## Verdicts

Second run, on the Flash model (566 s against the Pro run's 131 s). Applied in commit 39a74ba2 after each item was tested against the chapter and run under `uv run`.

1. Rejected, with a clarification applied. On this Python a class's own namespace holds `__annotate_func__`, which is what `display_object()` lists and the marker shows; `__annotate__` is a descriptor on `type` that reads it (`A.__annotate__ is vars(A)["__annotate_func__"]`). The prose now names `__annotate__` and says where it lives.
2. Rejected. `ty` reveals `o.__dict__` on a parameter typed `object` as `dict[str, Any]`, so the sentence about the type checker is right; the item's runtime point (a slotted instance has no `__dict__`) is not what the sentence claims.
3. Applied. Assigning `Color.__iter__` on the class left `list(Color)` raising `'type' object is not iterable` while instances iterated, so special method lookup on `type(Color)` is the mechanism, and the prose now states it.
4. Already applied from the Pro run (commit 60d7d2fa), with `{**cls.handlers, **marked}` rather than `getattr(cls, "handlers", {}) | {...}`.
