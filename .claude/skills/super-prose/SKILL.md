---
name: super-prose
description: Run every prose pass over a chapter or one section of it, in order, and commit the result. The eleven passes are literal, positive, straighten, cohesion, antecedents, ambiguity, activate, bruce-edit-apply, elements-of-style, alternative, and stutter, each read from its own SKILL.md and applied in one read of the prose. Use when asked for "all the prose passes", "the prose reviews and corrections", or "/super-prose" on a chapter or a section. The argument names the chapter by number or name, optionally followed by `section "<heading>"`; no argument means the chapter whose editing pass is open.
---

# Super-prose: the eleven prose passes as one request

`/super-prose 45` or `/super-prose 45 section "The Driver's Exception Channel"`
means: apply every prose pass the project defines, over that scope,
in the order below, in one session, and commit.
It is the in-session form of `tip rewrite CH=NN`, which runs the
passes headless, one model call per pass, over a whole chapter.
This form keeps the conversation's context (what Bruce has already
ruled on, the listing just edited) and can scope to one section,
which `tip rewrite` cannot.

## The order

Load all eleven skills with the `Skill` tool before touching the
prose, then read the scope once and apply them together.
The order is the order the skills' own boundary notes give:
each pass hands the next one less to do.

1. `literal`: a figure or a vague description becomes the mechanism.
   A part one design has and another lacks does not "disappear",
   "vanish", or "go away": say which construct in this design does
   its job ("the machine object disappears" -> "parameters and locals
   hold the data that `VendingMachine` keeps in attributes", C68).
   Grep the scope for `disappear`, `vanish`, `goes away`, and `gone`.
   A clause credited with an action gets the statement test: find
   the statement in the listing that performs the verb. An `except`
   whose body is `pass` drops nothing; the job is missing from
   `ready` because the exception skipped a statement ("The `except`
   catches the `StopIteration` from a job ... and drops that job" ->
   "`next(job)` raises `StopIteration` ... before `append()` runs,
   and that job stays out of `ready`", C73). The exception comes from
   the call that raises it (`next(job)`), not from the object. A
   thing that "leaves" or "drops out of" a container is the same
   shape: a statement removed it ("the job leaves `ready`" ->
   "`popleft()` has already removed that job from `ready`"). Grep
   the scope for `except`, `pass`, `continue`, and `leaves?` and
   read each sentence against its line.
2. `positive`: a negation that is an accident of phrasing turns around.
   A subject of "Nothing", "Nobody", or "No one" with a verb ("Nothing
   calls `throw()` on the first booking" -> "`list(book())` drives the
   steps with `next()`") is Tier 2 in `tip watch-words`, C61:
   say who acts and what they do, and do not trade it for the object
   form ("receives no `throw()`"). A limiter added to the positive
   sentence ("with `next()` alone", "only", "just", "nothing but")
   puts the negation back: it tells the reader an alternative is
   excluded and leaves them to find it. Cut the limiter when the
   passage has not yet named the alternative, or names it in the
   next sentence (C62). The test for each "only" and "alone" is
   deletion: read the sentence without the word. If the passage
   still says what it needs, or the next sentence supplies the
   contrast, the word goes ("an `undo` body starts only at `[1]`",
   followed by "The successful run finishes without reaching `[1]`",
   is "starts at `[1]`"). It stays when the reader would otherwise
   assume the excluded case ("the first `send()` accepts only
   `None`"). `tip watch-words CH=NN ARGS="--tier 1"` lists every
   `only`, `tip negatives CH=NN` counts them per paragraph, and
   `tip overclaims CH=NN` lists "X alone". Read the list for the
   scope, since both words are also what Claude reaches for when it
   turns a negative sentence positive. A thing named by "with no" and
   a construct elsewhere in the listing that would match or handle it
   ("An input with no `case` leaves the state's `while` loop
   running") gets the positive case first and then "any other", and
   the construct that produces the behavior becomes a subject, named
   as the listing writes it ("Each state's `while True` loop keeps
   the machine in that state. An input that matches a `case` returns
   the next state ... After any other input, the loop runs its
   `yield` again", C66). No tool lists it: grep the scope for
   `with no` and keep a property of the thing itself ("a function
   with no parameters").
3. `straighten`: a buried actor, a subject held open, an overloaded
   sentence, a colon or "and" carrying a second claim. A subject
   whose relative clause puts its object first sets two noun phrases
   side by side before any verb ("A machine whose states a test must
   enumerate belongs in chapter 31's table"); the clause is a
   condition, so write it as one ("If a test must enumerate a
   machine's states, use chapter 31's `Enum` design", C69).
   `tip subject-gap` misses it, since the gap is short: grep the
   scope for `whose` and read each clause for the order of its
   subject and object. The form with no pronoun counts too, anywhere
   in the sentence ("keep the state in a value a record can hold"
   -> "the current state is an `Enum` member, which a *Memento* can
   store in a field"): read for a noun followed directly by "a" or
   "the" and a second noun, and name the things the stand-in nouns
   ("value", "record", "object") point at.
4. `cohesion`: old before new, one topic string per paragraph, R29's
   one primary concept per paragraph. A paragraph that likens a real
   system to an earlier listing ("a driver like the one in
   `task_runner_send.py`") names the system (`asyncio`'s event
   loop), states each fact before the sentence that uses it, and
   maps the listing's words onto the system's parts ("The `Future`
   is the request, and its result is the reply") before using them
   ("answers the request each task yields" came two sentences before
   anything said a coroutine yields, C74). Grep the scope for
   `like the`, `as in`, and `the same as` beside a listing name. Two seams to read for in every
   walkthrough: a sentence after the paragraph's concluding sentence
   ("The nesting of the `try` blocks is the undo stack." followed by
   "The second booking receives no `throw()`, ..."), and a sentence
   that walks another run of the listing (a second object, the
   success case after the failure case). Each starts a paragraph,
   even at one sentence. A sentence written for a statement the
   listing gained is placed by this test, never appended to the
   paragraph already there. A "then" in a walkthrough that already
   narrates in order is read without the word and cut when the order
   survives ("The bare `raise` then re-raises" -> "The bare `raise`
   re-raises", C65); no tool lists it, so grep the scope for `then`.
   A third seam is a listing that leaves the section's running
   example: new names (`tick()`, `tock()` after two listings about
   the mousetrap) under a lead-in that names neither the example nor
   the question ("One shape looks like a transition and is a
   delegation:"). The lead-in is rewritten from the running example:
   what that example does, the alternative or question the listing
   takes up, and the new names as an instance of it ("In
   `trap_generators.py`, a state returns the next state ... The
   alternative is for each state to delegate to the next state
   itself ... `tick()` and `tock()` are two states written that
   way:", C71). For each listing in the scope, compare its names
   with the listing before it; when none carry over, read the
   lead-in for the tie.
5. `antecedents`: every pointer with two candidates gets its noun.
   A link is a pointer too: when its target teaches a named
   construct, the link text starts on the name ("The bare `raise`
   then [re-raises the exception the clause caught](...)" -> "The
   [bare `raise` re-raises the exception the clause caught](...)",
   C64). Read each link in the scope for where its brackets sit.
   One role, one name: a thing called "the engine" in one sentence
   and "such a driver" in the next reads as two things
   ("`trampoline()` is the engine, the loop at `[1]`. PEP 342 calls
   such a driver a *trampoline*" -> "The loop at `[1]` is the whole
   engine. PEP 342 calls such a loop a *trampoline*", C67). For each
   function the scope walks, list the role nouns the prose gives it
   (driver, engine, handler, proxy, loop, wrapper); two nouns for one
   function is a hit, and a noun the chapter defined goes only to a
   thing that fits the definition. The noun after "such a", "this",
   or "that" is one the passage has used for that thing.
6. `ambiguity`: every sentence that counts, compares, coordinates,
   modifies, or limits keeps one reading. A list of what two things
   share ("has `send()`, `throw()`, and `close()`, as a generator
   does") is counted against what the chapter taught the first
   thing to have; for a member left out, probe the second thing and
   say what it does ("It is not an iterator, so `next()` on a
   coroutine object raises a `TypeError`", C75). A trailing
   appositive with a role noun ("starts the event loop, a driver
   like ...") gets a sentence with its own subject (C67). A modifier that narrows a
   true claim tells the reader the other cases differ ("raise a
   `TypeError` on a suspended generator", Bruce: "can a generator in
   any state be copied?"): run the claim with the modifier removed,
   and if it still holds, state the full range and then the case the
   passage cares about, joined by the fact that puts the case in the
   range ("for every generator, started or not. A machine in this
   design is a generator, so a program cannot copy it or save it",
   C70). Test the repair too: the first repair of that sentence
   ended "a machine that is paused in a state" and drew the same
   question. The claim check passes such a sentence, since it is
   true. The other shapes: a count with two units, a
   word with two senses, a modifier with two heads, an open scope, a
   definite noun the listing has several of, a missing comparand,
   and a verb that reads with or without an object set before "and"
   and a second verb, with the object both share after the second
   ("A driver that holds the outermost generator stops and cleans up
   every generator beneath it" -> "One `close()` call on the
   outermost generator stops that generator and every generator
   beneath it, and each one runs its cleanup", C60). Cover the
   sentence from the conjunction on: if what is left is a complete
   sentence, the reader has taken it as the claim. No survey tool
   lists that shape: grep the scope for
   `\b(stop|start|end|run|close|open|resume|return|finish|move|change|fail)e?s? (and|or|then) \w+`
   and read each line; a first verb meant with no object ("the
   script runs and prints") and a set pair ("opens and closes a
   file") stay.
7. `activate`: passives with a natural actor, nominalizations,
   metadiscourse, empty frames, tense drift (a relative-clause past
   in a sentence about standing behavior included: "the value that
   `send()` delivered" -> "delivers", C63), and a verb of rest with
   nothing after it ("the generator that is waiting" -> "the generator
   paused at the innermost `yield`", C58). An "I" or "we" as the
   actor in a listing walkthrough is the author standing where the
   code's actor belongs ("lists `Ask` and `Tell` because I typed
   them" -> "because its annotation declares them", C72): grep the
   scope for `\bI\b` and `\b[Ww]e\b` outside code spans and give the
   verb to the annotation, the function, or "the programmer"; an
   opinion or the author's history ("I find", "what I call") stays.
   No survey tool lists the verb-of-rest
   shape: grep the scope for `wait`, `pending`, `idle`, `suspended`,
   `paused`, `sits`, `stays`, `remains`, and `holds`, and read each
   for its place or its event, and for its subject: the thing that
   rests gets the verb ("a state that stays" is "the machine stays
   in `Waiting`"). A walkthrough sentence "the run shows a NOUN that
   VERBs" becomes the call, its input, and the output line ("The
   listing's second run shows a state that stays" -> "At `[5]`,
   `run_all()` sends `Mouse.ESCAPES` to a machine in `Waiting`");
   grep the scope for `shows` and `demonstrates` with a run, a call,
   or a listing as the subject.
8. `bruce-edit-apply`: the Rules section of `bruce_edit_db.md`.
9. `elements-of-style:writing-clearly-and-concisely`: Strunk's rules,
   mostly needless words and emphatic words at the end.
10. `alternative`: a sentence in a listing walkthrough that describes
    the road not taken in the walkthrough's own register ("A `for`
    loop treats `StopIteration` as the normal end of the loop" under
    a `try`-driven listing; "`C().show()` then runs `B`'s version"
    after a framed opener) gets the lightest frame that carries over
    ("In that version", "If `__init__()` assigns `_value_`"), R57.
    A sentence about another chapter's listing counts, even with
    that listing's file name on it, when the listing on the page
    defines the same name ("`trap_states.py`'s `waiting()` returns
    `TrapState.WAITING` from its `case _`" under a listing with its
    own `waiting()`): cut it if the walkthrough reads complete
    without it, and otherwise open on this listing's thing and put
    the other design second under "In chapter NN's `file.py`,".
    Grep the scope for a file name the chapter does not define.
    A statement in a code span (`return ...`, `yield ...`,
    `raise ...`, `name = ...`) is searched for in the chapter's
    listings; one found in none is hypothetical code ("passes it to
    the next state as an argument, `return selecting(amount)`,"
    where no listing defines `selecting()`), and it gets the design
    it belongs to as a condition ("In a vending machine with one
    generator per state, the state that takes the money ends with
    `return selecting(amount)`"), with "In that design" on the
    sentence that continues it.
    It runs after the passes above because a split or a reframed
    sentence can strand an alternative's continuation from its
    opener, and before `stutter`, since a frame is new words.
11. `stutter`: a word beside its own code-span form ("The next
    `next()`"), one verb said of two things in a sentence, a prose
    noun and a code variable of one spelling naming different things.
    It runs last because the ten passes above write new sentences,
    and a rewrite can put a word beside its code span.

## Before the read

Run the survey tools over the chapter and keep the hits inside the
scope's line range:

- `tip negatives CH=NN` (for `positive`)
- `tip pointers CH=NN` (for `antecedents`)
- `tip positional CH=NN ARGS=--survey` (for `ambiguity`: `count+unit`,
  the survey hits on `call` and `time`, `construct xN`, `ordinal+span`;
  for `alternative`: `survey alternative`, a sentence in a walkthrough
  paragraph naming a construct the listing lacks with no marker word,
  the opener shape only; the continuation shape is read by hand)
- `tip sentence-shapes CH=NN ARGS=--survey` (for `straighten` and
  `cohesion`: `[AND]`, `[COLON]`, `[ADD]`, `[TWO]`, `[CAN]`, `[SAME]`,
  and the default `[PRT]`, a phrasal verb split around a noun phrase,
  "carries the request out" -> "carries out the request", R56;
  `ambiguity` reads `[SAME]`, `[PAIR]`, `[TWO]`, and `[AND+REL]` too,
  and `[REL+AND]`, a relative clause that ends on its verb directly
  before "and" and a second verb, "holds the generator `outer()`
  returned and calls `throw()` on it" -> "The driver calls
  `g.throw()`", the listing's name with no sentence to introduce it,
  C59, every hit printed,
  and `[SAME+NEW]`, a "same" on a noun the 30 lines above never use,
  "`safe()` uses the same separation" -> "`safe()` checks each value
  while it is still separate from the literal text", R63; the survey
  prints only the `[ADD]`, `[CAN]`, `[SAME]`, `[SAME+NEW]`, and `[TWO]`
  hits not yet judged, with `[AND]` and `[COLON]` in full, and a read
  keep goes into the survey baseline with
  `tip sentence-shapes CH=NN ARGS=--survey-accept`; `activate` reads
  `[CAUS]`, a causative with the actor in object position, R61, judged
  the same way)
- `tip watch-words CH=NN` (for `ambiguity`: `however`, Tier 2 since
  2026-11-08, the concessive "however many" that reads first as a
  contrast and is a universal over a count or a manner, R58; the
  contrastive "However," is skipped; `ARGS="--tier 1"` adds the
  negated subjects; for `literal`: `draws` with an exception or a
  diagnostic as its object, Tier 2 since 2026-11-09, "A `yield`
  inside a `finally` clause draws the same `RuntimeError`" -> "If a
  generator yields inside a `finally` clause, `close()` raises a
  `RuntimeError` with the
  message shown for `stubborn()`", the actor named with the verb the book
  taught, raises or reports, R62)
- `tip past-tense CH=NN ARGS=--survey` (for `activate`: `[PAST-SUB]`,
  a past in a subordinate clause, "From the value that `send()`
  delivered, the body chooses" -> "the value that `send()` delivers",
  C63: put each relative-clause hit in the present and keep the past
  only where it alone orders the events, "resumes where it stopped",
  or points at one run; the list has no judged baseline, so every hit
  prints and each one is read, never skipped as a reference back;
  and `[PERFECT]`, a present perfect in a time clause, "before the
  generator has yielded" -> "before the generator yields", C57)
- `tip stutter CH=NN` (for `stutter`: `[CODE!]`, `[CODE]`, `[STEM~]`,
  `[STEM=]`, and `[MIXED]`, one spelling in prose and in a code span
  in one paragraph; no baseline, so every hit prints, and most are
  keeps: the 2026-11-07 sweep reworded 56 of 1,311, and the `[MIXED]`
  survey that day found 5 in 177; run it again over the scope after
  the other passes' edits, since they can create the shape)
- `tip overclaims CH=NN ARGS=--survey` (for the claim check every
  pass makes: `[LEAD]`, a list lead-in that bounds every item above
  an item that exempts itself, "Each approach gives up one side's
  loop:" over "The list keeps both loops", 2026-11-07; it prints
  only lead-ins not yet judged, and a read keep goes into its own
  baseline with `tip overclaims CH=NN ARGS=--survey-accept`)

Read `deep_review_db.md` and the chapter's most recent
`deep_review/~NN...` file for standing exemptions, and the Rules
section of `bruce_edit_db.md` for the rules in force.

## Scope

A section runs from its heading to the next heading of the same or
a higher level.
Edit prose only: fenced blocks, `#:` markers, quoted material, and
headings stay, and a heading changes only when the section is being
restructured anyway, with every link to its anchor updated.
One addition is in scope: a section with no subsections whose listing
leaves the running example to take up a question of its own gets a
subsection heading that names the question (C71, "### Why a
Trampoline" in chapter 45's "One Generator per State"). Report each
heading added, since it changes the chapter's table of contents.
Every claim a rewrite touches is checked against the listing it
describes before the new sentence is written.
A sentence a pass adds beside a listing is held to R47 like any
other: if the listing or its `#:` markers already show it, the
sentence goes. The usual case is a repair that swaps a description
for the listing's own name and adds a sentence to introduce the name
("`g` is `outer()`'s generator." under `g = outer()`, cut by Bruce
2026-11-12). Use the name and stop.
Bruce's "we" and his em-dashes stay.

## After the edits

1. `uv run tip verify-ch CH=NN` (reflows, syncs, gates).
2. `uv run tip prose CH=NN`: read each `NEW` and each `stale` pair.
   A `NEW` hit on a sentence the pass wrote is a sentence to fix or a
   keep to accept; a `stale` entry paired with a `NEW` whose flagged
   word is unchanged is a re-keyed keep, accepted with the scoped
   `tip <check>-accept CH=NN`.
3. The survey rules with a judged list, `[ADD]`, `[CAN]`, `[CAUS]`,
   `[SAME]`, `[SAME+NEW]`, `[TWO]`, and `[LEAD]`: run
   `tip sentence-shapes CH=NN ARGS=--survey` and
   `tip overclaims CH=NN ARGS=--survey` again. A kept sentence the
   pass edited prints as `survey` beside its `stale` entry, so reread
   it. Then record the keeps with `ARGS=--survey-accept` on each. The
   accept takes in every unjudged hit in the chapter and its Solutions
   file, so a pass over one section reads the hits outside its
   section before accepting.
4. Read `git diff Chapters/`: a changed `#:` marker means an edit
   strayed into code.
5. Commit the chapter and any baseline files together, one commit,
   with the message listing the passes and what each changed
   (per [[commit-without-asking]], Bruce pushes).

## Report

One paragraph per pass that changed something, with before/after
pairs for the figures replaced, the sentences split, the pointers
named, the sentences cut and why, and the paragraphs split.
Name the passes that found nothing.
List the hits kept and baselined, with the reason each is the claim.
