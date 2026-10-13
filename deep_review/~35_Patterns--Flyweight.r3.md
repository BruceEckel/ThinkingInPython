> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 35_Patterns--Flyweight (2026-10-13, third review)

This review follows `~35_Patterns--Flyweight.r2.md` (2026-09-29) and the edits since, chiefly the listing-design changes that split `tile_map_demo.py` and `tile_enum_demo.py` out of their library listings.
It found nothing that needs your decision, so the file has no live blocks.
`tip verify-ch CH=35 ISOLATED=1` passed 27 of 27 before and after the edits.
Probes, on Python 3.15.0 (uv managed) and `ty` 0.0.86: `reveal_type(tile)` is `_lru_cache_wrapper[Tile]`, and `tile("?")` and `Tile("?")` pass the checker; past `to_symbol()`'s guard `char` narrows to `Literal[".", "~", "#"]`; a `SPECS` key outside its `Literal` key type is `invalid-assignment`; `Tile.DOOR` is `unresolved-attribute`; `int(str(n)) is int(str(n))` is `True` at 1024 and -5 and `False` at 1025 and -6; a runtime `sys.intern()`ed string is mortal (refcount 2, `sys._is_immortal()` `False`); `enum.py` reads `_value_` (line 270) before it calls `__init__()` (line 273).
Solutions 35 `exercise_2.py` prints 6.1 on its first line run standalone three times and 6.2 under the gate, the process difference `CLAUDE.md` records, so the committed marker stands; with `@dataclass(frozen=True)` in place of `@record` it prints 9.8, 9.9, 11.1, which backs the solution's "near ten".
A `__new__()` pool on a `WeakValueDictionary`, on a `Color` declared `@dataclass(frozen=True, slots=True, weakref_slot=True)`, interns and empties as Solution 5 says.

## Applied directly

Chapter:

- After `tile_map_demo.py`: "The last two lines of `tile_map_demo.py` call `label()`" pointed by position; now "The two `label()` calls in `tile_map_demo.py` go to one object".
- Thread-race paragraph: "One more property carries over" read as a Python `property`; now "One more hazard", which the paragraph's "adds a second hazard" then continues.
- Weak-pool paragraph: dropped the intensifier "exactly" from "lives exactly as long as".
- Lead-in to `tile_enum_demo.py`: it said "looks up one member by name, by symbol, and by attribute, then reads a member's fields", but `value` is not a field and the listing's third line iterates. Now lists the three accesses in listing order, "reads a member's value and walkability, and iterates over the members".
- End of "A Known Set: Enum": the chapter 31 pointer shared a paragraph with the loading-at-runtime trade, a second concept, and its "the same way" had no clear referent once read alone. Split into its own paragraph, now "also uses an `Enum` as a flyweight pool, with its members serving as shared, comparable states".
- "Flyweights in the Wild": "The benefit is the same in all three: memory proportional to..." sat after a compiler example whose stated benefit is comparison speed. Now "In all three, memory grows with the number of distinct values, not with the number of uses."

Solutions:

- Solution 2: "what one cell costs" and two more "costs" (commerce words for a consequence) now "the memory one cell takes"; the unshared cell "takes a reference plus a brand-new `Tile`", which is what the measurement compares.
- Solution 5 hint: "a weak reference needs a slot for it, which `record()` does not forward" said `record()` forwards slots; now names the `__weakref__` slot and the `weakref_slot=True` option that `record()` does not forward.
- Solution 5, last paragraph: "as [Choosing ...] says, on a `Color` declared with the same `@dataclass(...)` line" attributed the decorator line to the chapter section. Split so the chapter says what it says and the solution adds that such a `Color` keeps its constructor syntax and needs the same line.
- Solution 6 hint: "never reaches the pool" now "stays out of the pool", matching the solution's own wording.
- Solution 8: "*Flyweight* raises the stakes, because its whole point is" now "For a *Flyweight* the duplicate is a bug, because the pattern exists to make `tile("^") is tile("^")` hold."

## Considered and declined

- "A Pool That Does Not Leak" is a negative heading. Solution 5's hint links its anchor, and "A Pool That Shrinks" says less (the pool also guarantees sharing while objects live). Left.
- Line 466, "a slotted class gets one only by declaring it": the restriction is the claim. Left.
- `int("256")` paragraph after `interned_color.py` restates the previous sentence in its second sentence. Short and harmless. Left.

## For the session

- `tip prose CH=35` now reports five stale `watch_words` baseline entries for this chapter and its Solutions file (`exactly` in the weak-pool paragraph; three `costs` and one `never` in the Solutions file). The sentences were rewritten, so the entries can be pruned; I did not touch the baseline.
- `tip prose` also reports a stale `internal_names` entry in another chapter, `Examples/15_Techniques--Context_Managers/banner_cm.py::banner.title`, not from this review.
