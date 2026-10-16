> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: 35_Patterns--Flyweight (2026-10-16)

A full audit of the chapter's prose against the readability patterns, after the 2026-10-16 metadiscourse pass and continuity read (fa63c3c7).
`readability_db.md` was read first; its chapter 35 entry (the four-way decision paragraph under "Choosing a Flyweight and Its Pool") stands, and nothing here re-raises it.
The chapter is technical register with varied sentence lengths, no Tier 1A or Tier 2 vocabulary, no curly quotes, no spaced `--`, no boldface, no signposting openers, and no generic closer.
Five sentences fired a rule with one sensible answer and were fixed in place; nothing needs your decision, so the file has no live blocks and serves as the applied-directly record.
`tip verify-ch CH=35` passes 27 of 27.

## Applied directly

- Line 190, verdict fragment on output already on the page (the 2026-10-04 Sweep Decisions ruling on chapters 18 and 47): "Twenty-four cells, three objects." -> "The twenty-four cells share three `Tile` objects.", which reads the `24 3` marker instead of restating it as a beat.
- Line 194, one primary concept per paragraph: the comprehension-unpacking sentence and the `id(t)`-versus-`set` explanation shared a paragraph; the unpacking sentence now stands alone, and the counting paragraph starts at "The listing counts `id(t)`".
- Line 224, repeated connective: the second "therefore" in three sentences ("The boundary is therefore `to_symbol()`") -> "That leaves `to_symbol()` as the boundary".
- Line 351, treadmill (§70 restatement): "The construction syntax stays the same, so a caller sees an ordinary constructor call and receives a shared object. `int("256")` works the same way: an ordinary constructor call returns a shared object." said the same thing twice, and the paragraph before already says the call stays `Color(...)`. Now "A caller writes an ordinary constructor call and receives a shared object, as with `int("256")`."
- Line 354, "and" joining clauses with different subjects: "You write the bookkeeping yourself, and it must account for ..." -> two sentences, "You write the bookkeeping yourself. It must account for ...".

## Considered and declined

- "so the two are worth combining when memory matters" (§53 shape). The frame weighs combining against a stated condition, the `readability_db.md` carve-out for "worth".
- "What `tile()` gets from `@cache` is identity." A wh-cleft, but not the "is what" filler the rule targets: it sets "identity" against the caching job the two sentences before describe, and the next sentence defines it.
- "`_pool` stays a plain dict with an explicit membership test, not a `defaultdict`." "Plain" stands against the named `defaultdict`.
- "Only identity proves sharing." A sentence-initial "Only", one of the shapes ruled fine on 2026-10-04, and the restriction is the claim.
- "A first design gives each cell everything it knows about itself" keeps a reflexive "itself".
- "The enum version also brings iteration, exhaustive `match`, and a closed set of members" is a rule-of-three shape (§10) whose items the following paragraphs use (`match` in `tile_enum_match.py`, the closed set in the `ValueError`/`AttributeError` sentence).
- "A map has a handful of tile kinds and a program usually draws from a small palette" joins two subjects with "and", but the clauses are additive premises for the "so" that follows; no contrast or consequence hides in the "and".
