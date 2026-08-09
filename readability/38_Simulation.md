> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/38_Simulation.md` (r2)

A sweep of the Tier 1A, 1B, 2 and 3 vocabulary tables returns zero hits, and
there is no boldface, no curly quote, and no spaced ` -- `.
Everything below was in prose added since the first review: the deep review's
manifest edits and today's apply, which added an intro paragraph, four
headings, a conclusion section, and the `TaskGroup` and log commentary.

The clear-cut fixes were applied to the chapter directly (listed below);
one block remains for your judgment.

## Applied directly

- "When a grain lands on a still line" → "When a grain comes to rest on a
  still line" ("lands" is on the global "Don't use" list; the grain's
  stillness is the point, so the literal verb is also more accurate).
- "where a particular grain lands after a million random kicks" → "where a
  particular grain ends up after a million random kicks" (same word, the
  metaphor proper).
- The `TaskGroup` paragraph after `blackboard.py` split after "and half the
  rats do not exist yet": the concurrency argument and the dataclass note
  arrived from two separate review blocks and were doing two jobs in one
  paragraph. No wording changed.
- Intro: "The third does not, which is simulation's other purpose." → "The
  third produces a pattern nobody wrote down." (§70 metadiscourse that filed
  the example before the reader saw it; the concrete version is the better
  hook and removes the overlap with "Order from Noise," which already draws
  the confirm-versus-discover distinction at length).

***

**Section:** `## The Less the Agents Know` (the promoted conclusion) against the
new intro paragraph
**Pattern:** Treadmill effect (Structure and Rhythm Tests) (P2)

The conclusion now repeats the intro almost claim for claim. The intro says:

> Three simulations follow,
> each giving its agents less to work with than the last.
> ...
> The first two confirm a design you can predict from the code.
> The third produces a pattern nobody wrote down.

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
