> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 07_Foundations--Classes (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I checked each claim against its listing, the sections it links in chapters 08, 09, 12, 17, 18, 20, and 24, the committed `#:` markers, and `ty` 0.0.84 probes for the three places the chapter describes what a checker reports.
Both quoted `invalid-explicit-override` diagnostics match what `ty` prints today, including the `info:` line in the Solutions file.
`typing.override` sets `__override__` and returns the same function, as the chapter says.
`tip verify-ch CH=07` passes 24 of 24.

## Applied directly

Chapter, corrections:

- "Caching with `cached_property`": "A class declared with `slots=True` ([Performance]... uses it)" named a data class argument five chapters before data classes, and linked the Slots section, which never pairs slots with `cached_property`. Now "a class that declares `__slots__`", with the consequence stated (the first access raises a `TypeError`, confirmed by a probe) and the link moved to "When Slots Does Not Fit", whose `slots_limits.py` shows that failure.
- "Marking Overrides": "Two kinds stay undecorated by convention" read as a Python community convention. It is the book's rule, so it now says "This book leaves two kinds undecorated."
- After `demo_subclass.py`: "as the overridden `show()` does" pointed at the overriding method. The overridden one is `Simple.show()`. Now "as `Derived`'s `show()` does."

Chapter, teaching:

- After `demo_subclass.py`: the output shows the inherited `show_twice()` running `Derived`'s override, and no sentence said why. Added a paragraph: the lookup starts at the class of the object, so base-class code reaches a method the subclass replaced. The stray "`Derived` also inherits `show_twice()` unchanged" under "Calling the Base Constructor" moved into it.
- "Method Resolution Order": the prose said `A` comes first and never said what put it there. Added that the bases appear in the order the `class` statement lists them, and that `class C(B, A)` reverses the result.
- "Properties": added the near-miss. `c.area()` reads the property and calls the `float`, which raises a `TypeError` (probed).
- "Marking Overrides": the quoted diagnostic had no tie to the commented-out decorator in `Typo`. Added "With the decorator above `shwo()` uncommented, `ty` reports:".
- `forgot_self.py` followed a paragraph about `self` with no lead-in. Added "`forgot_self.py` leaves the parameter out:".
- "Ignore the `@override` decorator for now" now says where the explanation is, with a link to the section.
- `__dict__` appears two chapters before chapter 09 explains it. Added a gloss ("the dictionary that holds the instance's attributes") and a link to "Two Dictionaries, One Lookup".

Chapter, links and wording:

- Three bare chapter links now name the section that supports the sentence: `Protocol` to "Structural Typing with Protocols", the multiple-inheritance remark to "One Class, Many Protocols" (the diamond-problem paragraph), and both "sets that tool up" links to "The Type Checker: `ty`".
- Dropped "itself" twice ("a method the language itself calls", "the class itself") and "plain" twice ("a plain module-level function", "a plain method"), where the sentence reads the same without the word.

Solutions:

- Exercise 3: `Simple.show()` printed with `msg + ":"` where the chapter's `simple_class.py` uses `f"{msg}:"`. The copy now follows the chapter.
- Exercise 3: the prose said the solution strips the constructor `print()` calls "from `simple_subclass.py`", but one of the two is in `simple_class.py`. Reworded to name the two classes.
- Exercises 2 and 5: added the blank line after the slug comment that the other listings carry.
- Exercise 2: `Temperature.from_kelvin` and `from_fahrenheit` take empty parentheses; "classmethods" is "class methods", as in the chapter.
- Prose: two imperative-plus-consequence sentences in exercise 6 rewritten as conditions, "exactly" dropped twice, "Python has no opinion" and "the runtime is indifferent" restated literally, a comma splice split.

## Considered and declined

- `simple_subclass.py` prints "Overridden show() method" from the overriding method and its comment says "from inside the overridden method". Strictly the overridden method is the base one. The phrase also reads as "`show()`, now overridden", and changing it moves five markers in the chapter and two in Solutions exercise 3 for no gain in understanding. Left alone; the prose sentence was the only ambiguous use.
- `forgot_self.py` keeps its `try`/`except`. Through `expect(TypeError, Oops().show)` the checker sees nothing and the `# type: ignore` the prose explains goes unused (recorded 2026-09-16).
- The class-body `import` aside stays where the 2026-09-03 ruling put it.
- No exercise on the MRO. The new `class C(B, A)` sentence covers the one experiment such an exercise would ask for.
- The listings carry no type hints. Chapter 08 introduces them, and chapters 04 through 07 are unannotated as a set.
- The comment between `@classmethod` and `def from_fahrenheit` is an existing comment and the line has no room for it at 60 columns.
