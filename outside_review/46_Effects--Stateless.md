<!-- outside review of Chapters/46_Effects--Stateless.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `46_Effects--Stateless.md` chapter:

**1. Section: The Effect Definition (Modern Type Aliases)**

* **Target Text:** "Effect: TypeAlias = Generator[A | E, Any, R]"
* **Issue:** Since the book targets Python 3.15 and already uses PEP 695 generics elsewhere, it should use the modern `type` statement for type aliases. The older `TypeAlias` assignment with implicitly scoped `TypeVar`s is brittle and largely superseded in modern code.
* **Instruction:** Change the code block to use the modern syntax: `type Effect[A, E, R] = Generator[A | E, Any, R]`

**2. Section: Supplying an Interface (Type Narrowing of Annotated Variables)**

* **Target Text:** "An annotated local variable is different. screen: Console = Terminal() narrows back to Terminal at the assignment, so supply(screen) builds a Need[Terminal] handler again."
* **Issue:** This misstates type checker behavior. An explicit variable annotation like `screen: Console = Terminal()` sets the static declared type to `Console`, and type checkers (including `ty`/Pyright) respect this declared type rather than narrowing back to the assigned implementation type. Therefore, `supply(screen)` successfully builds a `Need[Console]` handler without needing `as_type()`.
* **Instruction:** Replace the two sentences with: "An annotated local variable works too. `screen: Console = Terminal()` sets the static type to `Console`, so `supply(screen)` builds a `Need[Console]` handler."

**3. Section: Emptying the Channels (Runtime vs Static Checks)**

* **Target Text:** "unsupplied.py shows run() refusing an Effect that still declares an Ability, before the program starts."
* **Issue:** `unsupplied.py` shows the `run()` function raising a `MissingAbilityError` during execution, not before the program starts. It is the static type checker that refuses the unsupplied Effect before the program starts, which is demonstrated by removing the `# type: ignore` comment.
* **Instruction:** Change the sentence to clarify the difference between the runtime and static checks: "`unsupplied.py` shows `run()` refusing an Effect that still declares an Ability at runtime, while the type checker rejects it before the program starts."

**4. Section: Where to Call run() (Orders of Magnitude)**

* **Target Text:** "On Windows, run(success(42)) measured about 650 microseconds (about 75 on Linux), four to five orders of magnitude above a plain function call."
* **Issue:** A plain function call in Python typically takes around 50 to 100 nanoseconds. 650 microseconds (650,000 nanoseconds) is roughly 6,500 to 13,000 times slower, which is three to four orders of magnitude, not four to five.
* **Instruction:** Change the text to reflect the correct math: "On Windows, run(success(42)) measured about 650 microseconds (about 75 on Linux), three to four orders of magnitude above a plain function call."

## Verdicts

Applied in commit 170f44b9, after each item was tested against the chapter and run under `uv run`.

1. Rejected. The block quotes Stateless's own definition: line 31 of `.venv/Lib/site-packages/stateless/effect.py` reads `Effect: TypeAlias = Generator[A | E, Any, R]`, and the chapter shows what the library declares, so rewriting it as a `type` statement would misquote the source.
2. Rejected. A probe in the extracted chapter directory had `ty` reveal `screen: Console = Terminal()` as `Terminal` and `supply(screen)` as `Handler[Need[Terminal]]`, and `run()` on the result drew the same `invalid-argument-type` the chapter quotes; a `Console` parameter revealed `Console`, as the boundary-function paragraph says.
3. Applied, with a different fix. Run as written, `unsupplied.py` raises a `MissingAbilityError` at runtime, so the before-the-program-starts refusal belongs to the type checker; the bullet now reads "shows the type checker rejecting a `run()` call whose Effect still declares an Ability, before the program starts," keeping the contrast with `error_escapes.py`, while the runtime `MissingAbilityError` stays explained in the paragraph below it.
4. Rejected. On this machine under `uv run` a call to `def f(): return 42` took 13.2 ns and `run(success(42))` took 420 us, a ratio of about 32,000 (log10 4.5); at the chapter's 650 us the ratio is about 50,000, so "four to five orders of magnitude" holds, and the item's 50 to 100 ns per call is slower than Python 3.15 measures.
