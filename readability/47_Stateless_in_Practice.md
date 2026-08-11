When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Readability review of `Chapters/47_Stateless_in_Practice.md`,
run after the deep review was applied
(including the ty 0.0.70 modernization of the five-way-union sentence
and the two-checker-gaps conclusion, treated as settled content).
The chapter is clean on AI vocabulary: no Tier 1A/1B/2 hits,
no curly quotes, no spaced `--`, no transition-phrase pileups,
no boldface or list inflation.
The one genuine cluster was §53 (social/endorsement framing):
five "worth X" constructions rating information instead of stating it,
all fixed directly.
A few residual watch-list items ("never", "has to") were fixed to match
the parallel replacements the deep review made.
No finding needed a decision, so there are no live blocks.

## Applied directly

- L208, watch list "has to": "the payload the request had to deliver" is now
  "the payload the request must deliver" (matches the deep review's
  "has to" replacements).
- L629, watch list "never": "The load's declared dependency never changes"
  is now "does not change"; the contrast with "What changes is the object
  answering the need" carries the emphasis.
- L1488, watch list "never": "checks each argument against one Ability,
  never against the others" is now "not against the others".
- L1492, §53: "The guarantee moved ... into a two-line function, and it is
  worth knowing which of those you are getting" is now two sentences
  ending "Know which of those you are getting."
  (instruction to the reader, the carve-out form).
- L1523, §53: "Retry is the one worth studying, because of what it does to
  the type" is now "Retry is the one to study, ...".
- L1644, watch list "never": "an `errors` attribute that `retry()` never
  assigns" is now "does not assign".
- L1845, §53 plus expletive opener: "There are five limits worth knowing."
  is now "The guarantee has five limits." (keeps the count that organizes
  the numbered subsections).
- L1976, §53: "The habit is worth keeping generally." is now the imperative
  "Keep the habit generally:" merged onto the following clause, which
  supplies the reason ("a named intermediate is where you read the
  Ability that remains").
- L2125, §53: "But the direction is worth watching." is now
  "But watch the direction." (same turn, instruction form).
- L2161, exercise 5: "until the program builds again, and list every line
  you had to edit" is now "until the program type-checks again, and list
  every line you edited"; Python has no build step, the point the deep
  review already applied to the retry section's "the program does not
  build", and "had to" is on the watch list.

## Considered and declined

- **"a failure `@throws` never lifted goes past `catch()` untouched"**
  (limit 1). "Never" inside a compact relative clause; "did not lift"
  muddles the generic tense and "does not lift" breaks the clause.
  Rewriting degrades it. Left as is.
- **"an ecosystem that has never heard of it"** (What Survives the
  Library). The idiom is the voice; "has not heard of it" is weaker.
  Left as is.
- **"The pipeline is in there, but you have to look for it."** (The
  Success Path). "Have to" is consider-rewriting tier and this is the
  spoken rhythm the sentence runs on; "must look for it" stiffens it.
  Left as is.
- **"here a scenario is nothing more than arguments to `supply()`"**
  (Composing a Program). The global rule's own carve-out: a comparative
  where the diminishing is the point, same ruling as the Observer
  "nothing more than a list of callbacks" precedent in
  `readability_db.md`. Left as is.
- **"Here is what ZIO does that Stateless cannot."** (Dependencies That
  Need Dependencies). The global "is what" rule names this sentence as a
  keep case verbatim. Left as is.
- **"That is a real loss against the Abstract Factory"** (§34
  real/actual inflation, Supplying a Whole Cast). Kept: two paragraphs
  of gains precede it, and "real" marks the turn to a genuine
  regression rather than rhetorical balance; the contrast is carried by
  the surrounding argument.
- **Enumerated-fragment beats** ("Four implementations, one Ability, one
  running program.", "Two runs, one attempt, ...", "Three changes, none
  of them silent."). §31 fires on runs of staccato fragments; these are
  single summary beats spaced across a long chapter, a house rhythm.
  Left as is.
- **"happen" hits** ("what happens at some critical time", "the window
  where this happens", "happens once per attempt"). All literal event
  usage, the legitimate case for the consider-rewriting tier. Left as
  is.
- **"already" hits** ("instances that are already built", "have already
  cost you a production incident"). Both draw a real contrast (against
  `ZLayer` construction; past incident versus future risk). Left as is.
