<!-- outside review of Chapters/09_Foundations--Class_Attributes.md, model gemini-3.1-pro-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `09_Foundations--Class_Attributes.md` chapter:

**1. Section: Two Dictionaries, One Lookup (Slots and explicit dict)**

* **Target Text:** "A class that declares `__slots__`, or a data class built with `slots=True`, has no instance `__dict__`, provided every base class is slotted too."
* **Issue:** A slotted class can still have an instance dictionary if the developer explicitly includes `"__dict__"` in its `__slots__` tuple. The absolute claim misses this explicit opt-in mechanism that allows dynamic attributes alongside memory-optimized slots.
* **Instruction:** Change the target text to: "A class that declares `__slots__` without including `"__dict__"`, or a data class built with `slots=True`, has no instance `__dict__`, provided every base class is slotted too."

**2. Section: Two Dictionaries, One Lookup (Property storage precision)**

* **Target Text:** "One kind of class attribute follows a different rule. A `@property` owns its name on the class, so reading calls its getter and assigning calls its setter, and neither one touches the instance dictionary."
* **Issue:** A property's getter or setter often writes to a private backing attribute (like `self._rating`), which absolutely does touch the instance dictionary. The descriptor mechanism itself bypasses the dictionary only for the property's *own name*.
* **Instruction:** Change the target text to: "One kind of class attribute follows a different rule. A `@property` owns its name on the class, so reading calls its getter and assigning calls its setter, bypassing the instance dictionary for that name."

**3. Section: A Shared Mutable Value (Mutable defaults in normal classes)**

* **Target Text:** "A mutable default belongs in a `@dataclass` field with a [`default_factory`](12_Techniques--Data_Classes_as_Types.md#defaults-built-not-shared)."
* **Issue:** This abrupt single-sentence paragraph points the reader to `@dataclass` as the only fix for a shared mutable class attribute, leaving plain classes unaddressed. In a normal class, the fix is to initialize the per-object storage inside `__init__`.
* **Instruction:** Change the target text to: "A per-object mutable default belongs inside `__init__`, or in a `@dataclass` field with a [`default_factory`](12_Techniques--Data_Classes_as_Types.md#defaults-built-not-shared)."

**4. Section: A Shared Mutable Value (Augmented assignment on mutable attributes)**

* **Target Text:** "Because shadowing starts with an assignment and `.append()` makes none, a read followed by a mutation slips past the rule."
* **Issue:** Readers might assume that an augmented assignment like `a.items += ["pear"]` is safe because it performs an assignment and therefore shadows. However, for a mutable object like a list, `+=` invokes `__iadd__`, which mutates the shared list in place *before* assigning it back to the instance, causing the change to leak anyway.
* **Instruction:** Change the target text to: "Because shadowing starts with an assignment and `.append()` makes none, a read followed by a mutation slips past the rule. Even an augmented assignment like `a.items += ["pear"]` mutates the shared list before shadowing it, so the change still leaks."

## Verdicts

Applied in commit 8e8645f0, after each item was tested against the chapter and run under `uv run`. The reply opened with a leaked block of the model's own planning notes before the review; that block is removed above.

1. Rejected. The sentence links `__slots__` to its full treatment, and the `"__dict__"` opt-in is covered where slots are taught: chapter 07's slots section says a `"__dict__"` entry in `__slots__` gives the dictionary back, and chapter 18's `cached_property` paragraph repeats it. This sentence states the default case, and adding the opt-in here would duplicate the linked section.
2. Applied, with a different fix. The setter the chapter links, `Circle`'s `radius`, writes `self._radius`, which lands in the instance dictionary, so "neither one touches the instance dictionary" was false for the common setter. The sentences now say the getter and setter stand in for the dictionary lookup for the property's own name, and that whatever the setter stores goes into the dictionary under its own name.
3. Applied, with a different fix. The one-sentence paragraph named only the `@dataclass` fix, while the chapter's own Real Per-Object Defaults section gives the plain-class fix, a constructor assignment. The sentence now names `__init__()` first, with a link to that section, and keeps the `default_factory` pointer.
4. Applied. A probe with `items = []` on a class and `a.items += ["pear"]` left `A.items`, `b.items`, and `a`'s own new instance attribute all equal to `['pear']`: `__iadd__()` mutates the shared list and the assignment then shadows with the same object, so the change leaks although an assignment happened. Since the paragraph's rule is "shadowing starts with an assignment", the reader needs this case named; two lines now do so.
