# Deep review: 01_Introduction.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Explain the `#:` output marker in "The Examples"

**Kind:** teaching
**Where:** section "The Examples" (line ~175, after "the output shown is the output it produces.")
**Problem:** The `#:` convention is explained only in chapter 2 (`02_Tour.md`, "The `#:` comments are particular to this book"), and the Introduction tells a Python-experienced reader that Part I "is for programmers coming to Python from another language. If you already know Python, you can skim for topics you don't know, or skip it altogether." A reader who takes that advice meets `#: affirmative` lines in chapter 11 onward with no idea whether they are output, assertions, or a doctest dialect. "The Examples" is where a reader looks for reading conventions, and it already explains the sibling convention (the `# tracer.py` filename comment) that chapter 2 also explains.
**Proposal:** Add after "and the output shown is the output it produces.":

> Output appears inside the listings as comments beginning with `#:`,
> one line of output per marker,
> placed directly after the statement that produced it.
> A `print("affirmative")` followed by a line reading `#: affirmative` means the program prints `affirmative` at that point.
> The build regenerates these markers from a real run,
> so they cannot drift from what the code prints.

Prose only, with no fenced block: a block whose first line is a `# name.py` comment would be extracted as a new example, and a bare `if.py` would collide with chapter 2's.
Alternative: put this in the opening paragraph of "The Examples" instead, ahead of the filename-comment paragraph, since a reader hits `#:` lines before they care where the file lives.
**Cost:** none. Chapter 2 keeps its own explanation, which is the right depth for a first-time reader; this is the skimmer's version.

---

## 2. "Early chapters omit type hints deliberately" is not quite true

**Kind:** prose
**Where:** section "The Examples" (line ~160)
**Problem:** Two listings before chapter 8 carry annotations: `tstrings.py` in `02_Tour.md` (`message: Template`, `def shout(template: Template) -> str`, `parts: list[str]`) and `ellipsis_placeholder.py` in `04_Control_Flow.md` (`def not_implemented_yet() -> None`). A reader who takes the sentence literally and then meets `-> str` on page ten wonders whether they missed something. Chapters 3, 5, 6, and 7 do hold the line.
**Proposal:** Soften to "Early chapters mostly omit type hints, until [Static Typing](08_Static_Typing.md) introduces the syntax."
Alternative: strip the annotations from the two listings instead. Not recommended for `tstrings.py`, where `Template` and `Interpolation` are the point of the example and the annotation is doing real explanatory work.
**Cost:** none.

---

## 3. Part I's contents list skips three of its nine chapters

**Kind:** prose
**Where:** section "How the Book Is Organized" (line ~122)
**Problem:** Part I runs 02-10 (`build_site.py` puts Part II at 11), so it includes Control Flow, Class Attributes, and Cleanup. The sentence lists "syntax, containers, functions, modules, classes, and static typing," which stops at chapter 8. A reader deciding whether to skip Part I skips `__del__`, context-managed cleanup, and `ClassVar` without knowing they were in there. Every other part's summary names everything in it.
**Proposal:** "Part I, *Foundations*, is a fast tour of the language: its syntax, containers, control flow, functions, modules, classes, static typing, class attributes, and object cleanup."
**Cost:** none.

---

## 4. "a complete program" mislabels the modules and test files

**Kind:** prose
**Where:** section "The Examples" (line ~164)
**Problem:** "Every code block that begins with a filename comment, like `# tracer.py`, is a complete program." Many listings are importable modules with no top-level demo (the book's own rule keeps demos out of importable modules), and `# test_tracer.py` blocks are run by `pytest`, not executed as programs. A reader who tries `python` on one of these and sees no output concludes the book is wrong.
**Proposal:** "Every code block that begins with a filename comment, like `# tracer.py`, is a complete file rather than a fragment. Most run on their own; some are modules that another listing imports, and a `test_*.py` file is run by `pytest`."
**Cost:** none.

---

## 5. The assurance spectrum ends in formal proof, not property-based testing

**Kind:** prose
**Where:** section "How the Book Is Organized", Part IV paragraph (line ~149)
**Problem:** The Introduction describes Part IV as ending with "a spectrum of assurances that ends in property-based testing." Chapter 43's spectrum has four rungs, and property-based testing is the third; the top is formal proof with Lean, Idris, and Rocq. The chapter's *sections* do end on property-based testing, so the sentence is defensible about the prose order and wrong about the spectrum.
**Proposal:** "and a spectrum of assurances that runs from local reasoning up to machine-checked proof."
Alternative: "and a spectrum of assurances whose practical top is property-based testing," which keeps the emphasis on what the reader can use.
**Cost:** none.

---

## 6. Move "AI Trigger Warning" after "How the Book Is Organized"

**Kind:** structure
**Where:** section "AI Trigger Warning" (lines 54-114)
**Problem:** Sixty lines of how the book got written sit between "Who This Book Is For" and "How the Book Is Organized," which are the two sections a reader opens an introduction to find. The reader is told who the book is for, then asked to absorb a 2008-to-2026 history and a position on AI, then finally told what is in the book. The AI section is worth reading, but it answers a question the reader has not asked yet.
**Proposal:** Move it to sit after "How the Book Is Organized" and before "The Examples," so the orientation runs audience, contents, then provenance. The section text is unchanged.
Alternative: move it to the end, before "Resources," treating it as an afterword to the introduction. Or leave it where it is, on the argument that a disclosure the title calls a warning belongs before the reader invests.
**Cost:** none mechanical. No chapter links to a heading in this chapter, and `heading_links.py` confirms no anchor points here.

---

## 7. Open on the thesis, not on the audience

**Kind:** structure
**Where:** opening paragraph (lines 3-6)
**Problem:** The first sentence names the audience, and "Who This Book Is For" names the same audience twenty lines later in more detail ("the programmer who already knows how to program," "This is an intermediate-to-advanced book"). The strongest sentence in the chapter, "It is about developing the judgment to choose the smallest thing that works," is buried under that duplication and is weakened by opening with a pronoun.
**Proposal:** Cut the opening two lines and start the book with "This book is about developing the judgment to choose the smallest thing that works. You build that judgment through insights, idioms, and patterns." "Who This Book Is For" already carries everything the cut sentence said.
**Cost:** none. The cut sentence's one unique phrase, "who can learn a programming language through an overview," is close to the existing "An introductory book must describe everything in lock step ... This one does not," so nothing is lost; fold it into that list item if you want it kept.

---

## 8. The Exercises section tells a solo reader the exercises are not for them

**Kind:** prose
**Where:** section "Exercises" (lines 185-198)
**Problem:** "These are meant for a workshop, worked in pairs at a keyboard, not left for solitary homework" reads as a dismissal to the reader most likely to be holding the book, who is alone. The next paragraph then addresses that same solo reader ("Try the exercise yourself before reading the solution"), so the intent is clearly to describe the exercises' origin, not to exclude anyone.
**Proposal:** "These come from workshops, where they are worked in pairs at a keyboard. They are short enough to do on your own, and they are worth doing that way."
**Cost:** none.

---

## 9. Say where the abandonment message appeared

**Kind:** prose
**Where:** section "AI Trigger Warning" (line 59)
**Problem:** "Eventually I even wrote a message confirming I was not going to complete it." The reader cannot tell whether this was a blog post, a note on the book's page, or a mailing-list reply, and a reader who followed the original project may have seen it.
**Proposal:** Name the place, e.g. "wrote a note on the book's web site confirming I was not going to complete it."
**Cost:** none. Only the author knows the actual venue, so this one needs a fact rather than a rewrite.

---

## 10. Mention the license in "Resources"

**Kind:** prose
**Where:** section "Resources" (line ~202)
**Problem:** The book says "The book is free" in the AI section, which a reader may read as public domain. `CONTRIBUTING.md` licenses it CC BY-NC-ND 4.0, and the chapter never says so. A reader who wants to translate an example or reuse a chapter has nothing to go on.
**Proposal:** Add one line after the thinkinginpython.com sentence: "The text is licensed [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/); the source repository's `CONTRIBUTING.md` has the details."
**Cost:** none.

---

## Already fixed directly (no decision needed)

- line ~120 and ~146: The chapter said "The book is organized into four parts," and folded the Effects chapters into the Part IV paragraph ("It then takes up Effects, everything a program does that a pure function cannot"). `tools/build_site.py`'s `PARTS` gained a fifth part on 2026-08-03 (commit d8110cb, "Added Part V Effects", starting at chapter 44), so the generated site shows five parts while the Introduction, last given its part nomenclature on 2026-07-24 (c1f10fb), still promised four. Changed "four parts" to "five parts" and split the paragraph: Part IV now "covers pure functions, ...", and a new paragraph reads "Part V, *Effects*, closes the book with everything a program does that a pure function cannot." The three sentences that follow it (chapters 44, 45, 46-47) were already describing Part V and are unchanged. This chapter is the only place in `Chapters/` that names a part, so nothing else needed updating.

## Checks run (all clean, nothing to report)

- `heading_links.py` and `banned_phrases.py` on this chapter: pass, before and after the edit.
- `reflow_prose.py --diff`: zero paragraphs would change, before and after the edit.
- Every cross-reference resolves: `24_Singleton.md` (opens with "A Module Is Already a Singleton"), `33_Visitor.md` (has "The Pythonic Visitor: singledispatch"), `08_Static_Typing.md`, `14_Decorators.md#maintaining-the-wrapped-interface` (the `# tracer.py` block sits under that heading), `Examples/14_Decorators/tracer.py`, `Examples/utils/result.py`, `Solutions/`, `CONTRIBUTING.md`, `tools/README.md`, and the README's `#thinking-in-python` anchor all exist.
- Part II, Part III, Part IV, and Part V contents descriptions each match the chapters in their range.
- "Most chapters end with a short Exercises section": 44 of 47 chapters have one.
- The chapter has no listings, so there is nothing to type-check, lint, or run.
- Watch-list sweep: no tier-3 phrases. The tier-2 hits (`already`, `even`, `never`, `only`) are all in the author's own voice and read correctly where they sit.
