# Readability review: 05_Functions

> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

The chapter reads human throughout: sentence lengths vary,
paragraphs carry one point each, and no Tier 1A vocabulary,
curly quotes, spaced ` -- `, or structural tells appear.
Every finding had one sensible answer,
so everything went into the applied-directly list
and nothing below needs a verdict.

## Applied directly

- Line 111, watch-list "anyway": "the last call names it anyway"
  became "the last call still names it."
- Line 293, imperative-plus-consequence: "Drop the `global` from
  `writes_global()` and `count += 1` reads..." became the condition form
  "If you drop the `global` from `writes_global()`, `count += 1` reads...".
- Line 376, watch-list "never": "by position, never by name" became
  "by position, not by name"; the "must" already carries the absoluteness.
- Line 512 (exercise 8), raise-needs-object form: "raises
  `UnboundLocalError`" became "raises an `UnboundLocalError`,"
  matching the article the same sentence pattern uses at line 295.

## Considered and declined

- **"Nothing checks the arguments on the way in." (line 87).**
  §9 tailing-negation by shape, but it is a full sentence with subject
  and verb, not a tacked fragment, and it lands the section's point.
  "The way in" is adverbial, not a stranded preposition, and the banned
  phrase is "the way out," a different idiom. Kept.
- **"a local that was never assigned" (line 294).** Watch-list "never,"
  but the claim is that no assignment to the local occurs at any point,
  which "not yet assigned" would misstate. Kept.
- **"even for the same name" (line 256).** Watch-list "even," carrying
  the real surprise: two `sentinel()` calls with identical arguments
  still differ. The surrounding claim is a standing deep-review
  exemption. Kept.
- **"a real name for tracebacks" (line 479).** §34 real-inflation by
  shape, but the contrast is concrete: `def` puts the function's name in
  a traceback where a lambda shows only `<lambda>`. Kept.
- **"positional-only" / "keyword-only" in predicate position** (lines
  424, 426). §26 would drop predicate hyphens, but these are terms of
  art the section defines and the headings use; unhyphenating some
  occurrences would split one term into two forms. Kept.
