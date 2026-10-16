> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability review of `Solutions/47_Effects--Stateless_in_Practice/README.md`,
2026-10-16.
The prose carried no AI-vocabulary clusters and no watch-list hits that
needed changing. The findings were mostly "and" joining clauses with
different subjects, where the relation was a consequence or a contrast,
plus one aphoristic restatement, one repeated subject, and one "fails"
with two possible subjects. Every fix had one sensible answer and went in
directly, so this file holds no live block and serves as the
applied-directly record. Line numbers are those of the file before the
edits. Rewritten paragraphs were rewrapped at about 70 columns; the rest
of the file keeps its mixed wrapping. `tip verify-ch CH=47 ISOLATED=1`
passed, 27 of 27.

## Applied directly

- Lines 140-144, aphorism and treadmill: "Reading a clock twice reads a
  changing value twice, and two readings are two facts rather than one"
  restated the sentence before it. Folded into it as a reason: "... the
  general shape of a clock bug, since two readings of a changing value
  are two facts." The last sentence's repeated "the failure" became "it".
- Lines 473-474, "and" hiding a consequence: "hour 20 has no supplier,
  and the `Blackout` propagates out of `run()`" became two sentences.
- Lines 583-591, repeated subject and a split thought: "The test cannot
  tell you ... The test leaves every question" became "... It leaves
  every question"; "The scripted handler ignores `request.hour`.
  Ignoring the hour makes the handler simple to write" became "The
  scripted handler ignores `request.hour`, which makes it simple to
  write and means ...".
- Lines 594-595, "and" hiding a consequence: "`controller()` builds an
  ordinary function ..., and a test can call that function" became
  "..., so a test can call that function".
- Lines 829-830, "and" joining different subjects: "`research.py` takes
  four edits, and the type checker names one of them" became "takes
  four edits, one of which the type checker names".
- Line 1291, "and" joining different subjects: "`spree()` attempts all
  four prices, and the test proves it from both sides" became "The test
  proves from both sides that `spree()` attempts all four prices."
- Lines 1296-1298, "and" joining different subjects, plus tense: "Stopping
  early leaves a balance unread, and the final assertion catches that"
  became "Stopping early would leave a balance unread, which the final
  assertion catches", matching the paragraph's conditional "would".
- Line 1309, pointer with two candidates: "A `spree()` that writes the
  wrong amount ... still fails" could mean `spree()` fails. Now "still
  fails the test". Checked against `test_ch47_wallet.py`, where
  `assert written == [40, 10]` catches a wrong write.
- Lines 1421-1422, "and" joining two separate claims: "The two versions
  produce the same results, as the loop demonstrates, and `reveal_type()`
  reports ..." became two sentences.
- Lines 1442-1443, "and" joining a claim and its reason: "The decorator's
  argument is a claim about the function, not a check on it, and no type
  checker compares ..." became two sentences.
- Line 1553, "and" joining different subjects: "Adding `| TooLong` ...
  fixes it, and the `print()` at `[1]` exercises the new branch" became
  two sentences. The `[1]` reference still precedes the next listing.
- Line 1559, "and" hiding a consequence: "Pyright does infer the union
  from the body, and under Pyright the function changes its type" became
  "..., so under Pyright ...".
- Line 1575, "and" standing for "but": "A type checker verifies claims,
  and an inferred type is not a claim" became two sentences.
- Lines 1715-1716, "and" joining the halves of a contrast with different
  subjects: "The accessor's annotation serves the type checker, and the
  handler's annotation is data ..." became two sentences.
- Lines 1855-1856, "and" joining different subjects: "That union is the
  answer to "what does `buttered()` need," and the fix is to write it
  down" became "... need?" The fix is to write it down."

## Considered and declined

- Line 269, "`catch()` cannot catch what never entered the channel." A
  short closing beat, and the "never" is the claim.
- Line 277, "`success()` is for a value you already have. `@throws` is
  for work that can fail." Contrast-pair shape (§47), but it is the
  exercise's usable rule, and "already" is temporal.
- Line 396, "`Turbine` is the only addition": "the only X" is a
  ruled-fine shape, and the claim checks out against the chapter's
  `power.py` and `microgrid.py`, which `grid.py` combines.
- Lines 841-843, a line of 112 columns holding a quoted `ty` message in
  a code span that crosses a line break. Left unwrapped so the quoted
  diagnostic's text stays as it is.
- Lines 849-850, "Each missing edit fails the type check ... The type
  checker reports each line the change requires, one edit at a time."
  Close to a restatement, but the second sentence adds "one edit at a
  time", the sequence the paragraph has just walked through.
- Lines 1061 and 2040, "worth retrying", "worth naming": each weighs a
  real cost (wasted retries, a pattern's ceremony), the recorded keep.
- Lines 1447-1449, "Keep `@throws` for ordinary code that raises
  exceptions, such as `latest()`." The decorator sits on `fetch()`,
  which wraps `latest()`; the example names the raising code, so it
  stays.
- Lines 1583-1597 (exercise 12's prose) and lines 2035-2038, "already
  an object with a type": "already" marks work the reader does not have
  to do.
- Lines 2069-2072, "The same distribution is why the chapter uses a
  factory function rather than more `supply()` arguments." The reason
  that follows is the nine-actor ceiling, not the distribution, so the
  link is loose. Rewording it would change what the paragraph argues;
  left for an editing pass.
- Lines 1146-1155, "Without the guard, each worker builds another
  pool." Repeats the paragraph that opens the solution, but it closes the
  "Guard the driver" step, which a reader opening the steps one at a
  time sees on its own.
