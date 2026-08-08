[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review 2: `Chapters/14_Decorators.md`

Run after the deep-review edits landed, so the new and moved prose gets the same
scan the rest of the chapter got in review 1.
Nothing from review 1 was rejected, so nothing is carried forward.

The chapter still reads as human technical prose.
No AI vocabulary hits, no significance inflation, no signposting, no boldface
padding, no curly quotes, no spaced ` -- `.
Five findings, all in prose written or moved during the deep review.

***

[] Reject

**Section:** Decorators That Take Arguments (after the `repeat.py` listing)
**Pattern:** §23 clarity, vague referent (P2)

Current:
> That first call is unconditional,
> so a `times` below one would still call `func` once rather than zero times.
> `repeat()` rejects such a value where it arrives instead.

Proposed:
> That first call is unconditional,
> so a `times` below one would still call `func` once rather than zero times.
> `repeat()` rejects those values rather than quietly rounding them up to one.

Why: "such a value where it arrives instead" carries three vague pieces at once,
and "instead" reaches back past the intervening clause.
Naming what the rejection replaces says the same thing in one pass.
The sentence after it already explains where the check runs.

***

[] Reject

**Section:** Decorating Classes (paragraph after `register.py`)
**Pattern:** §57 structure, a topic inserted mid-argument (P2)

The registry caveats now sit between the sentence about the side effect and the
sentence about the type parameter, so the paragraph goes side effect → import
completeness → name collisions → typing, and the typing point restarts a thread
the caveats interrupted.

Proposed: leave the first two sentences where they are, and move the three
caveat sentences into their own paragraph after "A class decorator can also
return a replacement class, just as a function decorator returns a replacement
function." That puts them next to the `__init_subclass__` pointer, which is the
other "registries have consequences" sentence in the section.

Why: the caveats and the typing explanation answer different questions, and each
reads better uninterrupted.

***

[] Reject

**Section:** Decorating Classes (same paragraph)
**Pattern:** §23 clarity, fronted participle (P2)

Current:
> Annotated `(cls: type) -> type` instead,
> `register` would hand back a bare `type`,
> and the checker would then see `Espresso()` as an `Any`.

Proposed:
> Annotated `(cls: type) -> type` instead,
> it would hand back a bare `type`,
> and the checker would see `Espresso()` as an `Any`.

Why: the fronted participle attaches to `register`, but the reader meets the
participle first and has to hold it open until the subject arrives.
Using the pronoun shortens that gap; "then" goes with it, since the sentence is
already sequential.
An alternative, if you would rather remove the construction: "If `register` were
annotated `(cls: type) -> type`, it would hand back a bare `type`."  [[do this]]

***

[] Reject

**Section:** What `@` Does Not Require (before `run_once.py`)
**Pattern:** §23 clarity, unanchored ordinal (P2)

Current:
> A second surprise sits on the return side.

Proposed:
> The return side is equally unconstrained.

Why: the section's new opening no longer calls the first point a surprise, so
"second" counts from something the reader was never given.
The replacement states the parallel the ordinal was carrying.

***

[] Reject

**Section:** Function Form or Class Form? (second paragraph)
**Pattern:** §23 clarity, tense mismatch (P2)

Current:
> and both stack the same way `stacking.py` stacked two function-form decorators.

Proposed:
> and both stack, the way `stacking.py` stacks two function-form decorators.

Why: "stack ... stacked" mixes tenses inside one clause, and the chapter
otherwise describes its listings in the present.
