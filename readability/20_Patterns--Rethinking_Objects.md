> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over chapter 20, 2026-10-16, after the metadiscourse and continuity passes earlier the same day.
The chapter carries few AI-writing tells.
What the pass found was mostly the author's "and" rule: clauses with different subjects whose relation is a contrast or a consequence.
Those seven changes are applied below.
One block asks what the bridge sentence before "Encapsulation Leaks" claims.
No `~` review exists for this chapter, so `readability_db.md` governed the keeps.

## Applied directly

- L43-44, split "and" (different subjects, contrast): "Objects were optional, and C++ brought ..." -> "Objects were optional. C++ brought ...".
- L50-51, split "and" (different subjects, consequence): "... by inheriting implementation, and that reuse works against substitutability" -> two sentences.
- L416-417, split "and" (different subjects, two claims): "A `Protocol` describes that shape, and any type ... satisfies it" -> two sentences.
- L480, empty intensifier: "unless callers really do write to it" -> "unless callers write to it".
- L559, vague subject: "A type holds other types as fields." -> "A composed type holds other types as fields.", which ties the sentence to the composition topic the paragraph opens with.
- L901-902, split "and" (different subjects, consequence): "... by coincidence, and the checker treats them as interchangeable:" -> "... by coincidence. The checker treats them as interchangeable:".
- L933, split "and" (different subjects, each claim stands alone): "The mismatch is in what the number means, and no type checker checks meaning." -> two sentences.

## Substitutability and the four promises (L140-143)

§11/§70 by shape (a bridge sentence that restates and miscounts).
The text reads:

> Substitutability is one thing OOP promised that no tool can check.
> OOP made four promises: encapsulation,
> behavior bundled into the object as methods, reuse through inheritance,
> and polymorphism.

The first sentence calls substitutability something OOP promised.
The second counts four promises and leaves substitutability out of the list,
so a reader cannot tell whether it is a fifth promise or part of one of the four.
The "no tool can check" claim also repeats L86 ("No tool reads the behavior behind the signature") and L134 ("No tool catches the broken contract").
Later, at L985-996, the chapter places the Liskov guarantee under polymorphism,
whichever way membership comes (base class or protocol).

Proposed, which treats substitutability as part of the polymorphism promise:

> Substitutability is the part of polymorphism that no tool can check.
> OOP made four promises: encapsulation,
> behavior bundled into the object as methods, reuse through inheritance,
> and polymorphism.

The alternative keeps it separate: "Substitutability is a guarantee OOP depends on and no tool can check."
The two fixes say different things about what OOP promised, so the choice is yours.

[] Reject

## Considered and declined

- L16, "I want to question": the author's own intent in first person, outside the anthropomorphized-object ban. In the watch-words baseline.
- L38, "Smalltalk was emphatically dynamic.": "emphatically" is an intensifier by shape, but it is a judgment about the language and reads as the author's voice.
- L62, "The industry has been quietly walking back ...": "quietly" carries a claim (no announcement), and the sentence closes the history section in the author's voice.
- L69, "never less": the claim (parameter contravariance), not emphasis. In the baseline.
- L87, "matching that signature perfectly": the adverb sharpens the contrast with breaking the contract.
- L140-148, L369, L484, L613, "OOP promise(s)": the chapter's frame, and a guarantee made and then shown to break, which the "promise" rule keeps. In the baseline.
- L197, "forever:" and L240, "yet again": voice, a deliberate beat on the burden of defensive copying.
- L343, "Frozen guards the binding, not the object.": aphorism shape (§32), but it states the mechanism precisely and the next sentences unpack it.
- L1056, "the most common conditional": an unsupported superlative by shape; first-edition voice, same precedent as 27's "might be the most common design pattern".
- L1092-1093, "Doing nothing is behavior, and behavior belongs in an object.": the chapter's argument for *Null Object*, not a punchline.
- L1167, "the benefit of using types is tremendous": promotional by shape (§4); the author's stance, carried from the talk.
- L1170, "truly": confirmed keep in `readability_db.md` (2026-10-04).
- L1221-1222, ""Bundling behavior with state" gives you this: one object holds the state, and the same class defines every method that changes it.": two clauses after a colon, but "this" names what follows and the two clauses together are its content.
- L1224-1225, "OOP is useful, sometimes. But not everywhere, all the time.": echoes the heading as the talk's closing line; voice.
- L144 and L629, roadmap sentences ("For each one, the question is ...", "The four subsections below demonstrate it."): orientation the reader uses, not §70 gloss.
