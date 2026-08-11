When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Readability pass over `Chapters/09_Class_Attributes.md`, run after the
deep review and its ty-0.0.70 postscript were applied.
The chapter is clean: no Tier 1A vocabulary, no signposting or filler
frames, varied sentence rhythm, and the deep review's own rewrites
(the `[CV]` tag explanation, the `real_defaults.py` referent fix,
the shadowing punchline) read as settled prose.
One watch-list word survived the deep review and was fixed directly.
No findings need a decision, so there are no live blocks.

## Applied directly

- Line 242 (`What ClassVar Catches`, prose after `counter_near_miss.py`):
  "the write lands on the instance and creates a fresh `total` there"
  is now "the write creates a fresh `total` on the instance".
  "lands" is on the global don't-use list; the deep review fixed the
  same word in the conclusion ("which dictionary did the value land
  in?") but this occurrence stayed.

## Considered and declined

- Line 126, "When you genuinely want one shared value, say so with
  `ClassVar`": "genuinely" is §34-adjacent by shape, but it draws the
  chapter's central contrast, intended sharing against the accidental
  sharing the previous section spent its pages on. Deleting it flattens
  that contrast.
- Line 174, "not annotations that merely describe one to come":
  "merely" is an empty adverb by the strictest deletion test, but the
  sentence's job is diminishment (attributes that exist against
  annotations that describe), and the word supplies the spoken rhythm
  of that put-down, the same reasoning that kept "It is simply a
  callable" in chapter 30 (see `readability_db.md`).
- Line 301, "It only tells the checker that `shared` belongs to the
  class, not that subclasses share storage": "only" is a watch word and
  the trailing "not that..." already restricts, but the "only" carries
  the section's claim (`ClassVar` changes nothing at runtime), and
  cutting it weakens the sentence it anchors.
- Line 21, "This example shows why it can be confusing:": a lead-in
  sentence before a listing, §28-adjacent by shape, but it is the book's
  standard listing introduction and names what the reader should watch
  for, not a "let's dive in" stall.
- Line 252, the three-item list ("A count of every object created, a
  registry mapping names to classes, and a constant that all instances
  read but none change"): §10 rule-of-three by shape, but the prose then
  uses the items individually ("`Tally.total` is the first of these.
  For the third..."), so the enumeration is genuine, not padding.
- The bug-framing paragraph's placement, the property-aside shorthand,
  and the ty version statement were all examined and kept by the deep
  review (`deep_review/~09_Class_Attributes.md`); not re-raised.
