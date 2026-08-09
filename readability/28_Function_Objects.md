> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/28_Function_Objects.md`

Run right after the deep-review edits landed, so the rewritten `Command`
paragraph, the new convergence caveat, the reordered chain paragraphs, the new
`Choosing the Lightest Callable` section, and the new exercise 6 get the same
scan as the older prose.
No completed readability review exists for this chapter, so nothing is carried
forward.

The chapter reads as human prose with good rhythm, and the deflating one-liners
("Three identical lines is the point", "four classes and a wrapper to say what
one list of functions says directly") are the best writing in it.
No §7 vocabulary hits, no curly quotes, no spaced ` -- `, no boldface or bullet
inflation.
Three findings are in prose written during this pass; the rest are watch-list
words and one repeated phrase.

Line numbers refer to the chapter as it stands now.

***

**Line 144 — "want" applied to code**
**Pattern:** watch list, "don't use"; §35 moral/volitional adjective on a
non-agent

Current:
> A `Command` base class becomes worth writing when the commands also want shared implementation.

Commands do not want anything.
This is prose written during the deep-review pass, replacing the "earns its
keep" sentence you asked to be rewritten, so the tic came in with the fix.

Proposed:
> A `Command` base class becomes worth writing when the commands also share implementation.

Line 616 in the new closing section has the same verb:
> 4.  A callable object, when that configuration wants a name and a `repr`

Proposed:
> 4.  A callable object, when that configuration needs a name and a `repr`

Line 598 ("If you instead want a single handler per type") and line 629 ("do
you now want an object?") address the reader, so they stay.

[] Reject

***

**Line 337 — "earns its keep" survives here**
**Pattern:** stock phrase, now inconsistent

Current:
> The Context earns its keep when something has to hold the current algorithm between calls,
> which a parameter cannot do.

You had the phrase cut from chapter 26's conclusion and rewritten out of this
chapter's `Command` paragraph.
This is the last instance in the chapter, and it sits in a sentence that would
read more directly without it.
"Has to" is also on the watch list.

Proposed:
> The Context becomes useful when something must hold the current algorithm between calls,
> which a parameter cannot do.

If you would rather keep one home for the phrase, this is a defensible one:
the Context is being weighed against a cheaper alternative, which is the
comparison the idiom exists for. Then mark this rejected.

[] Reject

***

**Line 438 — "A handler is trusted to know when it failed"**
**Pattern:** §13 subjectless passive, hiding who trusts

Current (prose added this pass):
> A handler is trusted to know when it failed.
> `secant()` and `newton()` stop when their step stops shrinking,
> which is not quite the same as landing on a root,
> so a chain is only as reliable as its handlers.

The passive hides the actor, and the actor is the point: the chain does the
trusting, and that is why a bad self-assessment propagates.

Proposed:
> The chain trusts each handler to know when it failed.
> `secant()` and `newton()` stop when their step stops shrinking,
> which is not quite the same as landing on a root,
> so a chain is no more reliable than its handlers.

"Only as reliable as" also becomes "no more reliable than," which drops the
watched "only" and says the same thing.

[] Reject

***

**Lines 27 and 98 — "just a function" twice**
**Pattern:** §23 empty adverb, and repetition seventy lines apart

Current:
> In Python the action is just a function, and a "macro" is a list of actions:

and
> In Python a callback is just a function, so the replacement is unnecessary.

Both sentences open the same way and lean on the same word.
"Just" is doing deflating work in the second one, where it answers *GoF Design
Patterns* calling commands "an object-oriented replacement for callbacks," so
that is the one to keep.

Proposed for line 27:
> In Python the action is a function, and a "macro" is a list of actions:

Leave line 98 as it stands.

[] Reject

***

**Lines 610-611 (the new closing section's opening)**
**Pattern:** a summary claim wider than what the chapter did

Current:
> Each section of this chapter replaced a class hierarchy with something smaller,
> and the replacements form one list.

The *Command* and *Strategy* sections show the function first and the hierarchy
second, so they do not replace anything; they decline to build it.
The claim also does not fit the event bus, which replaces a list rather than a
hierarchy.

Proposed:
> Every section of this chapter reached for something smaller than a class hierarchy,
> and the alternatives form one list.

Or, if you would rather not generalize at all:
> The alternatives this chapter showed form one list.

I recommend the second: it is shorter, and the list immediately after it makes
the point on its own. Note that "reached for" is a banned phrase, so the first
version needs different wording if you prefer its shape.

[] Reject

***

**Line 146 — "springs" and "best-known"**
**Pattern:** metaphor plus superlative in one clause

Current:
> Building commands in a loop springs Python's best-known closure trap:

"Springs" is the right verb for a trap and reads well.
"Best-known" is an unsupported superlative, and the sentence loses nothing
without it.

Proposed:
> Building commands in a loop springs Python's best-known closure trap:
> becomes
> Building commands in a loop springs Python's closure trap:

Low confidence: "best-known" tells a reader this is the trap they have heard
about, which is useful orientation. Reject if you read it that way.

[] Reject

***

**Line 96 — "to say what one list of functions says directly"**
**Pattern:** none; noting it as a keeper

No change proposed.
This is the sharpest sentence in the chapter and the reason the *Command*
section works.
Recorded here so a later pass does not "tighten" it.

[] Reject
