# Adversarial review: the undecided queue

The application pass (2026-09-03) applied 213 of the review's 252
findings and declined one with a contra-reproduction. Of the 38
author-level calls originally queued here, 37 were approved and
performed on 2026-09-03 (the perform-queue commits). One remains,
because only the author can supply it. When it is resolved, archive
this file beside `archive/~adversarial_review.md`.

The one declined finding, recorded so no later pass re-proposes it:
chapter 32's suggestion to type `duel()` with a `Protocol` fails
against the real call shape (`item_pair_gen(Item, n)` types the pair
as base `Item`, which declares no `compete()`; `ty` rejects the
Protocol version with `invalid-argument-type`). The `Any` is
deliberate and the nearby prose already explains the trade.

## Chapter 01 (Introduction)

- **The strongest pro-book AI-era argument is asserted, not shown.**
  "The knowledge in this book has helped me guide AIs toward better
  solutions" now closes the AI section, but it is still one
  unsupported sentence. It needs a real anecdote only Bruce has: one
  concrete case where book-level Python judgment steered an AI to a
  better solution (a prompt that went wrong until the author applied
  judgment the book teaches). A short paragraph there would do more
  work than anything else in the section.
