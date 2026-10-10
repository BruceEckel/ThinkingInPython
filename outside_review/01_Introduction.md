<!-- outside review of Chapters/01_Introduction.md, model gemini-3.1-pro-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `01_Introduction.md` chapter:

**1. The Examples (Linter tooling)**

* **Target Text:** "The book's build system extracts the examples, then type-checks\n(with Astral's `ty`), lints, runs, and tests them."
* **Issue:** The text explicitly identifies the type checker (`ty`) and its creator (Astral) but leaves the linter anonymous. Since the project relies on Astral's `ruff` for linting, naming it alongside `ty` gives the reader a complete picture of the modern static analysis stack used in the repository.
* **Instruction:** Change the text to: "The book's build system extracts the examples, then type-checks\n(with Astral's `ty`), lints (with Astral's `ruff`), runs, and tests them."

**2. The Exercises (Copying examples)**

* **Target Text:** "They usually ask you to change a small,\nworking example from that chapter and observe the result: add a class,\nbreak an invariant on purpose, extend a table, rewrite one function two ways."
* **Issue:** The text states earlier that the build system "extracts" the examples, and the repository rules specify that readers should work in a copy of the listing rather than the extracted file (which could be overwritten during a build or sync). Reminding the reader to copy the example first prevents them from accidentally modifying a generated file and losing their work.
* **Instruction:** Change the text to: "They usually ask you to copy a small,\nworking example from that chapter, change it, and observe the result: add a class,\nbreak an invariant on purpose, extend a table, rewrite one function two ways."

**3. Resources (Pytest documentation)**

* **Target Text:** "- [The Python type system specification](https://typing.python.org/en/latest/spec/),\n  the reference behind the annotations the book uses throughout"
* **Issue:** The book relies heavily on `pytest` for testing examples and running exercises, and lists testing as a key topic in Part II. Since the target audience (intermediate programmers coming from other languages) might not know Python's testing ecosystem, a direct link to the `pytest` documentation is a missing resource they will likely need when they encounter or write their first test.
* **Instruction:** Add a bullet point immediately following this entry: "\n- [The pytest framework](https://docs.pytest.org/), the testing tool the book uses"

**4. The Examples (Test Execution)**

* **Target Text:** "The short form is the listing's name alone.\n`tip membership` runs `membership.py`,\nand words after the name go to the program,\nso `tip membership --numbers` passes it the `--numbers` flag.\nWhen the book says to run a listing, use the short form."
* **Issue:** I am unsure if the `tip` tool automatically routes to `pytest` when the target is a test file. The text notes earlier that `pytest` runs each `test_*.py` file, but if a reader uses the short form `tip test_foo` and it executes as a plain Python script (without an `if __name__ == '__main__':` block), it will silently do nothing.
* **Instruction:** If `tip` automatically invokes `pytest` for test listings, add a clarifying sentence at the end of the paragraph: "If the listing's name starts with `test_`, `tip` automatically runs it via `pytest`." (If it requires a different command, specify that instead).

## Verdicts

Applied in commit f6850259, after each item was tested against the chapter and run under `uv run`.

1. Applied. The sentence named `ty`'s maker and left the linter anonymous, and chapter 12 later writes "the linter (`ruff`)", so the Introduction now names `ruff` too.
2. Applied. The README's "Working the exercises" says "Copy the example file, change it, run it", and `tip sync` overwrites every `.py` under `Examples/`, so a reader who edits the extracted file loses the work on the next sync. The sentence now reads "copy a small, working example from that chapter, change it, and observe the result".
3. Applied. No chapter links the pytest documentation (`docs.pytest.org` appears nowhere in `Chapters/`), and the book tests with `pytest` from chapter 11 on. The bullet reads "[pytest](https://docs.pytest.org/), the test framework the book uses".
4. Applied, with a different fix. `tip` does not route a test file to `pytest`: `uv run tip test_account` printed the by-hand commands and then ran `test_account.py` as a script, which exited 0 with no output, since a test file has no top-level code. The paragraph now says a `test_*.py` file is the exception to the short form and points at the Testing chapter's pytest section for the command.
