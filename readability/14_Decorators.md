When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Readability pass over `Chapters/14_Decorators.md`, following the deep review
(`deep_review/~14_Decorators.md`); its declined items were carried forward and
none re-flagged. `readability_db.md` has no chapter-14 entries. The chapter is
clean at the structural level: sentence lengths vary, no signposting, no
boldface or list inflation, no curly quotes or spaced `--`, and the watch-list
words that do appear ("only", "already", "never", "even") almost all draw real
contrasts. Three small findings cleared the direct-application bar; nothing
needed a decision from you, so there are no live blocks.

## Applied directly

- Line 250, §53 ("worth" frame rating information): "The return type is worth
  breaking down:" is now "Take the return type apart:", an instruction in the
  same register as the later "Compare the two cases."
- Line 669, watch-list "even": "even gets the checker involved" is now "gets
  the checker involved"; the payoff the "even" gestured at is stated two lines
  later ("catching the same problem before the program runs").
- Line 847, watch-list "happen": "The same collapse happens to classes." is now
  "Classes collapse the same way."

## Considered and declined

- "`report` only asks for a callable and never asks where `func` came from"
  ("What `@` Does Not Require"): two watch-list words in one sentence, but the
  repeated "asks" is a deliberate parallel and the sentence states the
  section's claim; rewriting flattens the rhythm without gaining precision.
- The chapter's many "X, not Y" contrast tails ("not at the decoration that
  caused it", "not one recursive one", "an object, not a type", "share a
  topic, not a type"): §9-adjacent by density, but each names a real,
  informative contrast, and none is the "not just... but" or clipped
  tailing-negation form the pattern targets. Book voice; left alone.
- "The class form separates the two phases cleanly" ("Decorators as Classes"):
  "cleanly" looks like an empty adverb, but it draws the contrast with the
  function form's nested closures that "Function Form or Class Form?" later
  makes explicit ("separate methods instead of nested closures").
- "Sometimes you want the choice made later" ("The Decorator Pattern"):
  "want" is addressed to the reader, which the global rule's carve-out covers;
  same call as the 31_State_Machines "a bug you want flagged" precedent in
  `readability_db.md`.
- "though every actual function does" and "really calls
  `logged.__call__(logged_instance, 5)`": §34 real/actual inflation by shape,
  but both carry named contrasts (the `Callable` type versus actual functions;
  what the call looks like versus what runs), which the pattern's carve-out
  keeps.
- "return a descriptor instead of a plain wrapper" ("Decorators You Already
  Know"): "plain" earns its contrast against the descriptor.
- "`@` constrains the statement below it and nothing else": settled in the deep
  review's declined list; carried forward, not re-raised.
