When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

First readability pass over `Chapters/21_The_Pattern_Concept.md`, run after
the deep review in `deep_review/~21_The_Pattern_Concept.md` was applied.
That review's declined list and `readability_db.md` were read first and bind
this pass; nothing they settled is re-raised here.
The chapter is clean: zero AI-vocabulary hits in any tier, no curly quotes,
no spaced `--`, no filler-phrase or hedging clusters,
and the sentence rhythm varies from clipped
("You have evidence.") to long definitional lines.
The prose is first-edition voice throughout, and every watch-word hit
either draws a real restriction or was examined and kept below.
No finding needed a direct edit or a live block.

## Considered and declined

- "An important step forward in object-oriented design was the 'design
  patterns' movement" (chapter opener): significance framing by shape
  (§1), but it is the chapter's historical claim, hedged to "important"
  rather than inflated, and first-edition voice, the same call as the
  kept 27_Factory opener in `readability_db.md`.
- "One of the most compelling motivations behind this is to *separate
  things that change from things that stay the same*": "compelling" is
  Tier 3 vocabulary, which flags at high density; this is the chapter's
  single occurrence, in a first-edition sentence whose italicized
  payload is the book's recurring refrain.
- "Certainly, the *Creational* patterns are fairly straightforward"
  (taxonomy critique): §42 flags "Certainly" by density, and this is
  the one use. It is concessive, granting the easy category before the
  turn "But I find *Structural* and *Behavioral* to be far less useful
  distinctions", inside a first-person passage no model wrote.
- "How will you create objects? This is a normal question, and the name
  brings you right to that group of patterns.": a self-answered question
  pair by shape (§43), but the question is the content, demonstrating
  what the category name evokes, not a stalling transition.
- "That remainder is worth learning, and it is usually the intent rather
  than the structure" (Reading the Chapters Ahead): §53's "worth"
  family, but the carve-out for a real comparison applies. The remainder
  is being weighed against Python's subtracted share, stated in the two
  question-answer pairs before it, and the clause after it says what
  the remainder is.
- The three question-then-answer pairs in Reading the Chapters Ahead
  ("What varies and what stays the same? That names...") are the
  section's announced structure, three questions each chapter will ask,
  not rhetorical stalling; the parallelism is what makes them a
  reusable checklist.
- "Simply declaring that a design should have 'low coupling' is usually
  too vague" (*Managed Coupling*): "simply" here means "merely" and
  draws the bullet's contrast, declaring low coupling versus
  acknowledging and controlling coupling; the deletion test fails.
- "so that adding a type never edits the factory" (Pattern Evolution):
  "never" states the guarantee the registry provides; "does not edit"
  weakens the claim the stage-three design exists to make.
- "a dizzying array of options that are often unused, misused or not
  useful" (*Simplicity before generality*): the bullet paraphrases
  Kevlin Henney's principle, credited in its footnote, so its wording
  stays as attributed content.
- "Coupling happens", "a Python module already is one", and "A method
  should talk only to itself" were all examined and kept by the deep
  review's declined list; not re-examined.
