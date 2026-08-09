> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/38_Simulation.md` (r2)

A sweep of the Tier 1A, 1B, 2 and 3 vocabulary tables returns zero hits, and
there is no boldface, no curly quote, and no spaced ` -- `.
Everything below is in prose added since the first review: the deep review's
manifest edits and today's apply, which added an intro paragraph, four
headings, a conclusion section, and the `TaskGroup` and log commentary.

***

**Section:** `## The Less the Agents Know` (the promoted conclusion) against the
new intro paragraph
**Pattern:** Treadmill effect (Structure and Rhythm Tests) (P2)

The conclusion now repeats the intro almost claim for claim. The intro says:

> Three simulations follow,
> each giving its agents less to work with than the last.
> ...
> The first two confirm a design you can predict from the code.
> The third does not, which is simulation's other purpose.

and the conclusion says:

> The three simulations form a progression.
> The rats cooperate through a blackboard.
> The robot follows a script.
> The grains know nothing.
> The less the agents understand, the more the run can tell you,

Before today the progression was stated once, at the end. The deep review moved
it to the front so it could organize the reading, which was right; nothing
trimmed the original. A reader now meets the same arc twice, ninety listings
apart, in nearly the same words.

The conclusion is the half to trim, since the intro's version does work the
conclusion's cannot. Cutting its three-sentence recap leaves:

> ... This is *emergence*:
> global order arising from local rules that never mention it.
> The less the agents understand, the more the run can tell you,
> because the outcome lives in the interactions rather than the instructions.
> When behavior emerges, reading the code is not enough.
> Run it.

which still names the progression's payoff and ends where it ended before.

The alternative is to trim the intro instead, keeping only "Three simulations
follow, each giving its agents less to work with than the last" and letting the
conclusion spell it out. That keeps the reveal but gives up most of what the
deep review's block was buying.

I lean toward trimming the conclusion. Your call, since it is your closing
paragraph either way.

[] Reject

***

**Section:** "Order from Noise," and the paragraph after `rats_and_mazes.py`
**Pattern:** Global watch list, "Don't use" tier: `lands` (P1)

Two occurrences, both in prose this pass did not add but which has not been
scanned for this word:

> When a grain lands on a still line, nothing kicks it away again.

> A test cannot guess where a particular grain lands after a million random
> kicks.

Proposed: "When a grain comes to rest on a still line" for the first, and "where
a particular grain ends up" for the second.

Why: `lands` is on the "Don't use" list in `~/.claude/CLAUDE.md`. The first
sentence has a literal verb available that is also more accurate, since the
grain's stillness is the point. The second is the metaphor proper.

[] Reject

***

**Section:** "Rats & Mazes," the new `TaskGroup` paragraph
**Pattern:** Paragraph-length uniformity / one idea per paragraph (P2)

The paragraph after `blackboard.py` now carries four separate facts: what a
`TaskGroup` guarantees, why `gather()` cannot, why `group` is `field(init=False)`,
and why the other four fields carry `default_factory`. The first two are one
argument about concurrency; the last two are a note about the dataclass.

Proposed split after "and half the rats do not exist yet," so the dataclass note
stands as its own short paragraph. Nothing else changes.

Low stakes. The paragraph is not wrong, only doing two jobs, and the two jobs
arrived from two separate review blocks.

[] Reject

***

**Section:** Intro, new paragraph
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> The first two confirm a design you can predict from the code.
> The third does not, which is simulation's other purpose.

Proposed:
> The first two confirm a design you can predict from the code.
> The third produces a pattern nobody wrote down.

Why: "which is simulation's other purpose" tells the reader how to file the
third example before they have seen it, and the noun it lands on is abstract.
Saying what the third one does is both concrete and a better hook, and it does
not spoil the Chladni figure any more than the current version does.

This also removes the overlap with "Order from Noise," whose opening paragraph
already draws the confirm-versus-discover distinction at length.

[] Reject
