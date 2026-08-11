[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/02_Tour.md` in the clean-slate
sweep. The mechanical layer is sound: all `#:` markers validate, ruff and
`ty` are clean on `build/examples/02_Tour`, and all ten scripts run. The
technical claims were re-verified: `-7 // 2` is `-4` and `-7 % 2` is `1`
(with the C/Java contrast stated correctly), `round()` and format-spec
half-to-even behavior, `~x` as `-x - 1`, `bool` as an `int` subtype, raw
strings not ending in a backslash, and `Template` iteration skipping empty
literal strings. The intro's tour list matches chapters 03 through 10
exactly, the five exercises line up with `Solutions/02_Tour.md`, and the
four inbound anchors other chapters use (#indentation-and-blocks,
#variables-and-references, #naming-conventions, #t-strings) are untouched
by the edits below. The one structural change: the chapter's first listing
used to appear before "How to Read the Examples" explained its notation,
and its explanation sat two sections later; the pieces now sit together.

## Applied directly

- Moved "How to Read the Examples" above the first listing, and moved the
  "Python is clean to write" paragraph plus `if.py` from "Scripting vs.
  Programming" into the top of "Indentation and Blocks". The notation is
  now explained before the first listing that uses it, and the section
  that walks through `if.py` now contains `if.py`. No other chapter links
  to the affected anchors, so the move costs nothing.
- "Indentation and Blocks": added "Binding still follows execution: had
  `response` not been `"yes"`, `val` would never have been assigned, and
  `print(val)` would raise a `NameError`." The no-new-scope paragraph
  otherwise leaves a reader thinking `val` exists unconditionally.
- "Numbers and Arithmetic": added the digit-separator sentence
  (`10_000_000`). Later chapters use underscore literals freely
  (`20_000`, `0.000_001`, `4_000`) and nothing taught them.
- Rewrote "both forms rebind, which is why `total += 5` above looks like
  augmented assignment in any other language" to "both forms rebind the
  name, so `total += 5` above behaves the way `+=` does in any other
  language". The old sentence said a `+=` looks like augmented
  assignment, which it literally is; the point is behavior.
- "Strings": added "In an ordinary string, a backslash starts an escape
  sequence, as in C and Java: `\n` is a newline and `\t` is a tab" before
  the raw-string paragraph. "You don't need to double them" presumed
  escape sequences, which no chapter states.
- "Booleans, None, and Truthiness": after `default if x is None else x`,
  added "That is a conditional expression, covered in
  [Control Flow](04_Control_Flow.md)." The form was used before being
  taught, and chapter 04 introduces it by name.
- Comma before "so" in "The subsequent statement is not indented, so it
  is no longer part of the `if`."
- Split "The built-in numeric types do not implement it but array
  libraries such as NumPy do" at the "but".

## A prediction exercise for negative floor division

The chapter's sharpest single fact for a C/Java reader is that `-7 // 2`
is `-4` and `-7 % 2` is `1`, and no exercise touches it. The five
exercises cover references, truthiness, f-strings, naming, and t-strings;
the Numbers section appears only via exercise 4's renaming task, which is
really about naming. A prediction exercise would make the reader commit
to an answer before running, which is where the C habit surfaces.
Proposed as exercise 6, with the matching solution added to
`Solutions/02_Tour.md`:

> 6. Before running anything, write down what C or Java would print for
>    `-9 / 4` and `-9 % 4` using integer math, then what Python prints
>    for `-9 // 4` and `-9 % 4`. Run `print(-9 // 4, -9 % 4)` and check.
>    State the rule that predicts the sign of the result of `%`.

Not applied because it grows the chapter's exercise set, and the listing
already demonstrates the fact with markers; whether it also needs an
exercise is a scope call. If accepted, I will add the solution block in
the same change.

[] Reject

## Considered and declined

- "It is marvelous for scripting, and you may replace all your batch
  files...": "may" reads as permission where "can" is plainer, but Bruce
  edited this exact sentence the day before this review (7ed66157), so
  the wording is a fresh deliberate choice.
- The opening trio ("Python exists to improve your productivity. The
  language aims to aid you as much as possible. It tries to hinder you as
  little as possible.") is clipped, but it survived the recent hedge and
  passive-voice passes and reads as voice, not accident.
- "It does not impose arbitrary rules or force a particular set of
  features" is vague about what "force a particular set of features"
  means, but any rewrite guesses at the intended claim; motivational
  heritage prose, left alone.
- `truthiness.py` and `bitwise.py` carry internal blank lines separating
  demo phases. The dense-listing rule names blanks between defs and after
  imports, but phase-separating blanks are the book-wide pattern in
  no-def listings, not a deviation.
- No closing section before Exercises: chapters 03, 04, and 05 share the
  same shape (last content section, then Exercises), so this is the
  tour-part convention rather than a missing conclusion.
- `python if.py` as the run command: chapter 01 prescribes no run-command
  style, so nothing to align with.
