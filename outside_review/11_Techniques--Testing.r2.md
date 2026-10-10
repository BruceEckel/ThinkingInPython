<!-- outside review of Chapters/11_Techniques--Testing.md, model gemini-3.8-flash-high, 2026-10-10 -->

Please apply the following technical and structural refinements to the `11_Techniques--Testing.md` chapter:

**1. Section: Comparing Floating-Point Values (Correction of factual claim about floating-point arithmetic)**

* **Target Text:** "and every other whole-percent rate on this starting balance gives an exact result too."
* **Issue:** In IEEE 754 binary floating-point representation, whole-percent values such as `0.07`, `0.14`, or `0.29` cannot be represented as exact finite binary fractions. When evaluated on a balance of `100.0`, `100.0 * 0.07` yields `7.000000000000001`, which makes `100.0 + 100.0 * 0.07 == 107.0` evaluate to `False`. Exact whole-number results on a base of `100.0` occur only for specific rates whose denominators divide cleanly into dyadic factors (such as 0.05, 0.10, 0.20, or 0.25).
* **Instruction:** Replace the claim that every whole-percent rate produces an exact result with text clarifying that only certain rates happen to produce exact values on this balance, for example: "and several other whole-percent rates on this starting balance happen to give exact results too."

**2. Section: Footnotes (Harmonize footnote style rule with chapter usage)**

* **Target Text:** "This book follows pytest's own spelling for `@pytest.mark.parametrize`, and uses \"parameterize\" everywhere else, for the general sense of a class or function taking a parameter."
* **Issue:** The footnote claims the book uses "parameterize" everywhere outside of `@pytest.mark.parametrize`. However, the chapter itself uses the `parametr-` stem across all prose and headings when discussing tests and fixtures: `## Parametrizing Tests`, "a parametrized one", "you can parametrize a fixture", "A parametrized fixture multiplies every test", and "a handful of parametrized cases".
* **Instruction:** Clarify the footnote to state that the book uses `parametr-` for pytest marks, fixtures, and test variations, reserving `parameterize` for the general programming sense (such as generic types or parameterized classes) in subsequent chapters.

**3. Section: Fixtures Replace Setup and Teardown (Clarify generator fixture teardown on test failures)**

* **Target Text:** "Everything after it runs once the test finishes, whether the test passes or fails. Close files, release locks, or check a final invariant after the `yield`."
* **Issue:** If a test fails or raises an unhandled exception, `pytest` resumes the fixture generator after the `yield`. However, asserting invariants directly after `yield` without a `try...finally` block means that if teardown actions (such as releasing locks or closing files) are placed after an assertion that fails, or if setup within the test left state that causes `withdraw()` itself to raise, critical cleanup code will be skipped. Advising readers to place cleanup and invariant checks together after `yield` needs a brief note on using `try...finally` to ensure cleanup runs even if assertions fail.
* **Instruction:** Add a brief sentence noting that when cleanup must run unconditionally, it belongs in a `finally` block around the post-`yield` teardown code so that a failing invariant check does not abort the cleanup.

## Verdicts

Second run, on the Flash model; the first two attempts exceeded the output token limit and the third answered. Applied in commit 8223bfe6, after each item was tested against the chapter and run under `uv run` on 3.15.0rc2.

1. Rejected. `account.py`'s `add_interest()` computes `self.balance += self.balance * rate`, and a probe of `100.0 + 100.0 * rate` for every whole-percent rate from `0.01` to `0.99` found no inexact result: `100.0 + 100.0 * 0.07` is `107.0`, not the `107.00000000000001` the reviewer gives (`100.0 * 0.07` alone is `7.000000000000001`, but the addition rounds back). The sentence holds for this listing's formula; the reviewer's counterexamples hold for `100.0 * (1 + rate)`, which the listing does not use.
2. Applied, with a different fix. The chapter uses the `parametr-` stem eighteen times, in "Parametrizing Tests", "a parametrized fixture", and so on, against the footnote's "`@pytest.mark.parametrize`" and "parameterize everywhere else". The footnote now says the book follows pytest's spelling for the mark and for the fixtures and tests it builds, and uses "parameterize" everywhere else; chapter 17's own footnote on the same word is about a general-sense use and stands.
3. Applied, with a different fix. In `test_teardown.py` the cleanup (`account.withdraw(account.balance)`) precedes the `assert`, so a failing check cannot skip it, and that ordering is the rule the paragraph had left implicit. One sentence now states it: "Do the cleanup first, as the listing withdraws before it asserts, so a failing check cannot skip it", in place of a `try`/`finally` the listing does not need.
