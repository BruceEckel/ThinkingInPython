When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Readability pass over `Chapters/10_Cleanup.md`, run after the clean-slate deep
review (`deep_review/~10_Cleanup.md`), which had already cleared most of the
watch-list vocabulary ("at all", "already", the stranded prepositions).
The chapter's rhythm is varied and its claims are concrete throughout;
no AI-tell clusters appear.
This run produced no live blocks: two settled-rule violations were fixed
directly, and everything else found was judged deliberate and kept.

## Applied directly

- Line 66, imperative-plus-consequence rule: "Run `cleanup.py` directly and
  three more pairs of lines follow the last one above" is now the condition
  form, "If you run `cleanup.py` directly, three more pairs of lines follow
  the last one above". The transcript is shown right below, so the sentence
  is a hypothetical whose result the prose states, not an instruction;
  the exercise imperatives are the carve-out and are untouched.
- Line 241, bare-"raises" rule: "shows it running when the body raises" is
  now "when the body raises an exception".

## Considered and declined

- "`Safe` printed on the way out" (finalize_trap prose). "The way out" is on
  the don't-use list, but that entry bans the noun phrase meaning a solution
  or escape; "on the way out" is the exit idiom, meaning "as it was being
  reclaimed", a different construction with a literal referent one sentence
  earlier ("the collector reclaimed `Safe`"). Compact, vivid, kept.
- "The dictionary is what you want as soon as you look instances up rather
  than count them." Both "is what" and "want" are watched. The cleft
  survives its own rule's test (the words after it are a clause that cannot
  attach without it), fronting "The dictionary" carries the contrast with
  "A `WeakSet` would do for counting alone", and "want" is addressed to the
  reader, the same carve-out that kept 31_State_Machines' "a bug you want
  flagged" (readability_db).
- Two uses of "happen": "where the release happened at an unknowable moment
  after the program's last statement" (after `closable.py`) and "so the
  release happens at a point in the program you can see" (The Rule). Both
  are the watched word's legitimate use: the subject is already the concrete
  noun ("the release"), so no stronger verb is hiding behind it, and the
  candidate replacements (occurs, takes place) are synonym swaps, not
  improvements.
- "an object that never goes away" (before `finalize_trap.py`). "Never" is
  on the avoid-if-possible list, but the sentence's claim is the permanence
  of the leak; nothing else says it.
- "the only thing a cycle costs now is the delay." "Only" draws the real
  contrast with the pre-3.4 behavior (objects stranded in `gc.garbage`)
  named in the same sentence.
- "This runs even when an error interrupts the code" (Reliable
  Alternatives, item 1). "Even" marks the real contrast the second half of
  `closable.py` then demonstrates.
- "at a line you can point at" was already considered and kept by the deep
  review (mid-sentence phrasal construction, not sentence-final stranding);
  not re-raised.
- "That was one run on one machine." A short human beat doing real
  epistemic work before the opposite-order observation; left alone.
- "This chapter shows the shape; that one explains it." Metadiscourse by
  shape (§70), but it states a real division of labor with the Context
  Managers chapter rather than glossing what was just said.
