<!-- outside review of Chapters/01_Introduction.md, model gemini-3.8-flash-high, 2026-10-10 -->

**Please apply the following technical and structural refinements to the `01_Introduction.md` chapter:**

**1. Section: The Examples (directive syntax for type checker)**

* **Target Text:** "along with the `# ty:` comments that appear from that chapter on."
* **Issue:** Astral's `ty` type checker suppresses diagnostics using `# ty: ignore` (or rule-specific suppressions such as `# ty: ignore[code]`), mirroring PEP 484's `# type: ignore`. Naming only `# ty:` leaves off the directive keyword, which does not suppress diagnostics if written by a reader.
* **Instruction:** Change "`# ty:`" to "`# ty: ignore`".

**2. Section: The Exercises (unnamed task runner mechanism)**

* **Target Text:** "Each solution opens in steps: a hint, then the shape of the code with its bodies left out, then the full answer, so you can take as little help as you need."
* **Issue:** The text describes the three-step ladder but only directs the reader to browse the `Solutions/` directory, where opening the file risks exposing subsequent steps prematurely. The repository provides a dedicated runner task, `tip hint CH=<chapter> N=<exercise>`, to reveal those rungs progressively one at a time, but the chapter leaves this CLI mechanism unnamed.
* **Instruction:** Append a sentence explaining the CLI command: "You can also reveal these rungs one at a time from the command line with `tip hint CH=<chapter> N=<exercise>`."

**3. Section: Resources (stale documentation URL)**

* **Target Text:** "- [The Python type system specification](https://typing.python.org/en/latest/spec/),"
* **Issue:** The official specification maintained by the Typing Council is published at `https://typing.python.org/spec/`. The path `/en/latest/spec/` is a legacy ReadTheDocs route that may fail to resolve or require redirection on the custom domain (author should verify with a web request).
* **Instruction:** Update the link target to `https://typing.python.org/spec/`.

## Verdicts

Second run, on the Flash model. Applied in commit fba78cf6, after each item was tested against the chapter and run under `uv run`.

1. Rejected. The book's `# ty:` comments are its own notation, not a directive: [Static Types](../Chapters/08_Foundations--Static_Types.md) line 147 defines "A neighboring `# ty:` comment summarizes what the type checker reports for a line" and says "The `# ty:` summary is for you, not for the tool", then names `# ty: ignore[...]` separately as the suppression. The chapters hold ten `# ty:` summaries (`# ty: expected ...`, `# ty: argument ...`) against one `# ty: ignore[...]`, so the sentence names the right thing and the proposed change would misdescribe it.
2. Applied, with a different fix. `tip hint` exists (`tools/tasks.py`, `tools/hint.py`), and a run of `uv run tip hint CH=02 N=1` printed the exercise statement and then one step per run, with `ARGS=--reset` forgetting the progress. The chapter's Examples section already introduces `tip`, so one sentence after the steps description now gives the command with a concrete `CH=30 N=3` and names what the two variables hold, in place of the reviewer's placeholder form. The reviewer's premise that browsing `Solutions/` exposes later steps is wrong, since GitHub and the site render the `<details>` ladder collapsed, so the sentence presents the command as a second way, not a safer one.
3. Rejected. A request on 2026-10-10 answered `200 OK` for `https://typing.python.org/en/latest/spec/` and `404 Not Found` for the proposed `https://typing.python.org/spec/`, so the link in the chapter is the live one and the "legacy" claim is backwards.
