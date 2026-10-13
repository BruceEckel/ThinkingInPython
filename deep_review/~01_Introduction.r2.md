> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 01_Introduction (2026-10-13)

The chapter has no listings and no Solutions file,
so the editing pass is a claims check.
I checked each statement about the book against the place it describes:
`build_site.PARTS` and the chapter list for the five parts and their summaries,
chapters 11, 14, 18, 24, 33, 39, 40, 42, 43, and both appendices for what the text says of them,
`tools/run_one_example.py`, `tools/tip.py`, and `tools/tasks.py` for `tip run-one`, the short form, and `tip hint`,
`AGENTS.md`, `README.md` (`#setup`, the `tip` install), and `tools/README.md` for the repository claims,
chapters 02 to 08 for the `# type: ignore` and `# ty:` claims,
and the step ladders in every `Solutions/*/README.md` for the solution-steps claim.
All ten external links return 200.
The 2026-09-29 review's live block (the rights sentence) is applied.
`uv run tip verify-ch CH=01 ISOLATED=1` passes 17 of 17 before and after;
`tip prose CH=01` reports no new stranded prepositions, watch words, or positional pointers.
No live blocks.

## Applied directly

- "The Exercises", solution steps: "a hint, then the shape of the code ..., then the full answer"
  described every solution, but 82 of the 360 have no shape step
  (278 `<summary>The shape</summary>` lines against 360 hints),
  since an answer with no function body has nothing to elide.
  Now "then, for most, the shape of the code with its function bodies left out".
- "How the Book Fits Together", appendices: "builds a checker for those annotations,
  as far as one can go without type inference" claimed a maximum the appendix does not claim.
  Appendices A and B both say B "builds the part that needs no type inference".
  Now "builds the part of a checker for those annotations that needs no type inference".
- "The Examples", `# type: ignore` paragraph: the meaning of the comment came last ("Until then, the comment marks ..."),
  after the pointer to chapter 08.
  The meaning now comes first, in chapter 02's terms (the error is deliberate),
  and Static Types "covers type checking in full" rather than "defines it",
  since chapter 02 already explains the comment at its first use.
- "The Examples", first paragraph: it explained three things
  (listings are files in `Examples/`, `utils/` helpers, running one example with `tip`).
  Split at both seams; the third paragraph now names `Examples/utils/` where it had "that path",
  whose antecedent sat in the paragraph before.
- Same paragraph: "Some are modules that another listing imports, and `pytest` runs each `test_*.py` file"
  joined two unlike clauses.
  Now "and the `test_*.py` files hold tests that `pytest` runs", parallel with the first half.

## Considered and declined

- The AI Trigger Warning section: `tip prose` flags "excellent" (line 70) as vague.
  The section is Bruce's first-person account and the prior review left its wording alone; so did this one.
- "Output from inside ... an `import` therefore appears in the group of markers after ... the `import`":
  the marker sits below the whole import block, not directly after the `import` (ruff's `I001`).
  Chapter 06's `package_only.py` shows the reader the shape, and the sentence is true read loosely.
- "Read these four chapters in order. The last two build on the chapters before them."
  gives a reason for two of the four.
  The reason that matters to a reader jumping in is the one given: 46 and 47 need 44 and 45.
- Earlier declines carried forward: the unsourced "most popular language for AI-generated code",
  "the one Part I chapter the rest of the book assumes", the `utils/` converse,
  the workshop-origin sentence, and the standing rejections in `deep_review_db.md`.

## For the session

Nothing. No baseline hits, no cross-chapter errors found.
