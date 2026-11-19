---
name: cohesion
description: Make each paragraph read as one line of thought: old information before new, one running topic in subject position, the news at the end of the sentence where the next sentence picks it up, and every connective stating a real relation. Use when asked to improve the flow, cohesion, or coherence of a chapter (or the book). The argument names chapters by number or name; no argument means all of Chapters/.
---

# Cohesion: old before new, one topic string per paragraph

A paragraph can pass every sentence-level test
(active, literal, concrete, no needless words)
and still be hard to follow,
because each sentence starts somewhere the previous one did not leave the reader.
Williams (*Style*, the lessons on cohesion and coherence)
and Gopen and Swan ("The Science of Scientific Writing")
describe the same two reader expectations.
The **topic position**, the start of the sentence,
should hold something the reader already has:
the running topic of the paragraph, or what the previous sentence just introduced.
The **stress position**, the end of the sentence,
should hold the news: the thing the reader will carry into the next sentence.
A paragraph whose sentences honor both reads as one line of thought.
One that reverses them reads as a list of true statements.

This pass works one paragraph at a time and moves information within
and between sentences.
It does not cut, does not add claims,
and does not reorder anything across a listing.
The `activate` pass already fixes each sentence's subject;
this one checks whether the subjects, read down the page, tell a story.
It edits `Chapters/NN_*.md` prose only;
code blocks, `#:` output markers, and quoted material stay untouched.

## The test: read the subjects down the page

For each paragraph, write its sentences' grammatical subjects in a column.
That column is the paragraph's topic string.

- If the column repeats one or two nouns (the proxy, the checker),
  the paragraph has a topic and the reader can follow it.
- If it wanders (the proxy, `object`, the lookup, `type(p)`, a dunder,
  `print()`), the reader restarts orientation at every sentence.
  Re-front the running topic where the meaning allows,
  even at the cost of a passive:
  `activate`'s own boundary says cohesion outranks activation.
- If the column changes topic once, in the middle,
  the paragraph is two paragraphs, or the second half belongs elsewhere.

Then, for each sentence, check its ends.
Does it begin with something the previous sentence gave the reader?
Does it end on the thing the next sentence picks up?

## Where flow breaks

**New before old.**
The sentence opens on its news and ends on its link to the previous sentence.
Swap the halves:

- "A `Protocol` needs no common base and reports the mismatch where code
  uses an object as a `Service`."
  after a sentence about the ABC's inheritance requirement
  becomes "A `Protocol` instead reports the mismatch where code uses an
  object as a `Service`, and needs no common base."
  (the contrast with the ABC is the old information; "no common base" is
  the news that the next sentence, on `isinstance()`, does not need, so
  it can close the sentence)
- "`len(p)` reports the miss because `object` defines no `__len__()`.
  `object` defines `__str__()`, so `print(p)` cannot."
  is already old-before-new: the second sentence opens on `object`,
  which the first just introduced, and ends on the news.

**A stolen stress position.**
The sentence ends on a qualifier, a citation, or a function word,
and the point sits mid-sentence where nothing marks it:

- "`p.f()` reaches a declared method with a declared return type, with
  explicit forwarding, as in `proxy_forwarding.py`."
  becomes "With explicit forwarding, as in `proxy_forwarding.py`, `p.f()` reaches
  a declared method with a declared return type, and the checker
  verifies it."
- "The two disagree, so the proxy stops consulting the implementation,
  as the output shows."
  becomes "The proxy stops consulting the implementation, and the two
  disagree."
  (the output reference adds nothing the marker does not; the
  disagreement is the news)

A trailing "which ..." clause is the usual thief;
either front it or make it its own sentence.

**A wandering topic string.**
Each sentence is fine and the paragraph is not:

- "The assignment stores `level` on the proxy. The next lookup finds it
  there. The implementation is never consulted again. The type checker
  objects to the assignment."
  (subjects: the assignment, the lookup, the implementation, the checker)
  becomes "The assignment stores `level` on the proxy, where the next
  lookup finds it, so the proxy stops consulting the implementation and
  the two disagree. The type checker objects to the assignment, ..."
  (subjects: the assignment, the proxy, the checker: the proxy is the
  topic, and the checker sentence opens the next point)

**A connective that names no relation.**
"Also", "additionally", "in addition", and a bare "and" between
sentences say only that another sentence follows.
Either state the relation ("so", "because", "but", "which means")
or, if there is none, the sentence is a list item and the paragraph
is a list.

- "The double underscore mangles the name. `__getattr__()` also runs
  only on failed lookups."
  has no relation to state; the two facts belong to different paragraphs,
  and the fix is to move the second.
- "A `Protocol` reports the mismatch at the use site. Also, it needs
  no base class."
  becomes "A `Protocol` reports the mismatch at the use site,
  and needs no base class."

**A claim and its reason kept apart.**
The sentence-level version of the deep-review lens
"where the question arises, where it is answered":
a sentence makes a claim the reader will want explained,
and the explanation arrives two sentences later
with an unrelated sentence between.
Move the reason next to the claim.
If the intervening sentence is the paragraph's real topic,
the claim and its reason move together, to after it.

**A paragraph carrying two topics.**
The topic string changes once and stays changed.
Split at the change.
If the second half is one sentence, it usually belongs
at the head of the next paragraph, whose topic it shares.

## Boundaries

- **Never move a sentence across a listing.**
  Prose before a listing sets it up; prose after reads its output.
  A sentence that seems to belong on the other side of a listing
  is a finding for a deep review, not a cohesion edit.
- **Never change a technical claim.**
  Reordering can silently change scope
  ("only" and "not" attach to whatever ends up next to them),
  so reread every moved sentence for what it now says.
- **Do not add transitions that only announce.**
  "Next,", "Now,", "Turning to", "As mentioned" are metadiscourse
  (`activate` removes them);
  a real transition states a relation between two facts.
- **Bruce's fragments and signposts stay.**
  "Two cautions." and "Brackets when you want a list." are deliberate
  paragraph openers; give them their paragraph, do not absorb them.
- **Bruce's "we" stays.**
  The book addresses the reader as "you", and new prose uses "you"
  unless "we" clearly reads better in that sentence.
  A "we" already in the chapter is Bruce's choice, like his em-dashes:
  do not change it to "you", however the sentence is otherwise rewritten.
- **Semantic Line Breaks.**
  A rewritten sentence goes on its own line,
  breaking at top-level commas when it is long;
  `tip reflow CH=NN` settles the rest.
- **Headings stay** unless the section is already being edited;
  a renamed heading changes its anchor.
- **Check the exemption records first.**
  `deep_review_db.md` in the repo root carries standing exemptions,
  and its notes on deliberately placed sections (chapter 34's
  three-walker paragraph, chapter 1's disclosure) are the section-level
  form of the same judgment: some placements that look wrong are chosen.

## Verify and report

Touched prose gets `tip reflow CH=NN` (Semantic Line Breaks),
then `tip verify`, then read `git diff Chapters/`:
a changed `#:` marker means an edit strayed into code, so investigate it.
Report each changed paragraph as its topic string before and after
(the column of subjects), which is the evidence that the edit helped.
List any paragraph whose string wanders but which you left alone,
with the reason (usually that the wander is a deliberate list,
or that fixing it needs a move across a listing).
Bruce reviews the diff and commits himself.

## Accrued patterns

Flow problems Bruce has flagged that the categories above do not name yet.
When he identifies a new one,
add it here as a bullet with a before/after pair,
and it becomes part of every future pass.

- **A paragraph holding two primary concepts under one topic string.**
  Bruce, 2026-10-05: "a paragraph will hold multiple primary concepts,
  and this makes it confusing."
  The subject column can stay on one noun while the paragraph changes
  what it explains, so the topic-string test passes it.
  The test for this shape: say in one sentence what the paragraph explains.
  If that sentence needs "and" to join two explanations,
  split the paragraph at the seam between them.
  In chapter 30, one paragraph after `weak_responder.py` held three:
  where the weak reference goes
  ("A `Broadcaster` holds a strong reference to whatever you `connect()`,
  so `weak_responder.py` puts the weak reference inside the responder."),
  why a bound method needs `WeakMethod`
  ("An ordinary `weakref.ref(plot.redraw)` is dead the moment it is created."),
  and what the listing does when it runs
  ("The first `announce()` runs while `plot` is alive:").
  Each now opens its own paragraph.
  The usual seams: a design reason beside a mechanism,
  a construct's explanation beside a walkthrough of the listing's run,
  what the code does beside when to use it,
  one listing's discussion beside the next listing's,
  one run of a listing beside its next run.
  Keep together a claim and its reason, the two halves of a contrast,
  and the steps of one walkthrough.
  A second test finds a seam the summary test can miss (Bruce, 2026-11-12, chapter 45's `saga.py`):
  find the paragraph's concluding sentence, the one that says what the walk showed
  ("The nesting of the `try` blocks is the undo stack.").
  A sentence after it starts a new paragraph, even a single sentence
  ("The second booking receives no `throw()`, ...", which walks another generator).
  The usual cause is a sentence written for a statement the listing gained and appended to the paragraph already there.
  A pronoun or "This" that opens the new paragraph gets its noun,
  since its antecedent now sits in the paragraph before.
  The break is often not the whole fix
  (Bruce, 2026-10-30: "sometimes this requires rewriting both paragraphs"):
  a half that leaned on the other through an opening "though" or "also",
  a pointer, or a lead-in sentence at the end of the first half
  is reworded so that each paragraph opens on its own claim
  and closes on its own point,
  and a sentence that tangles the two concepts at the seam is split with them.
  `bruce_edit_db.md` R29 has the record, the chapter 45 before/after,
  and the 2026-10-05 and 2026-10-30 sweeps.
- **An additive adverb after a change of subject.**
  Bruce, 2026-10-28, on a chapter 45 sentence:
  "'as well' could read as 'the same way a closure does'."
  "Also", "too", "as well", and "likewise" say that something joins a set
  the previous sentence set up, and a new subject is the reader's first candidate.
  "A closure keeps its captured variables between calls.
  The generator keeps its place as well" says the closure keeps its place.
  Read the sentence both ways, with the adverb on the subject and on the predicate.
  If the subject reading is false or beside the point, name the thing added
  ("The generator keeps its locals and its place in the body",
  "copies on the way in as well as on the way out")
  or let another word carry the addition ("removes that last change").
  A subject reading that is the claim stays ("Pyright accepts the read too"),
  and so does a sentence where both readings are true.
  `tip sentence-shapes CH=NN ARGS=--survey` lists the shape as `[ADD]`.
  Since 2026-11-09 it prints only the hits nobody has judged;
  after reading them, record the keeps with `ARGS=--survey-accept`,
  which takes in every unjudged hit in the chapter and its Solutions file.
  A kept sentence depends on the sentence before it,
  so a hit prints both (`[ADD] sentence | after: previous sentence`)
  and its baseline entry holds both:
  when you edit or move either sentence, the hit prints again for a read.
  `bruce_edit_db.md` R49 has the sightings.
- **A listing that leaves the section's running example.**
  Chapter 45's "One Generator per State" followed the mousetrap through two listings,
  then showed `tick()` and `tock()` under "One shape looks like a transition and is a delegation:"
  (Bruce, 2026-11-12: "this subsection has been about mousetraps and so the rest of this is kind of an abrupt change").
  The lead-in named neither the mousetrap nor the question the listing answers.
  Write it from the running example: what the example does, the alternative or question the listing takes up,
  and the new names as an instance of it
  ("In `trap_generators.py`, a state returns the next state and `trampoline()` delegates to it.
  The alternative is for each state to delegate to the next state itself ...
  `tick()` and `tock()` are two states written that way:").
  A section with no subsections gets a heading that names the question ("Why a Trampoline").
  The paragraph that returns to the running example starts a new paragraph and names its function.
  For each listing, compare its names with the listing before it; when none carry over, read the lead-in for the tie.
  C71 in `bruce_edit_db.md`.
- **An analogy to an earlier listing maps its terms before it uses them.**
  "`asyncio.run()` starts an event loop, a driver like the one in
  `task_runner_send.py`. The event loop gives each task a turn and
  answers the request each task yields." (Bruce, 2026-11-13:
  "unclear, and is this the asincio event loop? It sounds like a
  generator with ansering the request").
  The second sentence used the listing's words (turn, request,
  answer) for `asyncio` before the paragraph had said that a
  coroutine has `send()` or that `await` yields anything, so the
  reader could not tell which system it described.
  Name the system in the sentence ("the `asyncio` event loop",
  "each `asyncio` task").
  Put each fact before the sentence that depends on it: a coroutine
  object has `send()`, a task drives it, the loop keeps a queue as
  `task_runner()` keeps `ready`, `await` yields a `Future`.
  State the mapping in a sentence of its own: "The `Future` is the
  request, and its result is the reply."
  Probe the real system before writing the mapping.
  Grep the scope for `like the`, `as in`, and `the same as` beside a listing name.
  C74 in `bruce_edit_db.md`.
- **A restatement of a cited description says how it differs.**
  "[Concurrency] describes `await` as suspending a task until the
  event loop resumes it. `await` suspends the coroutine and yields a
  `Future` to its task." (Bruce, 2026-11-13: "describes suspending
  twice?").
  A citation of another chapter followed by a sentence with the same
  subject and verb reads as one fact stated twice.
  Open the second sentence with the relation ("In this chapter's
  terms", "Underneath") and give it a predicate the citation lacks:
  "an `await` on a `Future` that has no result yet is a `yield`".
  Grep the scope for `describes`, `calls`, and `defines` after a
  chapter link and read the sentence that follows.
  C76 in `bruce_edit_db.md`.
- **Two cases that end alike state the shared ending once.**
  "If a coroutine awaits a `Future` that has its result, the `await`
  expression evaluates to that result ... If the `Future` is still
  waiting ... and the `await` expression evaluates to the `Future`'s
  result." (Bruce, 2026-11-13: "echoes an earlier sentence in the
  paragraph so it confuses me").
  The second case ended on the first case's predicate, so the reader
  took it for a return to the first case.
  Walk the case with the steps first, give the short case one
  sentence, and put the shared ending after both, marked as shared:
  "In both cases the `await` expression evaluates to the `Future`'s
  result."
  A repair that adds a case to a paragraph rereads the whole
  paragraph for what the new sentence repeats.
  C78 in `bruce_edit_db.md`.
- **A mechanism the chapter taught under a name is called by that name when it returns.**
  "Each request passes through every awaiting caller on its way to
  the event loop" (Bruce, 2026-11-13: "is this like 'yield from'?").
  The chapter taught this relay for `yield from`, with its own
  words, and the sentence described it again in general words for
  `await`, so the reader had to ask whether it was the same thing.
  Probe that it is, then name the taught construct and reuse its
  vocabulary: "An `await` on a coroutine delegates to that coroutine,
  as `yield from` delegates to an inner generator, and it evaluates
  to the coroutine's return value."
  For each sentence that describes a relay, a delegation, a
  suspension, or a cleanup in general words, check the chapter's
  headings for the section that taught it.
  C79 in `bruce_edit_db.md`.
  A code-span name needs the same check (Bruce, the same day: "have
  we talked about `__aiter__()`?"). For each dunder or library name
  in a walkthrough, grep the book for its first mention and confirm
  that sentence says what calls it and when. If none does, introduce
  it where the construct that calls it is first explained, against
  the counterpart an earlier chapter taught: "In place of
  `__iter__()` it calls `__aiter__()` once ... In place of
  `__next__()` it awaits `__anext__()` on each pass."
- **Two paragraphs that make one point between them.**
  Chapter 45's "Half a Coroutine by Design" opened with a paragraph
  that recalled a premise ("The chapter's opening treats a function's
  position in its body as state. ...") and a second paragraph that
  held the contrast the premise was for ("A call preserves the
  caller's position and locals. ... An ordinary function, when
  called, starts at its first line every time ...").
  The third paragraph opened "That difference matters when"
  (Bruce, 2026-11-13: "see if you can make this clearer and simpler,
  possibly combine into one paragraph that makes the point").
  This is the paragraph test run the other way: say in one sentence
  what each paragraph tells the reader.
  If the first's sentence is a premise or a recollection that the
  first paragraph never uses, the reader reaches the break and asks
  "so?", and the two are one paragraph.
  Write the paragraph that states the point.
  For a contrast, give each side one concrete sentence,
  and give the two sentences subjects of one kind
  ("the caller ... The called function ...", two roles;
  the old pair set a role against "An ordinary function, when called,").
  A qualifier both sides need ("ordinary") goes in the sentence that sets up the pair.
  Cut a premise the chapter has already made,
  and keep one statement of each half, the concrete one (R19):
  "When an ordinary function calls another, the caller waits in the
  middle of its body. When the called function returns, the caller
  continues from that position, with its local variables intact. The
  called function starts at its first line on every call, with a new
  set of local variables."
  Keep two paragraphs when the second illustrates the first with an
  example of its own, or when later text uses each one separately.
  The pointer that opened the next paragraph was part of the fault,
  and the first repair left it there (Bruce, an hour later: "what difference").
  Two parallel sentences above a pointer are not enough:
  the paragraph must call the relation by the pointer's noun,
  state both sides in the one sentence before it,
  or give the two sides defined names
  (chapter 19's *I/O-bound* and *CPU-bound*, then "That distinction").
  Otherwise the next paragraph opens on its own subject,
  an example with "Consider",
  and its sentences repeat the claim's words:
  "Consider two ordinary functions in a single thread: a producer
  that computes a series of values, and a consumer that uses each
  value before the producer computes the next. ... As the caller, the
  consumer keeps its loop. As the called function, the producer
  starts at its first line on every call".
  Grep the scope for
  `^(That|This|These|Those) (difference|distinction|contrast|asymmetry|trade-off|gap|split|separation|overlap)`
  (C82, and the antecedents skill's Accrued patterns).
  Read the first sentence of each section for a subject that is the
  chapter or its opening.
  A sentence repaired phrase by phrase at two flags gets its whole
  paragraph reread at the second.
  C80 in `bruce_edit_db.md`.
- **A design described by what it keeps and leaves out of its source.**
  "PEP 255 kept the suspended frame and left out a coroutine's ability
  to hand control to any other coroutine"
  (Bruce, 2026-11-15, chapter 45: "left out from where?").
  The part removed entered the passage as the object of "left out",
  so the reader met the coroutine's capability and its removal in one phrase.
  This is old before new for a premise:
  state what the source can do in a sentence of its own,
  with the source as subject ("A coroutine can hand control to any other coroutine.").
  Then say what the design keeps, with its owner,
  and what the design does where the source had the missing part, in a positive verb:
  "PEP 255's generator keeps the coroutine's suspended frame and
  restricts the transfer: each `yield` hands control back to the
  caller of `next()` or `send()`."
  Grep the scope for `left out`, `leaves? out`, `drops`, `omits`,
  `without the`, and `kept`,
  and read each one that compares a design with the thing it came from.
  An item the reader can see in a listing
  ("`sets.py` leaves out a few operators") is a keep.
  C86 in `bruce_edit_db.md`.
- **The two sides of a contrast, joined.**
  "a suspended generator keeps its execution frame alive, and a later
  call resumes it. Python discards a function's stack frame when the
  function returns" became, in Bruce's hand (2026-11-15, chapter 45),
  "a suspended generator keeps its execution frame alive, whereas an
  ordinary function discards its stack frame when the function returns".
  Join the two sides with "whereas" or "while",
  give them subjects of one kind
  (the two things contrasted, where the old second side had "Python"
  as its subject and the function in a possessive),
  and move or cut a clause that stands between them.
  Keep a deliberate two-beat ("Failures never vanish. They only relocate.").
  R65 in `bruce_edit_db.md`.
- **A name first seen inside an example.**
  Chapter 46 showed `Effect[Need[Console], KeyError, None]` as its
  example of the three type parameters, before any sentence had said
  what `Need` is (Bruce, 2026-11-17: "This is the first time we see
  'Need' and it is unexpected"; "the reader will wonder 'why isn't
  it just Console?'").
  The sentence after the example read the annotation aloud ("The
  first parameter is `Need[Console]` rather than `Console`") and left
  the reason to a later section through a link.
  Introduce the name in the sentence before the example, with what it
  is, a link on the name to the section that teaches it, and the
  reason for the form: "The Ability that asks for a dependency is
  [`Need`](#declaring-a-dependency). ... `A` is the type of the
  request, `Need[Console]`:".
  For each code-span name in an example or a lead-in, find its first
  mention in the chapter.
  C79 in `bruce_edit_db.md`, sighting 3.
- **A sentence that states a later section's point.**
  "The work the Effect describes waits for a call to `run()`"
  (Bruce, 2026-11-17, chapter 46: "awkward") and "A synchronous
  program calls it once, at the outermost edge" (Bruce: "why are we
  introducing 'synchronous' here?") stood under the chapter's first
  listing.
  Each previewed a section hundreds of lines on, and the listing
  beside them showed neither: in `simplest_effect.py`, `n * 2` runs
  when `double(21)` is called.
  Ask what on the page supports the sentence. When the support is in
  a later section, cut the sentence, and make any later sentence that
  quotes it state the claim itself.
  Grep the scope for a link whose text is a quotation, `\["`.
  C21 in `bruce_edit_db.md`, sighting 2.
- **A class the listing never shows.**
  "`success()` returns a `SuccessEffect`" stood under a listing whose
  only type is `Success[int]` (Bruce, 2026-11-17: "the code makes it
  look like it returns a Success. Maybe we need a second example").
  When the prose names a class or a method that the listing's own
  annotation seems to contradict, add a listing that prints the
  object and exercises the claim, and say why the annotation holds
  (`SuccessEffect` inherits from `Generator`).
  C31 in `bruce_edit_db.md`, sighting 4.
- **Each name's facts in one paragraph, in the listing's order.**
  Under `simplest_effect.py`, chapter 46's paragraphs ran
  `Success[int]`, `run()`, `success()`, `double()`, `SuccessEffect`,
  `success()` again, `double()` again (Bruce, 2026-11-17: "this whole
  section seems to just be a jumble and doesn't have a good
  pedagogical sequence").
  List the paragraphs under a listing by the name each is about. A
  name at two places in the list fails. Gather its sentences (what it
  is, what it is for, how it works), and order the paragraphs as the
  listing's lines show the names: signature, body, call.
  C94 in `bruce_edit_db.md`.
- **A thing's history in one place, in date order.**
  Chapter 44's paragraph on exception specifications gave C++'s
  history twice: "while C++, before C++17 removed them, checked it at
  runtime" in its second sentence, and "C++11 reduced its version to
  a single bit" in its last (Bruce, 2026-11-19: "Can we combine this
  C++ evolution at the end of the paragraph").
  The later step came first, inside a clause that interrupted the
  description of what the design did, and "reduced" left the reader
  to work out what C++17 still had to remove.
  List the dated steps in a paragraph (a version, a year, a PEP). If
  they sit at two places or out of date order, first ask which steps
  the paragraph's argument uses. The first repair gathered both steps
  at the end in date order ("C++11 deprecated the list of exceptions
  and added the `noexcept` keyword ... C++17 abandoned the list
  altogether"), and Bruce cut the middle one: "let's instead skip the
  intermediate step". The paragraph argues that the specifications
  failed, and the outcome is what supports that: "By C++17, the
  language had eliminated the list of exceptions in favor of a single
  `noexcept` keyword, which states whether a function can throw an
  exception."
  In an aside about another language, state where the thing ended up
  and by when. Steps the argument does use go where the paragraph
  ends, in date order, each with what it did.
  The description above them then holds one tense for each language.
  C100 in `bruce_edit_db.md`.
- **The clause before "because" states what the reason explains.**
  "When the `match` unpacks an `Ok`, `slope()` divides at once,
  because `NonZero` guarantees that `run.value` is nonzero" (Bruce,
  2026-11-19, chapter 44: '"succeeds"?').
  The guarantee is a reason the division succeeds. The main clause
  said when it happens, so the reader looked for a delay that the
  reason removes.
  For each "because" or "since", ask what the clause is a reason
  for, and read the main clause for that word. An adverb of time or
  manner ("at once", "directly", "simply") is the usual stand-in for
  "cannot fail" or "needs no check".
  Keep the adverb when it is what the reason explains ("loops over
  the tuple directly, since the tuple holds the same responders for
  the whole loop").
  C103 in `bruce_edit_db.md`.
- **A described version gets its listing; check the exercises first.**
  "The production version uses objects that read with `input()` and
  write with `print()`" (Bruce, 2026-11-19, chapter 44: "perhaps we
  should show the example instead of describing it").
  The page had no listing of those objects, so the reader had to
  write the class in their head to follow the next sentence.
  The listing went in as `greet_console.py`.
  The same code was exercise 1 and its solution. Before a description
  becomes a listing, grep the chapter's Exercises and its Solutions
  file for the code. A listing that answers an exercise takes the
  exercise's place, and Bruce chooses the replacement: here a tracing
  layer written for the new listing, which kept exercises 2 to 5 at
  their numbers.
  A listing is what its lead-in says it is. The first form of this
  one kept `Scripted` for `ask` so that the gate could run it, and
  told the reader why: "because the book's listings run with no
  keyboard attached" (Bruce: "this is confusing"). The listing now
  ends `greet(Console(), Console())`. A listing the gate cannot run
  goes in `tools/data/norun.txt` and shows its run as a text block,
  with a lead-in that says what the transcript cannot ("The program
  waits for you to type a name, here `Alice`:").
  No sentence tells the reader how the book is built: grep the scope
  for `book's (listings|build)`, `unattended`, and `no (terminal|keyboard)`.
  C31 in `bruce_edit_db.md`, sighting 5.
- **A list whose order matters says "in order".**
  "A Koka function type has three parts: the parameter types, the
  Effect row, and the result type. The row sits between the other
  two." (Bruce, 2026-11-19, chapter 44: 'perhaps "... in order:" to
  eliminate the second sentence').
  The second sentence placed one item of a list the first had just
  given in that order. "In order" on the list carries it: "three
  parts, in order: the parameter types, the Effect row, and the
  result type."
  After a list, read the next sentence for a position word (between,
  first, last, before, after) said of one of its items.
  Keep a position in a listing or a call sequence that comes with a
  reason.
  C105 in `bruce_edit_db.md`.
- **A run of paragraphs on one term gets a subsection heading.**
  Chapter 44's Native Effect Management ran 160 lines under one
  heading (Bruce, 2026-11-19: "this block of paragraphs seems like it
  should be a subsection about handlers -- can we organize the
  sectioning for that?").
  List a long section's paragraphs by topic. Where several in a row
  take up a term the section introduces in italics, add a heading one
  level down that is the term, and give each later run a heading of
  its own: "Handlers", "Continuations", "Flix".
  One heading alone would have put the Flix listing under "Handlers".
  Point each term link at the subsection that defines the term, and
  leave a link whose text is the section's title.
  The headings went in at the fourth level, which the book uses in
  one other chapter and no contents list shows. Bruce then promoted
  the section, its sibling, and the sibling after it one level
  ("See if that works"). The parent had been 585 lines, more than
  half the chapter. A subsection that needs the fourth level is a
  sign to measure the parent and look one level up.
  C106 in `bruce_edit_db.md`.
