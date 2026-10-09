<!-- outside review of Chapters/37_Patterns--Pattern_Refactoring.md, model gemini-3.8-flash-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `37_Patterns--Pattern_Refactoring.md` chapter:

**1. Section: A Method on Every Material (Material subclass count and base class edit)**

* **Target Text:** "One new operation is an edit to all three material classes, and the operation after it is three more edits. Those edits sit in each class body, as `note_methods.py` shows. In the real program they go in `trash.py`."
* **Issue:** The simulation established four material subclasses in `trash.py` (`Aluminum`, `Paper`, `Glass`, `Cardboard`), but `note_methods.py` defines only three, silently omitting `Paper`. In addition, `Trash` itself was also edited to declare `def hazard(self) -> str:` (marked by `# New requirement, so a new method here` in the listing), meaning adding the operation touched the base class as well as the subclasses.
* **Instruction:** Change "all three material classes" to "the base class and all three material classes shown (four in `trash.py`, where `Paper` is also present)".

**2. Section: One singledispatch Function per Operation (Base class modification required by methods)**

* **Target Text:** "A third operation and a fourth are one more file each, where `note_methods.py` needs one edit per material every time."
* **Issue:** Adding an operation via methods requires modifying the base class `Trash` so that the method exists on `Trash` polymorphically and satisfies type checkers, in addition to editing each concrete subclass. In contrast, `singledispatch` leaves both the base class and subclasses untouched in their original module.
* **Instruction:** Update the sentence to note that adding methods requires editing the base class `Trash` in addition to every material subclass.

**3. Section: Exercises (Exercise 4 placement of `CrushedAluminum`)**

* **Target Text:** "4.  Derive `CrushedAluminum` from `Aluminum`,"
* **Issue:** `recycling_note.py` iterates over `Trash.registry.values()`, which is populated when `trash.py` is imported. If a reader derives `CrushedAluminum` in `recycle_dict.py`, running `recycling_note.py` will not have `CrushedAluminum` in `Trash.registry` and cannot demonstrate the MRO fallback. Exercise 1 explicitly directed "Add a `Plastic` material to `trash.py`", but Exercise 4 leaves the file location unspecified.
* **Instruction:** Change to "4.  Derive `CrushedAluminum` from `Aluminum` in `trash.py`,".

## Verdicts

Second run, on the Flash model. Applied in commit 92eaba23, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. `[1]` iterates `[Aluminum, Glass, Cardboard]`, so its count of 3 leaves out the edited `Trash` base; with the base `hazard()` deleted, `ty` still passed the listing's loop but reported `unresolved-attribute` for `t.hazard()` on a parameter typed `Trash`. The prose now says `[1]` counts the material classes, that the base takes an edit so a `Trash` such as a piece from `parse()` can call `hazard()`, and that one operation is four edits; the `Paper` parenthetical was left out, since in `trash.py` `Paper` would inherit the base's `"none"`.
2. Applied. The same undercount as item 1, two sections later: the sentence now reads "needs an edit to the base and to each material every time", which keeps the comparison with `disposal_hazard.py`'s zero edits consistent with item 1's wording.
3. Applied. `recycling_note.py` reads `Trash.registry` from its own `import trash`, so a `CrushedAluminum` defined in `recycle_dict.py` never reaches the `recycling_note.py` run the exercise asks for. The exercise now says "in `trash.py`", matching exercise 1's `Plastic`; the Solutions quote regenerated.
