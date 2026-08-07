[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: Chapters/16_Comprehensions.md

This chapter reads as human-written technical prose and is close to clean.
A mechanical scan of the Tier 1A/1B/2/3 vocabulary tables returned zero hits
(the only matches were the literal Python terms `unpack`/`unpacking` and
`key: value`), there is no boldface, no curly quotes, no non-ASCII characters,
no ` -- `, and no banned phrases.
No P0 or P1 findings.
What remains is three small P2 wordiness/clarity edits.

***

[] Reject

**Section:** List Comprehensions (paragraph beginning "The `# type: ignore` comments...")
**Pattern:** §50 Novelty Inflation, invented-label variant (P2)

Current:
> The `# type: ignore` comments mark a cost the reading test does not show.

Proposed:
> The `# type: ignore` comments mark a cost that readability alone does not show.

Why: "the reading test" names a test the chapter never sets up, so the reader
has to reconstruct it from the "harder to read" sentence two paragraphs earlier.
Naming the thing directly removes the coined label.

***

[] Reject

**Section:** List Comprehensions (paragraph beginning "List brackets (`[]`)...")
**Pattern:** §23 Filler Phrases, make verbs do the work (P2)

Current:
> List brackets (`[]`) enclose the list comprehension,
> so it is immediately evident that it produces a list.

Proposed:
> List brackets (`[]`) enclose the list comprehension,
> so you can see at a glance that it produces a list.

Why: "it is immediately evident that" is an expletive construction with no verb
doing work, and the second person matches the register of the surrounding prose
("You can achieve the same results...", "Nothing stops you from...").

***

[] Reject

**Section:** List Comprehensions (final paragraph, on the walrus operator)
**Pattern:** §23 Filler Phrases, make verbs do the work (P2)

Current:
> That is deliberate, and it is the reason a comprehension can accumulate a value without a separate loop.

Proposed:
> That is deliberate, and it lets a comprehension accumulate a value without a separate loop.

Why: "it is the reason X can" spends four words on a copula where one verb does
the same job. Borderline, since nothing about the original is unclear.
