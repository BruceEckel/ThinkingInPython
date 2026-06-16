# Proofreading Findings (for review)

Confusing or awkward sentences flagged during the prose pass, with proposed
rewrites. These are NOT applied. The user decides which to take.

Mechanical fixes (spelling, doubled words, em-dashes, run-ons) are applied
directly and committed per chapter, so they are not listed here.

Format per entry:

> **NN_Chapter.md:LINE**
> Original: ...
> Proposed: ...
> Why: ...

---

> **03_Containers_and_Control_Flow.md:38-39**
> Original: "It's as if Python is designed so that you only need to press the
> keys that absolutely must."
> Proposed: "It's as if Python is designed so that you only press the keys that
> are strictly necessary."
> Why: "the keys that absolutely must" is an incomplete clause (must *what?*),
> so it reads as if a word is missing.

---

> **04_Functions.md:23** (conceptual)
> Original: "Python is a *structurally-typed* language, which means it puts the
> minimum possible requirements on typing."
> Proposed: "Python is *dynamically typed*, so it puts the minimum possible
> requirements on typing." (or frame the example as *duck typing*)
> Why: Python is dynamically typed; "structural typing" is the Protocol concept
> used in the Static Type Checking and Rethinking Objects chapters. Calling the
> language "structurally-typed" here is inaccurate and clashes with that usage.

---

> **04_Functions.md:97** (conceptual / incorrect)
> Original: "Thus, a default value creates an implicit global variable."
> Proposed: "Thus a mutable default persists between calls: it is created once,
> at definition time, and lives on the function, not recreated on each call."
> Why: the shared default is not a global variable. It is one object bound to
> the function object. The current sentence states something false.

---

> **06_Classes.md:139 and :145** (terminology)
> Original: "demonstrates weak typing" ... "to provide weak typing in a
> strongly-typed language."
> Proposed: "demonstrates duck typing" ... "to provide duck typing in a
> statically-typed language."
> Why: Python is strongly typed (no implicit coercion), just dynamic. What
> `f()` shows is duck typing / polymorphism, not "weak typing." Line 60 of the
> same chapter already (correctly) says "Python is dynamically typed," so the
> "weak typing" wording is also internally inconsistent.

---

> **06_Classes.md:67-91** (structural redundancy)
> The Inheritance section re-explains modules, `import`, `from module import
> name(s)`, and PYTHONPATH/CLASSPATH at length. All of that is now covered in
> the preceding Modules and Packages chapter (05), so post-split it is
> redundant here. Suggest trimming to the one point inheritance needs: you
> import the base class before subclassing it (as `simple2.py` imports
> `Simple`). Flagging rather than cutting, since it is a sizable removal.
