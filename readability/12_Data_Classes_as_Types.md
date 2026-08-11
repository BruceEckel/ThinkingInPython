When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first readability review of
`Chapters/12_Data_Classes_as_Types.md` in the clean-slate sweep,
run after the deep review (`deep_review/~12_Data_Classes_as_Types.md`),
which had cleared most of the watch-list hits.
The chapter is clean of AI-pattern clusters:
no Tier 1A vocabulary, no curly quotes, no spaced ` -- `,
no signposting, no rule-of-three stacks, no staccato drama.
Sentence lengths vary and the short lines land on purpose
("The checks did not disappear. They moved.").
What remained were a few watch-list calls;
three cleared the direct-application bar and the rest are recorded below.
No findings needed a live block.

## Applied directly

- Line 597 (`A` section): watch-list "never";
  "`A` never overrides `__init__`, ..." is now "does not override"
  (simple negation says it; "overrides none of" was the close
  alternative, dropped because "reports none as redefined" ends the
  same sentence).
- Line 742 (`D` section): watch-list "ever";
  "no constructor call can ever assign one" dropped "ever"
  (deletion test passes).
- Line 745 (`D` section): watch-list "never";
  "never appears in either report" is now "appears in neither report".

## Considered and declined

- The remaining prose "never"s were each examined and kept, since in
  each the word carries the universal or temporal force the claim
  needs: "`11` was never a legal rating" (at no time),
  "against code the checker never saw" (the runtime-vs-checker
  contrast), "hoping you never miss a spot" (the check repeats
  indefinitely), "declared, but never assigned a value" (defines
  *bare annotation*; no assignment at any point),
  "it never compares the factory with the field" (for any
  annotation), and "the class never comes into existence" (not
  created at all). The deep review edited several of these paragraphs
  and left these words, which reads as the same judgment.
- "ever exist" (test comment in `test_stars.py`) and
  "`Connection.__init__` never ran" (comment in
  `dataclass_inherits_plain.py`) are inside fenced code blocks,
  out of this skill's scope.
- The "is what" constructions all pass the global rule's own
  carve-out (a noun phrase or clause that cannot attach without it):
  "`f3()` is what forgetting looks like",
  "It is what you do with any immutable value",
  "which is usually what an email address should mean",
  "which is not what you mean".
- "the annotation on the left already names the type": "already"
  draws the real contrast that makes the factory subscript look
  redundant.
- "even nested inside other structures" (JSON encoder): "even" marks
  the surprising extension, which is the sentence's point.
- "It gains one thing:" is a colon introducing the listing that
  demonstrates the gain, not a §69 staged reveal.
- "not that `@dataclass` changes the annotations, but that it builds
  something to act on them" is a real contrast, not §9 negative
  parallelism.
