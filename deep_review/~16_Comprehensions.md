[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/16_Comprehensions.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers
validate, `ty` (0.0.70) and `ruff` are clean on
`build/examples/16_Comprehensions`, and every script runs. The chapter's
checker claims were re-probed against the pinned ty 0.0.70, since the
map/filter listings were last rewritten for 0.0.63's behavior change:
`filter()` with a `lambda` predicate still does not narrow (revealed
`list[int | str]`, and `e ** 2` is an `unsupported-operator` error, so
both `# type: ignore` comments are still required and neither is flagged
unused); a named predicate returning `TypeIs[int]` narrows to
`list[int]`; `filter(None, ...)` narrows `list[int | None]` to
`list[int]`; and the comprehension's `if isinstance(e, int)` narrows.
One claim was slightly too strong: a `TypeGuard[int]` predicate also
narrows under 0.0.70, so "only ... `TypeIs[int]`" excluded a form that
works (fixed below; chapter 8's narrowing table teaches both). Runtime
probes on 3.15.0b4 confirmed every `SyntaxError` claim verbatim:
`assignment expression cannot rebind comprehension iteration variable
'e'`, `assignment expression within a comprehension cannot be used in a
class body`, `[x for x in xs if a else b]` (`invalid syntax`), and
`sum(n * n for n in nums, 0)` (`Generator expression must be
parenthesized`), while the parenthesized form and the PEP 798 async
unpacking form both compile. No findings met the bar for a live block.

## Applied directly

- map/filter section: merged the bracket-visibility point ("its
  brackets show at a glance that it produces a list") into the
  readability paragraph and cut the leftover paragraph that re-opened
  readability after the typing discussion; its other sentence repeated
  "inlines the test and the expression".
- Narrowing claim: added `TypeGuard[int]` beside `TypeIs[int]`; the
  probe showed both narrow `filter()` under ty 0.0.70, so "only ...
  `TypeIs[int]`" was too strong.
- Removed `str.join()` from the genexp-consumer list and added why it
  does not belong: it needs two passes (size, then fill), so it
  converts its argument to a list first, and a generator expression
  saves nothing over a list comprehension there. The old sentence's own
  criterion ("does not need them all at once") excluded it.
- Generator Expressions: added the no-tuple-comprehension note
  (parentheses make a generator expression; `tuple(...)` when you need
  a tuple), the natural misreading of the fourth delimiter.
- Added exercise 7 with its solution: move `any()` above `sum()` in
  `spent_generator.py` and predict all three outputs. It teaches
  partial consumption (`any()` stops after `5`, `sum()` continues from
  `6` and gives `230`, not `285`), the one generator behavior the
  chapter states but never shows, and the Generator Expressions
  section previously had no exercise. `SolutionsCode/` gained the
  generated `exercise_7.py`.
- Prose: "never spends" is now "avoids"; the second "Nothing stops you"
  opener is now "You can nest ..."; "is never assigned or used" is now
  "If nothing assigns or uses"; "No computation happens" is now "No
  computation runs"; dropped "ever" from "without ever building"; "It
  runs once, and once something consumes" lost its double "once"; both
  "never needs them all at once" are now "does not need them all at
  once"; "the values they ask for" is now "the values the consumer
  pulls" (stranded preposition, and "pulls" matches the section's
  vocabulary).

## Considered and declined

- The anatomy bullets say "input sequence" though any iterable works:
  "Feeding the Iterator Clause" widens the term deliberately, and the
  figure names the same parts as the bullets.
- The async-generator aside (`(*a async for a in agen())`) uses `async
  for` before the book teaches it: it is a one-line existence note
  closing the PEP 798 coverage, and a link or explanation would
  overweight it. Verified it compiles on 3.15.0b4.
- "the question was never asked" keeps its "never": the point is that
  `any()` examined nothing, and "was not asked" weakens it.
- `filtering.py`'s `if __name__ == "__main__":` guard goes unexplained
  locally: `mapping.py` imports it, the idiom is taught in Modules and
  Packages, and the book uses it without comment elsewhere.
- Mentioning `dict(zip(names, values))` in "Feeding the Iterator
  Clause": the section already shows `zip()`, and the dict-building
  ground is covered by `invert_dict.py` and `set_dict_from_genexp.py`.
