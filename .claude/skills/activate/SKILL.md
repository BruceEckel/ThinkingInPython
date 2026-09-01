---
name: activate
description: Rewrite prose into the active, in-the-moment register: clear the passive-voice, there-is, weak-verb, and nominalization warnings from `make prose`, and fix what Vale cannot see (abstract subjects, tense drift, padded verb phrases, metadiscourse, empty frames). Use when asked to activate a chapter (or the whole book). The argument names chapters by number or name; no argument means all of Chapters/.
---

# Activating prose: characters as subjects, actions as verbs

The book's register is active, concrete, and present:
the reader watches the machinery run, now,
with a real actor in every subject and a real action in every verb.
"Active voice" names the grammar-level slice of that register,
but the principle is wider (Williams' *Style* states it as
"make characters your subjects and their actions your verbs"),
and a sentence can pass the grammar test and still be dead:
the action hiding in a noun, the subject an abstraction,
the tense pushed into a distancing "will."
This skill is the cleanup pass for the whole register.
It has two sources of findings:
the mechanical warnings `make prose` reports,
and a read-through for the constructions no linter catches.
The pass edits `Chapters/NN_*.md` prose only;
code blocks, `#:` output markers, and quoted material stay untouched.

## Step 1: collect the mechanical findings

Run `make prose CH=NN` (one chapter) or `make prose` (whole book);
it needs the standalone `vale` binary.
Collect the `write-good.Passive` and `write-good.ThereIs` hits,
plus the three House rules this skill added:
`House.WeakVerb` (is used to, serves to, is responsible for, acts as),
`House.Nominalization` (weak verb + article + a curated noun list,
plus "takes place"), and `House.InOrderTo`.
`make prose` is not part of any gate,
so a clean `make verify` says nothing about these warnings.

## Step 2: read for what Vale misses

Vale flags "to be + participle", sentence-initial "There is/are",
and the House patterns above,
but the House rules are deliberately partial:
Vale's regex engine has no lookahead,
so `House.Nominalization` matches a curated noun list
rather than a suffix pattern
(a `-tion` suffix rule would flag "function" and every other
domain noun that merely ends that way),
and a hit can still be a substring artifact
("makes the composition case for it" is about a case, not a composition).
Vale also does not flag an abstract subject,
a "will" where the present belongs,
a nominalization whose noun is not on the list,
metadiscourse, an empty frame,
or an expletive buried mid-sentence.
Read the chapter for the categories below.
They group into three questions:
where did the action go, what frames the point,
and is the reader watching it now.

## Where the action went

**Passive voice.**
The test: is there a real agent, present in the discussion,
that the sentence demoted or dropped?
If so, promote it to the subject:

- "a `test_*.py` file is run by `pytest`" becomes "`pytest` runs each `test_*.py` file"
- "The `{}` literal was taken by `dict` first" becomes "`dict` claimed the `{}` literal first"
- "where they are worked in pairs" becomes "where pairs work through them"

When no agent is on stage, swap the verb instead of inventing one:

- "The text is licensed CC BY-NC-ND" becomes "The text carries a CC BY-NC-ND license"
- "The book is organized into five parts" becomes "The book has five parts"
- "At most one target can be starred" becomes "At most one target can carry the star"
- "the new value is stored" becomes "its result goes into the dictionary"

Keep a passive when both moves fail:
when the natural rewrite needs a fabricated subject
("the system", "one", "the programmer")
or when cohesion wins (see Boundaries).
Keep it too when the verb names an arrangement rather than an act,
and no agent is worth naming:
"the code that creates objects is distributed throughout your application"
describes where the code sits, and Bruce chose it over
"appears throughout" (chapter 27, 2026-09-01).
Vale still flags it; the recorded reason is what makes the warning
acceptable.
A kept passive is a judgment call, not a defeat;
note it in the report so the warning's persistence has a recorded reason.

**Nominalizations.**
The action turned into a noun, leaving a weak verb to hold the grammar.
The tell is a noun in *-tion/-ment/-ance/-sion*
propped up by *make, do, perform, provide, occur, take place, happen*.
Put the action back in the verb, and its agent back in the subject:

- "The evaluation of the default happens once, at definition time"
  becomes "Python evaluates the default once, when it defines the function"
- "performs a lookup in the instance dictionary"
  becomes "looks up the name in the instance dictionary"
- "The conversion to bytes takes place before the write"
  becomes "The stream encodes the text before writing it"

The watch list already bans "happen";
a nominalized sentence is usually why the word appeared,
an action left with no agent to do it.
Fixing the nominalization removes the banned word for free.

**Relative clauses with no actor.**
A "that"/"which" clause whose verb has no character behind it
usually collapses into a participle or an adjective:

- "`list` internals that no reading of `CountingList` reveals"
  becomes "`list` internals hidden in `CountingList`"
- "a default that is shared by every call"
  becomes "a default shared by every call"

The first was a nominalization in disguise:
"no reading of X reveals" invents an abstract actor
so the clause has something to negate.
"Hidden" states the property and drops the machinery.
Leave the clause alone when its verb has a real actor
("the list that `extend()` mutates").

**Weak-verb frames.**
No nominalization needed; the verb slot is occupied by filler
while the real verb sits inside an infinitive or a complement.
*is used to, serves to, is responsible for, acts as, functions as, works to.*
The real verb takes over:

- "`functools.wraps` is used to preserve the metadata"
  becomes "`functools.wraps` preserves the metadata"
- "The decorator serves to register the class"
  becomes "The decorator registers the class"
- "`__slots__` is responsible for blocking new attributes"
  becomes "`__slots__` blocks new attributes"
- "The property acts as a guard on assignment"
  becomes "The property guards assignment"

**Abstract subjects.**
Grammatically active, but the subject is not a character:
"this approach", "the design", "the process", "the fact that".
The book has a real cast available in nearly every sentence:
Python, the interpreter, the checker, `pytest`, ruff,
the garbage collector, the event loop,
the caller, the reader,
and the named constructs themselves
(the decorator, the registry, the `finally` block, `__init__()`).
Name the concrete actor:

- "This approach allows callers to skip the check"
  becomes "The registry lets callers skip the check"
- "The design guarantees that cleanup runs"
  becomes "The `finally` block guarantees the cleanup runs"

When no cast member fits, the abstraction may be the honest subject
(a paragraph genuinely about a trade-off can say "the trade-off");
the target is the reflexive "this approach/this design" opener,
not every abstract noun.

**Expletive constructions.**
"There is / there are / it is ... that" frames.
The content nouns become the subject:

- "There are three cases that matter" becomes "Three cases matter"
- "It is the factory that builds the default" becomes "The factory builds the default"

The "is what" cleft is the same disease
(a delayed verb behind a dummy frame)
and already has its own rule in the global style guide;
apply that rule's deletion test during this pass.

## What frames the point

**Metadiscourse.**
Writing about the writing or the reader:
"note that", "you can see that", "it is worth mentioning",
"as we saw", "keep in mind that".
Usually pure deletion:
"You can see that the loop never runs" becomes "The loop never runs".
State advice as an imperative and facts as a declarative.
Keep "you can" when the option's existence is the news:
"You can supply a different `Console` in a test"
is about the option, and flattening it changes the meaning.

**Empty frames.**
A clause that delays the point without adding one:
"The thing to understand is that X" becomes "X";
"What this means is that Y" becomes "So Y" or just "Y".
The test is deletion: if the sentence means the same without the frame,
the frame was scaffolding.

A whole sentence can be the frame,
and then deletion is the entire fix.
An evaluative opener rates what the next sentence delivers:
"The cost is visible and finite. You forward every operation by hand"
loses nothing when the first sentence goes,
since the second shows the cost and lets the reader rate it.
The tell is an abstract subject plus an adjective
("The cost is visible and finite", "The difference is subtle",
"The benefit is twofold") standing alone ahead of the concrete case.
A frame keeping its payload in the same sentence survives:
"The difference is where the bug lives: in the class you read"
answers its own opener.

## Is the reader watching it now

**Tense: present for program behavior.**
Timeless behavior gets the present tense;
"will" pushes the action into a distanced future it does not occupy:

- "If the key is missing, a `KeyError` will be raised"
  becomes "A missing key raises a `KeyError`"
  (the passive and the tense were the same problem)
- "The checker will flag the call" becomes "The checker flags the call"
- "the second call will find the cache warm"
  becomes "the second call finds the cache warm"

Reserve "will" for a genuine future event
(a scheduled deprecation, a release that has not shipped)
and "would" for a genuine counterfactual
("without the guard, the setter would call the setter").
The house style's imperative-plus-consequence rule
already produces present-tense conditionals
("If you remove `frozen=True`, the pattern fails");
this category extends the same tense discipline to every sentence.

**Tense: past only for what the reader watched.**
Future drift announces itself with "will";
past drift has no marker,
because a past verb reads as reportage rather than as distance.
Decide it one verb at a time, with a single test:
can you point at the run, the listing, or the release where this happened?
If not, the verb reports standing behavior, and standing behavior takes the present:

- "the subclass inherited hundreds it never wrote"
  becomes "the subclass inherits hundreds it didn't write"
- "A frozen dataclass rejected assignment to every field"
  becomes "A frozen dataclass rejects assignment to every field"

A generic subject settles most cases.
"The subclass", "a caller", "the checker" names a category,
so the verb names what always happens;
the past re-scopes the claim to one occasion
and sends the reader looking for the occasion.
Next to a present-tense clause it also invents a chronology:
"You forward every operation by hand,
where the subclass inherited hundreds"
reads as a sequence, when the two are competing alternatives.

One exception: a verb still backshifts inside a present-tense sentence
when it reports an act finished before now,
so "hundreds it didn't write" is correct, since someone else wrote them earlier.
Otherwise a general statement stays generic throughout.
That same sentence ended "and got one wrong" in a draft,
pointing at the failure the reader watched in the `CountingList` listing.
Defensible in isolation, wrong there:
the sentence states a rule about two designs, not an incident,
and once a sentence states the rule, every verb in it states the rule.
Reserve the past for sentences that point at the listing.
A retrospective closing section ("In every case the observer was a callable")
narrates the chapter the reader just finished, and stays past.

**One word in the present indicative.**
The future and past rules are two cases of a wider one:
a present-tense verb should be one word
unless the extra words carry meaning.
Two more padded forms recur.

*Modal plus infinitive where the fact is categorical.*
"Can" under a negative is the usual shape,
stating impossibility through a permission verb:

- "nothing can slip past the counter" becomes "nothing slips past the counter"
- "the checker can report the mismatch" becomes "the checker reports the mismatch"

Keep the modal where the possibility is the point
("a subclass can override this, and most do not").

*Progressive where the simple present says it.*
"Is/are" plus *-ing* frames a timeless fact as an activity underway:

- "in the class you are reading" becomes "in the class you read"
- "the loop is iterating over a copy" becomes "the loop iterates over a copy"

Keep the progressive for something genuinely mid-flight,
usually set against a second event
("the generator is still suspended when the caller returns").

The watch list already flags "never".
A past-tense absolute is often why the word appeared,
so fixing the tense removes it for free,
the way fixing a nominalization removes "happen".
Check the same sentence for a partitive that restates its own antecedent:
"got one of them wrong" is "got one wrong".

**Narrated mechanism.**
The prose-level twin of the deep-review skill's
mechanism-vs-outcome lens:
an outcome sentence reports a result,
an in-the-moment sentence lets the reader watch it unfold.
When prose walks a listing,
narrate the execution in order, in the present tense,
tracking state as it changes:

- Outcome: "Caching makes the second call fast."
- In the moment: "The first call misses the cache and computes the value;
  the second finds the entry and returns it without computing anything."

Sequence markers ("then", "now", "at this point the list holds three items")
keep the reader's position in the run explicit.
This category adds sentences rather than trimming them,
so apply it where the surrounding prose already walks the code
and the walk skips a step;
inventing a full walkthrough where none exists
is a teaching addition for a deep review, not this pass.

## Boundaries

- **Bruce's em-dashes stay.** Rewriting a sentence around one is fine;
  deleting or replacing the dash is not.
- **Check the exemption records first.**
  `readability_db.md` and `deep_review_db.md` in the repo root
  carry standing exemptions: prose that reads as a violation on purpose.
  A construction recorded there is settled; leave it.
- **Cohesion can outrank activation.**
  Williams pairs characters-and-actions with given-before-new:
  old information in the subject, news at the end.
  A passive that keeps the running topic in subject position is correct:
  "the interpreter compiles the source to bytecode;
  the bytecode is then executed on a stack machine"
  keeps "bytecode" as the topic,
  and fronting the interpreter again would derail the paragraph.
  The end of the sentence is the stress position,
  which is also why a stranded preposition reads badly:
  it spends the emphasis on a function word.
  When activation and cohesion conflict, cohesion wins;
  record the kept passive in the report.
- **Parallel structure can call for a passive.**
  Cohesion is one reason to keep one, matching subjects across a contrast another.
  "You forward every operation callers need by hand,
  where the subclass inherited hundreds it never wrote"
  became "Every operation is forwarded by hand,
  the subclass inherits hundreds it didn't write".
  The passive demotes a generic "you" who is no character in that paragraph,
  and puts a count of methods in subject position on both sides,
  so the sentence weighs "every operation" against "hundreds"
  instead of weighing a person against a class.
  Dropping the connective "where" belongs to the same move:
  two short parallel clauses carry a contrast by juxtaposition,
  and the connective only announces what the parallelism shows.
  This is a reason to write a passive, so it needs a real contrast to justify it,
  not a preference for the shorter sentence.
- **Definitions keep their "is."**
  "A closure is a function that captures variables from its enclosing scope"
  is an identity statement, and stative "is" is its verb.
  Do not force a dynamic verb into a definition.
- **An active verb must be literal.**
  The verb names what the machinery does:
  looks up, copies, binds, evaluates, raises an exception.
  Never trade a passive for a watch-list metaphor;
  "the check lands before the loop" is not an activation,
  it is a new violation.
- **Headings have their own rule** (see the
  `heading-style-infinitive-over-modal` project memory):
  infinitive or noun phrase, not a modal clause,
  so "A Value You Must Check Everywhere" became "A Value to Check Everywhere".
  A renamed heading changes its pandoc anchor;
  grep all of `Chapters/` for the old slug and update every cross-reference.
  `heading_links.py` (in `make verify`) catches a missed one.
- **Meaning outranks activeness.**
  If the active rewrite says more than the original claimed
  (a hedged "can cause" that really is conditional, for example),
  keep the original.

## Verify and report

Touched prose gets `make reflow CH=NN` (Semantic Line Breaks),
then `make verify`, then read `git diff Chapters/`:
a changed `#:` marker means an edit strayed into code, so investigate it.
Re-run `make prose CH=NN` and confirm the Passive/ThereIs count dropped;
list any warning deliberately kept, with its reason.
Bruce reviews the diff and commits himself.

## Accrued patterns

Phrasings Bruce has flagged, usually as passive-feeling or padded,
that the categories above do not name yet. When he identifies a new one,
add it here as a bullet with a before/after pair,
and it becomes part of every future pass.

- "the count would be wrong again" becomes "the count would still be wrong".
  "Again" implies a history (wrong, fixed, wrong once more);
  "still" makes the logical claim, that the fix left the condition in place.
  Prefer the word naming the relation over the word implying a timeline.
- "rather than in `list` internals" becomes "not in `list` internals".
  Where a colon or a preceding clause already marks the contrast,
  "rather than" is a three-syllable "not".
- "every operation callers need" becomes "every operation".
  A restrictive qualifier the reader supplies anyway
  costs two words and narrows nothing.
- "the `class` statement raises instead of finishing" becomes
  "the `class` statement raises a `TypeError` instead of finishing".
  "Raises" always takes an object: name the exception,
  or at least "an exception".
  A naked "raises" ("returns or raises", "this one raises instead")
  leaves the verb dangling.
  A relative clause with the object in front ("the exception it raises",
  "whatever `slope()` raises") is already complete.
