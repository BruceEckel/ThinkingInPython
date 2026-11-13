# Bruce-edit rule store

Editing practices induced from Bruce's own edits to `Chapters/`, written by
`/bruce-edit-capture` and consumed by `/bruce-edit-apply`. Two skills share
this one file: `.claude/skills/bruce-edit-capture/SKILL.md` mines a diff and
proposes entries, `.claude/skills/bruce-edit-apply/SKILL.md` applies the
promoted ones to a chapter or to the book.

**This file is a workbench, not a fourth style guide.** The permanent homes
for style rules are the global `~/.claude/CLAUDE.md` watch list, the
`activate` skill's "Accrued patterns", and the `deep-review` skill's accrued
notes. A rule that proves out gets filed into whichever of those fits, and its
entry here records where it went in a `Home` field. The entry stays here
afterward anyway, because being in a style guide is not the same as having
been applied to 47 existing chapters, and only this file drives that sweep.

**Promotion.** One sighting makes a candidate. A second independent sighting,
in a different chapter, promotes it to a rule. Only rules are applied. Bruce can
also promote on one chapter's evidence (R2-R9 were, on 2026-08-29); the
entry records that, and its first sighting from another chapter confirms
or narrows it.

**Retirement is permanent.** A rule or candidate Bruce rejects moves to
Retired with his reason and is never proposed again, in any wording. Without
that record, every capture round re-proposes the same rejected rule.

---

## Entry format

Both Rules and Candidates use this shape. Rules are numbered `R1, R2, ...`
and candidates `C1, C2, ...`; a promoted candidate keeps its sightings and
takes the next free `R` number.

```
### R1. Short imperative statement of the rule

**Test.** How to decide whether the rule fires at a given site. A rule with
no usable test cannot be applied and should stay a candidate.

**Keep when.** The exception, if the evidence shows one. "None seen yet" is
an honest value here and marks the rule as needing care during a sweep.

**Sightings.** 2
- `22_Chapter` 2026-08-15, was Claude-written:
  "the count would be wrong again" -> "the count would still be wrong"
- `31_Chapter` 2026-08-20, was Bruce-written:
  "..." -> "..."

**Home.** activate (Accrued patterns) | CLAUDE.md watch list | deep-review |
this file only
```

The verbatim before/after pairs are the point of the entry, not decoration.
When a rule later looks wrong, re-read its sightings rather than arguing from
its wording; the wording is my summary, the pairs are the evidence.

A rule that adds something is worth more than a rule that cuts something, and
is rarer in a diff. Mark additive rules so a sweep can weight them: a store
made entirely of cut-this-word rules will sand the voice off the book.

---

## Rules

Promoted, two or more sightings, applied by `/bruce-edit-apply`.

### R1. Give "raises" an object

**Test.** The verb "raise"/"raises"/"raising" with no object after it:
end of sentence, a comma, or an adverb/conjunction ("raises instead",
"returns or raises"). Supply the exception's name where the text knows
it, otherwise "an exception".

**Keep when.** The object is fronted in a relative clause ("the exception
it raises", "whatever `slope()` raises", "what it re-raises"). Code and
`#:` markers are never touched.

**Sightings.** 3 (additive)
- `26_Patterns--Factory` 2026-09-01 (`6f638b05`), was Claude-written:
  "A placeholder raises only when something calls it" -> "A placeholder
  raises an exception only when something calls it"
- `24_Patterns--Template_Method` 2026-08-29, was Claude-written:
  "The `class Typo` statement raises instead of finishing" ->
  "The `class Typo` statement raises a `TypeError` instead of finishing"
- `Solutions/14_Techniques--Decorators`, `Solutions/24_Patterns--Template_Method`,
  `Solutions/47_Effects--Stateless_in_Practice` 2026-08-29, found by sweep after
  Bruce named the rule: "returns or raises." -> "returns or raises an
  exception."; "this one raises instead" -> "this one raises an exception
  instead"; "returns rather than raises" -> "returns a value rather than
  raising an exception"

**Home.** CLAUDE.md watch list (global, Writing Style) and activate
(Accrued patterns). Bruce reported the rule as one that "has been lost";
no prior record of it existed anywhere in the repo, the skills, or memory.

### R2. Cut the tally of what a technique costs

**Test.** A clause or sentence whose content is a price/cost accounting of
what a mechanism requires: "the price of", "it costs nothing", "it costs
one decorator", "one base-class method, and", "it needs nothing added".
Delete the accounting and let the mechanism's own sentence lead.

**Keep when.** A measured cost (time, memory, a benchmark) is the subject.

**Sightings.** 3 (removal), all `24_Patterns--Template_Method` 2026-08-29, was
Claude-written:
- "The empty step is the price of the `...` defaults above. They make a
  step optional," -> "The `...` defaults make a step optional,"
- "The type checker, via `@final`: one decorator, and an override of
  `run()` is reported before the program runs." -> "The type checker, via
  `@final`. Discovers an overridden `run()` before the program executes."
- "The interpreter, via `__init_subclass__()`: one base-class method, and
  the offending subclass is refused" -> "...`__init_subclass__()`. An
  offending subclass is refused"; "It needs nothing added, but it only
  works when" -> "This only works when". Bruce also objected in
  conversation to "It costs one decorator" and the list's "Each has a
  cost" framing before the rewrite.

**Home.** this file only. Promoted at Bruce's call on one chapter's
evidence ("accept all", 2026-08-29).

### R3. Don't use an identifier's word in its ordinary sense nearby

**Test.** A prose word that is also a method, function, or variable name
in the section's listings (`shape`, `field`, `module`, `kind`), used in
a different sense in the same section. Choose a synonym for the prose
sense and keep the identifier's word for the identifier. Content words
only (Bruce, 2026-10-04, Sweep Decisions page): a function word or a
common verb used as an identifier (`run`, `order`, `one`, `first`,
`times`, `group`, a capture named `only`) is a skip, since a reader
does not confuse the English word with the identifier; the earlier
sightings on `run()`/"runs" and `fix`/"fixes" stand as history.
The chapter's subject vocabulary counts like an identifier's word
(widened 2026-10-19, chapter 31): beside a chapter whose subject gives
a word a technical sense (entering and leaving states; a set of
actions; a lookup key), the ordinary sense of that word reads as the
technical one, so "the message the action left" reads as leaving a
state and "the message the action set" reads as a set of actions.

**Keep when.** The prose word names the identifier itself ("`run()` runs
the steps" is about `run()`).

**Sightings.** 6 (additive), 3 chapters
- `26_Patterns--Factory` 2026-09-01 (`40323f50`), was Claude-written, in
  a chapter whose class is `Shape`: "the shape a factory-object design
  takes" -> "the form a factory-object design takes"
- `26_Patterns--Factory` 2026-09-12 (`4ab635e2`), was Claude-written, in
  a chapter where `kind` is the selector parameter of six listings: "a
  factory of the same kind as `factory()`" -> "a factory, of the same
  form as `factory()`"
- `24_Patterns--Template_Method` 2026-08-29, was Claude-written:
  "an override of `run()` is reported before the program runs" ->
  "Discovers an overridden `run()` before the program executes"
- "the quick fix" / "the fixed algorithm" / "What Actually Fixes the
  Algorithm" -> "the quick repair" / "the anchored algorithm" / "What
  Anchors the Algorithm" (Bruce: "the word 'fix' seems to be used in
  both senses in this chapter")
- `31_Patterns--State_Machines` 2026-10-19, Bruce's note on the
  `vending_demo` lead-in, in a chapter about entering and leaving
  states: "followed by the message the action left:" -> "then the
  `message` that the rule's action wrote:" ("set" was tried first and
  read as a set of actions)
- `31_Patterns--State_Machines` 2026-10-19, beside a dictionary's
  keys: "The engine's lookup keys on `type(event)` exactly, one
  dictionary lookup rather than an `isinstance()` test against each
  row." -> "The engine looks up rules by the exact `type(input_)`, so
  finding them takes one dictionary lookup rather than an
  `isinstance()` test against each
  rule."
- `45_Effects--Generators` 2026-11-09, was Claude-written (a same-day
  R59 repair): "That restriction calls for a driver: something must
  call `next()` and `send()`." -> "That restriction requires a
  driver: something must call `next()` and `send()`." Bruce: "'calls
  for' ... confuses with the later 'call'". The idiom's word is the
  chapter's term (a call resumes a generator), so the idiom goes.

**Home.** this file only. Promoted at Bruce's call (2026-08-29).

### R4. Front an already-established cause with "Because"

**Test.** "X, so Y" where X restates something the reader already has
(a fact the chapter established, a listing just shown) and Y is the
sentence's claim. Rewrite as "Because X, Y". Narrowed 2026-10-04
(Bruce, Sweep Decisions page, after the book-wide report found 160
sites and the agents said it fires on almost every "X, so Y" that
explains the listing just shown): X must have been *stated in an
earlier sentence of the same passage*, not merely visible in the
listing; the evidential "so" ("the output shows X, so ...") is never
a site; and a sweep applies only the sites rated high confidence.

**Keep when.** X is new information. Bruce's own "no subclass exists, so
nothing can replace the loop" keeps "so": the absence of a subclass is the
point being made. Chapter 26 confirmed this boundary from the other side.
Bruce fronted "Every assignment after `__init__()` reaches the
implementation, so ..." with "Because", then later rewrote the same
sentence back to "so" once he had added "Now" and "via the new
`__setattr__()`", which turned the clause into new information. The revert
is evidence for the exception, not against the rule.

**Sightings.** 6 (3 chapters), plus one keep-when
- `26_Patterns--Factory` 2026-09-01 (`40323f50`), was Claude-written,
  three: "A `class` statement is executable code, so every call would
  define fresh ... classes" -> "Because a `class` statement is
  executable code, every call ..."; "`deepcopy()` copies everything it
  can reach, so a prototype holding ..." -> "Because `deepcopy()` copies
  everything it can reach, a prototype ..."; "`interact_with()`
  dispatches on the character's type, and `obstacle.action()` dispatches
  again on the obstacle's, so the pair of calls" -> "Because
  `interact_with()` dispatches ... the pair of calls". The keep-when from
  the same commit: "Because the registry keys on `cls.__name__` alone,
  two classes ... overwrite" -> "The registry keys on `cls.__name__`
  alone, so two classes ...", where the keying is new information.
- `24_Patterns--Template_Method` 2026-08-29, was Claude-written:
  "`run()` calls methods the subclass supplies, so the subclass must
  finish its own setup" -> "Because `run()` calls methods the subclass
  supplies, the subclass must finish its own setup"
- `24_Patterns--Template_Method` 2026-08-29, was Claude-written:
  "Python functions are first-class, so you can also pass the steps" ->
  "Because Python functions are first-class, you can also pass the steps"
- `25_Patterns--Surrogate` 2026-08-31, was Claude-written:
  "*GoF Design Patterns* gives *Proxy* and *State* different structures
  and so treats them as unrelated" -> "Because *GoF Design Patterns*
  gives *Proxy* and *State* different structures, it treats them as
  unrelated"

**Home.** this file only. Promoted at Bruce's call (2026-08-29); first
independent-chapter sighting 2026-08-31.

### R5. In a labeled list, end the label with a period and explain in sentences

**Test.** A bullet whose lead-in ends with a colon followed by a lowercase
clause, typically starting "it" ("The type checker, via `@final`: it
reports an override."). End the label with a period and write the
explanation as full sentences; a following sentence that refers back to
the label starts "This".

**Keep when.** None seen yet. A colon introducing a listing or a literal
value is not a label.

**Sightings.** 4, one list in `24_Patterns--Template_Method` 2026-08-29, was
Claude-written:
- "Structure, in `template_function.py`: no subclass exists, so nothing
  can replace the loop." -> "Structure, in `template_function.py`. There
  is no subclass, so nothing can replace the loop."
- "Discipline, via the Liskov Substitution Principle: it governs whether
  each step is a faithful substitute" -> "Discipline, via the Liskov
  Substitution Principle. This governs the semantics of whether each step
  is a faithful substitute"
- the `@final` and `__init_subclass__()` items likewise (see R2).

**Home.** this file only. Promoted at Bruce's call (2026-08-29).

### R6. "is required to" becomes "must"

**Test.** "is/are required to VERB" (and "was/were required to"). Replace
with "must VERB" ("had to VERB" in the past).

**Keep when.** A requirement is the subject and named as such ("the
requirement is that..."); a passive reporting who requires it ("the
caller is required by the protocol to...") loses the agent if changed
blindly.

**Sightings.** 1, `24_Patterns--Template_Method` 2026-08-29 (`19b2b1e3`), was
Claude-written:
- "If every subclass is required to supply a step" -> "If every subclass
  must supply a step"

**Home.** CLAUDE.md watch list (global, Writing Style). Promoted at Bruce's
call (2026-08-29).

### R7. Cut the sentence that only points at the next listing

**Test.** A sentence whose only content is a pointer to an adjacent
listing or example ("The example below shows why.", "The following
listing demonstrates this.") with no claim of its own. Delete it; the
listing follows anyway. The same holds for a forward pointer to the next
example or to the rest of the chapter ("The rest of this chapter
replaces call sites like these with ...", "The next example,
`registry.py`, cannot take the same fix. Its whole point is that ...")
where the paragraph that follows makes the claim on its own. The same
holds for a sentence that only announces a list that follows.

**Keep when.** The pointer carries a claim the listing does not make on
its own ("The next listing shows the same trap in a generator").

**Sightings.** 6 (removal), 3 chapters
- `26_Patterns--Factory` 2026-09-01 (`0b7ff81d`), was Claude-written:
  "The next step gives each of those operations its own object." ->
  deleted, ahead of "A *factory object* defines a single `create()`
  method"; "No factory method and no factory class. The `dict` is the
  factory:" -> "No factory method and no factory class:"
- `26_Patterns--Factory` 2026-09-12 (`a03658af`), was Claude-written:
  "The rest of this chapter replaces call sites like these with a
  single place that knows about every shape." -> deleted; the next
  paragraph opens "The solution is to encapsulate object creation."
- `26_Patterns--Factory` 2026-09-12 (`a9731125`), was Claude-written:
  "The next example, `registry.py`, cannot take the same fix. Its whole
  point is that a new `Shape` subclass registers itself" -> "It would
  be even nicer if a new `Shape` subclass would register itself"
- `24_Patterns--Template_Method` 2026-08-29, was Claude-written:
  "The example below shows why." -> deleted
- `27_Patterns--Function_Objects` 2026-09-16, was Claude-written, a list rather than a
  listing: "The alternatives this chapter showed form one list. Go down
  it and stop at the first form that supports what you need:" -> "Stop
  at the first form that supports what you need:"
- `29_Patterns--Changing_the_Interface` 2026-09-16 (`8f94e3f7`), was
  Claude-written, a pointer to a later section: "[Telling the Wrappers
  Apart](#telling-the-wrappers-apart) sorts the four apart." -> deleted
  from the chapter opening

**Home.** activate (Accrued patterns), which already cuts metadiscourse;
this sighting is the concrete pair for it. Promoted at Bruce's call
(2026-08-29).

### R8. Cut a list item's capstone that ranks it against its siblings

**Test.** The last sentence of a list item or paragraph that restates the
item's point as superiority over the others ("It reaches what the other
three cannot: ...", "Only this one catches ...") and adds no mechanism.
Delete it.

**Keep when.** The comparison is the mechanism (the sentence says what the
others miss and why).

**Sightings.** 1 (removal), `24_Patterns--Template_Method` 2026-08-29, was
Claude-written:
- "It reaches what the other three cannot: what the steps do once the flow
  itself is safe." -> deleted

**Home.** this file only. The weakest test in the store; apply with care.
Promoted at Bruce's call (2026-08-29).

### R9. Name the concrete thing instead of a vague adverb or a negation

**Test.** "directly", "potentially", "possibly", a description by what
does not happen ("an attribute nothing reads"), or a vague "other" /
"the only other" whose excluded item can be named, where the concrete
means, frequency, kind, or item can be named ("as arguments",
"sometimes", "a type-checking attribute", "apart from the new
subclass"). Also a bare `only X` whose excluded item the context can
name: write the item ("catches only `AttributeError`" -> "catches
`AttributeError` and lets every other exception propagate"). State
the item's fate positively where a positive exists; "and not Y" is the
fallback (Bruce, 2026-10-04: a negative statement costs the reader the
effort of turning it into what it means). For "directly" and the other
vague adverbs (87 sites in the book-wide report, most of them
"directly"), Bruce's ruling of the same day: write the concrete word
where the listing supports one, and delete the adverb where no concrete
word exists; "directly" rarely changes a sentence's meaning.

**Keep when.** The concrete word is unknown or would be wrong; a hedge
that is the claim ("potentially unbounded") stays. An `only X` whose
alternative is unbounded ("accepts only keyword arguments") stays.

**Sightings.** 7 (additive), 2 chapters, plus about 55 `only X` sites in
roughly 25 files from 2026-10-04 (`c06fecc2`), the `only` sweep applying Bruce's rulings on the Only Shapes page:
- `25_Patterns--Surrogate`: "`hasattr()` catches only `AttributeError`"
  -> "`hasattr()` catches `AttributeError` and lets every other
  exception propagate"
- `46_Effects--Stateless`: "a double that overrides only `print()`" ->
  "a double that overrides `print()` and inherits `input()`"
- `26_Patterns--Factory`: "it lists only direct subclasses" -> "it lists
  direct subclasses and misses their descendants"; "adding a new type
  only changes the factory" -> "changes the factory and no call site"
- `Solutions/46_Effects--Stateless`: "the handler answers only
  `Need[Console]`" -> "answers `Need[Console]` and not `Need[Clock]`"
- Widened to cover `only X` on 2026-10-04, at Bruce's approval.
- `26_Patterns--Factory` 2026-09-01 (`2b18eed8`), was Bruce-written
  (older draft): "you will likely extend your program" -> "you often
  extend that program"; "first use polymorphism to create a common
  interface" -> "first create a base type as a common interface"
- `26_Patterns--Factory` 2026-08-31 (`2b18eed8`), was Bruce-written
  (older draft): "`factory()` is now the only other code that changes"
  -> "Apart from the new subclass itself, `factory()` is the only code
  that changes"; and, Claude-written, "and rules span the steps" ->
  "and some rules apply across several steps"
- `24_Patterns--Template_Method` 2026-08-29, was Claude-written:
  "pass the steps in directly" -> "pass the steps as arguments"
- "an attribute nothing reads" -> "a type-checking attribute"
- "code written later, potentially years later" -> "code written later,
  sometimes years later"
- `29_Patterns--Changing_the_Interface` 2026-09-16 (`144c546f`), was
  Claude-written: "The variations above are Java habits." -> "All three
  approaches carry one Java habit: the adapter inherits from `WhatIWant`
  so that `op()` accepts it."

- `44_Effects--Effect_Management` 2026-10-21 (the edit-start-44 pass, approved on the fault-review page), three:
  "One call up, the side effect is invisible" -> "In the caller, the side
  effect is invisible"; "a caller sees the same thing from each" -> "a
  caller receives `None` from each"; "perform Effects their signatures
  leave out" -> "perform Effects, and their signatures show only the
  arguments and the return type"

**Home.** this file only. Promoted at Bruce's call (2026-08-29).

### R10. Replace a judgment or figure about a mechanism with the mechanism

**Test.** A phrase that evaluates or characterizes rather than describes
("costs nothing", "satisfies", "is the exception", "they expect"), or a
scare-quoted idiom, where the sentence can state what actually happens.
Ask what the reader would observe; if the phrase does not say, replace it.

**Keep when.** The judgment is the claim being made and the mechanism is
already stated nearby, as in a summary sentence that closes a section.

**Sightings.** 17 (3 chapters)
- `25_Patterns--Surrogate` 2026-08-31, was Claude-written, five:
- "puts the check where it costs nothing" -> "puts the check where it
  does not restrict the surrogate"
- "The guard also satisfies `copy` and `pickle`" -> "The guard also makes
  the proxy work with `copy` and `pickle`"
- "both get the `AttributeError` they expect" -> "both get an
  `AttributeError`, which those modules handle"
- "Inheritance is the exception:" -> "Inheritance satisfies both."
- "As long as `Proxy` "speaks for" the class it forwards method calls to"
  -> "As long as code calls `Proxy` in place of the class that `Proxy`
  forwards method calls to"
- `26_Patterns--Factory` 2026-09-01, was Claude-written, three:
  "The registry also never forgets:" -> "The registry also never
  removes an entry:"; "The chained call in `__main__` hides the problem
  by throwing the builder away on the same line that creates it" ->
  "never shows the problem, because it keeps no reference to the
  builder after `build()` returns"; "each implementation picks a side"
  -> "chooses one behavior or the other"
- `26_Patterns--Factory` 2026-08-31 (`40323f50`, `2b18eed8`), five
  more, logged 2026-09-15: "hands `cls.__name__` straight to
  `factory()`" -> "passes `cls.__name__` unchanged to `factory()`"; "A
  *factory object* carries a single `create()` method" -> "defines a
  single `create()` method"; "choosing which object to ask" ->
  "choosing which factory object to call"; "calls it right away" ->
  "calls its `create()` immediately"; and, in Bruce's own older draft,
  "the most sensible first step is to use polymorphism" -> "first use
  polymorphism"
- `27_Patterns--Function_Objects` 2026-09-16, was Claude-written, four, three of
  them flagged by Bruce as a pasted phrase: "bisection declines by
  returning `None`" -> "bisection fails by returning `None`"; "the
  strategy keeps reading those settings after the outer function
  returns" -> "those settings stay available to the strategy after the
  outer function returns"; "because the languages behind those forms
  have no entries above it" -> "The C++ of that book had no lighter
  form that could carry state: a function pointer carried none, and
  closures did not exist yet"; "a `dict` from each event type to the
  functions subscribed to that type" -> "a `dict` keyed by event type.
  Each key maps to a list of handlers, and `subscribe()` appends a
  handler to the list under the event type it handles"
- `29_Patterns--Changing_the_Interface` 2026-09-16, four: "That interface
  makes a library or bundle of resources more comfortable to use" ->
  "The caller sees one entry point and never learns how those classes
  are built and wired together, so the wiring can change without
  affecting the caller" (`1f73cfad`, Bruce's older draft); "When you've
  got "this", and you need "that", *Adapter* solves the problem. The
  adapter needs only to produce a "that"." -> "An adapter's only job is
  to produce the interface you need from the one you have." (`2c5dbf6f`,
  Bruce's older draft, scare quotes gone); "Marking the old interface
  makes the risk visible on a schedule; without the mark, the risk
  surfaces when you delete something." -> "Marking it deprecated keeps
  it working while it tells each caller what to use instead; without
  the mark, nothing tells them."; "someone decided to retire this" ->
  "this should no longer be called" (both `f5a7b213`, Claude-written)

- `31_Patterns--State_Machines` 2026-10-18, Bruce's note "garbled,
  incomprehensible": "so data a state keeps for one machine has nowhere
  to go" -> "so a value stored on a member is shared by every machine
  too"; Solutions 47 the same day: "the request has nowhere to carry
  the range" -> "the request has no field to carry the range"

- `44_Effects--Effect_Management` 2026-10-21 (the edit-start-44 pass, approved on the fault-review page), five:
  "the check moves out of `slope()` and into the type" -> "the type's
  `__post_init__()` runs the check instead of `slope()`"; "escaping
  `slope()` as an exception" -> "reaching `slope()`'s caller as an
  exception"; "instead of touching every call site" -> "modifying";
  "checking the ones you left out takes the language" -> "Only a language
  with native Effects can find the ones you left out, because only its
  compiler reads every call in the body"; "one read of that function
  settles the question" -> "tells you what's happening"

- `45_Effects--Generators` 2026-10-22, Bruce's note "vague" on "states
  the arrangement", then "check and fix the rest of the chapter" and
  "the rest of the book": "so the annotation states the arrangement
  and a type checker enforces it" -> "so the annotation says which
  kind of value each channel carries, and a type checker rejects a
  value on the wrong channel"; "`next()` and `send()` do that work"
  -> "run the body"; "the same shape of trace" -> "the trace gains
  one more `request` line and one more `ask()` line". Fifteen more in
  that chapter, and a book-wide sweep the same day (one Opus agent per
  chapter, about 150 edits). The shape is now the `literal` skill's
  "Vague descriptions" section and the deep-review prose pass's
  "Vague" lens.

- `45_Effects--Generators` 2026-11-01, three sites, Bruce: "vague",
  "sounds like it does the same involving a GeneratorExit", "'lets the
  exception through' is vague": "The exception channel runs the other
  way as well." -> "`throw()` and `close()` deliver an exception from
  the driver into the generator. An exception can travel the opposite
  direction too, from the generator into the driver."; "`close()` does
  the same with a `GeneratorExit` exception." -> "`close()` resumes the
  generator and raises `GeneratorExit` at that `yield`."; "The body lets
  the exception through" -> "`pause()`'s `try` has a `finally` clause
  and no `except`, so Python runs the `finally` block ... and the
  `ValueError` propagates out of the generator."

**Home.** literal (Accrued patterns and the "Vague descriptions"
section), the pass that owns figures; deep-review (prose pass, "Vague").
Promoted 2026-09-01 on the second chapter's sightings (C3 -> R10).

### R11. Cut a scope phrase the book already supplies

**Test.** "In Python", "in Python code", "in your code", "in the system",
"in this design" introducing or qualifying a claim that the chapter
already scopes that way. Delete the phrase.

**Keep when.** The phrase contrasts with another language or another
system ("in Python, unlike Java"), which is the usual reason it was
written.

**Sightings.** 3 (2 chapters)
- `25_Patterns--Surrogate` 2026-08-31, was Claude-written:
  "In Python both are the same few lines of `__getattr__()` delegation"
  -> "Both are the same few lines of `__getattr__()` delegation"
- `26_Patterns--Factory` 2026-09-01, was Claude-written:
  "every place in your code that names a concrete type" -> "every place
  that names a concrete type"
- `26_Patterns--Factory` 2026-09-01, was Bruce-written (older draft):
  "the only other code in the system that needs to change" -> "the only
  other code that changes"

**Home.** CLAUDE.md watch list (global, Writing Style). Promoted
2026-09-01 (C5 -> R11, widened from "In Python" to the family).

### R12. Name a pointer's antecedent only where a competitor exists

**Test.** A pronoun, a clause-level "which", a "there", or a bare "the
class" with a competing candidate in reach gets its noun; one whose
subject just appeared unopposed keeps the pronoun. A refinement of the
`/antecedents` pass rather than a new sweep: that pass fires on
ambiguity, not on pronouns.

**Keep when.** This *is* the keep-when for `/antecedents`. The reverse
sighting from chapter 26 below is the point of the entry: a sweep that
reads the others as "prefer the noun" will overshoot.

**Sightings.** 18 (2 chapters)
- `26_Patterns--Factory` 2026-08-31 (`40323f50`), was Claude-written,
  six: "It covers only the first level of inheritance" ->
  "`__subclasses__()` covers only the first level of inheritance"; "It
  registers itself" -> "`Triangle` registers itself"; "They fail at
  call time" -> "Those bodies fail at call time"; "There the table
  holds classes" -> "In `registry.py` the table holds classes"; "which
  puts the creation method on a class" -> ": that pattern puts the
  creation method on a class"; "which is worse than unnecessary" ->
  "and that dispatch is worse than unnecessary"
- `26_Patterns--Factory` 2026-09-14 (`7ec15c2e`), was Claude-written:
  "the class solves a problem Python does not have" -> "the builder
  class solves a problem Python does not have" (competitor: `Pizza`)
- `25_Patterns--Surrogate` 2026-08-31, was Claude-written, eleven. Ten
  resolved a pointer that had a competitor:
  - "it calls that method in the implementing class" -> "the surrogate
    calls that method in the implementing class"
  - "the class it forwards method calls to" -> "the class that `Proxy`
    forwards method calls to"
  - "constructing it raises a `TypeError`" -> "constructing a `Partial`
    raises a `TypeError`"
  - "the type checker verifies its `f()` and `g()`" -> "the type checker
    verifies the `Proxy`'s `f()` and `g()`"
  - "the lookup on `type(p)` finds that one" -> "the lookup on `type(p)`
    finds `object`'s `__str__()`"
  - "For example, it can count the references" -> "For example, a smart
    reference can count the references"
  - "Give it a `__len__()` that forwards" -> "Give that `Proxy` a
    `__len__()` that forwards"
  - "instead of running attribute lookup, and never calls
    `__getattr__()`" -> "instead of running attribute lookup. That
    function never calls `__getattr__()`"
  - "It also ties this surrogate to one Protocol" -> "That annotation
    also ties the surrogate to one Protocol"
  - "which is what the generic surrogate exists to avoid" -> "and that
    tie is what the generic surrogate exists to avoid"

  One went the other way, where the subject had just appeared unopposed:
  - "because `Proxy` names no methods in `Implementation`, the proxy
    keeps working" -> "because `Proxy` names no methods in
    `Implementation`, it keeps working"
- `29_Patterns--Changing_the_Interface` 2026-09-16, was Claude-written:
  "Because `WhatIUse` calls `f()` and `WhatIHave` has none" -> "and
  `WhatIHave` has no `f()`"

- `44_Effects--Effect_Management` 2026-10-21 (the edit-start-44 pass, approved on the fault-review page), five:
  "every exception it raises" -> "every exception `slope()` raises";
  "Setting the wrong one ... in whatever frame reads it" -> "the wrong
  `ContextVar` ... in the frame that reads the `ContextVar`"; "the way
  `async def` already declares one" -> "declares `async`"; "you find
  them by inspection" -> "find Effects"; "A system that does so is" ->
  "That type system is"

- `45_Effects--Generators` 2026-11-01, Bruce: "this?": "Why does the
  driver need a method for this, when Python already has `raise`?" ->
  "Why does the driver need methods to raise exceptions inside the
  generator, when Python has a `raise` statement?"

**Home.** the `antecedents` skill, as a keep-when (its "zero ambiguous
pointers, not zero pronouns" line). Not a separate sweep. Promoted
2026-09-15 on chapter 27's sightings (C6 -> R12).

### R13. Next to a cross-reference link, cut the sentence that restates the target's content

**Test.** A sentence or trailing clause beside a link whose claim the
linked section states (read the target to confirm), where the
paragraph's argument stands without it. Delete the sentence, keep the
link.

**Keep when.** The paragraph's next step needs the fact and the reader
should not have to follow the link to get it. The contrast reading C4
started with ("how this differs from the previous section's subject")
is not the rule; the chapter that owns a comparison carries it.

**Sightings.** 4 (removal), 2 chapters
- `25_Patterns--Surrogate` 2026-08-31, was Claude-written: "That refusal
  separates a *Proxy* from a *Decorator*: a decorator adds behavior
  around a call it always makes. This proxy decides whether to forward
  the call." -> "`Guarded` requires `admin` privileges to call
  `erase()`." The Proxy/Decorator comparison lives in
  `29_Patterns--Changing_the_Interface`'s table.
- `25_Patterns--Surrogate` 2026-08-31, was Claude-written: "A *Smart
  reference* proxy adds behavior around each access without refusing
  any." -> "A *Smart reference* proxy adds behavior around each
  access." A contrast cut with no link beside it; the narrowing sets
  this sighting aside rather than claiming it.
- `26_Patterns--Factory` 2026-08-31 (`d6144479`), was Claude-written:
  "a convention rather than concealment, and the convention is all
  Python provides ([Singleton](...) makes the same case)" -> "a
  convention rather than concealment ([Singleton](...) makes the same
  case)". Chapter 24's linked section says "Privacy in Python is advice,
  not enforcement."
- `26_Patterns--Factory` 2026-09-15 (`a9ca27eb`), was Claude-written:
  "`copy.replace()` is the general form of the same operation, working
  on any object that defines `__replace__()`, shown in [The General
  Form of `replace()`](...). A data class defines that method for you."
  -> "`copy.replace()` is the [general form of the operation](...), and
  works on any object that defines `__replace__()`." Chapter 12's
  linked section says `copy.replace()` works on a frozen data class and
  anything else that defines `__replace__()`.

**Home.** this file only. Promoted 2026-09-15, narrowed from C4's
contrast reading (C4 -> R13).

### R15. Make the mechanism the subject where the sentence describes how a design behaves

**Test.** An imperative ("make a common factory create every object")
or a "you can VERB" ("you can remove that line by letting each subclass
register itself") whose content is how the design works rather than
advice to the reader. Put the mechanism in subject position with an
indicative verb: "A common factory creates every object"; "Letting each
subclass register itself removes that line".

**Keep when.** The sentence is advice or an exercise instruction ("Use a
`set` for membership tests"), or "you can" where the option's existence
is the news (the `activate` skill's existing keep, "You can supply a
different `Console` in a test").

**Sightings.** 5 (additive), 2 chapters:
- 2026-08-31 (`40323f50`), was Claude-written: "You can remove that
  line too, so the factory never needs editing when you add a type, by
  letting each subclass register itself through `__init_subclass__()`"
  -> "Letting each subclass register itself through
  `__init_subclass__()` removes that line too, so the factory never
  needs editing when you add a type"
- 2026-08-31 (`2b18eed8`), was Bruce-written (older draft): "Thus you
  can isolate, in one place, the effect of changing from one GUI to
  another." -> "The change from one GUI to another then touches one
  place in your code."
- 2026-09-12 (`a03658af`), was Bruce-written (older draft): "The
  solution is to encapsulate object creation: make a common *factory*
  create every object" -> "The solution is to encapsulate object
  creation. A common *factory* creates every object"; "so you change
  only the factory when you add a new type" -> "so adding a new type
  only changes the factory"

- `27_Patterns--Function_Objects` 2026-09-16, was Claude-written: "You provide a
  function that decides how to compare." -> "That argument determines
  how comparison works."

- `44_Effects--Effect_Management` 2026-10-21 (the edit-start-44 pass, approved on the fault-review page), three, Bruce's hand:
  "If you call a function that writes to an audit log, your function
  writes to an audit log" -> "If your function calls a function that
  writes to an audit log, your function writes to an audit log" (and the
  clock and `ValueError` sentences beside it)

**Home.** activate (Accrued patterns), beside its "you can" keep.
Promoted 2026-09-16 on the second chapter's sighting (C15 -> R15).

### R16. Carry the cross-reference on the term, not in a citation after it

**Test.** A term followed by a parenthetical "(see [Chapter](...#anchor))"
or a trailing ", shown in [Section](...)", where the term or phrase
could carry the link; or a bare term with a defining section elsewhere
in the book ("the MRO") that could be linked on first use in the
chapter.

**Keep when.** The citation points somewhere other than the term's
definition, or the term is already a link to something else.

Widened 2026-10-04 (Bruce, Sweep Decisions page) to the standalone
pointer sentence ("[Modules and Packages](...) covers the import
system.", about six in chapter 02) when the sentence before it already
names the term: fold the link onto that term and delete the pointer.
Keep a pointer sentence that is the paragraph's whole job, such as a
where-to-read-more sentence closing a section.

**Sightings.** 4, 2 chapters, was Claude-written:
- 2026-08-31 (`d6144479`): "I have also used a *generator* (see
  [Iterators](22_Patterns--Iterators.md#generators))." -> "I have also
  used a [*generator*](22_Patterns--Iterators.md#generators)."
- 2026-08-31 (`0b7ff81d`): "`cls.registry` resolves through the MRO" ->
  "resolves through the [MRO](07_Foundations--Classes.md#inheritance)"
- 2026-09-15 (`a9ca27eb`): "`copy.replace()` is the general form of the
  same operation, working on any object that defines `__replace__()`,
  shown in [The General Form of `replace()`](...)." -> "`copy.replace()`
  is the [general form of the operation](...), and works on any object
  that defines `__replace__()`."
- `27_Patterns--Function_Objects` 2026-09-16: "It is a *closure* ([Functional
  Foundations](40_Functional--Foundations.md#closures)):" -> "use a
  [*closure*](40_Functional--Foundations.md#closures)."

**Home.** this file only: a linking convention rather than a prose
register. Promoted 2026-09-16 on the second chapter's sighting (C12 -> R16).

### R17. A reader's experiment is "If you X, Y", not "X, and Y"

**Test.** An imperative whose only purpose is to set up a hypothetical
for the clause after it ("Uncomment the line, and the checker
reports ..."; "Define a factory class and stop there: creating an
instance still succeeds"). Rewrite as "If you X, Y".

**Keep when.** The imperative is an instruction to follow, as in an
exercise.

**Sightings.** 3, 2 chapters, was Claude-written:
- `26_Patterns--Factory` 2026-09-01 (`6f638b05`): "Uncomment the line
  that passes a `BrokenFactory` to `GameEnvironment`, and the checker
  reports" -> "If you uncomment the line ..., the checker reports"
- `26_Patterns--Factory` 2026-09-01, in conversation: "Define a factory
  class with `make_character()` and stop there: creating an instance of
  it still succeeds" flagged as "still hard to follow"; rewritten with
  Python as the actor
- `29_Patterns--Changing_the_Interface` 2026-09-16 (`974e6f15`):
  "Uncomment the commented-out signature in `adapter_variations.py`,
  `what_i_have: WhatIHave`, and the checker reports:" -> "If you use
  that signature in place of the union, a type checker rejects the
  override"

**Home.** CLAUDE.md (global, Writing Style), which already states it as
"No imperative-plus-consequence sentences"; this entry holds the pairs.
Promoted 2026-09-17 on the second chapter's sighting (C9 -> R17).

### R18. Cut the sentence that says what the output demonstrates when the output is on the page

**Test.** A sentence after a listing whose subject is the output and
whose predicate is a verdict on it ("is the point", "produce the same
three lines", "is deliberately monotonous"). Cut it; the markers show
the output.

**Keep when.** The sentence states a consequence the output does not
show on its own (why the lines match, what a difference would mean).

**Sightings.** 3 (removal), 2 chapters, was Claude-written:
- `27_Patterns--Function_Objects` 2026-09-16: "Three identical lines are
  the point: the algorithm changes and the caller stays the same." ->
  deleted
- `27_Patterns--Function_Objects` 2026-09-16: "Those five classes
  produce the same three lines that one function argument produced."
  -> deleted
- `29_Patterns--Changing_the_Interface` 2026-09-16 (`44ec1a58`): "The
  output is deliberately monotonous." -> deleted, after
  `adapter_variations.py`'s six identical marker lines

**Home.** this file only. Promoted 2026-09-17 on the second chapter's
sighting (C20 -> R18).

### R19. Cut the sentence that restates the one before it, or the chapter's opening

**Test.** Two consecutive sentences where the second says the first
again at a different altitude (abstract after concrete, or a claim
after its example); or a section's first sentence that restates the
chapter's opening claim; or (widened 2026-10-11) a paragraph or a
closing section whose every sentence restates what a listing on the
page or an earlier paragraph already established. Keep the concrete
one, or the opening; cut the recap.

**Keep when.** The second sentence, or the recap, adds a consequence or
a mechanism the earlier text did not state. A contrast drawn across
several listings that no one listing shows is such a consequence.

**Sightings.** 9, 3 chapters
- `26_Patterns--Factory` 2026-09-15 (`a9ca27eb`), was Claude-written:
  "Builder chains have a second use, starting from an existing
  configuration and varying it, covered by `dataclasses.replace()`."
  -> "A second use for builder chains is to vary an existing
  configuration." (the next sentence names `replace()`); "Each stage
  relies on what the previous stage established." -> "Each stage relies
  on the previous stage."
- `26_Patterns--Factory` (`2b18eed8`), was Bruce-written (older draft):
  "You must still find and edit every place that names a concrete type.
  Creation names the type. Use does not, because polymorphism handles
  use. The effect is the same: adding a new type means edits scattered
  through the code." -> "adding a type means finding and editing every
  place that names a concrete type."
- `26_Patterns--Factory` (`0b7ff81d`), was Claude-written: "No factory
  method and no factory class. The `dict` is the factory:" -> "No
  factory method and no factory class:"; "The next step gives each of
  those operations its own object. A *factory object* defines a single
  `create()` method" -> the second sentence alone
- `29_Patterns--Changing_the_Interface` 2026-09-16 (`f99192e5`), was
  Bruce-written (older draft), the section-opening shape: "When you've
  got "this", and you need "that", *Adapter* solves the problem." ->
  deleted from the Adapter section's opening; the chapter's first
  sentence already says "I don't have the interface I need."
- `30_Patterns--Observer` 2026-10-11 (the pass 2e61b3e7..HEAD), Bruce's
  hand, the recap shape: the "Four Scenarios, One Shape" section
  deleted whole; the binding-times advice paragraph at the chapter's
  end cut; two MVC paragraphs marked "[[just recapitulates the code]]"
  and then cut.

**Home.** this file only. Promoted 2026-09-17 on the second chapter's
sighting, widened from consecutive sentences to the section-opening
restatement (C8 -> R19); widened 2026-10-11 to the recap paragraph and
section, approved on the fault-review page.

### R20. Say when the earlier state held instead of "used to"

**Test.** Past-habitual "used to" ("a metaclass used to handle", "This
used to be a Windows concern"). Say when the earlier state held
("before 3.14", "before those hooks existed", "before the change") or
state the present. The purpose sense ("is used to preserve") is a
different phrase, and House.WeakVerb reports it.

**Keep when.** None seen yet.

**Sightings.** 7 (additive), 7 files, 2026-09-17 (`cacb544f`), all
Claude-written; Bruce named the rule ("'that used to' is generally
mushy") on chapter 29's sentence:
- `29_Patterns--Changing_the_Interface`: "A function that used to take a
  string and now takes a `Path` can then warn only the string callers."
  -> "A function that now takes a `Path` in place of a string can then
  warn only the callers still passing a string."
- `17_Techniques--Metaprogramming`: "every case a metaclass used to
  handle" -> "every case a metaclass handled before those hooks existed"
- `19_Techniques--Concurrency`: "This used to be a Windows and macOS
  concern only" -> "Before 3.14 this was a Windows and macOS concern
  only"
- `40_Functional--Foundations`: "fixing the third argument used to mean
  fixing the first two" -> "before 3.14, fixing the third argument
  meant fixing the first two"
- `Solutions/28`: "a bus where `BigDeposit` used to reach only `on_big`
  now reaches" -> "a `BigDeposit` that reached only `on_big` before the
  change now reaches"
- `Solutions/46`: "That change buys a diagnostic where a coin flip used
  to be." -> "That change turns the coin flip into a diagnostic."
- `Solutions/47`: "the evening hours the battery used to cover" -> "the
  evening hours the battery covered before it was added"

**Home.** `styles/House/UsedTo.yml` (a vale warning, in place
2026-09-17) and the CLAUDE.md watch list (global, "Consider rewriting"
tier). Promoted at Bruce's call (2026-09-17, "accept all").

### R21. A colon that joins a claim to its explanation becomes a sentence break

**Test.** A prose colon whose right side is a full clause explaining,
justifying, or expanding the claim on its left ("Subscriptions are
strong references: an observable that outlives its observers keeps
alive ..."). End the claim with a period and let the explanation stand
as its own sentence, capitalized; where the right side is the cause of
the left, reorder so the cause comes first and join with a comma or
"so". Two such colons in adjacent sentences ("X is one use: ... Y is
another: ...") are the strongest signal; recast both ("In X, ... In Y,
..."). Adjacent to a code span containing a colon (`always: 1`), the
prose colon goes even when it is the only one.

**Keep when.** The colon introduces a listing, a bulleted or numbered
list, or a run of parts ("has three parts: an `Observer` interface, a
`Subject` base class, and a `notify()`"); defines a term ("defines only
the communication: a list of callables and the argument it passes
them"); or supplies a direct answer to what the left side sets up ("GoF
leaves one choice open: who calls `notify()`"). R5 covers the colon
after a bullet's label.

Bruce's ruling on the 2026-10-04 book-wide report, where R21 had 501
sites and only 157 rated high-confidence: "Lean towards splitting
sentences at colons." So a medium-confidence site is applied; the
keep-whens above hold where they clearly apply, and a split that
leaves a fragment is the one other reason to keep the colon.

Extended to semicolons on 2026-10-04, after Bruce approved chapter 30:
"Go through the book looking for sentences that can be split into
smaller sentences at ':' or ';'." A semicolon joining two independent
clauses is a site under the same test; the style guide's "tightly
linked" exception and a semicolon separating comma-bearing items are
the keeps.

**Sightings.** 3 rounds, 21 chapters. Bruce named the rule on chapter
30 (2026-09-17, "There are colons that could be removed in favor of
separate sentences"):
- `30_Patterns--Observer` 2026-09-17 (`15f58a2d`), twelve colons, all
  Claude-written: "Subscriptions are strong references: an observable
  that outlives its observers keeps alive the instance" -> "Subscriptions
  are strong references. An observable that outlives its observers keeps
  alive the instance"; "Event handling is one use: a widget keeps a list
  of handlers ... The model-view split is another: the data keeps a list
  of views" -> "In event handling, a widget keeps a list of handlers ...
  In the model-view split, the data keeps a list of views"; "Without the
  copy, `always: 1` would be missing: `once`'s self-removal would skip
  `always`." -> "Without the copy, `once`'s self-removal would skip
  `always`, and `always: 1` would be missing."; "but not here: it cancels
  a failing task's siblings" -> "but not here. A `TaskGroup` cancels a
  failing task's siblings"
- `26_Patterns--Factory` 2026-09-12 (`571d9ec2`): "Both are static
  methods of the type: each takes data and returns an instance" -> "Both
  are static methods within the type. Each takes data and returns an
  instance"; "`of()` needs no `match`, because the `Enum` already holds
  every member it could return: it indexes `list(Month)`" -> "`of()`
  needs no `match`. The `Enum` already holds every member it could
  return, so `of()` indexes `list(Month)`"
- 19 chapters 2026-09-12 (`19f80f40`, "Fewer colons in 26 prose
  paragraphs"), the per-paragraph density sweep (three or more colons
  in one paragraph): `34_Patterns--Composite_and_Interpreter`: "One
  practical limit applies: every function here recurses once per level
  of tree" -> "One practical limit applies. Every function here recurses
  once per level of tree"

**Home.** this file only; the 2026-09-12 sweep is recorded in project
memory `colon-splice-audit-completed`. Promoted at Bruce's call
(2026-09-17).

### R22. In Solutions/, label each step paragraph with what its lines accomplish

**Test.** In a `Solutions/*/README.md` file, inside a solution's
"Solution" step, a discussion paragraph that follows a listing and
explains one group of that listing's lines, with no opening label. Open
it with a bold label ending in a period inside the bold: a verb phrase
of two to six words naming what the group accomplishes,
context-independent, the kind of phrase that fits any implementation of
the same design ("Collect the responders.", "Keep the loop going past a
failure.", "Return the descriptor on class access."). Name the function
of the step, not its content: "Append to the list." is content and is
wrong; "Collect the responders." is function and is right. Labels follow
listing order, three to six per solution; split a paragraph that covers
two groups, merge two short paragraphs that cover one. The explanation
after the label is full sentences, as R5 requires. This is an additive
rule: it adds a label where the paragraph had none. A literature report
on exercise and solution design (`reports/Exercise and solution design
for learning.md`) found subgoal labels on worked examples carry a medium
learning effect (Morrison, Margulieux, and Decker: d = .59 on far
transfer, half the withdrawals).

**Keep when.** A paragraph that is not about a group of lines gets no
label: a closing comparison of two versions, a remark on running the
demo, a paragraph about a test file that explains no step, the "If you
..." contrast paragraph that opens a solution, and the `Hint:`
paragraph. A one-paragraph discussion of a short listing may carry one
label or none.

**Sightings.** 3
- `Solutions/28_Patterns--Data_Transfer_Objects` 2026-10-02, the three
  labeled paragraphs "**The configuration bag is a `SimpleNamespace`.**",
  "**The grid coordinate is a `NamedTuple`.**", and "**The JSON record
  is a `@dataclass`.**" These name a thing rather than a step, so they
  are the form's precedent rather than a full match.
- `Solutions/30_Patterns--Observer` 2026-10-03 (`93ad36e0`), was
  Claude-written at Bruce's request, 33 labels over 11 solutions:
  - "Like `broadcaster.py`, this solution has no separate `Observer`
    class ..." -> "**Collect the responders.** Like `broadcaster.py`,
    this solution has no separate `Observer` class ..."
  - "`ExceptionGroup` is the right container because more than one
    responder ..." -> "**Report every failure together.**
    `ExceptionGroup` is the right container because more than one
    responder ..."
  - "The results come back in argument order, so the list is a record
    of ..." -> "**Pick out the failures.** The results come back in
    argument order, so the list is a record of ..."
- `Solutions/` sweep 2026-10-03 (`85f6ce4d`): 523 labels across the
  other 44 Solutions files, three to six per solution where the
  discussion walks the listing, none on closing comparisons, test-file
  remarks, or prediction exercises. One pair from Solutions 31:
  - "Each state decides its own successor. `Happy.next()` answers
    `Annoy` ..." -> "**Let each state pick its successor.** Each state
    decides its own successor. `Happy.next()` answers `Annoy` ..."

**Home.** this file only. Promoted at Bruce's call (2026-10-03) on one
file's evidence, as R2-R9 were; the 2026-10-03 sweep over the other 44
Solutions files (the third sighting) confirmed it.

### R23. Open a solution with the wrong approach the reader likely took

**Test.** A solution in `Solutions/*/README.md` whose exercise has a
specific wrong approach that the chapter demonstrates failing, that the
exercise or hint rules out by name, or that is the direct simplification
of the solution dropping one part (one keyword, one `list(...)` copy,
one `return fn`). Open the "Solution" step, before the listing, with one
paragraph beginning "If you ..." that names the approach, states its
observable consequence, and says why the solution takes the other path.
Two to four sentences. Every stated consequence is reproduced by running
the wrong variant before it is written. This is additive: the paragraph
contrasts the reader's likely attempt with the canonical solution, the
device Loibl and Rummel (2014) tested, from the same report as R22.

**Keep when.** No qualifying wrong approach exists; do not invent one.
In Solutions 30, four of eleven solutions (1, 5, 7, 8) have none.

**Sightings.** 2
- `Solutions/30_Patterns--Observer` 2026-10-03 (`93ad36e0`), was
  Claude-written at Bruce's request: seven paragraphs.
  - Exercise 3, inserted before the listing: "If you catch each exception
    and move on without keeping it, every responder runs, but `announce()`
    returns normally. The demo's `except*` block does not run, so the
    script prints nothing, and the test's `pytest.raises(ExceptionGroup)`
    fails with "DID NOT RAISE". The solution keeps each exception in a
    list and raises the list as one `ExceptionGroup` once the loop ends."
- `Solutions/` sweep 2026-10-03 (`85f6ce4d`), was Claude-written at
  Bruce's request: 128 "If you ..." paragraphs across 40 of the other 44
  Solutions files, each consequence reproduced by running the wrong
  variant. One, from Solutions 23 exercise 3:
  - "If you slice the generator the way you would a list,
    `fibonacci(1_000_000)[:10]` raises a `TypeError`, because a generator
    defines no `__getitem__()`. The type checker rejects the slice before
    the program runs, and `ty` reports it as `not-subscriptable`.
    `islice()` slices an iterator by pulling from it, as [Reusable
    Algorithms](../../Chapters/22_Patterns--Iterators.md#reusable-algorithms)
    notes."

**Home.** this file only. Promoted 2026-10-03 on the second sighting, per
the preamble's rule.

---

### R24. `only`: keep it, delete it, or fix the words around it

**Test.** Three outcomes, in order. *Keep* when the restriction is the
claim and the sentence reads cleanly; six whole shapes were ruled fine
as a class (sentence-initial "Only", "the only X", "only when/if", "only
the/a X", "only in/for/at", clause-final "only"). *Delete* when the
sentence already bounds: a count or "once" followed by a bounding clause,
a following "not" clause, or a next sentence that carries the exclusion.
*Rewrite* when the words around `only` are the problem: R25-R28, C28,
C29 name the shapes. A rewrite that names the excluded item states
its fate positively where a positive exists ("inherits `input()`",
"leaves `Need[Clock]` open"), since a "not Y" is a negative too
(Bruce, 2026-10-04). Bruce's ruling (2026-10-04): "In many cases, 'only'
is fine. In some 'only' can be removed. In other cases, it's not
necessarily the 'only' but the wording around it that makes it awkward
and confusing."

**Keep when.** The restriction is the claim. A compound (`read-only`,
`keyword-only`), a quotation, a diagnostic, a heading echoed in link
text.

**Sightings.** 154 sites in 60 files, 2026-10-04 (`c06fecc2`), the `only` sweep applying Bruce's rulings on the Only Shapes page:
37 deletions, 117 rewrites. Deletions:
- `Solutions/18_Techniques--Performance`: "The `"computing noisy(3)"`
  message prints only once, on the first call." -> "prints once, on the
  first call."
- `Solutions/38_Patterns--Simulation`: "`Robot.__init__()` needs only one
  new line, `self.coins = 0`" -> "needs one new line, `self.coins = 0`"
- `06_Foundations--Modules_and_Packages`: "so the set tracks only names
  still waiting, not names your program ever deferred" -> "tracks names
  still waiting, not names your program ever deferred"
- `17_Techniques--Metaprogramming`: "At runtime the decorator only marks
  the class, setting `__final__ = True`" -> "the decorator marks the
  class, setting `__final__ = True`"
- `46_Effects--Stateless`: "Failures never vanish. They only relocate."
  -> "They relocate."
- `30_Patterns--Observer` 2026-10-11, was Bruce-written (4841947b,
  2026-10-05): "`announce()` runs only once, for the original
  assignment." -> "runs once, for the original assignment." Raised as
  a conflict at the pass's capture, since the `only` had read as
  marking the contrast with the re-entrant run; Bruce's ruling: "'on
  the first call' is enough to imply 'only' in this case," so the
  delete shape stands and the sentence followed it.

**Home.** CLAUDE.md watch list (global, Writing Style), a dedicated
bullet beside the "nothing else" family, written 2026-10-04. The
baseline `tools/data/watch_words_baseline.txt` holds the 688 keeps.

### R25. Put `only` beside the phrase it restricts

**Test.** `only` sits before the verb while a later "when"/"if" clause or
the verb's object carries the restriction. Move it in front of that
phrase.

**Keep when.** The verb is the restricted element; there the choice is
between keeping and deleting (R24), not moving.

**Sightings.** 5, 3 files, 2026-10-04 (`c06fecc2`), the `only` sweep applying Bruce's rulings on the Only Shapes page:
- `18_Techniques--Performance`: "The comparison only holds when the input
  order gives neither side an advantage." -> "The comparison holds only
  when ..."
- `19_Techniques--Concurrency`: "**More cores only speed up the parallel
  fraction of the work.**" -> "**More cores speed up only the parallel
  fraction of the work.**"; "**A shared lock only prevents deadlock if
  every user agrees on the order.**" -> "prevents deadlock only if ...";
  "it has only touched the surface" -> "it has touched only the surface"
- `Solutions/34_Patterns--Composite_and_Interpreter`: "A child only gets
  parentheses when its own operator binds more loosely" -> "A child gets
  parentheses only when ..."

**Home.** CLAUDE.md watch list, inside the `only` bullet (R24).

### R26. "X is the one Y that ..." for an exclusive member

**Test.** `only` before a code span, where the point is that one member
of a known set has the property ("only `depth` appears", "calls only
`f()`", "adds only `accept()`"). Make the member the subject: "X is the
one Y that ...", "whose one Y is X", "leave X as the one open Y".

**Keep when.** The set is open, so "one" would overclaim.

**Sightings.** 6, 5 files (additive), 2026-10-04 (`c06fecc2`), the `only` sweep applying Bruce's rulings on the Only Shapes page:
- `12_Techniques--Data_Classes_as_Types`: "of the three fields only
  `depth` appears as an attribute, because it has an initialization
  value." -> "`depth` is the one field of the three that appears as an
  attribute, because it has an initialization value; `name` and `number`
  have none."
- `29_Patterns--Changing_the_Interface`: "Because at runtime
  `WhatIUse.op()` calls only `f()`," -> "Because `f()` is the one method
  `WhatIUse.op()` calls at runtime,"; "an object that has only
  `next_chunk()`" -> "an object whose one method is `next_chunk()`"
- `33_Patterns--Visitor`: "so it adds only `accept()` to the primary
  hierarchy" -> "so `accept()` is the one method it adds to the primary
  hierarchy"
- `Solutions/12_Techniques--Data_Classes_as_Types`: "`dataclasses.fields()`
  reports only `number`, and the generated signature takes only `number`."
  -> "`number` is the one field that `dataclasses.fields()` reports and
  the one parameter that the generated signature takes."
- `Solutions/24_Patterns--Template_Method`: "and leave only `process()`
  open" -> "and leave `process()` as the one open step"

**Home.** CLAUDE.md watch list, inside the `only` bullet (R24).

### R27. "X alone" where `only` restricts a verb's object

**Test.** `only` after the verb and before its object or a possessive
("concepts only `Maze` uses", "the type of only one of them", "with only
`Need[Butter]`"). Write "X alone".

**Keep when.** An "alone" already sits nearby, or the object is a count
(R24 decides).

**Sightings.** 5, 5 files, 2026-10-04 (`c06fecc2`), the `only` sweep applying Bruce's rulings on the Only Shapes page:
- `38_Patterns--Simulation`: "it names concepts only `Maze` uses" -> "it
  names concepts that `Maze` alone uses"
- `32_Patterns--Multiple_Dispatching`: "a method call resolves the type of
  only one of them, its receiver" -> "a method call resolves its
  receiver's type alone"
- `45_Effects--Generators`: "generators that only yield" -> "generators
  that use the yield channel alone"
- `47_Effects--Stateless_in_Practice`: "with only `Need[Butter]` first" ->
  "with `Need[Butter]` alone first"
- `Solutions/04_Foundations--Control_Flow`: "and only `from` fills that one
  in" -> "and `from` alone fills that one in"

**Home.** CLAUDE.md watch list, inside the `only` bullet (R24); the
"nothing but" bullet already recommends "alone".

### R28. "can only X" states the obligation or names the missing ability

**Test.** "can only", "may only", "can only ever" before a verb. Where X
is required, write "must X"; where the sentence is about a ceiling, name
what lies past it ("X, and cannot Y").

**Keep when.** The ceiling is the claim and no alternative is nameable.
A quoted diagnostic ("can only be used with @runtime_checkable
protocols") stays.

**Sightings.** 6, 6 files (additive), 2026-10-04 (`c06fecc2`), the `only` sweep applying Bruce's rulings on the Only Shapes page:
- `05_Foundations--Functions`: "`a` can only arrive positionally, `c` can
  only arrive by name," -> "`a` must arrive positionally, `c` must arrive
  by name,"
- `14_Techniques--Decorators`: "You may only use them together, as the
  `*args` and `**kwargs`" -> "They must appear together, as the `*args`
  and `**kwargs`"
- `47_Effects--Stateless_in_Practice`: "A library can only check the ones
  you wrote down." -> "A library checks the Effects you wrote down and
  cannot see any others."
- `Solutions/12_Techniques--Data_Classes_as_Types`: "The chapter's factory
  function can only advise against that call." -> "The chapter's factory
  function cannot stop that call, since a caller can construct `Stars`
  directly."
- `Solutions/17_Techniques--Metaprogramming`: "`__init__()` can only modify
  the completed class object" -> "`__init__()` receives the completed
  class object and can change it in place"
- `Solutions/19_Techniques--Concurrency`: "A task can only wait on a lock
  that comes later in the order than every lock it holds" -> "Every lock
  a task waits for comes later in the order than every lock it holds"

**Home.** CLAUDE.md watch list, inside the `only` bullet (R24).

### R29. One primary concept to a paragraph; split at the seam

**Test.** Say in one sentence what the paragraph explains. If that
sentence needs "and" to join two explanations, the paragraph holds two
primary concepts: put a paragraph break at the seam between them. The
subjects can stay on one noun the whole way (the cohesion pass's
topic-string test passes such a paragraph), so read for what is being
explained, not for who the subject is. Usual seams: a design reason
beside a mechanism, a construct's explanation beside a walkthrough of
the listing's run, what the code does beside when to use it, one
listing's discussion beside the next listing's, one run of a listing
beside its next run (a second object, a second driver sequence, the
success case after the failure case). A second seam test needs no
summary: find the paragraph's concluding sentence, the one that says
what the walk showed ("The nesting of the `try` blocks is the undo
stack."). A sentence after it belongs to the next paragraph, since
the reader takes the conclusion as the end and reads what follows as
more of the same walk. A pronoun or "This"
that opens the new paragraph gets its noun. The break is often not
the whole fix (Bruce, 2026-10-30: "sometimes this requires rewriting
both paragraphs"): a half that leaned on the other, through an
opening "though", "also", or "the same way", a pointer, or a last
sentence that was a lead-in to the other half, is reworded so that
each paragraph opens on its own claim with its noun written out and
closes on its own point. A tangled sentence at the seam, one that
joins the two concepts with "so ... where ...", is split with the
paragraph. Run the test on every paragraph you touch in any pass,
not only in a paragraph sweep.

**Keep when.** The halves need each other: a claim and its reason, the
two halves of a contrast, the steps of one walkthrough, a rule and the
one-sentence exception that qualifies it. A paragraph of three sentences
or fewer rarely splits. Neither keep covers a sentence that follows
the paragraph's conclusion or walks another run: it gets its own
paragraph even when it is one sentence long. Never split inside a
list item, a block quote, a footnote, or an exercise statement.

**Sightings.** 1 chapter (additive: adds a break, cuts nothing).
Promoted by Bruce on that evidence, 2026-10-05: "a paragraph will hold
multiple primary concepts, and this makes it confusing."
- `30_Patterns--Observer` 2026-10-05, was Claude-written: the paragraph
  after `weak_responder.py` ran "Because a `Broadcaster` holds a strong
  reference ... `WeakMethod` stores the instance and the function
  separately ... While `plot` is alive, `weak` forwards the reading to
  it ..." as one block. It became three paragraphs, opening "A
  `Broadcaster` holds a strong reference to whatever you `connect()`,"
  (where the weak reference goes), "An ordinary
  `weakref.ref(plot.redraw)` is dead the moment it is created." (why
  `WeakMethod`), and "The first `announce()` runs while `plot` is
  alive:" (the listing's run). Claude made the second break during a
  rewrite; Bruce made the first by hand and named the rule.
- Book sweep 2026-10-05, 48 files (every chapter and appendix but 30,
  left for its open editing pass): 265 breaks, one Opus agent per
  chapter, each told to add blank lines and change no wording. Most
  chapters took 3 to 8; chapters 17, 18, and 19 took 10 to 13, and 39
  and appendix A took one each. Three samples:
  `03_Foundations--Containers` broke "A `set` computes one hash and
  looks in one place." from "`timeit()` runs a callable `number`
  times" (why the lookup is fast, then how the listing times it);
  `20_Patterns--Rethinking_Objects` broke the Liskov definition from
  "A statically typed compiler can check that an override's signature
  stays compatible."; `44_Effects--Effect_Management` broke the
  propagation problem from "No PEP proposes Effect tracking today."
  Nine new paragraphs opened on a pointer and got the noun ("That
  backstop" -> "The diagnostic backstop", "Both exist on `Ok` alone"
  -> "`unwrap()` and the `answer` field exist on `Ok` alone", "has a
  real one" -> "has a real adapter"). One break was undone in review:
  chapter 23's "The two wrappers' inputs differ, though." leans on the
  sentence before it.

- Solutions sweep 2026-10-05, 44 files (all but Solutions 30): 63
  breaks in 38 files, six files unchanged, most files one or two. The
  solutions split far less than the chapters because R22 had already
  given each step its own labeled paragraph. A split of a labeled
  paragraph gave the second half its own label when it covers another
  group of lines (7 new labels, such as "**Look up handlers
  read-only.**" in Solutions 28) and no label when it is a remark, a
  comparison, or what the type checker reports. Six pointer repairs
  ("Length is not what separates them." -> "... separates the two
  versions."). Two samples: Solutions 19 exercise 2 broke "This version
  takes their sum ... because the waits run one after another." from
  "The list comprehension is not the problem."; Solutions 41 exercise 5
  broke the tuple-as-cache-key explanation from "Purity is a second,
  separate requirement."

- `45_Effects--Generators` 2026-10-30, Claude-written, during the
  structural pass: "Chapter 31's `Enum` makes the states a closed set.
  Here the set is open: any function that returns a `Machine` is a
  state, so a test reaches a state by driving the machine to it, where
  `test_trap_states.py` iterates over `TrapState` and checks every
  state against every move. A machine designed as a diagram still
  belongs in chapter 31's table." One paragraph held the open set, the
  two test designs, and a verdict, with the middle two tangled in one
  sentence. The rewrite: "Here the set is open: any function that
  returns a `Machine` is a state. `test_trap_states.py` iterates over
  `TrapState` and checks every state against every move; a test of the
  generator design reaches a state by driving the machine to it. A
  machine whose states a test must enumerate belongs in chapter 31's
  table." followed by a new paragraph for the copying limit ("The
  generator design has a second limit. `copy.deepcopy()` and `pickle`
  both refuse a suspended generator, ..."). A blank line alone would
  have left the tangled sentence and the unexplained verdict. Bruce,
  the same day: "I have regularly noticed paragraphs in the book that
  confusingly combine more than one topic and should be split
  (sometimes this requires rewriting both paragraphs)."
- Book sweep 2026-10-30, every chapter, appendix, and Solutions file:
  one Opus agent per chapter with its Solutions file, reading every
  paragraph with the rewrite clause in force (see the sweep log in
  project memory `paragraph-sweep-2026-10-30`).
- `45_Effects--Generators` 2026-11-12, Claude-written, Bruce added the
  break by hand: under `saga.py` the walkthrough of the failed booking
  ended "Each `except` prints its compensation and raises `Failed`
  again, hotel before flight. The nesting of the `try` blocks is the
  undo stack." and ran on with "The second booking receives no
  `throw()`, so `list()` runs it to its end and no `except` clause
  runs." The last sentence was written when `print(list(book()))`
  joined the listing, and it was appended to the paragraph that was
  there. It walks another generator, and it sat after the paragraph's
  conclusion. The keeps had argued for leaving it: a one-sentence
  half, "the steps of one walkthrough". Both were narrowed that day.
  When a listing gains a statement, the sentence about it is placed by
  this rule, not by where the old paragraph happens to end.

**Sweep notes.** A seam whose next sentence carries "though", "also",
"the same way", or a mid-sentence "it"/"one" still leans on the
paragraph before; the agents' rule covered the opening word alone, so
read the whole first sentence of each new paragraph. The agents' "close
calls left whole" lists (about 300 across the book) are the cases this
rule keeps: a claim with its reason, a contrast, a one-sentence half.

**Home.** CLAUDE.md (global, "One primary concept per paragraph"),
cohesion (Accrued patterns), deep-review (prose pass, "Overloaded").

### R30. "Iterate" takes "over"

**Test.** A form of "iterate" ("iterates", "iterating", "iterated")
with no "over" (or "through") after it. Where the sentence names what
the iteration covers, write "iterates over X". Where the object is left
out ("until you iterate", "while iterating"), supply it ("until you
iterate over it", "while iterating over `items`"). Listing comments
count as prose.

**Keep when.** "over" would end the clause on a stranded preposition
("a generator that nothing iterates over"): restructure instead ("a
generator, and nothing iterates over it"). A subject that does not
perform the iteration gets its real verb: a `dict` view "yields" its
values. A string a program prints stays as written when its `#:` marker
and the 60-column limit hold it (Solutions 18's "array is slower to
iterate").

**Sightings.** Rule stated by Bruce 2026-10-05 ("don't say something
'iterates' by itself as in 'it iterates'; instead it should be 'it
iterates over'"), after he changed chapter 30's "The copy that
`announce()` iterates" to "iterates over". Swept the same day: 36 sites
in 17 files (additive).
- `03_Foundations--Containers`: "Iterating the `dict` iterates
  `keys()`" -> "Iterating over the `dict` iterates over `keys()`"; "A
  `dict` iterates in insertion order" -> "Iterating over a `dict`
  follows insertion order"
- `22_Patterns--Iterators`: "computes nothing until you iterate," ->
  "computes nothing until you iterate over it,"; "When a function
  iterates more than once" -> "When a function iterates over its
  argument more than once"
- `Solutions/26_Patterns--Factory`: "builds a generator that nothing
  iterates." -> "builds a generator and nothing iterates over it."
- `Solutions/44_Effects--Effect_Management`: "which `sum()` cannot
  iterate." -> "and `sum()` cannot iterate over it."

**Home.** this file only.

### R31. Point at the adjacent listing with a leading "Here,"

**Test.** A sentence that introduces the listing directly below it and
points at that listing with "X below" ("`Repeat` below is ..."), with a
demonstrative subject ("This thermometer announces ..."), or with a
purpose clause ("To break the cycle, the setter returns early"), or
names the listing by its filename ("In `x.py`, ...", "`x.py` gathers
..."), which reads as a reference to some other listing (Bruce,
chapter 45, 2026-11-09). Write "Here, X ...", or name the thing ("One
module", "this solution", "the view"); the filename is on the
listing's first line. `tip positional ARGS=--survey` lists the
filename form as `survey self-name`.

**Keep when.** The sentence states a general property rather than one
of the adjacent listing (C16); "Here," belongs on a claim about that
listing only. A filename the reader already has stays: a module a
test needs before it is supplied (chapter 11's `palindrome.py`), a
chapter file a solution revises (Solutions 26's `registry_demo.py`),
a `(continued)` part ("complete `items.py`:"), and a generic name
(`__init__.py`, `conftest.py`).

**Sightings.** 10 (additive), 6 chapters
- `45_Effects--Generators`, `32_Patterns--Multiple_Dispatching`,
  `42_Functional--Error_Handling`, `38_Patterns--Simulation`,
  `Solutions/35_Patterns--Flyweight` 2026-11-09 (`7177b735`), Bruce's
  reading of chapter 45, six: "In `yield_from_nested.py`, a `yield
  from` in `survey()` receives that `Result`:" -> "Here, a `yield
  from` in `survey()` receives that `Result`:"; "`squasher_switch.py`
  is that subroutine as an iterator class," -> "Here is that
  subroutine as an iterator class,"; "In `radd_dispatch.py`, a
  `Meters` record implements `__add__()` and `__radd__()`." -> "Here,
  a `Meters` record implements `__add__()` and `__radd__()`.";
  "`steps.py` gathers the three steps the rest of the chapter chains,
  so a listing imports all three from one module." -> "One module
  gathers the three steps the rest of the chapter chains, so a listing
  imports all three from one place."; "The imports point one way, from
  `maze_view.py` into the model's modules." -> "The imports point one
  way, from the view into the model's modules."; "so `exercise_3.py`
  defines `MutableTile`," -> "so this solution defines
  `MutableTile`,". The book-wide scan kept eight, listed under Keep
  when.
- `27_Patterns--Function_Objects` 2026-09-16, was Claude-written:
  "`Repeat` below is a frozen data class" -> "Here, `Repeat` is a
  frozen data class"; "`Handler` below names their signature, not an
  interface:" -> "Here, `Handler` names their signature, not an
  interface:"
- `30_Patterns--Observer` 2026-10-11, Bruce's hand: "This thermometer
  announces a reading only when it differs from the reading before it
  by at least `_delta`:" -> "Here, the thermometer announces a reading
  only when it differs from the reading before it by at least
  `_delta`:"; "To break the cycle, the setter returns early" -> "Here,
  the setter returns early"

**Home.** this file only. Promoted 2026-10-11 on the second chapter's
sighting (C22 -> R31), widened from the trailing "below" to the
demonstrative subject and the purpose clause; approved on the
fault-review page.

### Rulings of 2026-10-04 (Sweep Decisions page)

Bruce decided the book-wide apply report's open questions on https://claude.ai/artifact/HjHyafWs5EDXQkoPmhV9g9:
R4 narrowed, R3 content words only, R16 widened, R9's "directly"
ruling (all recorded on their entries), R14 retired (X2), and R1, R6,
R20, R28 kept as guards although no site remained for them. Scope:
the Solutions files get their own report-and-apply round after the
chapters. Cadence: chapters 31 to 33 one at a time with his diff
between, then one commit per Part. Of the 26 conflicts between a
rule and a standing record, he applied the rule at 14 sites (chapters
08, 11, 18, 20 x2, 22 x2, 27 x2, 28, 35, 42, 46, 47) and kept 12; the
retired keeps are noted in `readability_db.md` and `deep_review_db.md`
beside the records they override.

### R32. Give a trailing participle tag its own clause

**Test.** A sentence ends with a comma and a past participle plus a
measure or a place ("belongs in that state's row, written once";
"contain the loop that iterates over the data, written once"). The tag
is a second claim (how many times, where), and the reader cannot tell
which noun it modifies: the action, the row, or the loop. Give the
claim a subject and a verb ("so the action appears once"), or fold it
into the main verb ("`bind()` is one copy of the sequence that
`composing.py` repeats").

**Keep when.** The participle describes the noun it follows ("a
parameter typed `TrapState`"), or two parallel tags set up a contrast
("one state's transitions, gathered in that state's function, or the
whole machine's, gathered in one table").

**Sightings.** 3 (3 chapters). Promoted by Bruce on the first,
2026-10-18 ("capture grammatical descriptions of the problems ...
and apply those descriptions to a sweep of the book").
- `31_Patterns--State_Machines` 2026-10-18, Bruce's note "awkward,
  unclear": "An action that must run on every entry into a state
  belongs in that state's row, written once." -> "A state's row holds
  its action, so an action that must run on every entry into that
  state appears once."
- `40_Functional--Foundations` 2026-10-18, the sweep: "`map()`,
  `filter()`, and `sorted()` each contain the loop that iterates over
  the data, written once." -> "... each contain the loop that iterates
  over the data, so that loop is written once, inside the function."
- `42_Functional--Error_Handling` 2026-10-18, the sweep: "`bind()` is
  the sequence `composing.py` repeats at every step, written once." ->
  "`bind()` is one copy of the sequence that `composing.py` repeats at
  every step."

**Home.** straighten (Accrued patterns).

### R33. In a contrast, the reason states a difference

**Test.** A passage compares two designs, tools, or forms, and a
sentence in it reads "X is P, so Y" where P holds of the other side as
well. The consequence then follows from nothing the reader can see,
and Bruce's note was "states are Enums in the other design too". State
the property the other side lacks: not "a state is an `Enum` member, a
label, so the action must go in the table" but "a member is a bare
name with no fields, so every action sits on a rule", set against "a
member is also a `State` record with an `action` field".

**Keep when.** The sentence is not drawing the contrast: a shared
property stated for its own sake, in a paragraph about one side alone.

**Sightings.** 1 chapter. Promoted by Bruce on that evidence,
2026-10-18.
- `31_Patterns--State_Machines` 2026-10-18: "In the table-driven design
  a state is an `Enum` member, a label, so an action that runs on every
  entry into one state must go in the table." -> "In the first design a
  member is also a `State` record with an `action` field. In the
  table-driven design a member is a bare name with no fields, so every
  action sits on a rule, and an action that must run on every entry
  into a state sits on every rule that leads there."

**Home.** deep-review (editing pass), this file.

### R34. Cut an "or" alternative that restates the first option

**Test.** "X, or Y" offers two ways to do one thing, and Y is X by
another name: "repeat the action on every rule that leads to that
state, or write a helper that those rules call", where a rule's action
is the helper. The reader hunts for the difference between the options
and finds none. Keep the one option and give it the chapter's concrete
instance ("`refund()` runs on every transition into `QUIESCENT`, so
each of the four `Quit` rules carries it").

**Keep when.** The options differ in what the reader would observe or
write: two mechanisms, two syntaxes, two places in the file.

**Sightings.** 1 chapter. Promoted by Bruce on that evidence,
2026-10-18 (his note: "garbled").
- `31_Patterns--State_Machines` 2026-10-18: "You repeat the action on
  every rule that leads to that state, or write a helper that those
  rules call." -> "`refund()` runs on every transition into
  `QUIESCENT`, so each of the four `Quit` rules carries it, from one
  comprehension."

**Home.** this file.

### R35. Replace a transactional connective with the contrast it stands for

**Test.** "In return", "in exchange", "as a trade", "the trade-off
is", "what you get back", or "on the plus side" opens a sentence that
sets an advantage against a drawback just stated. The connective
treats the two as an exchange and says nothing about either; next to
code, "In return" also reads as the `return` statement, which is what
Bruce asked ("in the return value?"). Write the advantage as a clause
with its mechanism, and name what the other side does instead: "A
rule's action reads the input that caused the transition, where a
state's `action` takes no arguments." R2 covers the commerce nouns
(cost, price, pay); this rule covers the connective.

**Keep when.** The sentence names a real exchange or a named
trade-off that is the subject (the expression problem in chapters 13
and 20).

**Sightings.** 1 chapter. Promoted by Bruce on that evidence,
2026-10-18. The 2026-10-18 grep found no second "in return" in the
book; the three "trade-off" hits all name the expression problem.
- `31_Patterns--State_Machines` 2026-10-18: "In return, the action can
  read the input that caused the transition." -> "A rule's action reads
  the input that caused the transition, where a state's `action` takes
  no arguments: `add_money()` reads the coin's `value`."

**Home.** CLAUDE.md watch list (with the commerce family), this file.

### R36. A capability describes its use

**Test.** A sentence states what a construct permits ("`list(TrapState)`
enumerates every state", "a parameter typed `TrapState` accepts a
member and rejects anything else") and neither it nor its neighbors say
what the chapter does with that. The reader asks "and?" (Bruce: "why is
this important?", "is that an essential here?"). Name the use in the
chapter's own listings (the test that iterates over the enum, the
comprehension that builds rules from it), or cut the capability.

**Keep when.** The capability is the claim, in a section that teaches
the construct, and the use is in the listing under discussion.

**Sightings.** 1 chapter. Promoted by Bruce on that evidence,
2026-10-18.
- `31_Patterns--State_Machines` 2026-10-18: "`list(TrapState)`
  enumerates every state, and a parameter typed `TrapState` accepts a
  member and rejects anything else." -> "Iterating over the enum
  reaches every member of that set: `test_trap_states.py` checks each
  state against each move, and `VendingMachine` builds its `Quit` and
  `Row` rules from a comprehension over `State`."

**Home.** deep-review (teaching pass), this file.

### R37. Cut a sentence whose antecedent the chapter no longer sets up

**Test.** "Such a X", "those two methods", "that class", or a claim
about the chapter's own code names a construct that no listing in the
chapter holds, because a listing rewrite moved on and the sentence
stayed: "Such a state is a class with a `run()` and a `next()` of its
own. To drive both a class and a record, an engine annotates its
parameter with a Protocol naming those two methods", in a chapter
whose states are enum rows and whose engine takes `State[I]`. Cut it,
or re-anchor it to the current listing. Check: the construct named
appears in a fenced block of the chapter.

**Keep when.** The antecedent is in the paragraph, or the construct is
in a listing the sentence names. R12 covers a pointer with two live
candidates; this rule covers a pointer with none.

**Sightings.** 1 chapter. Promoted by Bruce on that evidence,
2026-10-18 (his notes: "no idea what this is supposed to be saying",
"what?").
- `31_Patterns--State_Machines` 2026-10-18: the two sentences above
  were cut; the per-machine data point they trailed became "Data that
  belongs to one machine lives on the machine, as `VendingMachine`'s
  `amount` and `row` do."

**Home.** deep-review (editing pass), the claims sweeps.

### R38. Open an example given in words with "Consider"

**Test.** A sentence introduces an example or scenario whose material is
the sentence (no listing follows yet, or the listing follows the
description) and opens with "Here's", "Here is", or "Here are". Write
"Consider a ...", drop a flourish adjective on the example ("a fancy
mousetrap"), and do not add an aside saying that the material is
described rather than listed.

**Keep when.** None seen yet.

**Sightings.** 2, 2 chapters. Promoted 2026-10-19 on the second
chapter's sighting (C25 -> R38).
- `29_Patterns--Changing_the_Interface` 2026-09-17, was Claude-written,
  Bruce's own edit: "Here are three wrappers: one logs each call ..." ->
  (Claude) "Consider three wrappers, described in words rather than
  code: one logs each call ..." -> (Bruce) "Consider three wrappers: one
  logs each call ..."
- `31_Patterns--State_Machines` 2026-10-19: "As an example, here's a
  fancy mousetrap that can move through several states while trapping a
  mouse." -> "As an example, consider a mousetrap that can move through
  several states while trapping a mouse."

**Home.** this file only.

### R39. Name a type by its members and a design by its section title, never by a coined phrase

**Test.** A hyphenated compound or a quoted paraphrase stands as the
name of a design, a choice, or a type's shape ("One-table",
"each-state-decides", "the construction-starts-the-engine choice", "a
name for 'callable, plus `undo()`'"), and the book has a section title
or a member list for it. Write the members the type has. Name a design
by its section title, linked, or by a clause that says what it does
("so constructing the machine starts the engine").

**Keep when.** A compound the book defines as a term ("table-driven",
"read-only").

**Sightings.** 5 (additive), 2 chapters. Widened from a type's shape
to a design's name and promoted 2026-10-19 on the second chapter's
sightings (C19 -> R39).
- `27_Patterns--Function_Objects` 2026-09-16, was Claude-written: "a
  list of commands that also undo needs a name for "callable, plus
  `undo()`". That name is a `Protocol` with both members." -> "an
  undoable list of commands needs a type with two members,
  `__call__()` and `undo()`, and that type is a `Protocol`."
- `27_Patterns--Function_Objects` Solutions, same day: "needs a name
  for "callable, plus `undo()`", and in Python that name is a `Protocol`
  declaring both members." -> "needs a type with two members,
  `__call__()` and `undo()`, and in Python that type is a `Protocol`."
- `31_Patterns--State_Machines` 2026-10-19: "One-table suits a machine
  you build from a diagram, whose inputs carry data, or whose
  transitions need conditions." -> "The second design, the
  [Table-Driven *State Machine*](#table-driven-state-machine), suits a
  machine you build from a diagram, whose inputs carry data, or whose
  transitions need conditions."
- `31_Patterns--State_Machines` 2026-10-19: "The each-state-decides
  design keeps each state's transitions with that state, in its
  `next()` or in its table." -> "The first design, [Each State
  Decides](#each-state-decides), keeps each state's transitions with
  that state, in its `next` function."
- `31_Patterns--State_Machines` 2026-10-19: "`StateMachine`'s
  constructor runs the initial state, the construction-starts-the-engine
  choice that [*Template Method* discourages](...)." ->
  "`StateMachine`'s constructor runs the initial state, so constructing
  the machine starts the engine."

**Home.** this file only.

### R40. "if" or "when" for a condition, "once" for a step in time

**Test.** "once X" where X is a standing property or a condition ("the
machine needs more than a page of code", "the hierarchy belongs to
someone else", "more than one thread is borrowing"), so the sentence
reads as a point in time when it states a condition. Write "if" for a
condition and "when" for a recurring circumstance; keep "once" for a
step that follows another in time.

**Keep when.** X is an event with a before and an after: "Once the code
works", "Once you discover a hot spot", "once you decide you want one"
(a decision is an event; Bruce restored that "once" where the proposal
said "after you have decided"). The adverb "once" meaning one time
("a pair used once, in one place") is a different word and stays.

**Sightings.** 22, 19 chapters. Promoted 2026-10-19 on the fix-triage
page's decisions (C37 -> R40).
- `31_Patterns--State_Machines` 2026-10-19, Bruce's hand: "Choose a
  library once the machine needs more than a page of code." -> "Choose
  a library if the machine needs more than a page of code."
- The 2026-10-19 page searched that pair over the book: of 24 hits
  Bruce applied 21, six of them ones the proposing agent had doubted as
  events, and kept three (the two events and the adverb above). Among
  the applied: `15_Techniques--Context_Managers` "Write a manager once
  you want the `with` syntax at the call site, or once several places
  need the same setup and teardown" -> "when ... or when";
  `36_Patterns--Memento` "Switch to *Command* once the `O(k^2)` pointer
  total ... grows too large to hold" -> "if"; `20_Patterns--
  Rethinking_Objects` "A subclass becomes instantiable once it defines
  `area()`" -> "when".

**Home.** the global `CLAUDE.md` watch list (consider rewriting, with
the test under the tiers), since 2026-10-19; this file.

### R41. "names" takes an identifier; "describes" takes a thing with parts

**Test.** "X names Y" where Y is something the sentence could not put
in a code span or write as a proper noun: a limitation, a problem, a
shape, a condition, a kind of work, a consequence, an axis, or a clause
("what the retry would have to know"). The subject lays Y out rather
than refers to Y by its name, so "names" understates what it does and
"describes" says it. The usual subjects are a chapter, a section link,
a sentence, a record, a protocol, or a diagnostic line that spells Y
out. Where a more specific verb fits, use it: a line that quotes Y
"states" it, a record "holds" its fields, a pair of tests
"distinguishes" three states.

**Keep when.** Y is a name: an identifier, a type, a parameter, a
member, a key, a file, an exception, an Ability ("a call that names
its arguments", "the message names `Tally`", "`Need` names what the
function requires"); where the subject selects or declares Y, an
`except` clause and its exceptions or an annotation and its type, R42
turns "names" into "specifies". Keep
it too when the subject gives Y its name (an alias "names the shape"
`dict[type[Trash], list[Trash]]`; "Responder" names the action) or
picks Y out by name from alternatives ("the type checker names each
place that needs changing"). "name" as the reader's act of identifying
("name what separates your attempt from this one", "name its
drawbacks") stays.

**Sightings.** 1 chapter, Bruce's hand. Promoted by Bruce on that
evidence, 2026-10-19 ("you often say 'names' rather than 'describes',
when the latter is clearer").
- `44_Effects--Effect_Management` 2026-10-19, was Claude-written:
  "[Error Handling](...#turning-exceptions-into-results) names the same
  limitation." -> "describes the same limitation."
- The sweep that day read 497 verb uses of "name" over `Chapters/` and
  `Solutions/` and changed 21, among them
  `20_Patterns--Rethinking_Objects` "Each protocol names only the shape
  it needs" -> "describes"; `21_Patterns--Design_Patterns` "That names
  the problem the pattern exists to solve" -> "describes";
  `43_Functional--Confidence` "A comprehension names the result" ->
  "describes"; `17_Techniques--Metaprogramming` "that line names the
  fix" -> "states"; `19_Techniques--Concurrency` "Each `Fetch` record
  names an item, its delay, and whether it fails" -> "holds". The 476
  keeps are identifiers, aliases, and diagnostics that print a name.

**Home.** the global `CLAUDE.md` style rules (the line landed there on
2026-10-20, with R42; the 2026-10-19 entry recorded it before it was
written); `tip watch-words` Tier 1 (`names` before a wh-word or an abstract noun,
the 30 keeps baselined the same day); this file.

### R42. "names" where the subject selects or declares takes "specifies"

**Test.** "X names Y" where X picks Y out of alternatives or states Y
as a requirement, and Y is a concrete thing the reader could write in
code: an `except` clause and the exceptions it catches, a mapping
pattern and its keys, an import and what it brings in, a `with` and
its managers, an annotation, a signature, a `Protocol`, or a
`TypedDict` and the types or methods it states, a factory method and
its product, a client and the concrete class it leaves open. "names"
says only that Y is mentioned; "specifies" says X made the choice.
Where Y is several things in a row, "lists" ("a union lists the closed
set of alternatives", "`INTERESTING_DUNDERS` lists the four"). Where X
is a signature stating what it requires, "declares" ("`greet_all()`
still declares `Need[Log]` in its type"). Where the plain verb is the
mechanism, use it: a body "requests" or "calls", a `match` "covers",
`@safe` "catches" `Exception`.

The dependency sense Design Patterns builds on is this shape too,
positive or negative: a construct that commits to a particular class,
implementation, or driver, or leaves it open, "specifies" it or
"specifies no" one ("the client specifies the target interface",
"`Report` specifies no writer", "generators that do not specify their
driver", "without specifying any material in the sorting loop"; Bruce,
2026-10-20, on "a generator that does not name its driver": "it seems
like 'specify' would work in cases like this"). A class line that
carries a base "lists" it.

**Keep when.** X gives Y its name (a parameter named `self`, "name the
result `words`", an alias that names a shape, `checkpoint` names a past
`Drawing`). X contains Y's name, and the sentence is about the text
("renaming or moving the interface means editing every file that names
it", "two `import` statements name it", "the broadcaster names every
responder, and *Observer* replaces those names"). X is a message or a
report that prints Y ("the error names the key", "the type checker names the
`Effect`"). The reader's own act ("name its drawbacks", "name the
substitution"). A call that passes keyword arguments literally names
them ("a call that names its arguments", "a caller must name them").

**Sightings.** 1, Bruce's remark of 2026-10-20: "In many places (not
all) in the book, the word name or names is used where I think a word
like specify or specifies would often work better." Promoted on that
remark. The sweep that day read 296 verb uses of "name" in `Chapters/`
and 587 in `Solutions/` and changed 96 and 18; the rest are the keeps
above.
- `44_Effects--Effect_Management` 2026-10-20, was Claude-written:
  "an `except` clause catches the exceptions it names" ->
  "the exceptions it specifies"
- `08_Foundations--Static_Types` 2026-10-20:
  "A tuple annotation names one type per position" ->
  "specifies one type per position"
- `26_Patterns--Factory` 2026-10-20:
  "each subclass overrides that method to name a concrete product" ->
  "to specify a concrete product"
- `29_Patterns--Changing_the_Interface` 2026-10-20:
  "create the subsystem's objects without naming their concrete
  classes" -> "without specifying their concrete classes"
- `42_Functional--Error_Handling` 2026-10-20:
  "`-> int` names no failure, where `-> Result[int, str]` names one" ->
  "specifies no failure ... specifies one"
- `34_Patterns--Composite_and_Interpreter` 2026-10-20:
  "a union names the closed set of alternatives" -> "lists"

- `44_Effects--Effect_Management` 2026-10-21 (the edit-start-44 pass, approved on the fault-review page), four:
  "names the kinds of impurity" -> "specifies the kinds of impurity"
  (twice); "each name both parameters" -> "declare"; "the `Log` they
  name" -> "declare"

**Home.** the global `CLAUDE.md` style rules, in one line with R41,
since 2026-10-20; this file. Not yet in `tip watch-words`: the shape's
objects (a type, an exception, a key, a class) are also the objects of
the keeps, so a word rule would list every keep as a hit.

### R43. Standing behavior under a stated condition takes the present tense, not "would"

**Test.** The main verb carries a modal ("would", "can") and the
condition is in the sentence: a subject with a restrictive clause ("A
`list` there"), an "If" clause, a "With" or "Without" phrase. Drop the
modal and put the condition in the present ("If `host` has a default,
`name` follows it with none"); the claim about the listing is unchanged.
`tools/past_tense.py` skips modals, so no check covers this.

**Keep when.** A hedge about the reader's own choice ("the lambda you
would write"); "would otherwise"; an exercise prompt; a tool or design
that does not exist (appendix A's checker); "as though more money would
sell a sold-out item"; advice ("In real code `Weight` would be a
`@dataclass`").

**Sightings.** 3 shown, and a book-wide sweep. Promoted 2026-10-21 (P1
on the chapter 44 page) on Bruce's direction that day ("this could be
'breaks'. Search the book for similar present-tense transformations"):
106 sentences in 33 chapters and 20 Solutions files, commit ba516387.
- `44_Effects--Effect_Management` 2026-10-21 (the edit-start-44 pass, approved on the fault-review page):
  "Generated code that rebinds an implementation would break that
  guarantee" -> "breaks that guarantee"
- `44_Effects--Effect_Management` 2026-10-21, Bruce's hand:
  "A type system that verified purity would do that reading for you" ->
  "A type system that verifies purity does the work for you"
- `34_Patterns--Composite_and_Interpreter` 2026-10-21 (ba516387):
  "A `list` there would leave the tree mutable" -> "leaves the tree
  mutable"

**Home.** this file; the activate skill's accrued patterns (a register
rule).

### R44. A generic plural with a restrictive clause drops its article

**Test.** "the <plural> that/who <verb>" in a general claim about every
member of that kind ("The languages that track Effects today are
young"). Drop "the". If the sentence then reads as about a specific set
the text has set up, the article was definite and stays.

**Keep when.** A definite set: "the steps that vary" in a Template
Method's own sequence, "the imports that ran", "the records that inherit
from it", "the cells that need code" in a specific grid, "the ones that
return a pooled instance" ("ones" needs the article). A set phrase:
"separate the things that change from the things that stay the same".

**Sightings.** 3 shown, and a book-wide read. Promoted 2026-10-21 (P2 on
the chapter 44 page) on Bruce's direction ("Both 'the' can be removed.
Look through the book for other opportunities"): of 96 "the Xs that"
phrases, eight generic ones lost the article in chapters 01, 11, 17, 21,
39, 42, 44, 46 (commit 93cb0163) and 88 definite ones kept it.
- `44_Effects--Effect_Management` 2026-10-21 (the edit-start-44 pass, approved on the fault-review page):
  "The languages that track Effects today are young, and the libraries
  that retrofit Effect tracking are demanding" -> "Languages that track
  Effects today are young, and libraries that retrofit Effect tracking
  are demanding"
- `44_Effects--Effect_Management` 2026-10-21:
  "can drop the conveniences that help a person read code" -> "can drop
  conveniences that help people write and read code"
- `21_Patterns--Design_Patterns` 2026-10-21 (93cb0163):
  "The programmers who arrive next learn it as syntax" -> "Programmers
  who arrive next learn it as syntax"

**Home.** this file.

### R45. An enumeration of clause-length items becomes a list

**Test.** One sentence holds three or more parallel items joined by
commas and "that" or "and", and each item is a clause with its own
verb ("confirms that X, that Y, and that Z"; "First, ... Second, ...
Third, ..." across sentences). Write the lead-in with a colon and one
item per bullet, numbered when the order matters.

**Keep when.** The items are short phrases rather than clauses: "has
three jobs: it measures, it decides which changes to announce, and it
notifies the responders" stayed inline.

**Sightings.** 7, two chapters. Promoted 2026-10-21 (P3 on the chapter 44 page). First 4, one chapter (`30_Patterns--Observer`, the pass
2e61b3e7..HEAD, approved on the fault-review page 2026-10-11)
- Bruce's hand, twice: "Testing confirms that X, that Y, that Z." ->
  "The test file confirms that:" with one bullet per clause
- Bruce's hand: the paragraph listing the extraction designs -> bullets
- "less precise ... in three ways. First, ... Second, ... Third, ..."
  -> a numbered list, the compared things named in the lead-in

- `44_Effects--Effect_Management` 2026-10-21 (the edit-start-44 pass, approved on the fault-review page), three, two of them Bruce's own requests ("rewrite using
  bullet points for clarity", "make these bullets"): the EMS
  paragraph -> "does three things:" with one bullet each; the
  four-language survey sentence -> a lead-in and two bullets; the
  `returns` library's four containers -> "provides four containers:"
  and one bullet each

- `45_Effects--Generators` 2026-11-01, Bruce: "make bullets": two
  sentences describing `throw(exc)` and `close()` in parallel -> a
  two-item list under a colon.

**Home.** this file; the deep-review skill (structural).

### R46. "raises `X`", not "raises the `X`"

**Test.** A form of "raise" or "re-raise" followed by "the" and an
exception class in a code span ("Python raises the `StopIteration`").
Drop the "the": "Python raises `StopIteration`".

**Keep when.** "the" belongs to a different noun: a generic noun ("re-raises
the exception with a bare `raise`") or a possessive ("the `Enum`'s
`ValueError`", which the sweep rewrote as "makes `Month()` raise
`ValueError`"). "raises a `TypeError`" (R1's form) is untouched; the ruling
is about "the".

**Sightings.** Bruce's ruling 2026-10-23, on
`45_Effects--Generators` ("don't say 'the' when you're talking about
raising an exception. just say 'raises StopIteration'"):
- "Python raises the `StopIteration` on the generator's behalf." ->
  "Python raises `StopIteration` on the generator's behalf."
- The sweep that followed fixed 23 sites in chapters 05, 12, 30, 32, 47
  and Solutions 05, 09, 12, 19, 26, 32, 33, 34, 38, 41, 43, e.g. `30`
  "`announce()` raises the `ValueError` from `gather()`" -> "raises
  `ValueError` from `gather()`"; Solutions `33` "raises the
  `AttributeError` above" -> "raises `AttributeError`, as the `#:` line
  shows"

- `45_Effects--Generators` 2026-11-01, was Claude-written (same day,
  twice; Bruce: no "the"): "its `yield` raises the `ValueError`" -> "its
  `yield` raises `ValueError`"; "raises the `ValueError` at `yield
  \"ready\"`" -> "raises `ValueError` at ...". `RAISE-THE` in
  `tools/prose_lint.py` gates the shape since that day.

**Home.** CLAUDE.md watch list (global, the "Raise" bullet), beside R1.

### R47. A sentence beside a listing goes if the listing or its markers already show it

**Test.** Read a sentence that follows (or introduces) a listing and ask
what the reader learns from it that the code and its `#:` markers do not
state. Three shapes answer "nothing": a line-by-line narration of what the
code does ("`next(conversation)` starts the generator and produces a
`Question`"), an annotation read aloud ("`Question` fills the `YieldType`
position, `Answer` the `SendType`"), and a control-flow paraphrase of a
clause that is on the page ("`worker()` catches the exception, prints the
message, and yields again"). Cut those. A cut that would orphan a `[n]`
tag keeps the reference in a surviving sentence; the listing is not
edited.

**Keep when.** The sentence states what the code cannot: where an
exception lands ("`g.throw()` raises that exception at the suspended
`yield "ready"`"), why two output lines sit together (one `send()` ends
one inner generator and prompts the next), which way a value travels
through a chain (yielded items go to the driver, the return value to the
delegating generator), what would happen without a line (without `[3]`,
`send(4)` raises `StopIteration`), why an annotation is what it is
(`yield from` passes both channels through, so the types match), what a
design must do (a driver must prime with `next()`), or a forward
reference that looks wrong until explained (`watch()` names `watched`
before the module binds it). R18 is the special case of a verdict on
output that is on the page; R7 the sentence that only points at the
next listing.

**Sightings.** 3 rounds, 1 chapter, 2026-10-25, Bruce's ruling on two
pasted passages ("Most of this seems to reiterate what's in the code.
Strip it down to the essential observations.") and then "look through
the rest of the chapter for similar issues"; 15 passages cut in
`45_Effects--Generators` (`457761fe`, `9bee1fcb`, `64c1c4c8`):
- "`g.send(1)` becomes `first` inside `collect("alpha")` with no
  forwarding code in `both()`." -> deleted
- "`ask()` uses `Answer` in two of the three positions, in two different
  roles. As the `SendType`, `Answer` types each value the driver sends,
  which arrives as the value of the `yield` expression and binds to
  `answer`. As the `ReturnType`, `Answer` types the value `ask()`
  returns when it finishes. That value becomes the value of the whole
  `yield from` expression, so each of `interview()`'s three assignments
  binds an `Answer`." -> "`Answer` fills two of `ask()`'s three
  positions, in two roles. As the `SendType` it is the value of the
  `yield` inside `ask()`, sent by the driver. As the `ReturnType` it is
  the value of the whole `yield from` expression in `interview()`."
- "`task_runner()` gives the front job one `next()` per turn. When a
  job yields, the runner appends it to the back of the queue. When a
  job finishes, `next()` raises `StopIteration`, and the runner drops
  the job." -> deleted; kept "Each `yield` suspends its job and returns
  control to `task_runner()`, which then runs the next job. The output
  interleaves the two jobs in a single thread, although neither names
  the other."
- "`stubborn()` answers `GeneratorExit` with another `yield`, so
  `close()` raises `RuntimeError: generator ignored GeneratorExit`." ->
  deleted; kept "`close()` requires the generator to finish."
- Kept on the test: "`GEN_CREATED` shows that calling `interview()`
  created the generator and ran none of its body." (what the marker
  means); "`watch()` names `watched` before the module binds it."

- `45_Effects--Generators` 2026-11-01, Bruce: "Instead of restating the
  code, put [1] and [2] markers in the code and refer to those": "The
  first run calls `throw()`." / "The second run calls `close()`." ->
  tags on the two lines and "At `[1]`, ..." / "At `[2]`, ...".
- `45_Effects--Generators` 2026-11-12, Bruce: "it simply said what was
  in the code": "`g` is `outer()`'s generator." -> deleted, under a
  listing with `g = outer()`. The sentence was Claude's C59 repair of
  the day before. A repair from another rule that swaps a description
  for the listing's own name uses the name and stops. A sentence that
  introduces the name reads an assignment aloud, the first shape in the
  test above. Reread every sentence a repair adds beside a listing
  against this rule.

**Home.** CLAUDE.md (global, the "Prose beside a listing" bullet);
deep-review (prose pass, "Restating"). Promoted on Bruce's ruling, the
way R46 was. The 2026-10-25 book sweep that followed (one Opus agent
per file, 93 files, brief in `build/restate-2026-10-25/`) cut about
1,700 lines of prose across 88 files, 1,949 deletions against 248
insertions, and is the second sighting. Three keeps the sweep settled:
a one-sentence lead-in above a test listing stays (it introduces the
listing); a bold R22 step label stays with one reason sentence rather
than going with its narration; and a cut that takes the only prose
mention of a class name draws an `internal-names` hit, so the agent
restores a sentence or the name joins that baseline. Four cuts took a
reason along (chapters 04, 19, 30, 34, commit `73b3a3e9`), the shape
to reread for: a narration whose last clause was the mechanism.

### R48. A bullet item starts with a capital and ends with a period only when it is a sentence

**Test.** Read each item of a list on its own. It starts with a capital
letter whatever it is. If it is a sentence, it ends with a period. If it
is a fragment, it ends with nothing; the test for a fragment is whether
the items could be separated from one another with commas ("Functions,
classes, objects, and inheritance", "`Maybe`, for a value that might be
absent"). An imperative clause is a sentence ("React to each new
subclass: `__init_subclass__()`."). A list where one item carries a
second, full sentence keeps its periods throughout (chapter 21's
principles, chapter 19's bold rules). An item that passes both tests, a
clause that could also ride in a comma list, takes the comma reading
and no period. Numbered exercise lists are sentences and always take
periods.

**Keep when.** A bold or italic label that R5 governs ends with a
period, and its explanation is sentences. A `Hint:` or `Done when:`
paragraph is prose, not a list item.

**Sightings.** 3 rounds, 9 files, 2026-10-28, all on Bruce's rulings:
- `45_Effects--Generators` (`8bd2f662`), "capitalize each, remove the
  punctuation at the end of each", on a list he had just asked for:
  "- values go out through `yield`," / "- values come in through
  `send()`," / "- one value goes out through `return`." -> "- Values go
  out through `yield`" / "- Values come in through `send()`" / "- One
  value goes out through `return`"
- the book survey that followed ("check bullet points throughout the
  book"; 147 lists, 783 items, 44 changed in `fc5aa9a2`): `01_Introduction`
  "Functions, classes, objects, and inheritance." -> "Functions, classes,
  objects, and inheritance"; `46_Effects--Stateless`, three built-in
  dependencies written as one sentence over bullets, "`Files` in
  `stateless.files` that reads a whole file," -> "`Files` in
  `stateless.files` that reads a whole file" and the last item's period
  gone; Solutions `21_Patterns--Design_Patterns` "an interface,
  `ShippingStrategy`, declaring one method, `cost()`" -> "An interface,
  `ShippingStrategy`, declaring one method, `cost()`"; the same in
  chapters 16, 44, 47 and appendix B
- `17_Techniques--Metaprogramming` (`33f2daf3`), after Bruce stated the
  rule in words ("If a bullet point is an actual sentence, it should end
  with a period"): "React to each new subclass: `__init_subclass__()`" ->
  "React to each new subclass: `__init_subclass__()`." (the sweep had
  read the need-and-tool pairs as fragments; an imperative clause is a
  sentence)
- the tie-breaker, same day, on the chapter 45 list whose items are
  clauses and comma-separable both: "Leave them off. I see the
  conundrum, because they could either be separated by commas or stand
  alone as sentences."

**Home.** CLAUDE.md (global, the "Bullet items" bullet); this file.
Promoted on Bruce's ruling, the way R46 and R47 were. The survey found
the book nearly uniform before the sweep (about 670 sentence items with
periods, 29 fragment items without), so a new list is the place to
apply it, and `scratchpad/bullets_scan.py` from that session is the
shape of a checker if the rule ever needs one.

### R49. An additive adverb after a change of subject names what it adds

**Test.** "also", "too", "as well", and "likewise" say that something
joins a set the previous sentence set up, and the reader must decide
which constituent is the new member. When the sentence's subject differs
from the previous sentence's subject, the subject is the reader's first
candidate ("the generator, too, keeps its place"), so a sentence that
meant to add to its predicate is misread. Read each such sentence twice,
once with the adverb on the subject and once on the object or
complement. If the subject reading is false or beside the point, name
the thing added ("as well as X", "along with X", "X and Y") or let
another word carry the addition ("that last change", "a second guard").
A pronoun subject ("It also ...") carries the previous subject on and
is quiet, and so is a sentence where the subject reading is the one
meant ("Pyright accepts the read too").

**Keep when.** The subject reading is the claim: "Tuples and
dictionaries can carry them too", "A slice of CODE holds the export open
too", "Python also calls CODE on a live generator when it reclaims the
generator's memory" (the driver calls it, and Python does as well).
Where both readings are true, the sentence stands.

**Sightings.** 17 in 15 files, 2026-10-28, from Bruce's note on a
sentence the session had just written in `45_Effects--Generators`
("'as well' could read as 'the same way a closure does'. Analyze the
problem grammatically and apply that analysis across the book"); the
book-wide read had 178 candidates (`tip sentence-shapes ARGS=--survey`,
rule `[ADD]`):
- `45_Effects--Generators` (`7143c244`): "A closure keeps its captured
  variables between calls, but each call runs its body from the top.
  The generator keeps its place as well," -> "The generator keeps its
  locals and its place in the body,"
- `02_Foundations--Tour` (`4e378773`): "The copy shares the outer list's
  inner objects. The standard library's `copy.deepcopy()` duplicates the
  inner objects as well." -> "duplicates the inner objects as well as
  the outer list."
- `20_Patterns--Rethinking_Objects` (`23260e24`): "A fully defensive
  class must copy on the way in as well." -> "must copy on the way in as
  well as on the way out."
- `44_Effects--Effect_Management` (`32e4070b`): "A library checks the
  Effects you wrote down. A language with native Effects also finds the
  ones you left out," -> "A language with native Effects checks those
  and finds the ones you left out,"
- `21_Patterns--Design_Patterns` (`1aadacc7`): "A registry factory
  removes that last change too," -> "removes that last change," ("last"
  carries the addition)
- `36_Patterns--Memento` (`fecb80d5`): "The `strokes` tuple is immutable
  on its own. The record makes the attribute that holds it read-only
  too." -> "The record adds a second guard by making the attribute that
  holds it read-only."
- the rest in chapters 06, 12 (two), 15, 18, 22, 26, 47 and Solutions
  04, 17, 21, each the same shape and repair.

A reread on 2026-11-09 covered the 153 hits then standing, before
they were recorded as judged in the survey baseline (one Opus agent,
brief in `build/shapes-reread-2026-11-09/`; the session read a sample
of its keeps and decided its close calls): 4 rewritten, 149 kept.
- `Solutions/06_Foundations--Modules_and_Packages`: "the shell and the
  editor accept `bpackage` as well, but Python's import check compares
  case and rejects `bpackage`" -> "accept `bpackage` as well as
  `bPackage`," (the subject reading put the shell and the editor
  beside Python, which the same sentence says rejects the name)
- `Solutions/12_Techniques--Data_Classes_as_Types`: "`count("@") == 1`
  also rejects two-`@` strings like `"b@@x.com"`." -> "rejects both a
  string with no `@` and a two-`@` string like `"b@@x.com"`." (the
  sentence before says the original check accepts any number of them)
- `Solutions/38_Patterns--Simulation`: "Too small a kick keeps the step
  small in a loud region too," -> "in a loud region as well as near a
  nodal line,"
- `Solutions/34_Patterns--Composite_and_Interpreter`, an adverb with
  nothing on the page to add to: "`(2 * x + 1).right` also resolves
  for a caller." -> "resolves for a caller."

**Home.** CLAUDE.md (project, the `tip sentence-shapes` paragraph:
`[ADD]` is a survey rule there, since 161 of the 178 hits were keeps,
with its read keeps in `tools/data/sentence_shapes_survey_baseline.txt`
since 2026-11-09, each entry holding the sentence and the one before
it, so an edit to either brings the hit back); the `cohesion` skill's
Accrued patterns; this file.
Promoted on Bruce's ruling, the way R46 to R48 were.

### R50. A verb cancelled by its object says what happens instead

**Test.** A verb that promises an action or a possession, followed by an
object that cancels it: `no X`, `none`, `none of`, `nothing` ("runs none
of the function body", "raises no exception", "has no `__slots__`",
"needs no lock", "prints nothing"). Bruce's name for the fault is a
*reversal of expectation*: "'runs' makes the reader think something will
happen and 'none of' reverses that expectation." Say what does happen,
plainly, in the sentence's own terms: when the body runs, what Python
does instead, who supplies the thing, what stays as it was. The rewrite
must read as the natural way to say it. Two forms Bruce rejected the same
day are the trap on the other side, "with its body still to run" and
"leaves its body for the driver": they avoid the word and give the reader
nothing to picture. If the only positive form is a contortion, keep the
negative.

**Keep when.** The absence is the claim and has no positive term ("a
class with no `__slots__`" where the missing declaration is the lesson,
"Python has no labeled `break`", "`object` defines no `__len__()`" as
the reason a check fails); half of a real contrast ("`Strategy` has
none. ... `Observer` has one"); a quoted diagnostic's wording ("has no
attribute 'add'"); an exercise statement or a Done-when criterion that
tests an absence; a hint whose clue is the missing thing.

**Sightings.** 1 round, 48 files, 2026-10-28, from Bruce's note on
chapter 45 and the book sweep that followed ("That's the general pattern
(reversal of expectation) we want to fix throughout the book"); 593
hits read, about 350 rewritten, 251 kept (the `tip watch-words`
baseline holds them):
- `45_Effects--Generators` (`125a2f2c`): "Calling `interview()` returns a
  generator object and runs none of the function body." -> "Calling
  `interview()` returns that object. `next()` and `send()` run the body,
  one `yield` at a time."
- `06_Foundations--Modules_and_Packages` (`e90231b6`): "Python raises no
  exception, and the table ends up one row short." -> "Python
  continues, and the table ends up one row short."
- `22_Patterns--Iterators` (`8a4ed56d`): "so a new source needs no change
  to `total()`" -> "so `total()` stays the same for every new source"
- `19_Techniques--Concurrency` (`8ba96052`): "finds no idle worker" ->
  "finds every worker busy"; "shares no state" -> "keeps its state
  private"
- `30_Patterns--Observer` (`89811688`): "`Thermometer` declares its
  fields and writes no method" -> "consists of its field declarations"
- `44_Effects--Effect_Management` (`f95b3aee`): "The function's
  signature answers none of these questions" -> "leaves all four
  questions open"
- `04_Foundations--Control_Flow` (session follow-up): "It runs when the
  loop hits no `break`." -> "It runs when the loop exhausts its
  iterable."
- the rejected contortions, same day: "runs none of its body" -> "with
  its body still to run" and "leaves its body for the driver", both
  replaced by "The body runs later, one `yield` at a time, when the
  driver calls `next()` or `send()`."
- the shape turned around, a negated subject, same day: `45` (`05d56eea`)
  "The runtime enforces that pairing, though no annotation expresses
  it." -> "The annotation describes the three channels; the runtime
  enforces the pairing."; then a second sweep of 90 `no <noun> <verb>`
  sites, 45 rewritten and 45 kept: `26` "No tool reports the missing
  case at edit time" -> "At edit time, the type checker accepts both
  functions"; Solutions `46` "No greeting prints" -> "The log entries
  are the whole output"; `43` "so no call affects another" -> "so the
  calls are independent"; `20` "No signature records that dependence,
  and no type checker reports it" -> "The dependence sits in `list`'s
  implementation, below the signatures the type checker reads". The
  keeps were half the hits: "No lock protects the cell", "No type
  reports the race", "No tool reads the behavior behind the
  signature", where the absence is the lesson.

**Home.** CLAUDE.md (global, the `<verb> nothing` paragraph of the watch
list, widened to `no X` and `none of`, and to the negated subject);
`tip watch-words` (`NO_VERBS` in `tools/watch_words.py`, Tier 2, and
`NO_SUBJECT`, a Tier 1 survey, since the subject shape keeps as often
as it rewrites); this file. Promoted on Bruce's
ruling, the way R46 to R49 were. The `positive` skill's test is the
general case; this rule is its sharpest shape, where the verb itself
raises the expectation that the object cancels.

### R51. One picture per clause

**Test.** A clause relates two terms through a comparator ("the same
way", "the same X as", "as X as", "like", "unlike", "rather than",
"instead of", "compared with", "differs from"), and each term is a
picture the reader has to build before the relation can land: a noun
with a participle, a relative clause, or a clause under it. Bruce's
name for the fault is "asking the reader to hold two things at once"
(chapter 45, 2026-10-28): "`drive()`, imported unchanged, answers a
request yielded two generators deep the same way it answers one from
`interview()`'s own body." The reader builds the deep request, holds
it, builds the request from the body, then applies "the same way",
while the verb between them carries content of its own. Repair: give
each picture its own sentence, in the order the reader needs them,
the new thing first, then the mechanism, then the relation, so the
relation sentence compares two things already on the page. Or make
the second term a name the reader already has (a listing, a term the
paragraph introduced), or drop a modifier the context already
supplies. The test for the rewrite is one read at speed: the relation
lands on the first pass, and no added sentence repeats a term without
adding anything.

**Keep when.** Both terms are already on the page (the comparison
names two listings or classes the section just showed); the terms
are short enough to read as names even with a verb in them; "rather
than" or "instead of" joins two bare verb phrases ("return a
description rather than raise an exception", two actions, not two
pictures); an exercise statement, a Done-when criterion, or a hint;
an idiom the scan cannot tell from a comparison ("as soon as", "as
long as", "like any other", "looks like").

**Sightings.** 1 round, 2026-10-28, from Bruce's note on chapter 45
and the book sweep that followed (`[TWO]` in `tip sentence-shapes
ARGS=--survey`, 102 hits in 38 chapters, 21 Opus agents, 18
rewrites, 84 keeps, 17 commits):
- `45_Effects--Generators` (`ac20c972`): the sentence above ->
  "`drive()` is imported unchanged. The requests now come from `ask()`,
  one generator below `interview()`, and `yield from` passes each one
  up to the driver, so `drive()` sees the same `Question`s it saw in
  `interview_generator.py`."
- the sweep's keeps were the majority, because most comparators in the
  book join two short terms or two bare verb phrases, and the scan
  weighs words, not familiarity.
- a reread on 2026-11-09 covered the 84 hits then standing, before
  they were recorded as judged in the survey baseline
  (`tools/data/sentence_shapes_survey_baseline.txt`), and rewrote
  none: 62 comparisons that read once and 22 not the shape (an idiom,
  or "like" meaning "such as"). Fifteen of the 237 `[TWO]` and `[ADD]`
  lines had changed since the 2026-10-28 reads, and none of those
  failed.

**Home.** CLAUDE.md (global, "One picture per clause"); `tip
sentence-shapes` (`[TWO]`, `SURVEY_RULES` in `tools/sentence_shapes.py`,
`comparator()`, `heavy_side()`, `two_terms()`, with its read keeps in
the survey baseline since 2026-11-09); the deep-review skill's prose
pass; the `straighten` skill's Accrued patterns; this file. Promoted on Bruce's ruling, the way R46 to R50
were. It is a cousin of the `straighten` skill's "subject held open":
there the reader holds a subject across a long modifier, here two
modified terms across a comparator.

### R52. Name the thing, not its role

**Test.** A noun phrase identifies something by its place in the
machinery, through a chain of two or more "of"/"in" phrases or a
relative clause with a verb of its own, when the page already gives
that thing a name: an identifier in a code span, a term the section
introduced, a listing. Bruce's word for the fault is "convoluted"
(chapter 45, 2026-10-29). "`yield from` makes the `Result` the value
of the expression in the enclosing generator, after which that
generator keeps running" makes the reader climb `Result` -> value ->
expression -> generator and then attach a tail clause to the last
rung. "`survey()` names the generators it delegates to in its body"
describes `interview()` and `ask()` by their role when both names are
on the page three lines up. A second tell is the tail: "after which",
"at which point", or a trailing "in its body" that could attach to
more than one thing in front of it. Repair: write the name; make the
verb the action between the two named parties (hands X to Y, writes X
into Z, passes X up to W); let the tail say what the recipient does
next, in the paragraph's own terms, so a contrast sentence beside it
keeps the same shape. Delete a role phrase the paragraph already
stated ("the value of the expression" two paragraphs up).

- "`yield from` makes the `Result` the value of the expression in the
  enclosing generator, after which that generator keeps running." ->
  "`yield from` hands the `Result` to the enclosing generator, which
  continues the conversation." (beside "`drive()` returns the `Result`
  to its caller, ending the conversation")
- "`survey()` names the generators it delegates to in its body." ->
  "`survey()` delegates to `interview()` and `ask(...)`." (two
  earlier rewrites failed: "writes its two `yield from` targets ...
  into its body" read as editing source, and "both named in its
  body" restated what the listing shows; once the names are in the
  sentence, the role phrase goes entirely)

**Keep when.** The role is the only handle the page has (no name
exists yet, or the sentence is the definition that introduces the
name); the chain is a type or a path the reader must see as written
("the `ReturnType` position of `Generator`", "the `__dict__` of the
instance"); a quoted diagnostic; an exercise statement or a Done-when
criterion that must stay abstract so as not to give the answer away.

**Sightings.** 2, both Bruce's flags on chapter 45 on 2026-10-29
(`ca045294`, `4a5d14ea`), promoted on his request to apply it across
the book. The sweep the same day (brief `build/role-2026-10-29/`,
21 Opus agents over 422 regex candidates in 49 chapters) rewrote 13
sentences and kept the rest: the shape is rare outside chapter 45,
and the keeps were short relative clauses that are the claim, a role
that is the only handle before the listing names the thing, a
general rule a name would narrow, and exercise or Done-when wording. Candidates for a scan: "the value of the", "the X of the Y
in the Z", a relative clause ending on a preposition ("the generators
it delegates to"), "after which", "at which point"; a parse rule would
flag an object noun phrase with two or more nested prepositional
phrases or a relative clause when the paragraph holds a code span the
phrase could stand for.

**Home.** This file; the deep-review skill's prose pass (vague
descriptions, since 2026-10-22, is the neighbor: there a verdict or an
abstract noun stands where the mechanism should be, here a description
of the mechanism stands where its name should be).

### R53. "Can" for a standing capability, "could" for a condition or a past

**Test.** A "could" or "could not" in prose about what code, a type, a
construct, or the reader is able to do. Put the sentence in the present
with no condition attached: if it stays true, the modal is "can"
("cannot"). "Could" is the past of "can" and the modal of a
counterfactual, so a reader looks for the condition or the past event
it depends on, and a sentence with neither makes a standing capability
read as hypothetical. Bruce's flag (chapter 45, 2026-10-30): "`drive()`
accepts either, and `survey()` could delegate to either with `yield
from`" states what the shared annotation permits, so "can". The perfect
form is the same fault: "explain why `__getattr__()` could not have
supplied it" gives a standing reason, so "cannot supply it".

- `45_Generators` 2026-10-30, was Claude-written: "`survey()` could
  delegate to either with `yield from`" -> "can delegate to either"
- `25_Surrogate` 2026-10-30: "Then explain why `__getattr__()` could
  not have supplied it." -> "cannot supply it."
- `14_Decorators` 2026-10-30: "The wrapper's own `__dict__` could hold
  the count as well," -> "can hold the count as well,"
- `19_Concurrency` 2026-10-30: "since a preemptive switch could occur
  between them." -> "can occur between them."
- `A_Effect_Tracking` 2026-10-30: "The tool could run in three
  places." -> "The tool can run in three places."

**Keep when.** A narrated past ("I decided to see what the Claude AI
could do with it"; "Before Python 3.15 ... the manager closed any
resource it opened before the body could use it"); a counterfactual
whose condition is on the page ("If Python had always supported
coroutines, you could expect every library to conform"; "If one
`Signal` member lacked a `case`, `act()` could reach its end"); a
speculation about the future ("asks what Python could adopt", "A
future CPython could add another"); "could have" ("any one of them
could have caused the bug"); the idiom "could not be more different";
a report of one run's outcome ("a row that reads `Unknown` says the
checker could not resolve a call").

**Sightings.** 1 flag, promoted on Bruce's request to a book sweep the
same day (2026-10-30): 69 sites in `Chapters/` and `Solutions/`, 48
rewritten plus 4 generated exercise quotes that followed their
chapters, 17 kept. Scan: `could` is a Tier 2 entry in `tools/watch_words.py`
since the same day, with the 17 keeps in its baseline (Tier 1 has
no per-word baseline, so the keeps could not be recorded there).

**Home.** CLAUDE.md writing style (the "can"/"could" bullet beside
"Present tense for standing behavior") | this file.

### R54. "whichever" is "the X that", or the independence stated plainly

**Test.** The sentence has "whichever". If it picks out one thing by a
property ("whichever call resumed it", "whichever class receives the
call", "keeps whichever finished last"), write the definite noun phrase:
"the call that resumed it", "the class that receives the call", "keeps
the result that finished last", supplying the noun when "whichever"
stood alone. If the sentence's claim is that the outcome is the same
across a choice ("the same elements, whichever code holds it",
"Whichever form you choose, the borrower's side has two lines"), state
the independence in plain words: "no matter which code holds it", "In
all four forms", "for every input", "under either executor", or name
the two options ("Whether `__init__()` or `__enter__()` acquires the
resource"). A choice offered to the reader ("Use whichever name reads
better") is "the name that reads better".

**Keep when.** None seen yet. The 2026-11-01 sweep read all 45 sites in
`Chapters/` and `Solutions/` and kept none; the two generated exercise
quotes in `Solutions/` followed their chapters.

**Sightings.** 1 flag, promoted on Bruce's request to a book sweep the
same day (2026-11-01, "kind of a vague word. Here it seems like it could
be 'the'"): 45 sites, 44 rewritten by three Opus agents plus the
session, one in `Solutions/45` left for the session to finish.
- `45_Effects--Generators` 2026-11-01, was Claude-written (same day):
  "leaves the generator through whichever call resumed it" -> "leaves
  the generator through the call that resumed it"
- `45_Effects--Generators`: "up through `next()`, `send()`, or
  `throw()`, whichever the driver called" -> "up through the driver's
  call, whether that was `next()`, `send()`, or `throw()`"
- `26_Patterns--Factory`: "`cls` is whichever class receives the call"
  -> "`cls` is the class that receives the call"
- `03_Foundations--Containers`: "keeps the same elements, whichever code
  holds it" -> "keeps the same elements no matter which code holds it"
- `10_Foundations--Cleanup`: "Whichever method acquires the resource,"
  -> "Whether `__init__()` or `__enter__()` acquires the resource,"

**Home.** CLAUDE.md watch list (Tier 2, "whichever") | this file.

### R55. Name the actor for a language mechanism

**Test.** A language feature or an exception sits in subject position
under a verb it cannot perform on its own: a hook "fires", a lookup
"sees", a call "asks", a checker "wants", an exception "runs" a block.
Name the actor that performs it (Python, the type checker, the caller)
and use the verb that actor performs; the feature or the exception
becomes the object or the reason.

**Keep when.** The mechanism really is the actor. A function that returns
or raises does so itself, and "`__getattr__()` returns a value" needs no
rewriting. An exception "propagates" and "arrives": those are its own
verbs, and so is "runs" for a block or a statement. The actor to name is
the construct with its own verb before it is "Python": "the `finally`
block runs on the way out of the `try`", not "Python runs the `finally`
block" (Bruce, 2026-11-01: "as we know in this book we are using
Python"). Name Python where Python does something the construct does
not do on its own: "Python raises `StopIteration` on the generator's
behalf", "Python converts it into a `RuntimeError`", and where the
contrast is with another tool ("Python runs the program either way",
against the type checker).

**Sightings.** 4, two chapters (promoted 2026-11-01).
- "`__getattr__()` fires for any name the proxy and its class lack" ->
  "Python calls `__getattr__()` for any name the proxy and its class
  lack"
- "`__getattr__()` never sees a special method, never sees an assignment"
  -> "Python never calls `__getattr__()` for a special-method lookup or
  for an assignment"
- "`len(p)` asks `type(p)` for `__len__()` without consulting the
  instance" -> "`len(p)` looks up `__len__()` on `type(p)`, skips the
  instance"
- `45_Effects--Generators` 2026-11-01, was Claude-written, Bruce: "is
  that how it works?": "so the `ValueError` runs the `finally` block and
  propagates out of the generator" -> "so Python runs the `finally`
  block on its way out of the `try` statement and the `ValueError`
  propagates out of the generator"

- `45_Effects--Generators` 2026-11-01, was Claude-written (same day,
  the over-correction of the sighting above), Bruce: 'This could be
  "the finally block runs"': "so Python runs the `finally` block on
  its way out of the `try` statement" -> "so the `finally` block runs
  on the way out of the `try` statement"

**Home.** activate (Accrued patterns) | this file.

### R56. Keep a phrasal verb's particle beside its verb

**Test.** A two-word verb whose particle sits after a noun-phrase
object: "carries the request out", "looks the name up", "turns the
sensor off", "shuts the generator down". The particle holds the verb's
meaning ("carry" is transport, "carry out" is perform), so the reader
finishes "carries the request" and then revises it when "out" arrives.
Move the particle next to the verb: "carries out the request", "looks
up the name", "turns off the sensor", "shuts down the generator". In a
heading, the same shape takes one verb instead ("Telling the Wrappers
Apart" -> "Distinguishing the Wrappers"). `tip sentence-shapes` lists
the prose shape as `[PRT]` (`tools/sentence_shapes.py`, 2026-11-04).

**Keep when.** The object is a pronoun or a one-word code span, which
English puts before the particle ("carries it out", "looks `name` up";
from the 2026-11-06 read of the rule's 58 sites: "leave the `Time()`
out" in chapter 47, and "turns N806 off" in chapter 13, where the rule
code is the one-word object).
The particle opens a path or a measure and is not the verb's meaning
("leaves the amount up to you", "sends a request up to the event loop",
"stops one level up", "passes the `Question` up and the answer down").
The joined form has another meaning ("pass the error up", since "pass
up" declines; "pass the tuple on"; "start the work over"; from the
2026-11-06 read: "leaves the decorator off" in chapter 15, "leave the
annotation off" in chapter 47, and "Ruff leaves those rules off by
default" in Solutions 02, since "leave off" is to stop; "hands the
dependency in" in Solutions 11, since "hand in" is to submit; "play a
pair off" in chapter 32, since "play off" is a tiebreaker) or no joined
form ("lets zero through", "leaves one student over"). That read moved
51 of the 58 sites and kept these seven, which are the baseline's first
`[PRT]` keeps.

**Sightings.** 2, two chapters (promoted 2026-11-04; the heading
sighting was C26).
- `29_Patterns--Changing_the_Interface` 2026-09-17 (`cacb544f`), was
  Claude-written, Bruce's own edit:
  "## Telling the Wrappers Apart" -> "## Distinguishing the Wrappers"
- `45_Effects--Generators` 2026-11-04, was Claude-written, Bruce:
  'general style: carries out the request':
  "waits while the driver carries the request out" -> "waits while
  the driver carries out the request"

**Home.** straighten (Accrued patterns) | CLAUDE.md watch list |
`tools/sentence_shapes.py` `[PRT]` | this file.

### R57. An alternative inside a walkthrough says it is the road not taken

**Test.** A paragraph that narrates a listing (its run, its output,
its design) holds a sentence about a construct, call, or design the
listing lacks, in the plain present, with nothing marking it: "A
`for` loop treats `StopIteration` as the normal end of the loop, so it
discards the exception" under a listing whose driver is a `try`
statement. The reader takes it as the next step of the run and has to
back up when it fails to match the listing. The second and later
sentences of an alternative are the common site: the opener carries a
frame ("Writing the fix as `type(self).total += 1`", "An `__init__()`
that assigns `_value_`") and the continuation drops it ("`C().show()`
then runs `B`'s version", "The lookup table then stays keyed by the
tuples, so `Tile(".")` raises a `ValueError`"), and the continuation
often contradicts the listing's own `#:` output. Frame it with the
lightest marker that carries over: name what it replaces ("With a
`return` at the match in place of the `break` at `[1]`"), a condition
("If `__init__()` assigns `_value_`"), a frame for the continuation
("In that version", "In that order"), a gerund subject ("Adding an
`as` clause to the `with` line"), a tie to the listing's choice
("because a `for` loop would discard the exception"), or a colon that
attaches the consequence to the thing that produces it. Check the
alternative's claim against a probe before framing it; a framed
misdescription is worse than an unframed one. `tip positional
ARGS=--survey` lists the opener shape as `survey alternative`
(`tools/positional_refs.py`, 2026-11-08); the continuation shape is
read by hand.

**Keep when.** A general fact that holds for the listing too, in a
paragraph that explains rather than narrates ("A `for` loop makes one
`iter()` call, then calls `next()`" in the section that introduces
`for`); an alternative an earlier sentence of the paragraph introduces
as one ("The real mistake is catching too much. A bare `except:` ...
catches the cancellation"), including a continuation under a
conditional opener in a Solutions step ("If you leave out `return
cls`, `announce` returns `None`. Python then binds `None` to
`Point`"); a comparison paragraph whose subject is the difference;
advice; a `Done when:` paragraph about the reader's own run.

**Sightings.** 3 chapters the day it was named (promoted 2026-11-08);
the book-wide read that day (Opus agents, brief in
`build/alt-2026-11-08/`) reworded more, most of them continuations.
- `45_Effects--Generators` 2026-11-08, was Claude-written, Bruce:
  "this seems like it's continuing to describe what happens in the
  code, but it's actually describing an alternative -- that's not
  clear. I have regularly seen this pattern of describing an
  alternative in the same place where the description of what's
  actually happening is described, and I would like to fix this
  everywhere":
  "A `for` loop treats `StopIteration` as the normal end of the loop,
  so it discards the exception and loses the return value." -> "The
  listing catches `StopIteration` in a `try` statement because a
  `for` loop would discard the exception. A `for` loop treats
  `StopIteration` as the normal end of the loop and drops the `Result`
  along with the exception."
- `35_Patterns--Flyweight` 2026-11-08, was Claude-written, the
  session's scan: "An `__init__()` that assigns `_value_` runs too
  late. The lookup table behind `Tile(".")` then stays keyed by the
  tuples, so `Tile(".")` raises a `ValueError`." -> "If `__init__()`
  assigns `_value_`, the assignment comes too late. In that version
  the lookup table behind `Tile(".")` keeps the tuples as its keys, so
  `Tile(".")` raises a `ValueError`."
- `07_Foundations--Classes` 2026-11-08, was Claude-written, an Opus
  agent, the continuation shape: "`C().show()` then runs `B`'s
  version." -> "In that order, `C().show()` runs `B`'s version."
- `45_Effects--Generators` 2026-11-12, was Claude-written, Bruce:
  "very confusing because our waiting() has none of that, maybe this
  isn't necessary": "`trap_states.py`'s `waiting()` returns
  `TrapState.WAITING` from its `case _`, and `state_machine.py`
  re-enters the state and prints its message again." -> cut. The
  sentence after it had the same fault and was turned to face the
  listing: "`TrapState.HOLDING`'s `chime` is a third field in its row;
  here `holding()`'s entry code prints it after the message." ->
  "`holding()`'s entry action is two `print()` calls, the message and
  the chime. In chapter 31's `trap_states.py`, the chime is a third
  element in `TrapState.HOLDING`'s row."
  Why the passes missed it: the Keep-when below let "prose that names
  another listing by file name" stand, and a filename possessive
  counted as that name. Two things made it no frame here. The listing
  on the page defines a `waiting()` too, so the reader took the
  sentence for a claim about it and found no `TrapState` and no
  `case _`. And `trap_states.py` is another chapter's file, last
  mentioned 80 lines up. `survey alternative` was quiet for the
  filename, and `survey absent-subject` for `waiting()`, which the
  listing names. The tests added that day: (1) a file name frames an
  alternative only when the name it qualifies is absent from the
  listing on the page, and when both listings define the name the
  sentence opens "In chapter NN's `file.py`,"; (2) a comparison with
  another chapter's listing, inside the walkthrough of this one, is
  first tested for need: if the walkthrough reads complete without it,
  or a comparison paragraph further on covers the point, cut it; (3)
  a comparison that stays opens on this listing's thing and says the
  other design second.
- `45_Effects--Generators` 2026-11-12, the same section, was
  Claude-written, Bruce: "I don't see this in the example under
  discussion": "A generator state keeps such a value in a local and
  passes it to the next state as an argument, `return
  selecting(amount)`, so each state receives the data it needs and the
  machine object disappears." -> "... passes it to the next state as
  an argument. In a vending machine with one generator per state, the
  state that takes the money ends with `return selecting(amount)`, and
  `selecting()` receives the amount as a parameter. In that design,
  parameters and locals hold the data that `VendingMachine` keeps in
  attributes."
  `selecting()` is defined in no listing in the book: the span was
  invented code, set in apposition to a general claim, so it read as a
  quotation from the listing above. Why the passes missed it:
  `survey absent-name` reads a lead-in's colon sentence, `survey
  absent-subject` reads a span that opens a sentence, and this span
  sat mid-sentence, five paragraphs below its listing; `survey
  alternative` looks for a construct the listing lacks and the
  sentence's constructs (`return`, an argument) are all in the
  listing. The test added: a statement in a code span (`return ...`,
  `yield ...`, `raise ...`, `name = ...`) is searched for in the
  chapter's listings, and one found in none is hypothetical code. It
  gets the design it belongs to as a condition ("In a vending machine
  with one generator per state,") and the sentences that continue it
  get "In that design". A scratch scan that day found 9 such spans in
  chapter 45 and 115 in `Chapters/`; the other 8 in chapter 45 were
  framed ("If `outer()` wrote `yield one()`", "with `values.append(a)`
  in place of `yield a`", an exercise statement).

**Home.** alternative (its own pass, `.claude/skills/alternative/SKILL.md`)
| ambiguity (catalog and Accrued shapes) |
`tools/positional_refs.py` `survey alternative` | this file.

### R58. A concessive "however" states the independence instead

**Test.** "however" followed by a quantity, degree, or manner word:
"however many `next()` calls that takes", "however large `n` gets",
"however the block finished", "However deeply the delegations nest".
The reader meets the contrastive adverb ("However, ...") far more
often, so a "however" after a comma or at a sentence start announces
a contrast, and only the next word says it is the quantifier "no
matter how". The clause is also R54's shape with "how" in place of
"which": a universal claim that the outcome is the same across every
count or manner. Repairs, in order of preference. Drop the clause
where the verb already says the thing holds still: "stays the same
however large `n` gets" is "stays the same as `n` grows", and "takes
O(log n) each time, however many times you repeat it" is "every
removal takes O(log n)". Name the range: "whether you then take 100
items or one", "whether it covers one byte of the buffer or all of
it", "slow or fast". State the independence: "at any depth of
delegation", "on a map of any size", "in every interleaving of the
tasks", "on every request". Name the options for the manner sense:
"whether the block completed or raised an exception", "under either
scheduling of the producers", "built by comprehension or by
`append()`". Or say what the universal amounts to in the listing:
"each cell goes to the first rat that reaches it", "every transition
into that state shares it". "no matter how many" is the fallback, and
still a universal.

**Keep when.** The contrastive adverb, "However," and ", however,", is
a different word and takes a comma; `tools/watch_words.py` skips a
"however" followed by a comma or a period. No keep of the concessive
sense yet: the 2026-11-08 sweep read all 39 sites in `Chapters/` and
`Solutions/` and rewrote every one, and the two generated exercise
quotes in `Solutions/` followed their chapters.

**Sightings.** 1 flag, promoted on Bruce's request to a book sweep the
same day (2026-11-08, "unclear usage of 'however'"): 39 sites, all
rewritten in session.
- `45_Effects--Generators` 2026-11-08, was Claude-written: "each
  `yield from` stays with its target until that generator finishes,
  however many `next()` calls that takes" -> "each `yield from` stays
  with its target, through every `next()` call, until that generator
  finishes"
- `45_Effects--Generators`: "However deeply the delegations nest, the
  program has one driver." -> "At any depth of delegation, the program
  has one driver."
- `03_Foundations--Containers`: "work that stays the same however
  large `n` gets" -> "work that stays the same as `n` grows"
- `15_Techniques--Context_Managers`: "Call the manager's `__exit__()`,
  however the block finished." -> "Call the manager's `__exit__()`,
  whether the block completed or raised an exception."
- `38_Patterns--Simulation`: "so each cell goes to one rat, however
  many reach it" -> "so each cell goes to the first rat that reaches
  it"
- `18_Techniques--Performance`: "A view's own size stays fixed however
  much of the buffer it covers" -> "A view's own size stays the same
  whether it covers one byte of the buffer or all of it" (the
  hold-constant "fixed" went with it)

**Home.** CLAUDE.md watch list (Tier 2, "however") | ambiguity
(catalog, "A connective with two senses", and Accrued shapes) |
`tools/watch_words.py` | this file.

### R59. "X is how Y" hides X's verb; write what X does

**Test.** A sentence whose subject names a thing (a call, a type, a
construct, a mechanism, or a nominalized action: "`close()`", "`Need`",
"Assignment", "The reflected call", "That release") and whose predicate
is "is how", "is where", "is when", or "is why" plus a clause. The
copula and the wh-word stand in for the verb that relates the thing to
the clause, so the sentence says the thing's role and leaves the
mechanism out: "`close()` is how a driver ends a generator early" says
that `close()` is involved and lets the reader supply the rest. Bruce
(2026-11-09, chapter 45): "I don't like the hand-waviness of 'is how'.
Is the mechanism, is the tool for, or something else that is more
precise." Repair: lead with the purpose and make the action the verb (R60), or
make the clause the main clause and put the thing in a phrase that
states its part ("To end a generator early, a driver calls `close()`"; "Most programs meet an exception group in a
`TaskGroup`"; "A new duplicate goes at `right`"), or give the thing its
own verb ("`E` is its failure type"; "An assignment makes a name local
to the function"; "Because the GIL is released during a wait, a thread
pool helps with I/O-bound work").

**Keep when.** The subject is an abstraction whose content the
wh-clause is: "the question is when a hint is worth the words", "The
difference is how many places you edit", "The cause is where the
factory searches", "What changes is where you define the operation".
There the clause is an embedded question and no verb is hidden. A
pronoun subject that points at the clause before ("That is why
`doubled_ok()` uses `for`", "which is why the run still prints a
message", "which is how `list[int]` works at runtime") is a connective,
read by the antecedents pass, and stays unless "so" says the same.

**Sightings.** 1 flag, promoted on Bruce's request to a book sweep the
same day (2026-11-09): 80 sites of "is/are how|where|when|why" in
`Chapters/` and `Solutions/`, 50 rewritten (three Opus agents by chapter
band, chapter 45 by hand), 30 kept. The keeps split by the two shapes
above: nine abstractions whose content the clause is, accepted into
the watch-words baseline, and the pronoun connectives, which the check
skips; two "which is where" sites stayed because "so" did not fit.
- `45_Effects--Generators` 2026-11-09, was Claude-written: "`close()`
  is how a driver ends a generator early." -> "To end a generator
  early, a driver calls `close()`." (R60's form)
- `46_Effects--Stateless`: "`Need` is how Stateless does dependency
  injection." -> "Stateless does dependency injection with `Need`.";
  "`E` is how it can fail." -> "`E` is its failure type."
- `19_Techniques--Concurrency`: "`TaskGroup` is where most programs
  meet an exception group" -> "Most programs meet an exception group
  in a `TaskGroup`"; "A thread waiting on I/O releases the GIL. That
  release is why a thread pool helps with I/O-bound work." -> "A
  thread waiting on I/O releases the GIL, so a thread pool helps with
  I/O-bound work."
- `32_Patterns--Multiple_Dispatching`: "The reflected call is how a
  type written decades after `int` can sit to the right of an `int` in
  a sum." -> "The reflected call lets a type written decades after
  `int` sit to the right of an `int` in a sum."
- `Solutions/40_Functional--Foundations`: "Assignment is how Python
  decides a name is local." -> "Python decides that a name is local
  when the function body assigns it."
- `Solutions/18_Techniques--Performance`: "`right` is where a new
  duplicate goes, after the existing ones, and it is the wrong index
  to read." -> "A new duplicate goes at `right`, after the existing
  ones, but `right` is the wrong index to read."
- Twenty-two "which is why" or "That <noun> is why" connectives became
  "so" across the book, where "so" read the same.

**Home.** CLAUDE.md watch list (Tier 2, "is how") | literal (Accrued
patterns) | `tools/watch_words.py` | this file.

### R60. Lead with the purpose; make the action the verb

**Test.** The main verb names an outcome, and a "by <gerund>" phrase
names the action the subject takes to reach it: "A driver ends a
generator early by calling `close()`". The action is the one event
the reader can picture and the outcome is its purpose, yet the
sentence subordinates the action into a gerund, states the outcome as
the verb, and opens on the actor. Bruce's rewrite (2026-11-09, chapter
45): "To end a generator early, a driver calls `close()`". "Notice
that mine is more active and it also starts with the most important
thing (ending a generator early rather than 'a driver')." Repair: open
with the purpose as an infinitive and make the action the main clause:
"To end a generator early, a driver calls `close()`"; "To isolate a
database, a test passes a fake"; "To skip a value, the loop
continues". For a mechanism as subject, where a purpose does not fit,
give it the action as its verb and the outcome as a result clause:
"`@cache` stores each result, so a repeated call returns at once".
R59's first repair follows this rule.

**Keep when.** The "by" phrase names an instrument, a criterion, or an
agent rather than an action the subject takes ("sorts the list by
key", "finds the item by index", "is built by the decorator"). The
outcome is the sentence's news and the next sentence builds on it, so
the method is incidental. The sentence narrates a run on the page
("the test caught it by asserting on stdout") rather than a standing
method.

**Sightings.** 1, promoted at Bruce's call (2026-11-09), then a book
sweep the same day: 190 "by <gerund>" sites in `Chapters/` and
`Solutions/`, 64 rewritten (three Opus agents by chapter band, chapter
45 by hand), 126 kept. The keeps, by the agents' labels: a mechanism's
manner ("CPython frees most objects by counting references",
"`supply()` resolves at runtime by scanning its arguments"), an
instrument or criterion ("check by reading", "sorts by key"), the
outcome as the news the next sentence builds on, a narrated run,
exercise statements, and the sequence idioms ("opens by", "ends by",
"starts by").
- `45_Effects--Generators` 2026-11-09, Bruce's hand on a Claude
  rewrite: "A driver ends a generator early by calling `close()`."
  -> "To end a generator early, a driver calls `close()`."
- `11_Techniques--Testing`: "Run the test suite by typing `pytest` in
  the project directory." -> "To run the test suite, type `pytest`
  in the project directory."
- `19_Techniques--Concurrency`: "The programmer minimizes context
  switches by choosing where the code yields control." -> "To
  minimize context switches, the programmer chooses where the code
  yields control."
- `38_Patterns--Simulation`: "`landing()` decides whether a door is
  passable by testing the occupant's type with `isinstance()`." ->
  "To decide whether a door is passable, `landing()` tests the
  occupant's type with `isinstance()`."
- `29_Patterns--Changing_the_Interface`: "An adapter implements `f()`
  by calling `g()` and `h()`." -> "To implement `f()`, an adapter
  calls `g()` and `h()`."
- `12_Techniques--Data_Classes_as_Types`, a hazard keeps a gerund
  subject: "A caller can skip the check by calling the type instead
  of the factory:" -> "Calling the type instead of the factory skips
  the check:"
- `20_Patterns--Rethinking_Objects`, the purpose reads better last:
  "Java encouraged reusing code by inheriting implementation." ->
  "Java encouraged inheriting implementation to reuse code."

**Home.** CLAUDE.md (dedicated bullet after "X is how Y") | activate
(Accrued patterns) | this file.

### R61. A causative demotes the actor; put the actor in the subject

**Test.** A causative verb (requires, lets, allows, makes, forces,
enables, causes, permits, needs, gets) whose object is the thing that
acts and whose infinitive is the real event: "`close()` requires the
generator to finish", "the decorator lets the caller skip the check",
"`slots=True` makes `dataclass()` build a new class". The sentence is
active in form, but the actor sits in object position and its action
hangs off it as an infinitive, so the reader builds the causer's
clause first and meets the event second. Bruce (2026-11-09, on
chapter 45's heading "`close()` Requires the Generator to Finish"):
"see how passive that is? Maybe something like: '`close()`: the
generator must finish'." Repair: make the actor the subject with its
own verb or modal, and attach the causer as a condition, a phrase, or
a colon lead-in: "`close()`: the generator must finish"; "the caller
can skip the check"; "under `slots=True`, `dataclass()` builds a new
class"; "when the exception arrives, the driver stops".

**Keep when.** The causer is the claim and the actor is incidental
("`@record` makes every field read-only" has an adjective complement
and no demoted actor). A passive causative ("is required to") is the
passive rule's. "need" with a noun object and no event ("needs a
lock"). A causative whose object is not an agent and whose infinitive
is the point ("lets the type checker see the mismatch" names what the
checker does; test whether "the type checker sees the mismatch" with
the causer as a phrase reads better, and keep when it does not).
`tip sentence-shapes ARGS=--survey` lists the shape as `[CAUS]`, a
survey rule, since the parse cannot tell a demoted actor from an
incidental object.

**Sightings.** 2 flags, promoted at Bruce's call (2026-11-09), then a
book sweep the same day over the `[CAUS]` list: 308 sites, 112
rewritten (four Opus agents by chapter band, chapter 45 by hand), 196
kept. The keeps, by the agents' labels: a stative complement ("makes
instances unhashable", "depend on the schedule"), a causer that is the
claim with the type checker or Python as the object ("`@final` makes
the type checker report a subclass", a gerund edit that makes `ty`
report), an imperative or a step label ("Let the type checker infer
the rest"), a title, "need" or "want" with a purpose infinitive, an
exercise statement, and "make" as a light verb ("makes the same
calls"). Rewrites that worked: a condition or phrase for the causer
("Under `slots=True`, `dataclass()` builds a new class"; "With a
closure, a function carries state"), a modal for the actor ("Callers
must pass the fields after `KW_ONLY` by keyword"), the event as the
verb ("`throw(exc)` raises `exc` at the `yield`"), and a split where
the causative joined two claims ("gives each cast a narrator. Each
cast chooses its actors.").
- `45_Effects--Generators` 2026-11-09, heading, was Claude-written:
  "`close()` Requires the Generator to Finish" -> "`close()`: The
  Generator Must Finish"
- `45_Effects--Generators` 2026-11-09, same section, was Claude-written
  (Bruce: "weird and passive, the passivity makes it more complicated"):
  "A generator written for others to drive therefore lets
  `GeneratorExit` end it." -> "A generator for a driver must therefore
  finish when `GeneratorExit` arrives: it cleans up and returns."
- A second read the same day, before the 197 hits then standing were
  recorded as judged in the survey baseline (two Opus agents by
  chapter band, the session sampling their keeps and deciding their
  close calls), rewrote one more and kept 196.
  `26_Patterns--Factory`, a section title as the causer, where "the
  causer is the claim" cannot hold: "[Explicit Registration with a
  Protocol] makes the checker report a class that lacks `draw()` at
  the line that registers it." -> "In [Explicit Registration with a
  Protocol], the checker reports a class that lacks `draw()` at the
  line that registers it." Kept after a close look: a body that
  chooses to step aside ("It can handle the exception and yield
  again, clean up, or let the exception end the generator:", chapter
  45), a run of settings each stated first ("`random.seed(42)` makes
  the hand-written loop draw the same strings"), and the type
  checker's enforcement as the claim ("The type checker makes a
  caller tell the two apart").

**Home.** activate (Accrued patterns) | `tools/sentence_shapes.py`
(`[CAUS]`, with its read keeps in
`tools/data/sentence_shapes_survey_baseline.txt`) | this file.

### R62. Code does not "draw" an exception or a diagnostic; its actor raises or reports it

**Test.** "draws" (draw, drew, drawn) whose object is an exception, a
diagnostic name, or a noun for one (a diagnostic, a finding, a type
error, a warning): "A `yield` inside a `finally` clause draws the same
`RuntimeError`", "passing it draws `invalid-argument-type`", "`fetch()`
draws a finding". Bruce (2026-11-09, chapter 45): "'draws' is confusing
-- produces?" Three faults sit in the one word. It is a figure: "draw"
here means "attract", as in "draw criticism", while the reader's first
sense is "sketch", and the book has about 400 literal sites of that
sense (`draw()` on the shapes of chapters 08, 26, 32, and 36). It makes
the offending code the subject and leaves the actor out: a `yield`
raises no `RuntimeError`, `close()` does, and an assignment reports
nothing, the type checker does (R55). And it replaces the verb the book
has taught for the event: an exception is raised, a diagnostic is
reported. A different verb makes the reader ask whether a different
event is meant. Repair: name the actor and give it the taught verb,
with the offending code as a condition, a place, or a gerund subject of
its own clause: "If a generator yields inside a `finally` clause,
`close()` raises a `RuntimeError` with the message shown for `stubborn()`"; "so the type checker reports
`invalid-argument-type` when you pass it"; "the type checker reports
`invalid-assignment` on that line". "Produces" is not the repair. It
keeps the wrong subject, and in a chapter about generators a `yield`
that "produces" a `RuntimeError` reads as yielding one. Where the code
is the natural subject and the actor is obvious, "is" plus the
diagnostic works: "A call that leaves out `width` is a
`missing-argument` error".

**Keep when.** The literal sense: a shape draws, a method draws a
line, a figure is drawn. "Draws on" meaning uses. The idioms "draws a
distinction", "draws a conclusion", and "draws the line", which the
literal pass judges by its own test and which carry no hidden actor.
None seen yet for the flagged sense.

**Sightings.** 1 flag, made a rule at Bruce's call (2026-11-09), then
a book sweep the same day (six Opus agents by chapter band, brief in
`build/same-draws-2026-11-09/`, chapter 45 by hand): about 30 sites
rewritten in 22 files, nearly all a type-checker diagnostic, and no
figurative site kept. Six literal hits the scan matches ("draws `n`
random pairs", "To draw the `Room`", "draws from `SHAPES`") are in the
watch-words baseline. The forms that worked: "the type checker reports
X" with the code as an "If you" condition or a "when" clause, "is an X
error" where the call is the natural subject, and `ty` kept where the
sentence or the one before names it. A "Done when" criterion takes the
"If you" form.
- `08_Foundations--Static_Types`: "A call that leaves out `width`
  draws `missing-argument`." -> "A call that leaves out `width` is a
  `missing-argument` error."
- `Solutions/30_Patterns--Observer`: "Making that change in the first
  version draws `invalid-argument-type` at `t.attach()`." -> "If you
  make that change in the first version, the type checker reports
  `invalid-argument-type` at `t.attach()`."
- `B_An_Effect_Checker`: "so `fetch()` draws a finding." -> "so the
  checker reports a finding for `fetch()`."
- `45_Effects--Generators` 2026-11-09, was Claude-written: "A `yield`
  inside a `finally` clause draws the same `RuntimeError`, `generator
  ignored GeneratorExit`." -> "If a generator yields inside a
  `finally` clause, `close()` raises a `RuntimeError` with the message
  shown for `stubborn()`, `generator ignored GeneratorExit`."

**Home.** CLAUDE.md watch list (Tier 2, "draws") | literal (Accrued
patterns) | `tools/watch_words.py` | this file.

### R63. "The same X" has a second term the reader can name

**Test.** At each "the same X", ask "same as what?" and answer as a
reader who has this sentence, the sentence before it, and the adjacent
listing. "Same" is a comparison, and the reader goes looking for its
second term. The sentence fails when the search has more than one
result or none: (1) two candidates fit, since the page holds two
errors, two listings, two calls, or two classes; (2) the second term is
more than a sentence or an adjacent listing away; (3) a phrase after
the noun, an appositive, a quoted message, or a code span, reads as the
second term and is not; (4) the sentence opens a paragraph or follows a
listing that has several X; (5) nothing is compared, C55's shape, where
"same" is a pointer; (6) the noun after "same" was never introduced
("the same separation", "the same hazard", "the same machinery"), so
the reader has no first term to match; (7) the two things are not the
same. "Same" is a claim, so check it against the listing: "the same
`Queue`" beside a listing that uses a `PriorityQueue`, "the same guard"
where the two tests differ, "small in the same way" as a thing that is
absent. Bruce (2026-11-09, chapter 45, on "raises the
same `RuntimeError`, `generator ignored GeneratorExit`"): "same as
what". Repair: name the second term with words the passage has ("the
message shown for `stubborn()`", "the `TypeError` that `parse()`
raised", "as in `registry.py`", "as `bump()` does"), or, where identity
is not the claim, write the pointer ("that", "its", "the"). Where the
thing is no longer than the pointer, write the thing ("with
`metaclass=Singleton`", "the block's `ValueError`", "raises
`Tripwire`"). Where the second term is the sentence's own "each" or
"every", put it before an appositive ("makes the same call on each
element, `element.accept(visitor)`").

**Keep when.** The second term is in the sentence ("the same X as Y",
"both use the same X", "the same X in both"). It is the one candidate
in the previous sentence or the adjacent listing. The idioms ("the same
way" after the way is described, "at the same time", "stays the same").
Identity against a possible copy ("returns the same `cls` it
received"), and an unchanged input against a changed output ("the same
command now reports:"). Exercise statements and quoted diagnostics.

**Sightings.** 1 flag, made a rule at Bruce's call (2026-11-09), with
C55's sightings as shape 5. The book sweep the same day (six Opus
agents by chapter band, brief in `build/same-draws-2026-11-09/`) read
all 1,370 "same" sites and rewrote about 30, one in 45. By shape: a
second term in another section or several sentences back (the most
common), two candidates on the page, an appositive posing as the term,
and nothing compared. The keeps: a term in the sentence, one adjacent
candidate, and the idioms. The agents listed 42 close-call keeps, and
Bruce had the session answer "same as what?" on each (the Same Keeps
page, 2026-11-09, the answers recorded on its cards): 22 rewritten, 19
kept, and one gone with its sentence. That read found shapes 6 and 7.
The 19 keeps: the term in the sentence or in the sentence before, a
count that identifies the set ("the same four lines", "the same 36
answers"), "same" set against a stated difference ("runs the same
search with inputs it chooses"), and "the same way" straight after the
way. Test 6 became the `[SAME+NEW]` survey rule in
`tools/sentence_shapes.py` the same day (a "same" whose noun has no
cognate in the 30 source lines above). Its first book-wide run had
117 hits, and the session's read rewrote 20. Most were a second noun
for a thing the passage had named one sentence earlier, so the repair
was the passage's noun; three were untrue or stated their term only
afterward. The 96 keeps are a summary noun for the sentence before
("Gradual typing faced the same problem", "uses the same technique")
and "same" set against a stated difference ("the same answer by a
different algorithm"). They are the first entries of the rule's own
baseline, `tools/data/sentence_shapes_survey_baseline.txt`, so the
survey prints only a hit not yet judged. `[SAME]` joined that
baseline the same day, after the session reread its 143 standing hits
with their passages: 139 kept, 4 rewritten (the four sightings marked
"reread" below). Three were test 6 where `[SAME+NEW]` is quiet by
design, a command and a cognate in another sense inside its 30 lines,
so the read still applies test 6 by hand. One was test 7.
- `44_Effects--Effect_Management`, one sentence after "this design":
  "Flix expresses the same model with different notation." -> "the
  same design"
- `36_Patterns--Memento`, a role for a named thing (R52): "the same
  generic caretaker holds mementos of the mutable `Sketch`" ->
  "`History` holds mementos of the mutable `Sketch`"
- `43_Functional--Confidence`, the section's own term: "The same
  substitution serves your reasoning" -> "Referential transparency
  serves your reasoning"
- `42_Functional--Error_Handling`, untrue, since the lead-in two
  sentences later says "both limits": "The caller's side has the same
  limit." -> "The caller's side has a limit too."
- `Solutions/47_Effects--Stateless_in_Practice`, a term stated only
  afterward: "Exercise 2 draws the same distinction from the other
  side." moved below the two sentences that state the distinction, as
  "Exercise 2 draws that distinction from the other side."
- `Solutions/19_Techniques--Concurrency`, a figure on a new noun:
  "`InterpreterPoolExecutor` wins the same benchmark" -> "With
  `InterpreterPoolExecutor` that comparison is `True`"
- `02_Foundations--Tour`, a noun never introduced: "`safe()` uses the
  same separation to check each value." -> "`safe()` checks each value
  while it is still separate from the literal text."
- `19_Techniques--Concurrency`, not the same thing (the listing uses a
  `PriorityQueue`): "uses the same `Queue` as a throttle" -> "uses a
  `Queue`'s blocking `get()` as a throttle"
- `47_Effects--Stateless_in_Practice`, a comparison that does not hold:
  "The operator set is small in the same way." -> "The operator set is
  small."
- `Solutions/17_Techniques--Metaprogramming`, the thing is shorter than
  the pointer: "with the same `metaclass=` argument" -> "with
  `metaclass=Singleton`"
- `33_Patterns--Visitor`, "each" before the appositive: "makes the
  same call, `element.accept(visitor)`, on each element" -> "makes the
  same call on each element, `element.accept(visitor)`"
- `Solutions/11_Techniques--Testing`, a term stated only afterward:
  "Exercise 4 draws the same lesson from the environment variable." ->
  "In exercise 4, the patched test depends on the name of an
  environment variable."
- `24_Patterns--Template_Method`, three `TypeError`s in the listing:
  "raises the same `TypeError`." -> "raises a `TypeError` with the
  message shown for `Hijack`, `overrides a @final method`."
- `Solutions/47_Effects--Stateless_in_Practice`, two traces: "prints
  the same trace" -> "prints the `short` trace"
- `Solutions/44_Effects--Effect_Management`, nothing compared: "The
  same value always passes `validate()`" -> "A value of 1 or more
  always passes `validate()`"
- `Solutions/18_Techniques--Performance`, two readings (equal times,
  or the work counted again): "Every caller on the path accumulates
  the same time." -> "Every caller on the path counts that work
  again."
- `41_Functional--Toolkits`, a section opener: "The same dispatch,
  written as a method" -> "The same dispatch as `singledispatch()`,
  written as a method"
- `45_Effects--Generators` 2026-11-09, was Claude-written: "`close()`
  raises the same `RuntimeError`, `generator ignored GeneratorExit`."
  -> "`close()` raises a `RuntimeError` with the message shown for
  `stubborn()`, `generator ignored GeneratorExit`."
- `15_Techniques--Context_Managers` (reread), a noun the chapter had
  used once, as a verb, 650 lines up, one sentence after "one setup,
  one teardown": "Add `ContextDecorator` only when the same bracket
  should also wrap whole functions." -> "the same setup and teardown"
- `21_Patterns--Design_Patterns` (reread), a noun for what the passage
  said with a verb ("It describes what a caller needs"), under an
  unrelated "Declaring that a design": "[Stateless] moves the same
  declaration into a function's signature" -> "moves that description
  into a function's signature"
- `29_Patterns--Changing_the_Interface` (reread), a nominalization
  under a quoted "Liskov Substitution Principle": "[*Surrogate*] makes
  the same substitution for a proxy's implementation." -> "does the
  same for a proxy's implementation."
- `Solutions/32_Patterns--Multiple_Dispatching` (reread), not the
  same thing: "The weapon ranking is a cycle. ... The same cycle
  appears at the group level." -> "A second cycle appears at the
  group level."

**Home.** CLAUDE.md (the "same" bullet) | ambiguity (the comparison
entry and Accrued shapes) | `[SAME]` (shape 5) and `[SAME+NEW]`
(shape 6), with a shared baseline of judged keeps, in
`tools/sentence_shapes.py` | this file.

## Candidates

One sighting each. Logged, not applied. A second sighting in a different
chapter promotes one; several capture rounds with no second sighting mean it
was a one-off, and it can be retired at Bruce's call.

### C1. Drop the universal form where the indefinite carries it

**Test.** "any X" or "whatever a X" where "a X" / "what the X" means the
same, because the sentence already quantifies ("an instance of any
subclass must work" -> "an instance of a subclass must work").

**Keep when.** The universality is the claim ("any exception, not only
`ValueError`").

**Sightings.** 2, both `24_Patterns--Template_Method` 2026-08-29, was
Claude-written (same chapter, so not yet independent):
- "an instance of any subclass must work in its place" -> "an instance of
  a subclass must work in its place"
- "trusting that whatever a subclass supplies still fits" -> "trusting
  that what the subclass supplies fits"

### C7. Give a bare comparative its noun

**Test.** "looks/seems/is [comparative]" ("looks stronger", "is
simpler") with the compared quality unnamed. Supply the noun the
comparative modifies.

**Keep when.** The noun is the previous sentence's subject and repeating
it would be padding.

**Sightings.** 1 (additive), `26_Patterns--Factory` 2026-09-01
(`40323f50`), was Claude-written:
- "Nesting the classes inside `factory()` looks stronger and is worse"
  -> "looks like stronger enforcement and is worse"

### C10. Join a two-part contrast with "Whereas" or "while"

**Test.** Two adjacent sentences, or two halves of a semicolon, with
the same frame and opposite predicates and no connective ("A factory
takes information telling it what to build. A generator object does the
opposite:"; "In `registry.py` the table holds classes. In
`prototype_registry.py` the table holds instances."). Join them:
"Whereas a factory ..., a generator object does the opposite:"; "that
table holds classes ..., while `prototype_registry.py`'s holds
instances".

**Keep when.** The two sentences are a deliberate two-beat ("Failures
never vanish. They only relocate.").

**Sightings.** 3 (additive), all `26_Patterns--Factory`, was
Claude-written (same chapter, so not yet independent):
- 2026-08-31: "Where" in `40323f50`, corrected to "Whereas" in
  `d6144479`
- 2026-08-31 (`2b18eed8`): "Compare `spawn()` with `make()` in
  `registry.py`. In `registry.py` the table holds classes and calls a
  constructor. In `prototype_registry.py` the table holds instances and
  copies them." -> "Compare `spawn()` with `make()` in `registry.py`:
  that table holds classes and calls a constructor, while
  `prototype_registry.py`'s holds instances and copies them."
- 2026-09-12 (`a9731125`): "A closed set of names suits `Literal`; an
  open set, growing by subclassing, does not:" -> "A closed set of names
  suits `Literal`, while an open set does not:"

### C11. Cut "need(s) to" where the sentence describes rather than obliges

**Test.** "needs to VERB" / "need to VERB" describing what happens or
what is the case, not an obligation on the reader. Use the plain verb.

**Keep when.** The obligation is the claim ("every subclass must
supply a step", which R6 covers).

**Sightings.** 2, both `26_Patterns--Factory` 2026-09-01 (`40323f50`),
was Bruce-written (older draft) and Claude-written respectively:
- "the only other code in the system that needs to change" -> "the
  only other code that changes"
- "that's the only place you need to change the code" -> "that method
  is the only code you change"

### C13. Name a listing by its filename, not "the listing" or "this listing"

**Test.** "the listing" / "this listing" / "the example" as the subject
of a claim about a listing that has a `# name.py` header, where another
listing sits in the same section. Write the filename in code font.

**Keep when.** The filename was the previous sentence's subject, so
repeating it would be padding.

**Sightings.** 2, both `26_Patterns--Factory` 2026-08-31, was
Claude-written (same chapter, so not yet independent):
- (`d6144479`) "The listing keeps the plain names because" ->
  "`shape_factory1.py` keeps the plain names because"
- (`0b7ff81d`) "This listing keeps it because that is the form a
  factory-object design takes" -> "`shape_factory2.py` uses it to show
  the form a factory-object design takes"

### C16. Cut a sentence-opening locator on a sentence stating a general property

**Test.** "Here,", "In this example,", "As an example," opening a
sentence whose claim is about the pattern or design in general, not
about the adjacent listing ("Here, the steps must come in order, later
steps depend on earlier ones" is a claim about Builder). Delete the
locator, or move "here" to the end when the sentence does describe the
listing.

**Keep when.** The locator points at a fact of the adjacent listing.
Bruce kept four such openers in the same chapter ("Here `Triangle` has
just joined the hierarchy", "Here that argument is a string", "Here it
is a `Protocol`", "Here the table holds instances") and wrote a fifth
("Here, we create one factory object per `Shape` subtype:"). The
keep-when is the larger set; a sweep reads the sentence, not the word.
`27_Patterns--Function_Objects` 2026-09-16 adds one more keep: Bruce split "In
Python the action is a function, and a 'macro' is a list of actions"
into "In Python the action is a function. In this example, a 'macro'
is a list of actions:", a locator on the listing-specific claim only.

**Sightings.** 3, all `26_Patterns--Factory` (same chapter, so not yet
independent):
- 2026-08-31 (`2b18eed8`), was Bruce-written (older draft): "In this
  example, the setup and play are simple, but" -> "Setup and play are
  simple here, but"
- 2026-09-12 (`3e631333`), was Claude-written: "As an example, revisit
  the `Shape` hierarchy" -> "Consider the `Shape` hierarchy"
- 2026-09-15 (`a9ca27eb`), was Claude-written: "Here, the steps must
  come in order" -> "The steps must come in order"

### C17. In a decision list, state each condition as "When ..., action"

**Test.** A bulleted list whose items are shaped "condition: action"
with the condition a bare clause ("The choice is which arguments to
pass, not which class: write an alternative constructor"). Write "When
the choice is which arguments to pass, not which class, write an
alternative constructor."

**Keep when.** The item's lead is a label naming a thing rather than a
condition; R5 governs those.

**Sightings.** 1 (one list of six items), `26_Patterns--Factory`
2026-09-15 (`a9ca27eb`), was Claude-written:
- "A name maps to a class: use a dictionary." -> "When a name maps to a
  class: use a dictionary." (the colon survived on this item alone)
- "The choice is which arguments to pass, not which class: write an
  alternative constructor" -> "When the choice is which arguments to
  pass, not which class, write an alternative constructor"
- "You must choose several products together as a matched set: use
  Abstract Factory" -> "When you must choose several products together
  as a matched set, use Abstract Factory"
- likewise "Construction takes real work", "The interesting part of an
  object", "Construction is a genuine process"

### C18. A premise that is new information stands as its own statement, then "so" or "Thus"

**Test.** "If X, Y", "Since X, Y", or "Because X, Y" where X is the
first time the reader meets the fact. Write X as a statement and attach
Y with "so", or as its own sentence followed by "Thus, Y". The mirror of
R4, which fronts an already-established X with "Because".

**Keep when.** X was established earlier, so R4 applies. Narrowed
2026-10-11 (Bruce, at chapter 30's capture): when the claim's subject
is the paragraph's topic, the claim leads and the premise follows
with "because", even though the premise is new information.

**Sightings.** 4, 2 chapters (the second a narrowing rather than a
match, so not yet promoted):
- `30_Patterns--Observer` 2026-09-27 (`5d98cbbf`), from Bruce's
  paragraph note, the narrowing: "Iterating over an enum produces its
  members in definition order, so `list(Color)` is the cycle of
  colors." -> "`list(Color)` is the cycle of colors, because iterating
  over an enum produces its members in definition order." The
  paragraph is about `Color`'s cycle, so the claim leads.
- `26_Patterns--Factory` 2026-08-31, three (same chapter, so not yet
  independent):
- (`2b18eed8`), was Bruce-written (older draft): "If your program must
  call this factory whenever it needs one of your objects, then you
  change only the factory" -> "Your program must call this factory
  whenever it needs one of your objects, so you change only the
  factory"
- (`2b18eed8`), was Bruce-written (older draft): "Since every
  object-oriented program creates objects, and since you will likely
  extend your program by adding new types, Factory might be the most
  common design pattern." -> "Every object-oriented program creates
  objects, and you often extend that program by adding new types. Thus,
  *Factory* might be the most common design pattern."
- (`40323f50`), was Claude-written, R4's recorded keep-when: "Because
  the registry keys on `cls.__name__` alone, two classes that share a
  name ... overwrite each other" -> "The registry keys on `cls.__name__`
  alone, so two classes that share a name ... overwrite each other"

### C21. Cut the chapter roadmap paragraph; each sentence goes where its content is

**Test.** An opening paragraph whose sentences each say what a later
section will show ("*Command* appears first as a function, then as the
classic class-based form. ... A closing section keys the chain's
handlers by event type"). Delete it, and make sure each section states
the claim itself.

**Keep when.** None seen yet.

**Sightings.** 1 (removal), `27_Patterns--Function_Objects` 2026-09-16, was
Claude-written:
- the seven-sentence roadmap after the opening ("*Command* appears
  first as a function, then as the classic class-based form.
  *Strategy*'s function form gets the same fuller listing. ... and the
  list becomes an *event bus*.") -> deleted

### C23. Factor a property shared by two parallel sentences into one clause before them

**Test.** Consecutive sentences about parallel items that each restate
the same property ("`@event` makes a class a frozen data class and
...", "`@handler` makes a class a frozen data class too, ..."). State
the shared property once, in a clause introducing the pair, and let
each sentence carry only what differs.

**Keep when.** None seen yet.

**Sightings.** 1 (structural), `27_Patterns--Function_Objects` 2026-09-16, was
Claude-written:
- "A second version gives each side a decorator. `@event` makes a class
  a frozen data class and records it in `EVENTS`. `@handler` makes a
  class a frozen data class too, a function object whose fields are its
  configuration, and records in `HANDLES` ..." -> "A second version
  gives each side a decorator, both producing frozen data classes.
  `@event` records its class in `EVENTS`. `@handler` makes a function
  object whose fields are its configuration, and records in `HANDLES`
  ..."

### C24. A reader's action reads "To X, you Y", not "X-ing means Y-ing"

**Test.** A gerund subject with "means" and a second gerund, where the
subject is something the reader does ("Adding, removing, or reordering
handlers means editing a list."). Write "To add, remove, or reorder
the handlers you edit the `chain` list." The mirror of R15, which
takes "you" off a sentence about how the design behaves.

**Keep when.** None seen yet.

**Sightings.** 1, `27_Patterns--Function_Objects` 2026-09-16, was Claude-written:
- "Adding, removing, or reordering handlers means editing a list." ->
  "To add, remove, or reorder the handlers you edit the `chain` list."

### C27. Call an operation by the name its mechanism uses

**Test.** A synonym standing in for a term the section's API spells
("retire" for `warnings.deprecated()`'s deprecate). Use the API's word.
The inverse of R3, which keeps an identifier's word out of its ordinary
sense nearby.

**Keep when.** The synonym names a different act. The same edit
separated *replacing* an interface (the unsafe move) from *deprecating*
it (the mark that makes it safe).

**Sightings.** 1, `29_Patterns--Changing_the_Interface` 2026-09-16
(`f5a7b213`), was Claude-written:
- "## Retiring the Old Interface" -> "## Deprecating the Old Interface";
  "Retiring an interface is the unsafe move." -> "Replacing an
  interface you own is the unsafe move, because every caller was
  written against the old one."; "someone decided to retire this" ->
  "this should no longer be called"

---

### C28. "one X at a time", not "only one X ... at a time"

**Test.** "only one" and "at a time" in one clause with words between
them. Bruce (Only Shapes page): "'only one' is too far away from 'at a
time'." Drop `only` and move "at a time" next to "one".

**Keep when.** None seen yet.

**Sightings.** 5, all `19_Techniques--Concurrency`, 2026-10-04
(`c06fecc2`), the `only` sweep applying Bruce's rulings on the Only
Shapes page (one chapter, so not yet independent):
- "the interpreter-wide lock that lets only one thread run Python bytecode
  at a time" -> "that lets one thread at a time run Python bytecode"
- "so only one task holds it at a time" -> "so one task at a time holds
  it"
- "whose authors assumed that only one thread runs at a time" -> "whose
  authors assumed that threads run one at a time"
- "the event loop lets only one coroutine touch it at a time" -> "lets one
  coroutine at a time touch it"

### C29. "not only X but also Y" takes parallel halves, or "both X and Y"

**Test.** "not only X but also Y" where X and Y differ in kind (a noun
against a clause, a phrase against a sentence). Make the halves the same
kind, or write "both X and Y". Bruce marked the chapter 28 sentence
"garbled".

**Keep when.** The halves already match; most "not only ... but" pairs in
the book were kept.

**Sightings.** 2 (chapters 25 and 28), 2026-10-04 (`c06fecc2`), the `only` sweep applying Bruce's rulings on the Only Shapes page; thin, so held as a
candidate at the capture's suggestion:
- `27_Patterns--Function_Objects`: "The tests can then assert not only the
  root but also which finders ran." -> "The tests can then assert both the
  root and the names of the finders that ran."
- `24_Patterns--Template_Method`: "should expect to rename an occasional
  legitimate method, not only to catch misspellings" -> "should expect to
  catch typos and also to rename an occasional legitimate method"

### C31. Show the code the prose describes (additive)

**Test.** A sentence describes code in words ("becomes an awaitable
method", "the generated constructor takes the fields", "clears the
canvas") when the actual call or signature fits in a code span. Write
the code span: "a caller writes `await t.set_celsius(value)`".

**Keep when.** The code is longer than a line, or the listing holding
it sits directly beside the sentence.

**Sightings.** 3, one chapter (`30_Patterns--Observer`, 2026-10-11)
- "becomes an awaitable method" -> "a caller writes
  `await t.set_celsius(value)`"
- "the generated constructor takes the fields" -> "the generated
  `__init__(self, celsius: float)`"
- Bruce's hand: "clears the canvas" -> "calls `canvas.delete(\"all\")`"

**Home.** this file; the deep-review skill (teaching) if promoted.

### C32. An untaken design alternative is conditional, and its downstream exception is cut

**Test.** A sentence describes a design the listing on the page does
not take, in the indicative ("has no list of listeners", "can hold a
`Broadcaster`"), or follows a hypothetical failure past its first
consequence to the exception that then fires ("and `attach()` raises
an `AttributeError`"). Write "would" or "could", and end at the first
consequence.

**Keep when.** The exception is the point: the sentence exists to show
which error the reader sees.

**Sightings.** 3, one chapter (`30_Patterns--Observer`, 2026-10-11)
- Bruce's hand: "A `@dataclass` `Thermometer` has no list of listeners,
  and `subscribe()` raises an `AttributeError`" -> "A `@dataclass`
  `Thermometer` would have no list of responders"
- Bruce's hand: "can hold a `Broadcaster`" -> "could use composition"
- "If you remove that call, ..., and `attach()` raises" -> the second
  half cut

**Home.** this file.

### C33. A sentence that counts names the items

**Test.** A sentence says "one X and another", "of the two", or "three
things" and names the items only in a later sentence or not at all, so
the reader has to find them. Name them in the same sentence, or
introduce them with a colon.

**Keep when.** The count introduces the items in the same sentence, as
"gives up three things that ... keeps:" does.

**Sightings.** 2, one chapter (`30_Patterns--Observer`, 2026-10-11)
- Bruce: "vague". "*Observer* removes one coupling and keeps another."
  -> "*Observer* decouples the thermometer from its responders and
  leaves the responders coupled to the thermometer."
- "Of the two additions, only the telling moves out" -> the sentence
  names the two additions, the comparison and the announcement, and
  which one moves

**Home.** this file; a cousin of R9 (name the concrete thing).

### C34. Lay out a compressed consequence as steps (additive)

**Test.** A sentence carries a situation, what it would require, and
what follows, in one chain ("so one call to several responders could
produce several answers, or none"), or states an obligation as a lapse
("a caller can forget to make the call"). Write the situation, then
what it requires, then what follows until that is met.

**Keep when.** The consequence is one step, and the sentence states it.

**Sightings.** 3, one chapter (`30_Patterns--Observer`, 2026-10-11)
- Bruce's hand: "so one call to several responders could produce
  several answers, or none" -> three sentences: the situation, the
  rule a return value would require, and what returning `None` removes
- "a caller can forget to make the call" -> the obligation (the client
  must call `announce()`) and "Until it does, the responders hold
  stale data."
- Bruce's hand: the `fields()` paragraph laid out runtime first, then
  the checker's view

**Home.** this file; the deep-review skill (teaching) if promoted.

### C35. A concrete instance in parentheses beside an abstract noun (additive)

**Test.** An example sentence uses an abstract noun ("a widget", "its
event") with no concrete instance in the sentence. Add one in
parentheses: "a widget (like a button)".

**Keep when.** The noun is a term the chapter defines, so the reader
already has its instances.

**Sightings.** 1 (`30_Patterns--Observer`, 2026-10-11, Bruce's hand;
thin): "a widget keeps a list of handlers and calls each one when its
event arrives" -> "a widget (like a button) keeps a list of handlers
and calls each one when its event (a button press) arrives"

**Home.** this file.

### C36. Cut a trailing restatement of the clause's own contrast

**Test.** The sentence ends on "instead", "too", or an "as the X"
comparison, and deleting it leaves the meaning unchanged because an
earlier clause already carries the contrast: a closing "instead" after
an "If you swap" clause, a trailing analogy "as the `else` for the rows
above it" after "belongs last in its group". Kin to R32's trailing tag,
which gets its own clause; this one is a repeat and is cut.

**Keep when.** The tag carries the contrast on its own, with no earlier
clause stating it.

**Sightings.** 2, one chapter (`31_Patterns--State_Machines`,
2026-10-19)
- "If you swap the row order, the same input reports `UNAVAILABLE`
  instead." -> "If you swap the rule order, the same input reports
  `UNAVAILABLE`."
- "A row whose condition is `None` matches every time, so it belongs
  last in its group, as the `else` for the rows above it." -> "A rule
  whose condition is `None` matches every time, so it belongs last in
  its group."

**Home.** this file.

### C38. Name and link the rule a sentence applies (additive)

**Test.** A sentence states a consequence that holds only because of a
rule the chapter stated in an earlier section ("the first rule whose
condition passes wins"), and nothing in the sentence points at that
rule. Open with the rule's name, linked to the section that states it.

**Keep when.** The rule was stated in the paragraph just above.

**Sightings.** 1 (`31_Patterns--State_Machines`, 2026-10-19): "The
first row whose condition passes wins, whether or not a lower row
matters more." -> "By the engine's [ordering rule](#the-engine), the
first rule whose condition passes wins, whether or not a later rule
matters more."

**Home.** this file.

### C39. An effect names which way it cuts

**Test.** A sentence reports a change in what a tool or program does
("The `invalid-argument-type` report above disappears"), and a reader
cannot tell from the paragraph whether the change is wanted (Bruce: "is
this a good thing or not? unclear"). Say whether it is the gain or the
loss by naming the consequence. Kin to R36, where a capability describes
its use.

**Keep when.** The paragraph's next sentence states the consequence.

**Sightings.** 1 (`31_Patterns--State_Machines`, 2026-10-19, A Vending
Machine): "The `invalid-argument-type` report above disappears." ->
"The `Column`/`choose_row()` mismatch above then passes the checker. At
runtime `choose_row()` stores a `Column` in `self.row`, so the machine
carries on with a wrong selection."

**Home.** this file.

### C40. Give an elided noun its noun back

**Test.** A stand-in for a noun ("one", "others", "the third", "any of
them", "every callee") whose noun is in an earlier sentence, in a
sentence that makes a claim the reader must check against that noun.
Repeat the noun. Differs from R12, which fires only where a competitor
exists; here the stand-in is unambiguous but still makes the reader
reconstruct it.

**Keep when.** The noun is the subject of the sentence just before and
repeating it would be padding (R12's keep); "one" as a count ("one
Effect").

**Sightings.** 4, one chapter, Bruce's hand (approved as P4 on the
chapter 44 page, 2026-10-21)
- `44_Effects--Effect_Management` 2026-10-21 (the edit-start-44 pass, approved on the fault-review page):
  "One reading stops being enough as soon as the function calls others"
  -> "Reading a single function stops working when that function calls
  other functions"
- "A test installs one that returns a known name, and the same
  `greet()` runs" -> "A test installs a handler that returns a known
  name, so `greet()` produces the same result for each test run"
- "Knowing every one of them means reading every callee" -> "reading
  the code for every callee"
- "The third is an exception" -> "The third kind of Effect is an
  exception"

**Home.** this file.

### C41. A colon that names an item follows its noun directly

**Test.** "<noun phrase promising an item>, and <clause>: <item>". Move
the clause out to its own sentence; the colon now follows the noun.

**Keep when.** None seen yet.

**Sightings.** 1 (approved as P5 on the chapter 44 page, 2026-10-21)
- `44_Effects--Effect_Management` 2026-10-21 (the edit-start-44 pass, approved on the fault-review page):
  "Python tracks one Effect in function signatures, and enforces that
  tracking on every caller: `async`." -> "Python tracks one Effect in
  function signatures: `async`." with the enforcement as its own
  sentence after

**Home.** this file.

### C42. An "and" joining two clauses with different subjects, where neither explains the other, becomes two sentences

**Test.** A main-clause "and" whose two clauses have different subjects,
and the second is neither a consequence of the first (then it takes
"so") nor a parallel action by the same actor. `tools/sentence_shapes.py`
lists the wider shape under `ARGS=--survey` as `[AND]`, and its
calibration found the author's own rewrites fire it, so this is the
narrower case: the two clauses are about different things.

**Keep when.** Two actions by one actor ("reads the file and prints
it"); a consequence, which takes "so"; a deliberate pairing of two
parallel facts ("X is young, and Y is demanding").

**Sightings.** 2, one chapter (approved as P6 on the chapter 44 page,
2026-10-21)
- `44_Effects--Effect_Management` 2026-10-21 (the edit-start-44 pass, approved on the fault-review page):
  "Calling `greet()` builds a coroutine object, a description of work,
  and `ran` stays empty." -> "... a description of work. The body waits,
  so `ran` is still `[]`."
- "Effect tracking will look obvious in hindsight, and future
  programmers will regard ..." -> two sentences

**Home.** this file; the straighten skill if promoted.

### C43. When the prose explains one of a listing's parallel parts, name each of them (additive)

**Test.** The prose says what one member of a parallel pair in the
listing above does ("the `ask` handler says that `ask` means ...") and
the listing has a sibling of the same shape the prose never names.

**Keep when.** The siblings are identical in all but name and the
paragraph says so ("each of the three layers wraps its call the same
way").

**Sightings.** 1 (additive), Bruce's request "name the other handler as
well" (approved as P7 on the chapter 44 page, 2026-10-21)
- `44_Effects--Effect_Management` 2026-10-21 (the edit-start-44 pass, approved on the fault-review page):
  "In `main()`, the `with fun ask(prompt)` handler decides that `ask`
  means ..." -> "... says that `ask` means ..., and the `with fun
  tell(message)` handler says that `tell` means \"print the message.\""

**Home.** this file; the deep-review skill's teaching pass if promoted.

### C44. Before stating a loss, state what persists (additive)

**Test.** A main clause "X can no longer Y" or "X cannot Y" that closes
a comparison with an earlier design, where the earlier design's cost
(the bookkeeping, the parameter threading) is still paid under the new
one and the paragraph does not say so.

**Keep when.** The persisting cost is in the previous sentence; the
loss is the whole point and nothing persists.

**Sightings.** 1 (additive), Bruce's hand (approved as P8 on the chapter
44 page, 2026-10-21)
- `44_Effects--Effect_Management` 2026-10-21 (the edit-start-44 pass, approved on the fault-review page):
  "The type checker can no longer verify it." -> "You must still do the
  bookkeeping, but the type checker can no longer verify it."

**Home.** this file.

---

### C45. A suspended generator or coroutine has no "frame"; say what it preserves

**Test.** "Frame" (or "frames") stands for the saved state of a
suspended generator, coroutine, or task, or counts the generators in a
`yield from` chain. Readers take "frame" as a stack frame, which pops
when its function returns, and a suspended generator's state lives on
the generator object, off the call stack. Write what persists, "its
position in the body and its local variables", or name the generator
("the generator to which `both()` delegates", "every generator in the
chain", "three generators rather than two").

**Keep when.** "Frame" means a call's stack frame (a traceback, a
recursion depth, an `except` clause reading its own frame's locals), the
frame object an API returns (`f_locals`, `sys._getframe()`), or a panel
of a figure. This rule is a keep-when for C27: CPython's attribute is
`gi_frame`, and the API's word misleads here.

**Sightings.** 1, Bruce's ruling 2026-10-23 ("we need to consider a
different word than 'frame' because that suggests stack frame"), applied
in `ce27e8ec` and `4cd0d107` to sixteen sites in chapters 19, 44, 45 and
Solutions 45:
- `45_Effects--Generators`: "A suspended generator holds its frame: the
  position in the body and every local variable. ... The frame holds
  them, and the frame is the generator's state." -> "A suspended
  generator preserves two things: its position in the body and every
  local variable. The generator object stores both, so they outlive each
  `next()` or `send()` call that resumes the generator. ... The position
  and the locals together are the generator's state."
- `45_Effects--Generators`: "`drive()` receives a request that `ask()`
  yielded two frames down" -> "that `ask()` yielded inside
  `interview()`"; "`close()` unwinds every frame in the chain." ->
  "`close()` ends every generator in the chain."
- `44_Effects--Effect_Management`: "nothing can copy a generator's paused
  frame" -> "nothing can copy a paused generator's position and local
  variables"
- `19_Techniques--Concurrency`: "A suspended task is a paused frame that
  runs no bytecode" -> "A suspended task runs no bytecode" (the sentence
  before already says the task saves its position)

**Home.** this file only; the term is specific to generators and
coroutines.

---

### C46. State that survives a suspension or a call boundary is "preserved", not "held"

**Test.** "holds" (or "keeps") has state as its object, and the
sentence's point is that the state lasts across a gap: a suspension, a
return, a later call ("A suspended generator holds its frame"). Write
"preserves". "Holds" reads as containment at one moment and leaves the
lasting to inference.

**Keep when.** The sentence is about containment, not duration ("the
table holds classes", "a record holds its fields").

**Sightings.** 1, `45_Effects--Generators` 2026-10-23 (`ce27e8ec`),
Bruce chose the word ("or 'preserves'", over "retains") and confirmed it
("preserves says it better"):
- "A suspended generator holds its frame:" -> "A suspended generator
  preserves its frame:" (later "preserves two things:", see C45)

**Home.** this file only.

### C47. Close a pair word's phrase before the next clause starts

**Test.** A word that promises a pair ("between X", "both X", "either
X", "neither X") whose own phrase holds no "and"/"or"/"nor", followed
by that conjunction with no punctuation or verb between, and then a
noun phrase that is the next clause's subject. The reader takes the
noun phrase as the pair's second half and backs up at its verb:
"keeps state between values and the consumer has a loop of its own".
Repair by closing the phrase before the conjunction ("from one value
to the next while the consumer has"), by a comma plus "so"/"while"
that states the relation, or by repeating the pair word ("between
machines and between Python builds"). `tools/sentence_shapes.py`'s
`[PAIR]` rule finds the shape (`tip sentence-shapes`, in `tip prose`).

**Keep when.** A verb sits between the pair noun and the conjunction
("both forms keep the result and the name": "keep" has settled "both"
as a determiner), or a verb follows the conjunction at once ("leaves
both loops in one step and skips `else`"): the misreading never forms,
or ends within a word. A complete pair that happens to be a subject
("neither the class nor the instance holds") is the ordinary
construction.

**Sightings.** 1 marked by Bruce, `45_Effects--Generators` 2026-10-26
(`33d228b9`), was Claude-written ("kind of jumbles together"):
- "The problem appears whenever the producer keeps state between
  values and the consumer has a loop of its own." -> "The problem
  appears whenever the producer keeps state from one value to the next
  while the consumer has a loop of its own."

The same-day book sweep (`d957111a` and the `[PAIR]` commit) found
and fixed seven more, which count as the detector's sightings rather
than Bruce's: `47_Effects--Stateless_in_Practice` ("both appliances are
a `HeatSource` and ZIO must report" -> ", so ZIO must report"),
Solutions 04 ("for both strings and `int()` returns" -> ", while
`int()` returns"; "satisfies both conditions and the two blocks do" ->
"while the two blocks do"), Solutions 22 ("between machines and
Python builds" -> "between machines and between Python builds"),
Solutions 35 ("to both and leave `tile()` alone" -> "to `Symbol` and
`SPECS`, leaving `tile()` alone"), Solutions 45 ("under both drivers
and each returns" -> ", and each driver returns"), Solutions 47
("accepts both factories and `ty` passes" -> ", `ty` passes,").

**Home.** this file only | `tools/sentence_shapes.py` `[PAIR]`.

### C48. Don't name the listing in the sentence that introduces it

**Test.** A paragraph that ends directly above a listing names that
listing's file in a code span ("`color_count.py` walks a nested
dictionary of plants", "In `framework.py`, `run()` is the template
method"), and the listing's own path line repeats the name one or two
lines later. Drop the name and let the subject be the thing the
sentence describes: the function ("`run()` is the template method"),
"This example", "the solution", "one module". A rule of the R7 family:
R7 cuts the sentence that only points, R31 points with "Here,", and
this one cuts the name from a sentence that otherwise stays.

**Keep when.** The name is the claim: the file does not exist yet
("At this point `palindrome.py` does not exist"), the name is a
convention ("A directory has at most one `conftest.py`"), the sentence
names the chapter's file and the listing below is a changed copy
("The chapter's `research.py` and the doubles ... appear here",
"`registry_demo.py` imports `Shape` ... The unchanged demo therefore
prints `[]`"), the name matches a harness entry (`norun.txt`), or the
module name is what later listings import from ("`steps.py` gathers
the three steps the rest of the chapter chains").

**Sightings.** 1 marked by Bruce, `45_Effects--Generators` 2026-10-27
(`1ce4fce1`), was Claude-written ("gives the name before the listing
of the same name"):
- "`color_count.py` walks a nested dictionary of plants, yields the
  path to each plant, and returns a count of each color:" -> "This
  example walks a nested dictionary of plants, ..." (Bruce's wording;
  my first pass wrote "This one")

The same-day sweep read the 19 paragraphs of that shape in both trees
and changed 13 in ten files, keeping the six listed above: chapters
07, 18, 19, 22 (two), 24 (three), 42, 44, Solutions 15, 18, and 38
(two). The sweep's edits count as the detector's sightings, not
Bruce's.

**Home.** this file only.

---

### C49. "Can" where the sentence reports what happens is the plain present

**Test.** A modal "can" on a verb whose subject is a thing, in a
sentence that reports what that thing does in the case on the page:
the test the next sentence shows catching the failure, the handler the
run shows reaching the state. The reader takes "can" as possibility, so
the modal hedges a fact. Write the plain present: "A test can catch the
broken contract" is "A test catches the broken contract". Ask: is the
sentence about whether the thing is able to, or about what it does
here? The style guide's "can" bullet keeps "can" for a standing
capability, and this candidate is its other half.

**Keep when.** The capability is the claim ("a `set` can hold any
hashable object", "`survey()` can delegate to either"); the subject is
a person and the "can" is a choice or a permission ("you can skim");
a condition sits on the page ("if you remove the guard, a subclass can
take the slots back"); the modal is negated ("cannot").

**Sightings.** 1, Bruce 2026-10-30 on `20_Patterns--Rethinking_Objects`:
"A test can catch the broken contract." (my rewrite of "No tool catches
the broken contract, but a test can.") -> "A test catches the broken
contract." Bruce: "note that this could be 'catches' rather than 'can
catch'. What kind of rule can you create to discover and fix things like
this." `[CAN]` in `tip sentence-shapes ARGS=--survey` lists the
candidates since that day (`can_event()` in `tools/sentence_shapes.py`):
a main-clause "can" on a lexical verb, a thing as subject, no negation,
no "also"/"still"/"even"/"always", and no condition or option word in
the sentence. The book has about 800 prose lines with "can"; the rule
is a survey because the parse cannot tell a capability stated as a fact
from a hedged event.
- Book sweep 2026-10-30, the same day: 23 Opus agents read the 298
  `[CAN]` hits (one to three chapters each, with their Solutions files)
  and rewrote 21, keeping 277. The rewrites all had the chapter 20
  shape, a generic or definite subject followed by the listing that
  shows the event: "A test can check the model with no window" ->
  "checks" (38, `test_robot.py` below it), "A decorator can capture
  that pattern" -> "captures" (42, `@safe` follows), "a test can bind
  to `Recorder`" -> "binds" (46, `test_greeter.py` follows), "`yield
  from` can take over that job:" -> "takes over" (45, lead-in to
  `yield_from_nested.py`), "so the listing can print `f.closed`" ->
  "prints" (04). The keeps, by the agents' labels: a hazard or race
  ("can fail", "can each run the constructor"), what a construct
  permits in general ("a comprehension can use `:=`"), one option
  among several ("A `__getattr__()` proxy can annotate it `Service`"),
  a contrast with an inability ("can build the registry, but it stops
  at direct subclasses"), a purpose clause ("so the listing can show
  the runtime failure"), and an exercise or hint. The agents'
  closest calls were sentences true of the listing but phrased as the
  reason the design works ("Because the machine is deterministic, a
  test can drive it"); they kept those. Bruce read every close call
  in `build/can-2026-10-30/LEFTOVERS.md` the same day and kept them
  all, so a "can" that gives the reason a design works, with the
  listing as its evidence, is a keep, as is a "can" paired with a
  "cannot" or set against a sibling option. Yield 7%, so the shape
  is rare in this book; the rule stays a survey for new drafts.
- Reread 2026-11-09, before the hits were recorded as judged in the
  survey baseline: two Opus agents read the 278 hits then standing
  (259 of them sentences the first sweep had read, 19 written since)
  and rewrote none; the session read the 19 new ones and a
  one-in-eight sample of the rest. A lead-in keeps its "can" when its
  subject is generic ("A generator can wrap an iterator and check
  each item, in fewer lines:", where the plain present would say that
  every generator does) or when it sets one design beside a sibling
  ("`slope()` can catch `ZeroDivisionError` ... instead of
  introducing a new type:"). The first sweep's rewrites had a
  specific subject and no sibling ("`yield from` can take over that
  job:").

**Home.** CLAUDE.md (global, the "can"/"could" bullet);
`tools/sentence_shapes.py` (`[CAN]`, with its read keeps in
`tools/data/sentence_shapes_survey_baseline.txt` since 2026-11-09);
the `activate` skill's Accrued patterns; this file.

### C50. A part noun names its owner when a second owner is on the page

**Test.** "the body", "the loop", "the call", "the result" stands for a
part of one thing while a second thing with the same kind of part is in
the paragraph: a driver function beside a generator, an ordinary
function beside a generator function, two generators. Name the owner:
"the generator body", "`watch()`'s body", "`luring()`'s body", "the
innermost body". The pointer cousin is R12. A heading has no previous
sentence to supply the owner, so there the owner itself stands in for
the part: "An Exception Raised in the Generator", not "in the Body".

**Keep when.** The previous sentence names the owner and nothing else
with a body is on the page; "its body" with one candidate; "the body of
its loop".

**Sightings.** 1 (nine sites in one chapter), `45_Effects--Generators`
2026-11-01 and 2026-11-04, Bruce: "which body?", "look through the
chapter to find places where 'generator body' would be more
illuminating", and on a heading, "'Body' is vague":
- heading (2026-11-04, `f55d274f`): "### An Exception Raised in the
  Body" -> "### An Exception Raised in the Generator"
- "In both `[1]` and `[2]`, the body ends at the `yield`" -> "the
  generator body ends at the `yield`"
- "It starts the body with `next()`" (a paragraph opening "A driver
  function runs the generator") -> "It starts the generator body with
  `next()`"
- "`next()` runs the body after `watched = watch()` has bound the name"
  (after a sentence about functions in general) -> "`next()` runs
  `watch()`'s body after ..."
- "The exception belongs at the point where the body stopped" (two
  generators paused) -> "where the innermost body stopped"

**Home.** antecedents | this file.

### C51. A statement whose output shows only that execution continued is replaced by one that shows the effect (listing)

**Test.** A listing ends a demonstration with a `print()` of a constant
("closed", "done", "after") whose only information is that the program
reached that line. Replace it with a read of the state the operation
changed (`inspect.getgeneratorstate(g)`), a `finally` that prints when
it runs, or the operation's return value, so the output shows what the
operation did.

**Keep when.** Reaching the line is the claim: a listing showing that a
call returns at all, or that an exception was caught before this point,
and the prose says so.

**Sightings.** 1, `45_Effects--Generators` 2026-11-01, Bruce: "this seems
meaningless. Is there some better way to demonstrate close()?":
- `g.close()` / `print("closed")` / `#: closed` -> `g.close()` /
  `print(inspect.getgeneratorstate(g))` / `#: GEN_CLOSED`, and a
  `finally: print("finished")` in the generator so both runs show the
  exception passing through the body.

**Home.** listing-design (a seventh question) | this file.

### C52. Parallel runs in one listing start with the same statements (listing)

**Test.** A listing shows two or more runs that differ in one operation,
and the statements before that operation differ in a second way
(`print(next(g))` in one run, bare `next(g)` in the other), so the
output differs for a reason the listing is not about. Write the shared
part identically, dropping the output the point does not need.

**Keep when.** The difference in the setup is part of the point and the
prose names it.

**Sightings.** 1, `45_Effects--Generators` 2026-11-01, Bruce: "why does
this output two lines ... And the same thing later only one":
- run 1 `print(next(g))` with `#: started` `#: paused`, run 2 `next(g)`
  with `#: started` -> both runs `next(g)` with `#: started`; the
  yielded string then went unused and became a bare `yield` with
  `Generator[None]`.

**Home.** listing-design | this file.

### C53. The colon that introduces a listing sits on the sentence that says what the listing shows

**Test.** Two sentences lead into a listing, and the colon is on the
first, which states a claim, while the second describes the mechanism
the listing demonstrates. Give the claim a period and end the mechanism
sentence with the colon, so the colon points at what follows it. A
cousin of R21 (a colon joining a claim to its explanation) and R31
(pointing at the adjacent listing).

**Keep when.** One sentence leads in.

**Sightings.** 1, `45_Effects--Generators` 2026-11-01, Bruce: "This should
be two sentences, with the colon at the end of the last one":
- "An exception can travel the opposite direction too, from the
  generator into the driver: a `raise` in the generator body leaves the
  generator through whichever call resumed it." -> "An exception can
  travel the opposite direction too, from the generator into the
  driver. A `raise` in the generator body leaves the generator through
  the call that resumed it:"

**Home.** this file only.

### C54. A trailing "instead" goes where the sentence already names the alternative

**Test.** The sentence ends on "instead" (not "instead of"). Delete the
word and reread with the sentence before it. If the reader still knows
this option replaces the earlier one, the word was repeating what the
structure says. The usual carriers: a condition parallel to the previous
sentence's ("When the driver has the answer, it calls `send()`. When the
driver has a failure, it calls `throw()`"), an "In `a.py` ... In `b.py`"
pair, a "not" or "rather than" in reach, a listing after the colon that
shows the replacement, a verb that means replacement ("skip", "shadow",
"discards" against "raises").

**Keep when.** "instead" is the only word saying a substitution
happened, so that without it the new thing reads as an addition:
"`@dataclass` sets `__hash__` to `None` instead" (a reader would
otherwise think it also inherits the default), "so a named constant in a
`case` silently captures instead". A sentence-opening "Instead," that
joins two paragraphs whose contrast is otherwise unmarked. An exercise
statement. When deletion leaves the sentence ambiguous, name the
contrast: "If a `StopIteration` propagates out of the body instead" ->
"If the body raises a `StopIteration` of its own".

**Sightings.** 1 flag, then a book sweep the same day (2026-11-01,
Bruce: "is this necessary? Sweep the book for similar usages"): 104
bare "instead" sites read, 39 deleted, 1 rewritten, about 35 kept, 28
exercise statements left. Keeps were the majority outside the
parallel-condition shape.
- `45_Effects--Generators` 2026-11-01, was Claude-written (same day):
  "When the driver has a failure instead, it calls `throw()` with the
  exception" -> "When the driver has a failure, it calls `throw()` with
  the exception"
- `45_Effects--Generators`: "In `yield_from_nested.py`, a `yield from`
  in `survey()` receives that `Result` instead:" -> "... receives that
  `Result`:"
- `22_Patterns--Iterators`: "so the list habit `odd_squares[:5]` raises
  a `TypeError` instead." -> "raises a `TypeError`." ("defines no
  `__getitem__()`" carries the contrast)
- `19_Techniques--Concurrency`: "but not to the OS. Instead, control
  goes to the *event loop*" -> "Control goes to the *event loop*"

**Home.** CLAUDE.md (a bullet before "Prefer the positive statement",
2026-11-01) | this file. Not a watch word: a bare scan would list 400
"instead of"s, and the shape is a per-sentence judgment.

### C55. "same" with nothing to compare against is a pointer; write the pointer

**Test.** The sentence has "the same X" (or "this same X"). Ask what
second thing "same" compares X with. If there is none, because X has one
referent on the page and the sentence makes no identity claim, "same"
is standing in for "the", "that", or "its" and saying "the one I just
mentioned". Write that pointer, or the noun's owner: "At `[2]`, the
same `yield` raises `GeneratorExit`" -> "its `yield`" (one `yield` in
`pause()`); "The same directory reaches pytest" -> "That directory";
"uses this same self-registration" -> "uses this self-registration".

**Keep when.** "same" carries a claim, which is most of the time:
identity against a possible copy or second instance ("returns the same
`cls` it received", "reads the same list"), a comparison whose second
term is implied but real ("for the same reason `bump()` does", "the
same figure the CPU-bound version produces", "The same approach isolates
a database"), an unchanged input against a changed output ("the same
command reports:", "The same call works from outside the class"), a
relation between two things in the sentence ("a package of the same
name", "in the same file"), the idioms ("the same way", "stays the
same", "at the same time"), a quotation, an exercise statement.

**Sightings.** 1 flag, then a book sweep the same day (2026-11-01,
Bruce: "I think 'same' is redundant here. I'm pointing this out because
I'd like you to learn from it and apply that learning throughout the
book."). Of about 1339 "same" lines, 194 had no comparison word or
idiom in the sentence; four Opus agents and the session read those 194
and changed 6, keeping 183 and leaving 5 exercise or quote sites. The
fault is rare and specific; the sweep's filter (no "as", "that",
"than", "both", "each", "two", "and" in the sentence) is in the
session's `same_survey2.py` and is the shape a survey rule would use.
- `45_Effects--Generators` 2026-11-01, was Claude-written (same day):
  "At `[2]`, the same `yield` raises `GeneratorExit`." -> "At `[2]`,
  its `yield` raises `GeneratorExit`."
- `26_Patterns--Factory`: "[Pattern Refactoring] uses this same
  self-registration." -> "uses this self-registration."
- `14_Techniques--Decorators`: "The same `__get__()` makes them work on
  methods" -> "That `__get__()` makes them work on methods"
- `17_Techniques--Metaprogramming`: "The same directory reaches pytest
  through `pythonpath`" -> "That directory reaches pytest ..."
- `Solutions/43_Functional--Confidence`: "The same `[]`-returning
  function passes it too." -> "The `[]`-returning function passes it
  too." ("too" compares)
- `45_Effects--Generators` 2026-11-09, Bruce on "the same
  `RuntimeError`, `generator ignored GeneratorExit`": "same as what".
  A second shape: the comparand exists (the run of `stubborn()` in the
  listing above) but the sentence leaves it unnamed, and an appositive
  after the noun reads as the second term. Repair: name the comparand.
  "`close()` raises the same `RuntimeError`, `generator ignored
  GeneratorExit`." -> "`close()` raises a `RuntimeError` with the
  message shown for `stubborn()`, `generator ignored GeneratorExit`."

**Home.** CLAUDE.md (a bullet before "Prefer the positive statement",
2026-11-01) | `[SAME]` survey rule in `tools/sentence_shapes.py` (same
day) | antecedents (a pointer word in disguise) | this file.

### C56. Read every "whatever" with suspicion

**Test.** The sentence has "whatever". Two shapes. The concessive
("whatever the driver's reason", "whatever its base classes") claims
the outcome holds across every case of something, which is either a
universal the sentence has not earned (the overclaim shape, test it as
`tip overclaims` would) or a set the sentence need not mention at all,
in which case cut the phrase. The free relative ("whatever the caller
supplies", "whatever holds `self.close`") is R54's shape with a thing
instead of a choice: write the definite noun phrase ("the value the
caller supplies", "the object that holds `self.close`"), or name the
set when the independence is the claim ("any object with that shape").
`tip watch-words` lists the word as Tier 2 (2026-11-04).

**Keep when.** None seen yet. The chapter 45 pass the same day read
its seven sites and rewrote all seven: the free relatives became "the
code that calls `next()`", "the value the generator returned", "the
code that resumed it", "every resource its body opened" (a list of
them follows); the concessives became "no matter what answers it
receives", "from either driver" (the two options named), "when the
questions arrive in any order". The other 59 sites stay NEW for their
chapters' passes.

**Sightings.** 1, `45_Effects--Generators` 2026-11-04, was
Claude-written (same day), Bruce's own edit, "the use of 'whatever'
should be considered circumspect in general":
- "so the exception carries one meaning, finish, whatever the driver's
  reason." -> "so the exception carries one meaning, finish."

**Home.** CLAUDE.md watch list (Tier 2, "whatever") | this file.

### C57. A present perfect in a time clause is the simple present

**Test.** "has" or "have" plus a participle inside a clause opened by
"before", "after", "when", "once", "until", or "whenever": "before the
generator has yielded its last value", "when every generator beneath it
has finished", "after `watched = watch()` has bound the name". The
subordinator already orders the two events, and present narration keeps
one tense, so write "yields", "finishes", "binds". `tip past-tense
ARGS=--survey` lists the shape as `[PERFECT]` (`tools/past_tense.py`,
2026-11-04); the book had 41 sites that day. The activate skill's tense
category has the pattern.

**Keep when.** The perfect carries a completed state the present loses
("reads `counter` after the previous lock holder has written it", where
the completed write is the point). A perfect outside a time clause ("the
answers it has received", "has entered no `try` statement") is judged by
the standing-behavior test instead.

**Sightings.** 1, `45_Effects--Generators` 2026-11-04, was
Claude-written, Bruce: "'has yielded' can just be 'yields'. I thought we
had captured this kind of thing somewhere in super-prose":
- "before the generator has yielded its last value" -> "before the
  generator yields its last value"
- same pass: "when every generator beneath it has finished" -> "when
  every generator beneath it finishes"; "after `watched = watch()` has
  bound the name" -> "after `watched = watch()` binds the name"; and
  outside a time clause, "A generator that returns from a `case` has
  moved to a new state" -> "moves to a new state"

**Home.** activate (Accrued patterns) | `tools/past_tense.py`
`[PERFECT]` | this file.

### C58. A state verb says where the thing stopped or what it waits for

**Test.** A clause whose verb names a state of rest ("is waiting",
"waits", "is pending", "is idle", "sits", "is suspended", "is paused")
and ends on that verb: "to the generator that is waiting", "the `yield`
that is waiting". The verb reports that the thing does nothing and stops
before the one fact the reader can picture, which is where it stopped or
which event resumes it. Ask "waiting where, or for what?" and write the
answer, with the state verb the chapter taught: "the generator paused at
the innermost `yield`", "the `yield` where the inner generator waits",
"waits for the third answer". Bruce reads the bare form as passive: the
clause is active in grammar and has no action in it. No tool lists the
shape: `tip passive` needs a passive auxiliary, and the activate skill's
relative-clause and progressive rules both exempt a clause with a real
actor in a state that is mid-flight.

**Keep when.** The place or the awaited event follows the verb ("waits
at a `yield`", "is waiting to receive a value", "waits while the driver
carries out the request"), or the previous sentence supplies it and an
additive links to it ("Both tasks wait forever ... the one task that can
wake each of them is waiting too").

**Sightings.** 1, `45_Effects--Generators` 2026-11-11, was
Claude-written (88d89eff), Bruce: "passive":
- "A `yield from` forwards `throw()` and `close()` to the generator
  that is waiting:" -> "to the generator paused at the innermost
  `yield`:"
- same pass, found by grep: "passes back down to the `yield` that is
  waiting" -> "passes back down to the `yield` where the inner generator
  waits"
- `45_Effects--Generators` 2026-11-12, was Claude-written, Bruce:
  "unclear": "The listing's second run shows a state that stays.
  `waiting()` matches `Mouse.APPEARS` alone, so `Mouse.ESCAPES` leaves
  the machine in `Waiting`, and the entry message prints once." ->
  "At `[5]`, `run_all()` sends `Mouse.ESCAPES` to a machine in
  `Waiting`. `waiting()`'s one `case` matches `Mouse.APPEARS`, so its
  loop yields `Waiting` again, and the trace line ends `-> Waiting`.
  The entry message prints once."
  "Stays" is a verb of rest with no place after it, and it has the
  wrong subject as well: the machine stays in a state, and a state
  does not stay. The sentence was a topic sentence in the form "X
  shows Y", which names a verdict about the run and leaves out what
  the run sends and what it prints. Three additions to the test from
  this sighting: (1) `stays`, `remains`, and `holds` join the verbs of
  rest; (2) ask "who rests?" as well as "where?", and give the verb
  to the thing that rests; (3) a walkthrough sentence of the form
  "the run shows a NOUN that VERBs" is replaced by the call, its
  input, and the output line, with a tag on the call when the listing
  has more than one.
  Why the passes missed it: the grep list for this candidate had six
  verbs and "stays" was outside it; the literal pass reads "shows" as
  a plain verb, and its vague-description test looks for an abstract
  noun or a pointer phrase, where "a state that stays" is concrete
  words in a relation the listing does not have; `tip positional` was
  quiet for "The listing's second run".

**Home.** activate (Accrued patterns) | super-prose (pass 7) | this
file.

### C59. A relative clause's verb does not sit beside "and" and the main clause's next verb

**Test.** A relative or complement clause with its own noun or code-span
subject ends on its verb, and a conjunction and a second verb follow at
once: "holds the generator `outer()` returned and calls `throw()` on
it". The reader joins the two verbs under the clause's subject
("`outer()` returned and calls") and backs up when the object makes that
impossible. A dropped "that" and a code-span subject make it worse,
since nothing marks where the clause starts. Give the second verb its
own sentence, move the relative clause to the end of its sentence
("declares the keys and describes the `dict` that `json.loads()`
returns"), or replace the clause with a shorter name for the thing ("the
class body's fields", "`g`"). `tip sentence-shapes ARGS=--survey` lists
the shape as `[REL+AND]` (`tools/sentence_shapes.py`, 2026-11-11); the
book had 19 hits that day.

**Keep when.** Both verbs belong to the clause's subject ("one value
that every instance reads and writes", "the Effects the function
performs and leaves out of its declared row", "whether the read succeeds
or raises an exception"). A pronoun subject that is the main subject
again ("the keys it specifies and ignores the rest") and a second verb
whose number disagrees with the clause's subject read once, and the
survey skips them.

**Sightings.** 1, `45_Effects--Generators` 2026-11-11, was
Claude-written (88d89eff), Bruce: "jumbled":
- "The driver holds the generator `outer()` returned and calls `throw()`
  on it, but `inner()` prints the `caught` line." -> "`g` is `outer()`'s
  generator. The driver calls `g.throw()`, but `inner()` prints the
  `caught` line."
  Bruce deleted "`g` is `outer()`'s generator." the next day: the
  listing's `g = outer()` says it, so the added sentence broke R47. The
  repair is the name alone, "The driver calls `g.throw()`".
- same day, from the survey: "The body reads the value that `send()`
  delivered and chooses what to do next" -> "From the value that
  `send()` delivered, the body chooses what to do next"; nine more in
  chapters 08, 43, 44 and Solutions 12, 14, 28, 29, 45

**Home.** ambiguity (coordination entry, Accrued shapes) |
`tools/sentence_shapes.py` `[REL+AND]` | this file.

### C60. A verb that reads with or without an object keeps its object beside it

**Test.** A verb that makes a complete statement with no object (stops,
starts, ends, runs, closes, opens, resumes, returns, finishes, moves,
changes, fails) sits directly before "and", "or", or "then" and a second
verb, and the object both verbs share comes after the second verb: "A
driver that holds the outermost generator stops and cleans up every
generator beneath it". Cover the sentence from the conjunction on and
read what is left. If it is a complete sentence ("A driver ... stops"),
the reader has already taken it as the claim, and the shared object
arrives too late to turn the verb around. The chapter 45 sentence has
three more faults that the same repair removes. Its relative clause puts
a noun directly before the verb, so "the outermost generator stops"
reads as a clause too. "Beneath it" has the driver and the generator as
candidates. The actor, the `close()` call, sits in a trailing "with one
call". Repair: give the first verb its object at once, and make the
thing that acts the subject ("One `close()` call on the outermost
generator stops that generator and every generator beneath it"). The
second verb then gets its own clause with its own subject ("and each one
runs its cleanup").

**Keep when.** The first verb is meant with no object ("the script runs
and prints the same output", "the first task finishes and releases both
locks"). The two verbs are a set pair with the object directly after
the second ("opens and closes a file", "loads and saves itself", "close
or swallow that second splice"), where the covered reading ("the class
opens") is no claim the passage could make.

**Sightings.** 1, `45_Effects--Generators` 2026-11-12, was
Claude-written, Bruce: "it sounds like the driver stops":
- "A driver that holds the outermost generator stops and cleans up every
  generator beneath it with one call." -> "One `close()` call on the
  outermost generator stops that generator and every generator beneath
  it, and each one runs its cleanup."
- same day, a grep of both trees for these verbs before a conjunction
  and a second verb: about 55 lines, this the one site. The rest are the
  first verb with no object, and three set pairs.

**Home.** ambiguity (coordination entry, Accrued shapes) | super-prose
(pass 6 and its grep) | this file.

### C61. "Nothing" and "nobody" do not act: say who acts and what they do

**Test.** `Nothing`, `nobody`, or `no one` as the subject of a verb:
"Nothing calls `throw()` on the first booking". The sentence gives the
action an actor, and the actor does not exist, so the reader looks for
the thing that is calling and then cancels the call. It is the
cancelled-object shape ("receives no `throw()`") with the cancellation
moved to the subject, and a rewrite of one into the other fixes
nothing. Ask what does run, and write that with its real actor:
"`list(book())` drives the steps with `next()`." A second
negative in the same sentence ("and no `except` clause runs") gets the
same question: "Each `yield from` finishes normally, and every step
runs to its end." `tip watch-words` lists the shape as Tier 2 since
2026-11-12 (`NOBODY_SUBJECT` in `tools/watch_words.py`); the book had
26 sites that day.

**Keep when.** The absence is the claim and no actor could be written
("a class in a module nobody imports stays out of the registry"), or
the words are a heading's title in link text ("Nothing Runs Yet").

**Sightings.** 1, `45_Effects--Generators` 2026-11-12, Claude-written
the same day, Bruce: "what is this 'Nothing' that is calling throw()? I
feel like this issue keeps arising, the confusing negativity":
- "Nothing calls `throw()` on the first booking, so `list()` runs it to
  its end and no `except` clause runs." -> "`list(book())` drives the
  steps with `next()` alone. Each `yield from` finishes normally, and
  every step runs to its end." Bruce cut "alone" the same day (C62).
- Book read 2026-11-12, the 25 other sites `NOBODY_SUBJECT` listed: 17
  rewritten ("Nothing objects: not the annotation, not the type
  checker, not the running program." -> "The annotation, the type
  checker, and the running program all accept it."; "a coroutine that
  nothing awaits" -> "an unawaited coroutine"; "Nobody audits their
  imports" -> "Programmers stopped auditing their imports"), 8 kept:
  four link texts, and four where the absence is the claim ("If
  nothing touches the lazily imported name", "a module nobody
  imports", "a type nobody else provides", "Nothing absorbs the
  change" as the answer to an exercise that asks which part did).
- The sentence's earlier form, also Claude's, was the object shape:
  "The second booking receives no `throw()`, so ... no `except` clause
  runs." Both were written while adding to a listing, outside any prose
  pass, which is where the shape keeps coming back. A sentence written
  during a listing change gets the positive test before it is saved.

**Home.** positive (Accrued patterns) | super-prose (pass 2) |
`tools/watch_words.py` `NOBODY_SUBJECT` | this file.

### C62. A limiter on a positive sentence puts the negation back

**Test.** A positive statement ends on "alone", or carries "only",
"just", or "nothing but": "`list(book())` drives the steps with
`next()` alone." The limiter says an alternative is excluded, so the
reader looks for it, as with the negative the sentence replaced. Ask
whether the passage has named the alternative yet. If it has not, or
the next sentence names it ("To report the card's failure in the second
booking, the driver calls `throw()`"), cut the limiter: the plain
statement is true, and the contrast arrives where the passage makes it.

**Keep when.** The exclusion is the claim and the alternative is on the
page ("the first `send()` accepts only `None`", "A task's limit is heap
memory alone, because a task uses neither of the per-thread OS
resources").

**Sightings.** 1, `45_Effects--Generators` 2026-11-12, Claude-written
as the C61 repair, Bruce: "We can leave off the 'alone'":
- "`list(book())` drives the steps with `next()` alone." -> "`list(book())`
  drives the steps with `next()`."
- same chapter and day, Claude-written an hour later in the
  `saga_generators.py` walkthrough, Bruce: "Is 'only' necessary or
  useful here? Seems similar to the overuse of 'alone'": "`book()`
  creates every `undo` generator, and an `undo` body starts only at
  `[1]`." -> "... starts at `[1]`." The next sentence ("The successful
  run finishes without reaching `[1]`") already carried the contrast.
  The deletion test, added that day: read the sentence without the
  limiter, and keep the word only where the reader would otherwise
  assume the excluded case.

**Home.** positive (Accrued patterns) | super-prose (pass 2) | this
file.

### C63. A past in a relative clause of a standing-behavior sentence is the present

**Test.** A simple past inside a relative clause ("the value that
`send()` delivered", "the answer it received", "the requests `outer()`
gave it") in a sentence whose main verb is present and states what the
machinery does on every run. Write the clause in the present and read
the sentence. If the order of the two events still reads right, because
a preposition or the main verb carries it ("From the value ... the body
chooses what to do next", "answers the requests ... gives it") or
because the two are one event, keep the present: once a sentence states
the rule, every verb in it states the rule. `tip past-tense CH=NN
ARGS=--survey` lists the shape under `[PAST-SUB]`, mixed with the
keeps.

**Keep when.** The past is the only word that orders the events, so the
present moves the clause to another time or another thing ("resumes
where it stopped": "where it stops" is the next stop). The clause
points at one run the reader watched ("the `Failed` the driver threw at
`[2]`"). The act was finished by someone else before the sentence's
scene ("hundreds it didn't write").

**Sightings.** 1, `45_Effects--Generators` 2026-11-12, was
Claude-written, Bruce: "this can be 'delivers'":
- "From the value that `send()` delivered, the body chooses what to do
  next" -> "From the value that `send()` delivers, the body chooses
  what to do next"
- Why the passes missed it, read that day. The survey listed the
  sentence (`[PAST-SUB] delivered`), one of 39 such lines for the
  chapter, printed on every run with no judged list. Three texts told
  the reader to keep all of them: `tools/past_tense.py` and `CLAUDE.md`
  called a subordinate past "an anterior reference inside present
  narration, not the drift", the activate skill's tense category
  allowed a backshift for "an act finished before now", which every
  relative-clause past satisfies, and super-prose named `[PAST-SUB]`
  with no test and no example beside `[PERFECT]`'s. C57 covered the
  present perfect in a time clause and sent a perfect in a relative
  clause to the standing-behavior test, and no line did the same for
  the simple past.

**Home.** activate (tense category and Accrued patterns) | super-prose
(pass 7 and Before the read) | this file.

### C64. Link text holds the name of the thing the target teaches

**Test.** A link to a section that teaches a named construct ("bare
`raise`", "`yield from`", a pattern), where the construct's name sits
in the sentence just outside the brackets and the link text is the
predicate alone: "The bare `raise` then [re-raises the exception the
clause caught](...#errors-and-exceptions)". A reader who looks at the
link text sees a verb phrase and cannot tell what the target is about.
Move the opening bracket so the link text starts on the name: "The
[bare `raise` re-raises the exception the clause caught](...)".

**Keep when.** The target teaches the claim and not the construct (the
sentence's subject is this chapter's own object, "`step()` [re-raises
what it caught](...)"), or the name is the whole link text already.

**Sightings.** 1, `45_Effects--Generators` 2026-11-12, was
Claude-written (2a6ffd5a), Bruce's edit in the working tree:
- "The bare `raise` then [re-raises the exception the clause
  caught](04_Foundations--Control_Flow.md#errors-and-exceptions)" ->
  "The [bare `raise` re-raises the exception the clause caught](...)"
- Why the passes missed it: no pass reads where a link's brackets sit.
  `heading_links.py` checks the anchor, `tip link-support` asks whether
  the section covers the sentence's claim, and both pass with the name
  outside the brackets. No tool lists the shape.

**Home.** super-prose (pass 5) | this file.

### C65. "then" goes where the sentence order already gives the order

**Test.** A "then" between subject and verb in a walkthrough that
narrates events in the order they happen ("Each `except` clause prints
its step's undo line. The bare `raise` then re-raises the exception"),
most of all when a sentence nearby already carries one ("The exception
then propagates up through the `yield from`", two sentences above).
Read the sentence without it. If the order still reads right, cut it:
the word marks every step as a step, and the reader gets no news from
it.

**Keep when.** The order is the claim, or the sentence breaks from the
order of the page: a step the reader would place elsewhere ("the
`finally` clause then runs, before the exception reaches the caller"),
a consequence after a condition ("If ..., then ..."), or the first
"then" after a pause in the action (the exception arrives, and then
propagates).

**Sightings.** 1, `45_Effects--Generators` 2026-11-12, was
Claude-written (2a6ffd5a), Bruce's edit in the working tree, same
sentence as C64:
- "The bare `raise` then re-raises the exception the clause caught" ->
  "The bare `raise` re-raises the exception the clause caught"
- Why the passes missed it: "then" is in no watch list, and the
  stutter scan reads a window of three tokens inside one sentence, so
  two "then"s two sentences apart print nothing. The cohesion skill
  tests a connective for a real relation, and sequence is a real
  relation here, so the word passed.

**Home.** super-prose (pass 4) | this file.

### C66. "X with no Y" for a thing nothing handles: say the positive case, then "any other"

**Test.** A noun defined by "with no" and a construct that sits
elsewhere in the listing and would match, handle, or receive it: "An
input with no `case`", "a request with no handler", "a key with no
entry". The phrase gives the thing a possession it lacks, when the
fact is a relation: no `case` in the `match` matches this input. The
reader must find the `match`, list its cases, and take the complement.
State the positive case first, with the construct as written in the
listing, then name the rest as "any other": "An input that matches a
`case` returns the next state, which ends the loop. After any other
input, the loop runs its `yield` again." If the sentence then reports
a behavior ("the machine stays in that state"), the construct that
produces the behavior is the subject of a sentence of its own, named as
the listing writes it ("Each state's `while True` loop keeps the
machine in that state"), and not the object of "leaves ... running"
(R61's demoted actor, with a participle where R61 has an infinitive).

**Keep when.** The absence is a property of the thing itself, seen at
the thing: "a function with no parameters", "`f()` with no arguments",
"a field with no default", "a class with no `__slots__`".

**Sightings.** 1, `45_Effects--Generators` 2026-11-12, was
Claude-written, Bruce: "'with no case' is negative and confusing. Also
we should mention that the 'while True' is what keeps it in that
state":
- "An input with no `case` leaves the state's `while` loop running, so
  the machine stays in that state." -> "Each state's `while True` loop
  keeps the machine in that state. An input that matches a `case`
  returns the next state, which ends the loop. After any other input,
  the loop runs its `yield` again and reports the state's name."
- Why the passes missed it: `tip watch-words` lists a `no` after a
  `NO_VERBS` verb or as a subject, and skips a `no` after a preposition
  by design, since most "with no" phrases are the keep above (231 sites
  in the book, nearly all "with no arguments" and its kin). `CLAUDE.md`
  records the same gap from 2026-10-28 ("with no exception" slipped past
  the scan and was fixed by hand). `tip negatives` counts the word per
  paragraph and this paragraph held one. `[CAUS]` reads an infinitive
  after its verb list, and "leaves" with a participle is outside it.

**Home.** positive (Accrued patterns) | super-prose (pass 2) | this
file.

### C67. One role, one name: a second role noun for the same thing reads as a second thing

**Test.** Two sentences close together give one function or object two
role nouns: "`trampoline()` is the engine, the loop at `[1]`. PEP 342
calls such a driver a *trampoline*". The reader takes the new noun for
a new thing and looks for it. Pick the role noun by the chapter's own
definitions and keep it. A noun the chapter has defined ("the *driver*
(the loop that runs such a conversation)", chapter 45's opening list)
is used only for a thing that fits the definition: `trampoline()`
delegates with `yield from` and `run_all()` calls `send()`, so
`run_all()` is the driver and `trampoline()` is the engine. A pointer
phrase with a role noun ("such a driver", "this handler", "that
engine") is where the second name most often enters: the noun after
"such a", "this", or "that" is one the passage has already used for
that thing ("such a loop", after "The loop at `[1]`").

**Keep when.** The sentence states that the two roles are one ("the
proxy is also a driver: it calls `next()` on `inner`"), or the second
noun is a wider class the sentence places the thing in ("`drive()` is
a function like any other").

**Sightings.** 1, `45_Effects--Generators` 2026-11-12, was
Claude-written, Bruce: "first it calls it an engine, then a driver":
- "`trampoline()` is the engine, the loop at `[1]`. PEP 342 calls such
  a driver a *trampoline*" -> "The loop at `[1]` is the whole engine.
  PEP 342 calls such a loop a *trampoline*"
- same pass, the lead-in above the listing, found by grepping the
  section for the two nouns: "`luring()`'s body runs when a driver
  delegates to it. Here, `trampoline()` is that driver:" ->
  "`luring()`'s body starts when an engine delegates to it. Here,
  `trampoline()` is the engine and `run_all()` is its driver:"
- Why the passes missed it: each sentence is clear alone, and the
  fault is between them. The antecedents pass tests a pointer for two
  candidate targets, and "such a driver" has one. `[SAME+NEW]` tests
  the noun after "same" against the passage and nothing tests the noun
  after "such a", "this", or "that". The ambiguity pass reads for one
  word with two senses, and this is the reverse, two words for one
  thing. No pass checks a defined term against its definition.

**Home.** antecedents (Accrued patterns) | super-prose (pass 5) | this
file.

### C68. A part the design lacks does not "disappear": say what holds its job

**Test.** A verb of vanishing ("disappears", "vanishes", "goes away",
"is gone", "drops out", "melts away") whose subject is a class, an
object, a field, or a step that one design has and another lacks: "so
each state receives the data it needs and the machine object
disappears". Nothing on the page disappears: the design under
discussion never had the part, and the reader asks which object, and
from where. Say which construct in this design does the part's job, in
the words of both listings: "parameters and locals hold the data that
`VendingMachine` keeps in attributes".

**Keep when.** Something on the page is removed by a step the prose
narrates, and a later listing shows it gone ("Delete the `else` branch
and the second diagnostic disappears", written as "If you delete the
`else` branch, the type checker reports one diagnostic" by R9 where the
positive is available).

**Sightings.** 1, `45_Effects--Generators` 2026-11-12, was
Claude-written, Bruce: "??":
- "so each state receives the data it needs and the machine object
  disappears." -> "In that design, parameters and locals hold the data
  that `VendingMachine` keeps in attributes."
- Why the passes missed it: the literal pass reads for a figure
  standing in for a mechanism, and "disappears" is a dead metaphor
  that reads as a plain verb. The positive pass prefers it: it is the
  positive form of "needs no machine object", the kind of word a
  rewrite reaches for to remove a negative (C62 records the same
  habit for "alone" and "only"). `tip watch-words` has no entry for
  the verbs.

**Home.** literal (Accrued patterns) | super-prose (pass 1) | this
file.

### C69. A subject with a fronted-object relative clause becomes a condition

**Test.** A subject noun followed by a relative clause whose object
comes first, so two noun phrases sit side by side before any verb: "A
machine whose states a test must enumerate belongs in chapter 31's
table". The reader gets "a machine", "whose states", "a test" in a row
and has to hold all three until "must enumerate" says who does what to
which, and "states" can be read as a verb on the way. The same shape
with "that" or no pronoun: "the value that the driver the proxy wraps
sends". The relative clause is a condition on the subject, so write it
as one, in subject-verb-object order, and give the main clause what is
left: "If a test must enumerate a machine's states, use chapter 31's
`Enum` design."

**Keep when.** The relative clause's subject is a pronoun or one short
code span and the verb follows at once ("the value it sends", "the
generator `outer()` returned"), so no two noun phrases meet.

**Sightings.** 1, `45_Effects--Generators` 2026-11-12, was
Claude-written, Bruce: "??":
- "A machine whose states a test must enumerate belongs in chapter
  31's table." -> "If a test must enumerate a machine's states, use
  chapter 31's `Enum` design."
  The same edit made "chapter 31's table" into "chapter 31's `Enum`
  design": the paragraph opens on "Chapter 31's `Enum`", and "table"
  was a second name for it (C67).
- same section and day, Bruce: "awkward confusing": "A *Memento*
  belongs to the enum designs, which keep the state in a value a
  record can hold." -> "In the enum designs, the current state is an
  `Enum` member, which a *Memento* can store in a field."
  The shape sat at the end of the sentence this time, with no
  relative pronoun: "a value a record can hold" puts "a value" and "a
  record" side by side. Both nouns were also stand-ins: the value is
  an `Enum` member and the record is the *Memento*, so the repair
  names them and the clause becomes subject-verb-object with "which".
  "Belongs to" gave a verdict where the sentence could say what the
  *Memento* does (the literal pass's vague description). Additions to
  the test: the shape counts anywhere in the sentence, with or without
  "that"; and a clause built on "value", "thing", "object", or
  "record" as a stand-in gets the named thing first, which usually
  removes the clause.
- Why the passes missed it: `tip subject-gap` lists a subject nine or
  more words from its verb, and "machine" is six from "belongs". The
  straighten pass reads for a subject held open by length, and this
  one is short and dense. `[REL+AND]` needs a conjunction after the
  clause. No rule reads a relative clause for the order of its own
  subject and object.

**Home.** straighten (Accrued patterns) | super-prose (pass 3) | this
file.

### C70. A modifier that narrows a claim says the other cases differ: probe them

**Test.** A true claim carries a restricting modifier on its object or
subject: "`copy.deepcopy()` and `pickle` both raise a `TypeError` on a
suspended generator". The reader takes the modifier as the boundary of
the claim and asks about the other side (Bruce: "because a suspended
generator cannot be copied? can a generator in any state be copied?").
Run the claim with the modifier removed or reversed. If it still
holds, the modifier is the case the writer had in mind and not a
condition: state the full range ("for every generator, started or
not") and then, as a consequence, the case the passage cares about,
tied to the range by the fact that puts it there ("A machine in this
design is a generator, so a program cannot copy it or save it"). The
consequence gets the same test: it carries no modifier of its own
that the range does not need. If the other cases do differ, say how
in the same passage.

**Keep when.** The probe shows the other case behaves differently
("the first `send()` to an unstarted generator accepts `None`"), or
the passage has already defined the restricted set and the sentence is
about it by construction.

**Sightings.** 1, `45_Effects--Generators` 2026-11-12, was
Claude-written, Bruce's question above:
- "`copy.deepcopy()` and `pickle` both raise a `TypeError` on a
  suspended generator, so a *Memento* belongs to the enum designs" ->
  "`copy.deepcopy()` and `pickle.dumps()` raise a `TypeError` for
  every generator, started or not, so a program cannot copy or save a
  machine that is paused in a state. A *Memento* belongs to the enum
  designs"
- the repair above, minutes later, Bruce: "Only a Machine, or any
  generator? If it's not paused can it be copied?": "so a program
  cannot copy or save a machine that is paused in a state." -> "A
  machine in this design is a generator, so a program cannot copy it
  or save it."
  The repair moved the narrowing modifier from the first clause to
  the consequence ("that is paused in a state" for "suspended") and
  added a second narrowing, "a machine" for "a generator", with
  nothing saying a machine is a generator. Claude wrote it in the same
  edit that wrote this rule, so the rule's test goes on the repair
  before the commit, as C62 says of a limiter added to a positive
  rewrite.
  Probe, `uv run python` 3.15.1: `copy.copy()`, `copy.deepcopy()`, and
  `pickle.dumps()` each raise "TypeError: cannot pickle 'generator'
  object" for a generator that is `GEN_CREATED`, `GEN_SUSPENDED`, and
  `GEN_CLOSED` (closed and exhausted both).
- Why the passes missed it: the sentence is true, so every claim check
  passed it. `tip overclaims` lists a bound that claims too much
  ("the only", "one restriction"), and this modifier claims too
  little. C62's deletion test reads "only", "alone", and "just", not
  an adjective. No pass asks what a modifier implies about the cases
  it leaves out.

**Home.** ambiguity (Accrued shapes) | super-prose (pass 6) | this
file.

### C71. A listing that leaves the section's running example says what question about that example it answers

**Test.** A section has followed one example (the mousetrap, the
booking) through several listings, and the next listing uses new
names that the example never had (`tick()`, `tock()`), under a
lead-in that names neither the example nor the question: "One shape
looks like a transition and is a delegation:". The reader cannot tell
whether the section has moved on. Write the lead-in from the running
example: say what that example does ("a state returns the next state
and `trampoline()` delegates to it"), state the alternative or the
question the new listing takes up ("The alternative is for each state
to delegate to the next state itself, with `return (yield from
luring())` in place of `return luring()`"), and introduce the new
names as an instance of it ("`tick()` and `tock()` are two states
written that way:"). When the section has no subsections and the new
listing opens a question of its own, it also gets a heading that
names the question ("Why a Trampoline"). The paragraph that returns
to the running example afterward starts a new paragraph and names the
example's function ("`trampoline()` keeps the chain one level deep").

**Keep when.** The new listing reuses the example's names or imports
its module, so the tie is in the code; or the previous paragraph
already posed the question the listing answers.

**Sightings.** 1, `45_Effects--Generators` 2026-11-12, was
Claude-written, Bruce: "this subsection has been about mousetraps and
so the rest of this is kind of an abrupt change; does it need it's
own subsection or some other clarification?":
- "One shape looks like a transition and is a delegation:" -> a
  heading, "### Why a Trampoline", and the three-sentence lead-in
  quoted in the test.
- Why the passes missed it: every prose pass reads sentences and
  paragraphs, and this fault is between a listing and the section
  around it. Super-prose's scope says headings stay, so no pass could
  add one. `survey self-name` and `survey absent-name` test a lead-in
  against the listing under it and never against the listings above.
  The lead-in's "One shape" is a vague subject the literal pass could
  have caught, and it would have rewritten the sentence without
  supplying the tie.

**Home.** cohesion (Accrued patterns) | super-prose (pass 4 and Scope)
| this file.

### C72. In a listing walkthrough, the code's actor gets the verb, not "I"

**Test.** A paragraph walks a listing, and a sentence makes "I" or
"we" the subject of a verb about the code: "because I typed them",
"I added a `return`", "we pass `None`". The book's "I" gives an
opinion or the author's history, so here the reader stops to ask who
is speaking and why the author appears. Give the verb to the thing on
the page ("because its annotation declares them"), or to "the
programmer" or "you" where a person must act. Check the pronouns in
the rest of the sentence while there: the cut "I" can leave an "it" or
"them" with two candidates ("reads them back without comparing them
with the calls in its body" -> "reads the annotation without comparing
it with the calls in `greet()`'s body").

**Keep when.** The sentence gives an opinion ("I find Structural and
Behavioral far less useful"), the author's history ("I wrote *Thinking
in C++*"), or a term the author coined ("what I call"); or the chapter
uses "we" for a step shared with the reader ("We can modify
`task_runner()`").

**Sightings.** 1, `A_Effect_Tracking` 2026-11-13, was Claude-written,
Bruce: "unusual use of 'I'":
- "`greet()`'s row lists `Ask` and `Tell` because I typed them, and
  `row()` reads them back without comparing them with the calls in its
  body." -> "because its annotation declares them, and `row()` reads
  the annotation without comparing it with the calls in `greet()`'s
  body."
- Why the passes missed it: the sentence is active and names an actor,
  so activate's tests pass it. `tip past-tense` skips a main-clause
  past whose subject is "I" or "we", and no other tool lists the
  pronoun. It was the one "I" in the appendix; the 16 others in
  `Chapters/` found by a grep for "I" plus a verb are opinion or
  history, in chapters 01, 20, 21, and 43.

**Home.** activate (Accrued patterns) | super-prose (pass 7) | this
file.

## Retired

Rejected by Bruce, or promoted and later withdrawn. Never propose these
again. Record the reason: a bare "rejected" tells a future round nothing and
invites a reworded re-proposal.

### X1. Do not activate a passive that names an arrangement

Proposed 2026-09-01 as a contradiction: `26_Patterns--Factory` had
"If the code that creates objects appears throughout your application"
(Claude-written) and Bruce changed it to "is distributed throughout",
which vale flags. Bruce: "keep 'distributed'". The passive describes
where the code sits, with no agent worth naming. Recorded as a keep-when
in the `activate` skill (Step 2, passives). Do not propose "appears" or
any active rewrite for this shape again.

Retired 2026-10-04 at Bruce's ruling (Sweep Decisions page, "Let
activate win, retire R14"). The activate pass had rewritten the
lead-ins in chapters 20 and 24 (7d5576d0) to "A test confirms that" and
"The first test below confirms", and chapter 37 reads "The tests confirm
that"; those stay as activate wrote them, and the "Testing confirms
that" form is no longer applied anywhere. The lead-in-only layout note
(explanation after the listing) is still good practice. Entry as it
stood:

### X2. (was R14) Introduce a test listing with "Testing confirms that ..."

**Test.** A sentence introducing a test listing whose subject is "The
tests", "The test", "Tests", "A test", or "another" ("A test confirms
X, and another shows Y:"). Write "Testing confirms that X, and Y:".

**Keep when.** The sentence names a specific test function.

The lead-in is the only prose before the listing. A paragraph that
explains how the tests work (a helper they share, what they assert)
goes after the listing, not before it.

**Sightings.** 3, `26_Patterns--Factory` and `27_Patterns--Function_Objects`,
was Claude-written; plus the 2026-09-15 sweep
- 2026-08-31 (`0b7ff81d`): "The tests confirm that every subclass
  registers itself" -> "Testing confirms that every subclass registers
  itself"
- 2026-09-15 (`a9ca27eb`): "A test confirms the two forms produce the
  same pizza, and another shows the single-use hazard:" -> "Testing
  confirms that the two forms produce the same pizza, and the
  single-use hazard:"
- 2026-09-15 sweep after promotion, seven sites in six chapters, all
  Claude-written: `17` "Tests confirm the `@final` marker is present,"
  ; `20` "The test confirms the defensive copy holds."; `24` "The test
  confirms the objects differ but share one set of state."; `28`, `37`,
  and `42` (twice) "The tests confirm that ..." -> each "Testing
  confirms that ...". Before the sweep the book had three "Testing
  confirms" (17, 26, 27) against those seven.
- `27_Patterns--Function_Objects` 2026-09-16, was Claude-written, the ordering
  note: "The first two tests wrap each finder in `watched()`, which
  records the finder's name as it runs. The tests can then assert not
  just the root but *which* finders ran." moved from before
  `test_chain.py` to after it, leaving "Testing confirms that ..." as
  the only sentence before the listing

**Home.** this file only. Promoted at Bruce's call on one chapter's
evidence (2026-09-15, C14 -> R14).
