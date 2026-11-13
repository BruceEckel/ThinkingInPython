---
name: ambiguity
description: Find and fix sentences that have two readings. A count or ordinal the listing offers two ways to count ("the first three runs"), a word carrying two senses in one passage ("run", "state", "call"), a modifier or relative clause that can attach to two heads, a coordination or a negation whose scope is open, a definite noun the listing has several of ("the `yield`"), a comparison or an ellipsis missing its second term, a connective with two senses ("once", "since", "as"). Each candidate is tested against the listing and rewritten so only the true reading survives. Use when asked to disambiguate a chapter, remove its ambiguities, or find double readings (or the book's). The argument names chapters by number or name, optionally followed by `section "<heading>"`; no argument means all of Chapters/.
---

# Ambiguity: one reading per sentence

An ambiguous sentence is grammatical, true under one of its readings,
and invisible to every gate.
The reader who has the listing in view picks a reading,
and when the listing supports the other one the sentence is false for that reader.
The case that started this pass (chapter 45, 2026-11-04):
"In the first three runs the exception arrives in place of a value"
stood after `throw_close_basics.py`, a listing with three `g = worker()` generators and four tagged resumptions.
The writer counted the tags, and under that count the sentence was true.
The chapter counts generators everywhere else ("In the second run, `drive()` sees two requests"),
and under that count "the first three runs" meant all three, including the one that gets no exception.
The section's last sentence, "Every run leaves the generator `GEN_CLOSED`",
was true under the generator count alone.
The fixes cited the tags ("At `[1]`, `[2]`, and `[3]` the exception arrives in place of a value")
and named the unit ("All three generators end in `GEN_CLOSED`").

The other prose passes each own one species of this fault.
`antecedents` owns pronouns and stand-in nouns.
`tip positional` owns a pointer at a listing line.
`straighten` owns a sentence whose subject is held open.
The `[SAME]` survey rule owns a "same" with nothing compared.
This pass owns the rest, and it runs the one test below over every sentence that counts, compares, coordinates, modifies, or limits.
It edits `Chapters/NN_*.md` prose only;
code blocks, `#:` output markers, headings, and quoted material stay untouched.
Given a `Solutions/<chapter>/README.md`, it edits that file's prose the same way,
except the block quote under each `## N.` heading, which `tip statements` copies from the chapter;
an ambiguity there is fixed in the chapter's exercise.

## The test

1. Read the sentence as a reader who has the listing above it and the paragraph before it, and nothing else.
   The writer's intention is not available to that reader.
2. Write down each reading.
   If no second reading comes, move on.
3. Check the listing for which reading is true.
   Count what the sentence counts; run the listing from `build/examples` under `uv run` when the claim needs it.
4. If the readings agree, leave the sentence.
   If one reading is false, or the two differ, rewrite so only the true one survives:
   name the unit, move the modifier beside its head, repeat the shared word, place the limiter, supply the missing term.

The rewrite is a more specific word that the passage or the listing already uses,
never a parenthesis that explains which reading was meant
and never a hedge.

## Mechanical candidates

Run these first and keep the hits inside the scope.
Each line is a candidate, and the test decides;
most of the book's hits read one way.

- `tip positional CH=NN ARGS=--survey`: `count+unit` is a count on an execution noun (run, round, attempt, pass, resumption, trace, exchange),
  the `survey count+unit` lines are the same shape on `call` and `time`,
  and `construct xN` and `ordinal+span` are definite or ordinal pointers at a listing that has several of the thing.
  `survey alternative` (2026-11-08) is a sentence in a walkthrough paragraph that names a construct the listing lacks, with no marker word;
  it sees the opener of an alternative, and the continuation shape below is read by hand.
- `tip sentence-shapes CH=NN ARGS=--survey`: `[SAME]`, `[SAME+NEW]`, `[PAIR]`, `[TWO]`, `[AND+REL]`, and `[REL+AND]`.
  `[REL+AND]` (2026-11-11) is a relative clause that ends on its verb directly before a conjunction and a second verb; it has no judged list, so every hit prints.
  `[SAME+NEW]` (2026-11-09) is a "same" on a noun that no line in the 30 above uses, and it prints the noun (`[SAME+NEW] separation: ...`);
  ask "same as what?" and check that the passage called the thing by that noun.
  The survey prints only the `[SAME]`, `[SAME+NEW]`, and `[TWO]` hits not yet judged and ends on `K survey, J judged` (`[ADD]` is judged the same way; `[PAIR]` and `[AND+REL]` are default rules with the ordinary baseline).
  After the read, `tip sentence-shapes CH=NN ARGS=--survey-accept` records the keeps in `tools/data/sentence_shapes_survey_baseline.txt`.
  The accept takes in every unjudged hit in the chapter and its Solutions file, so a pass over one section reads the rest of that list first.
- `tip possessives CH=NN` and `tip stranded CH=NN`: an elided head noun, which the reader supplies from two candidates.
- `tip pointers CH=NN`: `antecedents` reads these; take only what that pass left.

## Where a sentence gets two readings

**A count with two units.**
An ordinal, a cardinal, or a quantifier on an execution noun: run, pass, attempt, round, call, time, step, case, iteration.
A listing offers several things to count:
its top-level driver calls, its tagged lines, its generators or objects, its printed lines, the repetitions inside one call.
Test: count the unit each way the listing allows; if the counts differ, the sentence is ambiguous.
Fix: name the unit ("all three generators", "the second `run()` call", "three repetitions of `save_user()`"), or cite the tags.
An ordinal has the same fault when the listing offers two orders:
"finishes when the last generator beneath it finishes" (the last to finish, or the lowest in the chain?)
became "finishes when every generator beneath it has finished".
Chapter 47 said "The same schedule that governed three attempts now governs three runs"
after pages where "run" counted `run()` calls, over a listing with one `run()`;
the repair names the repeated function.

**One word, two senses in one passage.**
A word the code uses as a name and the prose uses as an ordinary word:
"run" (Stateless's `run()` and executing), "state" (the *State* pattern and a generator's state),
"call" (a call expression and the act of calling), "yield" (the keyword and the handing over),
"driver", "handler", "return", "pass", "answer".
Test: does the passage use the word in both senses within a few sentences?
Fix: keep the word for the sense the code gives it and choose another for the other sense ("executes", "a resumption", "the machine's position").
The italic pattern-name rule already separates *State* from state.

**A modifier with two heads.**
A prepositional phrase, a participle, or a relative clause that can attach to two nouns or to a noun and a verb:
"the value of the generator that finished" (the value finished, or the generator?),
"resumes the generator with `send()` twice" (two resumptions, or two `send()` calls?),
"prints the name in the handler" (prints inside the handler, or the name stored there?).
Test: attach the modifier to each head and read each result.
Fix: move the modifier next to its head, or split the sentence so each head keeps its own.

**A coordination with open scope.**
"old tests and docs", "a handler or a driver and a generator".
Test: bracket the "and" or "or" each way.
Fix: repeat the shared word ("old tests and old docs"), move the shared word to the end, or split.
The verb form of this shape is a relative clause that ends on its verb directly before the conjunction:
"The driver holds the generator `outer()` returned and calls `throw()` on it" (does `outer()` call, or the driver?).
The clause's verb and the main clause's second verb sit on either side of "and", so the reader joins them under the clause's subject.
A code-span subject and a dropped "that" make it worse, since nothing marks where the clause starts.
Fix: give the second verb its own sentence, move the relative clause to the end of its sentence,
or replace the clause with the name the listing gives the thing ("The driver calls `g.throw()`").
Use the name with no sentence to introduce it: "`g` is `outer()`'s generator" reads the listing's `g = outer()` aloud, and R47 cuts it.
`tip sentence-shapes CH=NN ARGS=--survey` lists it as `[REL+AND]`; about half its hits are a real coordination inside the clause ("one value that every instance reads and writes"), which stays.
A second verb form is a shared object that arrives after the second verb, when the first verb also reads with no object:
"A driver that holds the outermost generator stops and cleans up every generator beneath it" (the driver stops?).
Test: cover the sentence from the conjunction on. If what is left is a complete sentence, the reader has taken it as the claim.
Fix: give the first verb its object at once, with the thing that acts as the subject
("One `close()` call on the outermost generator stops that generator and every generator beneath it, and each one runs its cleanup").
The keeps are a first verb meant with no object ("the script runs and prints") and a set pair ("opens and closes a file"). C60 in `bruce_edit_db.md`.

**A negation or a limiter with open scope.**
"every driver does not answer", "all generators are not closed",
and "only", which limits whatever it stands next to:
"the first `send()` accepts only `None`" and "only the first `send()` accepts `None`" are different claims.
Test: say what the "not" or "only" limits under each placement.
Fix: put the limiter directly before the word it limits,
and prefer the positive statement (the `positive` pass's territory when a paragraph is full of them).

**A definite noun the listing has several of.**
"the `yield`" over a body with two, "the generator" when two are live, "the exception" when two are raised, "the handler", "the loop".
`tip positional`'s `construct` rule lists the keyword cases; this covers nouns and names.
Test: count that thing in the listing.
Fix: the detail that identifies it (`yield "recovered"`, "the inner generator", "the `TypeError`"), or a `[n]` tag.

**A comparison or an ellipsis missing its term.**
"runs faster", "the same way", "does too", "likewise", "the second does as well", "twice as much",
and "the other" far from its pair.
Test: supply the missing term; if two candidates fit, the sentence is ambiguous.
Fix: write the term.

**A connective with two senses.**
"once" (one time, or as soon as), "since" (because, or from the time), "as" (while, or because),
"while" (during, or whereas), "then" (next, or therefore), "when" (whenever, or at the moment),
"however" (nevertheless, or no matter how: "stays with its target until that generator finishes, however many `next()` calls that takes" reads as a contrast until "many" arrives; chapter 45, 2026-11-08).
Test: substitute each sense.
Fix: the connective with one sense ("after", "because", "during", "whereas", "one time").
For the concessive "however", a universal over a count or a manner, state the independence or name the range
("as `n` grows", "at any depth of delegation", "whether the block completed or raised an exception", "whether you then take 100 items or one"),
or drop the clause where the verb already says the thing holds still; rule R58 in `bruce_edit_db.md`.
`tip watch-words CH=NN` lists it as Tier 2 and skips the contrastive "However," with its comma.

**An alternative in the walkthrough's register.**
A paragraph narrates the listing, and a sentence in it says what a construct the listing lacks does, in the plain present with no marker:
"A `for` loop treats `StopIteration` as the normal end of the loop, so it discards the exception" under a listing whose driver is a `try` statement (chapter 45, 2026-11-08).
Two readings: the listing's next step, or the road not taken.
The second sentence of an alternative is the usual site:
the opener is framed ("Writing the fix as `type(self).total += 1`", "An `__init__()` that assigns `_value_`")
and the continuation is bare ("`C().show()` then runs `B`'s version", "The lookup table then stays keyed by the tuples"),
and the bare sentence often contradicts the listing's `#:` output.
Test: is the sentence true of the listing on the page? If not, does a word in it, or an earlier sentence of the paragraph, say so?
Fix: the lightest frame that carries over: what it replaces ("With a `return` at the match in place of the `break` at `[1]`"),
a condition ("If `__init__()` assigns `_value_`"), "In that version", a gerund subject, or a tie to the listing's choice ("because a `for` loop would discard the exception").
Keep a general fact that holds for the listing too, and a continuation whose opener in the same paragraph is a real conditional.
Rule R57 in `bruce_edit_db.md`; the `alternative` pass (`.claude/skills/alternative/SKILL.md`) owns the paragraph-by-paragraph read, so this pass takes only the sentence it meets while testing for a second reading.

## Boundaries

- **Readings that agree mean no change.**
  The goal is one reading per sentence, not a noun repeated in every sentence.
- **A reading no reader with the listing can take is not a reading.**
  The test is the reader in step 1, not a parser.
- **No gloss, no hedge.**
  The fix is a word the passage or the listing already uses.
  If no such word exists, the sentence has a different problem; note it in the report.
- **Every claim a rewrite makes is checked against the listing first.**
  The 2026-09-01 sweep found nine factual errors in rewrites that skipped this.
- **Pronouns go to `antecedents`, listing lines to a `[n]` tag, a held subject to `straighten`, a dense paragraph of negatives to `positive`.**
- **Quoted diagnostics, headings, Bruce's "we", and his em-dashes stay.**

## Working a chapter

1. Run the mechanical candidates and keep those inside the scope.
2. Read each listing's prose region with the listing in view,
   and apply the test to every sentence that counts, compares, coordinates, modifies, or limits.
3. For a count or a definite noun, count in the listing; for a claim, run the listing.
4. `uv run tip verify-ch CH=NN`, then `uv run tip prose CH=NN`:
   read each `NEW` and `stale` pair, fix or accept with the scoped `tip <check>-accept CH=NN`,
   read `git diff Chapters/` for a changed `#:` marker, and commit the chapter with its baseline files in one commit.

## Report

One line per rewrite: the sentence before and after, the two readings, and which one the listing supports.
List the candidates read and kept, each with its single reading.
Name the shapes that found nothing.

## Accrued shapes

Shapes Bruce flags that the catalog above did not name, dated, with the sentence.

- 2026-11-04, chapter 45: a count with two units.
  "In the first three runs the exception arrives in place of a value", over three generators and four tags.
  Added as the first shape and as `tip positional`'s `count+unit` rule.
- 2026-11-08, chapter 45: an alternative in the walkthrough's register.
  "A `for` loop treats `StopIteration` as the normal end of the loop, so it discards the exception and loses the return value", under `drive_by_hand.py`, whose driver is a `try` statement.
  Added to the catalog, as R57, and as `tip positional`'s `survey alternative` rule;
  the book-wide read that day (brief in `build/alt-2026-11-08/`) found most hits in the second sentence of an alternative, where the opener's frame had lapsed.
- 2026-11-08, chapter 45: a concessive "however" read as the contrastive adverb.
  "each `yield from` stays with its target until that generator finishes, however many `next()` calls that takes" (Bruce: "unclear usage of 'however'").
  Added to the connective entry above, as R58, and as a Tier 2 watch word; the book sweep that day rewrote all 39 concessive sites.
- 2026-11-09, chapter 45: "the same X" with its second term unnamed.
  "`close()` raises the same `RuntimeError`, `generator ignored GeneratorExit`" (Bruce: "same as what").
  The second term was the run of `stubborn()` in the listing above, and the message after the noun read as the term.
  At every "the same X", ask "same as what?" with the sentence, the one before it, and the adjacent listing in view.
  Rewrite when two candidates fit, when the term is further away than that, when a phrase after the noun poses as the term, or when nothing is compared:
  "`close()` raises a `RuntimeError` with the message shown for `stubborn()`".
  Keep a term in the sentence, a single adjacent candidate, and the idioms. Rule R63 in `bruce_edit_db.md`; the `[SAME]` survey lists only the nothing-compared shape, so read every "same" in the scope.
  The read of the 42 close calls that day added two tests.
  Was the noun after "same" introduced? "The same separation", "the same hazard", and "the same machinery" each named a thing the passage had described and never called that, so the repair says what the thing is.
  Are the two things the same? "The same `Queue`" stood beside a listing that uses a `PriorityQueue`, and "the same guard" joined two different `isinstance()` tests; check the claim against the listing as for any other claim.
  Two repairs joined the list: where the thing is no longer than the pointer, write the thing ("with `metaclass=Singleton`"), and where the second term is the sentence's own "each" or "every", put it before an appositive ("makes the same call on each element, `element.accept(visitor)`").
  The first test became the `[SAME+NEW]` survey rule the same day. Its first run had 117 hits and 20 rewrites, most of them a second noun for a thing the passage had named:
  "the same generic caretaker" for `History`, "the same question" for a request, "the same model" one sentence after "this design", "the same guarantee" one sentence after "the rule".
  Use the passage's noun. The keeps are a summary noun for the sentence before ("Gradual typing faced the same problem").
  The 96 keeps of that run are in the rule's baseline, so a pass reads only a sentence written or edited since.
  `[SAME]` joined that baseline the same day, after a reread of its 143 hits in context: 139 kept, 4 rewritten.
  Three of the 4 were the first test again, in places `[SAME+NEW]` is quiet by design, so the read still applies it by hand.
  A command is quiet: "Add `ContextDecorator` only when the same bracket should also wrap whole functions", one sentence after "one setup, one teardown", is now "the same setup and teardown".
  A cognate in another sense inside the 30 lines is quiet too: "moves the same declaration" under "Declaring that a design should have low coupling" is now "moves that description", after "It describes what a caller needs";
  "makes the same substitution" under a quoted "Liskov Substitution Principle" is now "does the same".
  So is "the same shape", a quiet noun: check that the sentence before or after says what the shape is.
  The fourth was the second test: "The weapon ranking is a cycle. ... The same cycle appears at the group level" named a second, different cycle, and is now "A second cycle appears at the group level".
- 2026-11-11, chapter 45: a relative clause's verb, a conjunction, and the main clause's second verb.
  "The driver holds the generator `outer()` returned and calls `throw()` on it" (Bruce: "jumbled").
  The catalog's coordination entry showed nouns only, `[AND]` needs two subjects, and `[AND+REL]` needs a comma and a second subject, so no pass and no tool saw it.
  Added to the coordination entry above, as C59, and as the `[REL+AND]` survey rule; the first book-wide run had 19 hits and 10 rewrites.
- 2026-11-12, chapter 45: a verb that reads with or without an object, a conjunction, a second verb, and then the object both share.
  "A driver that holds the outermost generator stops and cleans up every generator beneath it with one call" (Bruce: "it sounds like the driver stops").
  `[REL+AND]` is quiet because the relative clause ends on a noun, and that noun before "stops" gives a second false clause, "the outermost generator stops".
  Added to the coordination entry above and as C60. No tool lists it: grep the scope for
  `\b(stop|start|end|run|close|open|resume|return|finish|move|change|fail)e?s? (and|or|then) \w+` and apply the cover test to each line.
  The grep of both trees that day had about 55 lines and this one site.
- 2026-11-12, chapter 45: a modifier that narrows a true claim.
  "`copy.deepcopy()` and `pickle` both raise a `TypeError` on a suspended generator" (Bruce: "because a suspended generator cannot be copied? can a generator in any state be copied?").
  The reader takes "suspended" as the boundary of the claim and infers that an unstarted or finished generator copies.
  A probe showed the same `TypeError` for a generator in every state, so the modifier was the case the writer had in mind, not a condition.
  The repair states the full range, then the fact that puts the passage's case in the range, then the consequence:
  "raise a `TypeError` for every generator, started or not. A machine in this design is a generator, so a program cannot copy it or save it."
  The first repair ended "so a program cannot copy or save a machine that is paused in a state" and drew the same question
  (Bruce: "Only a Machine, or any generator? If it's not paused can it be copied?"): the modifier had moved to the consequence.
  Apply the test to the repair before the commit.
  For each restricting adjective or participle on the object of a claim about what Python does (suspended, started, frozen, empty, nested, async), run the claim on the other case.
  Keep the modifier when the other case differs, and say how. The claim check passes these sentences because they are true. C70 in `bruce_edit_db.md`.
- 2026-11-13, chapter 45: a trailing appositive after "X starts Y".
  "`asyncio.run()` starts the `asyncio` event loop, a driver like
  `task_runner()`" (Bruce: "is run() or the event loop the driver?").
  A noun phrase after a comma can rename the object beside it or
  sum up the whole clause, so a role noun there has two candidates:
  the subject that acts and the object it acts on. The appositive
  gets a sentence with its own subject: "`asyncio.run()` starts the
  `asyncio` event loop. The event loop is a driver like
  `task_runner()`". Where the role is split between two parts, say
  so ("with the work divided between the loop and its tasks") and
  keep the role verb for one of them ("each task resumes one
  coroutine", not "drives", C67).
  Grep the scope for `, an? \w+ (like|that|which|for)` after a verb
  with a code-span subject and object.
