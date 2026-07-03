# Features to introduce: all resolved

Every item from the original list is now introduced or linked.
Chapter numbers below reflect the current numbering.

## Resolved by adding new sections to Static Typing (08)

- **PEP 695 type parameters**: new section "Generic Functions and
  Classes" (`generics.py`, `generic_box.py`), covering `def f[T]`,
  `class Box[T]`, bounds, the pre-3.12 `TypeVar` spelling, and a
  pointer to the `[**P, R]` form in Decorators (15). First-use sites
  now link back: Functional Error Handling (14) and Decorators (15).
- **`type X = ...` alias statement**: new section "Naming Types: The
  `type` Statement" (`type_aliases.py`). Pattern Matching (13) links
  back at its first use.
- **`typing.Self`**: new section "The `Self` Return Type"
  (`self_type.py`). Its true first use is Context Managers (16),
  which now links back. Simulation (35) also uses it.

## Resolved by brief expansions at first use

- **`@cache` / `functools.cache`**: Singleton (23) now explains
  memoization before the cached-factory example.
- **`dataclasses.field` / `default_factory`**: Data Classes as
  Types (12) now explains the shared-mutable-default problem (with a
  link to Functions (05)) after the `Months` example.
- **`StrEnum`**: State Machines (26) already explains it well; added
  a link to the `Enum` introduction in Data Classes as Types (12).

## Already resolved before this pass (list was stale)

- **Walrus operator `:=`**: introduced in Control Flow (04).
- **`typing.TYPE_CHECKING`**: explained at its first use in
  Simulation (35), alongside the circular-import motivation.
- **`functools.wraps`**: Functional Error Handling (14) forward-links
  to Decorators (15), which explains it fully.
- **`itertools.count`**: shown and explained in Iterators (27),
  "Reusable Algorithms."
