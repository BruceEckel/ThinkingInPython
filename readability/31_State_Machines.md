When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Readability pass over `Chapters/31_State_Machines.md`.
The chapter is close to clean:
the deep review's applied list had removed the watch-list hits
a mechanical sweep finds first
("ships", the module-cache "never", "plain methods", "only" placements),
and the prose has the varied rhythm and specific detail the skill treats as human signals.
Every finding had one sensible answer,
so this file has no live blocks:
five small fixes applied directly, the rest examined and kept.

## Applied directly

- Line 377, watch-list "never": "a question this input file never asks"
  is now "a question this input file does not ask".
- Line 380, raise-needs-an-object rule: "raises nothing" is now
  "raises no exception".
- Line 489, stranded preposition: "as the `else` the earlier rows fall
  through to" is now "as the `else` to which the earlier rows fall through".
- Line 746, watch-list "never": "the model never draws anything" is now
  "the model draws nothing".
- Line 849, "itself"-as-flourish plus watch-list "at all":
  "The states themselves shrink to `Enum` members with no behavior at all"
  is now "The states shrink to `Enum` members with no behavior";
  the contrast with the table already carries the emphasis.

## Considered and declined

- "The key distinction between this design and the next" (intro):
  "key" is a flagged adjective in §7, but it is a single hit,
  and the deep review already examined this sentence and kept it
  (its decline note covers the this-design/next-design framing).
  Rewording it now would be churn on a settled sentence.
- "a bug you want flagged" (An Unexpected Input):
  standing keep in `readability_db.md`; not touched.
- "The lookup keys on `type(event)` exactly" (The Engine):
  "exactly" is the global rule's own carve-out,
  a precise logical match (exact-type dispatch, a cross-chapter thread).
- "The rest of the input file only repeats them":
  "only" draws the real contrast (repeats, adds nothing new),
  and its placement is correct.
- "the event the message already names" (from-None sentence):
  "already" earns its place; it is the reason the chained `KeyError`
  can be dropped. Same call as the 33_Visitor "already" keep in the db.
- "worth its few lines" (base-class paragraph) and
  "The cases worth pinning down" (test paragraph):
  both fall under §53's carve-outs,
  a real cost-benefit weighing and a test-selection judgment,
  not endorsement framing.
- "`Enum` with `auto()` serves in place of `StrEnum`":
  looked at under §8/Tier 1B ("serves as"),
  but "serves in place of" means suffices as a replacement,
  not a copula dodge; "is" cannot substitute here.
- "The machine is now completely defined by a table" (§13 passive):
  the passive keeps the machine as the topic; advisory rule, kept.
- "a transition row answers three questions" (§10 rule of three):
  the three are the three tuple slots, a genuine count.
- Diagram alt text "loops COLLECTING back on itself":
  reflexive and load-bearing, not a flourish.
