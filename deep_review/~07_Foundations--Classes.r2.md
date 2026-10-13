> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 07_Foundations--Classes (2026-10-13)

Nothing here needs your decision, so the file has no live blocks.
I read the chapter and its Solutions file against `deep_review_db.md` and `~07_Foundations--Classes.md`, checked each claim against its listing, and probed the rest under `uv run` (Python 3.15.0, `ty` 0.0.86): `typing.override`'s source, `cached_property` having no `__set__`, a setter decorated under another name, `{p}` against `{p!s}`, and the five float values the Solutions file quotes for exercise 2.
All held.
`tip verify-ch CH=07 ISOLATED=1` passed 27 of 27 before the edits and 27 of 27 after; `tip prose CH=07` reports no new hits.

## Applied directly

Chapter, corrections:

- "Marking Overrides": "The `@override` decorator ... catches that bug" credited the decorator with the type checker's work; the next paragraph and the Solutions both say the decorator does nothing at run time. Now "lets a type checker catch that bug."
- "Marking Overrides", opening: "When you override a method, nothing requires the name to match a method in the base class" contradicted itself (an override matches by definition). Now "Python accepts any method name in a subclass. If you misspell the name of a method you mean to override, ..."
- After the C++/Java field paragraph: "The assignment creates space for that attribute" restated the sentence before it with a vague image. Replaced with the consequence: the attributes an object carries depend on which of its methods have run.
- "String Representation": `__repr__()` returns "the text of a call", since it returns a string.
- "Static and Class Methods": "`Reading.from_fahrenheit(212)` proves it" pointed at nothing specific, and "hard-codes `Temperature` into every subclass" left the result unsaid. Now the sentence says the call passes `Reading` as `cls`, and that `return Temperature(...)` would make `Reading.from_fahrenheit()` return a `Temperature`.
- Exercise 6: "does not change" is "stays the same" (the Solutions quote follows through `tip statements`).

Chapter, teaching:

- "Adding a Setter": the chapter never said how `@radius.setter` works. Added a paragraph: `@property` binds a property to `radius`, `setter()` returns a new property holding both functions, and the setter's `def` name rebinds it; that is why the getter comes first. The stray "The setter is written second because ..." sentence after `property_recursion.py` moved into it, and the duplicate "A getter alone gives a read-only property" became the lead-in to the write-only remark.
- "Adding a Setter": added the near-miss a Java reader writes, `@radius.setter` over `def set_radius(...)`. The property then binds to `set_radius`, `radius` stays getter-only, and the constructor's assignment raises an `AttributeError` (probed: "property 'radius' of 'Circle' object has no setter").
- "Caching with `cached_property`": the chapter said where the value is stored but not why the method stops running. Added that attribute lookup checks the instance first (the rule chapter 09's linked section teaches), and split the slots consequence into its own paragraph.
- Same section: `del n.total` ran in the listing with only a comment. Added that it removes the stored value and the next read runs the method again.

Solutions:

- Exercise 1: "`shrink()` does not touch `self._radius`. It assigns to ..." restated positively in one sentence.
- Exercise 4 hint: "A cached property is an ordinary attribute access" named the wrong thing as the access. Now "Inside `average`, reading `self.total` is an ordinary attribute access."
- Exercise 6: the "Miss the base-class method" paragraph said twice that `shwo()` is a new method and opened on "Nothing overrides anything." Tightened to one statement of each fact.

## Considered and declined

- `forgot_self.py`'s `try`/`except`, the class-body `import` aside, an MRO exercise, unannotated listings, the comment between `@classmethod` and its `def`, and "Overridden show() method" in the markers: all settled by the previous review; not reopened.
- A listing for the `set_radius` near-miss. One sentence with the exact error carries it, and a fourth `Circle` listing in the section would outweigh the point.
- "Because Python is dynamically typed, it applies an operation to an object without checking an interface first" is a negative statement, but the absence of a check is the claim the section argues from.

## For the session

Nothing. No cross-chapter errors found, no NEW baseline hits, and every listing ran.
