> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Fourth deep review: Generators (chapter 45)

This review ran on 2026-10-29 and carried forward `~45_Effects--Generators.r3.md` (no rejected blocks in any of the three completed reviews) and `deep_review_db.md` (no chapter 45 entries).
It followed a day of session edits to the chapter that Bruce directed and reviewed as they landed: `yield_from_arguments.py` and exercise 5, `follow_up.py`, the quiet `ask()`, one `interview()` from "All Three Channels" on, the guarded priming calls in `proxy()` and `task_runner_send.py`, and the R52 rewrites.
Those are in `git log` for the day and are not repeated below.
The correctness pass ran every extracted listing in both trees through `tip verify-ch CH=45` (27 of 27, Python 3.15.1, markers unchanged), probed `copy.copy()` on a suspended generator and `close()`'s return value, and checked the history section against PEP 255, PEP 342, and the May 1999 python-dev post.
`tip prose CH=45` shows no new hits.
One live block.

## Applied directly

- **Annotating a Generator, `interview_generator.py` paragraph:** "easer" was a typo, and the relative clause needed its comma. Now "a distinct type, which makes the logic easier to follow".
- **Annotating a Generator, after `drive_by_hand.py`:** the one-line paragraph "The `NewType` definitions let the type checker report any annotation mistakes" repeated the paragraph above the listing. Cut.
- **The Return Channel, `color_count.py`:** "Note that `Counter` objects can be added together" was metadiscourse beside an outcome. Now says the mechanism the listing uses: `Counter` supports `+`, so `counts += yield from visit(...)` merges a subtree's counts into the parent's counts.
- **`throw()` and `close()`, `throw_and_close.py` walkthrough:** "`close()` ... returns `None` once the generator finishes" has been false since Python 3.13 for a generator that returns a value while handling `GeneratorExit` (probed: `close()` returns that value). Now says `close()` returns when the generator finishes, that its return value is whatever the generator returned while handling `GeneratorExit`, and that it is `None` here because `worker()` lets the exception propagate.
- **Half a Coroutine by Design, opening:** "The problem appears whenever..." named a problem the paragraph had not introduced. Now "The need for that pause appears whenever...", tying it to the pause the previous sentences describe.
- **Half a Coroutine by Design, `fibonacci_list.py`:** "the generator `fibonacci()` in `iterators.py`" now links [Iterators](22_Patterns--Iterators.md#generators), where that listing lives.
- **The Restriction Behind the Driver:** "The other half came in 2005, when PEP 342 added the send channel to Python 2.5" conflated the PEP's year with the release's. PEP 342 is dated May 2005; Python 2.5 shipped in 2006. Now says both.
- **Composing Is Not Interpreting, proxy paragraph:** "returns before it yields at all" (Tier 2 "at all") is now "returns before its first `yield`".
- **Exercise 9, new, with its Solutions ladder:** replace `proxy()`'s loop with `return (yield from inner)` and explain from the output why it cannot answer `town`. The section's claim, that `yield from` composes and does not interpret, had no exercise; this one makes the reader meet the near-miss (a `yield from` where a relaying `yield` belongs) and name where `proxy()`'s body waits while `inner` runs. Appended as 9 rather than inserted after 5 to leave the existing numbering and Solutions file names alone.

## Live blocks

### Half a Coroutine by Design: the `accumulate()`/unfold digression

**Where.** The three paragraphs after `fibonacci_list.py`, from "This is a functional version of the generator `fibonacci()`..." through "A generator is the direct way to write an unfold."

**What.** The section's job is to show three pre-generator ways to write a producer and what each gives up, so that the generator's "both sides keep their loop" lands. The second way, the list, takes one sentence to make its point ("the sequence must be finite and fit in memory") and then three paragraphs to explain `accumulate()` over `repeat(None)`, compare it with chapter 41's `itertools_accumulate.py`, and introduce the unfold with `more-itertools` and `toolz`. Nothing after the section depends on any of it, and the "Each approach gives up one side's loop" summary names the list version in one line. Under the one-claim-one-arc test the digression is the one passage in the chapter that could be cut with nothing downstream noticing.

**Proposed change.** Keep the first paragraph's first three sentences (the functional version, `accumulate()` as a `reduce()` that keeps intermediates, `repeat(None)` as the step counter) and the last paragraph's last two sentences ("A sequence built from a start value and a step needs the opposite operation, an *unfold*. A generator is the direct way to write an unfold."), and cut the walk through the lambda's `_` parameter, the comparison with `itertools_accumulate.py`, and the `more-itertools`/`toolz` sentences. The listing stays as it is; it is a fair functional version and the unfold observation is the reason it reads awkwardly.

**Why a block.** The paragraphs are deliberate (two chapter 41 links, a third-party pointer) and the unfold observation is a real one, so whether the section carries that much functional-programming context is yours. I would cut it to the five sentences above.

`[] Reject`

## Considered and declined

- **Re-adding the `for item in inner: yield item` near-miss beside `yield from`.** The chapter once said "`yield from` is not shorthand for this loop" beside such a loop, and the third review kept it; Bruce removed the passage in c19c3ff06. The lookalike is real (the loop forwards the yield channel and drops the send channel, so `collect()`'s `first` would receive `None`), and exercise 9 now makes the reader meet the other half of it, a `yield from` where a `yield` belongs. Not re-proposed.
- **Showing the just-started `TypeError` in `send_none_is_next.py`.** The message the prose quotes, "can't send non-None value to a just-started generator", is wider than a `#:` marker allows, and printing the type alone teaches less than the quoted sentence does.
- **`drive()`'s `show_state` keyword and `inspect` import**, which exist for `two_way_generator.py` alone. Incidental code in a reused listing, but moving the state trace out needs a second driver, and every other reuse reads past the default.
- **`sequence()` accepting `interview()` and `ask()` because `Result` and `Answer` are both `str`.** A convenience of the `NewType` choice rather than a design, but exercise 5 turns it into the typing lesson it deserves, and the prose says why both qualify.
- **Exercise order.** Exercise 9 belongs with 4 and 5 by section. Inserting it there would renumber 6 through 8 and rename three Solutions files for no reader benefit.

## For the session

- `tip grounding-triage` was not run, since it writes `tools/data/grounding_verdicts.json`. One edited sentence links another chapter: the `fibonacci_list.py` paragraph's new link to [Iterators](22_Patterns--Iterators.md#generators), whose code term `fibonacci()` appears in that section's `iterators.py`.
