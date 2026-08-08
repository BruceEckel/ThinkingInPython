[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review 2: `Chapters/12_Data_Classes_as_Types.md`

Run after the deep-review edits landed, so the new and moved prose gets the same
scan the rest of the chapter got in review 1.
Nothing from review 1 was rejected, so nothing is carried forward.

The chapter still reads as human throughout.
A vocabulary scan across the Tier 1A/1B/2 lists returned no hits,
no boldface padding, no rule-of-three inflation, no signposting, no curly
quotes, and no spaced ` -- `.
Six findings, most of them small, and three of them in prose written during the
deep review.

***

[] Reject

**Section:** A Type Is a Set of Values (paragraph after `stars.py`)
**Pattern:** watch list, `at all` (P2)

Current:
> Immutability guarantees no one can rebind the fields after construction,
> and when the fields are immutable too, no one can damage the value at all.

Proposed:
> Immutability guarantees no one can rebind the fields after construction,
> and when the fields are immutable too, no one can damage the value.

Why: the sentence means the same without the tag, which is the deletion test the
watch list applies. "No one can damage the value" is already absolute.

***

[] Reject

**Section:** Comparing Ordinary Classes and Data Classes (opening, new prose)
**Pattern:** §7 metaphor standing in for a literal statement (P2, borderline)

Current:
> `@dataclass` has been a black box so far:
> you declare fields and a constructor appears.

Proposed:
> So far `@dataclass` has been used without opening it up:
> you declare fields and a constructor appears.

Why: "black box" is a metaphor doing work a literal phrase can do, and the
chapter's other transitions are literal.
Borderline: the metaphor is standard in programming prose and the second half of
the sentence already says the concrete thing, so this may be a fair use rather
than a tell.

***

[] Reject

**Section:** Comparing Ordinary Classes and Data Classes (opening, new prose)
**Pattern:** §3 superficial analysis with an `-ing` ending (P2)

Current:
> Four small classes show the difference between a class body that declares fields and one that stores them,
> going further than [Class Attributes](09_Class_Attributes.md) did:

Proposed:
> Four small classes show the difference between a class body that declares fields and one that stores them,
> and go further than [Class Attributes](09_Class_Attributes.md) did:

Why: the participial tail turns a second claim into a trailing modifier.
A finite verb states it directly, and the deep-review file proposed that wording.

***

[] Reject

**Section:** `A`: Annotations Only (first sentence)
**Pattern:** watch list, `plain` (P2, borderline)

Current:
> `A` is the plain case, with no defaults and no constructor,
> but with field declarations that look like class variables:

Proposed:
> `A` is the simplest case, with no defaults and no constructor,
> but with field declarations that look like class variables:

Why: the global rule keeps "plain" only where it draws a real contrast.
Borderline: it arguably does here, against `B`'s defaults and `C`'s decorator,
so this is a preference rather than a fix.
The rest of the sentence already names what is missing, which is the contrast.

***

[] Reject

**Section:** `D`: A Real `ClassVar` (paragraph about `s`)
**Pattern:** §32 aphorism formula (P2)

Current:
> `s`, declared `ClassVar[str]`, is a different story.

Proposed:
> `s`, declared `ClassVar[str]`, behaves differently.

Why: "is a different story" is a stock phrase where a verb will do, and the
sentences after it say what the difference is.

***

[] Reject

**Section:** Defaults That Are Built, Not Shared (before `factory_checking.py`)
**Pattern:** §34 real/actual adjective inflation (P1)

Current:
> That form seems redundant,
> because the annotation on the left already names the type,
> and the subscript is erased at runtime.
> It gains one small but real thing:

Proposed:
> That form seems redundant,
> because the annotation on the left already names the type,
> and the subscript is erased at runtime.
> It gains one thing:

Why: "real" is a bare intensifier on an abstract noun, and the listing
immediately below shows what the thing is.
Dropping "small but real" also stops the sentence from arguing with itself two
words before the evidence arrives.

***

[] Reject

**Section:** Inheritance and the Generated `__init__` (after `dataclass_super_init.py`)
**Pattern:** global rule, imperative-plus-consequence (P1)

Current:
> Delete `__post_init__()` and the same line raises an `AttributeError`.

Proposed:
> If you delete `__post_init__()`, the same line raises an `AttributeError`.

Why: the global rules forbid commanding the reader and then reporting what
happens; the condition should be written as a condition.
This is not an instruction to the reader, since deleting the method is
hypothetical, so the imperative carve-out for exercises does not apply.
