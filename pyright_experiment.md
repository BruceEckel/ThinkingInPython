# Pyright beside ty: the experiment

Branch `pyright-experiment`, 2026-09-14, pyright 1.1.414 against ty 0.0.80,
Python 3.15.0rc2.
The question was whether the book's listings can be checked by both,
together or separately, and what that costs.

## What the branch adds

- `pyright` as a dev dependency.
  It installs on the pinned Python (the wheel fetches its own Node through `nodeenv`).
- `[tool.pyright]` in `pyproject.toml`:
  `pythonVersion`, an `extraPaths` mirroring ty's,
  a per-root environment for Solutions ch06's own `a_package`,
  three rules off that ty also leaves off,
  and `reportPrivateImportUsage` off for `stateless`'s re-exports.
- `tools/data/pyright_baseline.txt`:
  every diagnostic pyright reports over both trees today,
  one line per occurrence as `path<TAB>rule<TAB>message`, line numbers dropped.
  The nine listings pyright cannot parse are entries here, not an exclude list.
- `tools/pyright_review.py`, behind `make pyright-review`:
  runs pyright over both trees and prints only the delta against the baseline,
  NEW for a disagreement the baseline lacks and GONE for one that no longer fires.
  `make pyright-accept` rewrites the baseline after you have read the delta.
  `make pyright` is the raw run over both trees.
- None of it is in `verify`, `gate`, `sweep`, or `ci`,
  and no listing carries a pyright suppression comment.
  `make ty` is untouched.

## Together or separately

Separately, and pyright only as a diff.
The two checkers could share a tree line by line,
because their suppressions do not collide:
`# ty: ignore[rule]` silences ty alone, `# pyright: ignore[rule]` silences pyright alone,
and each ignores the other's comment.
A shared `# type: ignore` silences both,
which is the trap: one that pyright needs and ty does not
draws ty's `unused-type-ignore-comment` and fails the ty gate.
The book does not take that route.
A pyright comment in a listing explains nothing to a reader using ty,
so every accepted disagreement lives in the baseline file instead
and the listings stay ty's alone.

Time per run: ty 0.2 s, pyright 3.7 s over `build/examples`;
ty 0.1 s, pyright 2.7 s over `build/solutions`.

## Results

| Run | `build/examples` | `build/solutions` |
|---|---|---|
| No configuration | 347 errors, 7 warnings | 162 errors, 7 warnings |
| With `[tool.pyright]` | 21 errors | 36 errors |

The unconfigured numbers were two things:
208 + 119 `reportPrivateImportUsage` on every `stateless` import,
and 102 unresolved `utils/` imports.
Both are configuration, not listings.

## What cannot work

Pyright 1.1.414, the newest release, does not parse PEP 798 comprehension unpacking
(`[*x for x in ...]`, `{**d for d in ...}`).
Nine listings use it, four in `build/examples`
(`unpacking_comprehensions.py`, `shared_iterator.py`, `tile_map.py`, `utils/display.py`)
and five in `build/solutions`.
Their thirteen parse errors are baseline entries, checked by ty alone,
and they will show up as GONE the day pyright parses the syntax.
The other 3.15 syntax the book uses (`sentinel`, `lazy import`, t-strings) parses.

## The residue, by cause

57 errors remain across 27 files.
None is a bug in a listing; each is a place where the two checkers disagree.

**One idiom, 27 errors.**
Chapter 34's `Operators` mixin annotates `self: Expr`,
where `Expr` is the union of the four node classes that inherit from it.
The chapter explains why ("the type checker cannot know that every such subclass is in the `Expr` union").
Pyright rejects it on principle: the type of `self` must be a supertype of the class,
and a union of subclasses is not.
mypy holds the same rule.
`expr.py` carries 4 of these; Solutions ch34 exercises 3, 4, 5, 6, and 8 carry 23.
A file-level `# pyright: reportGeneralTypeIssues=false` clears each file with one line,
at the cost of that whole rule for the file.

**Runtime-failure demos that pyright catches statically, 8 errors.**
The book shows these failing at runtime, and ty is silent, so no `# type: ignore` is present.
Pyright reports them before the program runs:
`finally_swallows.py` (a `return` inside `finally`),
`factory_checking.py` (`default_factory=set` on a `dict` field),
`proxy_interface.py` (instantiating the abstract `Partial`),
`fetch_stats.py` (a `NamedTuple` field named `count` shadows `tuple.count()`),
`prepare_namespace.py` and Solutions ch17 `ch17_keep_first.py` (a method declared twice on purpose),
Solutions ch03 `exercise_4.py` (`frozenset.add()` handed a list).
Each needs one `# pyright: ignore[rule]`.
The chapter 12 prose is the more interesting casualty:
"A bare `list`, `dict`, or `set` produces a type loose enough that a type checker accepts it against any annotation,
so the checker never compares the factory with the field."
That is true of ty and false of pyright, which infers `set[Unknown]` and rejects it.
"The type checker" in the book means ty, and a second checker makes that visible.

**Same error, different anchor line, 2 errors.**
`frozen_inheritance.py` carries `# type: ignore` on each `class` line, where ty reports.
Pyright reports on the decorator line above, so the shared comment misses.
The fix is two checker-specific comments on two lines, verified to satisfy both.

**Metaclass-added attributes, 3 errors.**
`my_list.py` and Solutions ch17 `exercise_7.py` read attributes a metaclass installed.
ty's `Any` escape covers it; pyright reports `reportAttributeAccessIssue`.

**Third-party stubs, 10 errors.**
`frozendict(theme=..., zoom=...)` in ch03 and Solutions ch03:
pyright reads `frozendict`'s stubs as taking no keyword arguments; ty accepts them.

**Inference differences, 7 errors.**
The PEP 661 `DONE` sentinel does not narrow out of `object | DONE` (ch23 and its solution, 2);
`repeat.py`'s loop-assigned `result` types as `Unbound | R` (1);
Solutions ch23 `exercise_9.py`'s recursive `Sequence[Nested]` alias against a nested `list` (2);
Solutions ch31 `exercise_9.py`'s transition table, where pyright keeps literal tuple keys (3).

## What a pyright gate would cost

- Nine listings permanently excluded until pyright parses PEP 798.
- About 20 listings gaining a checker-specific comment,
  each a visible line in the book that explains nothing to a reader using ty.
- A decision on chapter 34's idiom, since the chapter teaches it
  and two of the three major checkers reject it.
- Prose that says "the type checker" audited for claims that hold only for ty;
  the sweep found fourteen, and nothing gates the rest.
- Roughly 6 s per `make verify`, against ty's 0.3 s.

## Recommendation

Keep pyright as a periodic review, out of the gate and out of the listings.
The value of the second checker is the list above,
not a second green light:
it names eight demos where pyright is stricter than ty,
one taught idiom that pyright and mypy both refuse,
and, through the 2026-09-14 sweep it prompted,
fourteen prose claims about "the type checker" that hold for ty alone.
That list only matters when it changes, and the baseline diff shows the change.

Read `make pyright-review` at three moments:

- After editing a chapter's listings.
  A NEW entry is a fresh disagreement,
  and the nearest sentence saying "the type checker" is the one to reread.
- After `make tools-upgrade` moves pyright.
  GONE entries mean pyright caught up (the PEP 798 files leave this way);
  NEW ones mean a new strictness.
- After a `ty` upgrade.
  A disagreement that disappears because ty now reports it
  is a listing that may need an ignore;
  a new one may be a claim that has gone ty-specific.

Then `make pyright-accept` once every line in the delta has an explanation.
