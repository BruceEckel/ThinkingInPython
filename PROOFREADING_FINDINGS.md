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

> **04_Functions.md:23** (conceptual) — APPLIED
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

> **06_Classes.md:139 and :145** (terminology) — APPLIED
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

---

> **21_State_Machines.md:226-231** (prose does not match the code)
> The paragraph introducing `StateT` says it "adds a `Map` and a method to
> initialize the map from a two-dimensional array," and that the `next()`
> methods "test for a `null Map` ... and initialize it if it's `null`." The
> Python code has no `Map`, no `null`, and no two-dimensional array: it uses a
> `dict` named `transitions`, tests `if not self.transitions`, and each subclass
> builds its dict inline. This is leftover Java-translation prose. Suggest
> rewriting to: a dict of transitions, lazily initialized on first `next()`
> when it is still `None`.

---

> **21_State_Machines.md exercises 6, 7, 12** (Java leftovers)
> The exercises use Java vocabulary and mechanics: ex 7 says "Use a `HashMap`",
> "the key is a `String`", "override a method `nextState()`", and ex 12 ends
> with "before `hasNext()` returns `false`". Ex 6 refers to a `transition_table
> .py` that does not exist in the chapter. Suggest Pythonizing: `dict`, `str`,
> `next_state()`/snake_case, `False`, and pointing ex 6 at the real
> `tabledriven/` files (or dropping it).

---

> **26_Observer.md:5-12** (broken opening paragraph)
> The chapter opens with a sentence fragment: "*Observer*, and a category of
> callbacks called 'multiple dispatching (not in *Design Patterns*)' including
> the *Visitor* from *Design Patterns*." There is no main verb, and the next
> sentence's "this contains a hook point" has no clear referent. Line 10 also
> has an awkward possessive, "based on other object's change of state". Suggest
> a rewrite, e.g.: "The *Observer* pattern is a kind of callback: an object
> registers interest in another object and is notified when that object's state
> changes. It is the most dynamic of the callback patterns. (A related family,
> multiple dispatching, includes the *Visitor* pattern from *Design Patterns*;
> see the Multiple Dispatching and Visitor chapters.)"

---

> **28_Visitor.md exercises 2-3** (unconverted Java)
> Exercise 2 uses `getWeapon()` and "member function"; exercise 3 contains
> literal Java: "create a `Map` of `Map`s", `o1.getClass()`, and the cast
> expression `((Map)map.get(o1.getClass())).get(o2.getClass())`. Suggest
> Pythonizing to a `dict` of `dict`s keyed by `type(o1)`/`type(o2)`,
> `type(...)` instead of `getClass()`, snake_case method names, and "method"
> instead of "member function". (Same class of issue as the State Machines
> exercises.)
