> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Deep review of chapter 44 after the six prose passes (elements-of-style,
literal, positive, straighten, cohesion, antecedents). No earlier review
of this chapter exists; `deep_review_db.md` has no standing rejection or
exemption that touches it. The prose pass ran without the global
`~/.claude/CLAUDE.md` watch list, which does not exist in the cloud
session; it used the skill's own rules, `banned_phrases.py`, and the
repo's `CLAUDE.md`. Every claim about chapters 45-47 was checked against
those chapters as they read on `master`, and the external claims were
checked against their sources: Koka's `readline()` is
`<console,exn> string` in `std/os/readline.kk`, Pact's README shows
`needs` and `using`, and Lumen's stdlib uses `bind effect`.

## Applied directly

- "Return a Result Type": "imports ... helpers unchanged" became "reuses
  ... helpers", since the next sentence also says "unchanged" about
  `slope()`.
- "Combine the First and Third": "All three approaches take the division
  failure out of `slope()`" became "keep a division by zero from escaping
  `slope()` as an exception". The catch version keeps the failure inside
  `slope()`, as the same paragraph says two sentences later.
- "A Program Can Never Be Pure": "So why track them at all?" became
  "What does keeping the rest pure buy you?". The answers that follow
  (parallelism, testing) are benefits of the pure part, not reasons to
  track Effects; tracking gets its own motivation in "Two Phases".
- "Two Phases": "The next phase produces one benefit per subdivision"
  became "The second phase divides the impure part by kind, and each kind
  yields its own benefit". "Subdivision" had no antecedent.
- "Tracking and Management" and "Effects by Hand": the two sentences
  saying Stateless "verifies the declaration" now say the type checker
  does, matching "Effect Management for Python?" and chapter 46's
  "Effects Propagate, and the Type Checker Verifies It".
- "Effects by Hand": "If you add a `Log` Effect three levels down" became
  "If a new helper that `greet()` calls needs a `Log` Effect". The helper
  sits four calls below `main()`, and exercise 2 describes it as a helper
  `greet()` calls. "Exercise 2 walks through..." is unchanged, so the
  exercise-reference baseline still pairs.
- "Native Effect Management", generator paragraph: added that a
  suspended generator is a continuation you can resume once or discard,
  never resume twice. The previous paragraph lists resume once, discard,
  and resume several times, and a reader wants to know which of those a
  generator gives. Chapter 46's "An Effect Runs Once" builds on the same
  fact.
- Two links whose text said "Effect Management Systems" but whose anchor
  is `#tracking-and-management` (the AI-languages section and exercise
  5) now say "Tracking and Management".
- "Effect Management for Python?": "Each of these gives you the
  discipline of one part of an EMS. The guarantee is missing, because no
  type checker enforces it." became "Each of these supplies part of an
  EMS, and none supplies all three parts." `returns` types its `IO` and
  `RequiresContext` containers, so a type checker does follow them, and
  those are two parts, not one. The new sentence leads into "One library
  supplies all three parts."
- "Effects Are the Next Barrier": "Python offers no native version of
  Effect tracking" became "no native Effect tracking beyond `async`",
  since the chapter has just said `async` is native tracking of one
  Effect.
- Closing roadmap: "[Stateless] builds the Effect type on top of it"
  became "builds a library Effect system on top of it". Chapter 46
  presents the library's existing `Effect` type; it does not build one.
- `tools/data/timing.txt`: registered `pure_and_pointless.py`, a
  wall-clock boolean (`busy > idle * 100`) that was missing from the list.
  Its margin is huge, so this is bookkeeping, not a fix for a flake.
- Solutions exercise 3: the linked `Thermometer` (`broadcaster.py`, in
  chapter 30's "Callables in a List") calls `announce()` on subscribed
  listeners. The solution said `notify()` and "observer", which belong to
  the classic version earlier in chapter 30. The table row and two
  sentences now match the listing.
- Solutions exercise 2: "Four existing signatures have to be edited"
  became "You must edit four existing signatures", which clears the only
  Vale warning left in either file.

## The "space heater" punchline

"A Program Can Never Be Pure" used to end its paragraph with "A
perfectly pure computation, followed to its logical end, is a space
heater with extra steps." The literal pass changed it to "... heats the
processor and does nothing else." The literal version is accurate, but
the original sentence was a punchline, not a figure standing in for a
mechanism, and the elements-of-style pass had left it alone as your
voice. I recommend restoring the original sentence. Keep the literal
version if you want this chapter free of figures.

[] Reject

## Considered and declined

- "Tracking and Management" states twice that tracking tells you whether
  a function is pure and names the kinds of impurity: once before the
  three-item list and once in the paragraph that defines *Effect
  tracking*. Each instance does its own job (the first motivates the
  list, the second defines the term), so neither was cut.
- "Catch the Exception You Expect" names the Effect Management System
  in two sentences close together ("the tedious, error-prone work an
  Effect Management System replaces" and "the tracking problem an Effect
  Management System solves"). The straighten pass split them, and
  merging them again would bring back the overloaded sentence.
- "Combine the First and Third" opens by comparing all three approaches
  before combining two. The heading names only the combination, but the
  comparison is what justifies it, and renaming the heading would change
  an anchor for no gain.
- "Only a runtime failure verifies the wiring" (dependency injection).
  Some containers check the wiring at startup, but startup is still run
  time, so the claim holds.
