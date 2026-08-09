> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/31_State_Machines.md`

Run right after the deep-review edits landed, so the new `NoTransition` prose,
the two new `###` headings, the rewritten constructor-trap and enum paragraphs,
the module-shadowing note, the new `## Which Design Should You Use?` section,
and the rewritten exercises 6, 7, and 9 get the same scan as the older prose.
No completed readability review exists for this chapter, so nothing is carried
forward.

Much of this chapter is first-edition prose translated from *Thinking in Java*,
and it reads differently from the newer material around it: longer sentences,
more "you can see that," more hedging.
That is a voice question rather than an AI-tell question, and I have kept the
findings to places where it actually costs the reader something.
No §7 vocabulary hits, no curly quotes, no spaced ` -- `, no boldface or bullet
inflation.

Line numbers refer to the chapter as it stands now.

***

**Line 844 — "a machine that arrived as a diagram wants the table"**
**Pattern:** watch list, "don't use"; §35 volition on a non-agent

Current (the closing sentence of the new section):
> A machine small enough to hold in your head goes either way,
> and a machine that arrived as a diagram wants the table.

This is the chapter's last sentence, so the tic lands where it is most visible.

Proposed:
> A machine small enough to hold in your head goes either way,
> and a machine that arrived as a diagram belongs in the table.

[] Reject

***

**Lines 33-36 — "This class is unnecessary. However, it lets you say..."**
**Pattern:** a concession that reverses itself in two sentences

Current:
> This class is unnecessary.
> However, it lets you say that something is a `State` object in code,
> and provide a slightly different error message when a derived class fails to implement all the methods.
> You could get nearly the same effect by saying:

The paragraph says the class is unnecessary, then spends four sentences on what
it does for you, then offers a weaker alternative.
A reader cannot tell whether they are being told to write it or not.

Proposed:
> Python does not require this class.
> It earns its two lines by naming `State` as a type in annotations,
> and by producing a better error message when a derived class leaves a method out.
> You could get nearly the same effect by saying:

That states the same facts and stops the sentence from arguing with the next
one. Note this reintroduces "earns its," which you have been cutting elsewhere;
if you would rather avoid it, "It is worth its two lines because it names
`State` as a type..." says the same.

[] Reject

***

**Line 255 — "perfectly reasonable"**
**Pattern:** §24 hedge, and a compliment paid to code the section is about to
replace

Current:
> While the use of `match` inside the `next()` methods is perfectly reasonable,
> managing a large number of these could become difficult.

"Perfectly reasonable" and "could become difficult" hedge in both directions, so
the sentence commits to nothing. The point is concrete: the `match` version
scales badly in the number of states.

Proposed:
> The `match` statements inside `next()` work,
> but a machine with many states means many of them, spread across many classes.

[] Reject

***

**Line 391 — "a bug you want flagged"**
**Pattern:** watch list, "want"

Current:
> Failing fast suits a table you are still building,
> where a missing entry is a bug you want flagged,

Addressed to the reader, so "want" is defensible under the rule's carve-out for
second-person address, but the passive "flagged" leaves the flagger unnamed.

Proposed:
> Failing fast suits a table you are still building,
> where a missing entry is a bug the machine should report,

Low confidence: the current sentence is clear, and this may be a change for its
own sake. Reject if it reads fine to you.

[] Reject

***

**Lines 427-432 (the new module-shadowing note)**
**Pattern:** density; three mechanisms in one sentence

Current:
> The file has a different name from the first engine's `state_machine.py` on purpose.
> A module already in `sys.modules` is never re-resolved from `sys.path`,
> so two modules sharing a basename in one program means whichever imported first wins,
> and the second import silently receives the wrong one.

The second sentence carries the cache, the resolution rule, the collision, and
the consequence. It is correct and it needs two readings.

Proposed:
> The file has a different name from the first engine's `state_machine.py` on purpose.
> Python caches a module in `sys.modules` under its basename,
> and never looks it up again once it is there.
> Two files named `state_machine.py` in one program therefore collapse into one:
> whichever imported first wins, and the second import silently gets the wrong module.

[] Reject

***

**Line 828 — "real behavior"**
**Pattern:** §34 real-adjective inflation

Current (new section):
> Each-state-decides suits a machine whose states have real behavior and few transitions apiece.

Nothing names what unreal behavior would be. The contrast the section draws two
paragraphs later is concrete: the table-driven states "shrink to `Enum` members
with no behavior at all."

Proposed:
> Each-state-decides suits a machine whose states do something,
> and have few transitions apiece.

[] Reject

***

**Line 85 — "worth remembering during exercise 3"**
**Pattern:** §53 endorsement frame

Current:
> A `State` whose `run()` reads attributes off the machine revives the trap,
> which is worth remembering during exercise 3.

The clause rates the information instead of using it; the instruction is
"exercise 3 will hit this."

Proposed:
> A `State` whose `run()` reads attributes off the machine revives the trap,
> as exercise 3 will show.

[] Reject

***

**Line 487 — "keys on `type(event)` exactly"**
**Pattern:** watch list, "exactly"

Current:
> Note that the lookup keys on `type(event)` exactly: a dictionary probe,
> not an `isinstance()` walk.

Here "exactly" survives the test: the colon spells out the precise-match claim,
and the whole paragraph exists because the match is exact rather than
approximate. The global rule allows it for "a precise numeric or logical
match," which this is.

"Note that" is the part worth cutting:
> The lookup keys on `type(event)` exactly: a dictionary probe,
> not an `isinstance()` walk.

[] Reject

***

**Line 509 — "plain methods"**
**Pattern:** watch list, "plain"

Current:
> The conditions and actions are plain methods, stored directly in the table.

"Plain" draws a real contrast here: against the `Condition` and `Transition`
class hierarchies the Java version needed, named a few paragraphs earlier.
The rule's carve-out covers it.

No change proposed. Recorded so a mechanical sweep does not cut it.

[] Reject
