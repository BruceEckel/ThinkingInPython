> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Second deep review: 34_Patterns--Composite_and_Interpreter (2026-09-29)

This review follows `~34_Patterns--Composite_and_Interpreter.md` (2026-09-25) and reads the commits since, including the 2026-09-27 fix-triage edits.
It found nothing that needs your decision, so the file has no live blocks.
Probes run under `ty` 0.0.84 and the pinned 3.15.0rc2: `"a" + x` is still `unsupported-operator`; a `case _: assert_never(e)` under an `Operators` annotation draws `type-assertion-failure` with all four node cases present; a `Symlink` passed to `disk_usage()` or placed in a `Directory` is `invalid-argument-type`; with `sys.setrecursionlimit(10**9)`, `evaluate()` walks 100,000- and 1,000,000-level trees, while `repr()` and `hash()` on those trees raise `RecursionError: Stack overflow`.

## Applied directly

Chapter, damage from the 2026-09-27 triage:

- Opening: "Both patterns build on exhaustive matching" (from "This chapter builds each pattern with...") credited the GoF patterns with a Python technique. Now "Each of those `match` statements is exhaustive, so the type checker reports a node kind that no case handles", which also says what exhaustiveness gives you.
- "A Template Is a Tree": "Everything else about walking a `Template` is the recursive `match` over node kinds that *Composite* uses" contradicted the paragraph it closes (the walk is a loop, and the listing tests with `isinstance`). Now "Everything else follows this chapter's walkers: one branch per node kind, and a recursive call where a node holds more nodes."

Chapter, corrections:

- `pathlib` paragraph: "No `Path` method recurses through that tree" contradicted the sentence above it, which says `rglob()` walks the tree. Now "No `Path` method adds up a result over that tree the way `disk_usage()` does", which is the missing piece the next sentence supplies.
- `Operators` section: "`assert_never()` stops working" now says what happens: it "fails type checking even with a case for every node" (probed).
- Closing paragraph: "Textbooks usually present the *Interpreter* pattern as a way to add operations to a language" described *Visitor*. GoF's intent is interpreting sentences in a language; now "a way to evaluate sentences in a small language".
- Simplification: "so `simplify()` never edits the input" became "cannot edit its input"; the record guarantees the inability, not the habit.

Chapter, prose:

- "Add a `Symlink` to the `Node` union, and every function ... fails" (imperative plus consequence) is now an "If you add" condition.
- Injection paragraph: "The only remaining defense is inspecting the result to guess which characters the program wrote and which a user did" repeated the next paragraph's sentence nearly word for word. Now "Any defense then has to inspect that string and guess where the user's text begins."
- Exercise 8: "another way out" (a form of the banned "the way out") became "also avoids the error".

Solutions:

- Exercises 3 and 5 copied an older `expr.py` family: `evaluate()` lacked the chapter's `/`, `simplify()` lacked the `is` sharing guard, exercise 5's `simplify()` had no `case _: assert_never(e)`, and exercises 3-5 carried a stale `from __future__ import annotations`. All now follow the chapter's listings; exercise 3's `Neg` and `Div` cases get the same guard.
- Exercise 3 prose: the case for leaving division by `Num(0)` alone argued from branches and variables the language does not have. It now argues from what `simplify()` is (a rewrite that does not evaluate), adds why `Div` folds no constants (a quotient does not fit in `Num`'s `int`), and says `evaluate()` now returns a `float`. The sentence that opened with a dangling "too" is gone, and "honest" with it.
- Exercise 5 prose said exercise 3's solution "leaves `to_infix()`'s and `simplify()`'s new cases to prose rather than code". It writes both in code; the clause is cut.
- Exercise 8 prose said a raised recursion limit turns `RecursionError` into a segmentation fault because each Python frame consumes C stack. On 3.15 a Python-to-Python call uses no C stack, and a C-level overflow raises `RecursionError: Stack overflow` (both probed). The paragraph now states what raising the limit costs today: C-recursive operations (`repr()`, `hash()`) still fail, memory grows with depth, and the setting is global.
- Filler: "exactly" (exercises 1, 2, 5), "genuinely" (5), and "and that guarantee is what matters" (4). Exercise 1's "the same duplication in its simplest form" described a different duplication; now "a simpler duplication", with what it costs (a path alone does not say which directory matched).

## Considered and declined

- "`to_query()` uses the walk to keep user values out of the query text" (a triage rewrite) states content and leads into the injection example. Kept.
- `**env` paragraph: "the deep trees this chapter warns about later, which can run thousands of levels" describes the trees, not the walk, and the recursion-limit paragraph says the walk fails first. Kept.
- The three-walker paragraph stays, per `deep_review_db.md`.
