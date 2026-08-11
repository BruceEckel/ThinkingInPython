When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the readability pass over `Chapters/23_Iterators.md`, run after
the chapter's deep review. The prose is clean: no Tier 1A/1B vocabulary,
no curly quotes, no spaced ` -- `, no copula avoidance, no rule-of-three
padding, no colon reveals staged for drama, and sentence rhythm varies
(clipped beats like "`seen` is how." against long clause chains). The
watch-list hits a mechanical sweep finds are almost all literal or
settled: every "never" describes a call that does not return (or is
hedged with "almost"), and the deep review's declined list covers the
"ever" in the termination sentence and the "never" in "The fix is
almost never a `try`". One direct fix; no live blocks.

## Applied directly

- Line 47, global watch list (don't-use tier, "near-miss"): "The
  near-miss is `next(nums)`" is now "The tempting call is
  `next(nums)`". The sentence was added by the deep review, so it is
  recent editorial prose, not first-edition voice. Close alternative
  considered: "The mistake to avoid is `next(nums)`".

## Considered and declined

- "as if the outer generator had written the loop itself" (Delegating
  with `yield from`): "itself" is on the watch list, but here the
  reflexive carries the sentence's one contrast, delegation versus
  writing the loop as your own, which the next paragraph develops
  (`flatten_loop()` "does it by hand"). Kept.
- "so the tripwire fires and no list ever comes back" (Reusable
  Algorithms): "ever" survives the deletion test poorly but states the
  unbounded claim; without it the clause can read as describing only
  this run, when the point is that `list()` would ask forever. Kept.
- "The protocol costs you nothing, and tells you nothing." (closing
  section): parallel negation by shape (§9), but it is the section's
  thesis, echoes the heading, and ends the argument on its sharpest
  sentence. Deliberate closer, kept.
- "The chapter has now reached that conclusion three times: here, in
  `tee`'s buffering, and in the advice to collect into a list...":
  metadiscourse by shape (§70), but it ties the chapter's recurring
  buffering-cost argument into one thread rather than glossing a point
  already clear. Kept.
- "`seen` is how." (The Pattern That Disappeared): a clipped fragment,
  but a single emphatic one, which the skill's false-positive list
  protects; the surrounding sentences are long. Kept.
- "a plain function" / "the plain-function form" (The Costs of
  Laziness): "plain" draws the real contrast with a generator
  function, whose body does not run at the call. Kept.
- The two "surprise"/"surprising" echoes and the repeated "fresh
  generator for every pass" are deliberate refrains that carry the
  laziness thread across sections, not synonym cycling or treadmill
  restatement. Left alone.
