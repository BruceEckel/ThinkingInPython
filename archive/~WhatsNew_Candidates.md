# "What's New" Candidates for the Book

A pass through the CPython "What's New" pages from 3.15 back to 3.0,
filtered against what `Chapters/` already covers.
Each entry says what the feature is, where it would go, and how it would earn its place.

This document lists only recommendations.
Features that are out of scope (tooling, platform support, niche stdlib corners)
and features the book already covers adequately have been removed,
so an empty-looking release means that release had nothing worth acting on,
not that it went unread.
An entry survives when it carries an action, including "verify this" and "update this."

3.15 is a different kind of section from the rest.
It is the book's pinned target (`requires-python = ">=3.15"`),
so its features are the baseline rather than a compatibility question.
It is also still in development, so its "What's New" page will grow before release.

Verdicts:

- **Add** means a real gap in material the book already claims to teach.
- **Consider** means it would improve a chapter but nothing is currently wrong.
- **Mention** means one sentence or a footnote, not a section or a listing.

Coverage claims come from grepping `Chapters/`.
On 2026-09-29 every entry was rechecked against the book:
the 30 it now covers were removed,
and each partly covered entry says what is still missing.
A "not covered" note means the term appears nowhere in the book's prose or listings.
Later that day Bruce decided the nine remaining **Add** entries:
seven went into the book, and two were declined and removed.
The declined ones are module `__getattr__()` for deprecation with `__dir__()`
(chapter 6 teaches the hook once),
and `singledispatchmethod()` "dispatching on the second argument" in 3.15,
which did not reproduce on 3.15.0rc2.

---

## Top picks


---

## Python 3.15

The book's target version, so everything here is available to every listing without qualification.
`frozendict`, lazy imports, comprehension unpacking, `sentinel`, and the `profiling` package
are all in use in the book already and are not repeated below.

One task rather than a candidate:
**3.15 removes a batch of long-deprecated APIs** across `ast`, `collections.abc`, `ctypes`,
`datetime`, `glob`, `http.server`, `importlib.resources`, `pathlib`, `platform`,
`sysconfig`, `threading`, `types`, `typing`, and `zipimport`,
and `importlib.metadata` now raises `MetadataNotFound` where it used to be quieter.
The gates run on 3.15, so anything the book uses would already fail,
but prose that names a removed function would not.
Worth one grep pass over `Chapters/` against the removal list before release.

## Python 3.14

The release with the most that the book has no equivalent for.

## Python 3.13

## Python 3.12

## Python 3.11

## Python 3.10

## Python 3.9

## Python 3.8

## Python 3.7

## Python 3.6

## Python 3.5

## Python 3.4

## Python 3.3

## Python 3.2

## Python 3.1

## Python 3.0

Almost everything here is simply Python now, and the Python 2 comparison would only date the text.
Its three historical-framing items went to chapters 3, 8, and 17.

---

## Worked through, 2026-10-17

Every entry was decided: the nine Add entries on 2026-09-29, and the
rest on the Loose Ends page of 2026-10-17 (50 added, 8 declined) and in
chat the same day (the last five added). The "How Python Got Here"
appendix this file once suggested was declined: the version-history
sentences stay in the chapters that use the features. Each addition's
commit names the chapter and the feature.
