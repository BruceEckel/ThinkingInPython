> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability sweep of the chapter 06 Solutions README (2026-10-16).
The file carries few AI-writing tells; most findings were "and" joins between clauses with different subjects,
and every finding had one sensible answer,
so this file holds no live block and serves as the record of the direct edits.
Line numbers refer to the README after the edits.

## Applied directly

- 150, subgoal label that misnames its paragraph: "**Load the import chain first.**" -> "**Trace the load order.**" (the paragraph describes the order Python loads the modules; the old label read as an instruction to load something)
- 304-305, "and" standing in for a consequence: "turns the check off ..., and `import module` then finds `Module.py`" -> "..., so `import module` finds `Module.py`"
- 306-308, "and" joining two subjects, then a restatement: "Python reads that variable, and the filesystem ignores it. The variable's effect therefore confirms that Python, not the filesystem, compares the names." -> "Because Python alone reads that variable, its effect confirms that Python, not the filesystem, compares the names."
- 312-313, "and" joining two subjects: "recommends `snake_case` for modules, and with an all-lowercase name, an import and its file always match in case" -> two sentences
- 329-332, hint, two "and" joins between different subjects: "needs the module's `__package__`, and a file run as a script has none" and "needs the project root on `sys.path`, and the command you run decides the path's first entry" -> four sentences
- 350-352, "and" joining two subjects: "resolves a relative import against the module's `__package__`, and a file run as a script has none. The script runs as `__main__`, ..." -> "... `__package__`. A file run as a script has none, since it runs as `__main__`, ..."
- 360-366, three "so" clauses in a row and ragged wrapping: "The project root is nowhere on the path, so the search ... fails" -> "With the project root nowhere on the path, the search ... fails"; paragraph rewrapped at about 70 columns
- 374-375, inverted causality: "Because a module inside a package runs as a member of that package, you run it with `-m`." -> "A module inside a package works only as a member of that package, so run it with `-m`."
- 442-443, "and" joining two subjects in contrast: "`undeclared` therefore joins `public`, and `_helper` and `_internal` stay out" -> two sentences
- 501, "and" standing in for a consequence: "Appending changes that object, and both names show the new item" -> "..., so both names show the new item"
- 504-507, misattributed cause: "The script's name still references the first list, so the `append()` at `[1]` changes the second list" -> "The `append()` at `[1]` goes through the module's name, so it changes the second list. The script's name still references the first list, which stays as it was." (checked against `exercise_7.py`: the append is `plugin_list.plugins.append(...)`)

## Considered and declined

- 145 and 499, 504, bold subgoal labels ("**Import from the parent package.**", "**Share one list between two names.**", "**Replace the module's list.**"): §15/§16 inline headers by shape, but they are the deliberate subgoal-label convention across the Solutions files (commit 85f6ce4d); only the one label that misnamed its paragraph changed.
- 299, "where the two names really are different files": §34, but the sentence names the contrast (one file on Windows, two on Linux), the recurring keep.
- 368, "fixes both problems at once": "fix" in its repair sense, which the global rule keeps.
- 296, "The case check is deliberate, and PEP 235 says why.": two subjects joined by "and", but the second clause continues the first claim rather than contrasting with it; kept.
- 510-515, the closing paragraph of exercise 7 restates "The `from` import shares the module's object" from the hint: the hint and the solution are separate steps of the reveal ladder, so a reader who opens only the solution needs the sentence.
- 243-248, exercise 3's explanation repeats the hint's "binds the name and defers" wording: same reason as the previous item.
