[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: Chapters/28_Function_Objects.md

This chapter reads as human throughout.
A full scan of the Tier 1A/1B/2/3 vocabulary tables returned exactly one hit
(`simply`, line 239), there is no boldface in the prose, no curly quotes, no
non-ASCII characters at all, no signposting, no hedge stacks, and the sentence
lengths vary the way a person's do.
What is left is a small amount of restatement near the end of the event-bus
section, plus one dangling modifier.
Four findings, all P2, three of them borderline.

***

[] Reject

**Section:** Strategy: Choosing the Algorithm at Runtime (lead-in to `strategy.py`, line 239)
**Pattern:** §23 Filler Phrases, often-empty adverbs (P2)

Current:
> and the loop below simply tries each choice in turn:

Proposed:
> and the loop below tries each choice in turn:

Why: The deletion test passes: the sentence means the same without `simply`, and
the surrounding clause ("Because each finder is a function with the same
signature") already carries the "no machinery required" point.

***

[] Reject

**Section:** An Event Bus: Handlers Keyed by Type (paragraph on `subscribe`'s generic, lines 525-526)
**Pattern:** §70 Interpretive Metadiscourse / treadmill restatement (P2)

Current:
> The generic guards the boundary.
> The `Any` covers the heterogeneous storage behind it.

Proposed:
> Cut both sentences.

Why: Borderline.
The paragraph has already said both things four lines earlier ("The safety check
happens once, at registration" and "the element type erases the parameter to
`Handler[Any]`"), so the closing pair restates them in symmetric short form
rather than adding a fact.
Against that, the pair does name the division of labor between the two
mechanisms in one place, which is a real service in a typing discussion, so
this is a judgment call rather than a clear tell.

***

[] Reject

**Section:** An Event Bus: Handlers Keyed by Type (lead-in to `test_event_bus.py`, line 540)
**Pattern:** §13 Passive Voice and Subjectless Fragments, dangling modifier (P2)

Current:
> For testing, publishing calls every handler registered for a type,

Proposed:
> The tests confirm that publishing calls every handler registered for a type,

Why: "For testing" attaches to "publishing calls," which reads as if publishing
calls handlers for the purpose of testing.
The intended subject is the tests, and naming them matches the parallel lead-in
used before `test_chain.py` ("These tests confirm that...").

***

[] Reject

**Section:** An Event Bus: Handlers Keyed by Type (closing paragraph, lines 571-572)
**Pattern:** §70 Interpretive Metadiscourse / treadmill restatement (P2)

Current:
> The subscribers are functions,
> and the bus routes each event to them by its type.

Proposed:
> Cut both lines.

Why: "The subscribers are functions" repeats "The handlers are ordinary
functions" from the section's opening paragraph, and "the bus routes each event
to them by its type" repeats "the event type picks the audience" from the
sentence immediately before it.
Cutting them puts "Here a type may have many handlers" directly after the
Observer comparison, which is what sets up the `singledispatch` contrast.
