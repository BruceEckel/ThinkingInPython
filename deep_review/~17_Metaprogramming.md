[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/17_Metaprogramming.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers
validate, `ty` and ruff are clean on `build/examples/17_Metaprogramming`,
all 7 tests pass, and every one of the 22 scripts runs. The chapter's
checker and runtime claims were re-verified with probes on the pinned
toolchain: `ty` rejects `super().__call__(...)` inside
`Singleton.__call__[T]` with `invalid-super-argument` ("`type[T]` is not
an instance or subclass of `Singleton`"), matching the prose's reason
for `type.__call__(cls, ...)`, and `reveal_type(ASingleton())` is
`ASingleton`, matching the `[T]` claim; a `__prepare__` without
`@classmethod` fails with `TypeError: Strict.__prepare__() missing 1
required positional argument: 'bases'`, matching "leave `bases`
unfilled, producing a `TypeError` that says nothing about the real
mistake"; and an inline-lambda variant of `eager_event_classes.py`
really does stamp every generated class with the last name in `NAMES`
(probe printed `A(action='C', ...)`), backing the late-binding paragraph
added below. The standing exemptions in `deep_review_db.md` (sentinel
unions naming values, `_redefined()`'s `INTERESTING_DUNDERS` allowlist)
were honored and are not flagged. One cross-reference error was found
and fixed (see the applied list: the `[CV]` paragraph implied two
chapter-12 files were chapter-9 files). No findings met the bar for a
live block.

## Applied directly

- "Sorting Members into Attributes and Methods": the `[CV]` paragraph
  cited `classvar_dataclass.py` and `class_with_defaults.py` with no
  chapter attribution while its only nearby link pointed at
  [Class Attributes](../Chapters/09_Class_Attributes.md), so both read
  as chapter-9 files; they live in chapter 12. Added the
  [Comparing Ordinary Classes and Data Classes] link before the first
  and "from that same comparison" on the second. Verified against the
  current chapter-12 listings: `show(D)` tags both `D.x` and `D.s`,
  `show(B())` tags both `B.x` and `B.s`, and
  `display_object(Messenger(...))` tags none.
- "Generating Classes with `type`": added a paragraph explaining why
  `make()` exists (each `init()` closes over its own `name`; an inline
  lambda would close over the comprehension's variable and every class
  would record `RingBell`), with a forward link to
  [Function Objects]'s `late_binding.py`. The factory's shape silently
  dodged the book's best-known closure trap, and a reader generating
  classes in a loop would plausibly inline the closure. Probe confirmed
  the failure mode on the pinned interpreter.
- Moved the `Event.__init__(self, ...)`-instead-of-`super()`
  explanation (the missing `__class__` cell) from the `greenhouse.py`
  prose up to `eager_event_classes.py`, where the idiom first appears
  and the question first arises; `greenhouse.py` repeats the same
  shape, and `commander.py`'s later contrast with `greenhouse.py`
  still reads correctly.
- Intro roadmap: added "The `inspect` module closes the chapter from
  the other side, reading class structure instead of changing it"; the
  roadmap sentence ended at metaclasses and never announced the
  chapter's second half.
- "Making a Class Final": "The check happens at class-creation time"
  is now "runs" (watch-list "happen").
- Singleton `super()` paragraph: dropped "exactly" and tightened
  "before it will accept" to "before it accepts".
- `__prepare__` prose: "sees the second `on_open` land on a name" is
  now "assigned to a name" (banned "lands", and every `def` becomes a
  `__setitem__()` call, so "assigned" is the literal statement);
  `hook_order.py` prose: "both land between" is now "both run
  between".
- "Choosing Which Dunders to Show": "naming each sentinel value itself"
  drops "itself" (flourish; the contrast with the generic class
  carries the sentence).
- CRTP footnote: "until something actually calls them" drops
  "actually".
- Ran `make reflow CH=17` over the edited prose; `make verify` is
  green.

## Considered and declined

- The word "hook" (avoid-if-possible tier) appears throughout,
  including the "Which Hook for Which Job" heading. Here it is the
  literal technical term for `__init_subclass__()`, `__set_name__()`,
  and `__prepare__()`, not a metaphor; nothing else says it, and the
  Python docs use the same word. Left everywhere.
- "to show what a `class` statement actually does" keeps "actually":
  the sentence draws a real contrast with "a class definition is
  shorthand", and dropping the word weakens the claim the section then
  demonstrates.
- Repointing `commander.py`'s "That is the difference from
  `greenhouse.py`" at `eager_event_classes.py` now that the
  `__class__`-cell explanation lives there: declined; `greenhouse.py`
  is the nearest preceding listing with the nested-`init` shape and
  the sentence is self-contained.
- Opening "Learning a Name with `__set_name__()`" with the motivation
  instead of the descriptor primer: the primer is a prerequisite for
  `Field`, it pays off a debt [Decorators] explicitly deferred, and
  `function_is_descriptor.py` is the smallest listing in the section,
  so the escalation is already right.
- Merging the two one-sentence paragraphs after `my_list.py`: they
  make unrelated points (inherited methods; class-of-class is the
  metaclass) and the second sets up the metaclass sections, so the
  separation is doing work.
