<!-- outside review of Chapters/27_Patterns--Factory.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `27_Patterns--Factory.md` chapter:

**1. Builder: The smallest builder is easy to overlook (Inconsistent replace function)**

* **Target Text:** `from dataclasses import replace`
* **Issue:** The `Prototype` section introduces `copy.replace()` as "the general form of the operation" (introduced in Python 3.13), but `pizza_direct.py` and `test_pizza.py` revert to using the older `dataclasses.replace()`. For consistency and to reinforce modern Python practices, the builder examples should use `copy.replace()`.
* **Instruction:** In `pizza_direct.py` and `test_pizza.py`, change `from dataclasses import replace` to `import copy`. Then, update the calls from `replace(pizza, ...)` and `replace(base, ...)` to `copy.replace(pizza, ...)` and `copy.replace(base, ...)`.

**2. Simple Factory Method: Hiding the Concrete Classes (Redundant work in loop)**

* **Target Text:** `cls = random.choice(Shape.__subclasses__())`
* **Issue:** In `shape_factory_method.py`, `Shape.__subclasses__()` is called on every iteration of the loop, repeatedly rebuilding the list of subclasses. In the later `shape_factory_objects.py` listing, it is correctly pulled out of the loop into a `types` variable, which avoids this redundant work and makes the code cleaner.
* **Instruction:** In `shape_factory_method.py`, insert `types = Shape.__subclasses__()` immediately before the `for` loop, and change the loop body to `cls = random.choice(types)`, matching the implementation in `shape_factory_objects.py`.

**3. Abstract Factories: Unify type checker error message (Clarity and consistency)**

* **Target Text:** `# ty: expected "GameElementFactory", found "BrokenFactory":`
* **Issue:** The code comment abbreviates the type checker error, but the prose immediately following it explicitly states: "the checker reports `protocol member make_obstacle is not defined on type BrokenFactory`." Updating the comment to match the prose ensures consistency and accurately reflects how Pyright reports structural typing failures.
* **Instruction:** Change the comment in `abstract_factory_protocol.py` to `# ty: protocol member make_obstacle is not defined on type BrokenFactory:` so it exactly matches the error quoted in the text.

## Verdicts

No item applied; each was tested against the chapter and run under `uv run`.

1. Rejected. The chapter uses `dataclasses.replace()` on the record by choice and names `copy.replace()` as the general form right after `pizza_direct.py` ("For a record, `replace()` is *Prototype* and *Builder* in one function ... `copy.replace()` is the general form of the operation"), linking chapter 12's section on the two. A probe showed `copy.replace(p, size=20) == replace(p, size=20)` on `pizza_direct.Pizza`, so the swap changes no behavior and is a style preference.
2. Rejected. Calling `Shape.__subclasses__()` inside the loop is correct, and a probe with `random.seed(4)` gave the same `['Circle', 'Square', 'Circle', 'Square']` from `shape_factory_method.shape_name(4)` and from the hoisted form, so the marker stays as it is. Hoisting a four-iteration lookup is an efficiency style point; the listing is not wrong.
3. Rejected. With `[1]` uncommented, `uv run ty check` reports one `invalid-argument-type` diagnostic whose headline reads ``Expected `GameElementFactory`, found `BrokenFactory` `` and whose sub-line reads ``protocol member `make_obstacle` is not defined on type `BrokenFactory` ``. The comment quotes the headline, in the same form as the chapter's other `# ty:` comments, and the prose quotes the sub-line as the reason; both are accurate. The checker is `ty`, not Pyright as the item says.
