> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 37_Patterns--Pattern_Refactoring (2026-09-25)

This review follows the six prose passes (elements-of-style, literal, positive, straighten, cohesion, antecedents), each committed separately on `claude/prep-37`.
The prose pass of this review ran without the global `~/.claude/CLAUDE.md` watch list, which does not exist in cloud sessions; it used the skill's own rules, `banned_phrases.py`, and the repo's CLAUDE.md.
One block needs your decision.
Probes run for this review, in `build/examples/37_*` under `ty` 0.0.82: `Trash(1.0).value = 2.0` is rejected (the record's `value` reads as a read-only property); `Aluminum(1.0).value = 2.0` is accepted; a subclass that restates `value: ClassVar[float] = 0.5` draws `invalid-attribute-access` again. Pyright rejects both subclass forms.

## Should `trash.py`'s subclasses restate `ClassVar[float]`?

"The `Trash` Hierarchy", the paragraph after `trash.py`.
The straighten pass found and fixed a claim that contradicted chapter 9: the text said the bare `value = 1.67` inherits "the name and its type", with restating described as an optional extra.
Chapter 9's "ClassVar and Inheritance" says the override loses the type checker's guard, and the probes above confirm it for `trash.py`.
The paragraph now says so plainly, with the `ty` behavior spelled out.
That leaves the chapter's own listing openly skipping the practice chapter 9 recommends, with no reason given.

Two fixes, in different directions:

- **Restate the annotation** (`value: ClassVar[float] = 1.67`) in `trash.py`'s four subclasses, `note_methods.py`'s three, the `Plastic` class in `plastic_dropped.py` and `recycle_dict_plastic.py`, and the Solutions copies. The paragraph's last two sentences then shrink to one ("each subclass restates `ClassVar[float]`, which keeps [the check](09_...)"). The figure `trash_sorter.svg` prints `value = 1.67`, so it would be redrawn too. Every subclass line gets longer, and the listings lose their one-line-per-material look.
- **Keep the bare form and give the reason**: one sentence saying the listings leave the annotation off to keep each material one line, and that a real codebase should restate it. This costs nothing in the listings, but the book then shows a practice and recommends against it in the same paragraph.

I lean toward restating, because the listings should practice what chapter 9 teaches, but chapter 38's `symbol = "R"` overrides of `symbol: ClassVar[str]` use the same bare form, so whichever you pick should apply there too.

[] Reject

## Applied directly

Chapter, corrections:

- "`@dataclass` builds `__init__()`" (elements-of-style pass): the listing uses `@record`; now says `@record`.
- `ClassVar` override paragraph (straighten pass, checked here): now states that a bare override loses `ty`'s guard, matching chapter 9, with the two assignments `ty` rejects and accepts. See the block above.
- Opening: the literal pass turned "the spirit of Martin Fowler's *Refactoring*" into "That reshaping is Martin Fowler's *Refactoring*". *Refactoring* preserves behavior and this chapter adds requirements, so the claim was too strong. Now "follows the method of".
- *Visitor* intro: "a language that cannot add a method to a class from outside" contradicted the previous section's "You can assign a function onto a class from outside". Now "a statically typed language".
- "In Python, a single-dispatch function implements *Visitor*" is now "does *Visitor*'s job". The function replaces the pattern; it does not implement the visitor class, `accept()`, and double dispatch.
- Fallback paragraph: the positive pass's "When every material needs an answer of its own" changed the condition. Chapter 33's advice applies when the default answer would be wrong for an unregistered type. That wording is restored.
- After `disposal_hazard.py`: "each side is now one line" was false for the operations side, which the same paragraph prices at "one more file each". Now "an addition in one place".
- "This `match` runs over an open set, and Pattern Matching warns against a `match` over an open set" said the same thing twice. Now one sentence.
- Intro: "names each one at the point where the example would otherwise need it" was trimmed to "where the example would otherwise need it".

Chapter, teaching:

- `singledispatchmethod` pointer: the chapter linked only to chapter 41, which comes later, yet exercise 3 asks for a `singledispatchmethod`. Chapter 32 already uses it in "The `singledispatchmethod` Trap". The chapter now links there and names the trap (a dispatcher on a shared base serves every subclass), which exercise 3's `Sorter` is one step from.

Solutions:

- Exercise 1: "That is the only change to the Python code" contradicted the paragraph's own "Only the filename it parses has to change". Now "That class is the only new Python code."

Checked and correct: the sixty pounds of plastic (20 + 40 in `plastic.dat`); "That dispatch first appeared in the event bus in Function Objects" (no earlier chapter probes a dict with `type(...)`); chapter 33's `NotImplementedError` advice; chapter 27's `cls.registry` hazard and chapter 9's back-reference to this chapter's registry; the five incoming links (chapters 9, 21, 27, 28, 33), whose anchors are unchanged; the `trash_sorter.svg` labels against `trash.py`.

## Considered and declined

- Solutions 1 and 2 write `Trash.registry[name]` in `create()`, where the chapter's `trash.py` writes `cls.registry[name]`. Chapter 27 calls the `Trash.registry` form the safer one, and these are stand-alone solution listings, so the difference does no harm.
- Solutions 4's `CrushedAluminum` restates `value = 1.67`, which it would inherit anyway. Harmless, and it makes the class read complete next to `bin = Aluminum`.
- `plastic_dropped.py` wraps its import one name per line, where `recycle_rtti.py` packs the same import. The one-per-line form appears in about 15 listings book-wide (noted in the chapter 33 review), so this is a book-wide question.
- "The `match` is the statement that loses the plastic, not the parser: ... The `match` alone loses trash silently." The paragraph says it twice. The second sentence is the paragraph's conclusion and the one a skimming reader takes away, so it stays.
- Exercise 2's `price()` is `sum_value()` under another name. That is the point: the reader decides it needs no `singledispatch`, and the solution says so.
