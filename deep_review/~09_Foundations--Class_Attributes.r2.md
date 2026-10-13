> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 09_Foundations--Class_Attributes (2026-10-13)

Part of the 2026-10-13 sweep.
This run has no live blocks.
I checked each claim against its listing, against `ty` 0.0.86 and Pyright 1.1.414 with a scratch probe of every checker claim the chapter makes, and against the pinned interpreter for the runtime claims (the read-only `mappingproxy`, slots, `@dataclass` skipping a `ClassVar`, the `@classmethod` fork).
I ran every extracted listing directly and compared it with its markers.
`astral-sh/ty` issue 2158 is still open, so the version-pinned gap paragraph still holds.
`deep_review_db.md` and `~09_Foundations--Class_Attributes.md` were read, and nothing below re-proposes their rejections or declined items.
`tip verify-ch CH=09 ISOLATED=1` passed 27 of 27 before the edits and 27 of 27 after.

## Applied directly

Chapter, corrections:

- "ClassVar and Inheritance", the `Right` paragraph: said `ty` accepts `Right().shared = 5` and only Pyright rejects it. `ty` 0.0.86 now carries the base's declaration to the bare override and reports `invalid-attribute-access` for both `Left().shared = 5` and `Right().shared = 5`, as Pyright does. The paragraph now says the override is still a `ClassVar` and the type checker rejects both writes; the advice to restate `ClassVar[int]` went with the gap (no version history, per `deep_review_db.md`).

Chapter, teaching:

- "What `ClassVar` Catches": "`@dataclass` does read it at runtime" stated the fact with no consequence. It now says `@dataclass` leaves a `ClassVar` out of the fields it generates (probed: `fields()` omits it).
- "Two Dictionaries, One Lookup": `vars()` is now tied to `__dict__` at its first use, since the slots paragraph four lines later speaks of an "instance `__dict__`" the reader had not met by that name.

Chapter, prose:

- "A Shared Mutable Value": "A type checker accepts the line too." and its reason were two sentences; joined with "since", and "A" became "The".
- "When you genuinely want one shared value" is "When you intend one shared value", matching the section's later "when you intend the sharing".
- "Declaring a `ClassVar` and leaving the value elsewhere is deliberate" claimed it always is; now "The common reason to declare a `ClassVar` and leave its value elsewhere is a base class that names what its subclasses must supply".
- "since the value is checked against the declared `ClassVar[int]`" (Vale passive) is "since the checker compares the value with the declared `ClassVar[int]`".

Solutions:

- Exercise 7: the paragraph about the `type(self).total += 1` alternative opened the Solution step, before the listing, and said "this listing prints `2 2 2` too" before the reader had seen any output. It now closes the solution, after the `Counting` explanation, and says the subclass count comes after `c` and `d`.
- Exercise 7: the step label "**Silence the checker's report.**" headed a paragraph about what the checker reports once the ignore is removed; now "**Read the checker's report.**"
- Exercise 8: "The inheritance rule is harmless on its own" was followed by a sentence about both rules; now "Each rule is harmless on its own."
- Exercise 5: "Nobody inspects a plain class body" is "Without the decorator, Python runs the class body as written".

## Considered and declined

- **Exercise 4's title, "A plain class attribute masquerading as shared state".** The attribute is shared state, so "masquerading" fits loosely. Renaming the title changes what `exercise_refs.py` pairs with every "exercise 4" reference, and the wording does no harm.
- **"provided every base class is slotted too" (Vale passive).** "Slotted" is an adjective here, the book's term for a class with `__slots__`.
- **The `@property` and method asides after `inside_objects.py`.** Four short paragraphs follow the core listing (the proxy, slots, methods, properties). Each states an exception to the rule it sits beside, and the previous review kept the same arrangement.

## For the session

- `tools/data/watch_words_baseline.txt` now carries one stale entry for chapter 09 (`want: When you genuinely want one shared value`); `tip watch-words` reports it as stale. The sentence was reworded.
- The `tool-upgrade` skill's probe "a subclass under a bare `ClassVar` declaration" covers `sides` but not the instance-write case this chapter used to pin: `ty` 0.0.86 now rejects `Right().shared = 5` on a bare override of a base `ClassVar`. Worth adding that line to the probe so a regression shows up on the next upgrade.
