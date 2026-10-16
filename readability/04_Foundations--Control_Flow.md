> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over chapter 04, 2026-10-16.
The chapter had few AI-writing tells, so this file holds no live block.
It records the seven edits applied directly, mostly an "and" joining two claims, one past-tense slip, and one italic used for emphasis.
`tip verify-ch CH=04` passes.

## Applied directly

- 230, present tense for standing behavior: "whichever way the search went" -> "goes".
- 340, one concept per paragraph: the comprehension forward-definition after the walrus-in-`while` material now has a paragraph of its own.
- 344, "and" joining two subjects: "A comprehension can use `:=` the same way, and [Comprehensions] covers that use" -> two sentences.
- 383, "and" joining two subjects: "One of the two `2`s survives, and no exception reports the skip" -> two sentences.
- 492, "and" standing for "so": "The optional `finally` always runs, and that makes it the place for cleanup" -> "Because the optional `finally` always runs, it is the place for cleanup."
- 664, avoid-tier "even": "even if the body raises an exception" -> "whether or not the body raises an exception"; same sentence group, "and that cleanup runs every time the block exits" -> "which runs every time the block exits."
- 698, "and" joining a consequence: "so `f` stays bound after the block exits and the listing can print `f.closed`" -> "Because a `with` block shares the enclosing scope, `f` stays bound after the block exits, so the listing can print `f.closed`."
- 773 (exercise 7), italics for emphasis: "from a *different* exception object it constructs" -> "from a new exception object it constructs, rather than from the caught `ValueError`." The Solutions quote regenerates from this.

## Considered and declined

- 129, "so `6` through `9` never print": the "never" is the claim.
- 347, "the classic control-flow bug": orients the reader to a known trap, same call as 28's "best-known closure trap".
- 331, "gives `n` the result of the comparison, `True`, and not the length": half of a real contrast.
- 492 and the `finally_swallows.py` listing, "swallows": the listing's own name and the standard term.
- 520, "the `KeyboardInterrupt` you press": naming the key would add a fact the chapter does not state.
- 661-667, three statements that `with` cleans up on exit (pair, every exit, always closes the file): each adds a step from the general guarantee to the file case, so no cut.
- 261, "`enumerate()` yields ... and the loop here unpacks each pair": two steps of one action, additive "and".
- 13, the chapter-roadmap sentence: conventional orientation in an opening paragraph, not §70 metadiscourse.
