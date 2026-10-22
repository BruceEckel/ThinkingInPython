When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

# Deep review of 44 Effect Management (round 4, 2026-10-21)

Reviewed after the editing pass closed at tag `edit-start-44` (89 commits).
Four passes: correctness (every listing extracted and run under the gate,
`tip verify-ch CH=44` green at every step; the four non-Python programs
compiled and run under their own toolchains through `tip effects-test`, all
four printing the one expected transcript; Koka's and Leijen's accounts of
the three-part function type, Pact's `using` clause, Lumen's algebraic
effects and `bind effect`, the `eff` and `returns` libraries, and C++'s
exception-specification history checked against their sources), teaching
(the four lenses and the chapter-level order), the house-style audit of the
listings (no hand-written `__init__`, every frozen class a `@record` or
exempt), and the prose pass. The three earlier reviews' applied lists and
declined findings were read first; nothing here re-proposes them.

The chapter's claim, in a sentence: an Effect is what a caller takes on by
calling, no signature shows it, and the only fix that scales is to put it in
the type, which native languages infer and libraries encode. Every section
moves that forward, the order is motivation (the failing test, the three
kinds) then by-hand techniques then native then library then Python, and
each listing introduces one thing. The one gap is at the end of the teaching
pass, under Exercises below.

## Applied directly

- "Two Phases of Effect Analysis", the Failures bullet: "They are treated as ordinary return values rather than managing an exception-handling mechanism" had the caller doing one thing and nobody doing the other. Now "The caller handles them as ordinary return values instead of managing an exception-handling mechanism."
- "A Program Can Never Be Pure": "There are no surprises from side causes, side effects, or failures" was the one Vale error in the chapter (an existential "there"). Now "No side cause, side effect, or failure can surprise you."
- "Tracking and Management", the three-item list: item 1's label was a noun ("Effect tracking.") where items 2 and 3 are verbs ("Separates ...", "Binds ..."). Now "Tracks Effects."
- "Effects by Hand", the `greet_demo.py` lead-in: "`Scripted` and `Capture`, which check the greeting" credited the stand-ins with the check the test makes. Now "so the test checks the greeting without using the console".
- "Native Effect Management": "Thus, a native Effect type system function signature tracks Effects together with ordinary arguments and return types" restated the paragraph's first sentence (three pieces of information) in a five-noun stack. Cut (R19).
- "Library Effect Management": "its signature promises only a `Unit`" used the promise metaphor the review notes warn about in this part of the book. Now "declares only a `Unit` result".
- Same section: "Koka declared each Effect in two lines and handled it" and "Koka's `main()` read a line" narrated the listing above in the past tense. Now "declares ... handles" and "reads".
- Same section: "each Effect pays for it separately" was a commerce figure for the repeated machinery. Now "each Effect carries its own copy". "ships its own copy" and "no shipped wrapper" (watch-list tier 3) are now "supplies its own copy" and "no wrapper from the library".
- "Custom AI Languages with Effects": a semicolon joined two sentences ("are tracking systems; they provide"). Split.
- "Effect Management for Python": the lead-in to `coroutines_are_descriptions.py` said "It enforces that tracking on every caller:", which the listing does not show (it shows the description/execution split; the enforcement is the `await` paragraph below). Now "An `async def` builds a description instead of running its body:". The enforcement sentence survives where it was, "Python enforces the tracking the way an EMS does."
- Same section: "as `async def` already declares `async`" lost its "already" (watch list).
- Watch-word baseline: "never propagates" (the claim), "Even `greet()` grows", and "await its promise" (a JavaScript `Promise`, literal) accepted.

## Findings

### 1. The native and library sections have no exercise, and the programs are now runnable

Exercises 1 to 5 cover the by-hand techniques, the three conversions, and
`async`. Nothing asks the reader to touch the Koka, Flix, ZIO, or TypeScript
programs, and until today nothing could: they were listings to read. Since
commit f5ca0a95 they live under `effects/` with `tip effects-all`, and
`effects/README.md` says how to install each toolchain.

The chapter's strongest native-system claim is in the Koka section: "If
another function calls `greet()`, the compiler adds `ask` and `tell` to that
function's row automatically." Exercise 2 has the reader thread a `Log`
Effect through five Python signatures by hand. The natural sixth exercise is
the same change in Koka: declare `effect log`, call `log()` from `greet()`,
and run `koka` to see which rows change (`greet()`'s inferred row gains
`log`; `main()` needs one more `with` handler and nothing else, since its row
is inferred). The reader then has the chapter's five-signatures-versus-one
contrast in their own two runs, which no amount of prose supplies.

What I would write:

> 6.  The chapter says Koka infers a caller's row from what the body calls.
>     Test that: in `effects/koka/greet.kk`, declare a `log` Effect with one
>     operation, `log(message : string) : ()`, call it from `greet()`, and
>     run the program with `koka -e greet.kk`.
>     Delete the row annotation from `greet()` and run again.
>     Say which lines changed in the Koka program, and compare the count
>     with the five signatures exercise 2 edits in Python.

Two things only you can decide, which is why this is a block and not an
edit. First, whether a non-Python exercise belongs in the book at all, since
none exists yet and it asks the reader to install a compiler. Second, where
the solution goes: a `koka` block in `Solutions/44_.../README.md` would be a
fragment the gate never compiles (`extract_effects.py` reads `Chapters/`
only), so either the solution stays prose plus a diff, or the extractor
learns to read `Solutions/` as well, which is a small change I would make
with the exercise.

[] Reject

## Considered and declined

- "An enormous part of professional programming is consumed by this activity" (Effects Are the Next Barrier) is a passive with a by-phrase, the shape the activate pass clears. It is your rewrite from this pass, so it stands; the fault-review page records it as local.
- "We build programs from other people's code, and we don't know what that code does" uses "we" in the same section. Yours; left.
- "The first is a side effect ... The second is a side cause ... The third kind of Effect is an exception" opens three paragraphs with enumerators, the shape the capture pass flagged for "The first is Koka". Here the three paragraphs are a numbered walk through "Three things pass from callee to caller", and the enumerators are the walk's signposts, so they stay.
- "Flix hands you the continuation" and "Koka's `with fun` handler resumes for you" personify the languages lightly. Both name the mechanism in the same sentence (`resume(value)` returns the value to the point that performed the Effect), so the figure costs nothing.
- The Flix listing's `Option.getWithDefault("", line)`: a reader may ask why Flix's `readln()` returns an `Option` where Koka's `readline()` raises. The prose says it ("`None` at end of input"), and the contrast with Koka's `exn` in the row is already in the paragraph above, so no addition.
