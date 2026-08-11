When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/45_Generators.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers
validate, `ty` (0.0.70), ruff, and the run gate are clean on
`build/examples/45_Generators` (the chapter has no pytest tests; its
listings are trace demos whose behavior the markers gate). Every
runtime and checker claim in the prose was probe-verified on the
pinned 3.15 beta: `send()` on a fresh generator raises the quoted
`TypeError: can't send non-None value to a just-started generator`
verbatim; a generator resumed from two threads raises the quoted
`ValueError: generator already executing`; `threading.synchronized_iterator()`
exists; `v = yield from [1, 2, 3]` sets `v` to `None`; a coroutine
object has `send()`, `throw()`, and `close()`; ty rejects `send()` on
an `Iterator`-annotated generator (`unresolved-attribute`); the
transposed `Generator[Answer, Question, Result]` annotation draws
nine errors in three groups of three (3 `invalid-yield`,
3 `invalid-assignment`, 3 `invalid-argument-type`), as the prose
counts them; and `reveal_type(stop.value)` is `Any`, so "the checker
verifies only two of those three parameters" holds. The four inbound
anchors (`#annotating-a-generator` from 08/23/46,
`#yield-from-composes-descriptions` from 23,
`#a-generator-is-a-description` from 46/47, `#the-return-channel`
from 47) point at headings this review did not touch. Both "next
chapter" phrases correctly mean 46_Stateless; no stale split-era
relative reference remains. The seven exercises match
`Solutions/45_Generators.md` in number and content, and exercise 4
keeps the number that `Solutions/47_Stateless_in_Practice.md` cites.
The teaching structure needed nothing moved at the section level: the
chapter escalates cleanly (annotation, hand-driving, driver, the four
`yield from` subsections, the asyncio bridge), and the lookalike and
near-miss coverage (`next()`/`send(None)`, `yield g()` vs
`yield from g()`, the hand-written forwarding loop, `drive()` vs
`yield from`) is unusually complete. Two Solutions text blocks quoted
stale output and were corrected against fresh probes. No live blocks
remain: every finding had one defensible answer.

## Applied directly

- "Annotating a Generator" opener: "the short form `Iterator[int]`"
  is now "the short `Iterator` form"; earlier generators yield other
  element types, so the `[int]` was false precision.
- The three-channel bullets now all say "type": `YieldType` and
  `ReturnType` said "value" while `SendType` said "type", and the
  three positions are types.
- "A newly created generator pauses before its first `yield`" is now
  "pauses at the top of the function body, before any code runs",
  which blocks the misreading that creation runs the body up to the
  first `yield` and pre-seeds the next section's "calling
  `interview()` runs nothing".
- "The `# type: ignore` is interesting." is now "The `# type: ignore`
  marks a real mismatch:" (throat-clearing opener replaced by the
  claim); "not of type `Answer`" tightened to "not an `Answer`".
- "Typically, that stepping happens in a driver:" is now "Typically,
  a driver function does the stepping:" ("happen" watch word, and
  "stepping" now has a doer).
- "which is what the `# type: ignore` on that line suppresses" is now
  "so the `# type: ignore` on that line suppresses the checker's
  complaint" (cleft removed, and the suppressed thing named).
- "That is EMS in miniature." is now "That is an EMS in miniature."
  (article, matching "an EMS" everywhere else).
- Moved the `g.send(2)` cascade paragraph above the
  manual-forwarding listing: it analyzes `both()` from
  `yield_from_send.py`, but sat after `manual_forwarding.py`, where
  `g` names a different generator; the send-channel analysis is now
  contiguous and the subsection ends on "`yield from` is not
  shorthand for this loop."
- Dropped "simply" from "appears in the declaration and simply goes
  unused".
- Conclusion: "the requests have to reach the loop" is now "must
  reach the loop" ("has to" watch word).
- Exercise 2: "Explain what had to change in `interview()`" is now
  "Explain what, if anything, needed to change", since the solution's
  answer is that nothing changed and nothing could have; the old
  wording presupposed a change that never comes.
- Exercise 7: "reports where the machine got to" is now "reports the
  state the machine reached" (stranded preposition).
- `Solutions/45_Generators.md`, exercise 4: the quoted runtime line
  `request = 'color', answers[request] = 'blue'` is stale; the
  chapter's `drive()` prints `request = 'color', answer = 'blue'`
  (re-run to confirm). The quoted ty diagnostic also pointed at
  `yield_from_nested.py:7`; the real diagnostic points at line 8
  (the header comment is line 1). Both corrected.
- `Solutions/45_Generators.md`, exercise 6: the quoted diagnostic
  cited a line (`print(interview().send(None))`) that does not exist
  in `send_none_is_next.py`, whose real line is the f-string with a
  `# type: ignore` that suppresses the error. The solution now says
  the ignore must come off and quotes the real diagnostic
  (`send_none_is_next.py:4:27`), verified against ty 0.0.70.
- Solutions style sweep: "the separation the chapter is about" is now
  "the chapter teaches" (stranded preposition); "are what that hazard
  looks like" is now "show that hazard"; "a reader has to work
  backward" is now "must work backward"; "which is what the
  expression is" is now "the expression's own type"; "is what
  completes it" is now "completes it"; "no counterpart here at all"
  is now "no counterpart here".

## Considered and declined

- **No pytest tests in the chapter.** Neighboring chapters 42/46
  carry tests, but every listing here is a stepping trace whose whole
  behavior the `#:` markers gate; a test would restate the markers.
- **The walrus in `two_way_generator.py`'s
  `print(f"{type(c := conversation)}: {c.__name__}")`.** It exists to
  keep the line inside the 70-column limit; splitting into two
  statements would cost a line in a listing whose point is the
  driver, and the walrus is taught long before Part V.
- **`throw()` and `close()` get one sentence and no listing.** The
  chapter needs them only to complete the "yield from relays
  everything" claim; a listing would be a digression from the Effect
  arc, and neither is used by chapter 46.
- **"at the cost of saying nothing about the other two channels"**
  reads as if the silence were purely a loss; for a one-way generator
  it is also the protection the next clause describes. Read twice and
  left alone: the colon does connect the cost to its consequence.
- **Exercise 6's solution simplifies `send()`'s stub to
  `send(self, value: _SendT_contra) -> _YieldT_co`**, omitting
  typeshed's positional-only `/`. The omission is harmless at the
  solution's level of detail.
