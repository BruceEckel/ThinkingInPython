When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

First readability review of `Chapters/24_Singleton.md` in this sweep.
The chapter is clean: varied sentence rhythm, concrete claims throughout,
no Tier 1A vocabulary, no curly quotes, no spaced ` -- `.
The findings were two §53 "worth knowing/understanding" frames,
two watch-list "happen" uses, and one "anyway", all applied directly.
No live blocks: every finding had one defensible answer.
Checked against `readability_db.md` and
`deep_review/~24_Singleton.md`'s declined items;
"exactly once" (note 2) and the question-form heading stay per the latter.

## Applied directly

- Line 145 (privacy section), watch list "anyway": "`type(settings())`
  recovers it anyway" is now "`type(settings())` still recovers it".
- Line 331 (Classic Implementations intro), §53 endorsement frame:
  "The variations shown here are worth understanding, but each does more
  work than..." is now "Each variation shown here does more work than the
  module or the cached factory above." The recommendation half was
  redundant with the section handoff two sentences earlier ("The rest of
  this chapter is here for the techniques it demonstrates, not because
  you need these forms"). Close alternative: name the techniques instead,
  but the next paragraph enumerates them.
- Line 396 (`__getattr__()` typing), watch list "happen": "whatever the
  inner object happens to hold" is now "whatever the inner object holds";
  "whatever" alone carries the arbitrariness.
- Line 445 (`__new__()` section), §53 "worth knowing": "the return value
  carries a rule worth knowing:" is now "the return value decides whether
  `__init__()` runs:", stating the rule the colon introduces instead of
  rating it.
- Line 449, watch list "happen": "so all the work happens in `__new__()`"
  is now "so `__new__()` does all the work" (active, literal verb).

## Considered and declined

- "No class, no ceremony." (module section). §9-shaped clipped negation
  fragment, but it is the deflating beat after the listing, the same
  voice move `readability_db.md` preserved in 30_Observer. Kept.
- "Mutate through any name. Rebind only through the module." and its
  later echo "Mutate through any name. Declare only what you rebind."
  §31-shaped staccato pairs, but the repetition is the chapter's design:
  the locked listing's prose names the echo ("the chapter's opening
  distinction seen from inside a function"). Kept.
- "You might wonder why `__call__()` intercepts the constructor for a
  `Registry`." §41/§43-adjacent by shape, but a genuine teaching move;
  the deep review repositioned this paragraph and kept the phrasing. Kept.
- "the simpler hooks that replace most metaclasses" (metaclass
  paragraph). "hooks" is on the avoid list, and 33_Visitor's annealing
  changed one to "method", but here the word points into chapter 17,
  which uses "hook" as its established term throughout (ten-plus uses,
  including a `hook_order.py` listing). Renaming it here would break
  terminology with the chapter the sentence cross-references. Kept.
- "If you really want many handles sharing one set of state" (decision
  list). "really" reads as an empty adverb, but it carries Martelli's
  distinction between the surface ask (one object) and the underlying
  need (shared state). Kept.
- "exactly one instance" (twice) and "so the class already appears in
  the module's public signature". Both watched words earn their place:
  the counts are precise, and "already" marks that the return annotation
  exposes the class before any privacy measure applies. Kept.
