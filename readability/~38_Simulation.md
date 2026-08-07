[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/38_Simulation.md`

This chapter reads as human throughout.
A full mechanical scan found no Tier-1A or Tier-2 vocabulary in the prose,
no curly quotes, no non-ASCII characters, no spaced ` -- `,
no repo-banned strings, no boldface or emoji slop, no placeholders,
and no formulaic openers or closers.
Sentence and paragraph length vary the way a person's does,
and the specifics (Chladni and the 1787 bow, Jeremy Meyer's Java original,
`zip(pairs, pairs)` versus `zip(teleports, teleports)`) are the kind LLMs round off.
The three findings below are clarity defects, not AI tells:
one misplaced modifier, one tangled sentence, and one wrong noun.

***

[] Reject

**Section:** Rats & Mazes, paragraph introducing `blackboard.py`
**Pattern:** Tangled sentence (skill task 1, "tangled passages") (P2)

Current:
> This is the read-modify-write hazard [Concurrency](19_Concurrency.md#a-single-thread-still-races)
> demonstrated, avoided by construction:

Proposed:
> This is the read-modify-write hazard demonstrated in [Concurrency](19_Concurrency.md#a-single-thread-still-races),
> avoided by construction:

Why: With the relative pronoun dropped and the link text sitting where a verb is expected,
the reader garden-paths at "hazard Concurrency demonstrated";
moving the reference into a prepositional phrase keeps every fact and the same link target.

***

[] Reject

**Section:** Rats & Mazes, paragraph introducing `rats_view.py`
**Pattern:** Misplaced modifier (outside the §1-§70 taxonomy) (P2)

Current:
> Like every windowed view in this book, the harness skips it
> (`tools/data/norun.txt` lists all three of this chapter's views):

Proposed:
> The harness skips it, like every windowed view in this book
> (`tools/data/norun.txt` lists all three of this chapter's views):

Why: The comparison attaches to the subject of the main clause,
so as written the sentence says the harness is like a windowed view.

***

[] Reject

**Section:** Order from Noise, Watching It Happen (paragraph after `chladni_view.py`)
**Pattern:** Wrong noun (outside the §1-§70 taxonomy) (P2)

Current:
> It yields elements from the source item in sequence and cycles back to the beginning when it reaches the end.

Proposed:
> It yields elements from the source in sequence and cycles back to the beginning when it reaches the end.

Why: The previous sentence establishes that the source is an iterable, not an item,
so "source item" contradicts it; dropping the noun is the smallest fix.
