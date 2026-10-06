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
- `27_Patterns--Factory` 2026-09-01 (`6f638b05`), was Claude-written:
  "A placeholder raises only when something calls it" -> "A placeholder
  raises an exception only when something calls it"
- `25_Patterns--Template_Method` 2026-08-29, was Claude-written:
  "The `class Typo` statement raises instead of finishing" ->
  "The `class Typo` statement raises a `TypeError` instead of finishing"
- `Solutions/14_Techniques--Decorators`, `Solutions/25_Patterns--Template_Method`,
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

**Sightings.** 3 (removal), all `25_Patterns--Template_Method` 2026-08-29, was
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

**Keep when.** The prose word names the identifier itself ("`run()` runs
the steps" is about `run()`).

**Sightings.** 4 (additive), 2 chapters
- `27_Patterns--Factory` 2026-09-01 (`40323f50`), was Claude-written, in
  a chapter whose class is `Shape`: "the shape a factory-object design
  takes" -> "the form a factory-object design takes"
- `27_Patterns--Factory` 2026-09-12 (`4ab635e2`), was Claude-written, in
  a chapter where `kind` is the selector parameter of six listings: "a
  factory of the same kind as `factory()`" -> "a factory, of the same
  form as `factory()`"
- `25_Patterns--Template_Method` 2026-08-29, was Claude-written:
  "an override of `run()` is reported before the program runs" ->
  "Discovers an overridden `run()` before the program executes"
- "the quick fix" / "the fixed algorithm" / "What Actually Fixes the
  Algorithm" -> "the quick repair" / "the anchored algorithm" / "What
  Anchors the Algorithm" (Bruce: "the word 'fix' seems to be used in
  both senses in this chapter")

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
- `27_Patterns--Factory` 2026-09-01 (`40323f50`), was Claude-written,
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
- `25_Patterns--Template_Method` 2026-08-29, was Claude-written:
  "`run()` calls methods the subclass supplies, so the subclass must
  finish its own setup" -> "Because `run()` calls methods the subclass
  supplies, the subclass must finish its own setup"
- `25_Patterns--Template_Method` 2026-08-29, was Claude-written:
  "Python functions are first-class, so you can also pass the steps" ->
  "Because Python functions are first-class, you can also pass the steps"
- `26_Patterns--Surrogate` 2026-08-31, was Claude-written:
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

**Sightings.** 4, one list in `25_Patterns--Template_Method` 2026-08-29, was
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

**Sightings.** 1, `25_Patterns--Template_Method` 2026-08-29 (`19b2b1e3`), was
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
- `27_Patterns--Factory` 2026-09-01 (`0b7ff81d`), was Claude-written:
  "The next step gives each of those operations its own object." ->
  deleted, ahead of "A *factory object* defines a single `create()`
  method"; "No factory method and no factory class. The `dict` is the
  factory:" -> "No factory method and no factory class:"
- `27_Patterns--Factory` 2026-09-12 (`a03658af`), was Claude-written:
  "The rest of this chapter replaces call sites like these with a
  single place that knows about every shape." -> deleted; the next
  paragraph opens "The solution is to encapsulate object creation."
- `27_Patterns--Factory` 2026-09-12 (`a9731125`), was Claude-written:
  "The next example, `registry.py`, cannot take the same fix. Its whole
  point is that a new `Shape` subclass registers itself" -> "It would
  be even nicer if a new `Shape` subclass would register itself"
- `25_Patterns--Template_Method` 2026-08-29, was Claude-written:
  "The example below shows why." -> deleted
- `28_Patterns--Function_Objects` 2026-09-16, was Claude-written, a list rather than a
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

**Sightings.** 1 (removal), `25_Patterns--Template_Method` 2026-08-29, was
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
- `26_Patterns--Surrogate`: "`hasattr()` catches only `AttributeError`"
  -> "`hasattr()` catches `AttributeError` and lets every other
  exception propagate"
- `46_Effects--Stateless`: "a double that overrides only `print()`" ->
  "a double that overrides `print()` and inherits `input()`"
- `27_Patterns--Factory`: "it lists only direct subclasses" -> "it lists
  direct subclasses and misses their descendants"; "adding a new type
  only changes the factory" -> "changes the factory and no call site"
- `Solutions/46_Effects--Stateless`: "the handler answers only
  `Need[Console]`" -> "answers `Need[Console]` and not `Need[Clock]`"
- Widened to cover `only X` on 2026-10-04, at Bruce's approval.
- `27_Patterns--Factory` 2026-09-01 (`2b18eed8`), was Bruce-written
  (older draft): "you will likely extend your program" -> "you often
  extend that program"; "first use polymorphism to create a common
  interface" -> "first create a base type as a common interface"
- `27_Patterns--Factory` 2026-08-31 (`2b18eed8`), was Bruce-written
  (older draft): "`factory()` is now the only other code that changes"
  -> "Apart from the new subclass itself, `factory()` is the only code
  that changes"; and, Claude-written, "and rules span the steps" ->
  "and some rules apply across several steps"
- `25_Patterns--Template_Method` 2026-08-29, was Claude-written:
  "pass the steps in directly" -> "pass the steps as arguments"
- "an attribute nothing reads" -> "a type-checking attribute"
- "code written later, potentially years later" -> "code written later,
  sometimes years later"
- `29_Patterns--Changing_the_Interface` 2026-09-16 (`144c546f`), was
  Claude-written: "The variations above are Java habits." -> "All three
  approaches carry one Java habit: the adapter inherits from `WhatIWant`
  so that `op()` accepts it."

**Home.** this file only. Promoted at Bruce's call (2026-08-29).

### R10. Replace a judgment or figure about a mechanism with the mechanism

**Test.** A phrase that evaluates or characterizes rather than describes
("costs nothing", "satisfies", "is the exception", "they expect"), or a
scare-quoted idiom, where the sentence can state what actually happens.
Ask what the reader would observe; if the phrase does not say, replace it.

**Keep when.** The judgment is the claim being made and the mechanism is
already stated nearby, as in a summary sentence that closes a section.

**Sightings.** 17 (3 chapters)
- `26_Patterns--Surrogate` 2026-08-31, was Claude-written, five:
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
- `27_Patterns--Factory` 2026-09-01, was Claude-written, three:
  "The registry also never forgets:" -> "The registry also never
  removes an entry:"; "The chained call in `__main__` hides the problem
  by throwing the builder away on the same line that creates it" ->
  "never shows the problem, because it keeps no reference to the
  builder after `build()` returns"; "each implementation picks a side"
  -> "chooses one behavior or the other"
- `27_Patterns--Factory` 2026-08-31 (`40323f50`, `2b18eed8`), five
  more, logged 2026-09-15: "hands `cls.__name__` straight to
  `factory()`" -> "passes `cls.__name__` unchanged to `factory()`"; "A
  *factory object* carries a single `create()` method" -> "defines a
  single `create()` method"; "choosing which object to ask" ->
  "choosing which factory object to call"; "calls it right away" ->
  "calls its `create()` immediately"; and, in Bruce's own older draft,
  "the most sensible first step is to use polymorphism" -> "first use
  polymorphism"
- `28_Patterns--Function_Objects` 2026-09-16, was Claude-written, four, three of
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

**Home.** literal (Accrued patterns), the pass that owns figures.
Promoted 2026-09-01 on the second chapter's sightings (C3 -> R10).

### R11. Cut a scope phrase the book already supplies

**Test.** "In Python", "in Python code", "in your code", "in the system",
"in this design" introducing or qualifying a claim that the chapter
already scopes that way. Delete the phrase.

**Keep when.** The phrase contrasts with another language or another
system ("in Python, unlike Java"), which is the usual reason it was
written.

**Sightings.** 3 (2 chapters)
- `26_Patterns--Surrogate` 2026-08-31, was Claude-written:
  "In Python both are the same few lines of `__getattr__()` delegation"
  -> "Both are the same few lines of `__getattr__()` delegation"
- `27_Patterns--Factory` 2026-09-01, was Claude-written:
  "every place in your code that names a concrete type" -> "every place
  that names a concrete type"
- `27_Patterns--Factory` 2026-09-01, was Bruce-written (older draft):
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
- `27_Patterns--Factory` 2026-08-31 (`40323f50`), was Claude-written,
  six: "It covers only the first level of inheritance" ->
  "`__subclasses__()` covers only the first level of inheritance"; "It
  registers itself" -> "`Triangle` registers itself"; "They fail at
  call time" -> "Those bodies fail at call time"; "There the table
  holds classes" -> "In `registry.py` the table holds classes"; "which
  puts the creation method on a class" -> ": that pattern puts the
  creation method on a class"; "which is worse than unnecessary" ->
  "and that dispatch is worse than unnecessary"
- `27_Patterns--Factory` 2026-09-14 (`7ec15c2e`), was Claude-written:
  "the class solves a problem Python does not have" -> "the builder
  class solves a problem Python does not have" (competitor: `Pizza`)
- `26_Patterns--Surrogate` 2026-08-31, was Claude-written, eleven. Ten
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
- `26_Patterns--Surrogate` 2026-08-31, was Claude-written: "That refusal
  separates a *Proxy* from a *Decorator*: a decorator adds behavior
  around a call it always makes. This proxy decides whether to forward
  the call." -> "`Guarded` requires `admin` privileges to call
  `erase()`." The Proxy/Decorator comparison lives in
  `29_Patterns--Changing_the_Interface`'s table.
- `26_Patterns--Surrogate` 2026-08-31, was Claude-written: "A *Smart
  reference* proxy adds behavior around each access without refusing
  any." -> "A *Smart reference* proxy adds behavior around each
  access." A contrast cut with no link beside it; the narrowing sets
  this sighting aside rather than claiming it.
- `27_Patterns--Factory` 2026-08-31 (`d6144479`), was Claude-written:
  "a convention rather than concealment, and the convention is all
  Python provides ([Singleton](...) makes the same case)" -> "a
  convention rather than concealment ([Singleton](...) makes the same
  case)". Chapter 24's linked section says "Privacy in Python is advice,
  not enforcement."
- `27_Patterns--Factory` 2026-09-15 (`a9ca27eb`), was Claude-written:
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

- `28_Patterns--Function_Objects` 2026-09-16, was Claude-written: "You provide a
  function that decides how to compare." -> "That argument determines
  how comparison works."

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
  [Iterators](23_Patterns--Iterators.md#generators))." -> "I have also
  used a [*generator*](23_Patterns--Iterators.md#generators)."
- 2026-08-31 (`0b7ff81d`): "`cls.registry` resolves through the MRO" ->
  "resolves through the [MRO](07_Foundations--Classes.md#inheritance)"
- 2026-09-15 (`a9ca27eb`): "`copy.replace()` is the general form of the
  same operation, working on any object that defines `__replace__()`,
  shown in [The General Form of `replace()`](...)." -> "`copy.replace()`
  is the [general form of the operation](...), and works on any object
  that defines `__replace__()`."
- `28_Patterns--Function_Objects` 2026-09-16: "It is a *closure* ([Functional
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
- `27_Patterns--Factory` 2026-09-01 (`6f638b05`): "Uncomment the line
  that passes a `BrokenFactory` to `GameEnvironment`, and the checker
  reports" -> "If you uncomment the line ..., the checker reports"
- `27_Patterns--Factory` 2026-09-01, in conversation: "Define a factory
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
- `28_Patterns--Function_Objects` 2026-09-16: "Three identical lines are
  the point: the algorithm changes and the caller stays the same." ->
  deleted
- `28_Patterns--Function_Objects` 2026-09-16: "Those five classes
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
chapter's opening claim. Keep the concrete one, or the opening.

**Keep when.** The second sentence adds a consequence or a mechanism
the first did not state.

**Sightings.** 6, 2 chapters
- `27_Patterns--Factory` 2026-09-15 (`a9ca27eb`), was Claude-written:
  "Builder chains have a second use, starting from an existing
  configuration and varying it, covered by `dataclasses.replace()`."
  -> "A second use for builder chains is to vary an existing
  configuration." (the next sentence names `replace()`); "Each stage
  relies on what the previous stage established." -> "Each stage relies
  on the previous stage."
- `27_Patterns--Factory` (`2b18eed8`), was Bruce-written (older draft):
  "You must still find and edit every place that names a concrete type.
  Creation names the type. Use does not, because polymorphism handles
  use. The effect is the same: adding a new type means edits scattered
  through the code." -> "adding a type means finding and editing every
  place that names a concrete type."
- `27_Patterns--Factory` (`0b7ff81d`), was Claude-written: "No factory
  method and no factory class. The `dict` is the factory:" -> "No
  factory method and no factory class:"; "The next step gives each of
  those operations its own object. A *factory object* defines a single
  `create()` method" -> the second sentence alone
- `29_Patterns--Changing_the_Interface` 2026-09-16 (`f99192e5`), was
  Bruce-written (older draft), the section-opening shape: "When you've
  got "this", and you need "that", *Adapter* solves the problem." ->
  deleted from the Adapter section's opening; the chapter's first
  sentence already says "I don't have the interface I need."

**Home.** this file only. Promoted 2026-09-17 on the second chapter's
sighting, widened from consecutive sentences to the section-opening
restatement (C8 -> R19).

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
- `27_Patterns--Factory` 2026-09-12 (`571d9ec2`): "Both are static
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
- `Solutions/22_Patterns--Data_Transfer_Objects` 2026-10-02, the three
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
    Algorithms](../../Chapters/23_Patterns--Iterators.md#reusable-algorithms)
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
- `Solutions/25_Patterns--Template_Method`: "and leave only `process()`
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
that opens the new paragraph gets its noun.

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

**Sweep notes.** A seam whose next sentence carries "though", "also",
"the same way", or a mid-sentence "it"/"one" still leans on the
paragraph before; the agents' rule covered the opening word alone, so
read the whole first sentence of each new paragraph. The agents' "close
calls left whole" lists (about 300 across the book) are the cases this
rule keeps: a claim with its reason, a contrast, a one-sentence half.

**Home.** cohesion (Accrued patterns).

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
- `23_Patterns--Iterators`: "computes nothing until you iterate," ->
  "computes nothing until you iterate over it,"; "When a function
  iterates more than once" -> "When a function iterates over its
  argument more than once"
- `Solutions/27_Patterns--Factory`: "builds a generator that nothing
  iterates." -> "builds a generator and nothing iterates over it."
- `Solutions/44_Effects--Effect_Management`: "which `sum()` cannot
  iterate." -> "and `sum()` cannot iterate over it."

**Home.** this file only.

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

**Sightings.** 2, both `25_Patterns--Template_Method` 2026-08-29, was
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

**Sightings.** 3, all `26_Patterns--Surrogate` 2026-08-31, was
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

**Sightings.** 1 (additive), `27_Patterns--Factory` 2026-09-01
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

**Sightings.** 3 (additive), all `27_Patterns--Factory`, was
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

**Sightings.** 2, both `27_Patterns--Factory` 2026-09-01 (`40323f50`),
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

**Sightings.** 2, both `27_Patterns--Factory` 2026-08-31, was
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
`28_Patterns--Function_Objects` 2026-09-16 adds one more keep: Bruce split "In
Python the action is a function, and a 'macro' is a list of actions"
into "In Python the action is a function. In this example, a 'macro'
is a list of actions:", a locator on the listing-specific claim only.

**Sightings.** 3, all `27_Patterns--Factory` (same chapter, so not yet
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

**Sightings.** 1 (one list of six items), `27_Patterns--Factory`
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

**Keep when.** X was established earlier, so R4 applies.

**Sightings.** 3, all `27_Patterns--Factory` 2026-08-31 (same chapter,
so not yet independent):
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

### C19. Name a type's members instead of a coined phrase for its shape

**Test.** A quoted paraphrase standing in for a type or structure ("a
name for 'callable, plus `undo()`'"). Write the members the type has.

**Keep when.** None seen yet.

**Sightings.** 2 (additive), both `28_Patterns--Function_Objects` 2026-09-16,
was Claude-written (chapter and Solutions, so not yet independent):
- "a list of commands that also undo needs a name for "callable, plus
  `undo()`". That name is a `Protocol` with both members." -> "an
  undoable list of commands needs a type with two members,
  `__call__()` and `undo()`, and that type is a `Protocol`."
- Solutions: "needs a name for "callable, plus `undo()`", and in Python
  that name is a `Protocol` declaring both members." -> "needs a type
  with two members, `__call__()` and `undo()`, and in Python that type
  is a `Protocol`."

### C21. Cut the chapter roadmap paragraph; each sentence goes where its content is

**Test.** An opening paragraph whose sentences each say what a later
section will show ("*Command* appears first as a function, then as the
classic class-based form. ... A closing section keys the chain's
handlers by event type"). Delete it, and make sure each section states
the claim itself.

**Keep when.** None seen yet.

**Sightings.** 1 (removal), `28_Patterns--Function_Objects` 2026-09-16, was
Claude-written:
- the seven-sentence roadmap after the opening ("*Command* appears
  first as a function, then as the classic class-based form.
  *Strategy*'s function form gets the same fuller listing. ... and the
  list becomes an *event bus*.") -> deleted

### C22. Point at the adjacent listing with a leading "Here," rather than a trailing "below"

**Test.** "X below is ..." or "X below names ..." where X is defined in
the listing that follows. Write "Here, X is ...".

**Keep when.** None seen yet. Runs beside C16: "Here," belongs on a
claim about the adjacent listing, not on a general one.

**Sightings.** 2 (additive), both `28_Patterns--Function_Objects` 2026-09-16,
was Claude-written (same chapter, so not yet independent):
- "`Repeat` below is a frozen data class" -> "Here, `Repeat` is a
  frozen data class"
- "`Handler` below names their signature, not an interface:" -> "Here,
  `Handler` names their signature, not an interface:"

### C23. Factor a property shared by two parallel sentences into one clause before them

**Test.** Consecutive sentences about parallel items that each restate
the same property ("`@event` makes a class a frozen data class and
...", "`@handler` makes a class a frozen data class too, ..."). State
the shared property once, in a clause introducing the pair, and let
each sentence carry only what differs.

**Keep when.** None seen yet.

**Sightings.** 1 (structural), `28_Patterns--Function_Objects` 2026-09-16, was
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

**Sightings.** 1, `28_Patterns--Function_Objects` 2026-09-16, was Claude-written:
- "Adding, removing, or reordering handlers means editing a list." ->
  "To add, remove, or reorder the handlers you edit the `chain` list."

### C25. Open a scenario described in words with "Consider", and don't say that it is described

**Test.** An exercise or example whose material is the sentence itself
(no listing follows) opening with "Here are" / "Here is". Write
"Consider ...". Do not add an aside explaining that the material is
described rather than listed.

**Keep when.** None seen yet.

**Sightings.** 1, `29_Patterns--Changing_the_Interface` 2026-09-17, was
Claude-written, Bruce's own edit:
- "Here are three wrappers: one logs each call ..." -> (Claude) "Consider
  three wrappers, described in words rather than code: one logs each
  call ..." -> (Bruce) "Consider three wrappers: one logs each call ..."

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
- `28_Patterns--Function_Objects`: "The tests can then assert not only the
  root but also which finders ran." -> "The tests can then assert both the
  root and the names of the finders that ran."
- `25_Patterns--Template_Method`: "should expect to rename an occasional
  legitimate method, not only to catch misspellings" -> "should expect to
  catch typos and also to rename an occasional legitimate method"

## Retired

Rejected by Bruce, or promoted and later withdrawn. Never propose these
again. Record the reason: a bare "rejected" tells a future round nothing and
invites a reworded re-proposal.

### X1. Do not activate a passive that names an arrangement

Proposed 2026-09-01 as a contradiction: `27_Patterns--Factory` had
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

**Sightings.** 3, `27_Patterns--Factory` and `28_Patterns--Function_Objects`,
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
- `28_Patterns--Function_Objects` 2026-09-16, was Claude-written, the ordering
  note: "The first two tests wrap each finder in `watched()`, which
  records the finder's name as it runs. The tests can then assert not
  just the root but *which* finders ran." moved from before
  `test_chain.py` to after it, leaving "Testing confirms that ..." as
  the only sentence before the listing

**Home.** this file only. Promoted at Bruce's call on one chapter's
evidence (2026-09-15, C14 -> R14).
