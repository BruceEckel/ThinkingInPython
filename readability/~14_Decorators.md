[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/14_Decorators.md`

This chapter reads as human technical prose throughout.
The vocabulary is clean (no Tier 1A cluster, no significance inflation, no
generic conclusion, no boldface or bullet padding), sentence lengths vary, and
the explanations advance rather than restate.
Three small findings, none structural.

[] Reject

**Section:** Decorators That Take Arguments (first line after the `repeat.py` listing)
**Pattern:** §7 Overused "AI Vocabulary" Words, Tier 1A (P1)

Current:
> The return type is worth unpacking:

Proposed:
> The return type is worth breaking down:

Why: "unpacking" is on the Tier 1A replace-on-sight list, and "worth unpacking"
is the stock form of it.
"Breaking down" is the table's own replacement and keeps the sentence's length
and rhythm.

***

[] Reject

**Section:** A Limitation: Methods Need a Descriptor (first sentence)
**Pattern:** §34 Real/Actual Adjective Inflation (P1)

Current:
> The class form has one real limitation:

Proposed:
> The class form has one limitation:

Why: "real" is a bare intensifier here with no contrast named in the sentence;
the contrast it gestures at ("mostly a matter of taste") arrives 66 lines later
in a different section.
Minor on its own, but the chapter already uses "the real decorator," "really
calls," and "the real cause" elsewhere, and this is the one instance where
deleting the word costs nothing.

***

[] Reject

**Section:** A Class Decorator with State (lead-in above `count_calls.py`)
**Pattern:** §29 Fragmented Headers (P2)

Current:
> Here is a class-based decorator that counts calls.
> It keeps the count on the instance:

Proposed:
> This decorator counts calls and keeps the count on the instance:

Why: the first sentence restates the heading ("A Class Decorator with State")
before the content starts, and the two sentences carry one idea between them.
Borderline: this is an ordinary book lead-in, and the only cost of leaving it is
one redundant clause.
