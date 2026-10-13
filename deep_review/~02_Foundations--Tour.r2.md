> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 02_Foundations--Tour (2026-10-13)

Nothing here needs your decision, so the file has no live blocks.
I read the chapter and its Solutions file against `deep_review_db.md` and `~02_Foundations--Tour.md`,
checked each claim against its listing on Python 3.15.0 and `ty` 0.0.86,
and probed what the listings leave unshown:
the attributes of an `Interpolation` (four, including `conversion`),
`Template.strings` against `Template.interpolations`,
`++count` and `count++`,
tie rounding in a format spec (`f"{0.5:.0f}"` is `0`),
`&` precedence against comparisons,
the `unresolved-reference` and `unsupported-operator` that the two `# type: ignore` lines suppress,
and which lines of `exercise_4.py` draw `N816` with the `noqa` comments removed (all four).
`tip verify-ch CH=02 ISOLATED=1` passes 27 of 27 before and after,
and `tip prose CH=02` reports no new hits.

## Applied directly

Chapter, corrections:

- "t-Strings": "prints the three parts of each one" implied an `Interpolation` has three attributes. It has four (`conversion` too). Now "the loop prints those three attributes".
- "t-Strings": "rejects an interpolated value that contains a single quote, the way `trouble` does above" read as `trouble` doing the rejecting. Now it says `safe()` raises a `ValueError`, and that `trouble` holds a quote.
- "Indentation and Blocks": "Indenting can nest as deeply as you like" is false (CPython stops at 100 levels). Now "Blocks can nest, each one indented further than the block that contains it."
- "String Literals": "The triple-quote syntax quotes everything" overstated it, since escapes still work inside triple quotes. Now "can span lines, and it keeps every newline it contains."
- "Numbers and Arithmetic": "An f-string's format spec rounds the same way" named f-strings two sections before they are taught. It now links `#f-strings` and says "later in this chapter".
- "f-Strings": `printf()` appeared twice in three lines. The first mention is now "the `%` operator".
- "String Literals": "One limit remains." plus the raw-string sentence became one sentence, and "a raw string's backslash still escapes the closing quote" became "keeps the quote after it from closing the string", since a raw string keeps the backslash.
- "Scripting vs. Programming": two clipped sentences ("aid you" / "hinder you") joined into one.

Chapter, teaching:

- "Booleans, None, and Truthiness": no chapter said that Python writes `&&`, `||`, and `!` as `and`, `or`, and `not`, though `truthiness.py` uses `not`. Added, with the near-miss a Java reader writes: `&` and `|` accept `bool` values but bind more tightly than a comparison, so `x > 0 & y > 0` means `x > (0 & y) > 0`. A separate sentence says `not` always produces a `bool`, before the `and`/`or` paragraph.
- "Numbers and Arithmetic": after "no `++` or `--`", the trap: `++count` parses as two unary pluses and changes nothing, while `count++` is a syntax error.
- "String Literals": a new paragraph explains the empty `#:` lines around both triple-quoted outputs in `strings.py`: the newlines after the opening quotes and before the closing quotes belong to the string.
- "t-Strings": the `('', ' scored ', '%')` output had no explanation. A new paragraph says `strings` holds the literal text with one entry more than `interpolations`, so a template that opens with a value opens with `''`. Iteration became its own paragraph.
- "t-Strings": `shout()` calls `format()` with the `Interpolation`'s format spec, and the prose never said so, though Solutions exercise 5 turns on it. One sentence now says why `score` still prints as `92`. `safe()` moved to its own paragraph, opening "puts the same separation to work".

Solutions:

- Exercise 4: "Ruff's PEP 8 checks report `N816`" is true only because this repo's `pyproject.toml` selects `N`; ruff's defaults leave pep8-naming off, so a reader elsewhere sees nothing. The solution and the hint now say so.
- Exercise 1: "that is the one line on which the exercise's check turns" became "the exercise's check depends on that one line".

## Considered and declined

- **A listing for the `&` precedence trap.** One prose sentence with the parenthesized reading carries it; a listing would add a second topic to `or_fallback.py`.
- **"Python code from any two authors therefore lines up the same way."** Indent width is still a choice, but the four-space convention appears two paragraphs earlier, and the sentence is about brace placement.
- **The `int`-to-`str` digit limit beside "unlimited precision".** True of 3.11 and later, irrelevant at 31 digits, and a detour in a tour chapter.
- **Fewer `# noqa: N816` comments in `exercise_4.py`.** Ruff flags every one of the four lines, so each comment is needed.

## For the session

- Nothing in another chapter needed a fix.
- `tip prose CH=02` printed one stale `internal_names` baseline entry, `Examples/15_Techniques--Context_Managers/banner_cm.py::banner.title`. It belongs to chapter 15, likely from another agent's edit in this sweep.
- `tip reflow CH=02` failed with `OSError: [Errno 22] Invalid argument` on the chapter path, probably a file held by a parallel agent. `verify-ch` reflowed the chapter, so nothing is left unreflowed.
