> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/41_Functional_Toolkits.md`

Second review of this chapter.
All seven findings in `readability/~41_Functional_Toolkits.md` were accepted and
applied, and none were rejected, so nothing is carried forward.

The deep review that ran just before this one changed the chapter substantially:
Recursion and Lazy Evaluation swapped places, a `### Composing the Pieces`
subsection closes the `itertools` catalog, the case study gained a named
`met()` helper and a paragraph on why caching it would be wrong, and the chapter
gained both a `## Choosing From the Toolkits` conclusion and its first
`## Exercises` set. Every finding below is in that new prose.

One problem was corrected during the apply rather than recorded here, because it
breaks a stated rule rather than a judgment call: the new `singledispatch`
sentence ended "a keyword-only argument cannot be dispatched on at all," a
stranded preposition, and now reads "cannot drive the dispatch at all" with the
sentence's subject changed from a passive to `singledispatch()`.

---

**"Composing the Pieces", opening: the section narrates its own earlier claim,
and repeats the word it is explaining.**

> Each entry above is one stage.
> This section opened by saying they combine,
> and combining them is where the catalog pays off:

"This section opened by saying they combine" is §41, restating what the reader
was told rather than telling them something. It also puts "combine" and
"combining" in adjacent clauses, so the sentence explains the word with the
word.

Proposed change:

> Each entry above is one stage.
> Stacked, they are a pipeline:

Alternative, if you want to keep the callback to the section intro, which does
promise composition and then never demonstrates it:

> Each entry above is one stage.
> The section intro promised they compose; this is what that looks like:

I recommend the first. The intro's promise is worth redeeming, but redeeming it
is what the listing does, and saying so first is the metadiscourse the finding is
about.

[] Reject

---

**"Composing the Pieces": "the one that teaches" labels the payoff instead of
delivering it.**

> The second `print()` is the one that teaches.
> The source resumes at 16 rather than 13,
> because `takewhile()` had to pull the batch `(169, 196, 225)` and discard it
> to discover that its total of 590 exceeded the limit.

The label is §39. The sentence after it is the actual lesson and is concrete
enough to stand alone; announcing that it is about to be interesting is the
move that adds nothing. The book does this well elsewhere in the same chapter
("The single hit is the second `square(2)`"), which states the fact and lets it
land.

Proposed change: cut the labelling sentence and let the explanation open the
paragraph.

> Four stages sit on top of an infinite source,
> and none of them run until `list()` pulls.
> The second `print()` shows the source resuming at 16 rather than 13,
> because `takewhile()` had to pull the batch `(169, 196, 225)` and discard it
> to discover that its total of 590 exceeded the limit.

This keeps the pointer to which `print()` is meant, which the reader does need,
and drops only the claim about its importance.

[] Reject

---

**"Composing the Pieces", closing line: "one item further than it keeps" counts
in a different unit than the sentence before it.**

> A pull-based pipeline reads one item further than it keeps.

The claim is true at the level of the `totals` stream: `takewhile()` pulled one
total (590) past the four it kept. The sentence directly above it, though, has
just finished counting in batches and squares, where the overshoot is three
items, not one. A reader who carries the previous sentence's unit into this one
gets the wrong number.

Proposed change:

> A pull-based pipeline reads one value further than it keeps,
> and that one value cost three squares.

Naming both units connects the general rule to the specific number the reader
just saw, which is the reason the line is there.

Alternative: cut the line. The paragraph already makes the point concretely, and
the generalization is the kind of closing aphorism the prose pass watches for.
I recommend the change over the cut, because the general rule is what transfers
to the reader's own pipelines.

[] Reject

---

**`repeat`: "an argument that never changes without materializing anything"
reads two ways.**

> it supplies an argument that never changes without materializing anything,
> and here it stops when `range(5)` does,

Without a comma the reader can attach "without materializing anything" to
"changes" rather than to "supplies," which briefly says the argument changes
only when something is materialized. The intended reading is that `repeat()`
supplies the argument without materializing anything.

Proposed change:

> it supplies an argument that never changes, without building a list to hold it,
> and here it stops when `range(5)` does,

The comma fixes the attachment, and "building a list to hold it" is more
concrete than "materializing anything" for a reader who has not met that word
in this sense.

[] Reject

---

**Case study: "this is the shape the mistake takes in practice" is a gloss on a
point the paragraph has already made concretely.**

> The `cache` entry's rule that caching only works for pure functions is not a
> formality;
> this is the shape the mistake takes in practice.
> A function that reads mutable state is not pure, however simple its body looks.

Three sentences close this paragraph and all three assert the same thing at
different altitudes: the rule is not a formality, this is what the mistake looks
like, a function reading mutable state is not pure. The concrete work was
already done two sentences earlier ("a cached answer from round 0 would still be
reported in round 6"). This is the treadmill pattern: motion without distance.

Proposed change: cut the middle sentence.

> The `cache` entry's rule that caching only works for pure functions is not a
> formality.
> A function that reads mutable state is not pure, however simple its body looks.

The last sentence is the one worth keeping, because "however simple its body
looks" is the part a reader can carry to their own code.

[] Reject

---

## Checked and clean

- Zero hits across the §7 Tier 1A, 1B, 2, and 3 vocabulary tables in the new
  prose.
- `banned_phrases.py` and `prose_lint.py` both pass on the chapter.
- No em dashes, no spaced ` -- `, no curly quotes, no boldface, no emojis, no
  slot-fill placeholders.
- "The infinite form is the one that earns the import" echoes the chapter's own
  "`reduce()` earns its keep for every other fold," so it reads as the book's
  voice rather than a new metaphor. Not flagged.
- "Choosing From the Toolkits" opens "The rule for both modules is the same,"
  then "The second rule is that the pieces are meant to be stacked." Numbered
  rules in a conclusion are §54 by shape, but there are two of them and both
  are load-carrying, so the count is not inflation. Not flagged.
- The new exercises are imperatives addressed to the reader, which the global
  rules exempt from the imperative-plus-consequence ban.
- The `met()` helper's name was checked against the surrounding code for
  soft-keyword collisions and shadowing; it collides with nothing.
