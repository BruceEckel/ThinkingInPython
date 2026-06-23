# Review: Chapter 03 (Containers and Control Flow)

Solid coverage of the core containers and control flow. All sampled examples run
and their outputs match the prose. A handful of real issues, mostly in the first
example and a couple of grammar slips.

## Should fix

1. **First example shadows the builtin `list` (lines 11-23).**
   `list = [ 1, 3, 5, 7, 9, 11 ]` names a variable `list`, hiding the builtin.
   The prose then says "creates a `list`" and "adds new elements to a `list`",
   which blurs the variable and the type. This is the kind of thing the book
   warns against, and it is the very first container example. Suggest renaming to
   `numbers` (or `xs`, to match the slicing example). Note also the inner-bracket
   spacing `[ 1, 3, ... ]` is unlike the rest of the book (`[10, 20, 30]`); ruff
   does not flag it, so it stays inconsistent silently.

2. **Dead expressions in tuples.py (lines 67-68).**
   `tuple([1, 2, 3])` and `tuple("abc")` are bare expressions. Their results are
   discarded, so they print nothing, yet the comments suggest output. I confirmed
   the script prints only `3 4 / 1 / 1 9`. Wrap them in `print(...)`. The first
   comment also reads awkwardly and has a double space: "Converts to (1, 2, 3)
   from a list"; "`print(tuple([1, 2, 3]))  # (1, 2, 3) from a list`" or similar.

3. **Orphaned sentence and dangling colon (line 158).**
   "Python's comparison operators chain the way they do in mathematics:" ends with
   a colon but is followed by prose about `while`, not an example. The chained
   comparison was already shown at line 153 (`print(0 < x < 10)`). Either delete
   this line or merge the point into the conditional-expression discussion above.

4. **Number agreement (line 222).**
   "an exception propagates up the call stack until they find a handler": singular
   subject, plural verb. Use "until it finds a handler".

5. **"if expression" (line 137).**
   An `if` is a statement, not an expression (the conditional expression `a if c
   else b` is the expression form). Suggest "add `elif` to an `if` statement".

## Nits / optional

6. **Comment capitalization inconsistency (line 302).**
   `# with a filter` stays lowercase while its neighbors are `# List comprehension`
   / `# Dict comprehension` / `# Set comprehension`. The capitalization tool
   skipped it because "with" is in its keyword list, but here it is ordinary
   prose. Consider `# With a filter` (manual, the tool will not do it).

7. **"creates an iterator `x`" (line 23).**
   `x` is the loop variable bound to each item, not the iterator (the iterator
   over the list is implicit). Minor wording.

8. **Wordy opener (line 4).**
   "the essential nature of containers for programming is acknowledged by building
   them into the core of the language" could be tightened, for example "Python
   builds them into the core of the language."

## Verified

- Ran `slicing`, `tuples`, `sets`, `set_methods`, `comprehensions_intro`: all
  outputs match the prose; set orderings print as shown.
- Confirmed `tuples.py` lines 67-68 produce no output.
- ruff passes, but does not catch the bracket spacing or the builtin shadow in
  `list.py` (neither rule is in the active set).
- Function-paren convention applied (`append()`, `range()`, `enumerate()`,
  `zip()`, `print()`, `isdisjoint()`, `read_text()`/`write_text()`).
