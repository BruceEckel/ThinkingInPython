When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/44_Effect_Management.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers validate,
`ty` (0.0.70), ruff, and the run gate are clean on
`build/examples/44_Effect_Management` (7 scripts, no tests), and the one
timing boolean (`busy > idle * 100` in `pure_and_pointless.py`) held 6 of 6
standalone runs with a wide margin. Every cross-chapter claim in the opening
bullets was grep-verified (242,785 → 26 in ch18, `double()`/`withdraw()` in
ch40, `recolored()` in ch30, `simplify()` in ch34), and "the same
demonstration" claim against ch19 checks out: `async_mechanics.py` opens
with `x = fetch("a", 0.03)  # Nothing runs yet` and prints `coroutine`
first. The two Stateless claims ("an unsupplied dependency is a type error",
"calling an effectful function from one annotated as pure is a type error")
are both backed by ch46's demonstrated diagnostics (`invalid-argument-type`
at `run()`, `invalid-yield` at the undeclared yield), consistent with the
`stateless-partial-handling-ty-support` memory. All ten AI-language links
were fetched and verified live, and each one-line description matches its
project page (Mog's "fits in a model's context window" is near-verbatim from
its README; Pact is the AI-oriented KikotVit project, not Kadena's
blockchain Pact). Flix's `\ {Ask, Tell}` syntax, the TypeScript Effect
idioms (`Context.Tag`, `yield*` on a Tag, `Layer.succeed`,
`Effect.runPromise`), OCaml 5 (handlers, no effect typing), the
Koka/Flix/Eff/Effekt/Unison family list, and the three Python libraries
(returns: Result/Maybe/IO/RequiresContext; effect: intents + performers;
eff: handler models) all verified against their current docs. One factual
error surfaced and is fixed below: the Koka listing's `main` signature.
Inbound anchors from 40, 45, 46, 47, and `Solutions/` cover nearly every
heading in this chapter; no heading changed. The five exercises match
`Solutions/44_Effect_Management.md` in number and content. No live blocks
remain: every finding had one defensible answer.

## Applied directly

- Koka listing: `fun main() : console ()` is now
  `fun main() : <console,exn> ()`. Koka's stdlib `readline()` is typed
  `<console,exn> string` (std/os/readline docs), so a `main` whose `ask`
  handler calls it carries `exn`; the printed signature would not
  type-check. The customary `io ()` also works but hides the row the
  listing teaches. Worth a compile check against the research repo the
  section cites, since I cannot run Koka here.
- Handler paragraph, teaching addition: the listing's most instructive
  fact (main's row is `<console,exn>`, not `<ask,tell>`) went unexplained,
  so a reader comparing the two signatures had no account of where
  `ask`/`tell` went or where `console`/`exn` came from. Added: "Handling
  an Effect also discharges it..." naming both halves of the row change.
- Same paragraph: "so no Effect reaches the runtime unaccounted for" is
  now "unhandled" (dangling "for").
- "Effect Management Systems" opening: "Suppose a test starts failing
  intermittently. The test calls a function you wrote last week." is now
  "Return to the failing test from the chapter's opening." The section
  retold the chapter's cold open (same total price, currency helper,
  config read, audit write) without acknowledging it, reading as
  accidental repetition; the alternative, cutting one telling, would lose
  either the hook or the debugging detail.
- "Subdividing the Impure Portion" first bullet: "become data, the move
  ... just made three ways" is now "become data, as [Converting Effectful
  to Pure] showed with a `Result`". Only the `Result` conversion turns
  exceptions into checkable data; the `try` consumes the failure and
  `NonZero` prevents it, so "three ways" overclaimed, and "the move ...
  just made three ways" was garbled besides.
- "Two Phases" intro: "a series of phases" is now "two phases", matching
  the heading and the two phases the text then presents.
- `slope_result.py` prose: "`slope()` is total again" is now "is now
  total"; the undecorated `slope()` was never total.
- Exception-specification paragraph: "They leaked information" is now
  "They leaked implementation details" (the criticism is the abstraction
  leak, and "information" said too little).
- "why track them at all" paragraph: "The initial and most obvious
  reason" is now "The first and most obvious"; "touches nothing shared
  and runs in parallel" is now "touches nothing shared, so it is safe to
  run in parallel" (purity permits parallelism rather than causing it).
- "You only get these benefits if" is now "You get these benefits only
  if" (the "only" governs the condition).
- Delayed-binding paragraph: "flow up to a single point or edge" is now
  "a single point, usually the edge of the program", matching the two
  later "edge" mentions.
- ContextVar paragraph: "in whatever frame happened to need it" is now
  "needed it" (watch-word "happen"); "or forgetting to set one at all"
  dropped the "at all".
- "What that takes is a second channel" is now "That takes a second
  channel" (cleft delayed the verb).
- AI-languages intro: "Most of these only **track** Effects rather than
  providing a full EMS" is now "track Effects without providing the rest
  of a full EMS"; the mid-sentence bold was the book's only one outside a
  quotation.
- AI-languages section: lowercase "effects" in the Aver, Mog, AILANG,
  Pact, Zero, and Boruna bullets and in "an effect's interface" is now
  "Effects"/"Effect's", matching the chapter's capitalized term
  ("algebraic effects" in the Lumen bullet stays lowercase as a term of
  art, matching ch47).
- Coroutine paragraph: "This is the same demonstration [Concurrency]
  opened with" is now "[Concurrency] opened with the same demonstration"
  (stranded preposition).
- "The [eff] library models Effect handlers directly" dropped
  "directly": its mechanism is DI-style typed handler classes, not
  resumable handlers, so "directly" overstated.
- PEP-speculation paragraph: "almost all of which carry no annotations"
  is now "no Effect annotations"; much of PyPI carries type annotations,
  and the missing thing is the Effect row.
- C++ parenthetical: "whether or not a function throws at all" is now
  "whether a function throws".
- "how many functions have to know about it" is now "must know about it".
- `make reflow CH=44` after the prose edits (3 paragraphs repacked).

## Considered and declined

- **Noting that the PyPI `effect` library is dormant (last release
  November 2019).** The section catalogs partial approaches rather than
  recommending dependencies, and a maintenance-status remark goes stale
  by design.
- **Noting that Unison calls its effects "abilities".** Stateless also
  uses `Ability`, so the connection is real, but ch46 introduces the term
  in context; a cross-language naming aside here would interrupt the
  family list.
- **The "space heater with extra steps" line.** Meme-flavored, but it
  lands the section's point memorably and the book allows occasional
  humor; left alone.
- **Boruna self-describes as a deterministic workflow engine/DSL rather
  than a general-purpose language.** Its bullet's claim (VM-level
  policy-gated effects, tamper-evident replay) is accurate as written,
  and the section's frame is "experimental languages", which it satisfies
  loosely; not worth a qualifier in a one-line entry.
- **AILANG's five-item capability list.** The page confirms the
  mechanism and names `IO` and `FS` explicitly ("and others"); the full
  `IO, FS, Net, Clock, AI` list matches the project's documentation
  closely enough that no change is warranted.
