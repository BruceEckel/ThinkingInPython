> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 15_Techniques--Context_Managers (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I checked each runtime claim with a probe on the pinned 3.15.0rc2:
the single-use `AttributeError` and its message, `generator didn't stop`,
`_GeneratorContextManager` inheriting `ContextDecorator`,
the fresh manager per decorated call, `functools.wraps` on the wrapper,
`suppress()` suppressing nothing, `expected()` catching `KeyboardInterrupt` and `SystemExit`,
the per-manager rule in a comma-separated `with`, and `__context__` chaining.
All hold.
I read every linked section (chapters 02, 04, 05, 08, 10, 11, 14, 19, 23, 35)
and every inbound reference to this chapter (04, 10, 14, 16, 19, 39, 45, 47, and Solutions 19, 24, 26).
Each says what the link credits it with.
`tip prose CH=15` reports nothing, and `tip verify-ch CH=15` passes 24 of 24.

## Applied directly

Chapter, teaching:

- "The Protocol": the numbered list had no subject since the 2026-09-27 triage cut its lead-in,
  so the five steps read as instructions to the reader.
  Added "Python runs `with Trace("A") as t:` in five steps:", which names the actor.
- "The Protocol": `trace_cm.py` shows three `__exit__()` parameters that nothing explains for two sections.
  Added two sentences saying what they describe and that all three are `None` in this run.
- "The `__exit__()` Arguments": added the near-miss.
  Any truthy return suppresses, so an `__exit__()` that returns its last cleanup call's result swallows every exception.
  The advice is `-> None` unless suppressing is the manager's job; a `ty` probe confirms `invalid-return-type` on a returned `int`.
- `expected_one.py` had no introduction since the same triage.
  Added a lead-in stating what the class does: it suppresses through the return value of `__exit__()`.
- "What the Skeleton Leaves Out": added a paragraph saying `stale` stands for any stored reference
  and that `first` escapes without the assignment, because `with` creates no scope.
  The `# Escapes the block` comment suggested the assignment was needed.
- Exercise 8 added: restore the `try`/`finally` in `careless()` and predict where `exit A` prints.
  The chapter's main rule had no exercise.

Chapter, listings:

- `enter_fails.py`, `exit_masks.py`, `banner_cm.py`: `__exit__()` was `-> bool` with `return False`
  (or `-> bool` on a method that only raises an exception).
  All three are now `-> None` with no `return`, matching `Trace`.
  Two of them came before the section that teaches the return value.
  mypy rejects the old form (`exit-return`); `ty` accepts both.
- The `*exc: object` explanation moved from `banner_cm.py` to its first use, `enter_fails.py`.
  The `banner_cm.py` sentence now says why the method returns `None`.
- `pool_contention.py`: `WORKERS` and `ROUNDS` are `Final[int]`, per the constants rule.

Chapter, prose:

- "narrowed" is "narrows" (present tense for standing behavior).
- "prints which exception it ignores" is "prints the exception it caught"; the manager is no longer named `ignore`.
- "Fail the third manager and watch..." is two declarative sentences, without "at all".
- Dropped "really", "exactly" (twice), "at all", and "plain" where each changed nothing.

Solutions:

- Exercise 1: `__exit__()` parameters were unannotated. Now annotated as in `trace_cm.py`.
- Exercise 2: the listing defined its own `expected` that printed a `repr()`,
  and the prose said the output matched what `demo_exceptions.py` printed, which is `[Type] message`.
  The listing now imports the chapter's `expected` from `utils/`, as the exercise says, and the markers are in that form.
- Exercise 4: the exercise asks for a test, and the solution was a script.
  It is now `test_ch15_both_leased.py`, with a note on why it copies `Pool`
  and a sentence on what a third nested lease would do.
  `SolutionsCode/.../exercise_4.py` is pruned.
- Exercise 5: "one `banner(...)` object reused for every call" contradicted the chapter's
  "each call of the decorated function builds a fresh manager". Rewritten to say which object is built when.
- Exercise 6: the `ValueError` demonstration uses `expected(ValueError)`, not a `try`/`except` that prints.
- Exercise 8: new solution, `exercise_8.py`.
- Dropped "exact" and two uses of "exactly".

## Considered and declined

- The first four exception listings (`no_finally.py`, `exit_on_error.py`, `enter_fails.py`, `exit_masks.py`)
  use `try`/`except` with a `print()`. `expected` is defined later in this chapter, so they stay.
- `utils/exceptions.py` carries five things in one listing. It is one file, and the prose takes them one at a time.
- "The Async Protocol" uses `async`/`await` before chapter 19 teaches them. The section says so and links there.
- The `contextlib` list omits `redirect_stdout` and `chdir`. No chapter uses either.
- `leaked_lease.py` keeps `stale = first`. A stored reference is the realistic leak; the new paragraph covers the rest.
- "Python resumes the generator by raising the block's exception at the `yield`" is quoted verbatim by chapter 45,
  so I left the sentence untouched.
- Solutions exercise 6 types `tb` as `TracebackType | None` where the chapter uses `object`. Both are correct.
- "already", "even", "never", and "only" in the existing prose: each one I reread carries meaning in its sentence.
