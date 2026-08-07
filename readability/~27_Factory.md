[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/27_Factory.md`

This chapter reads as human throughout.
The legacy prose carried over from the Java-era material is unaffected,
and the newer Python sections (the dictionary factory, the registry, Prototype, Builder, the closing decision list)
stay concrete: named mechanisms, named failure modes, named standard-library examples.
No Tier-1A vocabulary, no promotional language, no rule-of-three padding, no generic conclusion.
Nothing here is P0 or P1.

What is left is a thin layer of P2 material:
three or four summarizing asides that restate the sentence before them (§70),
one "here is what to notice" signpost (§28),
and a handful of small clarity and consistency copyedits.
A mild secondary habit worth noting rather than fixing: several sentences use a mid-sentence colon to introduce a gloss
(lines 189, 274, 659, 704), which is fine individually but starts to feel like a tic when they cluster.

***

[] Reject

**Section:** Preventing Direct Creation (paragraph beginning "The privacy has a price.")
**Pattern:** §23 Filler and Precision (P2)

Current:
> so every `factory()` defines fresh `Circle` and `Square` classes.

Proposed:
> so every call to `factory()` defines fresh `Circle` and `Square` classes.

Why: There is one `factory()`; it is each *call* that defines new classes, which is exactly how the same paragraph phrases it six lines later ("on every `factory()` call"). Borderline, but the fix costs two words and removes a misreading.

***

[] Reject

**Section:** The Pythonic Factory: a Dictionary (paragraph beginning "Know when the registration runs")
**Pattern:** §28 Signposting and Announcements (P2)

Current:
> Know when the registration runs:
> `__init_subclass__()` runs as the subclass's `class` statement executes.

Proposed:
> `__init_subclass__()` runs as the subclass's `class` statement executes.

Why: The frame announces what the paragraph is about to say instead of saying it, and the paragraph's own content (invisible in one file, deferred across modules, the plugin that "never registered") already makes the timing the point.

***

[] Reject

**Section:** Polymorphic Factories (paragraph beginning "Now the factory methods are polymorphic")
**Pattern:** §70 Interpretive Metadiscourse / redundancy (P2)

Current:
> `ShapeFactory` is the dispatcher that finds and applies the correct one.

Proposed:
> Cut this sentence.

Why: The next sentence says the same thing with more detail ("`ShapeFactory.create_shape()` creates the shapes, a class method that reaches the registry through `cls` and finds the appropriate factory object based on an identifier that you pass it"), and the sentence after that covers the "applies" half. Cutting loses no fact.

***

[] Reject

**Section:** Abstract Factories (paragraph beginning "In this environment")
**Pattern:** copyedit, internal consistency (P2)

Current:
> but there are different types of Characters and obstacles depending on what kind of game you're playing.

Proposed:
> but there are different types of characters and obstacles depending on what kind of game you're playing.

Why: The same clause capitalizes one plain-English noun and not its parallel partner; the class names in the sentence before it are already set in code font as `Character` and `Obstacle`. Not an AI tell, just an inconsistency.

***

[] Reject

**Section:** Abstract Factories (paragraph beginning "The base classes `Obstacle`, `Character`, and `GameElementFactory`")
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> The two forms look interchangeable in a listing and fail at different moments.

Proposed:
> Cut this sentence.

Why: The two preceding sentences already establish that `raise NotImplementedError` fails at call time and `@abstractmethod` fails at instantiation, so this one restates the contrast as a closing gloss. Borderline: it is the kind of summary line a human writes for emphasis, so reject it if you want the beat.

***

[] Reject

**Section:** Abstract Factories (paragraph beginning "The concrete classes inherit nothing")
**Pattern:** §23 Filler and Precision, vague pronoun (P2)

Current:
> and uncommenting the line that passes one produces `protocol member make_obstacle is not defined on type BrokenFactory`.

Proposed:
> and uncommenting the line that passes a `BrokenFactory` to `GameEnvironment` produces `protocol member make_obstacle is not defined on type BrokenFactory`.

Why: "one" sits closer to `make_obstacle()` than to `BrokenFactory` and can be read as either; the commented-out line in the listing names both classes, so the replacement adds no fact the source lacks.

***

[] Reject

**Section:** Prototype (paragraph beginning "The deep copy is the part that matters")
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> The deep copy is the part that matters.

Proposed:
> Cut this sentence.

Why: It tells the reader how much weight to give what follows instead of stating it; the next two sentences make the case concretely, and the paragraph reads cleanly starting from "`captain` gets its own `powers` list."

***

[] Reject

**Section:** Prototype (sentence introducing `test_prototype.py`)
**Pattern:** §69 Colon Reveals (P2)

Current:
> These tests pin down the two properties a prototype registry has to have:
> each spawn is independent, and the stored prototype never changes:

Proposed:
> These tests pin down the two required properties for a prototype registry.
> Each spawn must be independent, and the stored prototype must never change:

Why: Two colons in one sentence, the second doing the real work of introducing the listing, so the first reads as a stall. Borderline stylistic.
