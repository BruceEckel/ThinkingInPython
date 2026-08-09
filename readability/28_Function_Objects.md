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

The clear-cut fixes were applied to the chapter directly (listed below);
the blocks that remain are the ones needing your judgment.

## Applied directly

- Line 27: "the action is just a function" → "the action is a function"
  (empty adverb, and it repeated line 98's opening; line 98 keeps its "just,"
  where the word answers *GoF* calling commands "an object-oriented
  replacement for callbacks").
- Line 144: "when the commands also want shared implementation" → "when the
  commands also share implementation" (watched "want" applied to code).
- Line 438: "A handler is trusted to know when it failed" → "The chain trusts
  each handler to know when it failed"; "only as reliable as its handlers" →
  "no more reliable than its handlers" (subjectless passive hiding the actor;
  drops a watched "only").
- Line 616: "when that configuration wants a name and a `repr`" → "needs a
  name and a `repr`" (watched "want"; lines 598 and 629 address the reader,
  so their "want"s stay).

Line numbers below refer to the chapter as it stood before these edits
(none of the edits changed line counts).

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

**Line 337 — "earns its keep"**
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

**Line 146 — "best-known"**
**Pattern:** unsupported superlative

Current:
> Building commands in a loop springs Python's best-known closure trap:

"Springs" is the right verb for a trap and reads well.
"Best-known" is an unsupported superlative, and the sentence loses nothing
without it:
> Building commands in a loop springs Python's closure trap:

Low confidence: "best-known" tells a reader this is the trap they have heard
about, which is useful orientation. Reject if you read it that way.

[] Reject

***

## Noted, no change

**Line 96 — "to say what one list of functions says directly."**
The sharpest sentence in the chapter and the reason the *Command* section
works. Recorded here so a later pass does not "tighten" it.
