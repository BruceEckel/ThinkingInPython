When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Chapter order: "Converting Effectful to Pure" (line 194) picks up a listing
from three sections back.**

The section opens:

> Transforming the exception Effect in `slope()` from
> `divide_by_zero_impurity.py` makes the function pure again.

`slope()` was last seen at line 77, inside "Are Exceptions Impure?".
Between them sit "A Program Can Never Be Pure" and "A Taxonomy of Benefits",
neither of which mentions `slope()` or exceptions-as-Effects.
A section that has to re-establish context from three sections back is the
tell the deep-review checklist names.

The two intervening sections are also the ones with the weakest claim on that
slot. "A Program Can Never Be Pure" argues that Effects are the point, which
reads *better* after the reader has just watched three attempts to remove one.
"A Taxonomy of Benefits" ends on "That failure motivates the machinery in the
rest of this chapter", and the section that immediately follows it today is
not machinery, it is three hand conversions.

**Recommended order:**

1. What Is an Effect?
2. Are Exceptions Impure?
3. **Converting Effectful to Pure** (moved up)
4. A Program Can Never Be Pure
5. A Taxonomy of Benefits
6. Effect Management Systems

That puts `slope()`'s three conversions immediately after the section that
raises the question, makes "Effects are not a defect to design away" a
corrective to what the reader just did, and lets "A Taxonomy of Benefits"
hand straight off to "Effect Management Systems", which *is* the machinery its
last line promises.

**Price of the move, checked:**

- Anchors survive. A move does not change a slug, and I verified every inbound
  link: `47_Stateless_in_Practice.md:2093` uses
  `#converting-effectful-to-pure`, `47:394` uses
  `#subdividing-the-impure-portion`, and neither depends on position.
- Two in-chapter links to `#converting-effectful-to-pure` (line 407 in
  "Effects by Hand", and exercise 3) keep working.
- Nothing in the moved section forward-references the two it jumps over.
  "Effects by Hand" is the only text that depends on it, and that stays after
  it either way.
- One sentence needs rewriting: "A Taxonomy of Benefits" currently opens the
  subdivision list with **Exceptions** "become data, via Error Handling", which
  after the move can point at the section just read instead of at chapter 42.

**Alternative, cheaper:** leave the order alone and change the opening sentence
of "Converting Effectful to Pure" to re-quote the function rather than name the
file, e.g. "Go back to `slope(rise, run)`, which divides and therefore raises."
That removes the reader's page-flip without moving anything.

I recommend the move; reordering is a proposal on principle, so it is yours to
decide.

---

[] Reject

**Front-load the payoff: the chapter's most convincing motivation sits at line
332, and the opening is a table of contents.**

The intermittent-test story ("Suppose a test starts failing intermittently...
Three calls deep, inside a helper that formats currency, you find the problem")
is the best writing in the chapter and the only place a reader feels the
problem rather than being told about it. It arrives 38% of the way in, after
the reader has already been asked to accept that hand-tracking "rapidly becomes
tedious and error-prone" on the strength of one abstract paragraph.

Proposed: open the chapter with a three-sentence version of that story, before
the bulleted list of prior chapters. Something like:

> A test you wrote last week starts failing about one run in five.
> The function it calls computes a total price, the math is right,
> and three calls down, inside a helper that formats currency,
> there is a read from a configuration service and a write to an audit log.
> None of that is in any signature on the path.

Then the existing "This book has emphasized the benefits of pure functions"
list reads as the answer arriving, rather than as throat-clearing.

The full story stays where it is at line 332; it is doing different work there
(it introduces the four questions and the EMS definition), and a reader who
meets it twice, once in miniature and once in full, is not being repeated at.

Reported, not applied: this is the chapter's opening and its pacing.

---

[] Reject

**"A Taxonomy of Benefits" (line 155): the heading names something the section
does not contain, and the section is one heading plus one subheading.**

The body is not a taxonomy of benefits, it is a two-phase account of how far
you have pushed the analysis: phase one splits pure from impure, phase two
subdivides the impure part into exceptions, side causes, and side effects.
The only actual taxonomy in the chapter is the three-kinds-of-Effect list in
"What Is an Effect?" and "Are Exceptions Impure?".

Proposed: retitle to **"What Tracking Buys You"** or **"Two Phases of Effect
Analysis"**, and either fold `### Subdividing the Impure Portion` up into the
parent (it is the section's only subheading) or give the parent a second
subheading so the level earns its place.

Cost: `#subdividing-the-impure-portion` is linked from
`47_Stateless_in_Practice.md:394`, so **that subheading's title must not
change**; only the `##` above it is free. `#a-taxonomy-of-benefits` has no
inbound links anywhere in `Chapters/` or `Solutions/`, so the `##` can be
renamed with nothing to update.

Reported, not applied: a heading is voice.

---

[] Reject

**Intro, lines 23-30: "potentially pure function" and the shifting subject of
"that function".**

Two sentences in the opening do more work than their wording supports.

> There's one important thing these all have in common:
> you can verify function purity just by examining the code in that function.

"these" is a list of six chapter references, and "that function" then names a
function that has not been introduced.
The reader has to reconstruct "in each of those cases, the function you are
checking is self-contained."

> What happens if your potentially pure function calls other functions?

"potentially pure" is not a category the book has defined, and the sentence is
really asking about a function you believe is pure.

Proposed replacement for both:

> In every one of those cases you can settle the question by reading one
> function.
>
> What happens when a function you believe is pure calls other functions?

Reported rather than applied because this is the chapter's first paragraph and
sets its voice, which is your call, not mine.

---

[] Reject

**"Custom AI Languages with Effects" (line 692): the section holds the reader
off for ten bullets before giving a reason it could give immediately.**

Line 700: "Most of these only **track** Effects, rather than providing a full
EMS, for reasons the end of this section explains:" and then the reason arrives
at line 728, after the list:

> For their purpose the other two parts are liabilities,
> since a host that pins the implementations itself can guarantee
> what generated code is able to do.

That reason is one clause long. Holding it back does not build anything; it
just makes the reader carry a question through ten bullets. The closing
paragraph then has to restate the setup ("By the definition above, most of
these are Effect-tracking systems rather than full EMSs") to reconnect.

Proposed: move the reason into the lead-in and shorten the closing paragraph to
its remaining content (the Pact/Lumen exceptions):

> Most of these only **track** Effects rather than providing a full EMS,
> and for their purpose the other two parts are liabilities:
> a host that pins the implementations itself can guarantee
> what generated code is able to do.
>
> [ten bullets]
>
> Pact and Lumen are the exceptions.
> Each separates an effect's interface from its implementation
> and binds the implementation later,
> the second and third properties of a full EMS.

Reported, not applied: it moves a paragraph, which is pacing.

Separate, smaller note on the same section: "Effect" names three different
things within 120 lines. The chapter's concept (capital-E Effect), the
TypeScript library at line 643, and the PyPI `effect` library at line 783. The
distinction is carried entirely by backticks and links. A half-sentence at the
PyPI mention ("no relation to the TypeScript library of the same name") would
save a reader the double-take, if you agree it is a real one.

---

[] Reject

**The chapter never hands off to chapter 45, and 45 is what comes next.**

"Effects Are the Next Barrier" ends on "future programmers will regard a
function with hidden Effects the way you regard a program written in one global
namespace." That is a good last line for a chapter and a bad last line for the
first chapter of Part V. The reader turns the page and lands on Generators with
no idea why.

I fixed the mid-chapter half of this (see the manifest: the Library Effect
Management sign-off now names 45, 46 and 47 in order), but the conclusion is
still a dead end.

Proposed: one short paragraph before "## Exercises", after the current last
line:

> Python cannot give you the language half of that today.
> It can give you the library half.
> The next three chapters build one:
> [Generators](45_Generators.md) supplies the mechanism,
> [Stateless](46_Stateless.md) builds the Effect type on top of it,
> and [Stateless in Practice](47_Stateless_in_Practice.md)
> puts it to work.

Reported, not applied: a chapter's closing paragraph is voice, and you may
prefer the current ending to stand undiluted.

---

[] Reject

**Exercises: nothing exercises "Effect Management for Python?", the chapter's
one Python-specific insight.**

Coverage today: exercises 1 and 2 hit "Effects by Hand", 3 hits "What Is an
Effect?" and "Converting Effectful to Pure", 4 hits "Make the Bad Value
Impossible". The `async`-is-already-Effect-tracking argument, which is the
chapter's strongest claim about Python and the one chapter 45 links back to
(`45_Generators.md:169`), gets nothing.

Proposed exercise 5 (safe to append; it does not renumber exercise 2):

> 5.  `coroutines_are_descriptions.py` shows that `async` tracks one Effect.
>     Write a synchronous `total_price()` that calls a helper,
>     then make the helper `async` and follow what the checker and the
>     interpreter force you to change, all the way up to `asyncio.run()`.
>     Name the two properties of a full EMS that `async` does *not* have,
>     using the three-item list in
>     [Effect Management Systems](#effect-management-systems).

The last sentence is the point: `async` tracks, but it does not separate
interface from implementation and it does not let you bind the implementation
later, so it is an Effect-tracking system in exactly the sense the AI-languages
section uses.

Reported rather than applied: the size of the exercise set is a pacing
decision.

---

[] Reject

**"Effects by Hand", line 451-452: "its signature says so" claims more than the
signature can deliver, and the chapter itself says so 350 lines later.**

> `greet()` performs an `Ask` Effect and a `Tell` Effect,
> and its signature says so.

The signature says `greet()` *may* perform those two. Nothing stops the body
from also calling `print()`, and then the signature is exactly the lie the
chapter accuses `-> None` of being. The chapter makes this point precisely, but
only at line 804, about Stateless:

> Nothing stops a function from calling `print()` directly,
> adjacent to its carefully declared Effects.
> ... A library checks the Effects you wrote down.
> Only the language can check the ones you didn't.

That limit is not specific to Stateless. It applies to every by-hand and
library technique in the chapter, and this is the first place a signature is
claimed to state Effects, so it is where the reader forms the belief.

Proposed one-line addition after "and its signature says so.":

> It says what `greet()` needs, not everything `greet()` might do:
> a `print()` in the body would still be invisible.
> [Effect Management for Python?](#effect-management-for-python)
> returns to that limit.

Reported rather than applied because you may be deliberately holding the
qualification until the Stateless discussion, so the by-hand section can make
its point cleanly first.

---

[] Reject

**"Native Effect Management", after the continuation paragraph (line 566-568):
Python's own pause-and-resume mechanism is never named, and it is the subject
of the very next chapter.**

The paragraph explains that a handler receives the continuation, and can resume
it once, discard it, or invoke it several times. That is exactly what a Python
generator's `send()`/`throw()`/`close()` do, it is the mechanism
[Generators](45_Generators.md) exists to teach, and it is what Stateless is
built out of. Chapter 46 states the dependency flatly ("Stateless is built on
generators"), and chapter 45 states it from its own end ("The next chapter
builds an Effect system on all three"). Only chapter 44, the chapter that
motivates both, never mentions generators at all.

Proposed addition at the end of that paragraph:

> Python has a construct that suspends a computation and hands control to
> whoever is driving it, then resumes it with a value: the generator.
> [Generators](45_Generators.md) covers the full two-way form,
> and it is the mechanism the Python Effect library in
> [Stateless](46_Stateless.md) is built from.

Reported rather than applied because it inserts a Python aside into a section
that is deliberately all non-Python, which is a pacing judgement.

---

[] Reject

**Exercise 2 asks the reader to count edited signatures, but the chain is two
functions long.**

> 2.  Feel the bookkeeping the chapter describes.
>     Add a `Log` Effect (a protocol with `log(message)`)
>     used by a new helper that `greet()` calls.
>     Count how many signatures you had to edit to pass it down,
>     then explain what an EMS would do instead.

As written the answer is "two" (the helper and `greet()`), plus the one call
site. Two is not a number that makes anyone feel bookkeeping, and the prose the
exercise is cashing says "you edit every signature on the path" and "parameters
accumulate at every level of the call stack."

Proposed rewrite:

> 2.  Feel the bookkeeping the chapter describes.
>     Wrap `greet()` in three callers, `session()`, `menu()`, and `main()`,
>     each calling the next and none of them using `Ask` or `Tell`.
>     Now add a `Log` Effect (a protocol with `log(message)`)
>     used by a new helper that `greet()` calls.
>     Count the signatures you had to edit, and note how many of them
>     mention an Effect they never use.
>     Then say what an EMS would do instead.

The added clause ("how many of them mention an Effect they never use") is the
part that actually hurts, and it is the thing the delayed-binding argument at
line 390 is about.

**Constraint if you change this exercise:** `46_Stateless.md:608` refers to it
as "The second exercise in [Effect Management](44_Effect_Management.md#exercises)",
so it must stay number two and must stay the `Log`-Effect exercise.

Reported, not applied: exercise difficulty is pacing.

---

[] Reject

**"Library Effect Management", ZIO listing (line 597): Scala 2 and Scala 3
syntax in the same twenty lines.**

The listing opens `import zio._` (Scala 2 wildcard) and then uses Scala 3
significant indentation throughout: `trait Tell:`, `object Main extends
ZIOAppDefault:`, and `ZLayer.succeed(new Tell: ... )`. Scala 3 still accepts
`_` as a wildcard, so this compiles, but a Scala reader will read the mix as an
error and stop to work out which dialect the listing is in, which is attention
spent on nothing.

Proposed: change both imports to Scala 3 form.

```scala
import zio.*
import zio.Console.printLine
```

Also worth a second look while you are in there: `ZLayer.succeed(new Tell: ...
)` puts a Scala 3 anonymous-class body inside a parenthesized argument, which
is legal only with the closing paren where it is. If this listing was
transcribed rather than compiled, that is the line most likely to be wrong.

Reported rather than applied because I have no Scala toolchain here and will
not silently edit code I cannot compile.

---

[] Reject

**CROSS-TREE, do not apply here: `Examples/` needs a sync.**

I changed one code listing, `coroutines_are_descriptions.py` (manifest item
13), so `Examples/44_Effect_Management/coroutines_are_descriptions.py` is now
one revision behind `Chapters/`. I did not run the sync, because
`extract_examples.py --write` without `-o` rewrites the shared tree and other
reviewers are working in this clone.

Run `make sync` (or `make verify`) once this review sweep is finished.

---

[] Reject

**MANIFEST, not a proposal. Changes already applied to
`Chapters/44_Effect_Management.md` in this pass.**

Verification after the last edit, all green: `extract_examples.py --write -o
build/private/44`; `validate_output.py --tree /tmp/tip/build/private/44
Chapters/44_Effect_Management.md` (1 ok, 0 failed, and no `#:` marker in the
chapter was rewritten by the tool); `ruff check` on the extracted chapter;
`ty check 44_Effect_Management` from inside the private tree; every extracted
script run directly; `heading_links.py` ("Anchor links OK");
`banned_phrases.py` ("No banned phrases found"); `reflow_prose.py --diff` on
this file only (0 paragraphs, so the new prose is Semantic-Line-Breaks clean).
The chapter has no tests, so no `pytest` step.

1.  "What Is an Effect?": "Side effects are relatively easy to spot because
    they change things in their environment" now reads "easy to spot **in the
    function that performs them**, because they change something outside it."
    Without the scope, the sentence contradicts the chapter's own motivating
    story 280 lines later, where the side effects are three calls deep and
    nobody spots them.
2.  "Are Exceptions Impure?", the Haskell/⊥ argument: "raising an *uncatchable*
    error is technically referentially transparent" → "raising an error **that
    nothing catches**". "Uncatchable" reads as a property of the language, and
    it is false in Haskell: `error` is catchable in `IO`, which is exactly the
    classic objection to imprecise exceptions. The referential-transparency
    claim depends on nothing catching it, not on nothing being able to.
3.  "Are Exceptions Impure?", new closing line: "Effects therefore come in
    three kinds: side effects, side causes, and exceptions." The chapter defines
    Effects as "the union of side effects and side causes" at line 67, then
    spends a section adding exceptions, and never restates the total. The
    three-way split is assumed from "Subdividing the Impure Portion" onward.
4.  "A Program Can Never Be Pure": "because Python cannot tell that the work is
    worthless, and skip it" → "because Python cannot recognize the work as
    worthless and skip it." The original comma made "and skip it" dangle off
    "cannot tell that".
5.  "A Taxonomy of Benefits": "Consider the depth of Effect analysis as a series
    of phases" → "Think of Effect analysis as a series of phases." A depth is
    not a series of phases.
6.  "Return a Result Type": "`@safe` catches whatever **it** raises" →
    "whatever **`slope()`** raises." Two candidate referents, and the nearer one
    is wrong.
7.  "Catch the Exception You Expect": "**By calling it**, `validate()`'s Effect
    becomes `slope()`'s Effect" → "**Because `slope()` calls it**, ...". The
    participle attached to "`validate()`'s Effect", which calls nothing.
8.  "Catch the Exception You Expect", exception-specifications note: added the
    reason they failed, which is the chapter's own thesis and was missing.
    "Nothing computed a specification from the functions a body called, so an
    exception introduced three levels down had to be written by hand into every
    signature above it. The usual escape was to widen the specification until it
    said nothing." Also fixed "C++ changed **their** specifications" →
    "**its**" (C++ is one language; the sentence lists two).
9.  "Make the Bad Value Impossible", after the three-way comparison: added
    "None of the three makes the failure disappear. A `Result` turns it into a
    value, a `try` consumes it, and `NonZero` moves it to the one line that
    builds the value. What changes is how many functions have to know about
    it." A reader finishing this section can otherwise conclude that `NonZero`
    removed an Effect from the program, when it relocated one to construction,
    where `__post_init__` still raises.
10. "Effect Management Systems": "**By its name and parameters**, that function
    calculates a total price" → "Its name and parameters say it calculates a
    total price for a list of items." Another dangling modifier, and it merges
    two short lines into one sentence.
11. "Effect Management Systems": "Most functions in most programs have this
    hidden life **which** makes code hard to understand:" → "..., **and it is
    what** makes code hard to understand:". The restrictive `which` said that
    only the code-hardening subset of hidden lives was meant.
12. "Effect Management Systems", the EMS definition: removed both uses of
    "guarantees", the chapter's one instance of the promise metaphor applied to
    a checker. "the EMS guarantees that your function also reports its Effects"
    → "the EMS **adds that Effect to your function's type**"; "the EMS
    guarantees that the new function also reports whatever Effects it produces"
    → "the EMS **carries the Effect into that function's type as well, and so on
    out to the edge of the program**"; "the EMS **will give details about** the
    kinds of impurities that function involves" → "**the signature names** the
    kinds of impurity involved." The rewrite also fixes an accuracy problem the
    metaphor was hiding: the sentence made the function do the reporting, when
    in a native system the compiler infers the row (which this chapter says
    itself at line 534) and in a library system the return type carries it.
    "Adds to the type" is true of both.
13. **`coroutines_are_descriptions.py`, mechanism instead of outcome.** The
    listing proved "nothing runs" by printing the object's type, from which a
    reader cannot tell whether the body ran and the result was wrapped. Added a
    module-level `ran: list[str]` that the coroutine appends to, and folded it
    into both existing prints:

    ```python
    print(type(description).__name__, ran)
    #: coroutine []
    print(asyncio.run(description), ran)
    #: Hello ['body']
    ```

    The prose now says "the empty list is the evidence: the body never
    executed." Verified: runs, deterministic, `ruff` clean at 70, `ty` clean.
    This matches how `19_Concurrency.md`'s `async_mechanics.py` makes the same
    point (a "started" line that fails to appear), so the chapter's claim that
    this is "the same demonstration Concurrency opened with" still holds.
14. "Native Effect Management": "come from my research, **which builds** the
    same small programs" → "**in which I build** ...". Research does not build
    programs.
15. **"Library Effect Management": corrected a count with no referent.**
    "[Stateless](46_Stateless.md) builds **all three of these listings** again"
    had nothing to point at: this section and the one before it hold four
    listings (Koka, Flix, ZIO, TypeScript), and chapter 46 rebuilds one of them
    while chapter 47 rebuilds another. The sentence also skipped chapter 45
    entirely, so a reader was sent from 44 straight to 46 and then landed on
    Generators with no explanation. Replaced with the real sequence:

    > Stateless is built on generators, so [Generators](45_Generators.md)
    > covers that mechanism first.
    > [Stateless](46_Stateless.md)
    > then writes these programs again in the language this book is about,
    > and [Stateless in Practice](47_Stateless_in_Practice.md#abilities-are-not-special)
    > rebuilds the `ask`/`tell` pair from [Effects by Hand](#effects-by-hand).

    Checked against the far ends: `46_Stateless.md:15` says "Stateless is built
    on generators", and `47_Stateless_in_Practice.md:28` says "Here is the
    Stateless version of `Ask` and `Tell` from [Effect
    Management](44_Effect_Management.md#effects-by-hand)". Both new anchors
    pass `heading_links.py`.
16. "Custom AI Languages with Effects": "These new languages have no
    human-constrained adoption curve. AI Effect Languages don't need the extra
    affordances that benefit humans." → "Adoption is not gated by how long
    humans take to learn them. A language written for an AI doesn't need the
    conveniences that help a person read code, and if it works, an AI can start
    using it immediately." "Human-constrained adoption curve" and "affordances"
    are out-of-character diction for this book, and "AI Effect Languages"
    capitalized a term the chapter never defines.
17. "Custom AI Languages with Effects": "a host that **fixes** the
    implementations" → "a host that **pins** the implementations itself".
    "Fixes" reads first as "repairs".
18. "Effect Management for Python?": "so that **the declaring** stops being
    manual?" → "so that **declaring Effects** stops being manual?"
19. "Effects Are the Next Barrier": "Version control made program elements
    unique across time" → "Version control gave every state of the code a name
    you can return to". The original is opaque next to the three concrete
    examples around it.
20. Ran `reflow_prose.py --write` on this file alone (three paragraphs, all of
    them ones I had just edited) so the new prose obeys Semantic Line Breaks.
    No other file was touched; the tool reported "1 file(s), 3 paragraph(s)".

**Checked and found clean, so no change was made:**

- **The "promise" metaphor.** One occurrence in the whole chapter,
  `Effect.runPromise` inside the TypeScript listing at line 666, which is a real
  API name and must stay. The metaphor's nearest relatives were the two
  "guarantees" in the EMS definition, now gone (manifest 12). The remaining
  "guarantee" uses are literal and correct: "The same guarantee makes testing
  trivial" (line 159), "Every function that receives a `NonZero` ... inherits
  that guarantee" (line 312-313), "The guarantee has a boundary" (line 802), and "a
  host ... can guarantee what generated code is able to do" (line 730). None of
  them has one thing promising and another keeping the promise.
- **"reach for"**: absent, before and after my edits; `banned_phrases.py`
  passes.
- **The PEP 695 `type`-alias trap from `CLAUDE.md`.** This chapter contains no
  `type X = ...` alias and no generator function at all, so there is no Effect
  signature here that `ty`'s invalid-yield check could be silently skipping.
  Nothing to unpick.
- **Both claims the chapter makes about Stateless, verified against the
  installed source** (`.venv/lib/python3.15/site-packages/stateless/`) with a
  scratch probe under `ty` in the private tree, not from the docs. "Declaring a
  dependency you never bind is a type error": `run()` is declared
  `run(effect: Effect[Async, Exception, R])`, so handing it a
  `Depend[Need[Config], Config]` gives `error[invalid-argument-type]:
  Expected Generator[Async | Exception, Any, Unknown], found
  Generator[Need[Config], Any, Config]`. "Calling an effectful function from one
  annotated as pure is a type error": `yield from` an effect inside a function
  annotated `Success[int]` gives `error[invalid-yield]: expression of type
  Need[Config], expected Never`, because `Success` is
  `Generator[Never, Any, R]`. Both diagnostics are real and land on the right
  line.
- **`pure_and_pointless.py`'s threshold boolean.** `busy > idle * 100` ran
  `True` six times out of six standalone. The margin is not marginal: `busy` is
  five iterations of a two-million-step loop and `idle` is five calls to
  `pass`, so the two differ by several orders of magnitude, not by a factor near
  100. This is not the fragile kind of timing boolean that `CLAUDE.md` warns
  about; it would only flip on an implementation that elides the dead loop
  (PyPy, or a future CPython JIT with dead-store elimination), and on such a
  build the prose's claim would genuinely be false, so a flip is information
  rather than flake.
- **House style.** No hand-written field-assigning `__init__` anywhere in the
  chapter. `NonZero` is a validated frozen dataclass with a checking
  `__post_init__`, which is exactly the idiom the style skill prescribes for a
  primitive standing in for a domain concept, and plain `frozen=True` without
  `slots=True` matches the book's practice (85 plain uses across `Chapters/`
  against 7 with slots). `Ask`/`Tell` are `Protocol`s rather than ABCs, as the
  skill asks. The one inline comment in a listing (`# Nothing runs`) predates
  this pass and the skill says to leave existing comments alone.
- **Inbound cross-references.** All seventeen inbound anchor links from
  chapters 45, 46 and 47 still resolve; `heading_links.py` is green. Two of
  them constrain future edits and are called out in the proposals above:
  `46_Stateless.md:608` pins exercise 2's number and subject, and
  `47_Stateless_in_Practice.md:394` pins the title of
  `### Subdividing the Impure Portion`.
- **Spot-checked the volatile external claims.** `veralang.dev` and
  `moglang.org` both match their bullets (Vera: mandatory contracts with Z3;
  Mog: a spec sized for a context window, effects gated by capabilities).
  `zerolang.ai` exists and mentions effects, but its landing page does not
  confirm "capability-based" or the JSON-diagnostics detail, so that bullet is
  worth re-reading before print. The proxy here blocks bare `curl` to most of
  these hosts, so I could not do a mechanical link check of all ten; the
  section is explicitly dated ("At this writing"), and it is the part of the
  chapter most likely to rot between now and publication.
- The OCaml claim ("OCaml 5 added the handler mechanism, though it does not yet
  track Effects in function types") is still accurate for upstream OCaml.
  Typed-effect work exists but lives in Jane Street's OxCaml fork, not in the
  OCaml 5 releases the sentence is about.
