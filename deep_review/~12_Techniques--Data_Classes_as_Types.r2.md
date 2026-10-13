> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 12_Techniques--Data_Classes_as_Types (2026-10-13)

No live blocks: every finding had one sensible answer, so all of them are applied below.
I read the chapter and its Solutions file against the 2026-09-29 review (`~12_...md`) and `deep_review_db.md`,
and checked each claim against its listing.
Probes ran on Python 3.15.0, `ty` 0.0.86, and Pyright (`uv run pyright`).
Every checker claim still holds:
`ty` infers `Unknown` for `field(default_factory=set)` and `field(default_factory=dict)`,
reports `invalid-assignment` for a `dict[int, int]` factory against `dict[str, str]`,
`invalid-named-tuple` for `__new__()` in a `NamedTuple` body,
`invalid-frozen-dataclass-subclass` for both mixed hierarchies,
and `built` as read-only for `self.built += 1` (Solutions exercise 6).
Pyright infers `set[Unknown]`, rejects it, and accepts the `NamedTuple` `__new__()`.
The quoted runtime messages match the interpreter
(`non-default argument 'b' follows default argument 'a'`, the `mutable default` `ValueError`,
`Object of type Person is not JSON serializable`, `replace() should be called on dataclass instances`),
and a `NamedTuple` body rejects `__init__()` with the same `Cannot overwrite` error as `__new__()`.
The Borg link (chapter 24's `Borg.__init__()` replaces `self.__dict__`) and the
`_replace()`-through-`tuple.__new__()` claim behind exercise 3 check out.
`tip verify-ch CH=12 ISOLATED=1` passed 27 of 27 before and after.

## Applied directly

Chapter:

- `stars_class.py` prose: "That check runs after the mutation, not instead of it" said the wrong contrast (instead of / before). Now "so it reports the damage instead of preventing it."
- `display_messenger_class.py` prose: one paragraph explained the generated methods, why `__hash__` is `None`, and why `depth` alone appears as an attribute. Split into three paragraphs, one per concept.
- `display_messenger.py` prose: "The default `display_object()` omits ..." left the reader to guess what "default" meant. Now "Called without a list of dunders, `display_object()` leaves out every dunder, including ...", matching its `dunder=()` parameter.
- `A` section: "does not override ... so every one of them is `object`'s generic version" stated positively: `A` inherits them from `object`.
- `D` section: the reason `x` carries no tag came after the observation. Now the generated `__init__()` assigns `x` to each instance, so `show(D())` finds it in the instance `__dict__`.
- "A Type Is a Set of Values": "The only way to make a `Stars` is through the constructor" contradicted the chapter's own `copy()`/`deepcopy()`/`pickle` section, the same overclaim the last review fixed in "Where the Checks Go". Now "Your code makes a `Stars` by calling the constructor", with a parenthetical link to `#copy-skips-the-constructor`.
- "Defaults Built Fresh": "produces a type loose enough that `ty` accepts it" now names the mechanism, re-probed on 0.0.86: `ty` infers `Unknown` for the `field()` call. Matches Solutions exercise 7.
- `NamedTuple` section: "replacement has no such back door" was a figure. Now `copy.replace()` is one of the constructions, because it builds the copy through the constructor.
- "Where the Checks Go": "re-validates the whole object on every change, even when only one field moved" now says what runs: every check in `__post_init__()`, including the checks on fields it copied unchanged.

Solutions:

- Exercise 1: "A test for divisibility by 4 alone" read as a `pytest` test. Now "An `is_leap()` that tests divisibility by 4 alone".
- Exercise 1: "rejects the same day ... 29 at most, even in a leap year" now names February 29 and says why February 30 fails in every year.
- Exercise 3: "The chapter's factory function cannot stop that call" sat between two claims about the subclass and read as a contradiction. Now it contrasts `make_stars()`, which checks only its own callers, with a subclass `__new__()` that runs on every call.

## Considered and declined

- "`test_stars.py` demonstrates that illegal values cannot exist. The test file confirms that:" reads redundantly, but the previous review declined the overstatement, and the list that follows carries the content.
- An exercise for "Normalizing a Frozen Field" or "Frozen and Plain Data Classes Do Not Mix": both sections are short and their listings already show the failure; an exercise would restate them.
- `stars_class.py`'s comment between `@property` and `def number`: existing comments stay.

## For the session

- `tip prose CH=12` reports four stale watch-words baseline entries, all from sentences this review rewrote ("even when only one field moved" twice, "The only way to make a CODE is through the constructor", Solutions "even in a leap year"). No new hits. Prune the baseline at your discretion.
