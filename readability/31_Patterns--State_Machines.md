> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: 31_Patterns--State_Machines (2026-10-15)

A full audit of the chapter's prose against the readability patterns, after the third deep review (3cc75070) and the `Column` enum change (641df199).
`readability_db.md` was read first; its chapter 31 keeps ("plain methods", "stored directly") stand, and nothing here re-raises them.
The chapter is technical register: sentence lengths vary (three-word beats beside thirty-word walkthroughs), no Tier 1A or Tier 2 vocabulary appears, no curly quotes, no spaced `--`, no signposting openers, no boldface, no generic closer.
The exercises and the "Which Design Should You Use?" heading keep their forms.
Two sentences fired a rule with one answer and were fixed in place; nothing needs your decision, so the file has no live blocks.
`tip verify-ch CH=31` passes 27 of 27.

## Applied directly

- "The Engine": "a type error rather than a silent dead end" stood a figure in for the alternative it was contrasting with. Now "a type error, where a misspelled string would be a key the machine never reaches", naming the string-keyed table the sentence has in mind.
- "Testing the Vending Machine": "The cases worth testing are:" rated the list instead of introducing it (the "worth" frame, §53). Now "The tests cover:".

## Considered and declined

- "Nothing here needs a `switch`, reflection, or a `Condition`/`Transition` class hierarchy" is a rule-of-three shape (§10) whose three items the next sentence uses; the second deep review kept it, and it stays.
- "Two consequences follow from the mixin" and "Two facts make that choice safe here" announce a count before delivering it (§54 shape). Each count is exact and the items follow at once, so they are structure, not padding.
- "That is the Moore shape" and "That is the Mealy shape" close parallel paragraphs with the same frame. The parallel is the point of the decision section, so the repetition stays.
- "We look at two designs" and "We use an enumeration" are the author's "we".
- "The deciding question is which you would rather read" has the surface of a §27 authority trope, but the sentence states the decision rule the whole section builds to, so it stays.
