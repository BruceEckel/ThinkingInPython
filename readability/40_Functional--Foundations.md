> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Foundations

Readability pass over `Chapters/40_Functional--Foundations.md`, 2026-10-16.
The chapter carried few AI-writing tells.
What it had were three restatements of a claim the paragraph had already made,
two uses of the "X does real work" formula,
and four "and" joins between clauses with different subjects.
Every finding had one sensible answer, so this file holds no live block:
it is the record of what was applied directly and what was considered and kept.
The `readability_db.md` keeps for this chapter (the two-colon `match`/table parallel
and the "Choose `match`" sentence) were respected.

## Applied directly

- 115, split an "and" joining different subjects:
  "the fixture the impure version needs, and purity removes it" -> two sentences.
- 181, repetition: the second "For a large value that changes often" (four lines after
  "For a large structure that changes often") -> "For such a value".
- 208, §70 restatement: cut "Each annotation is a constraint the type checker enforces.",
  which repeats the section's opening sentence; the concrete sentence after it now leads.
- 234-235, §70 restatement and "and" split: cut "A mutable value offers neither."
  (the paragraph opens with "two things a mutable value cannot");
  "You can hand the value to any code, and the value stays as you built it" -> two sentences.
- 309-310, restatement: "lets a data lookup select which function runs. A dictionary of
  functions replaces a long chain, because you select the behavior by looking it up"
  -> one sentence, "...which function runs, so a dictionary of functions can replace a long
  `if`/`elif` chain".
- 406, §34 formula (first of two "does real work"): "The `list()` calls do real work."
  -> "The `list()` calls are necessary."
- 582, §34 formula (second "does real work"): "The keyword does real work here.
  `partial(power, 2)` presets `base` instead" -> "Without the keyword, `partial(power, 2)`
  presets `base`".
- 680-681, "and" split: "Each piece stays small and pure, and composition combines them
  as they are" -> two sentences, "Composition combines the pieces as they are."
- 690-691, "and" split: "you insert or swap a single stage and the others stay as they
  were" -> two sentences, "The other stages stay as they were."

## Considered and declined

- 6, §28 signposting: "This chapter begins the book's exploration of functional
  programming." The part opener orients a reader arriving from Part III,
  and the paragraph turns to concrete payoffs at once.
- 76, unsupported superlative: "A pure function is the most reliable code you can write."
  The same sentence gives the reason ("because its inputs fully describe its behavior"),
  and the next four sentences each support it.
- 371, §32 aphorism shape: "A lambda's value is locality." A short beat among long
  sentences, defined by the two sentences after it.
- 426-430, restatement: "`map()` and `filter()` are a better choice when the function
  already exists" and the "As a rule of thumb" sentence state the same half of the rule.
  Kept: the rule-of-thumb sentence is the two-sided summary a reader returns for,
  the same call `readability_db.md` makes for the "Choose `match`" sentence.
  Both "already" uses mean "is predefined", not emphasis.
- 529, "exactly one function": a precise count, the case the watch-list carve-out names.
- 584 and 634, "already": temporal (an argument supplied ahead of the call) and
  work the reader does not have to do (`partial()` appends the call's arguments);
  both fall under the recurring "already" keep.
- 747, §25 generic closer: "The chapters ahead build on that single property."
  It names the property (dependence on arguments alone) from the chapter's opening
  paragraph, so it ties the chapter together rather than praising it.
- 14 and 86, "And" sentence openers: voice, one each, not a transition-phrase cluster.
