# Readability review: 03_Containers

> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

The chapter reads as human, first-edition voice throughout:
varied sentence lengths, concrete claims tied to listings, no vocabulary
clusters, no curly quotes or spaced `--`.
Every finding was mechanical enough to decide, so all of them are in the
applied-directly list and nothing needs a decision.

## Applied directly

- Dictionaries (~line 267), §8/Tier 1B copula avoidance:
  "so they cannot serve as keys" is now "so they cannot be keys".
- Sets (~line 370), watch list ("never"):
  "so never write code, or a test, that depends on it" is now
  "so do not write code, or a test, that depends on it".
- Sets, the `report()` paragraph (~line 445), imperative-plus-consequence:
  "run the listing with `--numbers` ... and it prints the two times it
  measured" is now the gerund form,
  "running the listing with `--numbers` ... prints the two times it measured".
- defaultdict (~line 517), §53 endorsement frame:
  "A plain `dict` has a second option worth knowing:" is now
  "A plain `dict` has a second option:"; the sentence after it already says
  what the option does.
- deque (~line 609), stranded preposition:
  "the sliding window a `list` has no equivalent for" is now
  "the sliding window a `list` cannot provide".
  (Close alternative: "the sliding window a `list` lacks".)
- Immutability (~line 727), §8/Tier 1B:
  "it can serve as a dictionary key or a set member" is now
  "it can be a dictionary key or a set member".

## Considered and declined

- **"assignment never copies" (list_traps paragraph).**
  "Never" is on the avoid list, but the universal claim is the content:
  assignment copies in no case, and "does not copy" understates it.
- **"a value you never read gets the name `_`" (unpacking paragraph).**
  Same word, judged differently from the Sets fix above:
  here it quantifies over every use of the value, and
  "a value you do not read" loses that without getting shorter.
- **"even when the source is a tuple or a string" (unpacking paragraph).**
  "Even" is on the avoid list but draws the real contrast:
  the starred name yields a `list` in the surprising cases too.
- **"The `list` automatically resizes itself" (Lists).**
  Reflexive "itself", the usage the global rule allows
  ("the function modifies itself").
- **"Iterating the `dict` itself" (Dictionaries).**
  "Itself" contrasts the `dict` with its three views, named in the
  previous sentence; dropping it blurs which thing is being iterated.
- **"a container holding an unhashable object is itself unhashable"
  (shallow immutability).**
  "Itself" marks the propagation: unhashability climbs from element to
  container. Without it the sentence reads as a restatement.
- **"plain `dict`" / "plain dict" (defaultdict section and code comments).**
  "Plain" draws the real contrast against `defaultdict`,
  the carve-out the global rule names.
- **"Lists grow, shrink, and answer questions about themselves" (Lists).**
  Rule-of-three shape, but each verb maps to operations the listing then
  shows (append/extend/insert, remove/del, `len`/`in`), so the triple is
  content, not padding.
- **The "only" instances ("Only `items()` yields", "not only a set",
  "when you only want to look", "only a read-only window").**
  Each is a real restriction or contrast, not an intensifier.
