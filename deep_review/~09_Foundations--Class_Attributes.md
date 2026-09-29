> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 09_Foundations--Class_Attributes (2026-09-29)

Part of the book-wide sweep of chapters 01-29 and the appendices, run in a worktree on branch `review/09`.
Nothing here needs your decision, so the file has no live blocks.
I checked each claim against its listing, against the sections the chapter links (05, 07, 08, 12, 18, 37, 38), against `ty` 0.0.84 and Pyright 1.1.414 with a scratch probe of every checker claim, against the pinned interpreter for the runtime claims (slots, the `cls` fork, the bare annotation), and against `astral-sh/ty` issue 2158, which is still open.
`deep_review_db.md` was read; its chapter 09 entry (the augmented-assignment gap) still holds under 0.0.84.
`tip verify-ch CH=09` passes 24 of 24, and `tip exercise-refs` reports 0 new.

## Applied directly

Chapter, corrections:

- `far_from_the_cause.py` did not show the bug its section describes. The section says a change to the class attribute reaches every object but the one that shadowed; the listing never changed the class attribute, so its output (`1`, `5`) matched what real per-object storage prints, and the prose called `show(b)`'s `5` "surprising" when it was the unchanged default. The listing now has `rerate()`, which assigns `Stars.rating`, and `show(a)` prints the stale `1` beside `show(b)`'s `9`. The paragraph under it is rewritten to match. It also drops "does not import", which meant nothing for functions in one file.
- "A subclass overriding a `ClassVar` inherits the name but not the type checker's guard" held for `ty` alone. Pyright rejects both `Left().shared = 5` and `Right().shared = 5`. The passage now names `ty`, says what Pyright does, and keeps the advice to restate `ClassVar[int]`.
- "A class declared with `slots=True`": `slots=True` is a `@dataclass` argument, and the linked section opens with `__slots__`. Now "A class that declares `__slots__`, or a data class built with `slots=True`". Both forms raise the `AttributeError` the paragraph describes (probed).
- "Stubs and *Protocols* use the same form throughout, since neither carries values": stub files are introduced nowhere before this chapter, a Protocol member can carry a value, and the italics marked no new term. Now one sentence about `Protocol`, linked to chapter 08's section.
- The `ty` gap paragraph: "promises more than `ty` 0.0.82 delivers" used the promise metaphor and an old version. Re-probed on 0.0.84 (the gap is still there) and reworded to "`ty` 0.0.84 enforces less than the declaration states". `Bad` appeared in the prose without being introduced; it is now "a subclass `Bad` that writes `sides = "four"`". The issue is cited by its title, "Enforce the Liskov Substitution Principle for non-methods".
- "One library does read it at runtime: `@dataclass`...": `dataclasses` is one of several readers, so the sentence now says only that `@dataclass` reads it.
- "Python has no syntax for declaring a per-object field in the class body" contradicted the later section title "A Bare Annotation Declares". Now "No syntax in a Python class body allocates a per-object field."
- "so no checker catches this read" named two checkers; now "neither checker".

Chapter, teaching:

- `type(self)` section: added the `@classmethod` form of the same fork (`cls.total += 1`), linked to chapter 07's "Static and Class Methods". The section's last sentence mentions `cls`, and nothing before it said why `cls` matters. Probed: `1 3`, the same as the listing.
- The section's opening sentence quoted the analogy and said it "cuts both ways". It now ties the fork to `counter_near_miss.py`, the instance form of the same mistake.
- Exercises 9 and 10 added, with solutions. "A Bare Annotation Declares" asserts that a missing assignment passes the checker and fails at the first read, with no listing and no exercise; exercise 9 has the reader produce it. "`type(self)` Forks the Counter" had no exercise; exercise 10 watches `vars(Sub)` gain its own `total`. Both are appended, so exercises 1-8 keep their numbers.
- Exercise 4 asked the reader to "have an instance assign to `self.total` directly" while the solution assigns `a.total = 99` from outside. The exercise now asks for what the solution does.

Chapter, prose:

- "Leave the value off and the class stores nothing" (imperative plus consequence) is "Without a value the class stores nothing".
- "`display_object(a)` tells a different story" is "Once an instance exists, `display_object(a)` reports both names".
- Trailing ", and nothing more" cut from the `__annotations__` sentence; the sentence before it says the class stores nothing.
- Emphasis italics removed from "*and*" and "*mutable*".

Solutions:

- Exercise 8's closing paragraph called a base-class registry a list "nobody meant to share", while chapter 37's `Trash.registry` shares one on purpose and this chapter cites it. The paragraph now separates the two intents.
- Exercise 4: "Declare ... instead, and the type checker flags" (imperative plus consequence) reworded, and its reason corrected: the checker rejects a write to a `ClassVar` through an instance, not a shadow it "can see".
- Exercise 1: inline comments aligned with extra spaces, now two spaces. Exercise 4: the comment's "NOT" in capitals lowered.
- "exactly like" and "precisely the bug" trimmed.

## Considered and declined

- **`@dataclass` three chapters before it is taught.** "Real Per-Object Defaults" needs it to answer the question the chapter raises, every use links to chapter 12, and the listings use only the default-value form.
- **Hand-written `__init__()` in `Tally` and `A`.** Standing exemption, and `A` is the contrast with `B`.
- **Cutting the version-pinned `ty` gap paragraph.** It is current, not history, so the "do not narrate tool-version history" rule does not reach it. It joins the pinned claims the `tool-upgrade` skill re-probes; when issue 2158 closes, delete the paragraph.
- **"Which Dictionary?" and the two exceptions.** Slots and `@property` both break "assignment through an instance writes the instance dictionary". Each exception is stated where the rule is introduced, and repeating them in a four-sentence conclusion would bury its point.
- **A listing for the slots paragraph.** The paragraph is an aside that sends the reader to chapter 18, which has the listings.
