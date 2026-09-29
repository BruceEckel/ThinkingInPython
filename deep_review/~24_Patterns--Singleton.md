> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 24_Patterns--Singleton (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I checked each claim against its listing, the sections the chapter links (5, 6, 11, 12, 14, 17, 18, 19, 20, 21, 26), runtime probes on the pinned 3.15, `ty` 0.0.84, Pyright 1.1.414, mypy (through `uv tool run`), the GoF *Singleton* chapter, and Martelli's "Five Easy Pieces".
`tip verify-ch CH=24`, `tip verify`, and `tip exercise-refs` pass.

Claims probed and found correct as written:
`inspect.get_annotations()` raises a `NameError` on the nested-class factory and `ty` reports `unresolved-reference`;
the cached race builds eight objects in five of five trials, and none without the sleep in twenty;
a lock inside the cached body still builds eight and takes 0.40 s against 0.05 s;
`OnlyOne.__OnlyOne` raises an `AttributeError` at runtime and passes `ty`, Pyright, and mypy;
a dataclass `Borg` subclass keeps separate `__dict__`s, and the `__post_init__()` variant loses its fields;
`class Sub(Registry)` fails under `ty` and Pyright and passes under mypy.

## Applied directly

Chapter, corrections:

- "The Classic Implementations": "To address languages like C++ and Java" was wrong for a 1994 book whose examples are in C++ and Smalltalk (chapter 21 says so). Now "writes its examples in C++ and Smalltalk".
- Same paragraph: "The rest reach it by other means" had no antecedent for "it", and the order did not match the sections. Now one clause per form, in section order.
- Borg paragraph: "The nested class above is a `@dataclass`" pointed two sections back at `__OnlyOne`. Now "`Singleton` writes its `__init__()` by hand, and it cannot be a `@dataclass`."
- Borg paragraph: `__init__`, `super().__init__`, and `__post_init__` gained their parentheses, and the `__post_init__()` failure now names its symptom (`AttributeError` on `val`, probed).
- "`isinstance(first, Registry)` and `class Sub(Registry)` both raise:" now "both raise a `TypeError`".
- "`@cache` disappears below, because it no longer makes the object single" misdescribed the reason; `@cache` never did under threads. Now: the check must sit inside the lock, `@cache` keeps its check out of reach, so the listing writes the check by hand.
- "The name `Registry` now refers to the decorated instance" now "a `singleton` object that holds the class".
- "That is the singleton: not a rule the class enforces": no class exists at that point. Now "a class".
- Heading "Borg: Singleton By Inheritance" now "by". The slug is unchanged, so chapters 12 and 39 still link to it.
- *Borg* is italic on every mention, as the catalog writes it (three plain mentions fixed).

Chapter, teaching:

- "When You Want a Class": one paragraph of motivation before the mechanism (fields and methods that belong together, or a type other code must name).
- Cached-factory trap: a default does not protect the cache. `settings()`, `settings("prod")`, and `settings(env="prod")` build three objects (probed).
- "Nothing Keeps the Class Private": the mangling sentences now say what the double underscore does at module level and why it is a trap inside a class body. "This listing keeps the bare name for a reason that outlasts the convention" became a literal statement.
- "The First-Call Race": says why the listing prints `> 1` while the prose says eight.
- `global` paragraph: links chapter 05's "Names Inside a Function", which teaches the rule.
- "Double-Checked Locking": new listing `singleton_double_checked.py`, since chapter 39's catalog sends readers to this section for the pattern and the section showed no code. "Both checks must be exactly right, and a subtle mistake reintroduces the race" is replaced by the two details that matter: the inner test, and assigning `_instance` last so the unlocked outer test cannot see a half-built object.
- "The Classic Implementations": says what GoF's form is (blocked constructor, `Instance()` class operation) and that `settings()` is that operation as a function.
- Borg: why `Borg.__init__()` reads `self._shared_state` (Martelli's stated reason, from the linked article).
- Class decorator: the static cost. Under `ty` and Pyright the decorated call accepts any arguments and returns `Any`; mypy still checks against the class (all three probed).
- Exercise 7 (new, last, so nothing renumbers): `__init__()` runs on the shared instance after every construction. The chapter stated this without showing it. The sentence carries "(see exercise 7)", accepted into `tools/data/exercise_refs_baseline.txt`.

Chapter, prose:

- "everyone shares anything defined at module level" restated with the module as the actor.
- "escape hatch" now "a reset".
- "`__new__()` itself" lost the "itself".

Solutions:

- Exercise 2: `release()` used `discard()`, so releasing a connection twice put it in `_available` twice and the pool could lease one connection to two callers. Now `remove()`, which raises a `KeyError`; the listing demonstrates it and the prose explains it. The unused `_all` list is gone.
- Exercise 2: "guarantees exactly one" now "yields one" (the chapter's own race section shows `@cache` guarantees nothing under threads).
- Exercise 5: "holding objects the cache has never heard of" was false, since the cache held each one until the next overwrote it. Now "objects the cache no longer holds". "The worst outcome a lock can produce" cut (a deadlock is worse).
- Exercise 5: "import time is single-threaded by guarantee rather than by hope" overstated the rule. Now: the body runs once, and a thread importing the module meanwhile waits.
- Exercises 3, 5, 6: "exactly like", "only earn ... genuinely", "honest answer", and "the sharing the pattern promises" reworded per the watch list.
- Exercise 7: new solution.

## Considered and declined

- **"Tests, Threads, and Locks" states results the next section demonstrates.** Notes 2 and 3 give the eight-object count and the lock placement before the listings that show them. Moving the notes after the listings would put the `cache_clear()` note, which needs no listing, in an odd place, and the notes read as a summary the next section then proves. Left.
- **`_shared_state` override without the `ClassVar` annotation.** House style says a subclass override does not repeat `ClassVar`. Under `ty` the bare `_shared_state = {}` reveals `dict[Unknown, Unknown]`, so the annotation keeps the type. Left annotated in the chapter and in solution 6.
- **Lowercase "singleton".** "A module is a singleton", "every lazy singleton", and the rest name the object, not the pattern, so they stay lowercase. Only the opening's "For the singleton", which names the pattern chapter 21's question is asked of, became *Singleton*.
- **`exactly once` in note 2** is a count, the use the style rule allows.
- **"hooks" for `__init_subclass__()` and `__set_name__()`** is the technical term chapter 17 uses.
- **A thread-safe pool in solution 2.** `acquire()` and `release()` take no lock. The exercise is about the factory, and a lock would add a second topic.
- **Subclassing `SingletonClassVar`.** A subclass constructed first stores a subclass instance in the base's slot. GoF treats subclassing at length; the chapter's argument is that you rarely need the class form, so the case stays out.
