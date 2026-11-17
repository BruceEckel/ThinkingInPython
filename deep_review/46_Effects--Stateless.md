> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 46_Effects--Stateless, fourth review (2026-11-17)

This review follows `~46_Effects--Stateless.r3.md` (2026-10-13).
The three earlier reviews checked claims against the Stateless source and
reported no structural finding.
This one is the teaching pass, at Bruce's request: "What can I ask you to do
with this chapter so that it isn't so jumbled and confusing? How can you make
it more pedagogically sound and easier to understand? Do that."

It came after he had flagged 20 sentences in the first 300 lines in one
sitting, two days after a whole-chapter super-prose pass (`2a115633`) had read
15 of the first 17 and kept them.
Those flags and their repairs are in commits `4a441c90` through `ebd6ab21`.
This file records the structural pass that followed, commits `3dcd5715`,
`a5ad1a72`, and the commit that adds this file.

What I did:

- Wrote one line per section, what it assumes and what it introduces, and
  read the two columns down the page.
- Read every section as a reader who knows only what the chapter has said so
  far, and wrote down the question each sentence leaves.
- Checked each claim I touched against the Stateless 0.6.1 source or a probe
  on `ty` 0.0.104: `Depend[A, R]` and `Effect[A, Never, R]` reveal as one type
  (likewise `Try` and `Success`), `Effect[Console, KeyError, None]` draws
  `invalid-type-arguments`, `success(42)` is a `SuccessEffect` that inherits
  from `Generator`, `read_file()` carries `@throws(FileNotFoundError,
  PermissionError)` over `Depend[Need[Files], str]`, and `Time` has one
  method.

`tip verify-ch CH=46` passes 28 of 28, `heading_links` passes over the book,
and `tip exercise-refs` shows no new reference.
The whole-book `tip verify` and `tip grounding-triage` were not run.

## Applied directly

Section order. No anchor changed.

- Built-in Dependencies: moved from between Declaring a Dependency and
  Nothing Runs Yet to just before Supplying an Interface. It interrupted
  declare, inspect, supply with a catalog that pointed forward to test
  doubles and `@throws`. Its point (concrete classes need inheriting
  doubles) is now stated where the next section uses it.
- Layering Handlers and An Effect Runs Once: both stood between Supplying
  the Dependency and Forgetting to Supply, the check the chapter's opening
  promises. Layering Handlers now follows When Two Implementations Match
  (two instances in one `supply()`, then two `supply()` calls). An Effect
  Runs Once now follows Where to Call `run()`.
- New section, A Missing `yield from`, after Retrofitting an Effect. Its
  three paragraphs sat inside Effects Propagate and reasoned about
  `greet_logged()` one section before `audit_log.py` shows it. Effects
  Propagate now holds the listing, the `async` comparison, and the check.
- Catching Is Not Handling: promoted from a subsection of The Error Channel
  to a section after Multiple Errors. `except_vs_catch.py` used `catch()`
  and a `match` on its result before Turning an Error Into a Value taught
  them. The paragraph in that section that compared `catch_score.py` with
  `handler_blocks_except.py` moved with it.

Within sections, in chapter order.

- The Effect Type: "builds everything atop a single type" is "describes
  every Effect with one type". "The three questions [Effect Management]
  asks" named questions chapter 44 never poses; the sentence now ties the
  three parameters to `ZIO`'s three, which that section does describe.
- The Simplest Effect: resequenced in the listing's order (signature,
  body, call), with the new `success_effect.py` listing (`097d0294`).
- Declaring a Dependency: `plain_greet()` and its hidden side effect come
  first, then the `Need` that declares it. The mechanism used to come
  before the problem.
- The Effect Definition: the pointer "[Waiting on a Coroutine] states the
  `A` bound as the rule for `Depend`" gave way to the bound's consequence,
  that the type checker rejects `Effect[Console, KeyError, None]`.
- Why `yield from`: `Need[Log]` is introduced as "a second dependency",
  and the last sentence ties the argument to the second detail it explains.
- Nothing Runs Yet: says what `send(Console())` does. Supplying the
  Dependency opens from it.
- Supplying the Dependency: ends on the subtraction. Three sentences about
  `run()`'s parameter previewed Forgetting to Supply, now the next section.
- Forgetting to Supply: says what happens at runtime before the
  diagnostic; "`Exception` is the error channel ... and everything after
  it" is "covers every failure an Effect declares".
- Swapping the Implementation: a lead-in for `test_greeter.py`; why a bare
  `supply(recorder)` does not answer `Need[Console]`; the closing pointer
  to Supplying an Interface is cut.
- Retrofitting an Effect: opens on the situation before the cross-chapter
  exercise.
- One Effect, Many Environments: says what `holds()` computes; the forward
  pointer to When Two Implementations Match is cut.
- Built-in Dependencies: the `Time` bullet says what `Time` is; the
  `read_file()` note moved to Errors Propagate, beside `announce()`.
- Layering Handlers: two sentences tie it to the section before.
- Dependency Injection: "service locator" is said before the listing that
  is one. The sentence that referred back to `untyped_greet.py` said the
  `print()` version uses a `Console`; it uses none.
- Waiting on a Coroutine: opens on `Async`, with a link back to the
  diagnostic it explains.
- An Effect Runs Once: `throws()` and `catch()` are named as coming in The
  Error Channel; the `memoize()` pointer sentence is folded into a link.
- The Error Channel: "leaves `A` out" is "puts `Never` in `A`'s place";
  "the same channel" is "the yield channel"; Declaring Is Not Handling no
  longer mentions `catch()` before it is introduced.
- Turning an Error Into a Value: introduces `catch()` in its first
  sentence.
- Multiple Errors: a lead-in for the test listing.

After this review was filed, at Bruce's request ("the example here is the
trivial case of a pure function, and I don't think it gives enough context").

- New section, One Effect at a Time, between The Simplest Effect and
  Declaring a Dependency: three minimal listings with one Effect each,
  `side_cause.py`, `side_effect.py`, and `failure.py`, under the new
  subsections A Side Cause, A Side Effect, and A Failure. The Simplest
  Effect now opens by saying `double()` is the trivial case, and its
  closing bridge to Declaring a Dependency is gone. No existing anchor
  changed.

## Blocks

### 1. Should `R` be called "the result channel"?

Your question was "does it not mention the result channel?"
The chapter names two channels, the Ability channel and the error channel,
and calls `R` "the result".
I kept that and added where `R` goes: "The Effect returns its result, of type
`R`, on its return channel."

The other choice is three named channels, as ZIO and Effect in TypeScript
name an error channel and a success channel.
It would read: "This chapter calls `A` the *Ability channel*, `E` the *error
channel*, and `R` the *result channel*."
About five later sentences then need rewording, since "both channels" and
"the two channels" would have three to choose from: "Both channels are
empty", "An Effect with both channels emptied is a `Success`", "So the two
channels guarantee different things", the section title Emptying the
Channels, and chapter 47's opening.

I recommend keeping two.
The two named channels are the ones a handler empties, and the chapter's
argument rests on that pair.
Reject this block to keep two; leave it live and I will make the change to
three.

[] Reject

### 2. `dependency_injection.py` also defines a `greet()`

You asked for `plain_greet()` in `untyped_greet.py` "so it isn't confused
with the previous one".
`dependency_injection.py` defines a `greet(name: str) -> None` for the same
kind of comparison, and its prose tells the two apart by file name:
"`greet()`'s body matches `greeter.py`'s `greet()` line for line".

I left it.
The sentence's point is that the two bodies match, and a shared name supports
it.
If you want the same treatment, the name would be `located_greet()`, changed
in the listing, its two calls, and four sentences.
Reject this block to leave the name; leave it live and I will rename it.

[] Reject

## Considered and declined

- Moving Swapping the Implementation next to Supplying an Interface. The
  first already gives the short answer to "why `as_type()`", and the three
  sections between them are the chapter's second promised check.
- Explaining `Unknown` in the `unsupplied.py` diagnostic. I believe it is
  how `ty` shows `run()`'s unsolved result type, and did not probe it.
- Renaming the file `untyped_greet.py` to match `plain_greet()`. Listings in
  this book are often named for their subject and not their function.
- Changing "implements ... with generators" to "using" in chapters 01 and
  44, after your edit to this chapter's opening. One edit does not settle
  the other two.
- The alias paragraph at the end of Retrofitting an Effect. It is a
  digression, and it is also the chapter's stated reason for writing every
  signature in full.
- Reordering the exercises to follow the new section order. They never
  followed it, and each names its listing.

## For the session

- `tip grounding-triage` needs the API key and was not run. Sentences that
  link another chapter changed in The Effect Type (two links to chapter 44
  and 45), Declaring a Dependency (chapter 11), and chapter 47's opening.
- `tip prose CH=46`: the new hits were read and accepted as keeps, each a
  count followed by its items, a parser misread, or Bruce's own sentence.
- `uv.lock` and `!NOTES.md` are modified in the working tree and were left
  alone.
