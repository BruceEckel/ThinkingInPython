> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Deep review of chapter 42, run on 2026-09-25 after the six prose passes
(elements-of-style, literal, positive, straighten, cohesion, antecedents),
each committed separately on `claude/prep-42`. The prose pass ran without
the global `~/.claude/CLAUDE.md` watch list, which is not present in cloud
sessions; it used the skill's own rules, `banned_phrases.py`, and the
repo's `CLAUDE.md`. Every checker claim the prose makes was re-probed
against `ty` in `build/examples/42_*`: the `unwrap` report on `Err[str]`,
`.bind(str)` rejected, a mixed-error chain revealing
`Ok[int] | Err[ValueError] | Err[str]` and failing a `Result[int, str]`
annotation, `isinstance(x, Result)` rejected (and raising `TypeError` at
runtime), and `__notes__` revealed as `list[str]`. All hold.

## Applied directly

- Intro, "removes all three" → "addresses all three": `totality_gap.py`
  shows a discarded `Result` passes the checker, so the third drawback
  (forgetting to handle one) is reduced, not removed.
- "Return the Error as a Value": dropped "(a *disjoint* union)". A disjoint
  union is the tagged kind; `int | str` has no tag, and the next section
  shows the two sides colliding, so the parenthetical contradicted the
  paragraph.
- "A Result Type": "frozen data classes" → "[records](18_...#record)", and
  "The two data classes" → "The two records", per `CLAUDE.md`'s `@record`
  rule (chapter 42 is past chapter 18, and `result.py` uses `@record`).
- After `composing_exceptions.py`: added that the message names the step
  only when the raiser wrote it in, and input 3's `division by zero` names
  none (the `#:` output shows it). See block 2.
- "Composing With bind": removed the second "the check `composing.py`
  repeats ... written once" (the section's first sentence already says it);
  the paragraph now says `composed()` has no `isinstance()` check or early
  return left.
- `Err.bind()` paragraph: "its return type is `Err[E]`, the same failure"
  repeated the previous sentence's "the same failure"; now "because it
  returns `self`".
- Monad paragraph: a monad also needs a way to wrap a plain value, not only
  `bind()`; the sentence now names `Ok()` as that. "Knowing the word is
  optional; the word marks" (a pass artifact) reworded.
- `test_result.py` lead-in: `is` proves the original `Err` came back, not
  that the lambda never ran; reworded to what the assertion proves.
- `test_composing.py`: the `for` loop inside one test became
  `@pytest.mark.parametrize("i", range(5))`, per the house style's
  one-case-per-report rule; `Examples/` synced. The lead-in sentence still
  holds.
- "Attaching Context": `__cause__` vs `__context__` were named but not told
  apart; added which one `raise ... from e` sets and which an implicit
  raise sets.
- After `noted_result.py`: added the near-miss. The chapter says reading
  `__notes__` before any `add_note()` raises, and the listing reads it
  directly; the listing is safe only because `parse_field()` always adds a
  note, so exceptions from elsewhere want `getattr(error, "__notes__", [])`.
- Exercise 3: `combined` → `combined()`.

## 1. Exercise 5 asks about a note that never exists

"What happens to the note the successful call would have added?" The
successful call never reaches `add_note()`, and the solution's answer is
"The successful call has no note to lose." A question built on a false
premise can be a deliberate trap (the reader should notice there is no
such note), or it can read as the book being wrong.

If it is deliberate, leave it. If not, I would reword it to
"Does the successful call carry a note? Why or why not?", which asks the
same thing without the premise; the solution needs no change.

[] Reject

## 2. The two `composed()` versions are not written alike

`composing.py`'s `func_c()` writes its own name into the `Err`
(`func_c(3): division by zero`), while `composing_exceptions.py`'s
`func_c()` lets the bare `ZeroDivisionError` through, so its message is
only `division by zero`. I added a clause saying the exception version's
message names the step only when the raiser wrote it in, which is true of
the listings as they stand. But the asymmetry is in the listings, not in
exceptions versus values: an exception version whose `func_c()` caught
and re-raised with its name would print the same text.

Two ways to go: keep the clause (it teaches that a message is only as good
as its author made it, which is also the lead-in to "Attaching Context");
or drop the clause and let the comparison rest on "the failure disappears
when the `except` clause ends", which is the difference that does not
depend on how the listings were written. I lean toward dropping it, since
the chapter's argument is stronger on the difference that holds in
general.

[] Reject

## Considered and declined

- **`utils/result.py` and `utils/safe.py`.** No change proposed to either.
  Both type-check and every claim about them holds, and `safe()` catching `Exception` is the deliberate small version the prose
  and exercise 4 already discuss.
- **"*Total Function*" capitalized.** Looks like the pattern-name
  convention misapplied, but chapter 44 uses the same form
  (`A *Total Function* doesn't raise exceptions`), so it reads as the
  book's chosen term of art. Left as is in both places.
- **`composing.py`'s bare `1 / (i - 3)` vs `composing_exceptions.py`'s
  `_ = 1 / (i - 3)`.** Different spellings of the same probe; both lint
  clean and each carries a comment saying what it does. Not worth a
  listing edit.
- **`noted_result.py`'s `parse_field(name: str,\n text: str)` wrap** differs
  from `describe()`'s one-parameter-line style. Cosmetic.
