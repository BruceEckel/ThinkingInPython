> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 42_Functional--Error_Handling, second review (2026-09-29)

This run follows the completed review of 2026-09-25
(`~42_Functional--Error_Handling.md`) and the five commits made since.
Nothing here needs your decision, so the file has no live blocks.
The commits since the first review left no damage:
the paragraph that `d73bf560` moved below `result.py` reads correctly there,
and the link that `98072242` repointed lands on a section that states the idea.
I re-probed every checker claim on `ty` 0.0.84 in `build/examples/42_*`:
the `unwrap` and `answer` reports on `Err[str]`, `isinstance(a, Result)`
(rejected, and a `TypeError` at runtime), `.bind(str)`, the mixed-error chain
(`Ok[int] | Err[ValueError] | Err[str]`, rejected as `Result[int, str]`),
`parse(42)` under `@safe`, and `__notes__` as `list[str]`.
All hold, and no sentence in the chapter names a `ty` version.
The `Err` narrowing gap stays closed: `case Err(error)` captures `Exception`.
The `returns` claims (`Success`/`Failure`, `@safe`, `map()`, do-notation)
match the library's documentation.
`utils/result.py` and `utils/safe.py` are unchanged,
so Appendix B's self-check marker is untouched.
`tip verify-ch CH=42` passes 24 of 24.

## Applied directly

Chapter, corrections:

- "Exceptions Discard Partial Calculations": the sentence said chapter 12
  "flags that scattering as a problem", but the linked section is about a
  range check repeated in every function, and does not mention `try`.
  The sentence now draws the comparison: handling repeated at every call,
  the way chapter 12 repeats a range check.
- "A Result Type": "`@final` states that neither can have subclasses" and
  "the type checker narrows ... because `Result` is a union" sat side by
  side with no link between them. `@final` is the cause. Without it `ty`
  narrows `isinstance(r, Err)` to `(Ok[int] & Err[Unknown]) | Err[Exception]`
  and `case Ok(answer)` captures `int | Unknown`. The prose now says why:
  no class can inherit from both.
- After `composing_exceptions.py`: "it reports a failure as a message to
  parse" drew no contrast, since `composing.py` also reports a string.
  The contrast the listings support is the signature, `-> int` against
  `-> Result[int, str]`, which is the chapter's second drawback.
  "Agree on every input" is now "succeed and fail on the same inputs",
  since the two print different text for input 3.
  The clause you kept on 2026-09-25 (the failure disappears when the
  `except` clause ends) stays.
- "Combining Multiple Results": "causes the same loss" compared a loss of
  later steps with a listing the chapter uses for lost earlier work.
  Now "does the same to `func_a(4)`, which never runs", which the output
  of `exceptions_lose_data.py` shows.
- "Turning Exceptions into Results": "`Result[int, str]` names exactly
  what could go wrong" was false of the type, since `str` names no
  failure, and "the narrower type" pointed at `func_c()`, whose error
  type is `str`. The paragraph now says what is narrower in `func_c()`
  (it catches `ZeroDivisionError` alone) and gives the type a hand-written
  `parse()` can return, `Result[int, ValueError]` (probed).
- "Which Failures Get a Result": "Some languages call these errors
  *panics* and separate them from regular exceptions." The languages
  with panics, Rust and Go, have no exceptions; they return errors as
  values, which is this chapter's subject. The sentence names them.

Chapter, teaching:

- "Matching on the Error": added the near-miss. `case Err(ValueError):`
  without the parentheses is a capture that matches every `Err`.
  Python compiles it and `ty` accepts it (probed; `ruff` reports only the
  name's case), and `describe()` then answers "Not a number" for a
  `ZeroDivisionError`. Links chapter 13's bare-name section.
- "Reaching the Answer": "the only way to the answer is narrowing" now
  says how, and names the two listings that do it.
- "Attaching Context": "typeshed" gets a gloss. The book does not explain
  it before the appendices.
- "The returns Library": its `@safe` takes an `exceptions` argument, the
  production form the `@safe` section describes and exercise 4 builds.
  The exercise reference is accepted in `exercise_refs_baseline.txt`.

Chapter, house style and prose:

- `must_unwrap.py`: the `try`/`except` that printed `e` is now
  `with expected(AttributeError):`, per the `expect()` preference.
  The call and its `# type: ignore` stay visible. The marker takes the
  `[AttributeError] message` form.
- "Total Functions": "Both type-check clean:" had no two things before it
  and repeated "`ty` accepts both" after the listing. The lead-in now
  says what the listing holds.
- After `combining.py`: removed "Each nested bind keeps the earlier
  answers in scope", the third statement of that point in the section.
- "Decorating a function that raises an exception is all it takes:" is
  now "`@safe` goes on any function that can raise an exception:".

Solutions:

- Exercises 1, 3, 4, and 5 each carried a copy of the chapter's `Ok`,
  `Err`, and `Result`. They now import them from `utils/result.py`, which
  Solutions listings can do since 2026-09-16. Exercise 2 keeps its own
  pair, since the exercise changes the classes, and its prose says so.
  `from __future__ import annotations` is gone from exercises 1 and 2;
  3.15 needs no such import.
- Exercise 1 asks you to confirm the skipped step never runs, and the
  solution only asserted it. `func_c()` now prints when it runs, and the
  output shows the line for inputs 0 and 3 and not for 4.
- Exercise 2: "`map_error()` is `bind()`'s mirror image" was wrong about
  the function each takes. `bind()`'s function returns a `Result`;
  `map_error()`'s returns the bare error, as the chapter's `map()` does
  for answers. Added that `returns` names this method `alt()`.
- Exercise 4: the `try`/`except` is now `expect(TypeError, parse, "oops")`.
  "Keeps the types honest" and "says exactly that" reworded.
- Exercise 5: "because there is no traceback" contradicted the chapter,
  which says the exception still holds its `__traceback__` (probed: it
  does). Also "reads better than nested binds here" described a listing
  with one flat `bind()`; the fault it means is the lambda that discards
  its argument.

## Considered and declined

- **The comments in `totality_gap.py`.** The two-line comment after the
  `raise` holds the reason `ty` accepts `lies()`, and by house style that
  belongs in prose. It is a comment already in the chapter, so it stays.
- **`matching_errors.py` defines the same `parse()` as `safe_demo.py`.**
  Importing it would save three lines and cost the listing its
  self-containment. Chapter 43's exercise 7 builds on this listing.
- **`exceptions_lose_data.py` and `composing_exceptions.py` keep their
  `try`/`except`.** Each handler prints its own text, and the handler is
  the subject of the listing.
- **"You can use `bind()` without the word, which names a reusable
  shape."** The first review reworded this sentence. "Which" sits beside
  "the word", so it has one reading.
- **No exercise covers "Matching on the Error" or "Total Functions".**
  Chapter 43's exercise 7 extends `describe()`, and `totality_gap.py`
  leaves little to build.
- **"A signature admits it can fail" in the closing section.** A figure
  of speech the literal pass left; the sentence is clear.
