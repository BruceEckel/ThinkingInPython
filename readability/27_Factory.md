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

The clear-cut fixes were applied to the chapter directly (listed below);
the two blocks that remain are the ones needing your judgment.

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

Line numbers below refer to the chapter before these edits;
the two 165-167 and 413-415 insertions shift later lines down by one each.

***

**Lines 270-288 (the `__init_subclass__()` caveat paragraph)**
**Pattern:** §57 excessive density, treadmill effect

The paragraph now carries four separate caveats in nineteen lines: import
timing, the `lazy import` variant, name collision, and (added this pass) the
`Shape.registry`-versus-`cls.registry` choice.
Each is worth keeping and each needs its own thought.
Read together they blur, and the last one is a different kind of claim from the
first three: the others are ways a reader's registry will fail, this one
explains a choice already made in the listing.

Proposed: split into three paragraphs at the existing seams.

1. Import timing, from "‌`__init_subclass__()` runs as" through "Import a plugin
   module eagerly when the import exists for its side effect."
2. Name collision, "The registry also keys on `cls.__name__` alone" through
   "Key on a qualified name if that can happen."
3. The `Shape.registry` choice, as its own paragraph.

No wording changes needed; the sentences already group this way, and the breaks
give a reader somewhere to stop.
I did not do it because paragraphing is pacing, and this section is the
chapter's argumentative center.

[] Reject

***

**Lines 405-408 (after `shape_factory2.py`)**
**Pattern:** dangling apposition, then §13 hidden actor

Current:
> `ShapeFactory.create_shape()` creates the shapes,
> a class method that reaches the registry through `cls` and finds the appropriate factory object based on an identifier that you pass it.
> The factory is immediately used to create the shape object,
> but you could imagine a more complex problem where the caller receives the appropriate factory object and then uses it to create an object in a more sophisticated way.

"a class method that..." sits after "creates the shapes," so it reads for a
moment as an apposition to "the shapes."
The next sentence then hides the actor ("The factory is immediately used")
and ends on "a more sophisticated way," which names nothing.
"The appropriate factory object" appears in both sentences, and a third
"appropriate" follows in the Abstract Factory section.

Proposed:
> `ShapeFactory.create_shape()` is a class method.
> It reaches the registry through `cls`,
> finds the factory object for the identifier you pass,
> and calls it right away.
> A more complex design would hand that factory object back to the caller,
> who could hold it and create objects from it later.

That keeps both points, names who does what, and drops one "appropriate."
This is first-edition prose rewritten wholesale, so it stays a block rather
than a direct edit: the fix is clear but the voice is yours to trade away.

[] Reject

***

## Considered and declined

**Line 26 — "Factory might be the most common design pattern."**
The deep-review pass removed "the most common form of factory in idiomatic
Python" from line 262 as an unsupported superlative, and this sentence makes
the same kind of claim.
But it is hedged with "might," opens the chapter, and is first-edition voice,
so I left it alone.
Recorded here so a later review does not re-raise it.
