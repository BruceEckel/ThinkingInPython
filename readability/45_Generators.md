When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first readability pass over `Chapters/45_Generators.md` in the
clean-slate sweep, run after the deep review in
`deep_review/~45_Generators.md` was applied.
That review already cleared the usual mechanical layer
(a "happen" fix, a dropped "simply", two clefts, two stranded prepositions),
and its declined blocks settle the "at the cost of saying nothing about the
other two channels" phrasing, so none of that is re-raised here.
The full pattern scan found the chapter clean:
no Tier 1A vocabulary, no colon reveals staged for drama
(both colons at "a coroutine: a description of work" and
"holds its frame: the position in the body" introduce definitions),
no metadiscourse, no rule-of-three padding
(the "no dictionary, no `input()` call, and no network connection" list is
three concrete absences), and varied sentence rhythm throughout
("One generator, one driver." and "The mechanism is this one." are single
deliberate fragments, not staccato runs).
One direct fix; no live blocks.

## Applied directly

- "Running to Exhaustion": watch word "happen" plus a vague pronoun;
  `"Exhausted" describes where the delegation ends, not when it happens.`
  is now `..., not when.`
  The next sentence carries the timing detail,
  so the elision loses nothing.

## Considered and declined

- **"not a sequence but a conversation"** (chapter opening).
  §9 by shape, but the contrast is real and it introduces the chapter's
  central metaphor; the two halves are weighed, not mirrored for rhythm.
- **"would hand the generator object itself to the driver as one value"**
  ("Running to Exhaustion"). "itself" is on the watch list,
  but here it draws the object-versus-its-values contrast the sentence
  exists to make; without it the emphasis falls on "as one value" alone.
- **"`Question("name")` produces the plain `str`"**
  ("Annotating a Generator"). "plain" draws a real contrast:
  the `NewType` distinction lives in the checker,
  and at runtime the wrapper is gone.
- **"knows nothing about where it originated", twice in one paragraph**
  ("All Three Channels"). Deliberate parallel repetition:
  the request and the answer are symmetrically ignorant,
  and the repeated clause is the symmetry.
  Not synonym cycling, and varying it would blunt the point.
- **"A `for` loop never sees that value" and "`drive()` never learns that
  `ask()` exists".** "never" is on the avoid-if-possible list,
  but both claims are unconditional facts about the mechanism,
  and a softer "does not" would understate them.
