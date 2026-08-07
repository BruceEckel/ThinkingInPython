[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/15_Context_Managers.md`

This chapter reads as human-written technical prose from start to finish.
No AI vocabulary (a scan for the Tier 1A/1B/2 tables turned up nothing), no significance inflation,
no signposting, no boldface overuse, no curly quotes, no spaced ` -- `,
and no banned strings ("reach for", `from __future__ import annotations`).
Sentence length varies, the bullets in "The `contextlib` Toolkit" are genuine API list content,
and the rule-of-three groupings (three tests, three production refinements, three `emit()` destinations)
each name three real items rather than padding to a number.
The only findings are five small clarity and repetition trims, all P2.

[] Reject

**Section:** A Basic Context Manager (paragraph after `no_finally.py`'s predecessor, `trace_gen.py`)
**Pattern:** §70 Interpretive Metadiscourse / repetition (P2)

Current:
> The code before `yield` is the setup, and the code after it is the cleanup.

Proposed:
> Cut this sentence.

Why: The section already said this before the listing ("everything before it is setup, everything after it is teardown"),
and the paragraph just above walked through the same thing concretely for `trace("A")`.
The paragraph then opens on its new information, "The `finally` makes the cleanup dependable:".

***

[] Reject

**Section:** A Basic Context Manager (same paragraph, last sentence)
**Pattern:** §13 Passive and Subjectless Fragments / ambiguous pronoun (P2)

Current:
> It relies on the generator and decorator machinery from [Decorators](14_Decorators.md)
> and [Iterators](23_Iterators.md#generators).

Proposed:
> The `@contextmanager` form relies on the generator and decorator machinery from [Decorators](14_Decorators.md)
> and [Iterators](23_Iterators.md#generators).

Why: The nearest antecedent for "It" is `finally` from the preceding sentence, which is not what relies on decorator machinery.
Naming the subject costs four words and removes the misreading.

***

[] Reject

**Section:** Context Manager as Decorator (final paragraph, last sentence)
**Pattern:** §70 Interpretive Metadiscourse / redundant tail (P2)

Current:
> Use it when setup and cleanup should be identical on every call,
> with nothing that needs to vary per call.

Proposed:
> Use it when setup and cleanup should be identical on every call.

Why: "with nothing that needs to vary per call" restates "identical on every call" in different words,
so the second clause adds no condition a reader could act on.

***

[] Reject

**Section:** An Object Pool (paragraph after `test_object_pool.py`)
**Pattern:** §70 Interpretive Metadiscourse / repetition (P2)

Current:
> The second lease hands back the same object, not a new one.

Proposed:
> Cut this sentence.

Why: The sentence introducing the tests already listed this ("the pool hands out the same object rather than a new one"),
and `test_objects_reused_not_recreated` asserts it in the listing directly above.
The paragraph continues with "A production pool adds refinements to this skeleton," which reads cleanly as the opener.

***

[] Reject

**Section:** An Object Pool (closing paragraph, "That is what the protocol buys:")
**Pattern:** §13 Passive and Subjectless Fragments (P2)

Current:
> the borrower's contract is two lines long and cannot be got wrong,

Proposed:
> the borrower's contract is two lines long and impossible to get wrong,

Why: "cannot be got wrong" is an agentless passive with an awkward participle;
the active adjective phrase makes the same claim without changing its strength.
