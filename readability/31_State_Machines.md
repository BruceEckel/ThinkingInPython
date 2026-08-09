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
findings to places where it costs the reader something.
No §7 vocabulary hits, no curly quotes, no spaced ` -- `, no boldface or bullet
inflation.

The clear-cut fixes were applied to the chapter directly (listed below);
one block remains for your judgment.

## Applied directly

- Line 85: "which is worth remembering during exercise 3" → "as exercise 3
  will show" (§53 endorsement frame; the clause rated the information instead
  of using it).
- Line 255: "While the use of `match` inside the `next()` methods is
  perfectly reasonable, managing a large number of these could become
  difficult." → "The `match` statements inside `next()` work, but a machine
  with many states means many of them, spread across many classes." (hedges
  in both directions replaced by the concrete point).
- Lines 427-432: the module-shadowing sentence now unpacks into three:
  "Python caches a module in `sys.modules` under its basename, and never
  looks it up again once it is there. Two files named `state_machine.py` in
  one program therefore collapse into one: whichever imported first wins,
  and the second import silently gets the wrong module." (one sentence
  carried the cache, the resolution rule, the collision, and the
  consequence).
- Line 487: dropped "Note that" from "Note that the lookup keys on
  `type(event)` exactly" (the "exactly" stays; the colon spells out the
  precise-match claim it makes).
- Line 828: "states have real behavior" → "states do something" (§34
  real-adjective inflation; nothing named what unreal behavior would be).
- Line 844: "a machine that arrived as a diagram wants the table" →
  "belongs in the table" (watched "wants" on a non-agent, in the chapter's
  last sentence).

Line numbers below refer to the chapter before these edits;
the module-shadowing rewrite added one line, shifting later lines down.

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

## Considered and declined

**Line 391 — "a bug you want flagged."**
"Want" is addressed to the reader, so the rule's carve-out covers it, and the
alternative ("a bug the machine should report") may be a change for its own
sake. Left alone; recorded so a later sweep does not re-raise it.

## Noted, no change

**Line 509 — "The conditions and actions are plain methods."**
"Plain" draws a real contrast here: against the `Condition` and `Transition`
class hierarchies the Java version needed, named a few paragraphs earlier.
The rule's carve-out covers it. Recorded so a mechanical sweep does not cut it.
