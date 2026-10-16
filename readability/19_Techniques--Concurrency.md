> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over `Chapters/19_Techniques--Concurrency.md` (2026-10-16 sweep).
No earlier review of this chapter exists, so `readability_db.md` was the carry-forward.
The chapter is already tight technical prose with few AI tells;
six findings had one sensible answer and were applied directly.
This file holds no live block: it is the applied-directly record.
`tip reflow CH=19` and `tip verify-ch CH=19 ISOLATED=1` passed (27 of 27).

## Applied directly

- 1017, §34 real-adjective inflation: "A real livelock looks busy on a monitor" -> "A livelock looks busy on a monitor". The paragraph compares livelock with deadlock in general, and the "real" echoed the previous paragraph's "A real livelock repeats these rounds forever", where the contrast with the demo is named and the word stays.
- 1123, §70 interpretive metadiscourse: "That distinction matters when scopes nest." -> "So when scopes nest, leaving an inner `with` block restores the value the outer one set." States the consequence of the sentence before it instead of rating it.
- 1373, §53 endorsement frame: "the two constants worth changing" -> "the two constants to adjust". The next sentence gives the instructions, so the frame now matches them. Close alternative: keep it under §53's instruction carve-out.
- 1394, §34: "yields real gains up to a point" -> "yields gains up to a point". No contrast named.
- 2080, §34: "Two real points of convergence exist" -> "Two points of convergence exist". The sentence keeps "genuinely", whose contrast ("not because the models are secretly the same") is named in the same sentence; two intensifiers in one sentence was one too many.
- 2624, §53: footnote label "Libraries worth exploring:" -> "Libraries to explore:".

## Considered and declined

- 10, "Performance is about the math, while concurrency is about the machine." §32 aphorism by shape. Kept: a real contrast that frames the chapter against the one before it, in the author's opening voice.
- 85-86, "more CPUs simply meant more resources to distribute (of course, it wasn't quite that easy)." "simply" is an empty adverb by the deletion test, but the aside deflates it on purpose; the pair is voice.
- 145, "suspends itself and yields control ... but not to the OS." Deliberate spoken beat; "itself" is reflexive.
- 325, "The event loop overlaps waiting, not computing." One-sentence paragraph stating the section's principle, a beat rather than a staccato run.
- 484, "How does `gather()` respond to a failure?" Rhetorical question that names the problem the section solves (`readability_db.md`, rhetorical-question keep).
- 633, "The real mistake is catching too much." §27 by shape. Kept: the previous sentence shows that `except Exception` is harmless, so "real" names its contrast.
- 1014 and 958, "A real livelock repeats these rounds forever." / "A real deadlock has no `timeout`." Each contrasts with the demo's bounded run, named in the next sentence.
- 1215 and 1353, "cost more to pickle" / "costs more than the better load balancing saves." Commerce words, but they name a measured quantity (time), which rule R2 keeps.
- 1488, "not worth the effort." §53 carve-out: weighs a stated effort.
- 1576, "That is scheduling luck, not safety." Short beat among long sentences.
- 1906, "Nothing in the language stops you, and nothing in the language makes it work." Deliberate parallel, repeated word for rhythm.
- 2008 and 2024, "only in the way a crash is better than corruption" / "looks like the answer and is not." Voice.
- 2123, "Three unrelated kinds of worker produce one set of answers." Considered against the 2026-10-04 ruling that cut verdict fragments; this is a full sentence that states the section's point for a listing with no `#:` markers, so it stays.
- 2462-2463, "famously muddied the waters" and the bold **only**. First-person voice in the closing section; the bold marks the word his reading of Pike turns on.
- 2481, "almost inevitably". The hedge carries meaning, so the empty-adverb rule does not fire.
- Guidelines list (2402-2456), bold-label bullets. §16 by shape, but every chapter's Guidelines section uses this form.
