[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: Chapter 05, Functions

This chapter reads as human technical prose throughout.
No Tier-1A vocabulary, no significance inflation, no signposting, no chatbot artifacts,
no curly quotes, no spaced ` -- `, and no banned phrases.
Sentence length varies, and the short sentences carry information rather than manufacture rhythm.
The only findings are two small restatement redundancies and one micro-trim, all P2.

***

[] Reject

**Section:** Default and Keyword Arguments (paragraph after `mutable_default.py`)
**Pattern:** Treadmill effect / restated clause (Structure and Rhythm Tests) (P2)

Current:
> `__defaults__` holds the tuple of default values stored on the function object,
> and it is the same list both calls appended to.

Proposed:
> `__defaults__` holds the tuple of default values,
> and it is the same list both calls append to.

Why: the sentence immediately before it already establishes that the default lives on the function object,
so "stored on the function object" repeats a fact one line old.

***

[] Reject

**Section:** Default and Keyword Arguments (same paragraph)
**Pattern:** Filler / redundant qualifier (§23 Filler Phrases) (P2)

Current:
> This behavior commonly confuses newcomers to the language.

Proposed:
> This behavior commonly confuses newcomers.

Why: in a Python book, "to the language" is understood; the trailing phrase adds no information.
Borderline: this is a micro-trim, not a tell, and the sentence is fine as written.

***

[] Reject

**Section:** Positional-Only and Keyword-Only Parameters (last paragraph)
**Pattern:** Treadmill effect / restated clause (Structure and Rhythm Tests) (P2)

Current:
> Marking a parameter positional-only also keeps its name out of the method's contract.
> That matters when a subclass overrides a method.
> Since the name is not part of the interface,
> the subclass can rename the parameter, and a type checker will not object.

Proposed:
> Marking a parameter positional-only also keeps its name out of the method's contract.
> That matters when a subclass overrides a method:
> the subclass can rename the parameter, and a type checker will not object.

Why: "Since the name is not part of the interface" restates "keeps its name out of the method's contract" from two lines earlier;
the colon carries the same causal link without the repetition.
