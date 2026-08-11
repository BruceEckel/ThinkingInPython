When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

First readability pass over `Chapters/38_Simulation.md`, after the deep review.
The chapter is clean by this skill's measures:
no AI-vocabulary hits, no curly quotes, no spaced `--`,
varied sentence and paragraph rhythm, and specifics everywhere
(eighteen messages, two per rat; 139 cells; 1787; mode `(2, 3)`).
Three small fixes were applied directly.
No live blocks remain.

## Applied directly

- Line 52, misplaced "only" (global watch list): "It only needs an object with
  matching methods" is now "It needs only an object with matching methods".
  Same repair the deep review made on "it names concepts only `Maze` uses".
- Line 569, "has to" (watch list): "so no code that reads `room` has to check
  for `None`" is now "so no code that reads `room` needs a `None` check".
- Line 811, §53 "worth" frame: "a small idiom worth decoding" is now
  "a small idiom". The next sentences do the decoding,
  so the frame rated the explanation instead of giving it.

## Considered and declined

- "It only answers questions" (line 26), "The code only declares `room`"
  (line 561), and "the grains only read it" (line 1223) keep their "only"
  placement: each means "does no more than", so the adverb sits on the verb
  correctly, unlike the line 52 case.
- "keep acting like real strings" (line 157) and "You need no real
  `Blackboard`" (exercise 1): §34 real/actual inflation by shape, but both
  carry a named contrast (`StrEnum` vs `Enum`; the fake the exercise builds),
  which the rule's carve-out covers.
- "the occupant really is a `Teleport`" (line 819): "really" survives the
  deletion test poorly on paper, but the sentence is about a runtime proof of
  what the checker cannot assume, and the word carries that spoken emphasis.
- "genuinely a process rather than a single call" (line 652): named contrast,
  same carve-out.
- "the collapse as it happens" (line 1157): "happen" is on the watch list, but
  the phrase is literal and echoes the section heading "Watching It Happen",
  which is anchored and stays.
- "each object it meets decides what happens" (line 7): also literal; the
  return value of `interact()` is the outcome being decided.
- "The randomness is not fighting the order but producing it" (line 1127): a
  "not X but Y" contrast, not §9's "not only...but" parallelism, and it is the
  chapter's central turn.
- "This final example is different. Its result appears in no line of its code."
  (lines 966-967): two short sentences in a row, but each is informative,
  not §31 staccato drama.
- The deep review's declined items stand unchanged: the "needs no lock"
  preview, exercise 5's "need not use the teleports", and the "Rats & Mazes"
  ampersand heading.
