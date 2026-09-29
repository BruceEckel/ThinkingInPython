> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Second deep review: Generators (chapter 45)

This second review ran on 2026-09-29, after the 2026-09-27 fix triage and the 2026-09-28 move of the transposed-annotation paragraph.
It carried forward `~45_Effects--Generators.md` and `deep_review_db.md`.
The triage rewrote one sentence here ("but generators are useful without it"), and it reads correctly, so it caused no damage in this chapter.
Every `ty` claim was re-probed on `ty` 0.0.84; all still hold.
Every finding had one sensible answer, so no block is left for a decision.

## Applied directly

- **Running to Exhaustion, "The `from` is what delegates":** a cleft ("is what" plus a verb) that delays the point. The sentence now reads "Without `from`, a bare `yield one()` yields the generator object as a single value." It also drops the flourish "itself".
- **The Return Channel, "`report()` itself is a one-way generator":** dropped the flourish "itself".
- **The Driver You Already Use, "three ideas from this one":** "this one" had no noun, since the preceding heading is a section. Now "from this chapter".
- **"The generator declares Effects, the driver interprets them":** a comma splice. Now joined with "and".
- **Composing Is Not Interpreting, the lead-in to `yield_from_nested.py`:** "Delegation can take over the job ... gives to `drive()`" contradicted the section's own conclusion, which is that `yield from` replaces `drive()` as `interview()`'s consumer but not as its runner. Now "`yield from` can take over one of the jobs `yield_from_delegates.py` gives to `drive()`, receiving `interview()`'s `Result`".
- **`throw()` and `close()`, "Doing so makes `close()` raise":** "raise" had no object. Now "raise a `RuntimeError`".
- **`throw()` and `close()`, the chapter 15 link:** dropped "already" from "already shows".
- **Solutions 5, closing paragraph:** it said `'(12 characters)'` appears "without ever crossing a frame boundary as a value". That is false: `report()` yields it and `summarize()`'s `yield from` relays it up to the driver. The paragraph now says that `12` reaches `summarize()` through two returns and is never yielded alone, while the string travels by the yield channel and no generator binds it to a name.
- **Solutions 1, "Three `NewType` aliases":** a `NewType` is a distinct type, not an alias, and that difference is the point of the solution. Now "definitions".
- **Solutions 7, "Both are `Generator[str, X, ...]`":** neither signature says `str`, since one yields `Question` and the other a `Report` literal. Now "Both yield strings".
- **Solutions 7, "two lines of the table-driven version":** the transition lookup in chapter 31's `table_machine.py` spans several lines. Now "two parts".
- **Solutions 7:** dropped "already" from "already cost something".

## Verified and left as written

- `ty` 0.0.84: `send()` on an `Iterator[int]` draws `unresolved-attribute`. All three `# type: ignore` comments still suppress a real diagnostic: the priming `send(None)` in `send_none_is_next.py` and `task_runner_send.py`, and `__name__` in `two_way_generator.py`. The transposed `Generator[Answer, Question, Result]` draws nine errors in three groups of three.
- Solutions 4: the quoted `invalid-assignment` diagnostic matches `ty` 0.0.84 at `8:23`, and `profile = interview()` with no annotation draws no diagnostic.
- The chapter 15 quotation ("Python resumes the generator by raising the block's exception at the `yield`") matches chapter 15, line 98.
- Chapter 31's table-driven machine keeps `self.state` and handles `Quit` from every state, as Solutions 7 says.
- Every solution does what its exercise asks, including exercise 2's short answer source and exercise 6's `SendType` argument.

## Considered and declined

- **"The Driver You Already Use" heading contains "already".** It states the section's claim (you have run such a driver through `asyncio`), and renaming it changes the anchor for no gain.
- **Chapter 15's sentence continues past the quoted clause.** The chapter quotes it ending in a period. The quoted clause is complete, so the quotation does not misstate it.
