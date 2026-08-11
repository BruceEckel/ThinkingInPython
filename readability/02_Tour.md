When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

First readability pass over `Chapters/02_Tour.md`.
The chapter is clean:
no curly quotes, no spaced `--`, no Tier 1A vocabulary,
no signposting, no chatbot artifacts,
and sentence and paragraph lengths vary the way human prose does.
The deep review's declined items
(the opening trio, "may replace all your batch files",
"arbitrary rules or force a particular set of features")
were honored and not re-raised.
Three small fixes were applied directly; there are no live blocks.

## Applied directly

- Line 36, redundant significance appositive (§1 by shape):
  cut ", a major factor in code readability" from
  "Indentation determines how statements group into blocks".
  The two sentences before it say the code is clean and easy to read,
  and the paragraph ending "one of the main reasons for
  Python's consistent readability" makes the same claim
  with a mechanism attached,
  so this was the third readability claim in four lines.
- Line 143, watch-list "never":
  "so they never overflow" → "so they cannot overflow".
  Unlimited precision makes overflow impossible,
  so the modal is also the more precise claim.
- Line 457, watch-list "never":
  "the leading `''` in `message.strings` never reaches the loop"
  → "does not reach the loop".
  The deletion test passes; nothing temporal is lost.

## Considered and declined

- Line 147, "with two worth noting:": §53's "worth" family by shape,
  but the colon delivers both facts immediately after the frame,
  so it signposts rather than rating information in place of using it.
  §53's carve-outs keep "worth" when the reader is told what to do with it,
  and here the two operators follow in the same sentence.
- Line 68, "`val` would never have been assigned": watch-list "never",
  but the temporal emphasis supports "Binding still follows execution"
  in the same sentence, and the wording is fresh from the applied,
  reviewed deep review.
- Line 478, "when it serves primarily as a callable": "serves as" is a
  Tier 1B copula-avoidance hit, but the bare copula misfires here:
  every Python class "is a callable", while "serves primarily as"
  states the usage role the sentence is about.
- The Naming Conventions paragraph states the snake_case-class criterion
  in three sentences ("serves primarily as a callable",
  "Reserve it for classes that behave like a function",
  "The default ... is still `CapWords`").
  Not treadmill: the first grants permission with the criterion,
  the second restricts the permission to that case,
  and the third restores the default, three distinct instructions.
- Line 60, "The next line ... The subsequent statement": §11-adjacent
  variation, but the referents differ (a line inside the block,
  then the statement after it), and the deep review edited this
  sentence the same week without changing "subsequent".
- Line 294, "It has a sharp edge.": a single short emphatic beat,
  which the false-positive guidance allows; the two sentences after it
  supply the specifics.
- Line 75, "not a matter of taste: it is the structure": the colon
  introduces a definition-like contrast, the same pattern
  `readability_db.md` confirms clean for 40_Functional_Foundations.
- Line 381, "It is readable and fast:": two-word praise, but both words
  are the concrete case for f-strings and the listing follows at once.
