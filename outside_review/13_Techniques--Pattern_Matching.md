<!-- outside review of Chapters/13_Techniques--Pattern_Matching.md, model gemini-3.1-pro-high, 2026-10-10 -->

Please apply the following technical and structural refinements to the `13_Techniques--Pattern_Matching.md` chapter:

**1. Matching Values (Literal patterns and singletons)**
* **Target Text:** "A literal pattern compares with `==`, not with `is`, so `case 200:` also matches `200.0` and `case 1:` matches `True`. `None`, `True`, and `False` are the exception. Those three compare with `is`, so `case True:` does not match `1`."
* **Issue:** According to PEP 634, literal patterns never match `True`, `False`, or `None` unless the pattern is identical to the subject. The match does not fall back to `==`. Therefore, `case 1:` does not match `True` any more than `case True:` matches `1`.
* **Instruction:** Replace the target text with: "A literal pattern compares with `==`, not with `is`, so `case 200:` also matches `200.0`. `None`, `True`, and `False` are the exception: a pattern never matches them unless it is the exact same identity, so `case 1:` does not match `True` and `case True:` does not match `1`."

**2. Built-in Types and Subclasses (Nonexistent built-in type)**
* **Target Text:** "(`bool`, `int`, `float`, `str`, `bytes`, `bytearray`, `list`, `tuple`, `dict`, `frozendict`, `set`, `frozenset`)"
* **Issue:** Python does not have a built-in `frozendict` type. While the standard library provides `types.MappingProxyType`, `frozendict` does not exist as a built-in and thus cannot be in the language's list of special-cased types for positional patterns.
* **Instruction:** Remove `frozendict` from the list, changing it to: "(`bool`, `int`, `float`, `str`, `bytes`, `bytearray`, `list`, `tuple`, `dict`, `set`, `frozenset`)"

**3. Pattern Matching (Mapping type semantics)**
* **Target Text:** "That case matches only a dictionary whose `"type"` is `"click"`, and it binds `x` and `y` from that dictionary as it matches."
* **Issue:** A mapping pattern matches any object that inherits from `collections.abc.Mapping`, not just instances of the built-in `dict`. Emphasizing that it works on any mapping (like a `defaultdict` or a custom mapping class) reinforces the structural, duck-typed nature of pattern matching.
* **Instruction:** Change the target text to: "That case matches only a mapping whose `"type"` is `"click"`, and it binds `x` and `y` from that mapping as it matches."

## Verdicts

Applied in commit 2cfac23b, after each item was tested against the chapter and run under `uv run` on 3.15.0rc2.

1. Rejected. PEP 634's identity rule applies to a pattern that is `None`, `True`, or `False`, not to a subject of that kind, and a probe confirmed the chapter: with `case 1:` first, a subject of `True` answered "case 1" (`1 == True`), while with `case True:` first, a subject of `1` fell through to `case 1:`. So `case 1:` matches `True` and `case True:` does not match `1`, as the two sentences say.
2. Rejected. `frozendict` is a built-in type since Python 3.15 (PEP 814; chapter 03 has a section on it), `hasattr(builtins, "frozendict")` is `True` on 3.15.0rc2, and `case frozendict(d):` bound the whole `frozendict({'a': 1})` to `d`, the positional special case the list describes. The reviewer's training data predates the type; the review prompt's version list now needs `frozendict` added.
3. Applied. A mapping pattern tests `collections.abc.Mapping`, and a probe matched `{"type": "click", "x": x, "y": y}` against a `defaultdict`, so "only a dictionary" excluded objects the pattern accepts. The two sentences now say "mapping"; the chapter's own Mapping Patterns section already writes "a catch-all for any mapping".
