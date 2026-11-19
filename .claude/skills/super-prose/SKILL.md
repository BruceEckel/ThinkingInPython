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

Each pass's entry below carries the lessons of the edits made so far.
"Every edit feeds this skill", the last section, is the standing rule
that puts the next lesson here.

## The order

Load all eleven skills with the `Skill` tool before touching the
prose, then read the scope once and apply them together.
A second read follows the passes, "The reader's read" below, and a
whole chapter goes through both one `##` section at a time.
The order is the order the skills' own boundary notes give:
each pass hands the next one less to do.

1. `literal`: a figure or a vague description becomes the mechanism.
   A walkthrough sentence that names an argument a call carries says
   what the call does with it ("the `next()` call takes a default of
   `""`" -> "`next()` returns that default when `chars` has no more
   characters", after a sentence that says `next()` otherwise raises
   `StopIteration`, C83).
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
   read each sentence against its line. An expression "evaluates
   to" its value, the reference's verb and the chapter's; it does
   not "take", "get", or "receive" one ("the `await` expression
   takes that value" -> "evaluates to that result", C77), and a
   rewrite never swaps a taught verb or a noun already in the
   sentence for a variation. A feature does not "reach" a version
   ("`yield from`, which reached Python 3.3 in 2012" -> "adopted in
   Python 3.3 (2012)", C87): grep the scope for
   `reach(ed|es)? (Python|[0-9])`. A check is not the act it checks
   ("Those two checks are the Effect tracking and delayed binding of
   a full EMS. In Stateless, the type checker performs both", Bruce:
   "Does the type checker perform delayed binding?"). Put the checker
   in front of the act's verb ("the type checker binds the
   dependency"); when that sentence is false, the check "enforces" or
   "verifies" and the act gets its own actor ("Those two checks
   enforce the Effect tracking and the delayed binding of a full EMS.
   The type checker ensures that you declare each Effect and supply
   each dependency", C89; the second sentence is Bruce's wording,
   2026-11-17, one sentence with the checker in front of "ensures
   that"). Grep the scope for
   `checks? (is|are) the` and
   `checker (performs|does|provides|supplies|binds)`. "Builds on"
   names no relation ("Stateless builds on generators", Bruce:
   "'builds on' is awkward; 'implemented using' or something like
   that"): say which one it is. A library and its mechanism take
   "implements ... using" or "uses" ("Stateless implements Effects
   using generators", his wording 2026-11-17, since "with" after a
   noun can attach to the noun; "frameworks such as FastAPI's
   `Depends` use it"), a listing that adds to an earlier one "extends" it, and a
   chapter that needs an earlier one "depends on" or "uses" what that
   chapter taught (R70; the book read that day rewrote all 24 other
   sites and kept none, so a hit is a sentence written since).
   `tip watch-words` lists the phrase as Tier 2. When the repair is a
   relative clause that parts the subject from its verb ("every
   singleton that keeps its state in a module depends"), use the
   chapter's own term ("the module form of a singleton").
   "Leaves open what X" says a thing is undecided and names neither
   the thing nor who decides it ("`need(SomeClass)` ... leaves open
   what supplies that instance", Bruce: "awkward"): cut the clause
   when the sentence before says who decides ("code outside the
   requesting function answers the `Need`"), and otherwise state the
   decision with its actor (C95). Grep the scope for `leaves? open`.
   A language construct takes its keyword, not a measure of what it
   holds ("put a single bit in their place: whether a function can
   throw an exception", Bruce: "'a single bit' is confusing and less
   clear than using 'noexcept'" -> "added the `noexcept` keyword,
   which states whether a function can throw an exception", C101).
   The reader can look up a keyword and cannot look up "a bit". Grep
   the scope for `\b(bit|flag|switch|marker)\b` said of a feature of
   a language, and keep the word for a real flag or bit in a listing.
   An appeal to practice is a claim about what programmers do
   ("Standard practice combines the first and third", Bruce: "is
   it?"). Ask whose practice. When the answer is "the book
   recommends it", say what the design does or where it applies
   ("The first and third approaches ... combine where input enters
   the program", C102). Grep the scope for
   `(standard|common|usual|accepted|typical) (practice|approach|way|solution|answer|fix)`
   and keep a practice the field holds.
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
   `None`"). When the exclusion is the claim and the excluded thing
   is off the page, say where the whole comes from ("`double()`
   depends on its argument alone", Bruce: "don't we have a rule
   about 'alone'?" -> "`double()` computes its result from its
   argument"). `tip watch-words CH=NN ARGS="--tier 1"` lists every
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
   with no parameters"). A trailing "instead" or "rather than X"
   gets the same deletion test as "only": when the passage has
   already stated the alternative, the tag goes ("The annotation
   describes that returned object rather than how the body reads",
   Bruce: "awkward", three sentences after "Python decides
   generator-function status from the body alone" -> "The annotation
   describes that returned object", C54). Grep the scope for
   `instead[.,:]` and `rather than (how|what|where|when|whether)`.
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
   ("value", "record", "object") point at. "One" is such a stand-in
   ("The `Console` in `greeter.py` is one this chapter defines",
   Bruce: "weird wording, confusing"): grep the scope for
   `(is|are) (the )?ones? `.
   A paragraph that argues is walked as an argument: for each
   "must", "cannot", and "so", find the fact that licenses it on the
   page. A "must" with no reason becomes the fact and its cases
   ("One of the two must call the other" -> "Either the consumer
   calls the producer to get each value, or the producer calls the
   consumer to deliver it", under a scenario that says "two ordinary
   functions in a single thread"), a "cannot" becomes
   the failure the reader can picture ("so you cannot write the
   producer as a loop" -> "so a loop in the producer starts over each
   time"), and a term comes after the sentences that say what it
   consists of ("A function written that way is a state machine"),
   C34. The scenario states every condition the argument uses, and
   each step is probed with a counterexample before it is written.
   No tool lists the shape: grep the scope for `\bmust\b`,
   `\bcannot\b`, and `, so ` outside a listing walkthrough. A
   paragraph Bruce has flagged twice is read this way before a third
   phrase is repaired, a description as much as an argument: say
   what the paragraph is for, then give each part its sentence and
   its verb (chapter 46's opening drew "Besides its result,", "go
   out on", and "every generator has." within minutes, and the
   repair was the paragraph).
   An opener that sets one member of a set aside ("Besides its
   result, an Effect's type declares two things:", Bruce: "awkward")
   makes the reader hold the exception before the set exists, often
   with a pronoun whose noun comes later and a count that leaves the
   member out. State the whole set in its own order, then say what
   holds for which members ("An Effect's type declares three things:
   the dependencies the Effect needs, the ways it can fail, and the
   result it produces. The Effect yields its requests for
   dependencies and its failures, and it returns its result", R71).
   Grep the scope for
   `^(Besides|Apart from|Aside from|Beyond|In addition to) `, and
   keep an opener whose member the page has just described ("Beyond
   those three,", "Apart from that hazard,"; the book read that day
   kept 8 of the 15 other openers for that reason and rewrote 7).
   An exception to a universal goes behind the claim ("No syntax in
   a Python class body allocates a per-object field, apart from
   `__slots__`, which comes up below").
4. `cohesion`: old before new, one topic string per paragraph, R29's
   one primary concept per paragraph. A sentence after a walkthrough
   that reports what a figure or flowchart in a cited source shows,
   where the page does not show that source and the listing has made
   the point, is cut ("Conway's flowchart of the coroutine version
   has those two steps in a row", C84); a quotation, or a fact about
   the source that the listing lacks, stays. A paragraph that likens a real
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
   lead-in for the tie. The paragraph test also runs the other way:
   two short paragraphs that make one point between them, a premise
   or a recollection in the first and the contrast it is for in the
   second, become one paragraph that states the point ("The
   chapter's opening treats a function's position in its body as
   state. ..." and "A call preserves the caller's position and
   locals. ... An ordinary function, when called, starts at its
   first line every time ..." -> "When an ordinary function calls
   another, the caller waits in the middle of its body. When the
   called function returns, the caller continues from that position,
   with its local variables intact. The called function starts at
   its first line on every call, with a new set of local variables",
   C80). Each side of a contrast gets one concrete sentence, and the
   two subjects are one kind of noun, two roles or two kinds. The
   pointer that opens the paragraph after them goes in the same
   edit (pass 5, C82). Read each section's first sentence for a
   subject that is the chapter or its opening: it is the recap R19
   cuts. A sentence that says what a design keeps or leaves out of
   its source ("PEP 255 kept the suspended frame and left out a
   coroutine's ability to hand control to any other coroutine",
   Bruce: "left out from where?") comes after a sentence that says
   what the source can do, and gives the design a positive verb ("A
   coroutine can hand control to any other coroutine. PEP 255's
   generator keeps the coroutine's suspended frame and restricts the
   transfer: each `yield` hands control back to the caller", C86).
   Grep the scope for `left out`, `leaves? out`, `drops`, `omits`,
   and `kept`. A sentence that opens on the far term and ends on the
   near one turns around ("The Effects of [Effect Management] are
   what that description declares", Bruce: "awkward" -> "That
   description declares the Effects that [Effect Management]
   defines"): the term the sentence before left in the reader's hands
   comes first. A chapter link takes a verb there too, since a noun
   joined by "of" to a title that holds the same word reads as
   another phrase, the effects of managing effects. The two sides of
   a contrast are joined with "whereas"
   or "while" and get subjects of one kind ("a suspended generator
   keeps its execution frame alive, whereas an ordinary function
   discards its stack frame when the function returns", R65).
   A code-span name is introduced before the example that uses it
   ("For example: `Effect[Need[Console], KeyError, None]`", Bruce:
   "This is the first time we see 'Need' and it is unexpected" ->
   "The Ability that asks for a dependency is
   [`Need`](#declaring-a-dependency). ... `A` is the type of the
   request, `Need[Console]`:", C79). For each name in an example or
   a lead-in, find its first mention in the chapter. A form the
   definition above did not lead the reader to expect gets its
   reason beside it ("why isn't it just `Console`?"), never a
   sentence that reads the form aloud (R47) or a link to a later
   section (R7). A pointer that says a later section "says why" or
   "explains why" stands where the reason goes: write the reason in
   a clause ("[Built-in Dependencies], below, says why", Bruce:
   "very weird ... rather than forward linking" -> "to show that a
   dependency is an ordinary class"), and grep the scope for
   `(says|explains|shows) why`. A sentence that states a later section's point
   under a listing that cannot show it goes ("The work the Effect
   describes waits for a call to `run()`", Bruce: "awkward"; "A
   synchronous program calls it once, at the outermost edge",
   Bruce: "why are we introducing 'synchronous' here?", C21). Ask
   what on the page supports the sentence, and make a later sentence
   that quotes it state the claim itself; grep the scope for a link
   whose text is a quotation, `\["`. A sentence that names a class
   the listing never shows, against the listing's own annotation,
   gets a listing that shows the class ("`success()` returns a
   `SuccessEffect`" under a signature that says `Success[int]`,
   Bruce: "the code makes it look like it returns a Success" ->
   `success_effect.py`, C31). Under a listing that introduces
   several names, list the paragraphs by the name each is about; a
   name at two places in the list fails, and its sentences are
   gathered in the listing's order, signature, body, call (chapter
   46's The Simplest Effect, Bruce: "a jumble", C94). A thing's
   history told at two places in one paragraph is the same fault in
   time: "while C++, before C++17 removed them, checked it at
   runtime" in the second sentence and "C++11 reduced its version to
   a single bit" in the last (Bruce: "Can we combine this C++
   evolution at the end of the paragraph"). List the paragraph's
   dated steps (a version number, a year, a PEP). For steps at two
   places, or out of date order, first ask which ones the
   paragraph's argument uses: an aside about another language
   usually needs the outcome alone (Bruce, on the first repair's two
   gathered steps: "let's instead skip the intermediate step" ->
   "By C++17, the language had eliminated the list of exceptions in
   favor of a single `noexcept` keyword, which states whether a
   function can throw an exception"). Steps the argument uses are
   gathered at the end in date order, and the description above
   them keeps one tense ("C++ checked its list at runtime", C100). Grep the scope for a version or a year between commas
   inside a sentence about something else.
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
   or "that" is one the passage has used for that thing. A compound
   term keeps both words on every mention ("the event loop", never
   "the loop" in a chapter full of `for` loops): for each compound
   term in the scope, grep for its head noun alone, and when one use
   of a word is changed for a clash, grep for its other uses.
   `[HEAD]` in `tip sentence-shapes CH=NN ARGS=--survey` lists the
   bare head nouns of terms the file rarely shortens ("so the channel
   stays at `Async`" -> "so the Ability channel stays `Async`"); the
   grep still finds a head the file mostly uses alone. Before keeping
   a `[HEAD]` hit, read the listing for a second thing of the kind:
   the competitor is seldom another of the file's terms (a `for` loop
   a paragraph from the event loop, a `check()` function beside the
   type checker, three kinds of block in one listing; the 2026-11-16
   read, R12). Name a loop by what it iterates ("the loop over
   `tasks.items()`"), and check the listing's variable names before
   writing an owner ("the group's block" under `except* ValueError as
   group`).
   A free relative leaves unnamed a thing the passage can name
   ("whatever holds `self.close` holds `Leaky` through it" -> "the
   registry holds `Leaky` through `self.close`", R69; "whichever call
   resumed it" -> "the call that resumed it", R54): write the
   definite noun phrase, and the name when the passage has one
   ("wraps whatever arrives" -> "wraps `other`"). `tip watch-words`
   lists both words.
   A repair that names the items for a bare "each" gives two items a
   clause apiece ("The producer is simplest to write as a loop, and
   so is the consumer"), never the two names in front of the old
   predicate ("The producer and the consumer are each simplest to
   write as its own loop": "are" is plural and "its" is singular,
   C81). After any repair that changes a sentence's subject, reread
   the verb and every pronoun after it for number. Grep the scope for
   `\b(are|were|have|do|keep|hold|take|get|need|run|return) each\b[^.]*\b(its|it|itself)\b`.
   A demonstrative with a relation noun ("That difference matters
   when a producer computes a series of values ...", Bruce: "what
   difference") points at a relation the passage must have stated:
   both sides in the one sentence before it, two defined terms, the
   phrase's own terms ("That split between the table and the body"),
   or the previous sentence's verb made a noun ("chooses ... That
   choice"). Otherwise drop the frame and say what happens; a bridge
   from a claim into an example becomes the example's opener
   ("Consider two ordinary functions in a single thread: a producer
   that computes a series of values, and a consumer that uses each
   value before the producer computes the next"), and the example
   repeats the claim's words (C82). Grep the scope for
   `^(That|This|These|Those) (difference|distinction|contrast|asymmetry|trade-off|gap|split|separation|overlap)`.
   After any paragraph is rewritten, cover it and reread the first
   sentence of the next paragraph: a pointer there was written
   against the old text. After a paragraph is split, read the new
   paragraph's first noun phrase for a "the" that points back across
   the break ("The languages differ" under a list of four other
   languages -> "Languages differ", R44). A kind noun with "the"
   ("the PEP" in a section that cites four PEPs, "the listing", "the
   function") passes when the sentence before it names the one
   meant, and otherwise takes the name ("two years before the PEP"
   -> "before PEP 255", R12). A bare noun far from the phrase that
   says what it holds takes the phrase again, in the number the
   paragraph uses ("C++11 deprecated its lists", eight sentences
   after "a list the programmer writes on each function", Bruce:
   "the list of exceptions? something better than 'its lists'" ->
   "deprecated the list of exceptions", R12). A repair that moves a
   sentence moves its nouns away from the sentence that identified
   them, so read each one where it lands. A part noun ("the body", "the loop",
   "the frame") names its owner when the paragraph holds a second
   thing with that part ("compile the body" -> "compile the
   generator's body", beside a loop body, C50). A count of items
   named far above names them, in the order of what the reader must
   match them against ("types the three channels as `Generator<T,
   TReturn, TNext>`" -> "types the yielded, returned, and sent
   values as", R66). A count under a noun the passage never gave the
   items is the same pointer ("An Effect yields both kinds of
   value", Bruce: "weird", after a sentence that called neither the
   Abilities nor the failures a value -> "An Effect yields an Ability
   to ask for what it needs, and it yields an exception to report a
   failure"): name each item with what it is for. An "it" that ends
   a clause is read for the nearest noun its verb could take ("A
   `Need` is a request for an instance, and code outside the
   requesting function answers it", Bruce: "what does 'it' refer
   to?" -> "answers the `Need`", R12). `tip pointers` lists the
   sentence-opening "it" alone, so grep the scope for ` it[.,;:]`.
   A term the book defines in an earlier chapter is a link at its
   first use in the chapter ("Stateless does [dependency
   injection](11_Techniques--Testing.md#random-numbers) with
   `Need`", R16).
6. `ambiguity`: every sentence that counts, compares, coordinates,
   modifies, or limits keeps one reading. A list of what two things
   share ("has `send()`, `throw()`, and `close()`, as a generator
   does") is counted against what the chapter taught the first
   thing to have; for a member left out, probe the second thing and
   say what it does ("It is not an iterator, so `next()` on a
   coroutine object raises a `TypeError`", C75). The list can be one
   the passage has just given: three parameters, then "This chapter
   calls `A` the *Ability channel* and `E` the *error channel*"
   (Bruce: "does it not mention the result channel?") gets a
   sentence that says where `R` goes. After every list or table,
   count the members the next sentences speak of. A trailing
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
   true. A claim set on one row of a table is the same modifier ("In
   `Success`, `Never` stands in for both `A` and `E`", under three
   aliases, Bruce: "does 'Never' also stand in with Depend and
   Try?"): probe the other rows, and state the claim for all of them
   or put it in the table. A member noun where the paragraph's rule
   is about the class is the same modifier ("If you forget to
   declare a dependency, the check fails", between "declares each
   Effect" and "declare each Effect", Bruce: "should this be Effect
   rather than dependency?"): for each verb in a paragraph's rule
   sentence, list the objects the other sentences give it, probe
   the claim with the class noun (an undeclared failure draws an
   `invalid-yield` too), and write the class noun when it holds
   ("If you forget to declare an Effect", C70 sighting 6).
   `[VERB+OBJ]` in `tip sentence-shapes CH=NN ARGS=--survey` lists
   the shape when the rule's object carries "each", "every", "all",
   or "any"; a rule stated another way is found by the list. A pronoun
   in the next sentence that pointed at the old noun gets its noun
   ("supply one" -> "supply a dependency"). A comparison of two look-alike names is
   true of the names and may be false of the things ("`success()`
   and `Success` differ only in case", Bruce: "one is callable and
   the other is a type"): make "the names" the subject or cut the
   sentence (C93). The other shapes: a count with two units, a
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
   file") stay. A bare "frame" in a passage with a generator's
   execution frame and a call's stack frame says which kind it is
   (Bruce: "clarify what kind of frame this paragraph references",
   R68): grep the scope for `\bframes?\b`. A time word on a standing
   fact ("after which the execution frame lives on the heap", when
   it is there from the generator's creation) is C70's modifier in
   time form: ask whether the statement was true before the event.
   "The same X" said of a list ("PHP and Dart follow the same
   design") is one claim for each member, so check each against its
   reference and give a member that differs its own sentence (R63).
   A concessive "whatever" is a universal (R69; the 2026-11-16 read
   rewrote all 54 of the book's sites). Cut it when the sentence or
   its neighbor says the same ("picks the field by name, whatever its
   position", two sentences after "Unpacking assigns by position").
   Otherwise name its options ("whatever its first character" ->
   "with or without a leading underscore"; "whatever its kind" ->
   "file or directory") or its range ("in any field order", "for
   every `y`"), with the name the listing gives ("whatever its base
   classes" -> "with or without a `Drawable` base class"). Test the
   universal before restating it: "raises a `RecursionError` that
   reports a stack overflow, whatever the limit says" was false at
   the default limit and became "despite the raised limit". After a
   cut, read the sentence against the next one for a clause the two
   now share ("stays what you last read. Because a deeply immutable
   value stays what you last read" took its phrase back as "no matter
   which code ran in between"). A capability credited to a mechanism
   ("invoke the continuation several times, which is how native
   systems express retries and backtracking", Bruce: "zio is a
   library effect system, yet it is able to do things that native
   effect systems achieve using continuations, like retries?") is a
   word with two senses when a design the book says lacks the
   mechanism has the capability by name: grep the Part for the
   capability's word (`retry()` in chapters 46 and 47 runs the
   function again from its start and needs no continuation), then
   cut the capability that does not need the mechanism ("express a
   backtracking search") or say how the two differ (C99).
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
   or a listing as the subject. A "re-" verb claims an earlier time
   ("Stateless reuses the word Effect for the whole description a
   function returns", Bruce: "reuses or uses?"): when the reader
   cannot name that earlier use from the sentence and the one before
   it, write the plain verb, "uses", and let the sentence that holds
   the earlier use make the comparison (C92; "again" for "still" is
   the same word of history). Grep the scope for `\breus(e|es|ed)\b`
   and `\bagain\b`.
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
  the same way; `antecedents` reads `[HEAD]`, a compound term
  shortened to its head noun, "the channel" beside "the Ability
  channel" and "the error channel", R12, judged the same way;
  `ambiguity` reads `[VERB+OBJ]`, a rule's verb with a second,
  generic object, "declare a dependency" in a paragraph that says
  "declare each Effect", C70, judged the same way)
- `tip watch-words CH=NN` (for `ambiguity`: `however`, Tier 2 since
  2026-11-08, the concessive "however many" that reads first as a
  contrast and is a universal over a count or a manner, R58; the
  contrastive "However," is skipped; `whatever`, Tier 2 since
  2026-11-04, R69, whose concessive is `ambiguity`'s and whose free
  relative is `antecedents`', as `whichever` is, R54; every site in
  the book is rewritten, so a hit is a sentence written since;
  `ARGS="--only whatever"` lists one word's sites; `ARGS="--tier 1"`
  adds the negated subjects; for `literal`: `draws` with an exception
  or a
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
A lead-in is held to R47 too. One that gives each call's argument and
its result reads the listing aloud before the reader reaches it ("A
`NonZero` that holds 2 passes to `slope()`, while building one that
holds 0 raises a `ValueError`:" above `slope(10, NonZero(2))` and
`NonZero(0)`, Bruce, 2026-11-19: "this restates the code that
follows"). The tell is a literal from the listing in the lead-in.
Write what the listing cannot say, here what the design asks of a
caller ("A caller builds the `NonZero` before it calls `slope()`:").
A lead-in that states the rule the listing demonstrates, and names no
call the listing makes, stays.
Bruce's "we" and his em-dashes stay.

## The reader's read

The eleven passes test a sentence against a rule. Bruce reads a
sentence and asks what a reader would ask. On 2026-11-17 he flagged
17 sentences in the first 300 lines of chapter 46, two days after a
super-prose pass over the whole chapter (`2a115633`) had read 15 of
them and kept them, and had written a sixteenth ("depends on its
argument alone"). Seven were plain applications of promoted rules
(R7 twice, R47 twice, R10, R12, R16). Each flag was a question: "does
it not mention the result channel?", "why isn't it just `Console`?",
"does 'Never' also stand in with Depend and Try?", "why are we
introducing 'synchronous' here?", "what does 'it' refer to?".

So the scope gets a second read after the passes, one paragraph at a
time, as a reader who knows only what the book has said up to that
sentence. After each sentence, write down the question it leaves, and
check that the page answers it before the paragraph ends:

- A name in a code span: has the chapter said what it is? (`Need` in
  an example, `SuccessEffect` under a signature that says `Success`.)
- A list or a table, then a sentence about some of its members: what
  about the others? (Three parameters and two channels, three aliases
  and "In `Success`".)
- A modifier or a limiter: what is the other case? ("A synchronous
  program", "alone", "only".)
- A pronoun that ends a clause: which noun? ("answers it".)
- A verdict or a comparison: is it true as the reader will take it?
  ("That signature is incomplete", of a standard Python signature;
  "differ only in case", of a function and a type.)
- A reason for a line that fails a check: is it false of the line
  beside it that passes? ("Structural matching decides what
  `isinstance()` accepts, not what the type checker accepts", under
  a listing whose second line passes the type check by structural
  matching, C98.)
- A type expansion: is the definition it follows from on the page
  yet? ("the alias for `Generator[Never, Any, int]`" and "A union
  with `Never`", both 150 lines or more above `Effect`'s definition,
  C79 sighting 4.)
- A pointer to another place: does the sentence need the reason here?
  ("below, says why".)
- A sentence beside a listing: does the listing show it, and does the
  reader already know it? ("`-> None` describes the return value".)
- A term of art: where does the book define it, and is it linked?
  ("dependency injection".)
- Two listings that define one name: can the reader tell them apart?
  (`greet()` in `greeter.py` and in `untyped_greet.py`, now
  `plain_greet()`.)
- The paragraphs under a listing: is each name's story in one place,
  in the listing's order? (The Simplest Effect.)
- A section's first listing: does it show the concept at work, or the
  trivial case, where the concept has nothing to manage? (`double()`,
  an Effect with zero Effects, as the one example in The Simplest
  Effect; Bruce: "I don't think it gives enough context". The test:
  would a plain function print the same output? The repair says in the
  listing's lead-in that it is the trivial case, then adds one minimal
  listing per kind, each doing one thing, C97.)

A question the page leaves open is a finding, under any rule or none.
Fix it under the pass that owns it. When no pass does, say so in the
report: a missing listing, a name used before its section, and a
section's order belong to the `deep-review` teaching pass.

Two limits on what a pass may take as settled:

- A sentence that an earlier pass or sweep read and kept is not a
  keep. The keeps the tools hold are keeps of one flagged word under
  one rule. Fifteen of the seventeen sentences had come through about
  twenty sweeps.
- A whole chapter is read one `##` section at a time, each section
  through the passes and then through this read, before the next one
  starts. The 2026-11-15 pass read 1,900 lines at once and changed 75
  sentences, most of them shapes a survey tool lists.

## After the edits

1. `uv run tip verify-ch CH=NN` (reflows, syncs, gates).
2. `uv run tip prose CH=NN`: read each `NEW` and each `stale` pair.
   A `NEW` hit on a sentence the pass wrote is a sentence to fix or a
   keep to accept; a `stale` entry paired with a `NEW` whose flagged
   word is unchanged is a re-keyed keep, accepted with the scoped
   `tip <check>-accept CH=NN`.
3. The survey rules with a judged list, `[ADD]`, `[CAN]`, `[CAUS]`,
   `[HEAD]`, `[SAME]`, `[SAME+NEW]`, `[TWO]`, `[VERB+OBJ]`, and
   `[LEAD]`: run
   `tip sentence-shapes CH=NN ARGS=--survey` and
   `tip overclaims CH=NN ARGS=--survey` again. A kept sentence the
   pass edited prints as `survey` beside its `stale` entry, so reread
   it. Then record the keeps with `ARGS=--survey-accept` on each. The
   accept takes in every unjudged hit in the chapter and its Solutions
   file, so a pass over one section reads the hits outside its
   section before accepting, or records one rule at a time with
   `ARGS="--survey-accept --rule NAME"`. The watch-words accept
   narrows the same way: `tip watch-words-accept CH=NN ARGS="--only
   could"`, with a phrase quoted inside the value
   (`ARGS='--only "has no"'`).
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

## Every edit feeds this skill

Bruce's standing instruction (2026-11-16): "Whenever I make an edit
in this book, or ask you to make an edit, you should learn from that
edit and incorporate it into the appropriate place in super-prose."
It holds in every session, inside an editing pass or outside one, and
it needs no request. The edit is the request.

An edit is any of these: a change Bruce typed (seen in the working
tree, in a commit of his, or in a chapter editor round), a sentence
he flags, pastes, or asks a question about, and a rewrite or a sweep
he asks for, with the repairs the session makes inside it. Who typed
the change does not matter (2026-09-28).
The `SessionStart` notice (`uv run tip uncaptured`) lists the commits
he made by hand and the prose files with uncommitted changes that no
session has read. After reading them and filing their lessons, run
`uv run tip uncaptured ARGS=--mark` and commit
`tools/data/edits_read_through.txt` with the lessons.

For each one, in the same turn as the edit:

1. **Say what the before-text got wrong**, in one line that would
   pick the fault out in another chapter. An edit that is local (a
   fact corrected, a name changed, prose following a listing that
   changed, a word that repeated a few lines up) teaches nothing
   here: say "local" in the reply and stop.
2. **Find the pass that owns the fault.** A figure or a vague
   description is `literal`'s. A negation is `positive`'s. A subject
   held open, or an "and" or a colon carrying a second claim, is
   `straighten`'s. Order, a paragraph's topic, and a seam are
   `cohesion`'s. A pointer or a stand-in noun is `antecedents`'. Two
   readings are `ambiguity`'s. A passive, a tense, and a frame are
   `activate`'s. A road not taken is `alternative`'s, and an echo is
   `stutter`'s. A fault no pass owns goes to the pass whose test
   comes closest, and the entry says so.
3. **Write the lesson into that pass's entry in "The order"**: the
   test, the before and the after in quotation marks, the store
   number, and how a pass finds the shape (the survey tool that lists
   it, or a grep). Add the dated entry, with Bruce's words when he
   gave any, to the Accrued section of the pass's own `SKILL.md`. A
   lesson about how the passes run (a check to make, a step out of
   order) goes in the section of this file it changes.
4. **Record it in `bruce_edit_db.md`**: a sighting on the rule or the
   candidate it matches, or a new candidate stated as narrowly as the
   one edit supports, with a `Home` that names the pass. A second
   chapter earns a `**Promotion.** Proposed` line. Promoting is
   Bruce's call.
5. **Grep both trees for the shape.** Fix the sibling sites in the
   chapter at hand, and give the count of the others in the store
   entry.
6. **Commit the lesson with the edit**, and say in the reply, in one
   line, what was learned and where it went.

Two limits. An edit Bruce is still typing inside an open pass is
evidence the `edit-start-NN` tag already holds: learn from it when it
settles (he commits it, flags it, asks about it, or closes the pass
with `/edit-done`), and leave a sentence in motion alone. And one
edit underdetermines its rule, so the narrow statement is the right
one (the `bruce-edit-capture` skill has the reasons). A pass entry
that fires on a tenth of a chapter's sentences was stated too
broadly.

This section is in the repository because project memory is kept per
machine. Bruce first gave the instruction on his laptop, and it had
not reached this checkout.
