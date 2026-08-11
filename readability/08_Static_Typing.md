When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

Readability pass over `Chapters/08_Static_Typing.md`,
with `readability_db.md` and `deep_review/~08_Static_Typing.md`'s
declined items read first as carry-forward.
The chapter reads as human, edited prose:
varied sentence lengths, claims tied to listings and to verified diagnostics,
no Tier 1A vocabulary, no curly quotes, no spaced `--`.
The db's standing rejection for this chapter
(keep both sentences after "the same idea checked at different moments")
was respected; that paragraph is untouched.
The few findings were mechanical, so all were applied directly;
nothing needs a decision, and there are no live blocks.

## Applied directly

- Line 103 (Catching Mistakes), filler verb phrase (§23):
  "which allows this book's build to complete successfully"
  became "so this book's build passes";
  same claim, without the bureaucratic verb chain.
- Line 464 (Type Parameter Defaults), banned "wants" family:
  "callers who want that answer write nothing"
  became "callers content with that answer write nothing".
  The close alternative was "callers who intend that answer",
  but "content with" better matches the idea of accepting a default.
- Line 483 (Type Parameter Defaults), flourish "itself":
  "one release after the bracket syntax itself"
  became "one release after the bracket syntax";
  the sentence means the same without it.
- Line 682 (Type Hint Summary), banned "spelling" metaphor:
  "Older code spells some of them differently"
  became "Older code writes some of them differently".

## Considered and declined

- **"`Circle` and `Square` never mention `Drawable`" (Protocols).**
  "Never" is on the avoid list, but this is a factual absolute about
  the code (nowhere in their definitions), not an intensifier,
  matching the 07_Classes precedent
  ("never calls a base-class constructor automatically").
- **"An explicit `Any` indicates that a value is truly dynamic"
  (Gradual Typing).** "Truly" passes the deletion test grammatically
  but carries the paragraph's contrast:
  deliberately dynamic by the author's choice,
  against the `Unknown` that comes from a missing annotation.
- **"Refusing the call keeps that from happening" (Variance).**
  "Happen" is a watch word, but the antecedent is a genuine event
  (appending a `Shape` to a list of circles),
  and the deep review shaped this sentence two commits ago;
  "prevents that" would be drier for no gain.
- **"`Blob` is the case worth watching" (Protocols).** §53 shape
  ("worth" rating information), but the colon delivers the reason
  in the same sentence, and the frame picks Blob out of the
  listing's four classes as the instructive failure. The other
  "worth" hits ("worth the words," "worth naming precisely")
  sit inside the carve-out: each weighs annotation effort
  against a stated cost.
- **"What should the type annotation be?" (The `Self` Return Type).**
  A rhetorical question by shape (§43), but it poses the section's
  genuine design problem rather than stalling before a point,
  and it is the chapter's only one.
