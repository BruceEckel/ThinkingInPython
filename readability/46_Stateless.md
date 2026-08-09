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
below is in that new or rewritten prose.

---

**"Emptying the Channels": the new item 3 breaks the list's grammar and its
promise.**

The list is introduced as

> The two halves of this chapter taught two vocabularies:

and now has three items, the third of which opens

> 3. An Ability the driver answers itself needs no vocabulary at all.

So the lead-in counts two, the list holds three, and the third item's content is
that it is not one of the things being counted. The deep review added it to
close a real gap (`Async` is taught for 190 lines and the conclusion never
mentions it), and the gap is worth closing. The seam is the lead-in.

Proposed change: make the lead-in count what follows.

> The two halves of this chapter taught two vocabularies, and a third case that
> needs none:

Alternative, which I prefer slightly less but which leaves the list at two:
drop item 3 and put its content in the paragraph below, where the `Success`
correction already lives, since both are about what `run()` accepts.

> `Async` never appears in either vocabulary. It sits in the Ability channel
> beside a `Need` and is never supplied, because `run()` owns the event loop
> that answers it.

I recommend the first. The numbered form makes `Async` findable by a reader
scanning the conclusion for it, which is the thing the deep review found
missing.

[] Reject

---

**`except_vs_catch.py` follow-up: "The last line is the sharp part" labels the
payoff instead of delivering it.**

> The last line is the sharp part:
> wrapping `guarded()` in a `catch()` makes its inner `except` dead code,

This is §39. The sentence after the colon is concrete and lands on its own; the
label in front of it tells the reader to be impressed first.

Proposed change:

> Wrapping `guarded()` in a `catch()` makes its inner `except` dead code,
> because `catch()` matches the yielded value before the driver gets it
> and abandons the inner generator where it stands.

The paragraph loses six words and no information. Note that the chapter does
this well two paragraphs earlier ("Nothing removed the `KeyError` from the
channel, though, so the signature keeps declaring a failure that can no longer
escape"), which states the surprising thing without announcing it.

[] Reject

---

**`Files` bullet: the extension turns a three-item list of names into two names
and a paragraph.**

> - `Console` in `stateless.console` with `print_line()` and `read_line()` accessors,
> - `Files` in `stateless.files` that reads a whole file,
>   whose accessor is `@throws(FileNotFoundError, PermissionError)`
>   and so declares both channels at once,
> - `Time` that [Adding Behavior to an Existing Effect](47_Stateless_in_Practice.md#adding-behavior-to-an-existing-effect)
>   supplies to `retry()`.

The fact is a good one and the deep review is right that it is the library's own
example of both channels at once. Inside a bullet list of one-line names it
reads as an aside that outgrew its slot, and it forward-references a section
about 550 lines later from the middle of a list.

Proposed change: keep the bullets uniform and put the fact in the sentence after
the list, where the chapter already comments on all three.

> - `Files` in `stateless.files` that reads a whole file,

and after the list's closing sentence:

> `read_file()` is also the library's own example of both channels at once:
> its accessor carries `@throws(FileNotFoundError, PermissionError)` on a
> function that already returns an Effect, so its type declares an Ability and
> two failures together.

That also gives the fact room to say the part the bullet had to drop, which is
that `@throws` is being applied to something that is already an Effect. Every
`@throws` in the chapter proper decorates a plain function, so this is the one
counterexample and it is worth a sentence rather than a subclause.

[] Reject

---

**"The Simplest Effect": the qualified sentence now carries three qualifiers in
one line.**

> Nothing the Effect describes happens until `run()` is called,
> and a synchronous program calls `run()` only once, at its outermost edge.

Both changes were right individually. Together the sentence now has a restrictive
subject ("Nothing the Effect describes"), a restrictive adjective
("a synchronous program"), and a restrictive adverb ("only once"), which is a
lot of hedging for the sentence that states the chapter's central idea for the
first time.

Proposed change: split it, and let the qualification sit in the second sentence
where it does not compete with the main claim.

> Nothing the Effect describes happens until `run()` is called.
> In a synchronous program that happens once, at the outermost edge.

The forward reference to `Where run() Can Be Called` is then unnecessary,
because "in a synchronous program" already signals that another case exists.

[] Reject

---

**"Where `run()` Can Be Called", after the swap: the new opening sentence
assumes the reader remembers `run_async()`, which they now meet later.**

The section now opens

> `run()` answers `Async` because its entire body is `return asyncio.run(run_async(effect))`.

Before the swap, `run_async()` had been introduced two sections earlier. After
the swap it is introduced in this section, about ten lines below this sentence.
So the opening line uses the name it is about to define.

This is the one seam the swap opened, and it is small. The fix is to name the
mechanism before the identifier:

> `run()` starts an event loop and drives the Effect inside it:
> its entire body is `return asyncio.run(run_async(effect))`.
> That has a consequence worth knowing before you incorporate Stateless into an
> existing application.

The reader can then meet `run_async()` properly at the point the section
introduces it, and the sentence still explains why the nested-loop failure
follows.

[] Reject

---

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
