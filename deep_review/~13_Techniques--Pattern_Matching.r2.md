> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 13_Techniques--Pattern_Matching (2026-10-13)

No live blocks: every finding had one sensible answer, so it is applied below.
I checked each claim against its listing and against runtime probes on `uv run python` 3.15.0, `ty` 0.0.86 probes, and `ruff --select ALL`.
Every quoted `SyntaxError`, `TypeError`, and `AssertionError` message matches what 3.15.0 prints, the `frozendict` built-in sub-pattern works, and both quoted `ty` diagnostics in the Solutions file match `ty` 0.0.86 on an edited copy, line and column included.
All 14 chapter listings and 6 Solutions listings print their `#:` markers when run directly.
`tip verify-ch CH=13 ISOLATED=1` passed 27 of 27 before the edits and 27 of 27 after (one intermediate run failed `solutions-drift` on chapter 16's `exercise_9.py`, another agent's edit in progress, and passed on the rerun).
I read the previous review (`~13_Techniques--Pattern_Matching.md`) and `deep_review_db.md` and re-proposed nothing from either.

## Applied directly

Chapter, corrections:

- "A Bare Name Captures": "neither `ty` nor `ruff` reports it" was false for this book. `ruff`'s pep8-naming rule N806 flags `case DEFAULT:` ("Variable `DEFAULT` in function should be lowercase"), and `pyproject.toml` silences it for `value_patterns.py`. Now: `ty` accepts the capture; `ruff` flags it only through N806, whose message is about naming style and which a lowercase constant escapes; the book's configuration turns N806 off for the listing because the capture is its point.
- "Exhaustive Matching": "`assert_never()` ... reports the error at the `match`" now says at the `assert_never()` call inside the `match`, and "the function's signature" became "the function's return type", which is where `ty` points the `invalid-return-type` diagnostic (probed).
- "A Bare Name Captures": "rebinds `DEFAULT` as a local name" suggested the module constant is rebound. Now "binds it to a local name `DEFAULT`", which the next clause's "leaves the module-level constant untouched" then confirms.
- "Keyword Patterns": "work on an instance of any class with the named attributes" read as duck typing (any object with an `x` matching `Point(x=0)`), which is false: the class test still applies. Now says the pattern reads each attribute directly, so it needs no `__match_args__` and works with any class.

Chapter, teaching:

- "Alternatives and Capture": added the near-miss a reader brings from `if` conditions. `case "up" or "u":` fails with a bare `SyntaxError: invalid syntax` (probed), a message that does not point at `|`.

Chapter, prose:

- Opening sentence: `match` "runs the first one that fits" said the pattern runs. Now it runs the body of the first `case` whose pattern fits.
- "Guards": the long paragraph held two explanations (leftover bindings after a failed guard, with the `leaky()` walk; the partial-failure caveat and the advice). Split at the seam, and the new paragraph opens with its noun ("A failed guard always leaves its bindings, because ...") instead of "That holds".
- "Mapping Patterns": "dataclass" twice in prose became "data class", the chapter's word everywhere else.
- "The Expression Problem": the sentence carrying the flagged `assert_never()` calls and the two `Webhook` cases split in two.

Solutions:

- Exercise 5: cut the closing "Give every path a return" paragraph, which repeated the paragraph above the first listing (unreachable `case _`, `sign()` typed `int`, `invalid-return-type`).
- Exercise 6: "more verbose than the dotted name, but it is what you want when the test is more than equality" did not say why the guard's `is` qualifies. Now: a value pattern always compares with `==`, a guard holds any expression (`is`, a membership test, a call), so choose the guard when the test needs one of those.
- Exercise 1 hint: "star pattern" became "starred name", the chapter's term.
- Exercise 3 hint: "can itself be a pattern" became "The value position in a mapping pattern holds a pattern, so it can hold another mapping pattern".

## Considered and declined

- **`STATUS.get(status) or f"..."` instead of `STATUS.get(status, f"...")`.** The prose already explains the `or` and its falsy-value caveat, and the listing-design passes have settled the listing.
- **Exercise 3's "each event fits only one of them".** An event carrying both `"at"` and top-level `"x"`/`"y"` fits both cases, and the nested one wins. That event is malformed, and naming it would distract from the point about the two shapes.
- **Cut the `ruff` remark entirely instead of correcting it.** Close call. The correction keeps the useful fact (a naming linter gives a clue for uppercase constants only), and the reader who runs `ruff` on the repo's `Examples/` would otherwise see the per-file ignore and wonder.

## For the session

- `tip positional` reports one NEW hit, `Chapters/13_Techniques--Pattern_Matching.md:154`, "the last `case`". It is the sentence whose `ruff` clause I corrected; the same phrase was already accepted (now stale) in the old wording. It names the rule's condition, not a line in the listing, so it is an accept.
- `tip watch-words` and `tip positional` list stale Solutions entries for the sentences I rewrote or cut (exercise 5's closing paragraph, exercise 6's guard sentence, exercise 3's hint).
