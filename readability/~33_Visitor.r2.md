> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/33_Visitor.md` (r2)

The chapter's older prose still reads clean.
A full sweep of the Tier 1A, Tier 1B, and Tier 2 vocabulary tables (§7) returned
zero hits, the specifics are checkable throughout, and the two `simply` adverbs
the first review flagged are gone.

Everything below sits in prose added or moved by the deep review that ran just
before this pass: the `dispatch_trace.py` lead-in and follow-through, the new
`The Price of the Empty Base` heading, the registry paragraph, and the reworked
`*Visitor* still has a place` sentence.

Every finding was resolved directly: applied (listed below) or declined
with the reason recorded. No blocks remain.

## Applied directly

- Paragraph after `dispatch_trace.py`: "The first hop lands on
  `Predator.visit`" → "The first hop reaches `Predator.visit`" ("lands" is on
  the global "Don't use" list; the same paragraph already uses "reaches" two
  sentences later, so the two hops now read parallel).
- Same paragraph: "The second hop is the one that earns the listing. For
  `Chrysanthemum` it reaches the override, and for `Gladiolus` it reaches
  `Flower.eat`, which is the visible form of the flower-side dispatch
  having nothing to say." → "For `Chrysanthemum` the second hop reaches the
  override, and for `Gladiolus` it reaches `Flower.eat`: the flower-side
  dispatch has nothing to say, and the output now shows it." (§39: the
  label rated the listing, and "the interesting one" would still
  self-label, so the cut was the right form; "the visible form of X" also
  buried its verb).

## Considered and declined

**`## The Price of the Empty Base` covering two paragraphs.**
The heading names only the first paragraph; the "Notice where the behavior
lives" paragraph under it is about a different price (no method
overloading). Considered retitling (`## What the Classic Shape Costs`) or
giving the second paragraph its own heading, and declined both: the second
paragraph ends on the line that motivates the whole `singledispatch`
section, so it sits last no matter what the heading says; a retitle makes
the heading vaguer, and a new heading adds an anchor for two paragraphs.
A slightly wide heading is the smallest cost of the three.

**Lead-in above `dispatch_trace.py` — "The output above shows results, not
mechanism."**
Flagged as §70 metadiscourse, with "names what happened, not which methods
ran" as the candidate. Declined by the block's own criterion: "mechanism" is
established book vocabulary (thirty-plus uses across the chapters, including
"the open-method mechanism that *Visitor* fakes" later in this chapter).

**"or when a framework you do not own already calls that hook."**
"Already" is on the "Avoid if possible" list, but here it earns its place:
the call site exists whether you want it or not. The global rule keeps a
watched word that draws a real contrast. Left alone.
