> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/38_Simulation.md` (r2)

A sweep of the Tier 1A, 1B, 2 and 3 vocabulary tables returns zero hits, and
there is no boldface, no curly quote, and no spaced ` -- `.
Everything below was in prose added since the first review: the deep review's
manifest edits and today's apply, which added an intro paragraph, four
headings, a conclusion section, and the `TaskGroup` and log commentary.

Every finding was resolved directly and applied (listed below).
No blocks remain.

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
- `The Less the Agents Know` conclusion: cut the four-sentence progression
  recap ("The three simulations form a progression. The rats cooperate
  through a blackboard. The robot follows a script. The grains know
  nothing."). The deep review moved the progression to the intro so it
  could organize the reading, and nothing trimmed the original, so the
  reader met the same arc twice in nearly the same words. The conclusion
  still names the payoff ("The less the agents understand, the more the
  run can tell you") and ends where it ended before ("Run it."). The
  alternative was trimming the intro instead, which would give back most
  of what the move bought.
