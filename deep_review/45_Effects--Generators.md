When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

# Deep review: chapter 45, The Driver's Exception Channel (2026-11-02)

Scope: the section `## The Driver's Exception Channel` and its four
subsections, after the day's hand edits (the `throw_and_close.py` fold into
`throw_close_basics.py`, the renamed `Stopping Early with close()`).
The correctness pass ran the section's six listings directly from
`build/examples` (all match their markers) and `tip verify-ch CH=45`
(27 of 27), and probed on Python 3.15.1: `close()` returns a value the
generator returns while handling `GeneratorExit` (42 came back); a
different exception raised while handling `GeneratorExit` comes out of
`close()`; `close()` on a `GEN_CREATED` generator runs none of the body and
marks it `GEN_CLOSED`; `throw()` on a `GEN_CREATED` generator raises
without running the body; a reclaimed stubborn generator prints
`Exception ignored while closing generator <...>: RuntimeError: generator
ignored GeneratorExit`; a `yield` inside `finally` draws the same
`RuntimeError` from `close()`. The chapter 15 quotation matches chapter 15
line 117. Prior reviews (`~45...` through `.r4`) hold no `[X] Reject` in
this section; the first review declined an exercise on `throw()`/`close()`
on arc grounds, which stands.

## Applied directly

- **Section opening, motivation before mechanism:** the two paragraphs
  asking why a driver needs `throw()` and `close()` when `raise` exists
  (the generator is off the call stack while the driver runs) sat after
  the first listing's walk. They now sit before `### An Exception at the
  yield`, so the reader meets the reason before the listing.
- **Lead-in to `throw_close_basics.py`:** "Here are the basics of
  `throw()` and `close()`:" was a throat-clearing opener. The "a generator
  body chooses: handle, clean up, or let it end" paragraph, which followed
  the listing, is now the lead-in and ends on the colon; the walk opens
  on "In every run the exception arrives in place of a value".
- **Cut, after the walk:** "`throw()` raises the exception the driver
  passed. `close()` raises `GeneratorExit`. The driver ... calls both
  methods. Inside the generator's body, `raise` works as it does
  anywhere." The bullets and the opening paragraph say the first three;
  `body_raises.py`'s lead-in covers the fourth.
- **Cut, end of the `[2]` walk:** "`GeneratorExit` is the driver's signal
  that this resumption is the last one. It tells the generator to
  finish." The bullet ("plus a rule: the generator must end") and the
  contrast paragraph ("sends one message: finish") carry it.
- **`body_raises.py` walk:** "the exception shut the generator down, as
  `throw()` does" was false for a handled `throw()` (`[1]` leaves
  `worker()` suspended). Now "as the `TypeError` thrown into `worker()`
  in `throw_close_basics.py` did".
- **Stopping Early with `close()`, new sentences:** a generator still at
  `GEN_CREATED` has entered no `try` statement, so `close()` on it marks
  it `GEN_CLOSED` and leaves the body unrun; closing `readings()` before
  its first `next()` leaves the sensor as it was. A reader who has just
  read "the `finally` block runs eventually" would expect cleanup from a
  generator that never ran. Probed.
- **`close()` Requires the Generator to Finish, new sentence:** a `yield`
  inside a `finally` clause draws the same `RuntimeError`, since
  `GeneratorExit` runs that clause on its way out. The near-miss a reader
  writes who knows to avoid `except GeneratorExit: yield`. Probed.
- **Subsection order:** `### close() Requires the Generator to Finish`
  moved ahead of `### Through yield from to the Innermost Generator`. The
  three `close()` subsections now run together (basics, stopping early,
  the rule), the two forward links to the rule point one subsection
  ahead instead of three, and the section ends on the *Saga*, whose one
  generator per step leads into `## One Generator per State`. Anchors are
  unchanged, so no link moved.
- **Prose tools:** `tip positional` flagged "the second `worker()`" in the
  `body_raises.py` sentence above; reworded to name the exception and
  the listing. `tip prose CH=45` otherwise reports 0 new.

## Considered and declined

- **"Python calls `close()` when the garbage collector reclaims the
  generator."** In CPython the usual reclaim is the reference count
  reaching zero, with the cyclic collector a fallback. The sentence uses
  "garbage collector" the way the rest of the book does for any reclaim,
  and the distinction adds nothing to the point (the `finally` block
  runs at an unchosen moment). Left as written.
- **An exercise on `throw()`/`close()`.** Declined by the first review as
  outside the chapter's arc, and nothing in this pass changes that.
- **`throw_through.py` has no tags.** Its walk names each construct once
  (`outer()`'s `yield from`, `inner()`'s `yield`, the two `finally`
  blocks), and each appears once in the listing, so the tag convention
  does not apply.
