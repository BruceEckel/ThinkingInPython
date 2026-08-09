> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/27_Factory.md`

Run right after the deep-review edits landed, so the new registry caveat, the
`__main__` guards, the rewritten self-registration and Builder sentences, the
`GameEnvironment` rewrite, and the two new demonstrations get the same scan as
the older prose.
No completed readability review exists for this chapter, so nothing is carried
forward.

The chapter reads as human prose, and much of it is first-edition voice with a
recognizable rhythm.
No §7 vocabulary hits, no curly quotes, no spaced ` -- `, no boldface or
bullet inflation, no formulaic conclusions.

Every finding was resolved directly: applied (listed below) or declined
with the reason recorded. No blocks remain.

## Applied directly

- Line 14: "It happens to be the creation of the type that matters here rather
  than the use of the type" → "Creation of the type matters here, not use of
  the type" (watched "happen" plus an "It ... that" cleft).
- Line 86: "It happens to be a string here but" → "Here it is a string, but"
  (watched "happen").
- Line 92: dropped "at all" after "with no argument" (watch list; the contrast
  is already in the sentence's first half).
- Lines 165-167: the prose now points at the listing's `False False` line
  instead of asserting the same fact: "The last line of the listing shows both
  checks failing: `type(a) is type(b)` is `False`, and so is
  `isinstance(a, type(b))`."
- Line 259: "which is what the printed key list shows" → "as the printed key
  list shows" (cleft that only delays the verb).
- Line 265: "Creating objects through a dictionary of classes is the
  dissolution" → "That is the dissolution" (the phrase opened two consecutive
  sentences).
- Line 274: "nothing ever imported the module" → "nothing imported the module"
  (watched "ever"; deletion changes nothing).
- Line 276: "from an import statement sitting right there in the file" →
  "even when the import statement is in the file" (conversational flourish;
  now states the surprise).
- Lines 413-415: added the pointer to the new cache-key output: "The two
  printed key lists show it: empty before any request, two entries after four
  requests for two kinds."
- Line 417: "leans on `eval()`" → "uses `eval()`" (metaphor for a literal
  verb).
- Line 866: dropped "just" in "steps are just optional values," matching the
  summary bullet's wording.

- Lines 270-288: the `__init_subclass__()` caveat paragraph split into
  three at its existing seams (import timing; name collision; the
  `Shape.registry`-versus-`cls.registry` choice). No wording changed; the
  last item is a different kind of claim from the first three, and the
  breaks give a reader somewhere to stop.
- Lines 405-408: "`ShapeFactory.create_shape()` creates the shapes, a class
  method that..." → "`ShapeFactory.create_shape()` is a class method. It
  reaches the registry through `cls`, finds the factory object for the
  identifier you pass, and calls it right away. A more complex design would
  hand that factory object back to the caller, who could hold it and create
  objects from it later." (the apposition read for a moment as describing
  the shapes, the passive hid the actor, and "a more sophisticated way"
  named nothing; drops one of three "appropriate"s).

Line numbers above refer to the chapter before these edits;
the 165-167 and 413-415 insertions and the paragraph split shift later
lines down.

***

## Considered and declined

**Line 26 — "Factory might be the most common design pattern."**
The deep-review pass removed "the most common form of factory in idiomatic
Python" from line 262 as an unsupported superlative, and this sentence makes
the same kind of claim.
But it is hedged with "might," opens the chapter, and is first-edition voice,
so I left it alone.
Recorded here so a later review does not re-raise it.
