> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/44_Effect_Management.md`

Second review of this chapter.
The findings in `readability/~44_Effect_Management.md` were all accepted and
applied, and none were rejected, so nothing is carried forward.

The deep review that ran just before this one moved "Converting Effectful to
Pure" up ahead of "A Program Can Never Be Pure", renamed "A Taxonomy of
Benefits" to "Two Phases of Effect Analysis", opened the chapter with the
failing-test story, rewrote two sentences in the first paragraph, added a
generators aside, a `print()`-is-still-invisible qualification, a closing
handoff to Part V, and a fifth exercise. Every finding below is in that new
prose or in a seam the moves opened.

---

**Opening: the new cold-open and the paragraph under it now both explain why
purity is hard to verify, in opposite directions.**

The chapter now begins:

> A test you wrote last week starts failing about one run in five.
> ...
> None of that is in any signature on the path.

and then, twenty lines later, after the bulleted list:

> In every one of those cases you can settle the question by reading one function.
>
> What happens when a function you believe is pure calls other functions?

The cold open is a concrete case of the problem. The question after the list is
the same problem stated abstractly. Between them sits a six-item list of things
the book already did, which is the throat-clearing the cold open was added to
displace. As it stands the reader gets the hook, waits through the list, and
receives the hook again as a question.

This is not an argument against the cold open, which is the strongest writing in
the chapter's first page. It is an argument that the question has become the
second telling.

Proposed change: cut the question and let the paragraph continue from the
one-function sentence.

> In every one of those cases you can settle the question by reading one function.
> That stops working as soon as the function calls others.
> If one or more of those have side effects,
> their impurity makes the calling function impure too.

The opening story already asked the question in a form the reader felt, so the
prose can move straight to the answer.

Alternative: keep the question and cut the cold open. I do not recommend it, but
it is the coherent other choice, and it is worth naming because the two are
solving the same problem.

[] Reject

---

**"Two Phases of Effect Analysis": the new heading is accurate and the old one
is still doing its job three lines later.**

The section now opens:

> The initial and most obvious reason to track Effects is parallelism.
> ...
> The same guarantee makes testing trivial.

Those two paragraphs are the benefits the old heading promised. The phases
material begins only at "Think of Effect analysis as a series of phases."

So the rename fixed the mismatch by moving it: the heading now describes the
back half of the section and the front half is orphaned under it.

Proposed change: move the parallelism and testing paragraphs up into the end of
the preceding section, "A Program Can Never Be Pure", which argues that Effects
are the point rather than a defect and has no closing beat of its own. The
benefits paragraph reads as the natural answer to "so why track them at all?"

Then this section opens on "Think of Effect analysis as a series of phases,"
which is what its heading now names.

Alternative, cheaper and less good: retitle again to something covering both,
which is the position the chapter was already in.

I recommend the move. Note the cost, which is real: it makes two structural
edits to a chapter that just had one, and if you would rather let the
reordering settle before moving more, this is a reasonable one to defer.

[] Reject

---

**"Effects by Hand": the new qualification arrives mid-paragraph and interrupts
the delayed-binding point.**

> and its signature says so.
> It says what `greet()` needs, not everything `greet()` might do:
> a `print()` in the body would still be invisible.
> [Effect Management for Python?](#effect-management-for-python)
> returns to that limit.
> This moves the Effects into explicit arguments.
> The bindings are delayed.

The qualification is correct and belongs in the chapter. Where it sits, it
splits "its signature says so" from "This moves the Effects into explicit
arguments," which is the sentence that continues the thought, and the reader
resumes the delayed-binding argument three sentences later having been sent to a
section 300 lines away.

Proposed change: move the qualification to the end of the paragraph, after the
delayed-binding point lands.

> and its signature says so.
> This moves the Effects into explicit arguments.
> The bindings are delayed.
> ...
>
> The signature says what `greet()` needs, not everything `greet()` might do:
> a `print()` in the body would still be invisible.
> [Effect Management for Python?](#effect-management-for-python)
> returns to that limit.

A caveat placed after the claim reads as a boundary on it. Placed inside the
claim, it reads as a retraction of a claim the reader has not finished hearing.

[] Reject

---

**"Native Effect Management", the generators aside: "Python has a construct"
announces a reveal it then makes.**

> Python has a construct that suspends a computation and hands control to whoever is driving it,
> then resumes it with a value: the generator.

The sentence withholds the name until after the colon, which is §69: the
noun-phrase-then-colon-then-reveal shape. Here the reveal is a word every reader
of this book has known since chapter 23, so the suspense buys nothing and the
delay costs a re-read of the clause to attach it to the right noun.

Proposed change:

> A Python generator does exactly this.
> It suspends a computation, hands control to whoever is driving it,
> and resumes it with a value.
> [Generators](45_Generators.md) covers the full two-way form,
> and it is the mechanism the Python Effect library in
> [Stateless](46_Stateless.md) is built from.

Naming it first also connects the aside to the sentence above it, which is about
what handlers do with continuations.

[] Reject

---

**Closing handoff: "Python cannot give you the language half of that today. It
can give you the library half." states the split twice before naming it.**

> Python cannot give you the language half of that today.
> It can give you the library half.
> The next three chapters build one:

Three sentences to say "the next three chapters build a library version." The
first two are a matched pair whose only content is the contrast between the two
halves, and the chapter has already spent a full section on native versus
library Effect systems, so the contrast is familiar rather than new.

Proposed change:

> Python offers no native version of this, and will not soon.
> The next three chapters build the library version:
> [Generators](45_Generators.md) supplies the mechanism,
> [Stateless](46_Stateless.md) builds the Effect type on top of it,
> and [Stateless in Practice](47_Stateless_in_Practice.md) puts it to work.

"the library version" leans on the section that defined the term rather than
re-deriving it, and the paragraph drops from six lines to five with nothing lost.

[] Reject

---

## Checked and clean

- Zero hits across the §7 Tier 1A, 1B, 2, and 3 vocabulary tables in the new
  prose.
- `banned_phrases.py` and `prose_lint.py` both pass on the chapter.
- No em dashes, no spaced ` -- `, no curly quotes, no boldface outside the
  existing EMS property list, no emojis, no slot-fill placeholders.
- The cold open is a §45 speculative scenario by shape ("A test you wrote last
  week starts failing"). The carve-out applies: it is a concrete instructional
  case with a stated payoff two sentences later, not a "picture a world where"
  opener standing in for an argument. Not flagged.
- The AI-languages restructure moved the reason into the lead-in as the review
  asked. The resulting sentence ("and for their purpose the other two parts are
  liabilities: a host that pins the implementations itself can guarantee what
  generated code is able to do") uses a colon to introduce an explanation rather
  than to stage a reveal, so §69 does not apply.
- Exercise 2's rewrite and its solution were checked against each other: the
  exercise now asks for three wrapping callers and the solution builds
  `session()`, `menu()`, and `main()`, so the counts it reports (five signatures
  edited, three of them mentioning an Effect they never use) are the counts a
  reader will actually get.
- The new "no relation to the TypeScript library of the same name" aside was
  checked for tone against the surrounding catalog of Python libraries; it
  matches the register and answers the double-take the review predicted.
