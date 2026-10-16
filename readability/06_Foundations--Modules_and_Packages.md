> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability sweep of chapter 06 (2026-10-16).
The chapter carries few AI-writing tells, and every finding had one sensible answer,
so this file holds no live block and serves as the record of the direct edits.
Line numbers refer to the chapter after the edits.

## Applied directly

- 47, §70 restatement ("That is,"): "The condition is true only when you run this file as a script. That is, `__name__` is `"__main__"` when you use the command line:" -> "`__name__` is `"__main__"` only when you run this file as a script from the command line:"
- 94, missing purpose: "Restart the program, or call `importlib.reload(use_module)`" -> "To load the edited file, restart the program, or call ..." (the instruction followed a statement of the problem with no link to it)
- 102, template opener (one of four "Here," openers): "Here, the `from` keyword brings ..." -> "The `from` keyword brings ..."
- 461, "and" joining two subjects, two claims: "gathers the public names into one readable place, and documentation tools read it ..." -> two sentences
- 501, §8 copula avoidance and pattern-name convention: "lets a module serve as a [façade](...)" -> "lets a module act as a [*Façade*](...)"; the link goes to chapter 29's *Façade* section and sits beside "[*Singleton*]", so it names the pattern
- 510, "and" joining two subjects, two claims: "`importlib.import_module("my-mod")` loads the file, and plugin loaders open oddly named files that way." -> two sentences
- 598, template opener: "Here, `noisy.py` prints a message ..." -> "`noisy.py` prints a message ..." (the "Here" openers at 55 and 303 stay; each points at the listing that follows or contrasts it with the one before)
- 633, redundancy: "Before your code runs, CPython loads standard-library modules at startup," -> drop "at startup", which repeats "before your code runs"

## Considered and declined

- 699, §9 tailing negation: "The failure is silent: no error, just a table with a row missing." A short beat among longer sentences, and the colon delivers a restatement; kept as voice.
- 408, "A plain `import`": "plain" contrasts with the `from` import in the sentence before (recurring keep).
- 655, "names your program ever deferred": the corrected form the global `only` rule cites; the "ever" draws the contrast with "still waiting".
- 547, "even on a filesystem that treats the two names as one": the concession is the claim.
- 453, "The underscore changes one mechanical thing:": recorded keep in `readability_db.md`.
- 566, rhetorical question "What if your module or package lives in a different directory ...?": the question names the problem the section solves (recurring keep).
- 37, "is special in some way": vague by itself, but the next sentence supplies the example, and the chapter defers dunders to chapter 07.
- 514-532, bold labels ending in a period (`**Modules** (`.py` files).`): paragraph labels in a naming-convention section, not §58 bullet labels.
