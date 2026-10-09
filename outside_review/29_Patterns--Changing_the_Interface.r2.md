<!-- outside review of Chapters/29_Patterns--Changing_the_Interface.md, model gemini-3.8-flash-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `29_Patterns--Changing_the_Interface.md` chapter:

**1. Section: Façade (Abstract Factory pattern conflation)**

* **Target Text:** "A *Façade* is often a [*Singleton*](24_Patterns--Singleton.md)
[*Abstract Factory*](27_Patterns--Factory.md#abstract-factories).
GoF supplies both halves of that combination.
One *Façade* object is usually enough, which makes it a *Singleton*,
and an *Abstract Factory* creates the subsystem's objects for it.
A class containing static factory methods covers both halves:"
* **Issue:** In GoF, *Façade* and *Abstract Factory* are distinct patterns; GoF notes that an Abstract Factory can be used *with* a Façade to construct subsystem objects polymorphically, not that a Façade *is* an Abstract Factory. In `facade.py`, `Facade.start_car()` is a static factory method constructing concrete classes directly (`Ignition(FuelPump(Engine()))`), which contradicts the definition of an *Abstract Factory* (producing families of related objects without specifying concrete classes) set in chapter 27.
* **Instruction:** Clarify that a Façade often incorporates factory methods to assemble subsystem objects for the caller rather than being an *Abstract Factory*, with proposed wording: "A *Façade* is often a [*Singleton*](24_Patterns--Singleton.md) that creates the subsystem's objects for callers. GoF notes that one *Façade* object is usually enough, which makes it a *Singleton*, and factory methods can build the subsystem objects. A class containing static factory methods covers both roles:"

**2. Section: Façade (Listing description omits subsystem class)**

* **Target Text:** "*Façade* puts a class there that takes over construction,
so the caller stops naming `Engine` and `FuelPump`."
* **Issue:** In `facade.py`, the subsystem consists of three classes: `Engine`, `FuelPump`, and `Ignition`. A caller constructing the subsystem directly would instantiate all three (`Ignition(FuelPump(Engine()))`), but `Facade.start_car()` encapsulates construction of `Ignition` as well. Stating that the caller stops naming only `Engine` and `FuelPump` misdescribes what the listing's façade encapsulates.
* **Instruction:** Include all three subsystem classes in the sentence: "*Façade* puts a class there that takes over construction, so the caller stops naming `Engine`, `FuelPump`, and `Ignition`."

**3. Section: Distinguishing the Wrappers (Mismatch between prose and comparison table)**

* **Target Text:** "That leaves the "What it adds" column to separate them:
a *Proxy* controls access to one implementation,
an *Adapter* makes one type fit a caller that expects another."
* **Issue:** In the preceding table, the "What it adds" column explicitly specifies `"nothing"` for *Adapter*, while `"the fit between caller and callee"` is placed in the "Remove it and you lose" column. Stating that the "What it adds" column separates them by assigning that adaptation role to Adapter contradicts the table's explicit entry.
* **Instruction:** Adjust the sentence to align with the table's columns: "That leaves the last two columns to separate them: a *Proxy* adds access control (losing control over reaching the implementation), whereas an *Adapter* adds no new behavior and only restores the fit between caller and callee."

**4. Section: Deprecating the Old Interface (Class deprecation runtime vs. static behavior)**

* **Target Text:** "The decorator also applies to a class,
where it warns on construction and on subclassing."
* **Issue:** In Python 3.13+ (PEP 702), `@warnings.deprecated` on a class wraps `__new__`, so only instantiation emits a runtime `DeprecationWarning`. Subclassing does not instantiate the class and issues no runtime warning; type checkers (`ty`, Pyright, mypy) report subclassing statically. Lumping construction and subclassing together without qualification misleads readers, especially since the subsequent paragraph explicitly notes that overload deprecation is static-only.
* **Instruction:** Clarify that the subclassing warning is static-only: "The decorator also applies to a class, where it warns on construction at runtime, and warns on both construction and subclassing in the type checker."

## Verdicts

Second run, on the Flash model. Applied in commit d16fb344, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. GoF's Related Patterns for *Façade* says an *Abstract Factory* "can be used with Facade," and `Facade.start_car()` builds concrete classes directly, so "a *Singleton* *Abstract Factory*" overstated it; the paragraph now calls a *Façade* a *Singleton* that also creates the subsystem's objects, says an *Abstract Factory* can work with a *Façade* to create them without naming their concrete classes, and says static factory methods cover both halves when one set of concrete classes is enough.
2. Applied. The figure's assembly panel shows the caller building `Ignition(FuelPump(Engine()))` and the *Façade* panel shows it naming `Facade`, so the caller stops naming all three; the sentence now reads "the caller names `Facade` in place of `Ignition`, `FuelPump`, and `Engine`."
3. Applied, with a different fix. The table's "What it adds" column gives *Adapter* "nothing," and the fit comes from the last column, so the sentence now says "the last two columns" separate them and keeps its two clauses, which match those columns.
4. Rejected. On 3.15.0rc2 a class marked `@warnings.deprecated` issued the `DeprecationWarning` at runtime both when constructed and when subclassed (`class Sub(Old): pass` recorded one warning), since the decorator wraps `__init_subclass__()` as well as `__new__()`; `ty` also reported both. The chapter's sentence is right as written.
