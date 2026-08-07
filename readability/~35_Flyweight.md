[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/35_Flyweight.md`

This chapter reads as human technical prose, and it is one of the cleanest in the run so far.
A sweep of the Tier 1A, Tier 1B, Tier 2, and Tier 3 vocabulary tables (§7) returned zero hits,
the file contains no boldface, no curly quotes, and no non-ASCII characters at all,
and the explanations stay anchored to checkable specifics
(why `int("...")` beats a literal, why `_value_` must be set in `__new__()`, why a `defaultdict` cannot replace `_pool`).
Three findings, all P2: one restated pair of sentences, one interpretive tag line, and one grammar slip.

***

[] Reject

**Section:** Interning in the Constructor, opening paragraph
**Pattern:** Treadmill effect / restated clause (Structure and Rhythm Tests), plus a grammar slip (P2)

Current:
> A factory function like `tile()` is a visibly different name.
> Its different syntax warns callers that something unusual is happening.

Proposed:
> A factory function like `tile()` has a visibly different name and call syntax,
> which warns callers that something unusual is happening.

Why: A function is not a name, it has one, and "visibly different" in the first sentence and "different syntax" in the second make the same point twice.
The merge keeps both claims (the name and the call syntax) and drops the repetition.

***

[] Reject

**Section:** Intrinsic and Extrinsic State, paragraph beginning "Twenty-four cells, three objects."
**Pattern:** §70 Interpretive Metadiscourse (P2), borderline

Current:
> That is the intrinsic/extrinsic split doing its work.

Proposed:
> Cut this sentence.

Why: The two sentences before it already show the split working, under a heading that names it,
so the line tells the reader what to notice instead of adding anything.
Borderline: in a book that is teaching these two terms, tying the worked example back to the vocabulary is defensible, so this is a reasonable one to decline.

***

[] Reject

**Section:** Flyweights in the Wild
**Pattern:** grammar, wrong object of "into" (no §; skill step 5, "fix the patterns, errors, and tangled passages") (P2)

Current:
> A column of a million country names stores small integer codes into a pool of distinct strings.

Proposed:
> A column of a million country names stores small integer codes that index into a pool of distinct strings.

Why: As written, the codes are being stored *into* the pool, which is the opposite of what the sentence means;
the codes live in the column and point at the pool.
