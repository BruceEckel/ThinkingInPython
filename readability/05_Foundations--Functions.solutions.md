> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over `Solutions/05_Foundations--Functions/README.md`, 2026-10-16.
Line numbers in "Applied directly" refer to the file before the edits; the declined list uses the edited file.
The file carries almost no AI-writing tells:
no Tier 1A or Tier 2 vocabulary, no signposting, no manufactured punchlines,
and its only watch-list hits are the compound "positional-only" and a sentence-initial "Only".
Five small edits were applied directly,
and nothing needed Bruce's judgment,
so this file holds no live block and serves as the applied-directly record.
The generated block quotes, the `<details>` ladders, the shape blocks, and the listings were left alone.

## Applied directly

- Lines 63-64 (exercise 1), "and" joining clauses with different subjects where "but" fits:
  "The function appends to `target`, and a tuple has no `append()`. The first call ... therefore raises" ->
  "The function appends to `target`. A tuple has no `append()`, so the first call ... raises".
- Lines 255-256 (exercise 4), treadmill (§70) and a claim checked against the listing:
  cut "Callers must write `total=True`.", which restates the paragraph above the listing,
  and "Every positional argument goes to `values`" -> "Every positional argument after the first goes to `values`",
  since `label` takes `"nums"` in the listing.
- Lines 418-422 (exercise 7), "and" with a subject change plus a doubled "therefore":
  "is therefore a leftover, and `**facts` collects leftover keywords. `facts` receives ... The message is therefore ..., which names" ->
  "is therefore a leftover. `**facts` collects leftover keywords, so `facts` receives ... The message, ..., names".
- Lines 433-435 (exercise 7), treadmill (§70):
  cut the clause "because `**facts` collects the stray keyword and leaves the parameter `name` empty",
  which repeats the first paragraph of the same solution nearly word for word.
  The close alternative was to keep the clause as a reminder after the intervening paragraph.
- Lines 445-449 (exercise 7), endorsement frame (§53) and an "and" joining two subjects:
  "The `/` and `**facts` are also worth using together. `/` makes `name` positional-only." ->
  "The `/` has two more effects on `describe()`." (the positional-only fact is stated at line 417);
  "`**facts` accepts any name a caller writes, and the `/` adds `name` to those names." ->
  "The `/` also lets `**facts` collect a keyword called `name`, so `describe("Bob", name="Robert")` stores a fact called `name`."

## Considered and declined

- The bold imperative step labels ("**Accumulate in the shared default.**", "**Rebind the local name.**", and the rest).
  Inline bold headers by shape (§16), but they are the book's Solutions convention for a solution's steps,
  run in prose rather than as a bulleted list.
- Line 578, "Only `clear_by_method()` empties the caller's list."
  A sentence-initial "Only", one of the shapes ruled fine on 2026-10-04, and the restriction is the answer to the exercise.
- Line 508, "Both calls raise ..." under the step label "**Drop the `global` declaration.**", which names only the first case.
  The sentence answers both halves of the exercise at once before the two steps explain each; moving it would split the answer.
- Line 591, "Here both functions attempt the same operation, emptying a list."
  Reads as a flat closer, but it names the difference from the chapter's `rebind()` and `append_all()` pair, which do different operations.
- Line 435, "`describe(name="Bob")` succeeds and `facts` stays empty."
  Two subjects joined by "and", but the clauses describe one outcome of one call, so the "and" is additive.
- Line 136, a hand-wrapped line that runs past 70 columns. Left as is; rewrapping is churn outside this pass's subject.
