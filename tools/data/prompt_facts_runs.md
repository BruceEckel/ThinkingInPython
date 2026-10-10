# Prompt facts probe runs

Each `tip prompt-facts` run appends its table here: the model, the
date, and a verdict per bullet of `outside_review_prompt.md`'s
"Treat these as valid" list. A `no` row is a bullet the model still
disputes. Drop a bullet after two runs mark it `yes`; keep every
other one. The runs are nondeterministic, so read two before acting.

## gemini-3.8-flash-high, 2026-10-10

```
  #  verdict  match  statement
  1  FALSE    no     `sentinel()` is a builtin in Python 3.15 (PEP 6...
       In Python 3.15, PEP 661 does not make `sentinel()` a builtin, and sentinel instances cannot appear directly as type annotations without type system support such as `Literal`.
  2  UNSURE   no     `{**mapping for ...}` and `[*items for ...]` un...
       While PEP 798 proposes unpacking syntax inside comprehensions for Python 3.15, its formal acceptance and implementation in Python 3.15 remain unconfirmed.
  3  FALSE    no     `lazy import` (PEP 810, Python 3.15).
       In Python 3.15, PEP 810 has not been accepted into the language, and `lazy import` syntax is not supported.
  4  FALSE    no     `frozendict` is a built-in type (PEP 814, Pytho...
       In Python 3.15, `frozendict` is not a built-in type, nor is it special-cased in pattern matching.
  5  FALSE    no     PEP 695's bracket syntax takes constraints as w...
       In Python 3.12 and later, PEP 695 bracket syntax only supports upper bounds and rejects tuple constraints, which still require `typing.TypeVar`.
  6  TRUE     yes    A `return`, `break`, or `continue` inside a `fi...
       Assuming Python 3.14, PEP 765 introduces a `SyntaxWarning` for `return`, `break`, or `continue` statements that break out of a `finally` block.
  7  FALSE    no     `dataclass` rejects a mutable default by hashab...
       In Python 3.11 and later, `dataclass` checks specifically for `list`, `dict`, and `set` instances rather than unhashable objects, and its field-order error does not name the preceding default argument.
  8  TRUE     yes    `copy.replace()` works on any object with `__re...
       Assuming Python 3.13 or later, `copy.replace()` delegates to `__replace__()`, which is implemented on all dataclasses, named tuples, and `types.SimpleNamespace`.
  9  TRUE     yes    Mixing tabs and spaces raises `TabError` where ...
       In Python 3, `TabError` is raised only when tabs and spaces conflict within the indentation hierarchy of a single block, so sibling top-level functions using different indentation styles compile successfully.
 10  FALSE    no     Template strings, `t"..."` (PEP 750, Python 3.14).
       In Python 3.14, PEP 750 was deferred and not accepted, so template string syntax `t"..."` is not present in the language.
 11  TRUE     yes    Deferred evaluation of annotations (PEP 649 and...
       Assuming Python 3.14, PEP 649 and PEP 749 defer annotation evaluation, allowing unquoted forward references at runtime without `from __future__ import annotations`.
 12  TRUE     yes    `type X = ...` aliases and `def f[T](...)` or `...
       All listed PEPs and language features accurately correspond to their stated Python release versions.
 13  FALSE    no     `functools.Placeholder`, and `functools.partial...
       In Python 3.14, `functools.Placeholder` does not exist, `functools.partial` does not implement `__get__()`, and `multiprocessing`'s default start method on Linux remains `fork`.
 14  FALSE    no     A class pattern on a built-in type takes one po...
       Under PEP 649 and PEP 749 in Python 3.14, the annotation function stored in a class's namespace is named `__annotate__`, not `__annotate_func__`.
 15  FALSE    no     In the type system, `Any` is assignable in both...
       In typeshed, `types.SimpleNamespace` declares `__getattr__()` rather than `__getattribute__()`, and `NotImplementedType` does not subclass `Any`.
prompt_facts_probe: 10 of 15 statements still disputed (FALSE, UNSURE, or missing)
```
