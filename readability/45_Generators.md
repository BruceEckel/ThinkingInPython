> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/45_Generators.md`

Second review of this chapter.
The findings in `readability/~45_Generators.md` were all accepted and applied,
and none were rejected, so nothing is carried forward. The earlier review's
theme was interpretive metadiscourse; that pattern is gone from the prose it
flagged, and the findings this time were different in kind.

The deep review that ran just before this one added `manual_forwarding.py`,
moved the threading paragraph to the end of "A Generator Is a Description",
rewrote the sentence that opens the chapter's central argument, added a
laziness sentence to "Running to Exhaustion" and a `throw()`/`close()` sentence
to "Composing Is Not Interpreting", and reshaped `drive()` so it looks its
answer up once. That last change rewrote ten `#:` marker lines across three
listings.

Every finding cleared the direct-application bar, so this run leaves no
blocks: the fixes are listed for the record, and the `git diff` is the place
to veto any of them.

## Applied directly

- "A Generator Is a Description" opening: "because you can be its driver" →
  "because the driver can be yours," with the new line "A coroutine's
  requests are addressed to the event loop; a generator's are addressed to
  whatever code calls `send()`." (the old sentence read as though a
  coroutine cannot be driven, which the chapter's own conclusion
  contradicts: `asyncio.run()` is a driver. The difference is who writes
  the driver, not whether one exists).
- `manual_forwarding.py` follow-up: reordered to lead with the mechanism.
  It now opens "Each `send()` delivers its value to `manual()`'s own
  `yield`, which throws it away," keeps the checker point as "because
  `manual()` is a valid `Generator[str, int]`: the send channel is declared
  and simply never used," and ends on "`yield from` is not shorthand for
  this loop." (three of the five old sentences carried the same claim at
  different altitudes).
- `throw()`/`close()` sentence: now introduces the methods as it names them:
  "A driver can also `throw()` an exception into a generator or `close()`
  it, and `yield from` relays both: a thrown exception surfaces inside the
  innermost generator rather than at the delegating one, and a `close()`
  unwinds every frame in the chain." (a reader met `throw()` for the first
  time in a subordinate clause; the deep review's rejection of a full
  subsection stands).
- "Running to Exhaustion": the colon in ""Exhausted" describes where the
  delegation ends, not when it happens:" became a period (what followed was
  a second independent claim, not a definition, list, or quote, and it is
  the claim the reader holds through the next three sections).

## Checked and clean

- Zero hits across the §7 Tier 1A, 1B, 2, and 3 vocabulary tables in the new
  prose.
- `banned_phrases.py` and `prose_lint.py` both pass on the chapter.
- No em dashes, no spaced ` -- `, no curly quotes, no boldface, no emojis, no
  slot-fill placeholders.
- The threading paragraph reads better at the end of its section than it did in
  the middle, and its move left no dangling reference: the sentence before it
  ("The generator declares Effects, the driver interprets them") ends the
  argument cleanly, and the paragraph opens with its own subject rather than a
  connective.
- The ten rewritten `#:` markers were checked against the reshaped `drive()`.
  All three listings now print `answer = ` and the chapter quotes none of those
  strings in prose, so nothing else needed updating.
- Exercise 2's new clause ("`StopIteration` now means two different things in
  the same loop; keep them apart") uses a semicolon between two tightly linked
  independent clauses, which the style rules allow. It is also an instruction to
  the reader, so the imperative is correct rather than the banned
  imperative-plus-consequence shape.
- `manual_forwarding.py` duplicates `collect()` rather than importing it. The
  deep review explains why (importing `yield_from_send.py` would print its
  module-level demo into this listing's output), and the duplication is six
  lines. Worth knowing it is deliberate if a later pass flags it as drift.
