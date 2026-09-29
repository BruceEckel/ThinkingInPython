> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 01_Introduction (2026-09-29)

The chapter has no listings and no Solutions file, so the editing pass is a claims check.
I checked each statement about the book against the place it describes:
`build_site.PARTS` for the five parts,
the chapter list for each part's summary,
chapters 08, 14, 18, 21, 24, 33, 42, 43, 44, 45, 46 and both appendices for what the text says of them,
`tools/run_one_example.py` and `tools/tasks.py` for `tip run-one`,
`README.md`, `CONTRIBUTING.md`, and `LICENSE.md` for the repository claims,
and every external link (all nine resolve, and the README's `#setup` anchor exists on GitHub).
An AST count over `build/examples` confirms the type-hint claims:
chapters 04, 05, and 07 annotate no function,
and from chapter 08 on every function in every listing is annotated.
`uv run tip verify-ch CH=01` passes 14 of 14.

The two standing rejections in `deep_review_db.md` hold:
"wrote a message" is untouched, and "AI Trigger Warning" stays where it is.

## Applied directly

- "How the Book Fits Together", Part V: the text named one appendix.
  The book has two, so the paragraph now says "Two appendices follow"
  and adds a clause for Appendix B, An Effect Checker.
- Same paragraph: "`stateless`" in code font was the only such form in the book.
  Chapters 44, 46, and 47 write "Stateless" on 90 lines, capitalized and without code font.
  Now "Stateless".
- Same paragraph: "the full generator protocol on which such tracking depends"
  said that Effect tracking depends on generators.
  The languages chapter 44 surveys track Effects without them, and so does Appendix A.
  Stateless is the thing built on generators (chapter 46: "Stateless builds on generators").
  Now "Another develops the full generator protocol.
  The last two put both to work with Stateless,
  a library that builds Effect tracking on generators and brings it to Python today."
- Part III: "A short chapter then introduces the design-patterns movement itself."
  Chapter 21 is 4,500 words since the Coupling section joined it,
  longer than 27 of the book's 49 chapters.
  Now "The next chapter introduces the design-patterns movement",
  which also drops the "itself".
- Part III: "Learning to ask those questions..." sat one sentence away from the questions it points to.
  It now follows them directly,
  and the two sentences that describe the rest of the part run together.
- "The Examples": `tip` appeared with no introduction,
  a paragraph before the README is mentioned.
  The sentence now names it as the task runner that comes with the repository,
  and the setup paragraph says the README's instructions include installing it.
  The command stays `tip run-one <name>`, per commit 02ce3b12.

## Findings for your decision

### "No reproduction without permission" contradicts the license sentence before it

"Copyright" says the book carries CC BY-NC-ND 4.0,
"you may share it unchanged, with attribution, for noncommercial use."
The next sentence says "no reproduction without permission."
Sharing a book unchanged is reproducing it, and the license grants that without asking.
`LICENSE.md` agrees with the license:
the book "can be reproduced on other web sites, etc., as long as you attribute it,"
and the restriction it states is narrower:
"This book or a derivative work cannot be published by a publisher without a contract with the author."

I would replace the sentence with the restriction `LICENSE.md` states:

> It is freely readable online.
> Commercial publication requires a contract with me.

The same phrase is in the site footer (`tools/build_site.py`, line 82)
and the EPUB's rights line (`tools/build_epub.py`, line 794),
so a change here should reach those two strings as well.
I left all three alone because the wording of a rights statement is yours to choose.

[] Reject

## Considered and declined

- "Python seems to be the most popular language for AI-generated code" has no source.
  It is hedged ("seems", "at the time of this writing") and sits in a personal section,
  so a citation would change the register.
- "Static Types is the one Part I chapter the rest of the book assumes":
  chapters 09 and 10 are also in Part I and later chapters use `ClassVar` and cleanup.
  The sentence gives advice to a reader who skips Part I,
  and both later topics are re-explained where they are used.
- "A helper that more than one chapter uses carries a `utils/` path":
  `utils/fetch_demo.py` is imported by chapter 19 alone.
  The sentence does not claim the converse, so it stands.
- "Solutions live in the `Solutions/` directory" could also name `SolutionsCode/`,
  the runnable copies.
  The README covers both, and the introduction is long enough.
- "These come from workshops, where pairs work through them at a keyboard":
  only you know whether that holds for the current exercise set. Left as written.
