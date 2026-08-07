# Readability review notes

This file is yours. Nothing here is read as instructions by a review run.

Use it for whatever is useful across reviews: standing exceptions, patterns you
have decided not to care about, chapters you want re-run, and so on.

## How the review files work

- `readability/NN_Name.md` is an active review, one per chapter, findings in
  reading order.
- Each finding block starts with `[] Reject` on its own line.
  Leave the box empty to accept the change.
  Put an `X` in it, `[X] Reject`, to decline it, and leave the block in place
  as a record, so a later review does not re-propose it.
- Hand a file back with `do readability/NN_Name.md` to apply the live blocks.
  The file is then renamed with a leading `~` to mark it done.
- A `~`-prefixed file is a completed review and is left alone.
