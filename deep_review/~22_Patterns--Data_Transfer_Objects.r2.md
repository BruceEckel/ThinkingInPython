> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 22_Patterns--Data_Transfer_Objects (2026-10-13)

Second review of this chapter, after `~22_Patterns--Data_Transfer_Objects.md`.
That review's one live block ("record" means two things) is in the chapter,
and nothing it applied or declined is re-raised here.
`deep_review_db.md` still binds the "Which Should You Use?" heading
and the `Any` thread to chapter 33; both hold, and the `m: Any` paragraph keeps its meaning.

Every claim in the chapter and its Solutions file was checked
against the listings, the linked sections of chapters 12, 18, and 19,
`ty` 0.0.86 probes, and runtime probes on Python 3.15.0 (uv's managed build).
The probes confirmed: four `unresolved-attribute` errors without `m: Any`
(the write and three reads), the write that `__getattr__()` alone leaves rejected,
a clean check with the `__getattr__()`/`__setattr__()` pair,
`SimpleNamespace`'s `__getattribute__() -> Any` and `__setattr__()` declarations,
`invalid-assignment` on `red.r = 9` and on `toast.steps = ...`,
the bare-`*` syntax error, `Color` and `Dimensions` sharing a `dict` key,
both `json.dumps()` results, the data class unpacking `TypeError`,
and every `ty` claim in Solutions exercise 5
(`index-out-of-bounds`, the `float`-to-`int` argument, `int.upper`,
a `Stats` parameter rejecting a tuple in either order).
Each extracted listing, run directly, matches its `#:` markers.
`uv run tip verify-ch CH=22 ISOLATED=1` passes 27 of 27 before and after.
No live blocks.

## Applied directly

Chapter:

- "A Hand-Rolled Messenger": "its output shows that the attributes and the keyword arguments are one dict" claimed the printed dict shows identity, which output cannot show. Now `vars(m)` returns the same `__dict__`, "so its output lists every attribute `m` holds".
- Same section: without `m: Any` the type checker "rejects both `m.more = 11` and `m.info`". `ty` reports the write and all three reads. Now "rejects the write `m.more = 11` and every read, such as `m.info`".
- Same section: "instead of repeating it at every use site" misplaced the repetition, since the annotation goes on each variable. Now "instead of annotating every variable that holds a `Messenger`".
- `SimpleNamespace` section: "Its type declaration says so. Reading any attribute yields `Any`" was two sentences for one fact, and "says so" pointed back at a sentence about knowledge. Merged into "Its type declaration gives every attribute read the type `Any`".
- `NamedTuple` section: the assignment refusal was stated twice ("Assigning to a field raises ..." then "A `NamedTuple` rejects this one, at runtime and in the checker"), and "Because no field can change, `_replace()` is the way to change one" contradicted itself. Now one statement of the two rejections, and `_replace()` "builds an updated copy with one field replaced".
- "Which Should You Use?" (teaching): the frozen-data-class choice now includes "when the type must check its own values", with `__post_init__()` linked to chapter 12's "A Type Is a Set of Values" and the contrast linked to chapter 12's "A `NamedTuple` Cannot Validate Itself". Validation is a deciding difference between the two immutable records, and chapter 12 states it; this chapter's comparison left it out. The trailing "To make a `@dataclass` guarantee ..." pointer to the same chapter-12 section moved into this sentence.

Solutions:

- Exercise 3 hint linked "A `NamedTuple` Is Still a Tuple", which mentions hashing in one sentence. The hashing and the list-field leak are in the `NamedTuple` section; the hint now links it without giving the answer.
- Exercise 5: "Position is something the type checker can verify and a reader cannot" contradicted the paragraph above it, which says the checker cannot catch a swap. Now "A position tells the type checker an element's type and tells a reader nothing. A name tells both of them what the element is."
- Exercise 7, grid coordinate: "which rules out the mutable `@dataclass`" had no clear antecedent. Now says a mutable `@dataclass` sets `__hash__` to `None` (verified).
- Exercise 7, JSON record: the answer is now a frozen data class, matching the chapter's new validation clause, with why freezing keeps the check final and why a `NamedTuple` cannot hold the check (linked to chapter 12). The scenario turns on validation, and the solution had not ruled out the `NamedTuple` on that ground.

## Considered and declined

- **Exercise 3 asks the reader to explain a result the chapter states two sections earlier** (a `NamedTuple` holding a list is unhashable). It works as a check that the reader can reproduce the fact, and the solution adds the one-declaration fix.
- **Chapter 12's `messenger.py` is a data class named `Messenger`**, and this chapter introduces a hand-rolled `Messenger` with no mention of it. The two never meet in a listing, and naming the earlier class here would add a distraction to the chapter's first section.
- **"`Any` switches the type checker off for `m`"** is a figure, but it says what happens in words a reader takes literally, and the next paragraph gives the mechanism.

## For the session

- The edited sentences in "Which Should You Use?" and Solutions exercise 7 link chapter 12; `tip grounding-triage` was not run (it needs a model verdict and is outside this review's scope). Both links were read against their targets: `#a-type-is-a-set-of-values` holds the `__post_init__()` check, and `#namedtuple-cannot-validate` holds the factory-function limit.
- No NEW `exercise_refs`, `quoted_diagnostics`, stranded, watch-word, or positional hits remain. `tip prose` reports one stale `internal-names` baseline entry, `Examples/15_Techniques--Context_Managers/banner_cm.py::banner.title`, unrelated to this chapter.
