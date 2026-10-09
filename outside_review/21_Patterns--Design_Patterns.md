<!-- outside review of Chapters/21_Patterns--Design_Patterns.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `21_Patterns--Design_Patterns.md` chapter:

**1. Section: Patterns You Have Already Seen (Terminology)**

* **Target Text:** "Composition also qualifies as a pattern, since it lets you change, dynamically or statically, the objects that implement your class, and thus the way that class works."
* **Issue:** Objects do not "implement" a class; they are instances of it. In composition, a class relies on composed objects to provide its behavior. Using "implement" here incorrectly mixes class/interface inheritance terminology with object delegation.
* **Instruction:** Change to "Composition also qualifies as a pattern, since it lets you change, dynamically or statically, the objects your class delegates to, and thus the way that class works."

**2. Section: What One Part Knows About Another (Precision on Protocol inheritance)**

* **Target Text:** "A `Protocol` is a class you write and nothing inherits, and a `Callable` annotation is not a class."
* **Issue:** Defining a structural type in Python requires the protocol class itself to explicitly inherit from `typing.Protocol`. Phrasing it as "nothing inherits" might mislead readers into thinking it has no base class at all, rather than meaning that the concrete classes satisfying the protocol do not inherit from it.
* **Instruction:** Change to "A `Protocol` is a class you write that no implementer inherits, and a `Callable` annotation is not a class."

**3. Section: A Pattern Moves an Edge (Contradictory statement)**

* **Target Text:** "The subject knows no observer: "All a subject knows is that it has a list of observers, each conforming to the simple interface of the abstract `Observer` class.""
* **Issue:** The claim "The subject knows no observer" directly contradicts the GoF quote that immediately follows it, which clearly states the subject does know its observers via their abstract interface. What the subject hides from is the concrete observer class, which is the essence of abstract coupling.
* **Instruction:** Change "The subject knows no observer:" to "The subject knows no concrete observer:".

**4. Section: Design Principles (Precision on coupling type)**

* **Target Text:** "The Law of Demeter is another way to say "minimize coupling.""
* **Issue:** The Law of Demeter is more specific than minimizing coupling in general. It explicitly restricts transitive or navigational coupling—where a method reaches through one dependency's object graph to couple to another's internals. Equating it broadly to "minimize coupling" loses this structural distinction.
* **Instruction:** Change to "The Law of Demeter is a specific rule for minimizing transitive coupling."

## Verdicts

Applied in commit 1066f5e0, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. The chapter's coupling section uses "implement" for a class that satisfies an interface ("every class that implements them"), so "the objects that implement your class" collides with that sense; the sentence now reads "the objects to which your class delegates", which avoids the reviewer's stranded "delegates to".
2. Applied. A probe `Protocol` showed `typing.Protocol` in its own `__mro__` while a matching `Square` with only `object` as a base passed `ty check`, so the protocol does inherit and its implementers do not; the sentence now reads "a class you write and no implementer inherits", parallel to the abstract base class sentence before it.
3. Applied. "The subject knows no observer" contradicted the GoF quote after it, which says the subject knows its observers through the abstract `Observer` interface; the paragraph is about heavy edges to concrete classes, so the sentence now reads "The subject knows no concrete observer".
4. Rejected. The bullet's previous sentence already states the specific restriction ("not to the internals of objects it reached through something else"), and the closing sentence ties that rule to the chapter's coupling theme; "transitive coupling" is a term the chapter never defines.
