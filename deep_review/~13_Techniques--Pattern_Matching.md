> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 13_Techniques--Pattern_Matching (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I checked each claim against its listing, the linked sections (chapters 4, 8, 12, 20, 32, 33, 34), runtime probes on the pinned 3.15.0rc2, `ty` 0.0.84 probes, `ruff --select ALL`, and the 3.15 language reference.
Every quoted `SyntaxError`, `TypeError`, and `AssertionError` message matches what the interpreter prints, and both quoted `ty` diagnostics in the Solutions file match `ty` 0.0.84 on an edited copy, line and column included.
`tip verify-ch CH=13` passes 24 of 24, and `tip verify` passes.

## Applied directly

Chapter, corrections:

- "Builtin Types and Subclasses": the list of builtins whose positional sub-pattern binds the whole value lacked `frozendict`. Python 3.15 adds it (language reference, confirmed at runtime), and chapter 3 teaches the type.
- "Patterns Nest": "A pattern can also nest inside a copy of its own case" described something patterns cannot do. Chapter 34's `evaluate()` recurses as a function; the pattern has a fixed depth. Now says so: nesting has the depth you write, and a tree needs a recursive function whose `match` takes one level apart.
- "Guards": the paragraph generalized from a failed guard to "an earlier, failed case". The language reference leaves bindings from a pattern that fails partway to the implementation (CPython 3.15 leaves them unbound). Added the distinction and the advice the section lacked: use a captured name only in the `case` that captured it.
- "Alternatives and Capture": "An alternative combines several patterns" used "alternative" for the whole, and the next sentence used it for each part. The same-names rule also came before captures were introduced. The rule now follows the listing, with its reason and a pointer to `nested_patterns.py`.
- "Sequence Patterns": `case [0, 0]` lacked the colon its twin `case 0, 0:` carries.

Chapter, teaching:

- "Exhaustive Matching": new paragraph answering the question `act()` raises. `value_patterns.py` gets an exhaustiveness check with no `assert_never()`, so why write one here? The check on `act()` comes from the return type (`ty` reports "Function can implicitly return `None`" at the signature). A `match` whose cases return nothing draws no diagnostic when a case is missing (probed). `assert_never()` covers both and reports at the `match`.
- "Exhaustive Matching": cut the post-listing sentence that repeated the pre-listing one (add a type without its `case`, the checker flags `assert_never()`).
- "Sequence Patterns": `match sign(x), sign(y):` used a `sign()` the chapter never defines (Python has no `math.sign()`). Now "Given a `sign()` helper that returns `-1`, `0`, or `1`". "Guards" in the same paragraph is used before it is taught, so it links to its section.
- "Guards": "A guard that merely compares one capture to a constant is a literal pattern written the long way" had an exception the chapter itself created: a bare-name constant such as `DEFAULT`, which only a guard (or a dotted name) can test. Added, since exercise 6 asks for that fix.
- `test_class_patterns.py` tested two listings and sat after a third subsection. Split into `test_class_patterns.py` and `test_keyword_patterns.py`, each at the end of its own subsection.

Chapter, prose:

- "A Bare Name Captures": "neither `ty` nor `ruff` catches it either", followed by a restatement of what the paragraph said five lines up. Now "Python compiles it without a warning, and neither `ty` nor `ruff` reports it."
- "a value that lied about its type" is a figure of speech; now "a caller ignores the annotation and passes the string `"x"`", which also introduces the `'x'` in the quoted message. The test is `test_assert_never_rejects_a_non_shape()`.
- Watch-list words: "never runs" (now "is unreachable"), "no entry at all", "is itself a pattern", "flips the meaning".
- The `{#dynamic-binding-vs-pattern-matching}` heading had no blank line after it.
- Exercise 2: `assert_never` gains its parentheses.

Solutions:

- Exercise 1: `classify(value)` had no annotations; now `(value: object) -> str`. Added `classify((1,))`, which answers "singleton", and a paragraph on why: the exercise says "for lists", and a sequence pattern accepts a tuple. `case list([_]):` restricts the case to a `list` (probed).
- Exercises 1 and 5: `Point` was `@dataclass`, where the chapter's is `@dataclass(frozen=True)`. A Solutions copy follows its chapter listing.
- Exercise 5: "five nearly identical `if` clauses" counted wrong; the listing has four guards. Cut "and the reason is worth naming". Added why the final `case _` is there (`ty` sees `sign()` return `int`; removing the case draws `invalid-return-type`, probed).
- Exercise 6: "Moving the constant into a class keeps one definition" sat under a listing that has two. Now says the listing keeps the module-level copy because `act()` and `guarded()` need the bare name.
- Exercise 3: blank line after the `# exercise_3.py` slug, as every listing without imports has.
- Exercise 2: "safety net" and "an actual `Rectangle`" reworded.

## Considered and declined

- **Tests import modules that print at import.** `sequence_patterns.py`, `class_patterns.py`, `exhaustive.py`, and the two `notifications_*.py` files carry top-level demos and are imported by tests. Splitting each into library plus demo doubles the chapter's listing count for seven-line demos, and pytest hides the output. Only `point.py` is a pure library, which is right.
- **The soft-keyword paragraph repeats chapter 4's nearly word for word.** Chapter 13 is the reference chapter for `match`, and a reader arriving by link needs it here.
- **`ch13_fallback_capture.py` breaks the `exercise_N.py` naming.** The name is what `pyproject.toml`'s per-file `N806` ignore keys on; `exercise_6.py` would match every chapter's.
- **"An `if`/`isinstance()` chain can reach the same guarantee, but only if you remember to end it with `assert_never()`."** A `match` needs the same remembering, so the sentence favors `match` a little more than the facts do. The next sentence gives the real reason (the dispatch has a visible shape), and the new `act()` paragraph covers what the checker does without `assert_never()`.
- **`**rest` and `[first, *middle, last]` appear in prose only.** Both verified at runtime. A listing for each would repeat `sequence_patterns.py`'s point.
- **Mapping-pattern keys must be literals or dotted names.** True and unmentioned, but the bare-name section already teaches the rule that produces it.
