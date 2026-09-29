When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Second deep review of chapter 39, run 2026-09-29 after the day's sweep decisions
changed chapters 11, 17, 18, 19, 21, 22, 23, and 31,
and after `Borg` and `Messenger` joined `tools/data/pattern_names.txt`.
Every link target's section was read against the row that points at it
(the moved sections of chapter 19 included),
and the three claims about chapter 21 still hold.
The standing rejection in `deep_review_db.md` (no conclusion, no exercises)
and the first review's "Considered and declined" list are honored.

No finding needed a decision only you can make, so this file has no live blocks.

## Applied directly

- Intro, *State*/*State Machine*: "each state chooses its successor" described only
  chapter 31's first design; its second keeps every transition in one table.
  Now "the machine chooses each successor", which holds for both.
- *Future/Promise* link: chapter 19's `#one-task-many-backends` opens on executors
  and never says "future"; the explanation of both `Future` classes sits in its
  subsection `#one-await-any-backend`, which the link now targets.
- *Messenger* row added to Other Patterns and Idioms, linking chapter 22's
  `#a-hand-rolled-messenger`, and a problem-table row "Returning several named
  values from one call" names it with *Data Transfer Object*.
  The book now gates *Messenger* as a pattern name, and a reader who meets it
  had no entry to look it up by.
- *Surrogate* row added to Other Patterns and Idioms, linking chapter 26.
  Chapters 08, 21, 22, 24, 27, and 29 name it as a pattern in italics, and the
  catalog had no entry for it.
  (Close alternative: a note on the *Proxy* and *State* rows. A row is simpler.)
- *Identity Map*: "Load each object only once per session" dropped "only".

## Considered and declined

- *Event Bus* is in `tools/data/pattern_names.txt` but has no catalog row.
  No chapter writes it as an italic pattern name; chapter 28 introduces it as a
  lowercase term, and *Publish-Subscribe Channel* already links there.
- *Multiple Dispatching* (chapter 32's title) gets no row of its own:
  *Double Dispatch* links chapter 32, and a second row would split one entry.
