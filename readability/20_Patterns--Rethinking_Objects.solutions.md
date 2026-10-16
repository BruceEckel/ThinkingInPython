> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Rethinking Objects, Solutions

The Solutions file for chapter 20 carries no Tier 1 or Tier 2
vocabulary, no signposting, and no significance inflation.
Most of the ten changes below apply the author's "and" rule: clauses
with different subjects whose relation is a contrast or a consequence.
The rest drop a doubled "at runtime", name the noun behind two vague
pointers ("the author", "the object"), replace "The chapter describes
that split" with a link to the section that describes it, and merge a
"Then ... Then" run in exercise 8's hint.
The section link and the `frozen_leaky.py`, `PairCoord`, `SILENT`, and
composition claims the prose makes were checked against
`Chapters/20_Patterns--Rethinking_Objects.md`.
This file holds no live block, so it records the direct edits.
No `~` review exists for this file, so `readability_db.md` governed the
keeps.

## Applied directly

- Lines 152-155, "and" joining different subjects (contrast): "The caller now mutates a throwaway copy, and `plugged`'s real `_tags` keeps the items it had" -> two sentences; the second "now" in the paragraph dropped.
- Lines 217-218, "and" hiding a consequence: "`Bob` is a mutable data class that compares by value, and on such a class `@dataclass` sets `__hash__` to `None`" -> two sentences.
- Lines 219-220, pointer with two candidates (`Immutable` or `Bob`): "If a field changed after the object went into a dict, the object's hash would change" -> "If a field of a `Bob` changed after that `Bob` went into a dict, its hash would change".
- Line 229, pointer that could read as the book's author: "The author must make immutability go all the way down" -> "The author of each class must ...".
- Lines 339-341, repeated phrase: "returns a float at runtime, as before", one sentence after "At runtime, `Package` still matches" -> "returns a float, as before".
- Line 349, §70 vague pointer: "The chapter describes that split." -> "[What the Shape Does Not Say](...) describes that split.", the section the exercise's hint links.
- Lines 448-449, "and" joining different subjects (contrast): "`Triple` names its fields `a`, `b`, and `c`, and a 2D distance uses two of them" -> two sentences.
- Line 722, "and" hiding a consequence: "adds the two elements, and `appends` stays at 1" -> "adds the two elements, so `appends` stays at 1".
- Lines 807-810, "and" joining different subjects, twice: "`CountingBox` gets only the methods you write for it, and a caller who needs `sort()` waits" and "With inheritance, `list` decides, and you discover later" -> sentences split at each "and".
- Line 944, "and" joining two standalone claims: "Inheritance is a claim about substitutability, and for `BoundedStack` that claim is false" -> two sentences.
- Lines 830-831, staccato "Then ... Then" run in exercise 8's hint: "Have `push()` accept every item and enforce the limit another way. Then add a `full()` method" -> one sentence joined by "and", leaving one "Then" before the final step.

## Considered and declined

- The bold step labels ("**Expose the internal list.**", "**Check hashability.**", and the rest): §15 by shape, but they are the Solutions files' step convention across the book.
- Line 348, "The distinction is real in the source and absent in the process.": §47 mirroring by shape, but the two halves are the exercise's answer (type check versus runtime), not an invented contrast.
- Line 872, "A refusal by return value is still a refusal": §32 aphorism by shape; it is the reason the solution rejects the `bool` return, and the sentence's "so" clause depends on it.
- Line 937, "Should `BoundedStack` be a subclass of `Stack`? Probably not.": the question is the exercise's own, and "Probably not." is a beat among long sentences (recurring keeps).
- Lines 13, 113, 154, and 587, "real internal list", "real `_tags`", "a real logger": §34, but each names its contrast (a copy, a null logger) in the same sentence (recurring keep).
- Line 212, "never runs": a guarantee, not emphasis (recurring keep).
- Lines 450-453, "the two properties `distance()` reads" and "because it reads `.x` and `.y` alone": a near repeat, but the second sentence answers the exercise's "with no change to `distance()`".
- Line 208, "The type checker accepts the assignment, and Python runs it.": additive; both clauses report that nothing objects.
- Lines 809-810, the "With composition ... With inheritance" pair: §47 by shape, but a real contrast the exercise sets up.
- Line 797, "A future CPython could add another.": speculative by shape (§45), but it states why the list of bypass routes cannot be closed.
- Lines 566-572, 799-803, and 922-925: source lines wrapped unevenly, which renders the same; left alone to keep the diff to real edits.
