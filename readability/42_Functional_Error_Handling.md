When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the readability pass over `Chapters/42_Functional_Error_Handling.md`,
run after the deep review and annealing of 2026-08.
The chapter is clean of AI-writing tells:
no watched-vocabulary clusters, no significance inflation,
no colon-reveal drama, no metronomic rhythm,
and the sentence lengths vary the way the skill's structure tests ask.
The deep review's applied-directly list had removed most of the
watch-list vocabulary before this pass ran,
so what remained were three stranded prepositions of the kind
that review was fixing elsewhere in the same chapter.
All three were applied directly; no live blocks remain.

## Applied directly

- Line 599, stranded preposition:
  "An exception knows what went wrong but not where it came from."
  is now "An exception knows what went wrong but not where."
  The next sentence ("which setting, which field, which row of the file?")
  supplies what "where" means, so the clause was carrying no information.
  Close alternative: "but not where it originated," declined because the
  raise site is in the traceback; the missing part is the data context.
- Line 636, stranded preposition:
  "can add its own line as the exception passes through"
  is now "can add its own line as the stack unwinds",
  which also echoes the chapter's opening
  ("An exception unwinds the stack").
  Close alternative: "as the exception passes through it,"
  declined because "it" could bind to "line".
- Line 678, stranded preposition:
  "a note says which piece of work it belonged to"
  is now "a note says which piece of work produced it",
  keeping the says/says/says parallelism of the sentence.

## Considered and declined

- **"narrow a `Result` to exactly one of the two" (A Result Type).**
  "Exactly" is on the watch list, but this is the precise logical use
  the global rule carves out: the claim is one and only one class,
  which is what `@final` guarantees and the `__notes__` section
  depends on.
- **"`Err` says a failure happened" (Attaching Context).**
  "Happen" is a consider-rewriting watch word, but the sentence needs
  "a failure" as a noun for the following "what it was" to refer to,
  and "occurred" would be the same word in a suit.
- **"Those are not exceptional. They are routine, and the type should
  say so." (Which Failures Get a Result).**
  Negative-parallelism by shape (§9), but the reversal of the label
  "exceptional" is the section's argument, not a rhetorical tic.
- **"Nothing disappears, because the error is just another return
  value" and "can't see the failure just by reading the return type."**
  Both "just"s pass the deletion test with changed meaning:
  each carries a "merely" contrast the sentence needs.
- **"truly exceptional conditions" (Which Failures Get a Result).**
  "Truly" reads as an intensifier in isolation, but it draws the
  section's contrast against routine failures commonly mislabeled
  exceptional.
- **"the same idea" appearing in consecutive sentences**
  ("the same idea as in Static Typing ... Python's humbler form of the
  same idea"). Repetition, not elegant variation; the echo is cohesive
  rather than accidental, and cutting the second occurrence weakens the
  link between `Result` and `int | None`.
- **"changes only the return type, never what the function accepts"
  (`@safe` section).** "Never" is on the avoid-if-possible list, but
  the sentence states a universal guarantee about the decorator, which
  is the one use the word is for.
