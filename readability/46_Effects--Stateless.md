> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: 46_Effects--Stateless

The 2026-10-16 readability sweep of chapter 46 found no cluster of AI tells:
no Tier 1A vocabulary, no signposting, no generic closers.
What it found were the global rules' mechanical cases,
mostly an additive "and" joining two clauses whose relation is a contrast,
plus one sentence that called a bound function a handler.
Every finding had one sensible answer, so this file holds no live block
and serves as the record of what changed.
`tip reflow CH=46` and `tip verify-ch CH=46 ISOLATED=1` passed after the edits.

## Applied directly

- L100, and-split (contrast): "`success()` is a function that builds an Effect, and `Success` is the alias" -> two sentences.
- L200, and-split (contrast): "`A` and `E` share the first type parameter, and `R` is the third" -> two sentences.
- L209, and-split (partition): "is a failure, and everything else is an Ability request" -> two sentences.
- L410, and-split (different subjects, each a claim): "and the type records which Abilities each layer leaves open" -> its own sentence.
- L441, accuracy and watch word `already`: "`chosen` is a second handler already applied to `greet`" -> "`chosen` is `greet` with a second handler applied". The listing binds `chosen = supply(Console("chosen"))(greet)`, a function, which the paragraph's later "`chosen` is already `(str) -> Success[None]`" also says.
- L1130, and-split (contrast): "`register()` puts an instance in, and `get()` looks up an instance by type" -> two sentences.
- L1270, and-split plus `only` before a code span: "The driver answers it, and `supply()` handles only a `Need`" -> "The driver answers it. `supply()` answers `Need` requests and passes every other Ability outward." The outward pass is the re-yield that Layering Handlers states.
- L1811, and-split (contrast): "The caught error moves to the result and the uncaught one remains" -> "... moves to the result. The uncaught one remains in the channel."
- L1846, and-split (contrast) in a list lead-in: "Emptying a channel takes one of two vocabularies, and a third case needs none:" -> "A channel empties in one of three ways, two of which take a vocabulary of their own:". The lead-in now counts the three items that follow it.
- L1858, §31 staccato run: "The vocabularies differ. The operation underneath them is the same. Both subtract from the type." -> "The vocabularies differ, but the operation underneath them is the same: each subtracts from the type." This also removes the "Both" that could point at either the vocabularies or the operations.

## Considered and declined

- L271 and L1281, `already` in "a function that already returns an Effect": marks that the function is an Effect before `@throws` or `wait()` would make it one, the work-the-reader-skips sense the recurring keeps cover.
- L448, `already` in "`chosen` is already `(str) -> Success[None]`": temporal, since the inner `supply()` ran before `fallback` wraps it.
- L1394, `even` in "takes time, even for an Effect with no `Async` in it": the concession is the claim (the loop starts whether or not the Effect needs it).
- L1397, "a plain function call": "plain" contrasts with the `run()` call the sentence is measuring, which is also a function call.
- L1398, "That is the cost behind": a measured time (650 and 75 microseconds), which R2 keeps.
- L1133, "matches the key exactly": a precise matching rule, set against `isinstance()` two lines later.
- L454, "a genuine default": the sentence names the contrast (silencing a type error).
- L173, "Two details in `greeter.py` matter:": §39 by shape, but a count lead-in to a numbered list that the next section picks up by number ("The first detail").
- L14-15, "the check fails" twice: parallel repetition for rhythm.
- L1163-1164, "DI meets its goal. The `Console` is swappable.": two beats before a long "But" sentence, not a staccato run.
- L203, "`A`'s bound is `Ability[Any]`, and `E`'s bound is `Exception`.": two parallel facts the paragraph introduced as "two bounds", additive.
- L1070, "`Terminal` prints Alice's greeting and `capture` stays empty.": two outcomes of one run, additive.
- L1711-1712, "A raised `KeyError` is a failure. A returned `KeyError` is data.": both halves are the chapter's own terms, so not §47 mirroring.
- L399, "Binding an implementation and satisfying the type checker are the same act.": a closer by shape, but it states the section's claim rather than a verdict on output.
- L1090, "can use only that class": the "only the X" shape ruled fine on 2026-10-04.
