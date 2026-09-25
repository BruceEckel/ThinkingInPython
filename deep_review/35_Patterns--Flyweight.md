> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 35_Patterns--Flyweight (2026-09-25)

This review follows the five prose passes (literal, positive, straighten, cohesion, antecedents), each committed separately on `claude/prep-35`.
This run found nothing that needs your decision, so the file has no live blocks.
Everything had one sensible fix and is listed below.
Probes run for this review, on the pinned 3.15.0rc2: `int(str(n)) is int(str(n))` is `True` through 1024 and `False` at 1025 and at -6, so "This build caches up to 1024" holds; `low, low2 = 100000, 100000` gives `low is low2` as `True` (constant pooling); a `sys.intern()`ed runtime string has refcount 3, not an immortal count, so interned strings still die with their last reference and "the same design as `sys.intern()`" holds; `@dataclass(init=False)` with the default `eq=True` sets `__hash__` to `None`.

## Applied directly

Chapter, corrections:

- "Freezing the Shared Tile", first sentence: the straighten pass turned "Freezing `Tile` is what lets clients share it" into "Freezing `Tile` lets clients share it". Clients share the tile whether or not it is frozen; freezing makes the sharing safe, as the chapter's opening says. Now "Freezing `Tile` is what makes sharing it safe."
- Small-integer paragraph: "(That pooling is also why Python warns about `is` on a literal.)" gave the pooling as the warning's cause. The `SyntaxWarning` exists because `is` on a literal gives an implementation-dependent answer, of which the pooling is one source. Now says that, and names the warning.
- After `interned_color.py`: "CPython's small-integer cache works the same way" (straighten pass, from a parenthetical) now says in what way: `int("256")` is an ordinary constructor call that returns a cached object. The cache is filled eagerly, unlike `Color`'s pool, so the unqualified "same way" overclaimed.
- `@dataclass(init=False)` paragraph: "each consequence pulls in another" (positive pass) was vague, and the paragraph never said why a `None` hash matters. Now "each fix forces the next", with the cost stated: a `Color` could no longer be a dict key or set member.
- "Flyweights in the Wild": "Pandas" is "pandas", the library's own spelling.

Chapter, wording:

- "The bookkeeping is by hand, and `__new__()` adds a rule of its own" (literal pass) now "You write the bookkeeping yourself, and `__new__()` brings a rule of its own."
- "A `@dataclass` would generate an `__init__()`, and the re-run with it" (positive pass) was missing its verb; now "and bring the re-run back with it."

Fixes the prose passes made while checking claims, recorded so a later review does not re-raise them: `Tile`'s `@dataclass` became `@record` (literal); the `ty` quote paragraph now says the function returns `None` implicitly for `Tile.ROCK`, since the diagnostic names no case (straighten); "It checks membership" now names `to_symbol()` rather than reading as `tile()` (antecedents); the chapter 31 link says that machine builds on its own `Enum`, not on this chapter's tile set (antecedents).

## Considered and declined

- The coupling-panel caption (also in `tools/coupling_panels.py`, `CAPTIONS[35]` and the panel's `alt`) still matches `tile_map.py`: `parse_map()` names `tile()`, `to_symbol()`, and `Tile` (its return annotation), and inside the listing only `tile()` constructs a `Tile`. `test_tile_map.py` constructs one directly, but that test exists to show the bypass, and the caption describes the pattern's listing. No change.
- `interned_color.py` hand-writes what a dataclass would generate, and `weak_pool.py`'s `Name` keeps `@dataclass(frozen=True)` instead of `@record`. Both carry their reasons in the prose (`__init__()` re-runs; a slotted class has no `__weakref__`), and `Name` is in `record_exceptions.txt`.
- "Which Pool Should You Use?" keeps its question form (standing exemption in `deep_review_db.md`).
- The chapter never contrasts `@cache` applied to the class itself (`Tile = cache(Tile)`), which a reader might try as a shortcut. It would work for construction but replace the class name with a function, breaking `isinstance()` and annotations. Judged too far from the chapter's line to earn a paragraph; the factory and `__new__()` forms already cover both call syntaxes.
