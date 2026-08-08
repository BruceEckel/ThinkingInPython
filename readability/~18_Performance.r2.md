[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review 2: `Chapters/18_Performance.md`

Run after the deep-review edits landed, so the new prose gets the same scan the
rest of the chapter got in review 1.
Nothing from review 1 was rejected, so nothing is carried forward.

The chapter still reads as human technical prose.
No AI vocabulary hits, no significance inflation, no signposting, no boldface
padding, no curly quotes, no spaced ` -- `.
Five findings, all in prose written during the deep review.

***

[] Reject

**Section:** Try a Faster Platform (new JIT paragraph)
**Pattern:** §53 the "worth" frame, plus a sentence that dates itself (P2)

Current:
> and the gain today is a single-digit percentage,
> so it is worth a measurement rather than a plan.

Proposed:
> and the gain is currently a single-digit percentage,
> so measure it before planning around it.

Why: "worth a measurement rather than a plan" rates the action instead of giving
it, and the instruction is the useful half.
"Today" also reads as the day of writing rather than the state of the release,
which matters for a paragraph the next CPython version may invalidate.

***

[] Reject

**Section:** Write Idiomatic Python (after `hoist_attribute_lookup.py`)
**Pattern:** §23 clarity, a compressed distributive that misreads (P1)

Current:
> Two machines measured the hoisted version five and twenty percent slower.

Proposed:
> One machine measured the hoisted version five percent slower, another twenty.

Why: "five and twenty percent" parses first as the archaic "twenty-five percent",
and the reader has to back up to see it means two separate measurements.
The chapter's own idiom elsewhere is "One machine measured…", which this matches.

***

[] Reject

**Section:** Slots (after `slots_dataclass.py`)
**Pattern:** §11 repetition (P2)

Current:
> That filter catches a `FrozenInstanceError` because `FrozenInstanceError` subclasses `AttributeError`.

Proposed:
> The filter catches it because `FrozenInstanceError` subclasses `AttributeError`.

Why: the name appears twice in one sentence, and the first use is already the
subject of the sentence before it.

***

[] Reject

**Section:** Converting a Slow Function to Rust (boundary-cost paragraph)
**Pattern:** watch list, `buy` (P2)

Current:
> but each crossing buys a hundred-odd loop iterations of real work,
> so the conversion cost disappears into the win.

Proposed:
> but a hundred-odd loop iterations of real work follow each crossing,
> so the conversion cost disappears.

Why: "buys" is on the avoid-if-possible list, and the sentence reads more
directly with the work as its subject, since the work is what the paragraph is
weighing.

***

[] Reject

**Section:** Profilers (opening)
**Pattern:** §23 clarity, stacked commas (P2)

Current:
> The standard library includes two: a deterministic tracing profiler, and,
> new in Python 3.15, a sampling profiler.

Proposed:
> The standard library includes two.
> The first is a deterministic tracing profiler; the second, new in Python 3.15,
> is a sampling profiler.

Why: three commas in eleven words interrupt the list the sentence is trying to
give. Splitting it also lets the paragraph's next sentence, which begins "The
classic `cProfile`", attach to the item it describes.
