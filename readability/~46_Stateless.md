[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/46_Stateless.md`

This chapter reads as human throughout.
A vocabulary sweep for Tier 1A/1B/2 words returned one hit (`simply`, used correctly),
there is no boldface, no rule-of-three padding, no generic conclusion,
and every list in the prose is genuine list content.
Four findings, one of them a clear pattern hit and three minor;
two are marked borderline.

[] Reject

**Section:** Forgetting to Supply (first line under the heading)
**Pattern:** §28 Signposting and Announcements / §29 Fragmented Headers (P1)

Current:
> Let's see what happens when we don't supply a required `Need`.
> Give `run()` an Effect that still needs a `Console`:

Proposed:
> Give `run()` an Effect that still needs a `Console`:

Why: The sentence announces what the section is about to do instead of doing it,
and restates the heading it sits under.
The line after it already gives the instruction, so nothing is lost.

***

[] Reject

**Section:** Declaring a Dependency (after `untyped_greet.py`)
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> That omission matters: the caller cannot see the dependency,
> redirect the output, or test the function without capturing stdout.

Proposed:
> The caller cannot see the dependency,
> redirect the output, or test the function without capturing stdout.

Why: "That omission matters:" tells the reader how much weight to give a point the
three concrete consequences then make on their own; the deletion test loses no information.
Borderline: the frame does carry an anaphoric link back to "a lie by omission" two lines up,
so reject this if you want that link kept.

***

[] Reject

**Section:** Builtin Abilities (last sentence)
**Pattern:** Tangled sentence (clarity; no § number) (P2)

Current:
> [Supplying an Interface](#supplying-an-interface), next,
> is where that cost comes from and how an interface avoids it.

Proposed:
> [Supplying an Interface](#supplying-an-interface), next,
> explains where that cost comes from and how an interface avoids it.

Why: "is where that cost comes from and how an interface avoids it" joins two
complements that do not take the same verb, so the second half reads as a snag.
`explains` governs both.

***

[] Reject

**Section:** Dependency Injection (after `dependency_injection.py`)
**Pattern:** §70 Interpretive Metadiscourse / treadmill restatement (P2)

Current:
> No type information indicates whether a `Console` has been registered.
> The type checker cannot report that something has gone wrong.

Proposed:
> No type information indicates whether a `Console` has been registered,
> so the type checker cannot report that something has gone wrong.

Why: The second sentence is the consequence of the first rather than a new claim,
and joining them also breaks up a run of five same-length sentences.
Borderline: the two-sentence version lands harder, so this is a rhythm call, not a defect.
