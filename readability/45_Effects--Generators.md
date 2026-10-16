> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: 45_Effects--Generators

The chapter reads as finished technical prose: no Tier 1A or Tier 2 vocabulary, no signposting beyond the opening roadmap, no stacked transitions, no staccato runs, and sentence lengths that vary.
The watch-list sweep finds one "real" and three restrictive "only"s, each covered by a recurring keep in `readability_db.md` or a ruled-fine shape.
Two "and" splices joining clauses with different subjects were split, and one pointer with two candidate targets was rewritten.
This file holds no live block, so it is the applied-directly record.

## Applied directly

- Line 277, global rule (name the noun when a pointer could point two ways): "A call such as `next()` on an exhausted answer source also raises `StopIteration`, so that `next()` call belongs outside the `try`." -> "Any other call that can raise `StopIteration`, such as `next()` on an exhausted answer source, belongs outside the `try`." "that `next()` call" could be read as `drive()`'s priming `next(conversation)`, which also sits outside the `try`; the rewrite names the class of call the sentence means.
- Line 289, global rule (split an "and" between different subjects; "whereas" fits): "The generator declares requests, and the driver interprets them." -> two sentences.
- Line 739, same rule: "A queue keeps the live generators, and the runner gives each a turn:" -> "A queue keeps the live generators. The runner gives each one a turn:" The colon now sits on the sentence that introduces the listing.

## Considered and declined

- Line 5, epigraph, "Python's generators can do that, and an Effect system is built on it.": a different-subject "and", but the epigraph's three-line rhythm is the author's. Kept.
- Line 17, "a generator is not a sequence but a conversation": §9 by shape, but the contrast is real (the sequence view from [Iterators] against the two-way view this chapter teaches), and "conversation" is the chapter's working term from here on.
- Line 20-24, "This chapter covers ...": §28 roadmap, but it introduces the italicized term *driver* and names the three pieces Stateless builds on. Kept.
- Line 95, "the annotation states the arrangement and a type checker enforces it": two steps of one mechanism (declare, then check), additive. Kept.
- Line 185, "The `# type: ignore` marks a real mismatch.": §34, but the contrast is named in the paragraph (the interpreter accepts the call, the type checker correctly rejects it), against a pragma that silences a false report ("real/actual" keep).
- Line 199, "The match is deliberate.": a short beat among long sentences, followed by the reason. Kept.
- Line 211, "Typically, a driver function steps the generator.": the hedge marks a real alternative, since `drive_by_hand.py` stepped the generator without a driver function.
- Line 276, 349, 447, "only the `send()` call", "only after", "only when": ruled-fine shapes, each restriction the claim.
- Line 338, "the line delegating to `one()` contributes one value and the line delegating to `three()` contributes three": both clauses hang on one "so"; splitting them would leave the second without its cause.
- Line 652, "`GeneratorExit` propagates, the `finally` block runs, and the generator ends": steps of one sequence, so the "and" is additive.
- Line 731-737, the three ideas Stateless builds on: a rule-of-three by shape, but the three items are the chapter's three sections. The third sentence's different-subject "and" stays so the passage keeps one sentence per idea.
- Line 857-858, "the question stops being what a function does and becomes what it requests": a closing reframe by shape (§32), but the next sentence makes it concrete (the next chapter types those requests in the return annotation), so it is a bridge, not a kicker.
