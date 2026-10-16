> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Pattern Refactoring

Readability sweep of 2026-10-16 over `Chapters/37_Patterns--Pattern_Refactoring.md`.
The chapter was already lean: no Tier 1A vocabulary, no chatbot artifacts, no signposting.
Five small fixes went in directly, and no finding needed Bruce's judgment,
so this file holds no live block and serves as the applied-directly record.
Line numbers refer to the chapter after the edits.

## Applied directly

- Line 22, §31 staccato run in the opening paragraph:
  "Then a second vector of change appears. The reshaped design leaves it unsolved."
  -> "Then a second vector of change appears, one the reshaped design leaves unsolved."
  (five short sentences in a row; this merges the pair that shares one subject)
- Line 293, §53 endorsement frame: "The wildcard is worth adding, but the flaw remains."
  -> "The wildcard helps, but the flaw remains."
  (no cost is weighed, so the `worth` carve-out does not cover it)
- Line 576, wrong actor: "Three materials register a note."
  -> "Three materials get a registered note."
  (the listing registers implementations for the materials; the materials register nothing)
- Line 581, §34 bare intensifier and pointer:
  `Here "no special handling" is a genuine answer for Paper, so the fallback is correct.`
  -> "`Paper` needs no special handling, so here the fallback answer is correct."
- Line 661, figurative actor: "Each vector now touches one place."
  -> "Each kind of change now touches one place."
  (echoes line 8's "so that kind of change touches one place"; a vector touches nothing)

## Considered and declined

- Line 656, §27 "The deeper skill is spotting the vector of change".
  "Deeper" draws a real comparison with the three constructs named just before it,
  and the sentence is the chapter's thesis. Kept.
- Line 397, "Swapping the `match` for the dictionary is a redesign, not a rename."
  A closer by shape (§32), but it states the subclass consequence the paragraph just showed. Kept.
- Line 525, "The method form is a real option, not an example built to fail."
  §34 with its contrast named in the same sentence (recurring keep).
- Line 400, "an alias for a plain `dict`": "plain" contrasts with the `defaultdict` the listing uses (recurring keep).
- Line 447, "editing nothing else": "nothing else" as an object, ordinary English per the global rule.
- Line 333, "Nothing fails.": a single beat among long sentences, not a staccato run (recurring keep).
- Line 646, "Each is right for its job.": the same call.
- Line 457, "the safety officer wants": a human subject, outside the don't-use entry for "wants".
