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

Every finding was resolved directly: applied (listed below) or declined
with the reason recorded. No blocks remain.

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
- Lines 610-611: "Each section of this chapter replaced a class hierarchy
  with something smaller, and the replacements form one list." → "The
  alternatives this chapter showed form one list." (the *Command* and
  *Strategy* sections show the function first, so they decline to build the
  hierarchy rather than replace it, and the event bus replaces a list; the
  list right after the sentence makes the point on its own).
- Line 337: "The Context earns its keep when something has to hold the
  current algorithm between calls" → "The Context becomes useful when
  something must hold..." (you had the phrase cut from chapter 26's
  conclusion and out of this chapter's `Command` paragraph, so the last
  instance goes for consistency; "has to" is also on the watch list).

Line numbers above refer to the chapter as it stood before these edits.

## Considered and declined

**Line 146 — "Python's best-known closure trap."**
An unsupported superlative by shape, but "best-known" tells the reader this
is the trap they have heard about, which is useful orientation for the
late-binding loop-variable trap, the one closure trap with a reputation.
Left alone; recorded so a later sweep does not re-raise it.

## Noted, no change

**Line 96 — "to say what one list of functions says directly."**
The sharpest sentence in the chapter and the reason the *Command* section
works. Recorded here so a later pass does not "tighten" it.
