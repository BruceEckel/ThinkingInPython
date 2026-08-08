> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review 2: `Chapters/17_Metaprogramming.md`

Run after the deep-review edits landed, so the new prose gets the same scan the
rest of the chapter got in review 1.
Nothing from review 1 was rejected, so nothing is carried forward.

The chapter still reads as human technical prose.
No AI vocabulary hits, no significance inflation, no signposting, no boldface
padding, no curly quotes, no spaced ` -- `.
Five findings, all in prose written during the deep review.

***

[] Reject

**Section:** Multiple Inheritance and Metaclasses (after the new `mixin.py` lines)
**Pattern:** accuracy, a cross-reference that names the wrong section (P2)

Current:
> That is the metamethod rule from the start of this section, failing out loud:

Proposed:
> That is the metamethod rule from the start of
> [Intercepting Instance Creation](#intercepting-instance-creation), failing out loud:

Why: the rule is stated at the head of "Intercepting Instance Creation", one
subsection up, not at the start of the subsection the sentence sits in.
A reader who looks back at "this section" finds the layout-conflict discussion
instead.

***

[] Reject

**Section:** Multiple Inheritance and Metaclasses (after the moved metaclass-conflict listing)
**Pattern:** §69 colon reveal, §32 aphorism formula (P2)

Current:
> Two failures, one shape: an inheritance graph that looks legal until you notice what the bases carry with them.

Proposed:
> Both failures have the same shape: an inheritance graph that looks legal until you notice what the bases carry with them.

Why: "Two failures, one shape:" is a verbless fragment staging a reveal, and the
sentence after the colon is the actual claim.
Stating it as a sentence keeps the pairing, which is the reason the two listings
now sit together.

***

[] Reject

**Section:** When You Still Need a Metaclass (new closing sentence)
**Pattern:** watch list, a metaphor standing in for the literal thing (P2)

Current:
> That is the whole case for reaching this far down:
> the class object needs behavior, and nothing that runs after the class exists can give it any.

Proposed:
> That is the whole case for a metaclass:
> the class object needs behavior, and nothing that runs after the class exists can give it any.

Why: "reaching this far down" is a spatial metaphor for "using a metaclass", and
the section is named for the literal thing.
The watch list also flags "reach" phrasing generally.

***

[] Reject

**Section:** Which Hook for Which Job (after `hook_order.py`)
**Pattern:** global rule, cut "is what" (P2)

Current:
> Knowing that sequence is what picks the hook.

Proposed:
> Knowing that sequence picks the hook.

Why: a verb follows the cleft, which is the giveaway that it only delays the
verb. The sentence means the same without it.

***

[] Reject

**Section:** Which Hook for Which Job (final paragraph)
**Pattern:** watch list, `itself` used as a flourish (P2)

Current:
> A class is an object, built at run time by executing its body,
> and `hook_order.py` is that construction narrating itself.

Proposed:
> A class is an object, built at run time by executing its body,
> and `hook_order.py` displays each step of that construction as it happens.

Why: "narrating itself" personifies the listing where a literal statement does
the same work, and the chapter's other summaries stay literal.
