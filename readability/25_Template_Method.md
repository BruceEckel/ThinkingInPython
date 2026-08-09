> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review 2: `Chapters/25_Template_Method.md`

Run after the deep-review edits landed, so the redesigned flagship listing, the
reframed constructor subsection, the new `## What Actually Fixes the Algorithm`
section, and the new exercise get the same scan the rest of the chapter got in
review 1.
Nothing from review 1 was rejected, so nothing is carried forward.

The chapter still reads as human prose.
No §7 vocabulary hits, no curly quotes, no spaced ` -- `.
Every finding below is in prose written during this pass, and the first one is
an accuracy problem rather than a style one.

***

**Section:** What Actually Fixes the Algorithm (second paragraph)
**Pattern:** a summary line that misdescribes the list under it (P1)

Current:
> They are listed in increasing cost and decreasing reach.

Proposed: cut the sentence, and let the four sentences after it carry the
comparison they already make.

Why: "decreasing reach" is backwards.
Structure covers only the case where you can pass functions instead of
subclassing, `@final` covers everyone who runs the checker,
`__init_subclass__()` covers everyone including the caller who skips it.
Reach widens down the list while cost rises, so the two halves of the sentence
disagree, and the paragraph then spends four sentences describing the widening
the summary just denied.

This needs your call because there are two defensible repairs and they say
different things.
Cutting the sentence is the cheap one and loses nothing, since the paragraph
was already making the comparison item by item.
Correcting it to "increasing cost and increasing reach" keeps the summary and
makes the trade explicit, which is the more useful sentence if you want the
reader to leave with a rule.
I did not pick, because the second version asserts a tidy relationship between
cost and coverage that holds for the first three mechanisms and breaks on
discipline, which costs the most and guarantees the least.

[] Reject

***

**Section:** Don't Start the Engine in the Constructor (opening)
**Pattern:** §39 self-labeling, a withheld reason used as a hook (P2)

Current:
> `ApplicationFramework` leaves starting to the client for a reason.
> A framework can call `run()` from its own constructor,
> and the `Framework` below does, which is where the trap lives.

Proposed:
> `ApplicationFramework` leaves starting to the client, and the `Framework`
> below shows what happens when a framework does not.
> A framework can call `run()` from its own constructor,
> and a subclass with its own `__init__()` then has a trap to avoid.

Why: "for a reason" announces that a reason is coming instead of giving it,
which is the tell, and the sentence after it does not supply the reason either;
the reason arrives at the end of the section.
"where the trap lives" is also a metaphor standing in for the literal statement.
The replacement names the contrast the subsection exists to draw and drops both.

[] Reject

***

**Section:** What Actually Fixes the Algorithm (last line)
**Pattern:** stranded preposition (P2)

Current:
> Choose by asking who you are protecting the algorithm from.

Proposed:
> Choose by asking whom you are protecting the algorithm against.

Why: the sentence ends on "from" with its object moved, which the style rules
rule out.
"Against" also fits the verb better than "from" does.

[] Reject

***

**Section:** What Actually Fixes the Algorithm (first paragraph)
**Pattern:** watch-list words, two in one paragraph (P2)

Current:
> The fixed algorithm is only ever as fixed as the mechanism holding it,
> ...
> and no tool checks that at all.

Proposed:
> The fixed algorithm is only as fixed as the mechanism holding it,
> ...
> and no tool checks it.

Why: "ever" and "at all" are both on the watch list, and both delete cleanly
here.
"checks that at all" also has a vague "that"; naming it "it", the substitution,
is shorter and clearer.

[] Reject
