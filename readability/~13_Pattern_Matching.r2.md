[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review 2: `Chapters/13_Pattern_Matching.md`

Run after the deep-review edits landed, so the new prose gets the same scan the
rest of the chapter got in review 1.
Nothing from review 1 was rejected, so nothing is carried forward.

The chapter still reads as human technical prose.
No AI vocabulary hits, no significance inflation, no signposting, no boldface
padding, no curly quotes, no spaced ` -- `.
Five findings, three of them in prose written during the deep review.

***

[] Reject

**Section:** chapter introduction (new prose, before the teaser listing)
**Pattern:** §35 gratuitous universal quantifier, and an accuracy problem (P1)

Current:
> No `switch` in any language does this:

Proposed:
> No C-style `switch` can express this:

Why: the claim is too wide, and the chapter contradicts it later.
"Exhaustive Matching" says "A `switch` in C, JavaScript, or traditional Java
cannot do this," and then credits Scala, Kotlin, and Java's switch expressions
with the check.
C# switch patterns and Rust's `match` also destructure.
Scoping the claim to the C-style `switch` keeps the contrast the sentence is
making and matches the chapter's own later wording.

***

[] Reject

**Section:** Sequence Patterns (new paragraph on bare-comma patterns)
**Pattern:** §23 clarity, stacked nouns (P2)

Current:
> Transforming the subject this way turns a set of comparisons into literal patterns,
> which is often clearer than the guards the untransformed subject would need.

Proposed:
> Transforming the subject this way turns a set of comparisons into literal patterns,
> which usually reads better than the guards you would write otherwise.

Why: "the guards the untransformed subject would need" stacks three nouns and a
negated adjective, so the clause needs a second reading.
Naming the reader as the one writing the guards says the same thing directly.

***

[] Reject

**Section:** Class Patterns (before `type_patterns.py`)
**Pattern:** §53 social endorsement closers, the "worth knowing" family (P1)

Current:
> The type test is `isinstance()`, which has consequences worth knowing:

Proposed:
> The type test is `isinstance()`, which has two consequences:

Why: "worth knowing" rates the information instead of using it, and the listing
plus the two paragraphs after it are the consequences.
Counting them also tells the reader what to look for: subclass order deciding
the winner, and the special-cased builtins.

***

[] Reject

**Section:** Guards (paragraph after `guards.py`)
**Pattern:** global rule, cut "is what" when deleting it changes nothing (P2)

Current:
> The guard runs only after the pattern matches,
> which is what lets it use the names the pattern bound.

Proposed:
> The guard runs only after the pattern matches,
> which lets it use the names the pattern bound.

Why: a verb follows the cleft ("is what lets"), which is the giveaway that it
only delays the verb. The sentence means the same without it.

***

[] Reject

**Section:** Exhaustive Matching (new prose after `exhaustive.py`)
**Pattern:** §9 negative parallelism (P2)

Current:
> `assert_never()` is not only a marker for the checker.
> If a value that lied about its type reaches it at runtime,
> it raises `AssertionError: Expected code to be unreachable, but got: 'x'`,
> naming the value it received.

Proposed:
> `assert_never()` acts at runtime as well as at check time.
> If a value that lied about its type reaches it,
> it raises `AssertionError: Expected code to be unreachable, but got: 'x'`,
> naming the value it received.

Why: "not only" sets up a contrast the sentence never completes, so the reader
holds it open through the next sentence.
Stating both roles directly also lets the second sentence drop "at runtime,"
which it was repeating.
