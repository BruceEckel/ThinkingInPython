> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 02_Foundations--Tour (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I checked each claim against its listing, against the chapters it links (1, 3, 4, 7, 8, 14, 16, 34), and against the pinned interpreter (3.15.0rc2) and `ty` 0.0.84 with scratch probes:
the `TabError` cases, raw strings that end in one and two backslashes, tie rounding in `round()` and in a format spec, `Template` iteration skipping empty strings, and the `unresolved-reference` that `unbound_val.py` suppresses.
`tip verify-ch CH=02` passes 24 of 24, and `tip verify` and `tip exercise-refs` pass over the book.

## Applied directly

Chapter, corrections:

- "Strings": "A raw string cannot end with a backslash" is false for `r'abc\\'`, which is legal and holds both backslashes. Now "a single backslash".
- "Common String Operations": "`in` tests membership" undersold what the listing does. `"World" in s` is a substring test. Now "`in` tests for a substring", and the stray "also" is gone.
- "Indentation and Blocks": "The `if` never runs" is wrong, since the test runs and the body does not. Now "The body of the `if` never runs".
- "Indentation and Blocks": "`print()` sends its argument" became "its arguments ..., separated by spaces and followed by a newline". The next section prints two values at a time.
- "Variables and References": "You never declare a variable's type" contradicted `message: Template` and `parts: list[str]` later in the chapter. Now "Python does not require you to declare".
- "Variables and References": "as `a` and `b` do in `references.py`" had no verb to attach to. Now "as `a` sees the `4` appended through `b`".
- "Numbers and Arithmetic": "as C does" now names C's `round()`, since C's `printf()` rounds ties to even too.
- "Booleans, None, and Truthiness": the conditional-expression link gained its anchor, `#conditionals`.
- "How to Read the Examples": "the filename first line" is now "the filename comment on a listing's first line".
- "Naming Conventions": the PEP 8 link used the retired `python.org/dev/peps` address. Now `peps.python.org`, as in every other chapter.

Chapter, teaching:

- `arithmetic.py` is split. The augmented-assignment lines moved to a new `augmented.py`, which sits after the "no `++`" paragraph and directly above the paragraph about in-place `+=`. It gained the other half of the lookalike pair, `items = items + [4]`, so the listing shows `alias` keeping the old list. The prose had only asserted it.
- `arithmetic.py` gained `round(0.5), round(1.5), round(2.5)`. The tie-to-even paragraph had no output behind it, and `round(3.14159, 2)` is not a tie.
- `truthiness.py` is split. The `or` lines moved to a new `or_fallback.py` beside the paragraph on `and` and `or`. It gained an `and` line (`items and items[0]` on an empty list), since the prose claims both operators return an operand and showed only `or`, and the `None` test that keeps a legal `0`, which the prose recommended without running.
- New `concatenate.py` in "Common String Operations": `"total: " + total` raises a `TypeError`. A Java or JavaScript reader writes that line first, and the chapter went from string methods to f-strings without saying why the conversion is needed.
- "Indentation and Blocks": added line continuation inside an open parenthesis, bracket, or brace. No chapter covered it, and `tstrings.py` wraps four calls that way.
- "Indentation and Blocks": one sentence says what the `try` and `except` in `unbound_val.py` do, with a link to chapter 4. It is the book's first `try`.
- "Booleans, None, and Truthiness": `Bucket` is the book's first class and first type hints, five chapters before either is taught. Two sentences now name both and link chapters 7 and 8.
- "Variables and References": one sentence names `copy.deepcopy()` after the shallow-copy demonstration, which left the reader asking how to copy the inner lists.
- "Strings": one sentence says what the `r` prevents in `strings.py`. Without it `\u` starts a Unicode escape and the literal is a syntax error.
- Exercise 4 names `augmented.py` as the home of `total`.

Solutions:

- Exercise 4: `exercise_4_constants.py` was not the rename the exercise asks for. It assigned `TOTAL_SUM = 5` once and dropped the `+=`. It now renames all four lines, so the listing shows a "constant" changing on its second line while `ruff` and `ty` stay silent. The prose says so, and it names `total` and `flags` where it had named `total_sum` and `flag_bits`, which appear in neither the chapter nor the exercise.
- Exercise 5: "no rule can tell the first word from the second" overstated it, since a rule that quotes the first match gets this case right by luck. Now "nothing in it says which of the two words is the value."
- Exercise 1: the two column-aligned comments take the two-space form the chapter listings use.

## Considered and declined

- **Strip the type hints from `truthiness.py` and `tstrings.py`.** Chapter 1 says the early chapters "mostly omit type hints", and chapters 3 to 5 do. Here `message: Template` and `parts: list[str]` tell the reader what a t-string evaluates to, so the hints stay and the new pointer explains them.
- **An exercise on the `x or default` trap.** `or_fallback.py` now runs both forms side by side, so an exercise would repeat the listing.
- **`expect()` in `unbound_val.py` and `concatenate.py`.** The helper is defined in chapter 15 and takes a callable. A `try` that prints the message is the form chapters 3 and 4 use.
- **"F-strings replaced them."** It follows "Both still work" and reads as a contradiction for a moment, but the paragraph is about what existing code carries, and the sentence closes it.
- **The length of the t-strings section.** It is the longest section in a tour chapter, with two consumers in one listing. Chapter 34 links to it by anchor and builds on `shout()` and `safe()`, and exercise 5 asks for a third consumer, so both stay.
- **"Scripting vs. Programming".** No later section depends on it. It is the chapter's statement of what Python is for, in your voice, and it stays.
