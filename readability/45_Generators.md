> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/45_Generators.md`

Second review of this chapter.
The findings in `readability/~45_Generators.md` were all accepted and applied,
and none were rejected, so nothing is carried forward. The earlier review's
theme was interpretive metadiscourse; that pattern is gone from the prose it
flagged, and the findings below are different in kind.

The deep review that ran just before this one added `manual_forwarding.py`,
moved the threading paragraph to the end of "A Generator Is a Description",
rewrote the sentence that opens the chapter's central argument, added a
laziness sentence to "Running to Exhaustion" and a `throw()`/`close()` sentence
to "Composing Is Not Interpreting", and reshaped `drive()` so it looks its
answer up once. That last change rewrote ten `#:` marker lines across three
listings.

---

**"A Generator Is a Description": the rewritten opening sentence now makes a
claim the paragraph above it contradicts.**

> A generator is the more useful of the two here because you can be its driver.

The paragraph immediately above establishes that a coroutine and a generator
have the same three-part shape and that both are descriptions something else
drives. The new sentence then says the generator is more useful because you can
drive it, which reads as though a coroutine cannot be driven. It can: the
chapter's own conclusion says a coroutine offers `send()`, and `asyncio.run()`
is a driver.

The distinction the deep review was reaching for is not *whether* you can drive
it but *who* does. With a generator, the driver is code you write, and it
decides what each request means. With a coroutine, the requests are addressed
to an event loop you did not write and cannot reinterpret.

Proposed change:

> A generator is the more useful of the two here because the driver can be
> yours.
> A coroutine's requests are addressed to the event loop; a generator's are
> addressed to whatever code calls `send()`.
> The generator yields a value out, and the caller sends a value back in.

That keeps the deep review's improvement (dropping "more interesting") and
makes the comparison land on the real difference, which the chapter's
conclusion then cashes in.

[] Reject

---

**`manual_forwarding.py` follow-up: the explanation is correct and arrives in
the wrong order.**

> `manual()` forwards what it receives from `collect()` and nothing in the other direction.
> Each `send()` delivers its value to `manual()`'s own `yield`, which throws it away,
> and the `for` loop resumes `collect()` with `next()`,
> so both of `collect()`'s `yield` expressions produce `None`.
> The checker says nothing: `manual()` is a valid `Generator[str, int]`.
> `yield from` is not shorthand for this loop, and the difference is the send channel.

The reader's question at this point is "why did it print `None and None`?" The
answer is in the second sentence, but the first sentence is an abstract summary
of that answer, so the paragraph states its conclusion, then derives it, then
restates it in the last line. Three of the five sentences carry the same claim
at different altitudes.

Proposed change:

> Each `send()` delivers its value to `manual()`'s own `yield`, which throws it away.
> The `for` loop then resumes `collect()` with `next()`,
> so both of `collect()`'s `yield` expressions produce `None`.
> The checker says nothing, because `manual()` is a valid `Generator[str, int]`:
> the send channel is declared and simply never used.
> `yield from` is not shorthand for this loop.

This leads with the mechanism, keeps the checker point (which is the finding a
reader could not get from the output), and ends on the one-line moral without
the abstract opener.

[] Reject

---

**"Composing Is Not Interpreting": the new `throw()`/`close()` sentence
introduces two methods the chapter never otherwise mentions.**

> `yield from` relays `throw()` and `close()` the same way,
> so an exception thrown at the driver surfaces inside the innermost generator,
> and a `close()` unwinds every frame in the chain.

This was added to make chapter 23's forward reference true, which it does. But
a reader meeting `throw()` for the first time in a subordinate clause gets no
sense of what throwing at a generator means or why anyone would, and the
sentence assumes they know `close()` raises `GeneratorExit`.

Two ways to fix it, and I do not have a strong preference.

The cheap one is to say what the methods are as you name them:

> A driver can also `throw()` an exception into a generator or `close()` it,
> and `yield from` relays both:
> a thrown exception surfaces inside the innermost generator rather than at the
> delegating one, and a `close()` unwinds every frame in the chain.

The other is to leave the sentence alone and accept that these two are named
but not taught, on the grounds that the chapter is already long and the reader
who needs them will look them up. The deep review considered a full subsection
with a listing and rejected it as too much for the payoff, which I agree with.

I lean toward the cheap fix, because "relays them the same way" is doing all
the work in a sentence whose subject the reader may not know.

[] Reject

---

**"Running to Exhaustion": the new laziness sentence uses a definition-style
colon in a section that has three other colons doing different jobs.**

> "Exhausted" describes where the delegation ends, not when it happens:
> each value still leaves the inner generator only when the driver asks for the next one.

The sentence is a good addition and fixes a real misreading. The colon is the
weak part: what follows is not a definition, a list, or a quote, but a second
independent claim, so the colon is standing in for "because" or a period.

Proposed change:

> "Exhausted" describes where the delegation ends, not when it happens.
> Each value still leaves the inner generator only when the driver asks for the
> next one.

Two sentences also lets the second one carry the weight it deserves, since it
is the claim the reader has to hold through the next three sections.

[] Reject

---

## Checked and clean

- Zero hits across the §7 Tier 1A, 1B, 2, and 3 vocabulary tables in the new
  prose.
- `banned_phrases.py` and `prose_lint.py` both pass on the chapter.
- No em dashes, no spaced ` -- `, no curly quotes, no boldface, no emojis, no
  slot-fill placeholders.
- The threading paragraph reads better at the end of its section than it did in
  the middle, and its move left no dangling reference: the sentence before it
  ("The generator declares Effects, the driver interprets them") ends the
  argument cleanly, and the paragraph opens with its own subject rather than a
  connective.
- The ten rewritten `#:` markers were checked against the reshaped `drive()`.
  All three listings now print `answer = ` and the chapter quotes none of those
  strings in prose, so nothing else needed updating.
- Exercise 2's new clause ("`StopIteration` now means two different things in
  the same loop; keep them apart") uses a semicolon between two tightly linked
  independent clauses, which the style rules allow. It is also an instruction to
  the reader, so the imperative is correct rather than the banned
  imperative-plus-consequence shape.
- `manual_forwarding.py` duplicates `collect()` rather than importing it. The
  deep review explains why (importing `yield_from_send.py` would print its
  module-level demo into this listing's output), and the duplication is six
  lines. Worth knowing it is deliberate if a later pass flags it as drift.
