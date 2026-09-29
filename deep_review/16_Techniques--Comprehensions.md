> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 16_Techniques--Comprehensions (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I checked each claim against its listing, the sections it links (04, 08, 15, 19, 23, 28, 40, 45), the committed `#:` markers, and the figure's labels.
Probes on the pinned interpreter covered the walrus restrictions, the `if`/`else` position rule, the two-argument `sum()`, the parenthesized `path_walk_comprehension.py`, `rglob()`, class-body scope, and the async unpacking form.
A `ty` 0.0.84 probe confirmed the narrowing paragraph: `filter()` with a `lambda` leaves `filter[int | str]`, a `bool` predicate leaves `list[int | str]`, `TypeIs[int]` and `TypeGuard[int]` both give `list[int]`, and `filter(None, ...)` drops `None`.
Pyright 1.1.414 reveals `list[Unknown]` for `a_list`, as the chapter says.
`tip verify-ch CH=16` passes 24 of 24, and `tip prose` and `tip spell` are clean on both files.

## Applied directly

Chapter, corrections:

- "Scope and the Walrus Operator": the chapter counted two walrus uses that are a `SyntaxError`. There are three. A walrus in the iterable expression after `in` is the third ("assignment expression cannot be used in a comprehension iterable expression"). Now "Three uses", with the third named.
- "Generator Expressions": "No computation runs until you pull a value" contradicted the later section, where creating the generator evaluates the outermost iterable. Now "The generator computes no square until you pull a value."
- "Comprehensions Build, Loops Execute": "a list built and immediately discarded" did not match `comprehension_side_effects.py`, which keeps the list in `wasted` and prints it. Now "a list that no code can use."
- "A Generator Expression Runs Once": "`genexp_consumers.py` iterates `nums` three times because `range` is re-iterable" read as the cause of the iterating. Now "can iterate".
- First bullet list after the figure: the output expression "squares it and appends it to the output list", but the expression only squares. Now "squares it and the result joins the output list."
- `cube_if_even` in prose became `cube_if_even()`, per the function-reference convention.
- The `map(str.strip, lines)` sentence joined its example with a comma. Now a colon.
- "Breaking Up a Complex Comprehension": "in one pass" ended two consecutive sentences. The second is gone.

Chapter, teaching:

- "Scope and the Walrus Operator": added the class-body trap. A comprehension in a class body cannot read the class's other attributes (`[n * base for n in range(3)]` raises a `NameError`), and the outermost iterable is the part that can (`[n for n in range(base)]`). The section names a class body for the walrus and had left the commoner trap unsaid. No other chapter covers it.
- After `flatten_wrong_order.py`: added the near-miss. The `NameError` appears only when no `row` exists in the enclosing scope. `identity_matrix.py`'s `for row in matrix:` leaves one behind, and then the backward comprehension produces a wrong list with no exception (probe: `[9, 9, 9]` from a stale `row = [9]`).
- "The Gap Between Creation and Consumption": added the link to chapter 28's late-binding trap, whose `late_binding.py` is a comprehension of lambdas. The generator expression's late read of `factor` and the lambda's late read of `n` are one mechanism.
- Lead-in sentences for four listings that had none: `a_list.py`, `map_and_filter.py`, `path_walk_comprehension.py` (which now says what `Path.walk()` produces, a fact the listing's three-name target depends on), and `comprehension_steps.py`.
- Exercise 8, on `genexp_timing.py` with brackets. "The Gap Between Creation and Consumption" is the chapter's sharpest trap and had no exercise. Added at the end, so no existing number moves.

Solutions:

- Exercise 8's solution, `exercise_8.py`, with markers checked by the gate.
- Exercises 1 through 7: each solution does what its exercise asks, and each prose claim matches its listing. No changes.

## Considered and declined

- `flatten_wrong_order.py` keeps its `try`/`except NameError` instead of `expected()`. pyflakes suppresses `F821` for the undefined `row` only inside a `try` that catches `NameError`.
- The comments inside `path_walk_comprehension.py` and `unpacking_comprehensions.py` explain what the code does, which new listings put in prose. They are existing comments and stay.
- A listing for the class-body trap. It would need `expected(NameError)` around a class statement and would give the section a third topic. The prose states the two cases, and both were probed.
- Exercise 2 changes one literal. It is small, but it confirms the reader found the conditional expression, and the chapter's other exercises carry the weight.
- "earns its place" appears twice ("A comprehension earns its place", "`walk()` earns its place"). It is a figure of speech, but it is your phrase and reads clearly in both places.
- The verbless sentences in "Choosing a Form" ("Brackets when you want a list.") are a deliberate rhythm for a closing list. Left as written.
