[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

**"The Send Channel": the chapter's biggest missing near-miss is the
hand-written forwarding loop, and chapter 23 already promised it lives here.**

`Chapters/23_Iterators.md` says, of `flatten_loop()` versus `flatten()`:

> The hand-written loop drops that value.
> `yield from` also forwards `send()` and `throw()` into the inner generator,
> which the loop cannot do.
> [Generators](45_Generators.md#yield-from-composes-descriptions)
> works all three channels.

Chapter 45 works all three channels, but never shows the loop failing. It
comes closest at "`both()` contains no code that forwards the value because
`yield from` does that forwarding," which states the fact and leaves the
reader to imagine the alternative. The alternative is exactly what a reader
writes when they have not met `yield from`, and its failure is silent: the
sent values vanish and the inner generator sees `None`.

Verified listing (ruff clean at 70, `ty` clean, output below is the actual
run):

```python
# manual_forwarding.py
from collections.abc import Generator

def collect(name: str) -> Generator[str, int]:
    first = yield f"{name} needs a value"
    second = yield f"{name} needs another"
    print(f"{name} got {first} and {second}")

def manual() -> Generator[str, int]:
    for prompt in collect("alpha"):  # noqa: UP028
        yield prompt

g = manual()
print(next(g))
#: alpha needs a value
try:
    for value in [1, 2, 3]:
        print(g.send(value))
except StopIteration:
    print("manual() is exhausted")
#: alpha needs another
#: alpha got None and None
#: manual() is exhausted
```

Suggested prose under it:

> `manual()` forwards what it receives from `collect()` and nothing in the
> other direction.
> Each `send()` delivers its value to `manual()`'s own `yield`, which throws
> it away, and the `for` loop resumes `collect()` with `next()`, so both of
> `collect()`'s `yield` expressions produce `None`.
> The checker says nothing: `manual()` is a valid `Generator[str, int]`.
> `yield from` is not shorthand for this loop, and the difference is the send
> channel.

Placement: after "`both()` contains no code that forwards the value because
`yield from` does that forwarding," which is where the claim is made. That is
your call, hence reported.

Two details worth knowing before you place it. The `# noqa: UP028` matches
`flatten_loop()` in chapter 23, which carries the same suppression for the
same rule, and 23's prose already explains what UP028 is, so this listing does
not need to. And `collect()` is duplicated rather than imported because
`yield_from_send.py` runs its demo at module level with no
`if __name__ == "__main__"` guard, so importing it would print that demo into
this listing's output. The alternative is to add a guard to
`yield_from_send.py`, which would need its interleaved column-0 `#:` markers
to sit inside an indented block; duplicating six lines is the smaller change.

[] Reject

---

**Exercise 2 sets a silent trap the chapter does not arm the reader for.**

> `drive()` answers from a `dict`.
> Write a second driver that answers from an `Iterator[Answer]`, in order,
> and run `interview()` under both.

The natural adaptation puts `next(answers)` where `answers[request]` was. If
the answer source runs short, its `StopIteration` is caught by the driver's
own `except StopIteration`, which reads it as "the conversation finished" and
returns `stop.value`. I ran it: the driver returns `None`, typed `Result`, and
`ty` reports nothing, because `StopIteration.value` is `Any`.

Two of this pass's applied edits point at that already (only `send()` now sits
inside the `try`, and the prose says why `StopIteration` from anywhere else
must stay outside), so a reader who copies the current `drive()` is fine. A
reader who writes their own from the description is not.

Proposed addition to exercise 2, after "and run `interview()` under both":

> Give your driver fewer answers than there are questions and say what it
> returns.
> `StopIteration` now means two different things in the same loop; keep them
> apart.

That turns the trap into the exercise's point, which suits it: the exercise's
existing question ("explain what had to change in `interview()`") has the
answer "nothing," so the exercise currently has one insight and room for a
second.

[] Reject

---

**Chapter-level structure: the order holds, with one local exception.**

I wrote the assumes/introduces columns for every section and read them down
the page. Nothing later appears in an earlier "assumes" column:

| Section | Assumes | Introduces |
| --- | --- | --- |
| Annotating a Generator | `Iterator[T]` (ch23), `NewType` | `Generator[Y, S, R]`, `send()`, `StopIteration.value`, priming, frame-as-state |
| A Generator Is a Description | ch44's coroutine-is-a-description, the above | the driver loop, EMS in miniature |
| Running to Exhaustion | generators | `yield from`, transitivity |
| The Return Channel | `yield from`, `ReturnType` | `yield from` as an expression |
| The Send Channel | `yield from`, `SendType` | forwarding two levels down |
| All Three Channels | all of the above | delegation carrying all three |
| Composing Is Not Interpreting | all of the above | the driver/delegation distinction |
| The Driver You Already Use | ch19's `await` | `asyncio` as the same mechanism |

The claim ("a generator is a two-way description, and `yield from` composes
descriptions without any of them learning who drives") is moved forward by
every section, and each transition has a real reason rather than "also about
generators." Motivation precedes mechanism, and the payoff is previewed in the
intro rather than held to the end. So no reordering is proposed.

The one exception is the threading paragraph in "A Generator Is a
Description":

> One generator, one driver.
> Nothing states that pairing, but the runtime protects it: ...
> [Concurrency](19_Concurrency.md#sharing-an-iterator-between-threads) ...

It sits between the coroutine parallel and the `drive()` listing, and it is
the only paragraph in the chapter about a failure mode the chapter never uses
again. A reader arriving at "A generator is more interesting than a coroutine
here" has just been detoured through `ValueError` and
`synchronized_iterator()`. Moving it to the end of that section, after
"That is EMS in miniature," would keep the coroutine-to-driver line
unbroken and let the aside close the section rather than interrupt it.
Cost: nothing. No anchor changes, no other chapter names it, and the ch19
link travels with the paragraph. Reported rather than applied because moving
a paragraph is pacing.

[] Reject

---

**"Running to Exhaustion": `list()` hides that `yield from` is lazy, and the
section title invites the wrong reading.**

The section is called "Running to Exhaustion" and says "Each `yield from` runs
its target until that generator is exhausted." Both listings are wrapped in
`list()`, so the only evidence a reader has is a finished list. Nothing in the
section rules out the reading a beginner will actually form: that
`yield from one()` runs `one()` to completion at that moment and buffers the
result, and that `list()` merely displays it.

The chapter needs that reading gone before "Composing Is Not Interpreting,"
whose whole argument is that a value leaves the innermost generator and
travels to the driver one at a time.

Cheapest fix, one sentence after "The number of contributions is a property of
the target." (which now also carries the `yield one()` near-miss line applied
in this pass):

> "Exhausted" describes where the delegation ends, not when it happens:
> each value still leaves the inner generator only when the driver asks for
> the next one.

Fuller alternative: replace `print(list(top()))` with a loop that prints each
value as it arrives, interleaved with a `print()` inside `one()`, so the trace
shows the alternation instead of the totals. That teaches the mechanism rather
than asserting it, at the cost of a longer listing in the chapter's simplest
section. I recommend the sentence.

[] Reject

---

**"The Driver You Already Use": `throw()` and `close()` appear for the first
and only time in the conclusion.**

> A coroutine object offers `send()`, `throw()`, and `close()`,
> as a generator does.

Neither is taught anywhere in the chapter, and neither appears in 46 or 47
(I grepped both for `.throw(`, `.close(` and `GeneratorExit`: no hits). So the
sentence asks the reader to accept a parallel with two constructs they have
not met. Chapter 23 makes it worse by name: it tells the reader that
`yield from` forwards `throw()` "which the loop cannot do" and sends them to
this chapter's `yield from` section to see all three channels.

Three ways out, in increasing cost:

1. **Drop the two names from the conclusion**: "A coroutine object is driven
   by `send()`, as a generator is." The sentence loses nothing it was using,
   and chapter 23's forward pointer becomes the only loose end.
2. **One sentence in "Composing Is Not Interpreting"**, where the relay
   argument already lives: "`yield from` relays `throw()` and `close()` the
   same way, so an exception thrown at the driver surfaces inside the
   innermost generator and a `close()` unwinds every frame in the chain." That
   closes 23's thread without a listing.
3. **A short subsection with a listing** showing `g.throw()` landing inside
   `collect("alpha")` and `g.close()` raising `GeneratorExit` there. This is
   the honest treatment of "all three channels plus the two exceptional ones,"
   but it adds a section to a chapter that currently earns every one it has.

I recommend 2. It is one sentence, it sits where the reader is already
thinking about relaying, and it makes chapter 23's cross-reference true.

[] Reject

---

**Cross-file: `Chapters/23_Iterators.md:354-357` promises more than chapter 45
delivers.**

> `yield from` also forwards `send()` and `throw()` into the inner generator,
> which the loop cannot do.
> [Generators](45_Generators.md#yield-from-composes-descriptions)
> works all three channels.

Chapter 45 works the three channels named in the annotation (yield, send,
return) and never mentions `throw()`. A reader who follows that link to see
`throw()` forwarded does not find it. Whichever fix you take for the
`throw()`/`close()` block above resolves this; if you take option 1 (drop the
names from 45's conclusion), then 23's sentence should drop "and `throw()`"
instead. I did not touch chapter 23, per the scope rules.

[] Reject

---

**Exercises: no `Solutions/45_Generators.md` exists.**

`Solutions/` holds `47_Stateless_in_Practice.md` but nothing for 44, 45 or 46,
and `README.md:104` marks `45_Generators.md` 🔴🔴. Seven exercises, none
answered. Exercises 3 and 4 in particular ask the reader to predict output and
compare a checker's verdict against a run, which are the two kinds a reader
cannot self-grade with confidence.

Flagging it rather than writing it: `Solutions/` is outside the files I may
touch, and the seven answers are a chapter-sized piece of work in their own
right. Worth knowing that exercise 4's answer changed in this pass (see the
manifest): the annotation now stays on `profile`, so the checker reports one
`invalid-assignment` and the run prints `<generator object interview at ...>,
color blue`.

[] Reject

---

**`two_way_generator.py`: `drive()` looks the answer up twice, and the
single-lookup form is the one exercise 2 needs.**

Applied in this pass (output unchanged): the `print()` moved out of the `try`,
so only `conversation.send()` sits under `except StopIteration`. That is the
minimal correct version. The fuller version also removes the double lookup:

```python
def drive(conversation: Generator[Question, Answer, Result],
          answers: dict[Question, Answer]) -> Result:
    request = next(conversation)
    while True:
        answer = answers[request]
        print(f"{request = }, {answer = }")
        try:
            request = conversation.send(answer)
        except StopIteration as stop:
            return stop.value
```

Why it matters beyond tidiness: exercise 2 asks the reader to write a second
driver that answers from an `Iterator[Answer]`. They will adapt this loop, and
`answers[request]` becomes `next(answers)`. With the current shape that is two
`next()` calls per question, consuming the answers twice as fast as intended;
with a local variable it is one. The model the chapter hands them should be
the one that survives the substitution.

Cost, which is why this is reported rather than applied: the `#:` markers
change from `answers[request] = 'Alice'` to `answer = 'Alice'` in three
listings, ten marker lines in total — `two_way_generator.py` (3),
`yield_from_delegates.py` (3), `yield_from_nested.py` (4). No prose quotes
those strings, and `Chapters/47_Stateless_in_Practice.md:132` names the file
but not its output, so nothing outside this chapter moves. I verified the
rewritten loop runs and type-checks; only the marker text differs.

Alternative if you want to keep the markers byte-identical: leave `drive()`
as it now stands and add one clause to exercise 2 warning that the answer
source is consumed once per question. Cheaper, but the reader still copies a
double lookup.

[] Reject

---

**Cross-file: `CLAUDE.md`'s two chapter-45 trap entries are misfiled, and one
of them re-verifies clean on ty 0.0.65.**

Both entries name ch45, but after the Generators/Stateless split neither
subject is in chapter 45 any more:

1. *"A PEP 695 `type` alias as a generator's return annotation disables `ty`'s
   invalid-yield check (0.0.63) ... Chapter 45 wraps long Effect signatures
   across lines instead of aliasing them, and warns the reader."*
   Chapter 45 contains no Effect signature, no `Depend`, no `Need`, and no
   `type` alias. The warning lives at
   `Chapters/46_Stateless.md:664-673` ("The repeated union invites a `type`
   alias ... Write Effect signatures out in full until your checker proves
   that it sees through the alias"), and the wrapped five-way union is at
   `Chapters/47_Stateless_in_Practice.md:1325`.

   I re-ran the probe on the installed **ty 0.0.65**: the limitation still
   holds. A generator whose return annotation is spelled out, or is an
   old-style `X: TypeAlias = Generator[...]`, gets `error[invalid-yield]` on a
   wrong `yield`; the identical annotation behind `type X = Generator[...]`
   produces zero diagnostics. So 46's warning is current, not stale, and the
   don't-clean-these-up instruction should keep pointing at 46 and 47.

2. *"higher-order union subtraction starting to work (ch45's documented
   limitation was half-obsolete)."*
   That documented limitation no longer exists anywhere in 45, 46 or 47. I
   grepped all three for "limitation", "subtract", "cannot subtract" and
   "higher-order": 46 and 47 discuss subtraction only as the thing `handle()`
   does correctly, and 45 never mentions it. Whoever fixed the text after
   0.0.63 removed the caveat and left the trap entry behind.

Change I would make in `CLAUDE.md`: retarget entry 1 at chapters 46/47 and
note it was re-confirmed on 0.0.65, and delete entry 2 or shorten it to the
version-history fact ("0.0.63 made higher-order union subtraction work; the
caveat it invalidated has already been removed from the text"). I did not
touch `CLAUDE.md`, per the scope rules.

[] Reject

---

**"A Generator Is a Description," first line of the third paragraph:
"more interesting than a coroutine" is not quite the difference.**

> A generator is more interesting than a coroutine here because `yield` is a
> two-way channel.

A coroutine object has `send()` too, and its annotation
(`Coroutine[YieldType, SendType, ReturnType]`) has just been shown to have the
same three-part shape. So "because `yield` is a two-way channel" does not
separate the two, and a reader who noticed the shape two paragraphs earlier
will feel the argument slip.

The real difference is who gets to be the driver. With a generator, your own
code reads the request and decides the answer. With a coroutine, `await`'s
requests are addressed to the event loop, which is the point the conclusion
makes ("`asyncio.run()` is the single interpreter at the edge of the
program"). Suggested replacement:

> A generator is the more useful of the two here because you can be its
> driver.
> The generator yields a value out, and the caller sends a value back in.

That drops "more interesting than a coroutine" and lets the existing next
sentence carry the two-way point, which it already does. Reported rather than
applied because it rewrites the sentence that opens the chapter's central
argument, and the phrasing is yours.

[] Reject

---

**MANIFEST, not a proposal: everything applied to
`Chapters/45_Generators.md` in this pass.**

All of the below re-verified together: `validate_output.py --tree` 1 ok,
`ruff check` clean at 70, `ty check` clean on ty 0.0.65,
`heading_links.py` OK, `banned_phrases.py` clean, `reflow_prose.py --diff`
reports 0 paragraphs. No heading was renamed, so the four inbound anchors
(`#annotating-a-generator`, `#a-generator-is-a-description`,
`#the-return-channel`, `#yield-from-composes-descriptions`, referenced from
16, 23, 46 and 47) are intact. Prose targets checked by reading: the chapter
contains no use of the "promise" metaphor and no "reach for", before or after
these edits, and I removed the one promise-family word it had ("guarantee",
item 6 below).

1.  Intro: "but nothing here is specific to that library" → "but nothing here depends on it"; "that library" had no antecedent, since no library is named until chapter 46.
2.  "Annotating a Generator," lead-in to `generator_defaults.py`: "An `Iterator` is the simplest form of a `Generator`:" → "A generator that only produces values can use either form:"; the original states the subtype relation backwards (`Generator` is the subtype of `Iterator`, not the reverse).
3.  Same section, after the listing: "`Iterator[int]` says the same thing" → "describes the same one-way generator and reads better, at the cost of saying nothing about the other two channels: a checker rejects `send()` on anything annotated `Iterator`." Verified: ty 0.0.65 gives `unresolved-attribute: Object of type Iterator[int] has no attribute send`.
4.  Same section, after "the `Result` arrives as that exception's `value`": added three lines stating that a `for` loop catches and discards the `StopIteration` along with its `value`, so getting at the `ReturnType` means catching the exception yourself.
5.  Same section: "The first call made on a new generator object must be `next()`" → "The first call on a new generator object cannot carry a value"; the old absolute is contradicted ten lines later by the `send(None)` equivalence. Added the actual message: `TypeError: can't send non-None value to a just-started generator`.
6.  "A Generator Is a Description": "That pairing is an assumption, not a guarantee, and a generator resumed from two threads at once raises a `ValueError`" → "Nothing states that pairing, but the runtime protects it: ... raises `ValueError: generator already executing`". The old "and" read as if the absent guarantee caused the failure; the runtime is what prevents interleaving. Message verified on the pinned 3.15 build.
7.  Same section, after `two_way_generator.py`: new paragraph explaining the previously unexplained first output line (`<class 'generator'>: interview`) and the previously unexplained second `# type: ignore` in the chapter, one paragraph after the chapter makes a point of the first one. Verified: removing it gives `unresolved-attribute: Object of type Generator[...] has no attribute __name__`.
8.  `two_way_generator.py`: moved `print(f"{request = }, {answers[request] = }")` out of the `try`, so only `conversation.send()` can have its `StopIteration` caught. Output and `#:` markers unchanged.
9.  Same section: new lines saying why only `send()` is inside the `try` and that any other code that could raise `StopIteration` belongs outside.
10. Same section: new lines recording that only two of the three type parameters are actually checked, because `StopIteration.value` is typed `Any`. Verified with `reveal_type(stop.value)` → `Any`, and by returning it into a declared `int` with no complaint.
11. "Running to Exhaustion": added the bare-`yield` near miss, "`yield one()` would hand the generator object itself to the driver as one value." Verified: `['start', <generator object one at 0x...>, 'end']`.
12. "The Send Channel": "A generator that only receives values needs no `ReturnType`" → "A generator that receives values but produces no final result needs no `ReturnType`"; `collect()` both yields and receives, so "only receives" describes nothing in the listing.
13. Same section: "so the return signature becomes `Generator[str, int]`" → "so the annotation shortens to `Generator[str, int]`"; a return signature is not a thing this book names elsewhere.
14. "All Three Channels": "A request raised two frames down" → "A request yielded two frames down", and "interprets Effects raised anywhere inside it" → "Effects yielded anywhere inside it". Effects travel out by `yield` here; "raised" was the only place in the book that borrows the exception verb for them, and this chapter has real `raise`/`StopIteration` traffic to confuse it with.
15. Exercise 4: "leaving `profile = interview()`" → "leaving `profile: Result = interview()`". Verified both ways: with the annotation, ty reports one `invalid-assignment` and the script prints the generator's repr, which is the "explain both results" the exercise asks for; without it, ty says "All checks passed!", so the exercise's own closing question ("what would the checker have said if `profile` carried no annotation?") is asking about the state it just put the reader in.
16. Ran `tools/reflow_prose.py --write` on the chapter so the new prose matches Semantic Line Breaks; it rewrapped two paragraphs and now reports clean.
</content>
</invoke>

[] Reject
