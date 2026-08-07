[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/26_Surrogate.md`

This chapter reads clean. It has no Tier-1A/Tier-2 vocabulary hits at all, no boldface,
no curly quotes, no promotional language, and no generic conclusion. The only recurring
structural habit is the "X, not Y" antithesis, which appears eight or more times
("forwards reads, not writes"; "the methods, not the type"; "on the proxy's type, not on
the instance"). Most of those are load-bearing technical distinctions and should stay;
two of them carry no information and are flagged below. One repeated sentence template
between the two test paragraphs is also flagged.

***

[] Reject

**Section:** Proxy (paragraph after `proxy_1.py`)
**Pattern:** §70 Interpretive Metadiscourse (P2) — borderline

Current:
> The loose reading is about what the pattern requires,
> not about how to name your wrapper.

Proposed:
> Cut these two lines.

Why: The sentence tells the reader how to read the preceding claim rather than adding to
it, and the sentence immediately after it does the same job concretely by naming the
*Proxy* / *Adapter* choice. With it cut, the "still" in "the interface is still the
question that separates them" carries the contrast on its own. Borderline: the scoping it
performs is real, just already performed by its neighbor.

***

[] Reject

**Section:** Proxy (final paragraph, after `proxy_identity.py`)
**Pattern:** §32 Aphorism Formulas / fake-profound kicker (P1)

Current:
> A surrogate is verified by using it, not by asking what it is.

Proposed:
> Cut this sentence.

Why: This is the third statement of the same fact in eleven lines: the prose before the
listing already says "Code that calls the method, or probes with `hasattr()`, works on a
surrogate; code that asks `isinstance()` sees only the proxy's own class," and the line
directly above it says "yet neither check recognizes the proxy." Reshaped as a closing
aphorism it adds no information, and the section ends more firmly on the concrete
sentence.

***

[] Reject

**Section:** Kinds of Proxy (lead-in to `test_counting_proxy.py`)
**Pattern:** §61 Template and Slot-Fill Phrases (P2) — borderline

Current:
> Testing hands the counting proxy a small stand-in and confirms the proxy forwards the call with its result,
> and counts only callable accesses:

Proposed:
> The test for the counting proxy uses a small stand-in to confirm that the proxy forwards a call with its result,
> and counts only callable accesses:

Why: The identical template already opens the State test paragraph ("Testing hands the
State surrogate a small stand-in and confirms..."), and the two are the only uses in the
chapter, so the repetition reads as slot-fill rather than as a book convention. Borderline:
if this opener is deliberate boilerplate shared with other chapters, reject it.
