> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 37_Patterns--Pattern_Refactoring, third review (2026-10-13)

This review follows `~37_Patterns--Pattern_Refactoring.r2.md` (2026-09-29) and the commits since,
mainly the listing-design round that added `report()`, renamed `t` to `piece`, and reshaped `note_methods.py`.
Probes ran under `ty` 0.0.86 and Python 3.15.0 in `build/verify-ch-37/`.
Every checker claim holds: `ty` rejects `Trash(1.0).value = 2.0` and `Aluminum(1.0).value = 2.0`,
accepts `bins: Bins = {}`, and reports `assert_never(piece)` with the remainder `Trash & ~Aluminum & ~Paper & ~Glass & ~Cardboard`.
At runtime `Aluminum.create("Paper", 1.0)` returns a `Paper`, the empty-dict version raises a `KeyError`,
`recycling_note()` returns `Aluminum`'s note for a `CrushedAluminum`, and `create()` raises a `KeyError` for an unregistered name.
The Solutions near-miss claims hold too: `max(items)` raises the quoted `TypeError` and draws `invalid-argument-type`,
`@singledispatch` on the `Sorter` methods prints "no special handling" five times with no diagnostic,
and the unconditional `cls.bin = cls` leaves three bins.
All nine chapter listings and five solutions print their markers when run directly.
`tip verify-ch CH=37 ISOLATED=1` passes 27 of 27 before and after. No live blocks.

## Applied directly

Chapter, corrections:

- "Nothing fails" paragraph: "a number that is wrong and looks right" contradicted the listing and Solutions 1, since each total `plastic_dropped.py` prints is right for its pieces.
  Now a sentence says so, and the dropped trash is "a report that looks complete and leaves out a material".
  The opening's "a requirement that makes it report wrong totals" now reads "leave trash out of its report" to match.
- After `note_methods.py`: the base's edit was justified by the type checker alone, but the base `hazard()` also supplies the "none" that `Cardboard` inherits. Both reasons are now given.
  "The operation after it edits the base and those classes again" assumed the next operation differs for the same materials; now "each material whose answer to it differs".

Chapter, teaching and structure:

- `trash_sorter.svg` moved from above `trash.py` to the end of "Let a Dictionary Do the Sorting".
  Its frames show `plastic.dat`, `Plastic`, `bins[type(piece)]`, and `parsed 4, binned 4`, none of which the reader had met at the old spot (the `figures` skill's placement rule).
  A lead-in names the path it traces, and a follow-up says the `Plastic` class is the one new code on that path.
- `report()` paragraph: added why the output starts with `Glass` (a dictionary keeps insertion order, so the first material in the data prints first). The "so each sorter ends with `report(bins)`" non-sequitur is now its own sentence.

Chapter, prose:

- "Now write the safety officer's question the same way" commanded the reader to do what the listing does, and used "question" where the chapter now says "operation". Now "The safety officer's disposal hazard becomes a second `singledispatch` function."

Solutions:

- Hints 1 and 4 said the chapter keys bins on `type(t)`; the chapter now writes `type(piece)`.
- Exercise 4: "know exactly what arrived" is "know the exact class that arrived", the term the paragraph contrasts with MRO dispatch.

## Considered and declined

- The Solutions listings keep `t` where the chapter renamed to `piece`. Each solution's prose matches its own listing, and the rename would touch every listing for no reader gain.
- "Polymorphism is one way to do that. This chapter uses a dictionary keyed by type and a `singledispatch` function." The link between the two sentences is loose, but "two more ways" would be wrong under the book's broad definition of polymorphism, which `singledispatch` meets.
- `note_methods.py`'s base `note()` says "nothing special" where `recycling_note()` says "no special handling". The base answer never prints, and the line is at 60 columns.
- Carried forward and not re-raised: the undecorated material subclasses, the "Readers of *Composite* and *Interpreter*" attribution, "cannot break it", the italic *exact*, and the `# Dollars per pound` comment.

## For the session

- `tools/data/watch_words_baseline.txt` line 972 (`Solutions/37...: exactly: The sorter must know exactly what arrived`) is now stale; this review reworded that sentence.
- Not a chapter 37 claim, but worth knowing for chapters 18 and 20: at runtime `Aluminum(1.0).value = 2.0` (an undecorated subclass of a `@record`) raises `TypeError: super(type, obj): obj (instance of Aluminum) is not an instance or subtype of type (Trash)`, not `FrozenInstanceError`.
  The frozen `__setattr__()` that `slots=True` generates closes over the pre-slots class. Any prose that says what such an assignment raises at runtime should be checked against this.
