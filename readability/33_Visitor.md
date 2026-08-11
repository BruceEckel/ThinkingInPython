When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the readability pass over `Chapters/33_Visitor.md`.
The chapter is clean: it carries a recent deep review and annealing,
sentence lengths vary, and no Tier 1A vocabulary, curly quotes,
spaced `--`, or structural tells appear.
The three decisions `readability_db.md` binds for this chapter
(the `## The Price of the Empty Base` heading covering two paragraphs,
"The output above shows results, not mechanism",
and the "already" in "a framework you do not own already calls that method")
were checked and not re-raised,
as were the five items `deep_review/~33_Visitor.md` considered and declined.
One settled-rule fix was applied directly; there are no live blocks.

## Applied directly

- Dispatch-table paragraph (stranded preposition, global rule):
  "reports which implementation `cls` resolves to"
  is now "reports the implementation to which `cls` resolves".
  Fronting the preposition keeps the "resolves" vocabulary
  the next sentence echoes ("it resolves to the same implementation");
  the alternative verb swap ("reports which implementation handles `cls`")
  would have broken that echo.

## Considered and declined

- **"How do you get around this?"** (opening section) is §43 by shape,
  a rhetorical question used as a transition.
  Kept: the whole preceding paragraph is the setup it closes,
  the question is the pattern's problem statement rather than a stall,
  and the next paragraph answers it directly.
- **"The cases worth covering are the registered types, ..."**
  (testing paragraph) matches the §53 "worth" family.
  Kept under the rule's own carve-outs:
  it instructs the reader which tests to write
  and names the cases in the same sentence,
  so it uses the information rather than rating it.
- **"When two types must genuinely resolve together"**
  (One Dispatch Is Enough) has a watch-family intensifier.
  Kept: "genuinely" carries the contrast the paragraph above establishes,
  that *Visitor*'s second dispatch only appears to involve two unknown types,
  so deleting it would erase the distinction the sentence exists to draw.
- **"when the elements must drive the traversal themselves"**
  ("*Visitor* still has a place").
  "Themselves" is load-bearing:
  it contrasts element-driven traversal with a caller driving it,
  which is the case being carved out.
- **"is what" twice**
  ("the empty `Visitor` base is what the classic pattern looks like",
  "That is what *Visitor* does").
  Both are the global rule's keep case:
  the words after "is what" are clauses that cannot attach without it,
  so deleting it breaks the sentence rather than tightening it.
- **"plain function" twice** (`singledispatch` intro, testing paragraph).
  Both draw a real contrast,
  against the dispatching function the decorator builds
  and against a method on the hierarchy.
- **"The second dispatch ... is not there because two types are unknown;
  it is there because the operation has nowhere else to live."**
  §9 negative parallelism by shape.
  Kept: a genuine corrective contrast with both halves specific,
  and it is the sentence the section's argument rests on.
