# Review: Chapter 12 (Functional Error Handling)

A polished chapter. The arc from "exceptions throw everything away" to a
hand-rolled `Result`, then `bind()`, then `@safe`, then matching on the error
type, is clear and well-motivated. Every one of the eight scripts produces output
that matches its "The output is:" block exactly, the 7 tests pass, and `ty` and
`ruff` are clean. Very little to fix.

## Should fix

1. **Trailing whitespace (lines 20 and 150).**
   - Line 20: `An exception discards the whole computation, ` (trailing space).
   - Line 150: `A function reports failure by returning a `Failure` object, `
     (trailing space).
   Neither fails the build (the CRLF check does not look at trailing spaces, and
   `prose_lint`'s TRAILING-WS rule only runs under `make spell`), so they sit
   there silently. Easy to strip.

2. **Muddled type-variable sentence (line 99).**
   "`A`, `B`, and `E` are type variables, which mean they expect type arguments."
   Two problems: "which mean" reads better as "which means", and "type variables
   expect type arguments" conflates the placeholders with the generic classes that
   take the arguments. Suggested rewrite: "`A`, `B`, and `E` are type parameters:
   placeholders that are filled in with concrete types when the class is used."
   Then the next sentence ("Here they have no constraints...") follows naturally.

## Nits / optional

3. **Comma for readability (line 162).**
   "because to get the answer `Result` must be unpacked" parses more easily as
   "because, to get the answer, the `Result` must be unpacked".

4. **Tone (line 258).**
   "You do not need to know that word to use it." is a nice aside; just flagging it
   as the one chatty line if you want a uniform register. Fine to keep.

## Verified

- Ran all eight scripts. Every output matches the prose, including:
  `exceptions_lose_data` (loses calls 0-2), `sum_type`
  (`[0, 1, 2, 'func_a(3)', 4]` plus the match branches), `returning_result`,
  `composing` and `composing_with_bind` (identical output), `combining`
  (`add(7 + 5 + 12): 24` for the only all-success case), `safe`
  (`42: parsed 42` / `oops: ValueError`), and `matching_errors`
  (`4: 0.25` / `0: Cannot divide by zero` / `OOPS: Not a number`).
- `pytest` on the chapter: 7 passed.
- `ty` and `ruff` clean on the chapter.
- The PEP 695 generics (`class Success[A]`, `def bind[B, E]`,
  `type Result[A, E] = ...`) type-check, and the function-paren convention is
  applied (`bind()`, `func_a()`, `parse()`, `reciprocal()`, `add()`,
  `pytest.raises()`, and the exercise references `func_e()`/`map_error()`).

Note: the example extraction now lands in `build/examples/` (not
`ExtractedExamples/`); the tooling output path changed since the earlier reviews.
This did not affect anything, just flagging in case it was unintended.
