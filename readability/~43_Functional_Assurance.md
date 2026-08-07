[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/43_Functional_Assurance.md`

This chapter reads as human writing throughout.
A full sweep of the Tier 1A/1B/2/3 vocabulary tables turned up exactly zero hits,
there is no boldface, no emoji, no curly quotes, no spaced ` -- `,
no banned repo strings, and no rule-of-three padding.
Sentence and paragraph lengths vary, and the concrete detail
(`ProcessPoolExecutor`, Dafny, Hoare logic, Lean/Idris/Rocq, the shrinking behavior)
is specific enough that none of it is portable to another subject.

What is left is one recurring habit rather than a pattern cluster:
short restatement sentences that re-say the claim just made,
and metadiscursive tack-ons that point back at the chapter's own opening.
The chapter ties back to its opening question five times
(lines 48, 69, 148, 168, 272), and two of those are load-bearing while the others
are tack-ons. Everything below is P2 polish; there are no P0 or P1 findings.

***

[] Reject

**Section:** Referential Transparency (lines 46-48)
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> This property lets you check parts of a program,
> and sometimes prove them correct,
> and it connects back to this chapter's opening question about what counts as "what works."

Proposed:
> This property lets you check parts of a program,
> and sometimes prove them correct.

Why: The third clause is a tack-on that tells the reader a connection exists instead of making one, and it stretches the sentence into an `and ... and ...` chain. The "An Assurance Spectrum" section opens by returning to that same question properly, so nothing is lost.

***

[] Reject

**Section:** Declarative Style (line 71)
**Pattern:** §32 Aphorism Formulas (P2)

Current:
> Declarative code says less and means more.

Proposed:
> Cut this sentence.

Why: The very next sentence ("By naming the result instead of the steps, you hand the reader your intent and give the runtime freedom to choose how to deliver it") states the same claim concretely, so the chiasmus is a punchline sitting on top of its own explanation. This paragraph already says the idea three times before it; cutting one of the abstract restatements leaves the concrete ones intact.

***

[] Reject

**Section:** An Assurance Spectrum, list item 2 (line 161)
**Pattern:** §11 Elegant Variation / §70 Interpretive Metadiscourse (P2)

Current:
>    Types are propositions and programs are their proofs.

(The line is indented three spaces as a continuation of numbered item 2.)

Proposed:
> Cut this line.

Why: It restates "A type signature is a small theorem, and the function body is its proof" two lines earlier with a different pair of nouns; the linked Curry-Howard name already tells a reader where to look up the formal slogan. Borderline: the two phrasings sit at different levels of formality, so if the technical wording is the one you want, the earlier "small theorem / its proof" sentence is the better cut.

***

[] Reject

**Section:** An Assurance Spectrum, list item 3 (lines 167-168)
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
>    It works to falsify it,
>    which is the falsifiability the chapter's opening requests.

Proposed:
>    It works to falsify it,
>    which is the falsifiability the opening asked for.

Why: An opening does not "request" anything, and "this chapter's opening" is redundant inside the chapter. Borderline: this is a wording fix, not a pattern removal, and the tie-back itself is worth keeping since falsifiability is the point of this rung.

***

[] Reject

**Section:** Property-Based Testing (line 214)
**Pattern:** §26 Hyphenated Word Pair, consistency (P2)

Current:
> including awkward ones a handwritten loop misses,

Proposed:
> including awkward ones a hand-written loop misses,

Why: The chapter spells the compound "hand-written" four lines above ("Hypothesis turns the hand-written loop into a declaration") and again in exercise 2 ("a hand-written insertion sort"); this is the only unhyphenated instance. Consistency fix, not an AI tell.

***

[] Reject

**Section:** Property-Based Testing (lines 233-235)
**Pattern:** §9 Negative Parallelisms and Tailing Negations (P2)

Current:
> When a law fails, Hypothesis does not only report the failing input.
> It shrinks it to the smallest example that still fails,
> so the bug surfaces as the clearest case rather than a random one.

Proposed:
> When a law fails, Hypothesis reports the failing input and shrinks it to the smallest example that still fails,
> so the bug surfaces as the clearest case rather than a random one.

Why: "does not only X. It Y" is the "not just X, it's Y" shape split across two sentences; stating both behaviors positively is shorter and keeps every claim.
