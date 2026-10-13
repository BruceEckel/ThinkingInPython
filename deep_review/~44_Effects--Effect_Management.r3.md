> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 44_Effects--Effect_Management, third review (2026-10-13)

This run follows `~44_Effects--Effect_Management.r2.md` (2026-09-29), both outside reviews' verdicts, and the commits made to the chapter since.
None of the earlier applied items, declined items, or verdicts is raised again.
I ran every listing directly from `build/verify-ch-44/` and compared it with its `#:` markers (all match);
`pure_and_pointless.py` printed `True` on three runs, with ratios from 390,000 to 500,000.
I re-probed the Solutions' checker claims on `ty` 0.0.86:
`CoroutineType[Any, Any, float]`, `no-matching-overload` for both the missing `await` and the generator expression,
and `invalid-argument-type` at the `greet(...)` call for a `tell()` returning `str` all still hold,
and both `TypeError`s and the `RuntimeWarning` appear under `uv run python`.
I rechecked the cross-chapter claims (18, 20, 30, 32, 34, 40, 43, 46, Appendix A), Koka's `readline()` signature in its standard library,
the npm registry for Effect's current release, and the PEP index for an Effect-tracking proposal (none).
`tip verify-ch CH=44 ISOLATED=1` passed 27 of 27 before and after; `tip prose CH=44` reports no new hits.
No live blocks.

## Applied directly

- TypeScript listing: Effect 4.0.4 is now the `latest` release on npm, and `Context` in 4.x exports `Service` and no `Tag`.
  `class Tell extends Context.Tag("Tell")<...>() {}` is now `class Tell extends Context.Service<...>()("Tell") {}`,
  and the comment says "as a service".
  `Layer.succeed(Tell, {...})`, `yield* Tell` (a `Context.Key` extends `Effect`), and `Effect.provide` are unchanged in 4.x.
  This is the revisit the second review's declined item scheduled for the 4.0 release.
- Koka listing: `readline()` lives in `std/os/readline`, which `std/core` does not import, so the program as shown did not compile.
  Added `import std/os/readline`. Its signature there, `<console,exn> string`, matches the prose's account of `main()`'s row.
- "Native Effect Management": "so you rarely write one by hand" sat right after a listing that writes two rows by hand.
  Added "The listing writes both rows out so you can read them."
- "Are Exceptions Impure?": "The argument over purity leaves this chapter's question open" read as "unanswered", and the paragraph then answers it.
  Now "This chapter asks a different question: does the exception pass from callee to caller?", which the next sentences answer.
- "Make the Bad Value Impossible": "removes the failure instead of handling it" contradicted "None of the three makes the failure disappear" two sections on.
  Now "removes the failure from `slope()` instead of handling it there".
  "Effects by Hand" said the same ("removes the failure at construction"); now "moves the failure to construction", the chapter's own verb for it.
- "Custom AI Languages with Effects": the reason the second and third parts are liabilities was compressed into one clause.
  Now two clauses: a host that supplies every implementation can guarantee what generated code does, and rebinding would break that.
- Exercise 5: "that `async` does *not* have" used italics for emphasis; now "that `async` lacks". The Solutions quote regenerated.
- Solutions exercise 2: the answer described only a library EMS ("declares in its return type") for a question about what an EMS would do.
  "An Effect Management System collapses ..." is now "A library EMS collapses ...", and a new paragraph says what a native EMS does:
  Koka infers an unannotated function's row, so the four existing signatures stay as they were.

## Considered and declined

- "Calling an effectful function from one annotated as pure is a type error" ("Effect Management for Python?").
  Chapter 46 shows that a bare `greet(name)` inside a generator with another `yield` passes every check, so the precise claim is about `yield from`.
  The reader has not met `yield from` yet, chapter 46 teaches the trap where it applies, and the next paragraph already states the guarantee's limit.
- `ask_tell.py` and `bookkeeping_scales.py` keep `@dataclass` on `Capture`.
  The class is mutable state (its list grows), and `tip records` only governs frozen classes.
- "A `ContextVar` holds a value for the current task": a thread has its own context too, but the paragraph is about a call chain,
  and chapter 19's linked section frames it the same way.

## For the session

- `tip prose` prints a stale `internal_names` baseline entry outside this chapter:
  `Examples/15_Techniques--Context_Managers/banner_cm.py::banner.title`. Not touched.
