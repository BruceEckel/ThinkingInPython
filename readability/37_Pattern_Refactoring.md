When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Readability pass over `Chapters/37_Pattern_Refactoring.md`,
run after the deep review on this branch.
The chapter is clean: no curly quotes, no spaced `--`,
no Tier 1A vocabulary, no pattern clusters.
Sentence and paragraph rhythm vary naturally,
and the deep review's declined items
(the `rtti` file name, "You can use a dictionary keyed by type",
"in the *GoF* sense", the `bins: Bins = {}` idiom) were not re-raised.
Every finding was either applied directly or declined,
so this file has no live blocks.

## Applied directly

- Line 13, watch list (`happen`) plus vague antecedent:
  "This chapter points that out as it happens" is now
  "This chapter points out each one as the example reaches it".
  The "it" in "as it happens" had no single referent;
  the new sentence names what gets pointed out and when.
- Line 336, stranded preposition:
  "no trace in any total the plant will act on" is now
  "no trace in any total on which the plant will act".
- Line 405, §53 ("worth knowing" rates the fact instead of using it):
  "but worth knowing before you subclass a material" is now
  "but keep it in mind before you subclass a material",
  turning the rating frame into the instruction it implied.
  Close alternative: leave it under the §53 instruction carve-out,
  since the "before you subclass" condition already says when it matters;
  the imperative says the same thing without the frame, so it won.
- Line 432, stranded preposition:
  "the shape the book's version settles on" is now
  "the shape on which the book's version settles".

## Considered and declined

- "That is the argument. Here is the requirement that makes it concrete."
  §28 by shape (an announcement before the content),
  but the pair does real structural work:
  it closes the abstract case against `match` and pivots to the demo,
  and the two short sentences break up a long paragraph's rhythm.
- "Here \"no special handling\" is a genuine answer" is §34 by shape
  (a real/genuine intensifier on an abstract noun),
  but the contrast the carve-out asks for is named in the same sentence pair:
  the case "when no default makes sense" follows immediately,
  and "genuine" is the word drawing that line.
- "The deeper skill is spotting the *vector of change*" brushes §27
  ("the deeper issue"), but the comparative is real:
  deeper than knowing the patterns, which the sentence before establishes.
- "a pattern is worth keeping only when it is still useful once the language
  does part of the work" is the §53 carve-out, not the tell:
  keeping is weighed against a stated condition.
- "even writing that down takes work": "even" is on the avoid list
  but carries the emphasis (transcribing Visitor is work
  before you use it for anything).
- "`type(t)` is the perfect key because it adapts to new types":
  a promotional-shaped adjective, but the reason is attached
  and the claim is technical, not praise.
