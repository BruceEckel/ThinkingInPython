[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/22_Data_Transfer_Objects.md`

This chapter reads as human throughout.
No Tier 1A or Tier 2 vocabulary, no significance inflation, no signposting openers,
no rule-of-three padding (the three-way `SimpleNamespace`/`@dataclass`/`NamedTuple`
comparison is genuine list content), no curly quotes, no spaced ` -- `, no banned strings.
Sentence lengths vary and every paragraph advances the argument.
Two findings only, and one of them is a factual check rather than an AI pattern.

[] Reject

**Section:** A NamedTuple Is Still a Tuple (paragraph after `still_a_tuple.py`)
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> This refines the selection rule.

Proposed:
> Cut this sentence.

Why: The sentence announces what the next two sentences do instead of doing it;
the "Choose ... Choose ..." pair already reads as a refinement of the earlier
"Use `SimpleNamespace` ... a `@dataclass` ... and a `NamedTuple` ..." rule.
Borderline: it is the only explicit link back to that earlier rule, so keeping it is defensible.

***

[] Reject

**Section:** Exercises, item 4
**Pattern:** not an AI pattern, factual check (P0)

Current:
>     Confirm `vars(m)` reports the same four attributes, in the same order,
>     either way.

Proposed:
>     Confirm `vars(m)` reports the same four attributes either way,
>     and note whether they come out in the same order.

Why: The two variants do not produce the same order.
Passing a fourth attribute to the constructor puts it before `more`
(`['info', 'b', 'extra', 'more']`); assigning it after `m.more = 11` puts it after
(`['info', 'b', 'more', 'extra']`).
As written the exercise asks the reader to confirm something that is false,
and the ordering difference is the more interesting observation anyway.
(Verified by running both forms; the leading four-space indentation in the quoted
lines is the exercise's existing indent.)
