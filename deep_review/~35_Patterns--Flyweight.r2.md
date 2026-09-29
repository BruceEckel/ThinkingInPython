> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 35_Patterns--Flyweight (2026-09-29, second review)

This review follows `~35_Patterns--Flyweight.md` (2026-09-25) and the edits since: the blockquote opener, the slotted `Name` with `weakref_slot=True`, and the 2026-09-28 move of the `lru_cache` paragraph.
It found nothing that needs your decision, so the file has no live blocks.
The 2026-09-27 triage left no damage here: every cut lead-in in this chapter was metadiscourse, and each following sentence still has its subject.
Probes run for this review, on `ty` 0.0.84: `reveal_type(tile)` is `_lru_cache_wrapper[Tile]`, and `tile("?")` and `tile(5)` both pass the checker; `Tile.DOOR` on the enum is `unresolved-attribute`; a `match` over `Symbol` that leaves out `"#"` draws the same `invalid-return-type` as the enum's; `Tile("?")` and `Tile(5)` pass the checker; the quoted `tile_enum_match.py` diagnostic still matches. `enum.py` on 3.15 reads `_value_` before it calls `__init__()`, so the chapter's `_value_` paragraph holds.

## Applied directly

Chapter:

- "Typing the Symbol Set": `@cache` hides `tile()`'s `Symbol` parameter from callers (`_lru_cache_wrapper.__call__` accepts any hashable arguments), so the checker passes `tile("?")`. The section said `tile()` "trusts the declaration", which let a reader believe callers were checked. Now says so, and gives it as the reason the boundary is `to_symbol()`.
- Literal-pooling sentence: "with literals (`low, low2 = 256, 256`) even `100000 is 100000` prints `True`" paired a 256 example with a 100000 claim. Now "`high, high2 = 100000, 100000` makes `high is high2` print `True`".
- "Interning in the Constructor": "If you want callers to keep writing `Color(...)`" named a class the reader had not met yet. Now "construct objects with an ordinary class call such as `Color(...)`".
- Before `tile_enum_match.py`: "the type checker reports the missing case" overclaimed, since the diagnostic names no case and comes from the declared return type. Now "If you leave one out of a function that declares a return type, the type checker reports the gap before the code runs".

Solutions:

- Solution 5 never answered the exercise's "Say what the rewrite gave up". Added the answer (the constructor syntax and its guarantee: `Color(...)` now bypasses the pool) with a `bypass` line in the listing that shows it (`#: True False`), and noted that weak references did not force the trade, since `__new__()` can use a `WeakValueDictionary`, as "Which Pool Should You Use?" says. Also removed "that omission rules out `@dataclass`", which the chapter's `@dataclass(init=False)` paragraph contradicts, and gave `_pool` its `Final`.
- Solution 7 said "The type checker catches nothing new" and did not answer the exercise's first question. Now: exhaustive `match` is caught in both; the `SPECS`/`Symbol` drift cannot happen; `Tile.DOOR` is newly caught, where `tile("+")` was never checked because of `@cache`; an unknown symbol from data fails at runtime in both.
- Solution 3: "Restoring `@record` turns this same test into a demonstration of the fix" was wrong, since the test then stops with a `FrozenInstanceError`. Now says that.
- Solution 4: italics used for emphasis ("*flyweight*", "*position*"), a trailing "and nothing more", and "after captures clear the whole board" (kings are never captured). Rewritten.

## Considered and declined

- The `lru_cache` paragraph now sits between the slots paragraph and `test_weak_pool.py`, so the test follows a paragraph about a different pool. Your 2026-09-28 move put the slots paragraph next to `weak_pool.py` deliberately, and the chapter's other test listing also appears with no lead-in. Left.
- *Multiton* (italic here and in chapter 39) and *Object Pool* (chapter 39) are not in `tools/data/pattern_names.txt`, the same question as the Borg/Messenger card. Not this chapter's file to change.
