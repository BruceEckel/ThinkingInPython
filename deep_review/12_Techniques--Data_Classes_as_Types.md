> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 12_Techniques--Data_Classes_as_Types (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I checked each claim against its listing, the sections the chapter links
(5, 8, 9, 17, 18, 20, 22, 24, 27, 36, 40), and the committed `#:` markers.
Probes ran on `ty` 0.0.84, Pyright 1.1.414, and mypy (through `uv tool run`).
Every checker claim in the chapter holds:
`ty` accepts the bare `set` factory (it infers `Unknown` for the `field()` call)
and reports `invalid-assignment` for `dict[int, int]`;
Pyright rejects the bare `set` factory and accepts `__new__()` in a `NamedTuple` body;
`ty` reports `invalid-named-tuple` and `invalid-frozen-dataclass-subclass`.
The quoted `ValueError`, both `TypeError` messages, and `Month(7)`'s `ValueError` match the interpreter.
`tip verify-ch CH=12` passes 24 of 24.

## Applied directly

Chapter, corrections:

- "`check()` and `TypeFailure`": the fix-triage cut of "The following `check()` function appears throughout the chapter" left the section opening on "It raises `TypeFailure`", with nothing for "It" to name. Now "`check()` raises `TypeFailure` when its condition is false", and the description of `TypeFailure` is its own sentence.
- `C` section: "`@dataclass` stores nothing on the class" contradicted the sentence before it (the recorded field list lives on the class, as do the generated methods). Now "stores no value for a field on the class".
- "Defaults Built Fresh": "every `Months` reads and writes that one list" described what the rejected default would do as though it ran. Now "The rejection prevents shared storage", and the sharing is stated under "with that default".
- Same section: "any default that is not an immutable literal" excluded legal immutable defaults that are not literals (an `Enum` member, a frozen instance). Now "immutable value".
- `KW_ONLY`: "Python refuses that with `TypeError`" credited the interpreter. `@dataclass` raises that exception; Python's own complaint for the same signature is a `SyntaxError`.
- "The General Form of `replace()`": the prose listed "a `datetime`" and the listing replaces a `date`. Now "a `date` or `datetime`".
- Same section: "`copy.replace()` builds the new object through the constructor" holds for a data class and not for the `NamedTuple` in the same listing, whose `_replace()` the chapter has just said skips `__new__()`. Now "For a data class, ...".
- "Where the Checks Go": "nothing can skip them, because the constructor is the only way to make the value" contradicted the chapter's own section on `copy()`, `deepcopy()`, and `pickle`. Now "where they run once, for every value the program constructs".

Chapter, teaching:

- New subsection "The Annotation and the Check", with `stars_float.py`. The chapter says `Stars` holds "the integers one through ten", and `Stars(5.5)` builds at runtime: `@dataclass` does not enforce an annotation. The subsection says which check belongs to the type checker and which to `__post_init__()`, and that a type built from `Any` at a boundary tests the field's type as well. Alternative considered: one sentence with no listing; the printed `Stars(number=5.5)` makes the point faster.
- New exercise 8 (and its solution) on the same gap, including `Stars(True)`, which passes both `isinstance()` and `ty`.
- `validation.py` prose: one sentence says what `@dataclass` does on the exception and links "Data Classes", since the decorator appears two sections before the chapter explains it.
- "Normalizing a Frozen Field": `object.__setattr__()` also works from outside the class, so one sentence now says `frozen=True` stops an accidental assignment, not a determined caller.
- "Composing Types from Types": `Person` "declares no checks of its own" now says what does the work: its annotations, enforced by the type checker.
- "Enums Are Types Too": chapters 13 and 31 say this section introduces `Enum`, and it used the term without defining it. One sentence defines *enumeration*.
- "Parse, Don't Validate": "Here the type carries a guarantee" followed the Static Types citation with no stated connection. Now "A parameter annotated `Stars` states more than a type: the value passed the check."
- `test_birth_date.py` had no lead-in sentence; added one.
- "Inheritance and the Generated `__init__()`": the reason the base constructor is skipped sat in the section's last paragraph, after three listings. It now follows the claim in the first paragraph. The rest of that last paragraph repeated the sentence above the third listing, so the paragraph is gone.

Chapter, prose:

- Dunder methods named in prose take parentheses (`__init__()`, `__eq__()`, `__repr__()`), including the Inheritance heading, whose explicit `{#dataclass-inheritance}` anchor keeps every inbound link.
- Watch-list words: "exactly the failure", "has to stay mutable", "is what happens the one time", "is what creates ... by itself", "already names the type", "even nested", two uses of "never" where "did not" or "does not" says the same.
- "`dataclasses.replace()` has nothing to work with" ended on a preposition. Now "finds no fields to replace".
- Exercise 5: "Give `Stars` a `copy.replace()`-based variant helper" reworded to say what to build.

Solutions:

- Exercise 1: removed `from __future__ import annotations` (annotations are lazy on 3.15, and the chapter's `birth_date.py` has no such import). Added a test for `Year(2000)`, the one century year `Year` accepts, so the divisible-by-400 branch of `is_leap()` has a test.
- Exercises 1-6: removed the docstring from each copy of `TypeFailure`; the chapter's `validation.py` has none.
- Exercise 3: "it has only one construction path" contradicted the chapter's `copy()`/`pickle` section. Now "its replacement goes through the constructor".
- Exercise 7: "`dict` is a class whose call returns `dict[Unknown, Unknown]`, loose enough to satisfy any `dict` annotation" gave the wrong mechanism. `ty` infers `Unknown` for the `field()` call, which is why the chapter's `set` factory passes against a `dict` annotation. The mypy claim in the same paragraph checks out (mypy reports `arg-type` for a mismatched bare factory).
- Exercises 3, 4, 6: "at all", two uses of "itself", "ever".

## Considered and declined

- Moving "`check()` and `TypeFailure`" below "A Value to Check Everywhere", for motivation before mechanism: `stars_unchecked.py` imports `check()`, so the helper must come first, and the section is short.
- Moving "Comparing Ordinary Classes and Data Classes" out of the path between the problem (`stars_class.py`) and its solution (`stars.py`): the previous review weighed the same move and declined, and the section has since been placed here on purpose.
- Restoring a lead-in for the `A`/`B`/`C`/`D` list and for `replace_vs_copy.py`: both sentences were cut on the fix-triage page, and the text reads without them.
- `copy_replace_protocol.py` types `Channel` as a `Literal` where house style prefers an `Enum`: the names are the keyword arguments `__replace__()` receives, so strings are the right type, and the Literal sweep chose this form.
- The three-line comment in `test_stars.py` and "# A set" in `factory_checking.py`: existing comments stay.
- "Testing demonstrates that illegal values cannot exist" overstates what four sample values show; the next sentence says what the tests confirm.
- An exercise for the Inheritance section: declined by the previous review for the same reason (it would restate `dataclass_super_init.py`).
