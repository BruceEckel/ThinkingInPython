# Review: Chapter 04 (Functions)

Clean progression: definition, dynamic typing, defaults and keyword args, the
mutable-default trap, `*args`/`**kwargs`, positional-only and keyword-only,
unpacking, lambdas. Every example runs and matches its prose.

## Should fix

1. **`def sum(...)` shadows the builtin (lines 43-50).**
   The `sum.py` example defines `sum`, hiding the builtin of the same name. This
   is the same shadowing pattern as `list` in chapter 03, and the book elsewhere
   advises against it. Consider renaming to something like `add` or `concat`. The
   point (one function, both ints and strings) survives the rename.

2. **Mixed quote styles in one call (line 49).**
   `print(sum('spam ', "eggs"))` uses single quotes for the first argument and
   double for the second. The book otherwise uses double quotes. ruff would not
   flag this (the quote rules are not in the active set), so it stays inconsistent
   silently.

## Nits / optional

3. **Redundant mutable-default explanation (lines 71-73 and 95-97).**
   The "evaluated once at definition time, shared across calls" point is made
   before the example (71-73) and then again after it (95-97) in nearly the same
   words. Consider keeping the short setup before and trimming the after-paragraph
   to one new sentence, or vice versa.

4. **Lambda assigned to a name (line 179).**
   `square = lambda n: n * n` is the E731 anti-pattern, which the comment honestly
   flags ("Usually prefer def"). Worth knowing: ruff does not catch it here
   (E731 is not active in the project config), so this reads as a deliberate
   teaching example only because of the comment. Fine to keep; just noting the
   gate will not enforce the advice.

5. **"comprise a single expression" (line 183).**
   Slightly off idiomatically. Consider "because they are limited to a single
   expression".

6. **"enforces type constraints at runtime" (line 24).**
   Python does very little type enforcement (duck typing); errors surface when an
   operation is unsupported, not from a type check. Consider softening, for
   example "type errors surface at runtime rather than at compile time".

## Verified

- Ran all nine scripts (`a_function`, `flexible_args_and_returns`, `sum`,
  `default_args`, `mutable_default`, `var_args`, `param_markers`, `unpacking`,
  `lambdas`). Every output matches the prose and inline comments, including the
  mutable-default contrast (`[1] / [1, 2]` vs `[1] / [2]`) and the
  sort-by-length result.
- Function-paren convention applied (`sorted()`); `dict.get(key, default, /)` is
  shown with its signature, correctly left as is.
- The intentional bad patterns (`target=[]`, the name-shadowing) are not flagged
  by ruff, which matches their teaching purpose.
