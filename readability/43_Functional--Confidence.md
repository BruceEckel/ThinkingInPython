> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over `Chapters/43_Functional--Confidence.md`, 2026-10-16.
No earlier `~` review exists for this chapter, so `readability_db.md` set the carry-forward.
The chapter reads cleanly: the watch-list hits are all keeps under the recurring rulings, and the AI-writing tells were three, all fixed directly.
This file holds no live block, so it is the record of what changed and what was looked at and kept.

## Applied directly

- L378-380, §31 staccato run: four clipped sentences opening "Shrinking a Failure" ("... both pass. Shrinking needs a failure. The next codec has a bug. Hypothesis exposes it ...") -> two sentences, "Shrinking needs a failure, but `property_check.py` and `test_property.py` both pass. The next codec has a bug that Hypothesis exposes with unusual Unicode:".
- L421-422, treadmill restatement: "Hypothesis finds it by drawing from a wider alphabet, treating `decode()` as opaque throughout" repeated the paragraph's opening sentence ("Hypothesis draws from every character UTF-8 can encode") -> "Hypothesis finds it while treating `decode()` as opaque throughout."
- L471, §9 negative parallelism: "The claim these chapters share is not that functions are special. It is that purity, ..." -> "The claim these chapters share is that purity, ...". The contrast with functions stays in the same paragraph, where "That gain, more than the presence of functions, is the 'functionality' the introduction sets out to find" already carries it, so the "not X. It is Y." frame said it twice. The close alternative was to keep the frame and cut "more than the presence of functions" instead; the later sentence is the one that ties back to the introduction, so it kept the contrast.

## Considered and declined

- L7, "functions really are a central part of the practice": §34, but the sentence names its contrast ("usually call it ... But ..."), and it is first-person opening voice.
- L14, "perhaps some should even be mathematically provable": "even" marks a real escalation from "fit that definition" to "provable".
- L29, "and that is the reason purity matters:": the colon introduces the listing that demonstrates the property; the clause carries the section's claim.
- L104-105, "looks safe. It is not.": a short beat among longer sentences, not a staccato run.
- L118-119, "The more of your program is referentially transparent, the more of it a machine can optimize and a proof can cover.": §32 shape, but it generalizes the two cases the paragraph just named (`lru_cache`, a query planner) and leads into the cached-`withdraw()` listing.
- L165-166, "Purity removes the problem instead of managing it. With nothing shared, a lock has nothing to guard.": the contrast is the lock just described, and the second sentence gives the reason.
- L240, "Can programming make provable claims?": the question is the section's content and the chapter's only one (recurring keep).
- L244, "Together they provide confidence at every level.": vague by shape, but "every level" points at the numbered rungs that follow.
- L246 onward, "spectrum" with "rung": a mixed figure, but the heading and the numbered list depend on both words, and the pairing is the chapter's terminology rather than an AI tell.
- L293, "Formal proof is real, but rare outside specialized work.": §46 shape, but the concession is the claim (it exists, and it is uncommon).
- L374, "The framework automates falsification.": ties the Hypothesis section back to the introduction's "falsifiable"; a beat, not a verdict on output.
- L429, "A real test keeps the defaults.": §34, with the contrast named two sentences later ("a demonstration rather than a test").
- L438, "Knowing the family is most of the skill.": an authorial stance, the one such sentence in the section.
- L465, "Functional programming does not make correctness provable so much as it makes the proof short enough to write.": the negation is half of the chapter's central contrast.
- L211, L277, L492, L510: "only when", "only for", "only the counts", and "exactly one" are ruled-fine shapes or a numeric match.
