> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over `Solutions/08_Foundations--Static_Types/README.md`
(2026-10-16 sweep). The file carries few AI-writing tells: no Tier 1A
vocabulary, no curly quotes, no spaced ` -- `, no metadiscourse frames.
Most of what fired was the global rule on an "and" joining two clauses
with different subjects, each fixed directly. This file holds no live
block; it is the applied-directly record.

## Applied directly

- Line 190, restatement: the paragraph opens "`last()` mirrors
  `first()`", so the closing ", as with `first()`" repeats it; cut.
- Line 517, "and" with a subject change (consequence): "so it has no
  `append()`, and the diagnostic is `unresolved-attribute`" -> two
  sentences, "... no `append()`. The diagnostic is therefore
  `unresolved-attribute` ...".
- Line 522, "and" with a subject change (contrast): "A writable
  container is invariant, and a read-only type is covariant" -> two
  sentences. Rewrapped the paragraph.
- Line 579, "and" with a subject change (consequence): "`if text:`
  tests whether the value is missing or empty, and the function returns
  `"(nothing)"` for both" -> two sentences.
- Line 587, "and" with a subject change: "is the same trap as [...],
  and the same answer applies. Test for the condition you mean." -> "is
  the same trap as [...]. The same answer applies: test for the
  condition you mean." Link text and target unchanged.
- Line 662, "and" with a subject change (reason): "`val` is a second
  name for the string `"hi"`, and `reset()` rebinds `b.val`" -> two
  sentences.
- Line 713, "and" with a subject change (contrast): "On a list, `Final`
  forbids rebinding the name, and any code holding a reference ... can
  still change its contents" -> two sentences.

## Considered and declined

- The bold step labels ("**Keep the subclass type through the
  chain.**", "**Widen the set at its definition.**", and the rest) are
  the Solutions files' step-label convention, not §15 boldface overuse.
- Line 48 and lines 80-83 both say `Triangle` qualifies by having the
  `draw() -> str` that `Drawable` declares. The first comes before the
  listing as the reason for the method's name; the second, after it,
  ties `Triangle` to `Circle` and `Square`. Kept both.
- Line 127, "The diagnostic marks the mistake the chapter describes."
  §70 by shape, but it ties the quoted diagnostic to the chapter's
  claim and leads into the reason. Kept.
- Line 411, "a `Literal` constrains nothing at run time": a negative
  that is the claim. Kept.
- Line 716, "`Final` stops a rebinding, and the tuple type has no
  method that changes its contents": two parallel reasons, so the "and"
  is additive. Kept.
- The heading "What a missing type parameter default costs" (exercise 5)
  uses "costs" as a figure (rule R2), but headings are out of scope for
  this pass; noted for the session.
