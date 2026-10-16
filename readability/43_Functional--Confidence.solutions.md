> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Confidence, Solutions

The Solutions file for chapter 43 carries no Tier 1 vocabulary, no
signposting, no significance inflation, and no curly quotes.
The seventeen changes below split "and" joins that hid a "so" or a
"whereas", split four paragraphs that each explained two things, cut
three sentences that restated a neighbor, and make two sentences name
their real actor.
Each touched sentence was checked against its listing: chapter 42's
`describe()` has the `match result:` line and four `case` lines, and
`describe_isinstance.py` reads `result.error` three times.
`tip verify-ch CH=43 ISOLATED=1` passed after the edits (27 of 27).
This file holds no live block, so it is the record of the direct edits.
Line numbers are the file's after the edits.

## Applied directly

- Lines 66-75, one concept per paragraph: the "greater than one" paragraph and the "far below thirty-two" explanation were one paragraph joined by "But"; split, and the opening "But" dropped since "also" carries the turn.
- Lines 71-75, literal actor: "A submitted task goes to an idle worker ... and starts a new worker otherwise" (a task starting a worker) -> "The pool hands a submitted task to an idle worker ... and starts a new worker otherwise"; "Four tasks therefore start at most four processes" -> "For four tasks it therefore starts at most four processes". Also "allows one worker per core, but it starts" -> "allows one worker per core but starts", one "but" fewer beside the dropped one.
- Lines 136-138, present tense: "Counting distinct process IDs revealed process parallelism in the previous exercise but says nothing" -> "reveals process parallelism, as in the previous exercise, but says nothing". The mixed tenses read as two claims about two times.
- Lines 143-144, "and" hiding a "whereas": "`ProcessPoolExecutor` runs the calls in separate processes and `ThreadPoolExecutor` runs them in threads" -> two sentences.
- Line 294, restatement: cut "`ß` breaks the law for a different reason." Line 325 says "`ß` breaks the same law from the other side" and gives the reason; the earlier sentence was a forward pointer with nothing after it but the `µ` listing.
- Lines 321-328, one concept per paragraph: the case-mapping paragraph explained `µ` and then `ß` plus `casefold()`; split at "`ß` breaks the same law".
- Line 331, generic conclusion (§25): cut "That coverage is the argument for property testing in one example." The two sentences before it make the argument; the paragraph now ends on "characters nobody thinks to type." (Close alternative: keep it as the exercise's closing beat.)
- Lines 424-425, nominalization: "The property test finds the need for the two lines guarding an empty `groups`" -> "The property test shows that `group_rounds()` needs the two lines guarding an empty `groups`".
- Lines 429-430, "and" standing for "so": "the `while len(pool) >= size` loop runs zero times and `groups` stays empty" -> "runs zero times, so `groups` stays empty". Paragraph rewrapped at 70.
- Lines 433-441, hand wrap only: the paragraph had a 110-column line and a two-word line; rewrapped at 70, words unchanged.
- Lines 445-446, "and" joining a division of labor ("while" fit): "The property states what holds for every roster, and Hypothesis finds the roster that breaks it" -> two sentences. Paragraph rewrapped.
- Lines 452-453, run-on: "so it records both students' meetings under the same keys, and when it avoids repeat meetings it treats the two students as one" -> period after "keys"; "When it avoids repeat meetings, it treats ...".
- Lines 479-480, "and" standing for "so": "that group stays empty, and the left side of the assertion is `[]`" -> ", so the left side".
- Lines 482-484, "and" plus a contradiction with the next paragraph: "The report shows the shrunk case ..., and its names vary from run to run" sat above "A second run reports the identical counterexample". Split, and the varying names scoped: "When each run starts with an empty `.hypothesis/` directory, its names vary from run to run." The replay paragraph below and exercise 4's statement supply the scope. Paragraph rewrapped.
- Lines 596-598, restatement: cut "Move the hidden input into the parameter list.", which repeated the bold label "Make the hidden input a parameter." word for word in substance.
- Lines 694-707, one concept per paragraph: the repetition evidence (`result.error` three times) and the weak fallthrough at `[1]` were one paragraph; split at "The `return` at `[1]`". In the second, "a fallthrough that happens to be correct rather than a branch stating what it matches" -> "a fallthrough rather than a branch stating what it matches" (watch word "happen"; the deduction clause after it carries the correctness).
- Lines 715-729, cohesion and one concept per paragraph: the Pyright and mypy sentence sat between "lose that precision together" and its "therefore". It now follows the `ty` 0.0.87 claim it contrasts with, and the even-comparison conclusion opens its own paragraph, "Under `ty`, the `match` and the `isinstance()` tests lose that precision together." Words otherwise unchanged; rewrapped at 70.

## Considered and declined

- Lines 83-85, "so it is reproducible on your machine and nowhere else": the "nothing else" family by shape, but the exclusion is the claim (why the listing carries no marker), so the deletion test fails.
- Lines 166-171 and 232-234, the oracle's independence stated twice ("A property that restates the implementation tests nothing", then "That independence makes an oracle useful, and makes `assert sorted(xs) == sorted(xs)` worthless"): the closing pair adds "by a different algorithm" and ties back to the opening trap, which is the solution's frame.
- Line 433, "a real defect rather than an unstated precondition": §34, but the contrast is named in the sentence.
- Line 448, "does real work": §34 by shape; the paragraph then shows the work, against a reader's guess that `unique=True` is decoration.
- Lines 580 and 587, the bold labels "Take the time without declaring it." and "Take a setting without declaring it.": they name what `stale()` and `timeout()` do wrong rather than steps to follow, but labels are the solution's step convention and the pair is parallel.
- Lines 594-595, "No argument list records the dependency.": a negative, but the absence is the claim.
- Line 696 and line 731, "Reading, not length, separates the two versions" and "The choice is about reading, not about proving": §9 twice, but each is a real contrast the paragraph argues.
- Line 731, "Neither form tells the type checker anything the other cannot": sits below the paragraph saying the `isinstance()` version narrows `result.error` and the `match` leaves it `Exception`. The `match` binds no name there, so it has nothing to narrow, and the sentence's claim about what each form tells the checker holds; left as written.
- Line 728, "The decorator's effect is a more useful finding than a win for either version.": evaluative closer, but it is the author's judgment on the exercise's result, not a generic positive conclusion.
