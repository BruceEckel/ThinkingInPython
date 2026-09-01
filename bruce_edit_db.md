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

**Sightings.** 2 (additive)
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
in the section's listings (`run()`, `fix`), used in a different sense in
the same section. Choose a synonym for the prose sense ("executes",
"repair", "anchored") and keep the identifier's word for the identifier.

**Keep when.** The prose word names the identifier itself ("`run()` runs
the steps" is about `run()`).

**Sightings.** 2 (additive), both `25_Patterns--Template_Method` 2026-08-29, was
Claude-written:
- "an override of `run()` is reported before the program runs" ->
  "Discovers an overridden `run()` before the program executes"
- "the quick fix" / "the fixed algorithm" / "What Actually Fixes the
  Algorithm" -> "the quick repair" / "the anchored algorithm" / "What
  Anchors the Algorithm" (Bruce: "the word 'fix' seems to be used in
  both senses in this chapter")

**Home.** this file only. Promoted at Bruce's call (2026-08-29).

### R4. Front an already-established cause with "Because"

**Test.** "X, so Y" where X restates something the reader already has
(a fact the chapter established, a listing just shown) and Y is the
sentence's claim. Rewrite as "Because X, Y".

**Keep when.** X is new information. Bruce's own "no subclass exists, so
nothing can replace the loop" keeps "so": the absence of a subclass is the
point being made. Chapter 26 confirmed this boundary from the other side.
Bruce fronted "Every assignment after `__init__()` reaches the
implementation, so ..." with "Because", then later rewrote the same
sentence back to "so" once he had added "Now" and "via the new
`__setattr__()`", which turned the clause into new information. The revert
is evidence for the exception, not against the rule.

**Sightings.** 3 (2 chapters):
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
listing follows anyway.

**Keep when.** The pointer carries a claim the listing does not make on
its own ("The next listing shows the same trap in a generator").

**Sightings.** 1 (removal), `25_Patterns--Template_Method` 2026-08-29, was
Claude-written:
- "The example below shows why." -> deleted

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

**Test.** "directly", "potentially", "possibly", or a description by what
does not happen ("an attribute nothing reads") where the concrete means,
frequency, or kind can be named ("as arguments", "sometimes", "a
type-checking attribute").

**Keep when.** The concrete word is unknown or would be wrong; a hedge
that is the claim ("potentially unbounded") stays.

**Sightings.** 3 (additive), all `25_Patterns--Template_Method` 2026-08-29, was
Claude-written:
- "pass the steps in directly" -> "pass the steps as arguments"
- "an attribute nothing reads" -> "a type-checking attribute"
- "code written later, potentially years later" -> "code written later,
  sometimes years later"

**Home.** this file only. Promoted at Bruce's call (2026-08-29).

---

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

### C3. Replace a judgment about the mechanism with the mechanism

**Test.** A phrase that evaluates or characterizes rather than describes
("costs nothing", "satisfies", "is the exception", "they expect"), or a
scare-quoted idiom, where the sentence can state what actually happens.
Ask what the reader would observe; if the phrase does not say, replace it.

**Keep when.** The judgment is the claim being made and the mechanism is
already stated nearby, as in a summary sentence that closes a section.

**Sightings.** 5, all `26_Patterns--Surrogate` 2026-08-31, was
Claude-written (same chapter, so not yet independent):
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

### C4. Cut the clause that defines this thing by contrast with the one just discussed

**Test.** A sentence or trailing clause whose work is to say how the
current subject differs from the previous section's subject, where the
current subject's own description already stands without it.

**Keep when.** The contrast is the section's point, or the two are a
lookalike pair the chapter exists to separate.

**Note.** Both sightings are deletions. The first removed a
Proxy/Decorator contrast that `29_Patterns--Changing_the_Interface`
already carries in its comparison table, so the underlying rule may be
narrower: leave cross-pattern comparison to the chapter that owns it. Two
sightings in one chapter cannot decide between the two readings.

**Sightings.** 2, both `26_Patterns--Surrogate` 2026-08-31, was
Claude-written (same chapter, so not yet independent):
- "That refusal separates a *Proxy* from a *Decorator*: a decorator adds
  behavior around a call it always makes. This proxy decides whether to
  forward the call." -> "`Guarded` requires `admin` privileges to call
  `erase()`."
- "A *Smart reference* proxy adds behavior around each access without
  refusing any." -> "A *Smart reference* proxy adds behavior around each
  access."

### C5. Cut "In Python" in a Python book

**Test.** "In Python" (or "in Python code") introducing a claim that the
whole book already scopes to Python.

**Keep when.** The sentence contrasts Python with another language, which
is the usual reason the phrase was written.

**Sightings.** 1, `26_Patterns--Surrogate` 2026-08-31, was Claude-written:
- "In Python both are the same few lines of `__getattr__()` delegation"
  -> "Both are the same few lines of `__getattr__()` delegation"

### C6. Name a pointer's antecedent only where a competitor exists

**Test.** A refinement of the `/antecedents` pass rather than a new sweep.
A pronoun or demonstrative with a competing candidate in reach gets its
noun; one whose subject just appeared unopposed keeps the pronoun.
`/antecedents` fires on ambiguity, not on pronouns.

**Keep when.** This *is* the keep-when for `/antecedents`. The reverse
sighting below is the whole point of the entry: a sweep that reads the
other ten as "prefer the noun" will overshoot.

**Sightings.** 11, all `26_Patterns--Surrogate` 2026-08-31, was
Claude-written (same chapter, so not yet independent). Ten resolved a
pointer that had a competitor:
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
- "instead of running attribute lookup, and never calls `__getattr__()`"
  -> "instead of running attribute lookup. That function never calls
  `__getattr__()`"
- "It also ties this surrogate to one Protocol" -> "That annotation also
  ties the surrogate to one Protocol"
- "which is what the generic surrogate exists to avoid" -> "and that tie
  is what the generic surrogate exists to avoid"

One went the other way, where the subject had just appeared unopposed:
- "because `Proxy` names no methods in `Implementation`, the proxy keeps
  working" -> "because `Proxy` names no methods in `Implementation`, it
  keeps working"

**Home.** the `antecedents` skill, as a keep-when. Not a separate sweep.

---

## Retired

Rejected by Bruce, or promoted and later withdrawn. Never propose these
again. Record the reason: a bare "rejected" tells a future round nothing and
invites a reworded re-proposal.

*(none yet)*
