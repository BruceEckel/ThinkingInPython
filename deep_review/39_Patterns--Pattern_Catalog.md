When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Deep review of chapter 39, run after the elements-of-style, literal, positive,
straighten, cohesion, and antecedents passes (one commit each on
`claude/prep-39`). An Opus agent checked all 69 links (59 distinct
targets) against the target sections, the nine "Patterns Python Absorbed"
rows, and the three claims about chapter 21. Every anchor resolves, all
nine absorbed rows and all three chapter 21 claims hold, and the
alphabetical-order claim holds for every table. The prose pass ran
without the global `~/.claude/CLAUDE.md` watch list, which the cloud
session does not have; `banned_phrases.py`, Vale, and the repo's rules
stood in for it. The standing rejection in `deep_review_db.md` (no
conclusion, no exercises) is honored.

No finding needed a decision only you can make, so this file has no live
blocks.

## Applied directly

- Intro, *State*/*State Machine* pair: "A design rarely needs both at once"
  contradicted chapter 31 ("That loop is the *State* pattern plus the
  transition") and chapter 26's *State Machine* passage. It now reads
  "*State Machine* builds on *State*: each state chooses its successor, so
  the object advances without the client choosing."
- Intro, the "dissolve" sentence: the cohesion pass left "the body of this
  book argues" as an interrupting clause. It is restored to the front of
  the sentence and keeps the pass's link to the language-limits clause.
- Intro, idiom groups: "language idioms tied to C++ or Java's limits"
  became "most of them tied to", since *Mixin* in that table is not a
  workaround for a language limit.
- Intro: "The rest sits in Other Patterns and Idioms" became "Everything
  else sits in", because "the rest" had no clear antecedent.
- Problem table: *Unit of Work* and *Identity Map* moved from "Saving and
  restoring state" to "Persisting domain objects to a database". Their
  own intent lines (commit tracked changes; load each object once per
  session) are persistence, and both belong to Fowler's object-relational
  group, as *Lazy Load* does.
- Problem table: *Null Object* added to the "instead of null" row. Chapter
  20 teaches it as the book's answer to null.
- Links made precise: *Model-View-Controller* → chapter 30's `#where-the-controller-goes`
  (where `model_view_controller.py` lives), *Blackboard* → chapter 38's
  `#the-rat-and-the-blackboard`, *Monad* → chapter 42's `#composing-with-bind`
  (where the word is defined). Each had pointed at the top of its chapter.
- *Dead Letter Channel*: "no one can deliver or process" became "the
  messaging system cannot deliver". In Hohpe and Woolf, a message that a
  receiver cannot process goes to *Invalid Message Channel*, a different
  pattern.
- Prose passes, reverted or adjusted before commit: elements-of-style's
  Pimpl rewrite ("clients stay compiled") was reverted, because the
  negative carries the claim. The literal pass's "Mediate between" on
  *Repository* went back to "Stand between", because "mediate" reads as
  the *Mediator* pattern. Its "every subscriber" on *Publish-Subscribe
  Channel* became "every subscriber to its topic". The positive pass's
  "A plain name" became "A name without a link", because every name in
  the tables is italic.

## Considered and declined

- Linking the unlinked names that other chapters mention in passing:
  *Mediator* (a GoF quote in 21), *Bulkhead*/*Circuit Breaker* (one
  sentence in 47 saying the library lacks them), *CRTP* (a footnote in
  17), *Mixin* (a scratch class in 17), and *Plugin* (self-registering
  plugins in 27 and 34, which is not Fowler's configuration-driven
  *Plugin*). The chapter links a name only when the book covers it, and
  none of these is coverage.
- *Fluent Interface* could link to chapter 08's `#the-self-type` instead of
  27's `#builder`. Either one fits, and 27 shows the pattern in use, so the
  link stays.
- The problem table is not alphabetical, and neither is "Patterns Python
  Absorbed". The intro's alphabetical claim covers only the source and
  group tables, and both of these tables have their own order.
