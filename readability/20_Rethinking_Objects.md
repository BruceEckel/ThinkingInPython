When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

First readability pass over `Chapters/20_Rethinking_Objects.md`, run after the
deep review in `deep_review/~20_Rethinking_Objects.md` was applied.
That review's declined list and `readability_db.md` were read first and bind
this pass; nothing they settled is re-raised here, including the
"Substitutability is the first thing OOP promised" opener and the
"*Subtype polymorphism* is what..." cleft.
The four "OOP promise" section themes are the settled book-wide deliberate
use of "promise" and were not flagged.
The chapter is clean of AI-vocabulary clusters, curly quotes, and spaced
`--`; sentence rhythm varies from three-word sentences ("The dot fills in
`self`.") to long compound ones, and the four-promises structure gives the
chapter a through-line no paragraph shuffle survives.
No finding needed a live block.

## Applied directly

- Protocols section, watch word "never": "The type's author never needs
  to hear that your protocol exists" is now "The type's author need not
  hear that your protocol exists". "Need not" matches the chapter's own
  register ("It need not live inside `Point`" in Methods or Functions?),
  and the at-no-time force survives. Close alternative was "does not
  need to hear", which reads flatter.

## Considered and declined

- "Notably, not everything in Simula was an object" (Evolution): §42
  lists "Notably" as a calibration cue, but it is the chapter's single
  occurrence, far under the skill's own density bar, and it primes the
  contrast the Smalltalk paragraph then draws ("everything is an
  object").
- "Satisfying three of them costs nothing more than having the three
  methods": "nothing more than" is the comparative the global rule keeps
  where the diminishing is the point, and low cost is this sentence's
  point.
- The remaining "never"s all state guarantees: "never refuses a
  `push()`" (the base contract), "hands out references, never copies"
  (the contrast that explains the leak), "code the checker never saw",
  and "movement code never checks for `None`". Weakening any to
  "does not" trades a guarantee for a report.
- "Only the checker sees it, and only at edit time" (NewType): the
  doubled "only" is the sentence's structure, two restrictions stated in
  parallel, not filler.
- "the caller's copy of the list still holds your actual `Bob`s"
  (Plugging Leaks): §34 real/actual inflation, but the contrast is
  named, copies of the container versus the same elements, which is the
  rule's carve-out.
- "It uses genuinely separate functions per type" (`singledispatch`
  aside): "genuinely" points back at `@overload`, whose multiple
  signatures look separate but share one body, so the intensifier draws
  a real contrast.
- "the payoff for using types is tremendous" and "OOP is useful,
  sometimes. But not everywhere, all the time." (OOP Is Useful,
  Sometimes): first-person-chapter voice; the second echoes the heading
  deliberately.
- "When a program truly needs an object, it tells you": "truly"
  contrasts genuine need with the reflexive habit the chapter argues
  against; deleting it flattens that contrast.
- "The last two lines are the payoff" (composition listing): points at
  concrete listing lines, the book's standard listing narration, not §39
  self-labeling.
