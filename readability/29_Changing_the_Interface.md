> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/29_Changing_the_Interface.md`

Run right after the deep-review edits landed, so the split `adapter.py` /
`adapter_variations.py` prose, the rewritten `ProxyAdapter` naming aside, the
new `WhatIWant` sentence, the deprecation version clause, and the new exercise 4
get the same scan as the older prose.
No completed readability review exists for this chapter, so nothing is carried
forward.

The chapter reads as human prose, and the Façade epigraph plus "A façade is an
agreement about which names to call, not a lock on the rest" are the strongest
lines in it.
No §7 vocabulary hits, no curly quotes, no spaced ` -- `, no boldface or bullet
inflation, no formulaic conclusion.

Every finding was resolved directly: applied (listed below) or declined
with the reason recorded. No blocks remain.

## Applied directly

- Line 56: "`WhatIUse` wants an `f()`" → "`WhatIUse` calls `f()`" (watched
  "want" applied to a class; "calls" is also more precise, since the
  requirement exists because `op()` makes the call).
- Lines 112-117: "Four different structures produce one behavior" →
  "Counting the object adapter above, four structures produce one behavior"
  (the count now spans two listings; the reader is looking at three).
- Line 197: dropped the flourish "itself" from "defines those dunders itself."
- Line 201: "which is what `copy.copy()` and `pickle` do" → "which
  `copy.copy()` and `pickle` do" (cleft; the deletion test passes).
  Chapter 26's matching sentence got the same fix, so the two stay parallel:
  "which `copy.copy()` and `pickle` do when they rebuild one."
- Line 230: "That is what *Façade* accomplishes." → "That is *Façade*."
  (cleft; keeps the sentence that connects the epigraph to the pattern's
  name rather than deleting it).
- Line 334: "the Adapter is what a Proxy becomes once you stop insisting" →
  "a Proxy becomes an Adapter once you stop insisting" (cleft delaying the
  verb).
- Line 127: cut "One detail in the second listing needs a closer look."
  (§29 warm-up: it announced the explanation instead of starting it, and
  the paragraph is the only place the `/` is discussed, so it provided no
  orientation. It replaced "repay attention" at your request; the request
  was to lose that phrase, which the cut still honors.)

Line numbers above refer to the chapter before these edits.

***

## Noted, no change

**Line 10 — "a later section sorts the four apart."**
The chapter's opening used to say the chapter "ends by" sorting the four apart,
which was wrong once "Retiring the Old Interface" became the closing section.
The deep-review pass corrected it to "a later section," and the accrued note in
`deep-review/SKILL.md` was corrected to match.
Recorded so a later pass does not restore the tidier-sounding but false version.
