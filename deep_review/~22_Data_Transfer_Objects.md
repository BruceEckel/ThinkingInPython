[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/22_Data_Transfer_Objects.md`
in the clean-slate sweep. The mechanical layer is sound: the `#:`
markers validate, `ty` and ruff are clean on
`build/examples/22_Data_Transfer_Objects`, and all six scripts run.
Runtime probes confirmed every behavioral claim: `Messenger("Spam")`
raises a `TypeError`; `def __init__(self, *, **kwargs)` is a
`SyntaxError` ("named parameters must follow bare *");
`dataclasses.astuple()` deep-copies (the probe's list field came back
as a different object); `json.dumps()` writes `[1, 2, 3]` for a
`NamedTuple` and raises a `TypeError` for a data class;
`copy.replace()` works on both a `NamedTuple` and a frozen data
class; a list-holding `NamedTuple` mutates through the field and is
unhashable while an all-`int` one hashes; `<` between two different
frozen `order=True` types raises a `TypeError`; sorting `Color`s is
lexicographic; unpacking a data class raises a `TypeError`; and
`vars()` on a `SimpleNamespace` reports the same order whether an
attribute arrives by constructor or by assignment. `ty` probes
confirmed the static claims: with no declarations both the read and
the write are `unresolved-attribute`, declaring only `__getattr__()`
leaves the write rejected, `SimpleNamespace` accepts the write and
reveals `Any` on the read, and assigning to a `NamedTuple` field is
`invalid-assignment`. One probe overturned prose instead of
confirming it: typeshed's `SimpleNamespace` stub declares
`__getattribute__()` and `__setattr__()`, not the `__getattr__()` the
sentence pointed back at (applied below). The load-bearing-`Any`
thread (22 → 33) is a standing exemption in `deep_review_db.md` and
was left untouched at both ends.

## Applied directly

- `Any` discussion: "The standard library's stub for
  `SimpleNamespace` declares both" now reads "declares such a pair
  (its read half is `__getattribute__()`, which intercepts every
  attribute access)". The stub has no `__getattr__()`, so "both" was
  factually off; the parenthetical states the actual method without
  teaching it (the full contrast belongs to Surrogate, chapter 26).
- NamedTuple section: added "Immutability also makes the record
  hashable, so a `Color` can key a `dict` or join a `set`" at the end
  of the `_replace()`/`copy.replace()` paragraph. The next paragraph's
  "Nor can you hash such a record" presupposed hashability without
  the chapter having said it, and exercise 3's dict-key question
  leans on it.
- Same section: "not the objects they refer to" is now "not the
  objects they name" (sentence ended on a stranded preposition).
- Serialization paragraph: "A data class is not serializable at all:
  `json.dumps()` on one raises a `TypeError`" is now "`json.dumps()`
  on a data class raises a `TypeError` instead" ("at all" was
  filler, and "instead" carries the contrast with the array output).
- Closing section: "When it only has to *become* a dict" is now
  "When it need only *become* a dict".
- Ran `make reflow CH=22`; no further changes.

## Considered and declined

- Linking the `__getattribute__()` parenthetical forward to
  Surrogate's `__getattr__`-vs-`__getattribute__` contrast: the
  chapter's intro should stay light, and chapter 33's anchor-free
  link into this same intro is a standing exemption, so the passage
  is better left unelaborated.
- Mentioning hashability in "Which Should You Use?": both typed
  records hash (`frozen=True` generates `__hash__()`), so it does not
  separate the two; the new sentence in the NamedTuple section
  covers the capability where it is taught.
- The "Which Should You Use?" heading: matches the question headings
  in chapters 24, 27, 31, and 35.
- The chapter mixes "data class" and "dataclass" in prose; both
  forms appear throughout the book, so this is not a chapter-22
  inconsistency to fix locally.
- The italic in "*become* a dict": contrastive with "must stay a
  dict" two sentences earlier, not simple emphasis; kept.
