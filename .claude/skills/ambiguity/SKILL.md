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
and named the unit ("All three generators end `GEN_CLOSED`").

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
- `tip sentence-shapes CH=NN ARGS=--survey`: `[SAME]`, `[PAIR]`, `[TWO]`, and `[AND+REL]`.
- `tip possessives CH=NN` and `tip stranded CH=NN`: an elided head noun, which the reader supplies from two candidates.
- `tip pointers CH=NN`: `antecedents` reads these; take only what that pass left.

## Where a sentence gets two readings

**A count with two units.**
An ordinal, a cardinal, or a quantifier on an execution noun: run, pass, attempt, round, call, time, step, case, iteration.
A listing offers several things to count:
its top-level driver calls, its tagged lines, its generators or objects, its printed lines, the repetitions inside one call.
Test: count the unit each way the listing allows; if the counts differ, the sentence is ambiguous.
Fix: name the unit ("all three generators", "the second `run()` call", "three repetitions of `save_user()`"), or cite the tags.
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
"old tests and docs", "leaves its send and return channels at `None`", "a handler or a driver and a generator".
Test: bracket the "and" or "or" each way.
Fix: repeat the shared word ("old tests and old docs"), move the shared word to the end, or split.

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
"while" (during, or whereas), "then" (next, or therefore), "when" (whenever, or at the moment).
Test: substitute each sense.
Fix: the connective with one sense ("after", "because", "during", "whereas", "one time").

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
