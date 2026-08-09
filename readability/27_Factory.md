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
The findings split three ways: one paragraph that has grown past what a reader
can hold, two sentences whose grammar tangles, and a run of single watch-list
words.

Line numbers refer to the chapter as it stands now.

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

[] Reject

***

**Line 26**
**Pattern:** unsupported superlative

Current:
> Factory might be the most common design pattern.

The deep-review pass removed "the most common form of factory in idiomatic
Python" from line 262 as an unsupported superlative.
This one is hedged with "might" and is about the pattern rather than about a
form of it, so it is defensible, but the two sat in the same chapter making the
same kind of claim.

Proposed, if you want them consistent:
> Factory may be the design pattern you use most.

That keeps the hedge and drops the ranking claim about the whole field.
I lean toward leaving line 26 alone: it opens the chapter, the hedge is
explicit, and the sentence is first-edition voice.
If you agree, mark this rejected.

[] Reject

***

**Lines 262-266**
**Pattern:** repetition in consecutive sentences

Current:
> A dictionary of classes, filled by hand or filled by the classes themselves,
> is the ordinary Python factory.
> Creating objects through a dictionary of classes is the dissolution described in [The Pattern Concept](21_The_Pattern_Concept.md#when-a-pattern-dissolves):

"A dictionary of classes" opens two sentences in a row.
This is prose written during the deep-review pass, replacing a single sentence,
so the collision is new.

Proposed for the second sentence:
> That is the dissolution described in [The Pattern Concept](21_The_Pattern_Concept.md#when-a-pattern-dissolves):

[] Reject

***

**Lines 165-167 (after `nested_shape_factory.py`)**
**Pattern:** a claim that now has evidence the prose does not point at

Current:
> Two shapes from different calls share behavior but not a class:
> `type(a) is type(b)` is `False`,
> and `isinstance()` comparisons across calls fail with it.

The listing now prints `False False` for exactly this, added during the
deep-review pass, but the prose still reads as an assertion.
"Fail with it" is also vague about what "it" is.

Proposed:
> Two shapes from different calls share behavior but not a class.
> The last line of the listing shows both checks failing:
> `type(a) is type(b)` is `False`,
> and so is `isinstance(a, type(b))`.

[] Reject

***

**Lines 413-415**
**Pattern:** same, for the cache

Current:
> `ShapeFactory` fills its dictionary lazily.
> The first request for a kind builds that kind's factory object (via `eval()`)
> and caches it for later requests.

The listing now prints the cache keys before and after, added this pass.

Proposed, adding one sentence at the end:
> The two printed key lists show it: empty before any request,
> two entries after four requests for two kinds.

[] Reject

***

**Line 259 — "which is what"**
**Pattern:** cleft that delays the verb (global rule on "is what")

Current:
> The two `class` statements filled `Shape.registry` on their own,
> which is what the printed key list shows.

Proposed:
> The two `class` statements filled `Shape.registry` on their own,
> as the printed key list shows.

[] Reject

***

**Lines 14 and 86 — "happens to be" twice**
**Pattern:** watch list, "consider rewriting"

Line 14:
> It happens to be the creation of the type that matters here rather than the use of the type

This is also an "It ... that" cleft on top of the watched verb.

Proposed:
> Creation of the type matters here, not use of the type

Line 86:
> It happens to be a string here but it could be any set of data.

Proposed:
> Here it is a string, but it could be any set of data.

Both are first-edition sentences, so take them together or leave them together.

[] Reject

***

**Line 92 — "at all"**
**Pattern:** watch list, "avoid if possible"

Current:
> a generator object holds an internal algorithm and produces the next value with no argument at all.

The contrast with the factory taking information is already in the first half
of the sentence, so "at all" repeats it.

Proposed:
> a generator object holds an internal algorithm and produces the next value with no argument.

[] Reject

***

**Line 276 — "sitting right there in the file"**
**Pattern:** §31 conversational flourish in explanatory prose

Current:
> A [lazy import](06_Modules_and_Packages.md#lazy-imports)
> produces that same failure from an import statement sitting right there in the file.

Proposed:
> A [lazy import](06_Modules_and_Packages.md#lazy-imports)
> produces the same failure even when the import statement is in the file.

That states the surprise (the import is present and still does not register)
instead of gesturing at it.

[] Reject

***

**Line 417 — "leans on"**
**Pattern:** metaphor standing in for a literal verb

Current:
> This version leans on `eval()` and a `Factory` class nested in every shape,
> neither of which Python needs.

Proposed:
> This version uses `eval()` and a `Factory` class nested in every shape,
> neither of which Python needs.

[] Reject

***

**Line 866 — "just"**
**Pattern:** §23 empty adverb, and inconsistent with the summary bullet

Current:
> When the "steps" are just optional values,
> keyword arguments and a data class are the builder.

The summary bullet at the end of the chapter states the same rule without
"just": "When the 'steps' are optional values, keyword arguments are the
builder."

Proposed: drop "just" here so the two agree.

[] Reject

***

**Lines 273-274 — "nothing ever imported"**
**Pattern:** watch list, "avoid if possible"

Current:
> the class is fine,
> the registry is fine, and nothing ever imported the module that defines it.

Deleting "ever" changes nothing: "nothing imported the module that defines it"
is already absolute.

Proposed:
> the class is fine,
> the registry is fine, and nothing imported the module that defines it.

Lowest-priority item in the file; the sentence reads well either way.

[] Reject
