> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Effect Management, Solutions

The Solutions file for chapter 44 carries no Tier 1 or Tier 2
vocabulary, no signposting, no significance inflation, and no
manufactured punchlines.
Most of the thirteen direct edits split an "and" that joined clauses
with different subjects, where the relation was a consequence or a
contrast.
Two correct a claim against its source: exercise 2's Koka paragraph
said the four functions stay "as they were", though `greet()` gains a
log call and a helper call, and exercise 3 said the chapter "calls"
the conversion "pushing the Effects to the edges", where the chapter
reports what people call it.
Edited paragraphs are rewrapped to the file's 70-column hand wrap.
This file holds no live block, so it is the record of the applied
edits and the declined findings.

## Applied directly

Line numbers are in the edited file.

- Line 236, "and" hiding a contrast: "Five signatures name the new Effect, and only two of them use it" -> two sentences.
- Lines 257-260, "and" joining two claims with different subjects: "The function's signature hides that it logs, and every test runs with the logger the module chose" -> two sentences, each a separate consequence of removing the choice.
- Lines 275-279, accuracy and "and" splice: "leaves `greet()`, `session()`, `menu()`, and `main()` as they were, and the compiler adds `log` to each of their rows" -> "leaves the signatures of `greet()`, `session()`, `menu()`, and `main()` as they were. The compiler adds `log` ...". In the exercise `greet()`'s body gains a `log.log()` call and the helper call, so only the signatures stay; the paragraph's lead sentence ("removes the signature edits") already scopes it that way.
- Lines 343-346, personification: "`withdraw()` takes the by-hand technique from [Effects by Hand] instead:" -> "the by-hand technique from [Effects by Hand] applies instead:". The colon still delivers the technique.
- Lines 348-349, "and" joining two consequences with different subjects: "The same inputs then give the same answer, and the caller holds the state" -> two sentences.
- Lines 361-363, "and" joining different subjects: "returns each reading as a value from the temperature source, and the caller folds new readings ..." -> two sentences.
- Line 363, misattribution: "The chapter calls that conversion [pushing the Effects to the edges]" -> "The chapter quotes the common name for that conversion, [pushing the Effects to the edges]". Chapter 44 line 374 reads "People call this 'pushing the Effects to the edges.'" Link target unchanged.
- Lines 444-445, "and" hiding a contrast: "`validate()` rejects negatives but lets zero through, and the `try` catches zero but lets negatives through" -> two sentences.
- Lines 451-452, "and" hiding a consequence: "so dividing by it always succeeds and the `try`/`except ZeroDivisionError` goes" -> "A `PositiveInt` holds a value of 1 or more. Dividing by it always succeeds, so the `try`/`except ZeroDivisionError` goes." This matches the next sentence's "so the call to `validate()` goes".
- Lines 464-465, "and" joining two claims with different subjects: "is pure with respect to this failure, and its signature says which values it accepts" -> two sentences.
- Lines 515-516, "and" joining the checker's report to the runtime failure: "`ty` reports `no-matching-overload` at the `sum()` call, and the `asyncio.run()` call raises a `TypeError` ..." -> two sentences. The shorter pair at line 563 stays (see below).
- Lines 572-573, function reference and a verb used as a noun: "`ty` reports `price_of_async`'s return as" -> "`ty` reports the return type of `price_of_async()` as". The bare name at line 517 stays, since it quotes the `RuntimeWarning`.
- Line 585, "and" joining different subjects: "It says 'run this particular coroutine,' and the coroutine's body defines what awaiting it does" -> two sentences.
- Line 592, "and" hiding a contrast: "`asyncio.run()` chooses an event loop, and that choice sounds like late binding until ..." -> two sentences.

## Considered and declined

- Line 563, "Without the brackets, `ty` reports `no-matching-overload`, and the `sum()` call raises a `TypeError`." The clauses have different subjects, but the sentence is short and lists two parallel results of one omission, so the "and" is additive.
- Lines 560-562, "because a generator expression with an `await` inside it is an asynchronous generator, and `sum()` requires a synchronous iterable." The two clauses are the two premises of one reason; a period would cut the reason in half.
- Lines 567-568, "must then become `async` in turn, and the propagation continues up to `asyncio.run()`". One story continued, not a contrast or consequence.
- Lines 320-321, "`slope()` catches the `ZeroDivisionError`, and in `slope_nonzero.py` a restrictive type makes a zero `run` unconstructable." An enumeration of the two conversions the previous sentence names, so additive.
- Lines 571-579, treadmill check: the paragraph restates the propagation the "Run the coroutine at the edge" step describes. Kept, because its job is to map that propagation onto property 1 of the chapter's three-item list, which the next two paragraphs then contrast with properties 2 and 3.
- Line 553, "Making the helper `async` forces four changes." followed by three bold steps. The first step carries two changes (await each call; `total_price()` becomes an `async def`), so the count holds.
- Lines 583 and 591, bold inside a sentence ("It does not **separate the interface from the implementation**"), §15 by shape. The bold names the two items of the chapter's list that the paragraphs test, so it is a label, not emphasis.
- Lines 597-598, "The event loop is a scheduler, not a handler." A short beat that closes the paragraph; "handler" is the chapter's term, so §47 does not apply.
- Lines 365-368, "three storage mechanisms for one idea: something outside the call participates in the result." The colon delivers the idea the lead-in names.
- Line 88, "The substitution is the point either way." Kept as voice; "either way" points at the interactive and scripted runs just described.
- Line 256, "Most codebases avoid the forwarding with a module-level logger." Unsourced generalization by §5's shape, but it is the author's claim about common practice, not a vague attribution.
