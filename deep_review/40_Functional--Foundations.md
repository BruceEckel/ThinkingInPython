> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 40_Functional--Foundations

Reviewed after the six prose passes (elements-of-style, literal, positive,
straighten, cohesion, antecedents), each committed separately on
`claude/prep-40`. No `~` file existed for this chapter; `deep_review_db.md`
was read and its standing rejections and exemptions honored (none name this
chapter). The prose pass ran without the global `~/.claude/CLAUDE.md` watch
list, which is not available in a cloud session; it used this skill's rules,
`banned_phrases.py`, and the repo's `CLAUDE.md` instead.

Every listing ran and matched its `#:` markers. Probed directly: `ty`
rejects `p.x = 5` on the `@record` `Point` (`invalid-assignment`, read-only
property) and accepts the `setattr()` form; with the `nonlocal` line deleted
`ty` reports `Name 'count' used when not defined`; with `placeholder.py`'s
ignores stripped `ty` reports `invalid-argument-type` on the `partial()` call
and `too-many-positional-arguments` (expected 0) on each `percent()` call;
`compose(label, increment_then_double)` reveals `(int, /) -> str`;
`partial(clamp, 0, Placeholder)` raises "trailing Placeholders are not
allowed"; `percent()` with no argument raises `TypeError`;
`getclosurevars(tally).nonlocals` after three calls is `{'count': 3}`, and
setting `cell_contents` rewrites the counter. Solutions 6's two quoted
diagnostics match `ty`'s current text. Every cross-chapter link and the
claims around it (44's `slope()`, 28's `late_binding.py`, 20's
`frozen_leaky.py`, 16's generator expressions) were checked against the
target.

## Applied directly

- Opening: "In the functional style you keep loops, classes, and mutation,
  notice ..." (a pass's rewrite) read as an instruction to keep mutation.
  Now "The functional style lets you keep loops, classes, and mutation. It
  asks you to notice ...", the original sense.
- Immutability in Annotations: "The constraint binds one side" punned on
  name binding in a paragraph about `Final` bindings. Now "covers only
  `total()`'s side".
- A Stable Hash: "Immutability offers ... a *stable hash*" contradicted the
  paragraph after it, where a mutable plain instance hashes by identity.
  Now "a *stable hash* of the contents". The follow-up sentence "Equality
  based on *contents* removes hashing, not mutability by itself" now reads
  "What costs a type its hash is contents-based equality, not mutability by
  itself."
- A Stable Hash: "That combination is why ..." lost its antecedent when the
  straighten pass split the `@record` sentence; now "Contents-based equality
  together with a stable hash is why ...".
- Higher-Order Functions: the lambda paragraph said "The higher-order
  functions in this section" one paragraph before the term is defined; now
  "The functions in this section".
- Higher-Order Functions, teaching addition: `sorted()` is now named as the
  pure counterpart of `list.sort()`, with a link to Containers, which
  teaches the in-place/`None` behavior. A chapter about not mutating inputs
  had the lookalike pair and never contrasted it.
- Higher-Order Functions: "`map(str.strip, lines)` reads better ... because
  the name says what the comprehension repeats" gave no clear reason. Now
  "because `str.strip` names the operation once, with no loop variable to
  invent."
- Higher-Order Functions: "A higher-order function can also work the other
  way around: instead of containing the loop, it wraps ..." now says what
  the other way is: it returns a function, the wrapper. That ties back to
  the definition's "returns one".
- Closures: "show the captured value" is now "values" (two closures);
  the `balance` contrast is now "`withdraw()` is unpredictable because every
  call changes the global `balance`; nothing changes `factor` after
  capture", replacing a sentence whose "it" had two candidates.
- Closures: cut "Only `increment()` can name that variable, so only
  `increment()` can change it", the second of three statements of the same
  privacy claim before the paragraph that calls it a convention.
- Closures, `nonlocal` paragraph: the `count += 1` sentence stated twice
  was merged into one ("makes `count` a fresh local variable, reads that
  local before anything has assigned it, and fails with
  `UnboundLocalError`"). The quoted runtime message moved mid-sentence to
  satisfy the `QUOTE-PUNCT` check the straighten pass had tripped.
- Partial Application: "where a lambda ... reads" is now "whereas".
- Placeholder: "rejects a *trailing* placeholder, for the opposite reason"
  named no first reason. Now "because it would do nothing", and the
  duplicate "The marker would add nothing." is cut.
- Solutions 1, 3, 4: the listings dropped the annotations the chapter's
  versions carry (`deposit()`, `multiplier()`, `compose()` and its stages).
  Annotated to match, with `compose[T, U, V]` as in `compose_functions.py`;
  `SolutionsCode/` synced.
- Solutions 2: the passive "is caught with `expected()`" (the file's one
  fixable Vale warning) is now active. The remaining "are unchanged" warning
  is a predicate adjective, left as is.

Pass-review reverts and repairs, for the record: literal's "The
comprehension returns a finished list" became "builds" (a comprehension
returns nothing), and its composition intro said "passes its result to the
next" twice; positive's "`Sequence[int]` is `total()`'s promise" became
"declares" (the skill's notes flag "promise"), its claim that the library's
loop is "the only place an off-by-one ... can occur" was an overclaim and
went back to "You stop rewriting the same loop, and with it ...", and its
"encapsulation from a closure in place of a class" went back to the
original wording; antecedents' "Staying fixed after capture is the
difference between ..." was rewritten (above).

## Immutability's cost: name the persistent-structure alternative?

Immutability, the cost paragraph ("That safety has a cost, and the cost is
copying. Python's immutable types share no structure ..."). The paragraph
states the cost and stops. A reader who has used Clojure, Scala, or
Immutable.js knows the standard answer, persistent data structures that
share unchanged parts, and will wonder whether Python has one. The standard
library does not; third-party packages (`pyrsistent`) do. Proposed: one
sentence after "That time and memory are the price of sharing without
coordination.": "Languages built around immutability answer this with
*persistent* data structures, which share every part a change leaves alone;
Python's standard library has none, so a large value that changes often is
the one place a mutable structure, kept private to one function, is
still the right choice." Whether to name a third-party package is yours: the book
names third-party libraries only where a listing uses them, which argues for
leaving `pyrsistent` out, as the proposal does.

> `[] Reject`

## Considered and declined

- A Stable Hash has no exercise of its own (exercise 6 covers `Final`, the
  other half of Immutability). An exercise putting an unfrozen `@dataclass`
  into a `dict` would fit, but `hashable.py` already shows the `TypeError`
  for `list`, and nine exercises already cover every other section.
- "A pure function is the most reliable code you can write" is a strong
  claim, but it is the author's framing and the following sentences support
  it.
- "the type checker verifies every case" (of a `match`): `ty` checks each
  case body; it does not prove exhaustiveness over `str` keys. The sentence
  claims only the first, so it stays.
