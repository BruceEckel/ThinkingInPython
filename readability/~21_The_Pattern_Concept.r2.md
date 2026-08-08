[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review 2: `Chapters/21_The_Pattern_Concept.md`

Run after the deep-review edits landed, so the new and moved prose gets the
same scan the rest of the chapter got in review 1.
Nothing from review 1 was rejected, so nothing is carried forward.

The chapter still reads as human prose: no §7 vocabulary hits, no curly
quotes, no spaced ` -- `, and the moved sections carry no new tells.
Two findings, both in sentences written during the deep review.

***

[] Reject

**Section:** Design Principles (opening paragraph)
**Pattern:** treadmill restatement, two sentences making the same claim (P2)

Current:
> A pattern is a shape of solution.
> A principle is a test you apply to whatever shape you chose.
> Each one is a claim you can hold a design up against.

Proposed:
> A pattern is a shape of solution.
> A principle is a test you apply to whatever shape you chose:
> a claim you can hold the design up against.

Why: the second and third sentences say the same thing in different clothes
(a test you apply; a claim you hold a design against), so the paragraph
restates itself before reaching the list.
This needs your call rather than mine because each sentence traces to a
different deep-review block you approved: one supplied the pattern/principle
contrast, the other supplied the claim framing for the bullets that follow.
The merge above keeps both jobs in one sentence.
The alternative is to cut the third sentence and let "a test you apply"
introduce the list alone.

***

[] Reject

**Section:** Pattern Taxonomy (the Behavioral bullet)
**Pattern:** §11 repetition, "this book" twice in one sentence (P2)

Current:
> This book contains multiple examples including [Observer](30_Observer.md),
> [State](26_Surrogate.md#state), and [Visitor](33_Visitor.md),
> though *State* appears in this book beside *Proxy*, for reasons given below.

Proposed:
> This book contains multiple examples including [Observer](30_Observer.md),
> [State](26_Surrogate.md#state), and [Visitor](33_Visitor.md),
> though *State* appears beside *Proxy*, for reasons given below.

Why: the sentence opens with "This book contains" and repeats "in this book"
eleven words later.
The second mention adds nothing the first has not established,
and the sentence reads cleanly without it.
