> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 22_Patterns--Data_Transfer_Objects (2026-09-29)

Part of the book-wide sweep of chapters 01 to 29, run in its own worktree.
No earlier `~22` review exists.
`deep_review_db.md` binds two things here, and both hold:
the "Which Should You Use?" heading keeps its question form,
and the `Any` thread to chapter 33 is untouched.

Every claim was checked against the listings, the linked sections
(chapters 03, 05, 08, 12, 18, 19, 20, 26), a `ty` 0.0.84 probe,
and a runtime probe on the pinned interpreter.
All of the chapter's technical claims hold:
the two `unresolved-attribute` errors without `m: Any`,
the write that `__getattr__()` alone does not cover,
`SimpleNamespace`'s `__getattribute__()`/`__setattr__()` pair,
`ty`'s report on `red.r = 9`, the bare-`*` syntax error,
the JSON array, and both `TypeError`s.
`uv run tip verify-ch CH=22` passes 24 of 24.

## Applied directly

Chapter, corrections:

- Intro, second paragraph: "[Parallelism] pickles arguments and return values ... the same way" gave the reader nothing for "the same way" to point at, and made a section the thing that pickles. Now the objects "have the same shape, whether or not they leave the process", and a process pool does the pickling, with the link in parentheses.
- "A Hand-Rolled Messenger": "The standard library's stub for `SimpleNamespace`" used "stub" in the typing sense, which the book defines nowhere before Appendix B. Chapter 11 defines a stub as a test stand-in. Now "type declaration", the phrase the next section uses.
- `NamedTuple` section: "a declared field rejects this one" credited the rejection to the declaration, but the `Point` listing above it has declared fields and accepts `p.x = 3.5`. Immutability is the cause. Now "a `NamedTuple` rejects this one".
- Same section: `copy.replace()` "does the same job for any immutable record" overstated. It works on types that define `__replace__()`, as chapter 12 says. Now names the `NamedTuple`, the frozen data class, and that condition.
- "Which Should You Use?": "Between the two typed records" followed a sentence naming `@dataclass` and `NamedTuple`, then compared `NamedTuple` with the frozen data class, which the section had not yet named. Now "The frozen data class is the second typed immutable record. Between it and a `NamedTuple`, ...".
- Exercise 5 said "Every caller still runs." That stays true of the old listing only; see the `fetch_stats.py` change below. Now "repair the one line that stops working".

Chapter, teaching:

- `fetch_stats.py` never read a field by name, so the pattern's main benefit showed only in the repr. Added `print(result.mean, result.count)`.
- After that listing: the near-miss. Unpacking goes by position, so `count, mean = summarize(data)` runs, passes the type checker, and swaps the values. Solutions exercise 5 made this point; the chapter did not.
- `@dataclass` section had a listing and no prose after it. Added why `p.x = 3.5` succeeds, and a pointer to where the frozen form is compared, naming `@record` with a link to chapter 18. Before this the chapter never mentioned `@record`, which every listing from chapter 18 on uses.
- "A NamedTuple Is Still a Tuple": added why `still_a_tuple.py` writes `@dataclass(frozen=True)` in full (so `order=True` is the one difference between the twins), and the hashing consequence of type-blind equality (`Color(1, 2, 3)` and `Dimensions(1, 2, 3)` are the same `dict` key, verified).
- "Which Should You Use?": the frozen data class choice says "which this book writes as `@record`".

Chapter, prose:

- "Convert first, ... and the output is ..." was imperative plus consequence. Now a gerund subject.
- "that happens to have the same shape" is "with the same shape".
- `*become*` lost its emphasis italics.
- "dataclass" as a prose noun is "data class" in three places, the book's dominant form (68 uses against 12).
- "DTO" is introduced in parentheses before "Fowler's DTO" uses it.
- "Messenger" as a pattern name is italic at its two later mentions, matching the first.

Solutions:

- Exercise 4 did not do what the exercise asks. The exercise adds the fourth attribute to `display_namespace.py`, where `m.more = 11` is an assignment, so the constructor version yields `info, tags, note, more` and the assignment version `info, tags, more, note`. The solution had moved `more` into both constructors and reported "Even the order matches". The listing now follows the exercise, and the prose explains why the dicts are equal and the orders differ. `TAGS` is `Final[list[str]]`. Retitled "A fourth attribute, by keyword and by assignment".
- Exercise 5 follows the changed `fetch_stats.py`: the listing repairs `result.mean` to `result[0]`, and the first paragraph says which lines still run.
- Exercise 5: "A function annotated `Stats` also rejects a reversed `tuple[int, float]`" implied the order caused the rejection. `ty` rejects a bare tuple in either order. Now says so.
- Exercise 7, JSON scenario: the exercise asks why the other types do not fit, and the solution skipped `TypedDict`, the type "Which Should You Use?" offers for JSON. Added: it names the keys but runs no code, so it cannot validate.
- Exercise 7 prose: removed "exactly the looseness", "in the first place", "already", and two filler uses of "plain".
- Exercise 6: "never pretends to be one" is "no tuple compares equal to one". "dataclass" is "data class" throughout.

## "Record" means two things after chapter 18

Chapter 18 defines the term: "a *record* is an immutable class defined by its fields",
and from there the book's listings write `@record`.
Chapter 22 uses "record" as the generic noun chapters 03 and 12 use:
"produces a mutable record", "a typed mutable record", "a different record type".
"A mutable record" contradicts chapter 18's definition four chapters after the reader met it.

I left the generic noun alone, since it is the book's word from chapter 03 on
and only you can say which sense wins.
If `@record`'s sense wins, the change in this chapter is small:
"produces a mutable record" becomes "and its fields stay assignable",
"a `@dataclass` for a typed mutable record, and a `NamedTuple` for a typed immutable one"
becomes "a `@dataclass` for typed fields you reassign, and a `NamedTuple` for typed fields you cannot",
and the `NamedTuple` uses stay, since a `NamedTuple` is an immutable class defined by its fields.
I recommend making that change.

`[] Reject`

## Considered and declined

- **A frozen-data-class subsection under "The Standard-Library Versions".** Chapters 12 and 18 teach the frozen form; a pointer from the `@dataclass` section costs three lines, and a fourth subsection would repeat chapter 12.
- **The `# Unpacks like a tuple` comment in `fetch_stats.py`.** The prose says the same thing, but an existing comment stays unless you ask.
- **"Immutability also makes the record hashable."** A tuple is hashable because `tuple` defines `__hash__()`, not because it is immutable. The next paragraph qualifies the claim with the list-holding record, and the loose version is what a reader needs at that point.
- **Adding "Messenger" to `tools/data/pattern_names.txt`.** Chapters 12 and 17 have classes named `Messenger` in code font, which the check skips, so it would probably pass. It is a tools change outside this chapter's review.
- **Exercises for the JSON and ordering paragraphs.** Seven exercises cover every section; these two paragraphs are consequences of the equality point that exercise 6 tests.
- **`match` patterns over a `NamedTuple` and a data class.** Both support positional patterns, and chapter 13 owns that topic.
