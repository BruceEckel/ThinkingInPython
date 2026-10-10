<!-- outside review of Chapters/07_Foundations--Classes.md, model gemini-3.8-flash-high, 2026-10-10 -->

**Please apply the following technical and structural refinements to the `07_Foundations--Classes.md` chapter:**

**1. Section: Inheritance (correction to code description)**

* **Target Text:** "In the constructor, `super().__init__()` calls the base-class constructor."
* **Issue:** In [`simple_subclass.py`](file:///C:/git/ThinkingInPython/Chapters/07_Foundations--Classes.md), `Derived.__init__` invokes `super().__init__(text)`, not `super().__init__()`. Because `Simple.__init__` requires the `text` parameter, calling `super().__init__()` without arguments would fail with a `TypeError`. The prose sentence misdescribes its own listing by dropping the argument (unlike the later section *Calling the Base Constructor*, which cites `super().__init__(text)` correctly).
* **Instruction:** Change `super().__init__()` to `super().__init__(text)` so it matches the listing. Proposed wording: "In the constructor, `super().__init__(text)` calls the base-class constructor."

**2. Section: Adding a Setter (technical precision on decorator mechanics)**

* **Target Text:** "The getter and setter are independent, so you choose the access you want by defining one or both."
* **Issue:** With `@property` decorator syntax, getters and setters are not independent. The setter decorator `@<name>.setter` is an attribute of the existing property object created by `@property`; attempting to define only a setter with `@<name>.setter` raises a `NameError` at class definition time because the property name does not yet exist. Defining only a getter creates a read-only property, but a setter cannot be defined alone using this decorator syntax.
* **Instruction:** Clarify that while a getter alone creates a read-only property, the setter decorator requires the property object created by `@property` to already exist. Proposed wording: "Defining only a getter gives you a read-only property, but the two are not symmetrical in decorator syntax: `@<name>.setter` requires the property object created by `@property` to already exist on the class."

**3. Section: Calling the Base Constructor (clarification of base constructor execution)**

* **Target Text:** "Unlike C++ and Java, Python never calls a base-class constructor on its own."
* **Issue:** Unqualified, this claim appears to contradict the sentence immediately following the listing: "A derived class that defines no constructor of its own inherits and runs the base version." In Python, the base `__init__` runs automatically whenever the subclass defines no constructor of its own; Python omits the implicit call only when the subclass defines its own `__init__`.
* **Instruction:** Specify that the absence of an automatic base call applies when a derived class defines its own constructor. Proposed wording: "Unlike C++ and Java, Python never calls a base-class constructor on its own when a derived class defines its own constructor."

**4. Section: String Representation (precision on f-string conversion flags)**

* **Target Text:** "In an f-string, `{p}` selects `__str__()` and `{p!r}` selects `__repr__()`."
* **Issue:** In an f-string, `{p}` invokes `__format__()`, which only falls back to `__str__()` via `object.__format__` if no custom format method is defined on the class. The true symmetric conversion specifier that explicitly selects `__str__()` (matching `{p!r}` for `__repr__()`) is `{p!s}`.
* **Instruction:** Introduce the `{p!s}` conversion flag alongside `{p!r}` so readers see the explicit specifier. Proposed wording: "In an f-string, `{p!s}` (and unadorned `{p}` when no custom `__format__()` exists) selects `__str__()`, while `{p!r}` selects `__repr__()`."

## Verdicts

Second run, on the Flash model. Applied in commit d544e44e, after each item was tested against the chapter and run under `uv run` on 3.15.0rc2.

1. Applied. `simple_subclass.py` line 151 reads `super().__init__(text)`, and `Simple.__init__()` takes `text`, so the sentence dropped the argument its listing passes. It now names `super().__init__(text)`.
2. Applied, with a different fix. A probe class with `@x.setter` and no `@property` above it failed at class creation with `NameError: name 'x' is not defined`, so "independent" misdescribed the decorator form; `property(fset=...)` built a write-only property whose read raised `property 'v' of 'W' object has no getter`. The paragraph now says a getter alone gives a read-only property, that the setter is written second because `@radius.setter` needs the property the getter created, and that a write-only property is built with `property(fset=...)`, keeping the "rare, a method expresses that intent better" advice.
3. Applied, with a different fix. The sentence after `missing_super.py` says a derived class with no constructor inherits and runs the base version, which contradicted "never calls a base-class constructor on its own". The sentence now reads "Python adds no call to the base-class constructor when a derived class defines its own", the condition the reviewer asked for in fewer words.
4. Applied, with a different fix. A probe class with `__str__()` and `__repr__()` gave `str str repr` for `{p} {p!s} {p!r}`, and a subclass adding `__format__()` gave `format str repr`, so `{p}` goes through `__format__()` and reaches `__str__()` only when the class defines none, as `Point` does not. The sentence now gives `{p!r}` for `__repr__()` and `{p}` or `{p!s}` for `__str__()` "for a class that defines no `__format__()`", stating the condition without the reviewer's parenthetical.
