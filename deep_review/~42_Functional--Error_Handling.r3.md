> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 42_Functional--Error_Handling, third review (2026-10-13)

This run follows `~42_Functional--Error_Handling.r2.md` (2026-09-29)
and the listing-design and outside-review commits since.
I re-probed every checker claim on `ty` 0.0.86 under Python 3.15.0
in the isolated tree: `unwrap` and `answer` on `Err[str]`,
`Result + 1`, `isinstance(r, Result)` (rejected, `TypeAliasType`),
`.bind(str)`, the mixed-error chain (`Ok[int] | Err[str] | Err[ValueError]`,
rejected as `Result[int, str]`), `parse(42)` under `@safe`,
the bare-name `case Err(ValueError):` (accepted, binds `Exception`),
`__notes__` as `list[str]`, `match`/`isinstance()` narrowing to
`Err[str]`/`Ok[int]`, and no diagnostic on `lies()` or the discarded
`func_a(1)`. All hold. In Solutions, exercise 2's `unresolved-attribute`,
exercise 4's `call-non-callable` and both revealed signatures hold.
Every listing run directly matches its markers.
`utils/result.py` and `utils/safe.py` are unchanged,
so Appendix B's self-check marker is untouched.
The open Listing Proposals card on `test_safe.py` was left for that page.
`tip verify-ch CH=42 ISOLATED=1` passes 27 of 27 before and after;
`tip prose` reports no new hits. No live blocks.

## Applied directly

Chapter:

- Opening: the paragraph on what returning a value fixes held two
  ideas (the signature, local control flow) and ended on "The check at
  each step is where you handle every failure", which needed a second
  reading. Split at the seam; the locality half now names the drawback
  it answers (a failure leaves the other results intact) and says where
  the handling sits.
- After `must_unwrap.py`: "The `# type: ignore` is the point of the
  listing" overstated it; the point is the runtime `AttributeError`.
  Now says the comment silences the checker so the listing can reach
  the runtime failure, and that without it the reader sees the report
  at check time, before the runtime error.
- "Total Functions": split the author-side gap from the caller-side
  gap (two concepts). "ignoring one is up to you" read as permission;
  now "noticing an ignored one is up to you". The listing lead-in names
  both gaps.
- After `totality_gap.py`: "accepts both, because a function that always
  raises an exception..." gave one reason for two cases. The discarded
  value now gets its own reason.
- "Composing by Hand": the `__all__` sentence implied `__all__` makes
  the import possible. It now states the goal first and what `__all__`
  declares, linking chapter 6's section.
- `composing_exceptions.py`: comment "Raises when i == 3" names the
  exception, `ZeroDivisionError` (59 columns).
- `@safe` "takes a function that raises an exception" is now "can raise".
- Split the paragraph after `safe_demo.py` between the unpacking
  consequence and the breadth of `Exception`; "a bare `except Exception`"
  is now "an `except Exception` clause" (a bare `except` means no type).
- After `matching_errors.py`: "so `bind()` chains them" gained its
  reason, each returns a `Result`.
- "The returns Library": "the same `@safe` decorator" is now "a `@safe`
  decorator like the one in `safe.py`", since its version takes the
  `exceptions` argument described in the next sentence.

Solutions:

- Exercise 3: `combined()` ran an error list, an `if errors:` return,
  and three `assert isinstance` lines to narrow for the checker. It now
  matches the three results as a tuple: `case Ok(a), Ok(b), Ok(c)`
  narrows each to `Ok[int]`, and `case results` gathers the errors.
  `ty` accepts it with no asserts (probed), and the tests pass. The hint
  and the "Gather" and "Narrow" paragraphs follow; the old shape is now
  the near-miss (probed: `ty` rejects `a.answer` after the early return).
- Exercise 5: "The successful call has no note to lose" echoed an older
  wording of the question; now "carries no note".

## Considered and declined

- **`test_safe.py`'s `match` with `raise AssertionError`.** The open
  Listing Proposals card `c42-test_safe-q1-r10` covers it.
- **Exercise 1 and 3 copy `func_a()` through `func_c()`.** Solutions may
  import `utils/` but never chapter modules, so the copies stay.
- **The `__context__` parenthetical** ("set when a handler raises an
  exception without `from`"). `__context__` is set with `from` too, but
  the sentence tells the reader where to look in each case, which holds.
- **"Exceptions remain the right tool for truly exceptional conditions."**
  "truly" carries the contrast with routine failures in the next paragraph.

## For the session

Nothing outside this chapter. `tip verify-ch` regenerated
`Examples/42_Functional--Error_Handling/composing_exceptions.py` and
`Solutions/42_Functional--Error_Handling/test_ch42_combined.py`.
