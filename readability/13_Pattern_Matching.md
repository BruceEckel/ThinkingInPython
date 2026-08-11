When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This readability pass ran after the deep review
(`deep_review/~13_Pattern_Matching.md`), which had polished most of the
prose this skill would otherwise flag.
The chapter shows no AI-tell clusters:
sentence lengths vary, no Tier 1A vocabulary appears,
no signposting, no rhetorical-question transitions,
no curly quotes, no spaced ` -- `.
One watch-list fix cleared the direct-application bar;
everything else examined is recorded below so the next sweep does not
re-raise it.
No findings needed a live block.

## Applied directly

- Line 502, global watch list ("has to"):
  "Without `as` you would have to choose between testing the shape and
  keeping the object" is now "Without `as` you must choose between
  testing the shape and keeping the object."
  The counterfactual survives the modal, and the sentence tightens.

## Considered and declined

- Line 16, "`match` becomes valuable once the patterns do more than test
  equality." "Valuable" is on the §7 high-frequency list, but it is the
  single occurrence in the chapter, and a lone hit is not a tell.
  "Pays off" was the candidate replacement; the existing sentence says
  the same thing without the idiom, so it stays.
- Line 144, "`act()` also shows why an enum is worth the trouble:".
  §53's "worth the trouble" family, but the carve-out applies: the
  trouble is real (defining an enum instead of raw constants), and the
  colon delivers the payoff immediately (the checker sees the closed
  set). The frame is a weighing, not an empty endorsement.
- Line 180, "The last `case _` never runs." "Never" is on the
  avoid-if-possible list, but the claim is factual and total, and the
  phrasing is the deep review's own applied edit. Settled.
- Line 187, "even though a string is a sequence in every other context."
  "Even" sits inside the standard concessive conjunction, and the
  concession is the point of the paragraph.
- Line 470, "A sub-pattern is itself a pattern." Reflexive and
  essential: without "itself" the sentence reads as a tautology instead
  of stating the recursion that the section demonstrates.
- Line 4, "test a value's shape, look inside it, and pull out the parts
  you need" and line 415, "an ordering test ... a relation between two
  captures ... or any call": both are three-item lists by shape (§10),
  but each enumerates genuinely discrete things; neither pads to reach
  three.
- Line 139, "refusing to compile with `SyntaxError: ...`": an "-ing"
  tail by shape (§3), but it states the concrete mechanism, not fake
  depth.
