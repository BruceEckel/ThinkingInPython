When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Readability pass over `Chapters/18_Performance.md`, run after the deep review
and the NumPy-section conversion in the same sweep.
The chapter came through the deep review clean of AI-vocabulary tells:
no Tier 1 words, no curly quotes, no spaced `--`, no banned phrases,
and the restrictive `only`/`already`/`anyway` uses all earn their place.
The NumPy section's new prose was treated as settled content per the sweep
instructions.
Everything found was either applied directly or declined;
no finding needs a decision.

## Applied directly

- Line 51, watch list (stranded preposition):
  "third-party packages you rely on." is now "you need."
  ("on which you rely" was the alternative; it read stiff.)
- Line 129, watch list ("hooks"):
  "the interpreter's own hook mechanism" is now
  "the interpreter's own instrumentation mechanism",
  which also echoes "the instrumentation slows the program"
  from the cProfile paragraph above it.
- Line 189, watch list ("hooks"):
  "quietly fighting over the same hooks" is now
  "over the same callbacks", the thing `register_callback()` registers.
- Line 237, stranded preposition:
  "when you know which function you care about" is now
  "when you know which function matters".
- Line 744, watch list ("buy"):
  "Fitting the whole data set in memory buys more than a second pass"
  is now "gives you more than a second pass".
- Line 1364, stranded preposition:
  "it changes which curve your program is on" is now
  "which curve your program follows".

## Considered and declined

- "A profiler tells you for sure, preventing wasted time." A tacked-on
  participle by shape (§3), but it carries the real consequence of the
  bad-at-guessing claim before it, and it is first-edition voice.
  Cutting it loses the cost claim; expanding it pads a tight paragraph.
- "and the gap widens as `n` grows" appears verbatim twice (heap-vs-hash
  and caching). A mild template repeat, but the two uses sit five pages
  apart, each is the right clause in its spot, and varying one would be
  change for its own sake.
- "Registering nothing costs nothing" (sys.monitoring intro): chiasmus
  by shape, but the colon after it explains the mechanism concretely,
  and the compression is the point.
- "The goal is not the fastest possible program. It is a program that
  is fast enough, at the lowest cost in clarity." Negative parallelism
  by shape (§9), but the contrast is the chapter's closing argument,
  stated once, with both halves concrete.
- The two near-identical Numba parentheticals ("The comment above shows
  one machine's actual output. Expect a different, but still large,
  multiple on yours."): deliberate parallel boilerplate for the same
  not-run-by-the-build situation, and "actual" draws a real contrast
  with the book's generated `#:` output elsewhere.
- Per the deep review's declined list, left alone: the cleft in
  "The counts, not a stopwatch, are what this listing measures"
  (deleting "are what" breaks the sentence), and every
  timing-threshold sentence.
