When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first readability review of `Chapters/39_Pattern_Catalog.md`
in the clean-slate sweep.
The chapter is a catalog: eight tables of names and one-line intents,
with prose only in the intro, the problem-index lead-in,
and the "Patterns Python Absorbed" frame.
The deep review already tightened that prose
(its applied-directly list dropped a filler "already"
and reworded several intents),
and its declined section binds the source-faithful intent wordings
(GoF, POSA1, PoEAA, EIP), which are content here, not style targets.
The scan found no pattern that clears the bar for an edit:
no watch-list violations, no Tier 1A vocabulary,
no em dashes or curly quotes, and the intro's rhythm is varied.
No change was made to the chapter, and there are no live blocks.

## Considered and declined

- **Participial tails on GoF intent lines** (§3 by shape):
  "Separate constructing a complex object from its representation,
  building it in steps" (Builder);
  "Encapsulate a request as an object, enabling queues, logging, and
  undo" (Command);
  "Define an algorithm's skeleton, letting subclasses fill in steps"
  (Template Method).
  Each `-ing` clause carries the pattern's defining content
  (stepwise construction, the queue/log/undo payoff, subclass hooks
  into a fixed skeleton), paraphrased from GoF's own intent statements.
  These are the fake-depth tails §3 hunts in shape only;
  cutting one would drop half the intent.

- **"Deliver a message to exactly one receiver"** (Point-to-Point
  Channel): "exactly" is on the global watch list, but this is the
  precise logical match the rule's own exception names, and the
  one-receiver guarantee is the property that distinguishes the
  channel from Publish-Subscribe in EIP.

- **"Future/Promise"** (Concurrency table): "promise" names the actual
  construct, the global rule's carve-out. The row is the pattern's
  literature name, not a metaphor.

- **"A well-known object others use to find services or data"**
  (Registry): "well-known" is a §26 hyphenated-pair candidate, but it
  sits in attributive position, where the hyphen is correct, and the
  deep review's declined section keeps this row on Fowler's wording.

- **Noun-phrase intents without a verb** ("A packet of data sent over
  a channel", "A small immutable object compared by value, not
  identity"): §8 copula-avoidance by shape. A catalog intent line is a
  definition slot; the noun phrase is the format, and "Message is a
  packet of data" would add a copula to a table cell, not to prose.

- **"Many overlap, some compete, and several exist only to work around
  limits of a particular language"**: a three-part parallel (§10 by
  shape), but each clause makes a distinct claim, and "only" draws the
  real contrast (those patterns have no other reason to exist). The
  progression many/some/several is doing ranking work, not padding.

- **Problem-index rows as bare phrase lists** (§59 by shape): the
  "Look at" column is genuine list content, the carve-out's own case,
  and the row labels ("Surviving a failing dependency") are indexing
  phrases, not claims.
