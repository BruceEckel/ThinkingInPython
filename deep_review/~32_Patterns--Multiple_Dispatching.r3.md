> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Third deep review of chapter 32 and its Solutions file, run 2026-10-13.
It carries forward `~32_Patterns--Multiple_Dispatching.r2.md` and `deep_review_db.md`.
The r2 open block, "Solution 8 has no second dispatch", is settled:
solution 8 now gives the six weapons `compete()` and six `eval_*()` methods each,
and solution 10 keeps `Troll2` and `meeting()`, so it is not raised again.
Every listing was extracted and run in `build/verify-ch-32/`
and every chapter and Solutions claim about a near-miss was probed on `ty` 0.0.86
and Python 3.15.0 (`uv run`):
the `Meters | NotImplementedType` diagnostic,
the `singledispatch_trap.py` `# type: ignore` (still needed, `unresolved-attribute` on `.register`),
the table version's ten seeded duels,
solution 8's nine diagnostics without `Weapon.compete()`,
solution 9's two `unresolved-attribute`s without the `isinstance()` tests,
solution 10's "35 pairs agree" and `KeyError` without `strict=True`,
and solution 8's "all three kinds win" over 200 seeds (Troll 94, Dwarf 56, Elf 50).
Pyright 1.1.414 accepts the union access, as the chapter says.
`tip verify-ch CH=32 ISOLATED=1` passed 27 of 27 before and after;
`tip prose CH=32` is clean.
No live blocks.

## Applied directly

- Opening: "the dispatch the language performed for the receiver" is now "performs" (standing behavior).
- `Any` paragraph: "unless something declares all four methods: `Item`, as abstract methods, or a `Protocol`" read as a three-item list. Now "A precise type needs a declaration of all four methods, either on `Item` as abstract methods or in a `Protocol`."
- Table-preview paragraph: it said the table version "keeps the checking" and that a class "is complete the moment it inherits `compete()`", right after the method version's eight-of-nine problem, so a reader would infer the table catches a missing answer statically. It does not. The paragraph now says a missing row escapes the type checker the way a missing method does and fails at the first duel that needs it. "is typed `Item`" (passive) became "`compete()` takes its opponent as an `Item`".
- After `paper_scissors_rock_table.py`: "Dictionary keys are flexible. A tuple works as a key..." sat after the "same ten duels" sentence; it now leads, and says what the tuple keys are ("each key in `OUTCOME` is a pair of classes").
- After `exact_match.py`: "so `Origami` is not `Paper`" is now "so `(Origami, Rock)` and `(Paper, Rock)` are different keys", naming what the probe compares.
- `match` section: added the near-miss a reader writes next. `match` takes the first case that matches, where `singledispatch` picks the most specific class, so an `Origami` case placed after the `Paper()` case is dead code.
- `singledispatchmethod` trap: "raises no error" became "runs cleanly" (positive), and the sentence that said "every subclass" twice is split into two.
- Conclusion: "the one case where Python performs the second dispatch" contradicted the section saying `singledispatchmethod` supplies it; now "the interpreter".
- Solution 3: the helper dropped the chapter's `isinstance(result, Outcome)` guard, losing the protection the chapter explains (a bare `"win"` passes `==`). It now asserts against `module.Outcome`, and the prose says why.
- Solution 4: `random.seed(47)` sat between two function definitions; it now sits with the demo it seeds. Marker unchanged.
- Solution 6: "the order the loops happen to walk" lost "happen to"; the order is deterministic.
- Solution 7: `self.__class__.__name__` is now `type(self).__name__`, as in every other listing in the chapter and Solutions.
- Solution 9: "That is the type test about which the chapter warns in the ladder version" is now "the kind of test the chapter's ladder version repeats in every class".

## Considered and declined

- Solutions 8 and 10 name their classes `Inhabitant2`, `Dwarf2`, `Project2`, and so on, although each sits in its own file. The suffix marks them as exercise 7's classes modified, and renaming touches two listings and the prose for no gain in the lesson.
- `paper_scissors_rock.py`'s comments say "self was Paper" and "caller was Paper". The past tense points at an event in the call chain (the first dispatch has run by then), which the style rule allows; rewriting eighteen comments would be churn.
- Solution 8's `meeting()` pairs groups with index loops where `itertools.combinations()` would be shorter. The listing-design pass covered this chapter on 2026-10-12/13; left to that queue.
- "Three techniques in this chapter answer the same question" does not count `match` or `singledispatchmethod`. `match` involves no first dispatch, and `singledispatchmethod` automates the `eval_*()` family, so the three are the distinct answers.

## For the session

- `tip verify-ch` regenerated `Solutions/32_Patterns--Multiple_Dispatching/exercise_3.py`, `exercise_4.py`, and `exercise_7.py` from the Markdown; they belong in the same commit.
- mypy is not installed, so the chapter's "Pyright and mypy accept the access" was checked for Pyright alone.
