When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Readability pass over `Chapters/29_Changing_the_Interface.md`,
run after the deep review in `deep_review/~29_Changing_the_Interface.md`.
The chapter is clean: varied sentence rhythm, no Tier 1A vocabulary,
no signposting or colon-reveal staging, no hedge stacking.
The deep review's declined list was honored
("differ only in where the adaptation lives" keeps its "only",
the Façade Singleton/Abstract-Factory sentence stays,
the wrapper table's "nothing" cells stay).
One direct fix, no live blocks.

## Applied directly

- Line 289 (module-façade paragraph), delayed-verb cleft:
  "What the underscore does mechanically is keep the name out of
  `from checkout import *`" is now
  "Mechanically, the underscore keeps the name out of
  `from checkout import *`".
  The cleft only delayed its verb;
  the fronted adverb keeps the contrast with
  "a convention, not a barrier" two sentences up.

## Considered and declined

- **Contrastive italics on "*where*" (Adapter) and "is a *module*"
  (Façade).** Both match a book-wide convention:
  28_Function_Objects uses "*what*"/"*how*" for the same contrast,
  and "is a *closure*" (ch. 14, 40), "is a *hook*" (ch. 25),
  and "is a *handler*" (ch. 44) all introduce a thing in its new role
  the way "is a *module*" does here.
- **"What separates them is intent" (Telling the Wrappers Apart).**
  A wh-cleft, but its complement is a noun phrase carrying an
  appositive, the global rule's keep case;
  "Intent separates them" would orphan the apposition.
- **"already" twice** ("Both wrap something that already exists";
  "A module already presents a curated set of names").
  Each earns its place: the wrapped thing predates the wrapper,
  and the module form costs nothing extra against a `Facade` class.
- **"never fires"** (overload deprecation).
  Factual, not an intensifier:
  Python discards overload declarations at runtime.
- **The run of "X, not Y" contrast pairs**
  ("a thin wrapper, not a hierarchy"; "a convention, not a barrier";
  "an agreement ..., not a lock"; "a warning, not a break";
  "for why it is there, not for its shape").
  Each carries a real correction of a likely misreading,
  none is the "not only ... but" or tailing-negation form §9 targets,
  and the density reads as the chapter's voice.
- **"is how you make the risk visible" (closing paragraph).**
  Cleft-adjacent, but the sentence was settled by the deep review
  one pass ago and the gerund-subject rhythm reads as deliberate.
