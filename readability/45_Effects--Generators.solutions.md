> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Generators, Solutions

The Solutions file for chapter 45 has no Tier 1A or Tier 2 vocabulary,
no signposting, no curly quotes, and no staccato runs. Its watch-list
hits are three restrictive "only"s in ruled-fine shapes and one "want"
addressed to the reader. The twelve changes below split "and" joins
whose clauses change subject (most of them hiding a "but" or a "so"),
cut one signpost sentence and one word echo, and turn a repeated
subject into a pronoun. Each touched sentence was checked against its
listing: `drive_in_order()` carries the comment the rewritten sentence
cites, the loop in `exercise_3.py` sends five values, and `report()`
declares `Generator[str, None, int]`. Edited paragraphs were rewrapped
at about 70 columns. `tip verify-ch CH=45 ISOLATED=1` passed after the
edits (27 passed). This file holds no live block, so it is the record
of the direct edits.

## Applied directly

- Line 15 (Hint), "and" joining different subjects: "the generator finishes, and the total is the `value` ..." -> two sentences.
- Line 84, word echo after the bold label: "**Drive the conversation by hand.** Driving `tally()` takes four calls" -> "`tally()` needs four calls".
- Lines 151-152, "and" joining two separate claims: "`drive_naive()` returns `None`, and the type checker reports nothing" -> two sentences. The ragged wrap below it ("catches the one from" on a line of its own) was rewrapped.
- Line 242, "and" hiding a "whereas": "The generator describes the conversation, and the driver interprets it." -> two sentences, matching the chapter review's split of "The generator declares requests, and the driver interprets them."
- Lines 255-258, signpost cut: "One detail in `drive_in_order()` needs its comment. `next(answers)` sits outside the `try` because ..." -> "In `drive_in_order()`, `next(answers)` sits outside the `try`, as its comment says, because ...". The cut sentence announced the detail the next sentence states.
- Line 265, repeated subject: "`drive_naive()` puts ... `drive_naive()` therefore catches" -> "It therefore catches"; the only candidate is the previous sentence's subject.
- Line 348, "and" hiding a "but": "the three collectors need six, and the loop supplies five" -> "need six. The loop supplies five."
- Line 489, "and" hiding a "whereas": "because `report()` with no `return` statement returns `None`, and its annotation declares an `int`" -> "because `report()` declares an `int` and, with no `return` statement, returns `None`", one subject for both halves of the reason.
- Line 523, "and" joining two claims: "travel by different channels, and the listing shows both at once" -> two sentences.
- Line 561, "and" hiding a "but": "`next(g)` and `g.send(None)` do the same thing at runtime, and the `SendType` tells them apart" -> two sentences.
- Lines 740-741, "and" hiding a "but": "runs the opposite direction from the one in `interview()`, and neither signature says so" -> two sentences.
- Lines 744-745, "and" joining different subjects: "`send(Coin(25))` delivers an event and answers no question, and the `COLLECTING` it returns reports ..." -> two sentences.
- Lines 752-753, "and" joining different subjects: "An `if` chain reaches `UNAVAILABLE` and `NEED_MONEY`, and from each one the machine loops back" -> two sentences.

## Considered and declined

- The bold step labels in every exercise (§15/§16 by shape): the Solutions files' convention for a labeled step, not emphasis.
- Long or ragged lines in paragraphs this run left untouched (for example lines 83-89's neighbors, 240, 352, 418-420): hand-wrapping leaves the rendered page unchanged, so only edited paragraphs were rewrapped.
- Lines 87-89, "The return value arrives as `StopIteration`'s `value` rather than as the result of `send()`." A restatement of line 42 by shape, but it completes the four-call walkthrough, and the opening paragraph serves a different purpose (the failure the solution guards against).
- Lines 268-269, "`None` is wrong twice over. The interview stopped ..., and `None` is not a `Result` in any case." The "and" joins the two items "twice over" announces, so it is additive.
- Lines 277-278, "Keeping the two meanings apart is a one-line discipline: put inside the `try` only the call ...": the colon delivers the discipline it names ("namely" fits), and "only the X" is a ruled-fine shape.
- Line 424, "The type checker told you more.": past tense for the reader's own run of the two tools, an event on the page.
- Lines 531, "The count `12` therefore reaches `summarize()` through two returns.": a summary of the chain above it, kept because it sets up the contrast with `'(12 characters)'` in the next sentence.
- Lines 536-537, "The choice decides which code receives the number: a yielded value goes to the driver, and a returned value goes to the delegating generator.": two clauses after a colon, but they are the parallel pair the lead-in announces, so the colon delivers one thing.
- Line 583, "The mismatch is real rather than a type checker limitation.": §34, with the contrast named in the sentence (recurring keep).
- Lines 590-591, "So the first call is special in both directions, and `None` is the only value it accepts.": both clauses hang on the one "So"; "the only X" is a ruled-fine shape.
- Lines 602-603, "The one call that cannot carry a value comes from the one function that cannot pass one.": an aphorism by shape (§32), but it states the fit between the priming call and `next()` that the sentence before it leaves implicit, so it carries content rather than a kicker.
- Line 748, "For another state, take the table.": a short answer to the exercise's question, followed by the reasons. A beat, not a staccato run.
