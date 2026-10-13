> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: A_Effect_Tracking (2026-10-13)

Nothing here needs your decision, so the file has no live blocks.
I read the appendix against the previous review (`~A_Effect_Tracking.md`), `deep_review_db.md`, the sections it links in chapters 44, 46, and 47, Appendix B's closing section, and the installed Stateless source (`effect.py`, `need.py`, `handler.py`).
`tip verify-ch CH=A ISOLATED=1` passes 21 of 21 before and after the edits, and `tip prose CH=A` reports no warnings afterward (one passive before).
The installed checker is `ty` 0.0.86.

## Applied directly

- "The Tracking Problem": the `row(g)` sentence linked "Effect Management" to "Native Effect Management", which the next paragraph links again two lines later. It now links "Effect Management for Python?", the section that calls propagation the hard part, and says so, which ties it to the appendix's opening.
- "A Row Inside `Annotated`", metadata paragraph: the sentence about classes ("reads each one as a value, even when it is a class") came before the sentence that explains why (each piece is an ordinary expression). The two are now in that order, and the `even` is gone.
- Same paragraph: "requires one piece of metadata and accepts any number after it" is now "requires at least one piece of metadata."
- Same section, the PEP-rule paragraph: "and the runtime can read it back" joined two facts with a vague actor. Now two sentences, "At runtime, your code reads it back with `get_type_hints()`", and the next sentence opens "Those two facts" instead of "That".
- After `effect_rows.py`: "act only on the objects it recognizes" is now "act on the objects it recognizes and pass over the rest" (positive form).
- The `Ask is a label` paragraph stood alone with no stated purpose. It now ends with a pointer to "Tracking Is Not Management", which explains why a row alone cannot manage the Effect.
- "Resolve Every Call": "where `tell()` is defined" (passive) is now "which defines `tell()`."
- "Find a Place to Run": the sentence about the `handling` term held its subject open across a long clause. Now two sentences: the handling function leaves `Ask` out of its row, and inside its `handling(Ask, Scripted())` block the term puts `Ask` back in the set, so the `greet()` call passes.

## Verified and left as written

- On `ty` 0.0.86: `reveal_type(ask)` reports `def ask(prompt: str) -> str`; `reveal_type(twice(hello))` reports `Generator[Need[Console], Any, None]`; `supply(Console())` reveals `Handler[Need[Console]]` and applying it to `hello` reveals `() -> Generator[Never, Any, None]`; a `yield from twice(hello)` in a function declared `Depend[Never, None]` draws `invalid-yield` ("expression of type `Need[Console]`, expected `Never`").
- Stateless's `Depend` is `Generator[A, Any, R]` (`effect.py`), so "its row `A` is that generator's yield type" holds.
- `ty` still has no plugin interface; I found no announcement of one. "At this writing" stays accurate.
- "Five signatures" and "a helper four calls below `main()`" match chapter 44's `bookkeeping_scales.py` and its count. `Scripted` answers every prompt with "Alice". Chapter 44's "Effect Management for Python?" says gradual typing took a decade, and "Tracking and Management" lists interface separation and delayed binding second and third.
- Appendix B's closing section has the second list ("The checker reports nothing about them") the "Find a Place to Run" sentence describes.

## Considered and declined

- **"Now the design has two halves, a static tool and a runtime library"** in "Subtract What a Handler Discharges" reuses "halves" from "The Tracking Problem" (row half, handler half). The two splits line up (the static tool is the row half, the runtime library the handler half), so the shared word reads as a parallel, not a collision.
- **The `Ask is a label` paragraph's position.** Moving it up beside the paragraph about eager bodies would group "what the listing does" ahead of "the weakness". Adding the forward pointer gave the paragraph its purpose where it stands, and the move would split the two `shout()` paragraphs from the listing they discuss.

## For the session

- `tip watch-words` now reports 2 stale baseline entries for this appendix: the `even` and the `only` the edits above removed. The baseline is outside my scope.
- The edited sentence in "The Tracking Problem" links chapter 44 with a new claim ("calls the hard part"). Chapter 44, "Effect Management for Python?", says "The hard part is propagation, not syntax." `tip grounding-triage` was not run.
