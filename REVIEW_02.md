# Review: Chapter 02 (Tour)

Overall a clear, well-paced tour. Every example runs and every inline `# output`
comment matches what the script actually prints (I ran all eight). The notes
below are small.

## Should fix

1. **Non-ASCII hyphens (lines 324, 331, 332).** "all‑lowercase" (twice) and
   "run‑together" use U+2011 (non-breaking hyphen), not the ASCII `-`. This slips
   past every check: it is not CRLF, and the spell checker splits the word at the
   hyphen so both halves look fine. Replace the three with ordinary hyphens.

2. **Comment mis-capitalized (lines 135-136).** The two-line comment reads:
   `# Bitwise and shift operators on integers. Binary literals (0b...)` /
   `# Make the bit patterns easy to see.` "Make" is mid-sentence (the sentence is
   "Binary literals (0b...) make the bit patterns easy to see") so it should be
   lowercase "make". This is a `capitalize_comments.py` artifact: the trailing
   `(0b...)` ends in a dot, so the tool thought the sentence had ended and
   capitalized the next word. Worth a one-character fix, and a reminder that the
   capitalization tool can misfire after an ellipsis.

3. **Dated tooling (line 318).** It recommends AutoPEP8 and YAPF, but the book
   uses ruff (and `ty`) everywhere else. Suggest pointing at ruff instead, so the
   advice matches the toolchain the rest of the book describes.

## Nits / optional

4. **Oxford comma (line 304).** "identifiers, functions and file names" should be
   "identifiers, functions, and file names" to match the Oxford-comma style used
   elsewhere (for example line 4-5).

5. **Long sentence (line 13).** "while hindering you as little as possible with
   arbitrary rules or requirements that you use a particular set of features" is
   hard to parse. Consider splitting, for example: "It tries to hinder you as
   little as possible. It does not impose arbitrary rules or force a particular
   set of features."

6. **"the result" is vague (line 46).** "a `print()` statement which sends the
   result to standard output" sits next to `if.py`, which prints the literal
   "affirmative", not a computed result. Consider "sends its argument to standard
   output".

7. **Naming-term consistency (lines 304, 312, 328).** The chapter says
   "snake-case", `snake_case`, "pascal-cased", and "CapWords" for two concepts.
   Picking one spelling for each (for example `snake_case` and CapWords) would
   read more cleanly.

## Verified

- Ran `references`, `multiple_assignment`, `numbers`, `bitwise`, `truthiness`,
  `fstrings`, `string_methods`, `functions`: all outputs match the prose.
- The "don't shadow stdlib" filenames (`random.py`, `types.py`, `weakref.py`) are
  only mentioned here; no example file actually uses those names, so there is no
  contradiction.
- Function-paren convention is applied (`print()`, `printf()`). No docstrings to
  check. Comment-period and capitalization gates pass (aside from item 2, which
  the gate allows because it is a multiline comment).
