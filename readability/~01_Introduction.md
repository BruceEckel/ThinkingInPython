[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: Chapters/01_Introduction.md

This chapter reads as human writing throughout.
It carries most of the "signs of human writing" the skill tells you to preserve:
dated, hard-to-fabricate specifics (2008, 2011, June 2026, PyCon, `uv`, Astral's `ty`),
mixed feelings that stay unresolved ("I know some people don't like AI"),
self-deprecation ("I hardly do"),
and genuinely varied sentence length.
A full sweep of the Tier 1A/1B/2/3 vocabulary tables returned exactly three hits in 223 lines,
none of them clustered: "That said" (line 108, doing real contrastive work),
"daunting" (line 124), and "myriad" (line 131).
Under the isolated-word rule none of the three is a finding, so they are noted here rather than proposed as changes.
The mechanical checks are also clean:
no spaced ` -- `, no curly quotes, no non-ASCII characters,
no banned strings, no single-bracket placeholders.

Two findings, both minor.

***

[] Reject

**Section:** AI Trigger Warning (lines 101-103)
**Pattern:** §10 Rule of Three Overuse (P2)

Current:
> The experience was amazing, and I began adding material from talks, writing,
> and presentations.

Proposed:
> The experience was amazing, and I began adding material from writing and presentations.

Why: "Talks" and "presentations" name the same thing here, as line 70 confirms ("Many of these chapters came from presentations I've given, mostly at PyCon"), so the list is padded to three with a synonym.
Borderline: reject this if you intend a distinction between a conference talk and a written presentation.

***

[] Reject

**Section:** AI Trigger Warning (lines 106-107)
**Pattern:** §23 Filler Phrases (P2)

Current:
> This book never would have happened without the help of Claude,
> which gave me tremendous support throughout the process.

Proposed:
> This book never would have happened without the help of Claude.

Why: The trailing clause restates the first half in vaguer words, and "tremendous support throughout the process" would sit unchanged under any tool and any book, which is the portability test failing.
Cutting it also lightens the near-duplicate claim eight lines later at "Without it, this book wouldn't exist," which is doing real rhetorical work and should stay.
