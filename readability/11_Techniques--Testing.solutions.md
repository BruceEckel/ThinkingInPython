> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Solutions/11_Techniques--Testing/README.md

The Solutions file for Testing reads as human-written technical prose, with no
cluster of AI tells: no Tier 1A vocabulary, no signposting, no staccato runs,
no generic closers. Three sentences had a fault with one sensible fix, and
those are applied below. This file holds no live block, so it is the
applied-directly record. The float claims in exercise 2 were checked by
running both expressions under `uv run python`: the four listed rates give
identical results, and `0.1` gives `110.0` against `110.00000000000001`.

## Applied directly

- Line 147, split an "and" hiding a consequence: "the two sides are
  bit-identical and `==` passes just as well" -> "bit-identical, so `==`
  passes just as well".
- Line 422, portability test (a vague noun where the passage has the
  specific one): "Here the lesson applies to a different kind of
  dependency." -> "Here the dependency is a function."
- Line 517, misattribution: "The chapter's `create_autospec()` builds a
  mock ..." -> "`create_autospec()`, which the chapter introduces, builds a
  mock ...". `create_autospec()` belongs to `unittest.mock`, as the chapter
  says; the chapter introduces it.

## Considered and declined

- The bold step labels ("**Pin the order with a test.**", "**Record the
  calls by hand.**") match §16's inline-header shape. They are the
  Solutions files' convention for walking a solution step by step, so
  they stay.
- Line 318, "the one place a patching test is worth writing": "worth"
  weighs a real effort against a stated condition (recurring keep).
- Line 311, "although the fixture alone touches the disk": a compact
  concession, but the next sentence gives the reason the test takes
  `tmp_path` anyway, so the pair reads clearly as it is.
- Line 335, "a plain function returning an `io.BytesIO`": "plain"
  contrasts with the `Mock` and the patched module, and echoes the
  exercise's own wording.
- Line 428, "An injected test depends only on the shape of what it
  passes": the `only` carries the contrast with the patched test's two
  dependencies (name and module).
- Lines 510-511, "A stub that records its calls is a mock written by
  hand.": aphorism by shape (§32), but it states the definition the
  next sentence builds on.
- Line 514, "the type checker checks it": a repeated root, mild enough to
  leave.
