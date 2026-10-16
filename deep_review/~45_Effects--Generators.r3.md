> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Third deep review: Generators (chapter 45)

This review ran on 2026-10-13 and carried forward `~45_Effects--Generators.r2.md`, `~45_Effects--Generators.md`, and `deep_review_db.md`.
It ran every extracted listing in both trees directly under `uv run` (Python 3.15.0) and compared each against its `#:` markers; all matched.
Every `ty` claim in the chapter and its Solutions file was re-probed on `ty` 0.0.86: the nine errors in three groups for the transposed annotation, `unresolved-attribute` for `send()` on an `Iterator[int]`, `Any` for `StopIteration.value`, both quoted diagnostics (Solutions 4 at `8:23`, Solutions 6 at `4:27`), and the near-miss claims in Solutions 1, 5, and 7.
Runtime claims were probed too: a hand-written iterator's `StopIteration(5)` reaching `yield from`, the just-started `TypeError` text, `close()` on garbage collection, and the "never awaited" warning a coroutine draws and a generator does not.
`tip verify-ch CH=45 ISOLATED=1` passed 27 of 27 before and after; `tip prose CH=45` shows no new hits.
No live blocks: every finding had one sensible answer.

## Applied directly

- **Annotating a Generator, "Earlier examples annotate every generator with the short `Iterator` form":** false since chapter 15's `@contextmanager` listings annotate with `Generator[str]` and `Generator[None]`. Now names both short forms with links to Iterators and Context Managers.
- **A Basic Context Manager quotation (`throw()` and `close()` section):** the quoted sentence "Python resumes the generator ..." no longer exists in chapter 15, which now says `@contextmanager`'s `__exit__()` calls `throw()`, "which resumes the generator by raising the block's exception at the `yield`." The quote now matches, and the lead-in no longer presents `throw()` as new when chapter 15 already names it.
- **Opening, "the loop that carries such a conversation":** "driver" was used here and at the priming paragraph before the chapter defined it (line 209). Now "the loop that runs such a conversation, called a *driver*".
- **`interview_generator.py` paragraph, "`Question("name")` produces the plain `str`":** filler "plain", and the mechanism unstated. Now "At runtime, `Question("name")` returns its argument unchanged, a `str`."
- **StopIteration paragraph, "Python raises that `StopIteration` for the generator. The body finishes with `return`.":** two disconnected sentences with the cause after the effect. Joined: the body finishes with `return`, and Python raises the `StopIteration` on its behalf.
- **`yield from` Composes Descriptions, "carry an EMS":** figurative; now "support".
- **Running to Exhaustion:** the `yield one()` near-miss sat inside the paragraph about what exhaustion means. It is now its own paragraph and shows its consequence: `list(outer())` would show `<generator object one at ...>` in place of `'only'`.
- **All Three Channels, "`drive()` is the same function as in ... Only the generator portion changed":** now says the listing imports `drive()` unchanged and the new code is all on the generator side (vague "portion", an `only` before a vague noun).
- **`throw_and_close.py` walkthrough:** added that `throw()` returns the next yielded value (where the printed `recovered` comes from) and that an unhandled thrown exception ends the generator and propagates out of `throw()`. Both are mechanisms the listing shows only by outcome.
- **`throw_and_close.py` walkthrough, "Nothing prints the `GeneratorExit` itself":** restated positively and without the flourish "itself".
- **`throw_and_close_gotcha.py` closing paragraph:** added that Python calls `close()` on an unfinished generator it reclaims, and that a stubborn generator's `RuntimeError` then appears as an "Exception ignored" message. The rule "must let `GeneratorExit` end it" now holds for generators nobody closes explicitly.
- **Solutions 3, "The second line of `send(6)`'s pair is the exception":** "exception" read as a Python exception in a paragraph about `StopIteration`. Now "breaks the pattern".
- **Solutions 4:** added the lookalike contrast with chapter 19: a coroutine nothing awaits draws a `RuntimeWarning`, while a generator nothing drives disappears silently. Dropped "happily".
- **Solutions 5, "`Iterator` sets the `ReturnType` to `None`":** `Iterator` has no `ReturnType`. Now "Under `Iterator[str]` a generator may return only `None`".
- **Solutions 6, widening to `Answer | None`:** said each `yield` "must then handle a `None` that arrives only once". The priming `None` reaches no `yield` at all, since it arrives before the first one. Now says the `None` exists only in the type, and why.
- **Solutions 6:** dropped "whatsoever".
- **Solutions 7, "each one returns by looping back":** "returns" read as Python's `return`. Now "from each one the machine loops back to the top".

## Considered and declined

- **The Solutions file has bold-label paragraphs with first lines over 70 columns** (exercises 1, 2, 3, 5, 7). The rendered output is unaffected, and rewrapping would touch many lines for no reader benefit.
- **"Annotating a Generator" also covers driving by hand, `StopIteration`, and priming.** Renaming it to match would break the anchor that chapters 08 and 23 and Solutions 1 and 6 link to.
- **"`yield from` is not shorthand for this loop."** The negative sits right after the near-miss loop and corrects the reader's assumption, so it stays.
- **Chapter 15 annotates with `Generator[str]` while this chapter says `Iterator[int]` reads better.** That choice belongs to chapter 15, and both forms are correct.

## For the session

- **Chapter 15, line 32:** "[Iterators](22_Patterns--Iterators.md#generators) covers generators in full." Chapter 23 covers one-way generators and defers the full form to chapter 45, as its own line 90 says. Suggested fix: "covers generators", or add "and [Generators](45_Effects--Generators.md) covers the rest".
- **Stale baseline entries** that this review's edits removed (for pruning; I did not touch `tools/data/`): watch-words `itself: Nothing prints the CODE itself`, `only: Only the generator portion changed`, and Solutions 45's `only: ... arrives only once`; positional `'The second line' :: The second line of `send(6)`'s pair is the exception.`
- **`tip grounding-triage` not run**, since it writes `tools/data/grounding_verdicts.json`. Three edited sentences link another chapter: the new chapter 23/15 short-form sentence, the chapter 15 quotation, and Solutions 4's chapter 19 link. Each sentence's code terms appear in the linked section.
- **Exercise 7 and its solution depend on chapter 31** (open editing pass). I checked them against the current chapter 31 `vending_machine.py` (an `Enum` state, a transition table, `Quit` from every state but `QUIESCENT`) and made no change that depends on it.
