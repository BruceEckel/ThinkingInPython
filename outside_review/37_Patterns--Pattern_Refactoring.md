<!-- outside review of Chapters/37_Patterns--Pattern_Refactoring.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `37_Patterns--Pattern_Refactoring.md` chapter:

**1. The First Cut: Checking Every Type (Self-Registration Caveat)**

* **Target Text:** "`__init_subclass__()` registers `Plastic` the moment its `class` statement runs, and without that `class` statement `create()` raises a `KeyError` at the first `Plastic:` line, loudly, at parse time."
* **Issue:** A classic pitfall with the self-registration factory pattern is that subclasses defined in separate files are completely invisible to the program unless explicitly imported. The reader needs to know that defining the class is not enough; the module must be loaded.
* **Instruction:** Change to: "`__init_subclass__()` registers `Plastic` the moment its `class` statement runs. If you define a new material in its own file, you must explicitly import that file somewhere before calling the factory; otherwise, its `class` statement will never run and `create()` will raise a `KeyError` at the first `Plastic:` line, loudly, at parse time."

**2. One `singledispatch` Function per Operation (Type Annotation Mechanism)**

* **Target Text:** "Each implementation above takes the placeholder name `_`."
* **Issue:** In modern Python, `singledispatch` relies entirely on the first parameter's type annotation to know which type to register. If the reader omits the type hint out of habit, the decorator will fail at runtime with a `TypeError`. Mentioning this explicitly clarifies the mechanism.
* **Instruction:** Change to: "Each implementation above takes the placeholder name `_`. The `@register` decorator reads the type annotation on the first parameter (like `t: Aluminum`) to know which class it handles; if you omit the annotation, `singledispatch` raises a `TypeError`."

**3. One `singledispatch` Function per Operation (Stateful Visitors)**

* **Target Text:** "In Python, a single-dispatch function does *Visitor*'s job:"
* **Issue:** The GoF *Visitor* pattern natively allows the visitor object to accumulate state across multiple elements during traversal. While a single-dispatch function gracefully replaces the double-dispatch mechanism, it cannot hold state natively without resorting to globals or closures. 
* **Instruction:** Change to: "In Python, a single-dispatch function does *Visitor*'s job for stateless operations (for stateful operations, use `singledispatchmethod` on a class so the instance can hold state):"

**4. Let a Dictionary Do the Sorting (Pattern Matching Mechanism)**

* **Target Text:** "`case Aluminum()` matches any subclass, so `recycle_rtti.py` puts a `CrushedAluminum` in the `Aluminum` bin."
* **Issue:** Experienced programmers coming from languages with different pattern matching semantics might not realize *why* a class pattern matches subclasses. Explicitly naming the `isinstance` mechanism removes the ambiguity.
* **Instruction:** Change to: "`case Aluminum()` matches any subclass because class patterns use `isinstance()` under the hood, so `recycle_rtti.py` puts a `CrushedAluminum` in the `Aluminum` bin."

**5. The `Trash` Hierarchy (Currency Data Types)**

* **Target Text:** "# Dollars per pound (per subclass)"
* **Issue:** Experienced developers reading a refactoring chapter will instantly recognize that using `float` for currency calculations introduces precision errors. Acknowledging this prevents distraction and reassures the reader that the code smell is a deliberate simplification for the example.
* **Instruction:** Change the comment to: `# Dollars per pound (use decimal.Decimal in production)`

## Verdicts

No item applied; each was tested against the chapter and run under `uv run`.

1. Rejected. The claim is right, and the chapter already links the place that makes it: [Factory](27_Patterns--Factory.md#hazards-of-self-registration), cited three paragraphs into the chapter, says "a subclass defined in another module registers itself only when something imports that module" and adds the lazy-import variant. Every `Plastic` in this chapter sits in the listing that uses it, and the target sentence already says that without the `class` statement `create()` raises a `KeyError`.
2. Rejected. A probe confirmed it: `@f.register` on an unannotated `def _(x)` raised `TypeError: Invalid first argument to register()`. The sentence links [The Pythonic Visitor](33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch), which says "`@nectar.register` reads the annotation on the implementation's first parameter" and how that fills the dispatch table, so the mechanism is taught where the link points.
3. Rejected. The chapter already names the method form for an operation that belongs on an object, at "For an operation that belongs on an object and still varies by type, `functools.singledispatchmethod` provides the same dispatch in method form", with links to chapters 41 and 32, and exercise 3 asks for that conversion. Both operations here, `recycling_note()` and `hazard()`, keep no state, so a qualifier on the lead-in guards a case the listings never exercise.
4. Rejected. A probe confirmed it: a `case C()` against a metaclass with `__instancecheck__()` called that hook, and `case A()` matched a `B(A)`. [Pattern Matching](13_Techniques--Pattern_Matching.md#builtin-types-and-subclasses) teaches it ("The type test is `isinstance()`, so a subclass matches its base's pattern") and contrasts it with a `dict` keyed on `type(value)`, the same contrast this paragraph draws; the sentence states the behavior the comparison needs.
5. Rejected. A style comment that adds a production caveat to a teaching listing. The values are per-pound prices in a simulation, `sum_value()` prints with `:.2f`, and the `Aluminum` total prints `584.50` as computed; nothing in the chapter compares or accumulates money where float rounding shows.
