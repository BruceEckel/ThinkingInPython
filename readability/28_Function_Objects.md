When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Readability pass over `Chapters/28_Function_Objects.md`.
`readability_db.md` binds two items here, both honored:
"Python's best-known closure trap" stays,
and "to say what one list of functions says directly" was not touched.
The deep review (`deep_review/~28_Function_Objects.md`) ran two days ago
and its style audit already removed the watch-word hits this pass hunts
("happens", an imperative-plus-consequence sentence),
so the prose comes to this pass close to clean.
The mechanical sweep found no curly quotes, no spaced ` -- `,
no Tier 1A vocabulary, and no structural tells:
the colons are definitional ("Three identical lines is the point: ..."),
not §69 reveals; the closing ladder is a genuine five-item decision list;
sentence lengths vary well
("Both do the same thing." against the long mechanism sentences).
One direct fix; no live blocks.

## Applied directly

- Line 102, watch-list "already" (filler by the deletion test):
  "names a function with its instance already attached" is now
  "names a function with its instance attached".
  The preceding sentence's "ready-made command" carries the
  came-that-way emphasis, and ladder item 2 states the same fact
  without the word.

## Considered and declined

- Intro, "a job the caller already has" and "In Python a function is
  already an object": both "already"s earn their place. The first marks
  the Command/Strategy contrast (the job is in hand before the *how* is
  chosen); the second is the chapter's thesis (no wrapping needed, the
  language provides the object). Kept.
- "when a configurable version already exists with the setting as a
  parameter": "already" draws the real contrast with the closure branch
  (the function pre-exists rather than being manufactured). Kept.
- "In Python a callback is just a function": "just" is the deflating
  beat against GoF's "object-oriented replacement for callbacks" quoted
  in the previous sentence, not filler emphasis. Kept.
- "plain function(s)" (three uses) and "plain functions" in the bound
  method sentence: each draws the chapter's own contrast against bound
  methods, closures, callable objects, and base classes, which is the
  carve-out the global rule names. Kept.
- "at the cost of an event type no longer naming its audience by
  itself": "by itself" means "alone" and is load-bearing; with the MRO
  walk, the type no longer determines the audience on its own. Kept.
- "A `Command` base class becomes worth writing when the commands also
  share implementation": "worth" carries a real weighing (class cost
  against shared implementation), which §53's carve-out allows. Kept.
- "Building commands in a loop springs Python's best-known closure
  trap": binding keep in `readability_db.md`; not re-flagged.
- "The class version is four classes and a wrapper to say what one list
  of functions says directly": recorded in `readability_db.md` as the
  chapter's sharpest sentence; not touched.
- The trailing participles ("trying candidates until one accepts",
  "letting the `defaultdict` build each event type's list on first
  use", "leaving a stray entry behind ..."): §3 by shape, but each
  states a concrete mechanism or consequence, not fake depth. Kept.
- "Three identical lines is the point: the caller does not change when
  the algorithm does": §70-adjacent self-labeling by shape, but the
  sameness of the output is the pedagogical claim, and the colon's
  second half supplies the support the rule asks for. Kept.
