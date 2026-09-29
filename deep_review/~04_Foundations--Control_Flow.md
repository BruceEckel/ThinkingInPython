> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 04_Foundations--Control_Flow (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I ran all 19 extracted listings and the nine solutions against their `#:` markers,
and probed the claims the markers do not cover on the pinned 3.15.0rc2:
the `SyntaxWarning` text from `finally_swallows.py`,
the three `__cause__`/`__context__`/`__suppress_context__` states behind the chaining table,
`"²".isdigit()` against `int("²")`,
the walrus rewrite of `while_true.py`,
and `pathlib.Path.read_text()`'s source.
I read the sections the chapter links in chapters 03, 08, 10, 13, 15, and 16.
`tip verify-ch CH=04` passes 24 of 24.

## Applied directly

Chapter, corrections:

- "Loops", before `while_true.py`: the prose said the test "belongs at the bottom of the body",
  but the listing tests between the `pop()` and the addition.
  Now "in the middle or at the bottom", with a sentence after the listing saying where the test sits and why.
- "Mutating a Container While Looping": "[Containers] hit it while removing from a list" was past tense
  and credited chapter 03 with half of what it shows.
  Chapter 03 has both `remove_while_iterating.py` and `dict_iteration_trap.py`, so the sentence now names both.
- "Context Managers", last sentence: `read_text()` and `write_text()` handle a whole file in one call,
  which the sentence left out and exercise 8 depends on.
- "Comprehensions": "from another sequence" is now "from an iterable", the term the Loops section uses.

Chapter, teaching:

- Walrus near-miss: the listing parenthesizes `(n := len(text))` and the prose did not say why.
  Without the parentheses `n` is bound to the comparison's result, `True`. Added after the listing.
- `try`/`else`: the chapter said when `else` runs, not why you would use it over more lines in the `try` block.
  Added the reason: an exception from the `else` code is outside the handlers' reach.
  Probed: a `ValueError` raised in `else` escapes the `except ValueError` above it.
- `nested_break.py`: the prose names `return` as one way to leave two loops,
  then demonstrates the `else` technique inside a function, where `return` is shorter.
  Added a paragraph saying `locate()` is a function only to run two searches, and when the `else` form applies.
- "Context Managers": tied `with` to the `try`/`finally` cleanup the previous section taught.
- "Comprehensions": the section ended on its listing, with no account of the syntax and no pointer onward.
  Added the order of the parts, what the delimiters choose, and the link to chapter 16.

Solutions:

- Exercise 6: "for three of them the name `evens` holds an empty list" was false.
  `evens` is empty only until the first iteration appends `0`. Now "holds a partial result".
- Exercise 8: the third case for `with` ("when you are writing rather than reading and the failure case matters")
  did not answer an exercise about the reading half, and implied `read_text()` lacks the closing guarantee.
  `read_text()` opens the file in a `with` block of its own. The paragraph now says so.
- Exercise 5: "falls through to `case _`" contradicted the chapter's "a `case` does not fall through".
  Reworded, along with "and nothing else" and "somewhere to land".
- Exercise 7: "`joining_line()` looks at nothing else" misdescribed the function, which searches the formatted traceback.
  Now says Python builds that traceback from `__cause__`.
- Exercises 1, 6, and 9: removed "exactly when", "exactly why", "at all", and three italics used for emphasis.

## Considered and declined

- **"Mutating a Container While Looping" repeats chapter 03.**
  Both failures appear one chapter earlier with near-identical listings.
  The section adds the comprehension fix and carries exercise 9, so I left it and corrected the credit.
  I tried adding the dictionary fix (`for name in list(ages):`) to the listing.
  The failed loop leaves `"a!"` behind, so the fixed loop's output needs its own explanation, and I dropped it.
- **PEP 758's unparenthesized `except ValueError, TypeError:`.**
  Valid on 3.14 and later without `as`. The chapter's example uses `as e`, which still requires the parentheses,
  and no listing in the book uses the new form.
- **`placeholders.py` writes `...` on its own line** while the prose says you normally write it on the signature's line.
  The listing shows `...` as a statement beside `pass`; the link to chapter 08 shows the stub form.
- **`from None` sets `__suppress_context__`.** Every `from` sets it, including `from e`.
  The sentence is true as written, and the fuller account is in the solution to exercise 7.
- **The chapter's "never" and "only".** Each draws a real contrast. Left as written.
- **Comments in `walrus.py` and `comprehensions_intro.py`** that explain rather than label. Pre-existing, so left alone.

## For other chapters

- `Chapters/B_An_Effect_Checker.md` links "[walrus operator](04_Foundations--Control_Flow.md)" with no anchor;
  `#the-walrus-operator` exists.
- `Chapters/02_Foundations--Tour.md` links "[conditional expression](04_Foundations--Control_Flow.md)" with no anchor;
  `#conditionals` is the section that introduces it.
