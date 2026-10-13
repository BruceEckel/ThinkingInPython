> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Third deep review: 34_Patterns--Composite_and_Interpreter (2026-10-13)

This review follows `~34_Patterns--Composite_and_Interpreter.r2.md` (2026-09-29) and reads the chapter and its Solutions file whole.
It found nothing that needs your decision, so the file has no live blocks.
Run under `ty` 0.0.86 and `uv run python` 3.15.0 final.
`tip verify-ch CH=34 ISOLATED=1` passed 27 of 27 before the edits, and 26 of 27 after: the one failure is the NEW `exercise_refs` hit for the "(see exercise 8)" pointer added below, which names the right exercise and waits for `tip exercise-refs-accept`.
Probes confirmed every claim checked: `"a" + x` is still `unsupported-operator`; a `match` over an `Operators` annotation with all four node cases still draws `type-assertion-failure` at `assert_never()`; `list(t"{a}{b}")` yields two `Interpolation` objects while `.strings` is `('', '', '')`; `t"x{a}" + t"y{b}"` concatenates into one flat `Template`; `Var("x") and Var("y")` evaluates to `Var(name='y')`; the default recursion limit is 1000; the 3.15 dataclass `__eq__()` opens with `if self is other: return True`, which makes the chapter's "descends into any subtree that changed" exact; and `utils/exceptions.py`'s `expected()` prints nothing when no exception arrives, as Solutions exercise 6 says.

## Applied directly

Chapter, corrections:

- Operators section: "the library sets `eq=False` on the dataclass" said SQLAlchemy's columns are data classes. They are an ordinary class hierarchy. Now SQLAlchemy's column classes "define their own `__eq__()` and give up `==` as a structural comparison", and a data class that builds a node from `==` sets `eq=False`, "which keeps the generated `__eq__()` from shadowing an inherited one" (the mechanism the paragraph above sets up).
- Operators section: "Python's grammar sets the limit of the technique" opened the `==` paragraph, but the `==` limit is `expr.py`'s choice, not grammar. The grammar sentence now opens the `and`/`or`/`not` paragraph as "Python's grammar sets a harder limit", with "no special method makes them build a node"; the `==` paragraph opens "`==` is the exception in `expr.py`", and the next one "Leaving `==` alone suits `expr.py`" (was a second "`expr.py` leaves `==` alone").
- `pathlib` paragraph: "`iterdir()` and `rglob()` walk the tree" credited `iterdir()` with a walk; it lists one directory. Now each method gets its own verb, and "both yield a `Path` for each entry, whatever its kind".
- Recursion-limit paragraph: "(roughly a thousand frames)" is now "(1000 frames by default)", the probed value and the number Solutions exercise 8 uses.

Chapter, teaching:

- Recursion-limit paragraph: "The alternative is an iterative walk with an explicit stack" named a technique the chapter never shows. It now ends "(see exercise 8)", the exercise that builds it.

Chapter, prose:

- "A Template Is a Tree": "yields exactly one level" dropped "exactly".

Solutions:

- Exercise 1: the near-miss `find(root, "src")` "returns an empty list"; `find()` is a generator, so it "yields nothing".
- Exercise 2: "`disk_usage(tree)` prints `10`" is now "returns `10`".
- Exercise 3: "Every case keeps the chapter's `is` test" was false of `Neg`'s `Num(a)` and `Neg(deeper)` cases. Now "Both new cases keep the chapter's `is` test", which holds for the `Neg` and `Div` branches.
- Exercise 8: the "three drawbacks" paragraph opened with a sentence that was not a drawback, so the reader had to find the three. Now "First, it lifts the limit for Python calls alone", "Second", "Third", with the facts unchanged (the r2 review probed them).
- Exercise 9: "What breaks in the closed version is obvious" told the reader it was obvious; now "The closed version breaks at the union".

## Considered and declined

- The opening's `disk_usage(root)` (above the figure) uses the function form before either listing exists, and the first listing calls `root.disk_usage()`. It names the operation the figure draws, and the function form is the one the chapter settles on. Kept.
- The `pathlib` fragment's `root.rglob("*")` reuses the name `root` for a `Path` where the listings use it for a `Directory`. The fragment is unextracted and the paragraph is about `Path`, so the reading is clear. Kept.
- Solutions exercise 4 calls the parentheses in `x + (x + 1)` "redundant". They are redundant algebraically but not for the tree, which prints back differently without them. The paragraph's closing clause ("keeps every pair that the expression's meaning requires") frames it as algebra, so it stands.
- Solutions exercise 9, "Every walker would then be silently wrong rather than helpfully extended", is loose about which design it describes. Two reviews passed it; it reads as the closed-grammar argument and changes nothing a reader does. Kept.
- The three-walker paragraph and the "A Template Is a Tree" heading stay, per `deep_review_db.md`.

## For the session

- NEW `exercise_refs` hit: `Chapters/34_Patterns--Composite_and_Interpreter.md` line 711, "(see exercise 8)" -> "8. An iterative walk over a deep tree". The pairing is right; accept with `tip exercise-refs-accept`.
- `tip watch-words` now reports one stale baseline entry for chapter 34 (`exactly: CODE yields exactly one level of ...`), because this review removed that "exactly". The baseline needs the entry dropped.
- `tip internal-names` reports a stale entry outside this chapter: `Examples/15_Techniques--Context_Managers/banner_cm.py::banner.title`, presumably from chapter 15's concurrent review.
