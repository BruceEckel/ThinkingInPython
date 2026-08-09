> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/46_Stateless.md`

Second review of this chapter.
The findings in `readability/~46_Stateless.md` were all accepted and applied,
and none were rejected, so nothing is carried forward.

The deep review that ran just before this one swapped "Where `run()` Can Be
Called" and "Waiting on a Coroutine", added `except_vs_catch.py`, added a third
numbered item and a correction to the conclusion, extended the `Files` bullet,
loosened the instant-clock assertion, and rewrote four sentences. Every finding
was in that new or rewritten prose.

Every finding cleared the direct-application bar, so this run leaves no
blocks: the fixes are listed for the record, and the `git diff` is the place
to veto any of them.

## Applied directly

- "Emptying the Channels" lead-in: "The two halves of this chapter taught two
  vocabularies:" → "...taught two vocabularies, and a third case that needs
  none:" (the list holds three items and the third's content is that it is
  not one of the two being counted; the numbered form stays because it makes
  `Async` findable by a reader scanning the conclusion).
- `except_vs_catch.py` follow-up: cut the §39 label "The last line is the
  sharp part:" and let the concrete sentence open the paragraph ("Wrapping
  `guarded()` in a `catch()` makes its inner `except` dead code, ...").
- `Files` bullet: restored to one line ("`Files` in `stateless.files` that
  reads a whole file,") and its fact moved below the list's commentary as its
  own paragraph: "`read_file()` is also the library's own example of both
  channels at once: its accessor carries `@throws(FileNotFoundError,
  PermissionError)` on a function that already returns an Effect, so its
  type declares an Ability and two failures together." (the bullet aside had
  outgrown its slot, and the paragraph can say the part the bullet dropped:
  every other `@throws` in the chapter decorates a plain function).
- "The Simplest Effect": "Nothing the Effect describes happens until `run()`
  is called, and a synchronous program calls `run()` only once, at its
  outermost edge." → two sentences, with the qualification second ("In a
  synchronous program that happens once, at the outermost edge."), so three
  stacked qualifiers no longer compete with the chapter's central claim.
- "Where `run()` Can Be Called" opening: "`run()` answers `Async` because
  its entire body is..." → "`run()` starts an event loop and drives the
  Effect inside it: its entire body is..." (the swap moved `run_async()`'s
  introduction below this line, so the old opening used a name it was about
  to define).

## Checked and clean

- Zero hits across the §7 Tier 1A, 1B, 2, and 3 vocabulary tables in the new
  prose.
- `banned_phrases.py` and `prose_lint.py` both pass on the chapter.
- No em dashes, no spaced ` -- `, no curly quotes, no boldface, no emojis, no
  slot-fill placeholders.
- "Type checking is the earliest practical time to discover these errors"
  replaced "the optimal time". The new version is both plainer and true of the
  chapter's own position, and "these errors" narrows the claim to the ones the
  next sentence assumes. Clean.
- The conclusion's `Success` correction ("`run()` accepts more than that") was
  checked against the two sections it cites. Both say what the correction says,
  so the conclusion no longer walks them back.
- The new `default_console.py` lead-in ("This `Console` carries a tag so the
  output says which handler answered") was checked against the five-`Console`
  problem the deep review raised. It names the distinguishing feature at the
  point of introduction, which is what that finding asked for.
- Exercise 11 and its solution were checked against each other. The exercise
  asks the reader to show the ambiguity becoming a type error, and the solution
  produces a real `ty` diagnostic rather than asserting one. The solution also
  records the honest limit (distinct names fix cross-ability ambiguity, not two
  implementations of one ability), which the exercise does not ask for and the
  section's advice needs.
