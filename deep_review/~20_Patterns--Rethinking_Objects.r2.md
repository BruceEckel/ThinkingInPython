> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 20_Patterns--Rethinking_Objects (2026-10-13)

Nothing here needs your decision, so the file has no live blocks.
I ran every extracted listing directly and compared it with its `#:` markers (all matched),
and re-probed each type-checker claim in the chapter and its Solutions against `ty` 0.0.86:
the read-write protocol form rejecting both `Point` and `PairCoord`,
`immutable.bob.name = "Ralph"` rejected on a frozen `Bob`,
`t: object` failing on `display()`,
the `NewType` diagnostic quoted in `newtype_boundary.py`,
the unguarded `logger.log()` on `ListLogger | None`,
both `stringify()` overloads,
and, for the Solutions, exercise 3's `invalid-return-type`, exercise 5's implicit-`None` report without `case _`,
and exercise 8's `invalid-method-override` for a `bool`-returning `push()`.
At runtime I confirmed `ABC.__slots__ == ()`, `frozendict` (named in Solutions 2) on 3.15,
and the cross-chapter claims about the empty `__slots__` bases in chapters 29 and 34 and the shared `EDGE` room in chapter 38.
`tip verify-ch CH=20 ISOLATED=1` passed 27 of 27 before and 27 of 27 after; `tip prose CH=20` shows no new hits.

## Applied directly

Chapter:

- "The Liskov Substitution Principle": "pin down" appeared three times in two lines. The tests now "check" and "confirm".
- "Encapsulation Leaks": "The getter returns no view or snapshot of the list, but a reference to the list" now leads with what the getter returns, then the contrast.
- "The Immutability Solution": "Hashing goes the same way" named no actor. Now "The same list field breaks hashing."
- "Methods or Functions?": "It can live outside `Point`" stated the advantage without the reason. Added "so it can serve any type that has an `x` and a `y`", which also sets up the next section.
- "Protocols": the nominal/structural paragraph ended its case for protocols, then gave their drawback (no grep for implementers), then praised them again. "Protocols connect pieces..." now closes the case, and the drawback is its own paragraph, opened by "The same independence hides membership."
- "What the Shape Does Not Say": "the `# type: ignore` silences the type checker's diagnostic, which lets the rejected call run" was wrong; Python runs the call whatever the checker says. Now the sentence says the call runs and prints `user-42`, like `lookup(UserId(42))`. The `Data Classes as Types` alternative that followed is its own paragraph.
- `shapes_oo.py`, `protocols_typed.py`, `protocol_collision.py`, `shapes_match.py`, `balance_object.py`: dropped the `if __name__ == "__main__":` guard. No listing imports them, and the guard now marks exactly the five listings another listing or test imports (`plugged.py`, `immutable.py`, `dynamic_typing.py`, `newtype_boundary.py`, `optional_logger.py`). This extends the applied listing-design card `c20-point_distance-q4-r4` ("drop the guard in listings no other code imports") to the single-print listings its reach left out. Markers unchanged.

Solutions:

- Exercise 1: both listings stored `_numbers` and `_bob` with no property to read them, a class that matched neither `leaky.py` nor the exercise ("add a `tags` field to `Leaky`"). Each listing is now the chapter's class plus `tags`; `exercise_1b.py` imports `deepcopy` for `bob`, and the prose says `deepcopy()` still guards it.
- Exercise 2 hint: "explains what `frozen=True` generates" described nothing the section contains. Now it points at `frozen=True` on a class with a `list` field.
- Exercise 6: the exercise asks for `NullLogger`'s shape, and the prose described a function defaulting to a shared `NullCache` that the listing did not show. Added `NO_CACHE: Final[NullCache]` and `render()`, which takes `cache: Cache = NO_CACHE` and tests the `None` from `get()`, so the listing shows both halves of the prose: no `None` check on the cache, a `None` check on the miss.
- Exercise 7 hint: "`CountingList` missing calls that `list` makes in its own implementation" now says what happens, `list.extend()` adding items without calling the overridden `append()`. Dropped an "entirely" in the solution prose.

## Considered and declined

- "If you avoid implementation inheritance, the payoff for using types is tremendous." "payoff" sits beside the commerce family (R2) and the banned "pays off", but the sentence states a benefit, not a mechanism's consequence, and reads as the talk's voice. Left as written.
- A `c is twin` line in `composition.py` to contrast identity with the value equality the listing shows. The prose already says `twin` is a separate object built from equal parts, and the listing-design pass just reshaped this demo.
- Converting `dynamic_typing.py` and the other imported listings to library-plus-demo pairs so every marker hugs its `print()`. Their markers sit after one loop or one call each, so nothing is misplaced, and the split would add five files.
- Everything in the 2026-09-29 review's declined list still holds, and the standing rulings (the four "promise" section themes, hand-written `__init__()` in `leaky.py` and `plugged.py`, long-form `@dataclass(frozen=True)` in `immutable.py` and `frozen_leaky.py`) were left alone.

## For the session

- Nothing cross-chapter needs fixing.
- `tip prose CH=20` reports one stale `internal_names` baseline entry, `Examples/15_Techniques--Context_Managers/banner_cm.py::banner.title`. It belongs to chapter 15, not this one; it appeared while another agent's chapter 15 edits were in the working tree.
- `verify-ch` rewrote the generated `Examples/20_Patterns--Rethinking_Objects/{shapes_oo,protocols_typed,protocol_collision,shapes_match,balance_object}.py` and `Solutions/20_Patterns--Rethinking_Objects/exercise_{1a,1b,6}.py` from the Markdown, as its sync step does.
