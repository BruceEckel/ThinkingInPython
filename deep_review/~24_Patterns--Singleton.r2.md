> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 24_Patterns--Singleton (2026-10-13)

No live blocks: nothing here needs your decision.
I read the chapter and its Solutions against `deep_review_db.md` and the 2026-09-29 review (`~24_Patterns--Singleton.md`), and ran every listing on the pinned 3.15 through `uv run`, with `ty` 0.0.86.
`tip verify-ch CH=24 ISOLATED=1` passed 27 of 27 before the edits and 27 of 27 after; `tip prose CH=24` shows no new stranded, watch-word, or positional hits.

I ran the extracted listings directly and checked them against their markers. The three race listings each ran three times and gave the same result every time: `True`, `1`, `1`.
Probed again on `ty` 0.0.86:
`OnlyOne.__OnlyOne` raises an `AttributeError` at runtime and passes `ty`;
the nested-class factory's annotation draws `unresolved-reference`, and `inspect.get_annotations()` raises a `NameError`;
`class Sub(Registry)` draws `invalid-base`, while `Registry(42)` and a misspelled attribute on its result pass;
the eager `ClassVar[__OnlyOne | None]` variant in solution 1 draws `unresolved-attribute` on `None`.
`@cache` under the race keeps the object from the last thread to finish (three of three), so "Only the object from the last thread to finish stays in the cache" holds.
Martelli's article confirms that `Borg.__init__()` reads `self._shared_state` with one underscore to allow the subclass override.
Chapter 17's metaclass `__call__()` matches what the chapter and solution 7 say about it.

## Applied directly

Chapter:

- "A Module Is Already a Singleton": the long mutate-versus-rebind paragraph split at "To replace the whole value". It held two concepts: why rebinding ends the sharing, and how to replace the value safely.
- "When You Want a Class": "When the shared thing has ... it is a class" became "When the shared state has ... you need a class". "Thing" was a stand-in noun, and "it is a class" made the state the class.
- Note 2: "Every lazy singleton has a first-call race" became "faces". The chapter's own locked and double-checked versions are lazy and have no race.
- "Double-Checked Locking": "The classic escape" became "The classic workaround" (figurative).
- Same section: "a bad trade for saving one lock acquisition" became "Skipping one lock acquisition per call rarely justifies two details that must both stay right" (a commerce figure).
- "Lazy Creation": "fails at runtime with `AttributeError`" became "with an `AttributeError`".
- Class decorator: the paragraph after `singleton_class.py` split before "Why does `__call__()` intercept". One paragraph covered what the name now binds; the other covers why the parentheses run `singleton.__call__()`.
- Metaclass paragraph: split before "[Metaprogramming] also covers". That sentence moves away from the metaclass-versus-`__new__()` contrast.
- "Which Should You Use?" (teaching): the class bullet now says that both the cached factory and the `__new__()` override create the instance on the first call, so under threads you build it once at import time. The old line named only the factory, and `SingletonClassVar.__new__()` has the same check-then-build race.

Solutions:

- Exercise 1: "The single-threaded import builds the object" overstated the import rule (solution 5's wording was corrected the same way last round). Now "The class body runs once, during the import, so no first call remains to race."
- Exercise 4 (teaching): the exercise says to add `import config` at the end, and the listing puts it at the top without comment. A new sentence says why (ruff) and that the position changes nothing, since whichever import comes first runs the body.
- Exercise 6: "Mutation is its design, so every version of the pattern carries the trap" contradicted the `Separate` class just above it. Now it says that every *Borg* instance writes into the shared dict by design, so any subclass that leaves `_shared_state` alone writes into `Borg`'s dict.

## Considered and declined

- **Import order in "A Module Is Already a Singleton".** The prose said the first import "runs `config.py` top to bottom and files the resulting module object in `sys.modules`", and the generated `singleton_story` figure used the same order ("config.py runs and is filed"). The import system files the module before it runs the body (`importlib._bootstrap._load_unlocked()`). Corrected on 2026-10-13: the prose now says Python creates the module object, files it in `sys.modules`, then runs the body, and the figure's first frame says "the module is filed, then config.py runs", as its `<title>` does.
- **`singleton_cached_race.py` is not in `tools/data/timing.txt`.** Its `True` is a race outcome, not a wall-clock threshold. With a 50 ms constructor it came out `True` in every run here and in the last review's. A flip would need all seven other threads delayed 50 ms. Left unregistered.
- **The figure paragraph and the mutate-versus-rebind paragraph repeat each other.** The first reads the figure's arrows and the second states the same point in code. The repetition fits a first explanation. Left.

## For the session

Nothing outside this chapter's two files.
