<!-- outside review of Chapters/07_Foundations--Classes.md, model gemini-3.1-pro-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `07_Foundations--Classes.md` chapter:

**1. Adding a Setter: Adding a setter vs property conversion**

* **Target Text:** "Code outside the class reads both versions the same way,
and that is why you can wait to add a setter until you need one."
* **Issue:** A plain attribute natively supports both reading and writing. Converting it to a validated property requires adding both a getter and a setter at the same time to preserve that writability. The uniform syntax lets you wait to convert the attribute to a property, rather than just waiting to add a setter to an existing property.
* **Instruction:** Change to "Code outside the class reads both versions the same way,
and that is why you can wait to convert an attribute to a property until you need to."

**2. Method Resolution Order: super() traversal**

* **Target Text:** "`super()` and ordinary attribute lookup both follow one list,
the class's *method resolution order* (MRO).
The MRO names the classes Python searches for a name,
starting with the class and ending at `object`."
* **Issue:** While ordinary lookup searches the entire MRO starting from the object's class, `super()` delegates to the next class in line. It avoids infinite recursion by starting its search from the class *after* the one where `super()` is invoked.
* **Instruction:** Replace with:
"`super()` and ordinary attribute lookup both follow one list,
the class's *method resolution order* (MRO).
Ordinary lookup searches the whole list starting with the class,
but `super()` searches starting from the class after the current one,
which is how it avoids calling itself."

**3. Inheritance: Instance vs class lookup**

* **Target Text:** "The lookup starts at the class of the object,
not at the class that defines the calling method,
so base-class code reaches a method the subclass replaced."
* **Issue:** Attribute lookup in Python always starts at the object instance itself, not its class. The search falls back to the class and its MRO only because the instance dictionary doesn't contain the method (which lives on the class).
* **Instruction:** Change to "The lookup starts at the object itself,
not at the class that defines the calling method,
so base-class code reaches a method the subclass replaced."

## Verdicts

Applied in commit 7134cb0c, after each item was tested against the chapter and run under `uv run`.

1. Applied. In `properties.py` `radius` is a plain attribute, readable and writable, and `property_setter.py` converts it into a property with a getter and a setter in one step; the paragraph's own "began as a plain attribute and is now a validated property" names that conversion, so "wait to add a setter" misnamed what the reader defers. The sentence now says "wait to convert an attribute into a property until you need the validation".
2. Applied, with a different fix. The chapter described the MRO as ordinary lookup walks it and said nothing about where `super()` starts, although `Derived.show()` calls `super().show(msg)` two sections earlier and relies on the search skipping `Derived`. One sentence after the MRO description now says `super()` searches the same list starting with the class after the one whose method calls it, so `super().show(msg)` in `Derived` reaches `Simple`'s `show()`. The reviewer's replacement dropped the "starting with the class and ending at `object`" description, which stays.
3. Rejected. The paragraph contrasts the object's class (`Derived`) with the class that defines the calling method (`Simple`), and `show()` lives on a class, so `self.show()` resolves at `Derived` with no instance entry to find; "the object itself" would blur the contrast the sentence makes. The instance-dictionary-first order is the subject of chapter 09's "Two Dictionaries, One Lookup" ("Reading an attribute checks the instance first, then falls back to the class"), which this chapter links in its slots section.
