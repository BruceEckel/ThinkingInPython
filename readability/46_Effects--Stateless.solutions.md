> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Stateless, Solutions

The 2026-10-16 readability sweep of the chapter 46 Solutions file found
no cluster of AI tells: no Tier 1A or Tier 2 vocabulary, no signposting,
no significance inflation, no generic closers, and no curly quotes.
Most of the fifteen changes below split an "and" that joined two clauses
whose relation is a contrast or a consequence. The rest correct one hint
that told the reader to pass `supply()` a class, fix a colon that
delivered two clauses, and rewrap paragraphs an earlier edit had left
with broken lines.
The claims beside the edits were checked against the listings and the
chapter: `audit_log.py`'s `Log` is a `@dataclass` and its `Console`
comes from `greeter.py` as a concrete class, `supply()` takes instances,
three implementations put `Terminal` first in two of six orderings, and
the When Two Implementations Match section names ZIO's compile-time check.
This file holds no live block, so it is the record of the direct edits.
`tip verify-ch CH=46 ISOLATED=1` passed after the edits (27 of 27).

## Applied directly

- L19 (exercise 1 hint), accuracy: "pass `supply()` a scripted class ... pass it a class wrapping `input()`" -> "a scripted object ... an object wrapping `input()`". The listing passes `Scripted("Alice")`, an instance.
- L87-88, wrap: an overlong line rewrapped at about 70 columns.
- L94, and-split (contrast): "changed which classes qualify, and `supply()` still picks among them the same way" -> two sentences.
- L103, and-split (two claims, different subjects): "the wrapper returns the same `scripted` object, and `supply()` still finds it" -> two sentences.
- L419-425, and-split (consequence) plus wrap: "`Log` is a shape, and a single `Recorder` can have that shape" -> "`Log` is a shape, so a single `Recorder` can have that shape"; the paragraph, with "As a" stranded alone on a line, rewrapped.
- L587-588, wrap: the broken lines around "The handler answers the `Clock` request too" rewrapped.
- L636, and-split (contrast): "`default_console.py` supplies one prepared instance, and `default()` builds whatever the request names" -> two sentences.
- L707-709, and-split (consequence) plus figure: "and the `Need[Console]` request inside the body goes with the Effect" -> "so the body never yields its `Need[Console]` request". The "never" is the claim (exercise 7's whole point is the request that does not happen).
- L751-753, colon delivering two clauses: "has the wrong type: a `Generator` rather than a `Console`, and generators have no `print()`" -> "has the wrong type, a `Generator` rather than a `Console`. Generators have no `print()`."; broken wrap fixed.
- L875, and-split (contrast): "Retrying means running the same work more than once, and an Effect supplies one run" -> two sentences.
- L890-891, wrap: "It also" stranded at a line end; rewrapped.
- L979-983, and-split (contrast) plus wrap: "when its requirements differ, and here all three delegations request `Async`" -> "when its requirements differ. Here all three delegations request `Async`".
- L985, and-split (contrast): "`run()` raises a `RuntimeError`, and `await run_async(...)` works" -> two sentences.
- L1123, and-split (contrast): "The declaration says the failure can occur, and `catch()` turns it into a value" -> two sentences.
- L1225, and-split (partition): "send the greeting to the screen, and the remaining four split evenly" -> two sentences.

## Considered and declined

- L151, "declare `Need[Console]` itself": the reflexive "itself" is load-bearing; it contrasts the caller declaring the need with the caller supplying a `Console`.
- L174, "The fix is the annotation, and only the annotation:": the repetition is deliberate rhythm, and the "only" restates the exercise's own constraint.
- L199-201, "`greet_all()` did the right thing all along. Its signature described a different function.": past tense for the pre-fix listing, a state the exercise points at.
- L327-328, "Both functions have handled every error ... Only `all_handled()` has interpreted what it caught.": a sentence-initial "Only", ruled fine, and the contrast is the paragraph's claim.
- L433-437, "with no capture of stdout and no temporary file": a §9 tailing negation by shape, but it names the two alternatives the test avoids, which is the point of supplying recorders.
- L519-526, "The parametrize table is a list of environments, and the test body is the driver": a parallel pair; no "but", "so", or "while" fits the "and".
- L717-719, "Building a value and discarding it is legal Python, and `greet(name)`'s value is a generator like any other": two reasons for one claim, additive.
- L762-763, "a value nobody uses is a value nobody checks": a maxim by shape (§32), but it states the mechanism the paragraph has just shown, in the paragraph's own terms.
- L879-881, "`retry()` needs a fresh Effect per attempt, and the function that builds the Effect supplies one on each call": need and supply are two halves of one reason; the "and" is additive.
- L890-893, "a registry, a queue, or a cache": rule of three by shape, but each is a real place a reader stores an Effect.
- L1221, "Three implementations have six orderings, and one rule predicts them all": no "but", "so", or "while" fits the "and".
- L1296-1297, "That is what structural typing means": the cleft cannot be deleted without breaking the sentence.
- Long lines after the bold step labels (L90, L97, L311, L317, L427, L433, L508, L512, L520, L634, L1105, L1109, L1118, L1275): artifacts of the labels' insertion, left alone because rewrapping them changes no rendered text and only enlarges the diff.
