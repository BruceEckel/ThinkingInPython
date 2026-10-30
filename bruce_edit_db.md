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
  `isinstance()` test against each rule."

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
listing's discussion beside the next listing's. A pronoun or "This"
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
or fewer rarely splits. Never split inside a list item, a block quote,
a footnote, or an exercise statement.

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
purpose clause ("To break the cycle, the setter returns early"). Write
"Here, X ...".

**Keep when.** The sentence states a general property rather than one
of the adjacent listing (C16); "Here," belongs on a claim about that
listing only.

**Sightings.** 4 (additive), 2 chapters
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

**Home.** CLAUDE.md (project, the `tip sentence-shapes` paragraph:
`[ADD]` is a survey rule there, since 161 of the 178 hits were keeps);
this file. Promoted on Bruce's ruling, the way R46 to R48 were.

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

**Home.** CLAUDE.md (global, "One picture per clause"); `tip
sentence-shapes` (`[TWO]`, `SURVEY_RULES` in `tools/sentence_shapes.py`,
`comparator()`, `heavy_side()`, `two_terms()`); the deep-review skill's
prose pass; this file. Promoted on Bruce's ruling, the way R46 to R50
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

### C2. Name the actor for a language mechanism

**Test.** A language feature sits in subject position under a verb it
cannot perform on its own: a hook "fires", a lookup "sees", a call
"asks", a checker "wants". Name the actor that performs it (Python, the
type checker, the caller) and use the verb that actor performs.

**Keep when.** The mechanism really is the actor. A function that returns
or raises does so itself, and "`__getattr__()` returns a value" needs no
rewriting.

**Sightings.** 3, all `25_Patterns--Surrogate` 2026-08-31, was
Claude-written (same chapter, so not yet independent):
- "`__getattr__()` fires for any name the proxy and its class lack" ->
  "Python calls `__getattr__()` for any name the proxy and its class
  lack"
- "`__getattr__()` never sees a special method, never sees an assignment"
  -> "Python never calls `__getattr__()` for a special-method lookup or
  for an assignment"
- "`len(p)` asks `type(p)` for `__len__()` without consulting the
  instance" -> "`len(p)` looks up `__len__()` on `type(p)`, skips the
  instance"

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

### C26. In a heading, one verb rather than a split phrasal verb

**Test.** A heading whose verb's particle sits after the object
("Telling X Apart", "Setting X Off") where one verb says the same
("Distinguishing X", "Offsetting X").

**Keep when.** Prose sentences: the global CLAUDE.md allows a phrasal
verb with its object present ("pass it around"). Headings only.

**Sightings.** 1, `29_Patterns--Changing_the_Interface` 2026-09-17
(`cacb544f`), was Claude-written, Bruce's own edit:
- "## Telling the Wrappers Apart" -> "## Distinguishing the Wrappers"

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
