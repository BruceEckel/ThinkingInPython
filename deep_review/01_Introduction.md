[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Line numbers below refer to `Chapters/01_Introduction.md` *after* the six fixes
this review already applied (see the end of this file for the applied list).

---

[] Reject

**"Who This Book Is For", lines 37-41: the advice comes before the thing it
advises about.**

The section currently reads:

> If a language feature is new to you, look it up as you go.
> You should be comfortable with:
>
> - Functions, classes, objects, and inheritance.
> - Containers: lists, dictionaries, tuples, and sets.

The reader is told what to do about a gap before being told where the gaps
are allowed to be. Swap the two so the prerequisite list lands first:

> You should be comfortable with:
>
> - Functions, classes, objects, and inheritance.
> - Containers: lists, dictionaries, tuples, and sets.
>
> If a language feature is new to you, look it up as you go.

Cost: none. Nothing links to this section and no wording elsewhere depends on
the order.

---

[] Reject

**"Who This Book Is For", lines 45-49: the setup/tooling paragraph is in the
wrong section, and two of its three sentences need work.**

```
The book is about the language, not the tooling around it.
Fortunately, `uv` and other tools greatly simplify setup,
so you don't need to spend time on it.
The repository's [README](https://github.com/BruceEckel/ThinkingInPython#setup)
gives detailed setup instructions.
```

Three problems:

1. The section is about the reader, and these three sentences are about the
   repository. "The Examples" (which already points at the source repository
   and at `tools/README.md`) is where a reader looks for this, and it is where
   a reader who skipped the front matter will look for it later.
2. "Fortunately" is a throat-clearing opener.
3. "so you don't need to spend time on it" — "it" can read as setup or as the
   tooling the previous sentence just said the book is not about.

Recommended: keep sentence 1 where it is (it belongs with "You do not need to
know design patterns, metaclasses, or type checking"), and move sentences 2
and 3 into "The Examples", next to the existing `tools/README.md` sentence at
line 173, rewritten as:

> `uv` and other tools make setup short.
> The repository's [README](https://github.com/BruceEckel/ThinkingInPython#setup)
> has the instructions,
> and `tools/README.md` explains how to build the book and run the examples
> yourself.

Alternative if you would rather not move anything: leave the sentences where
they are and just replace "Fortunately, `uv` and other tools greatly simplify
setup, so you don't need to spend time on it." with "`uv` and other tools make
setup short." Cost either way: none, nothing cross-references this text.

---

[] Reject

**Lines 53-54 and 60-62: "most chapters are self-contained" plus "you can skip
[Part I] altogether" sends an experienced Python reader past the one Part I
chapter the rest of the book leans on.**

`08_Static_Typing.md` is linked from fourteen chapters numbered above 10 —
more than every other Part I chapter combined (05: six, 07: five, 09: three,
04: three, 02: two, 03: two, 10: one, 06: none). The Introduction also
promises "You do not need to know ... type checking. This book covers them,"
and covering it is exactly what chapter 8 does. A reader who takes "skip it
altogether" literally then meets annotated code from chapter 11 onward with
the syntax never introduced.

Proposed: add one sentence after line 62.

> If you skip [Part I], come back for [Static Typing](08_Static_Typing.md):
> every chapter after it annotates its examples,
> and it is the one Part I chapter the rest of the book assumes.

Cost: one sentence in the organization section; no other text changes.

---

[] Reject

**Lines 72-80: the Part III summary skips chapter 21, *The Pattern Concept*.**

The paragraph goes straight from "opens by stepping back to question object
orientation" (chapter 20) to "The part then works through the classic design
patterns." Chapter 21 sits between them and is where the design-patterns
movement, the GoF, and the book's own thesis about patterns dissolving into
the language are introduced. It is the chapter the rest of Part III argues
against, so leaving it out of the map understates the part.

Proposed: insert after line 73, before "The part then works through...":

> A short chapter then introduces the design-patterns movement itself,
> and the question the rest of the part keeps asking.

Cost: one sentence. No cross-references name this paragraph.

---

[] Reject

**Line 76: filler adverb and a person shift.**

> I consistently ask what problem we are solving and whether the language
> already does the pattern's job.

"consistently" adds nothing that the surrounding sentences do not already
imply, and the sentence moves from "I" to "we" and back to a "you"-addressed
paragraph. Proposed:

> I ask what problem you are solving and whether the language already does
> the pattern's job.

---

[] Reject

**Line 87: the Part V opener has an odd object.**

> Part V, *Effects*, closes the book with everything a program does that a
> pure function cannot.

"closes the book with everything a program does" reads as if the part is
being handed a list of everything. Proposed:

> Part V, *Effects*, closes the book by covering everything a program does
> that a pure function cannot.

---

[] Reject

**Line 91: name the library.**

> The last two put that idea to work with a library that brings Effect
> tracking to Python today.

Chapters 46 and 47 are titled *Stateless* and *Stateless in Practice*, so the
library's name is already in the table of contents; withholding it here makes
the two chapter titles opaque to a reader scanning the map. Proposed:

> The last two put that idea to work with `stateless`,
> a library that brings Effect tracking to Python today.

---

[X] Reject

**"AI Trigger Warning" (lines 93-152): consider moving this section to the end
of the chapter.**

It is the longest section in the Introduction (about 57 lines, a quarter of
the chapter) and it sits between "How the Book Is Organized" and "The
Examples" — that is, between the two sections a reader consults to start
reading. A reader working out how to use the book hits a personal essay in the
middle of the instructions.

Proposed: move the whole section, unchanged, to after "Resources" so the
chapter runs Who This Book Is For → How the Book Is Organized → The Examples →
Exercises → Resources → AI Trigger Warning. Nothing in the book links to
`01_Introduction.md` at all (checked across `Chapters/`, `tools/`, `Makefile`,
`README.md`), so the move costs nothing but the ordering decision, which is
yours: keeping the AI disclosure early is a defensible choice on its own
terms, which is why this is a proposal and not an applied fix.

---

[X] Reject

**Line 98: "wrote a message" is vague.**

> Eventually I even wrote a message confirming I was not going to complete it.

A reader cannot tell where: a blog post, a note in the repository, a mailing
list reply. Naming it (and linking it, if it is public) makes the sentence do
its job. Only you know which it was, which is why this is a report and not a
fix.

---

[] Reject

**Line 103: "material from writing and presentations" is vague.**

The repository `README.md` says the same thing concretely: "I began going back
through my Pycon presentations and blog posts and adding those." Proposed:

> and I began adding material from my blog posts and presentations.

This also sets up line 70's "Many of these chapters came from presentations
I've given, mostly at PyCon."

---

[] Reject

**Lines 120 and 122: two consecutive sentences open with "But".**

> But I was either unable to implement it, or it seemed too hard,
> so I didn't do it.
> But with AI I can explore and often implement every whim, ...

Both contrasts are real, so the fix is to carry one of them differently rather
than delete the word. Proposed for line 120:

> I was either unable to implement it, or it seemed too hard,
> so I didn't do it.

The contrast with the preceding "I would get a good idea about something" is
carried by "so I didn't do it", and line 122's "But" then lands with full
force. (`proselint.But` is disabled in `.vale.ini`, so no gate catches this.)

---

[] Reject

**Lines 175-176: the build-system sentence omits linting.**

> The book's build system extracts the examples, then type-checks
> (with Astral's `ty`), runs, and tests them.

It also lints every example with `ruff` at a 70-column limit, which is a
visible property of the listings a reader is about to read (short lines, no
double blank lines) and worth one word. Proposed:

> The book's build system extracts the examples, then type-checks
> (with Astral's `ty`), lints, runs, and tests them.

---

[] Reject

**Lines 180-186 (already partly fixed): consider adding the case that trips
readers up.**

The applied fix corrected the false claim that each marker sits "directly
after the statement that produced it" — `validate_output.py` compares a run of
`#:` lines against everything printed since the previous run, and markers only
ever sit at column 0, so output from inside a loop or from an `import` lands
below the block, not beside the line that produced it. `import_once.py` in
[Singleton](24_Singleton.md#a-module-is-already-a-singleton) is the clearest
instance: `#: config body runs` comes from `import config` three lines above
the `print()` it sits under.

If you want the point made explicitly rather than left to be inferred, add
after line 183:

> Output produced inside a loop, or by an `import`,
> therefore appears in the run of markers below the block,
> not next to the line that produced it.

Left as a proposal because the Introduction is deliberately brief and the
corrected wording is already accurate without it.

---

[] Reject

**Line 191: the Introduction's `## Exercises` heading holds no exercises.**

Every other chapter's `## Exercises` section contains numbered exercises; this
one describes the convention. A reader jumping to the heading (or scanning the
site's per-chapter navigation) expects exercises and gets an explanation.
`tools/build_epub.py`'s own comment counts "44 chapters each end in `##
Exercises`" while `grep -c '^## Exercises' Chapters/*.md` finds 45 — this
section is the extra one.

Proposed: rename the heading to `## The Exercises`, which also parallels the
`## The Examples` section directly above it. Nothing links to
`01_Introduction.md#exercises` (checked repo-wide), and heading ids are
namespaced per chapter in the EPUB build, so the rename is free.

---

[] Reject

**Lines 215-223: the Resources bullet list has no lead-in.**

The paragraph above it is about where the book lives and how it is licensed,
then six unannounced bullets appear. Proposed: add one line before the list.

> Places worth knowing about:

---

## Applied in this pass (no action needed, listed for the record)

1. Line 48: the README link pointed at `#thinking-in-python` (the page title)
   while the sentence promises setup instructions; retargeted to `#setup`.
2. Lines 53-54: "Most chapters are self-contained, so you can read straight
   through, or jump to a chapter that interests you." The "so" claimed
   self-containment as the reason you can read straight through, which it is
   not; it is the reason you can jump. Reordered to
   "You can read straight through, or jump to a chapter that interests you,
   since most chapters are self-contained."
3. Line 100: "after having people mention the online book to me" →
   "after people mentioned the online book to me".
4. Line 151: "If it's not already true, I think most programmers will
   regularly use AI." → "I think most programmers will regularly use AI, if
   they don't already." The trailing condition was modifying a future-tense
   clause from in front of it.
5. Line 156: "uses type hints throughout" contradicted the very next sentence,
   "Early chapters mostly omit type hints." Dropped "throughout". (Verified:
   annotations appear in 1/10 of chapter 2's files, 0/19 of chapter 3's, 0/16
   of chapter 4's, 2/11 of chapter 5's, 0/15 of chapter 6's, 3/14 of chapter
   7's, then 12/13 of chapter 8's and effectively all of 10-12's — the
   "early chapters mostly omit them" claim is right and the "throughout" was
   the wrong half.)
6. Lines 180-183: "placed directly after the statement that produced it" was
   false. `validate_output.py`'s own docstring: "Each `#:` block is compared to
   the stdout produced by the top-level code above it (since the previous `#:`
   block)", and markers match only at column 0. Replaced with "A run of markers
   shows everything the code above it printed since the previous run, in
   order."

## Verified, no change needed (listed so a later review does not re-check)

- All five part summaries match `tools/build_site.py`'s `PARTS` ranges
  (I: 02-10, II: 11-19, III: 20-39, IV: 40-43, V: 44-47) and the chapters in
  them, with the single omission reported above (chapter 21).
- "A [Singleton](24_Singleton.md) is a module" matches chapter 24's "A Module
  Is Already a Singleton". "A [Visitor](33_Visitor.md) is a function that
  dispatches on type" matches chapter 33's "The Pythonic Visitor:
  singledispatch".
- `# tracer.py` is in `14_Decorators.md` under "Maintaining the Wrapped
  Interface" and extracts to `Examples/14_Decorators/tracer.py`; `#
  utils/result.py` is in `42_Functional_Error_Handling.md` and extracts to
  `Examples/utils/result.py`. Both anchors pass `heading_links.py`.
- `tools/README.md`, `CONTRIBUTING.md` (which does carry the CC BY-NC-ND 4.0
  details), and `Solutions/` all exist as described.
- Every external link resolves and says what the chapter says it says:
  thinkinginpython.com serves this book, docs.python.org/3.15/whatsnew is live
  (currently labelled 3.15.0rc1), typing.python.org/en/latest/spec/ is the
  type system specification, pythonbytes.fm is a podcast and newsletter.
- No em-dashes, no banned phrases, no watch-list filler
  ("actually"/"simply"/"just"/"leverage"/"robust"/...), and no "promise"
  metaphor. `reflow_prose.py` reports the chapter compliant before and after
  the edits.
- The chapter contains no fenced code blocks, so the house-style listing audit
  and the `ty`/`ruff`/`pytest`/`run_examples` gates have nothing to check here.
