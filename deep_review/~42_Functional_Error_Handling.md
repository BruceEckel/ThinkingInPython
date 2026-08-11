[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/42_Functional_Error_Handling.md`
in the clean-slate sweep. The mechanical layer is sound: all `#:` markers
validate, `ty` (0.0.70), ruff, and pytest are clean on
`build/examples/42_Functional_Error_Handling` (10 tests), and every
runnable script runs. Every checker claim in the prose was probe-verified
against the extracted tree: `func_a(1).unwrap()` draws the quoted
`unresolved-attribute` diagnostic ("`unwrap` is not defined on `Err[str]`
in union"), `.bind(str)` is rejected on both `Ok.bind` and `Err.bind`,
`isinstance(a, Result)` fails the checker and raises `TypeError` at
runtime, `parse(42)` fails, and `ValueError("x").__notes__` type-checks
(typeshed declares it unconditionally) and raises `AttributeError` at
runtime, as the prose says. The `@final` claims were probed both ways:
with `@final`, `case Err(error)` narrows the capture to `Exception` and
`isinstance(result, Err)` gives `Err[Exception]`; with `@final` removed,
the same probes degrade to `int | Unknown` and `Unknown | Exception`, so
"rules out a value that inherits from both, so the checker narrows ... to
a single class, whether you use `match` or `isinstance()`" is accurate on
ty 0.0.70. One repo-level note: the project memory
`ty-gaps-placeholder-and-err-narrowing` (item 2, "narrowing to `Err[E]`
loses `E`, `@final` does not help") is stale for this chapter; ty gained
that narrowing and the chapter's direct `case Err(error)` form is the
right one. Inbound anchors from 20, 39, 40, 41, 43, 44, 46, and 47
(`#a-result-type`, `#turning-exceptions-into-results`,
`#matching-on-the-error`, `#composing-with-bind`) all point at headings
this review did not touch. The six exercises match
`Solutions/42_Functional_Error_Handling.md` in number and content. The
teaching structure needed nothing moved: the chapter escalates cleanly
(untagged union, tagged union, manual composition, `bind()`, combining,
`@safe`, matching, notes), and the near-miss coverage (`.bind(str)`,
`isinstance` on the alias, `unwrap()` on the union) is unusually
complete. No live blocks remain: every finding had one defensible answer.

## Applied directly

- "Return the Error as a Value": "untagged spelling of a *sum type*" is
  now "untagged form"; "spelling" is on the banned list.
- Same section: "the two cases collide" after "If a successful answer
  were" is now "would collide" (subjunctive agreement).
- Total Function paragraph: "with nothing left for an exception to sneak
  out through" is now "with nothing left to escape as an exception"
  (stranded preposition).
- `composing.py`: cut the header comment "Composing functions that
  return Results, by hand.", redundant with the section title; comments
  explaining what/why belong in prose.
- "Composing With bind": "the `bind()` method on `Result`" is now "the
  two `bind()` methods in `result.py`", since the previous section just
  taught that `Result` is an alias with no runtime class, and the next
  sentence names two different behaviors.
- Same section: "Bind removes the boilerplate" is now "`bind()` removes
  the boilerplate" (function references use code form with parens).
- Monad paragraph: "What the word buys you is that the shape is
  reusable" is now "The word marks a reusable shape" ("buy" watch word
  plus a pseudo-cleft).
- "`.bind(str)` say," is now "say `.bind(str)`,".
- Teaching addition before `test_result.py`: the `is`-vs-`==` point is
  now stated ("The last assertion uses `is` rather than `==`, proving
  the same `Err` object came back and the lambda never ran"), since the
  short-circuit mechanism is otherwise shown only by its outcome.
- "Combining Multiple Results": dropped "already" from "Three inputs
  already cost three levels of nesting"; the escalation is carried by
  the next clause. Also "Testing confirms combining returns" is now
  "Testing confirms that `combined()` returns", matching the earlier
  "Testing confirms that ..." sentence and naming the function.
- `@safe` section: "changed its type" is now "changed its return type"
  (the parameter types are unchanged, as the same paragraph says).
- The standalone Decorators paragraph now opens "That chapter" instead
  of repeating the `[Decorators](14_Decorators.md)` link the previous
  paragraph already carries.
- Production-`@safe` sentence: "the distinction this chapter ends on"
  is now "the distinction that ends this chapter", and "a failure the
  caller can act on" is now "can handle" (two stranded prepositions;
  "handle" matches the conclusion's "no caller can reasonably handle").
- Notes section: "Whatever context it needs, it needs to be carrying:"
  is now "The exception must carry whatever context it needs:" (doubled
  "needs", dangling progressive).
- "the same argument the chapter opened with" is now "the chapter's
  opening argument" (stranded preposition).
- Final `__notes__` paragraph: "leaving the checker one class to narrow
  to" is now "so the checker narrows the `Result` to a single class"
  (stranded preposition); claim probe-verified as described above.

## Considered and declined

- **Exercise 1 names its new step `func_e()`, skipping `func_d`.**
  `func_d` appears nowhere in the book, so the skip is unexplained, but
  the rename is cosmetic and would drag `Solutions/` markers and prose
  along; possibly `d` was avoided for its visual similarity to `b`.
  Left as is.
- **"The returns Library" section has no listing.** Deliberately
  prose-only: `returns` is not a dependency, and the pinned 3.15 beta
  makes new third-party dependencies a known risk. The section's three
  claims (Success/Failure naming, `@safe`, do-notation) are accurate.
- **Naming Rust's `and_then()` in the monad paragraph.** A reader who
  knows Rust maps `Result`/`bind` onto `Result`/`and_then` immediately,
  but cross-language naming is outside the chapter's arc and the
  paragraph already generalizes to `Maybe` and async containers.
- **`matching_errors.py` redefines `parse()` instead of importing it
  from `safe_demo`.** Importing would hide the `@safe` decoration the
  section's point depends on seeing next to `reciprocal()`'s; the
  duplication is the clearer teaching choice.
