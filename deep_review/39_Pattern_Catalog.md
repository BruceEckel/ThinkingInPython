When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Opening paragraph: POSA is the only source cited without an author.**

> It draws from *Pattern-Oriented Software Architecture* (POSA),
> *Patterns of Enterprise Application Architecture* (Fowler),
> *Enterprise Integration Patterns* (Hohpe and Woolf),

The other three sources are attributed: GoF in the line above, then Fowler,
then Hohpe and Woolf.
POSA gets only its acronym, which reads as an oversight rather than a choice,
and POSA is the one source a reader is least likely to be able to name.
It is also a five-volume series rather than one book,
so the bare title is doing less work than the others.

Proposed change:

> It draws from *Pattern-Oriented Software Architecture* (POSA, Buschmann et al.),

Reported rather than applied because attribution style is an authorial call,
and because chapter 21 names all four GoF authors in full,
so you may prefer the fuller form here too.

---

[] Reject

**Second paragraph: "find it elsewhere" does not say where "elsewhere" is.**

> Each entry has a one-line intent so you can recognize a pattern by name and find it elsewhere.

Two readings compete.
"Elsewhere" could mean elsewhere in this book (which the link column already
handles, and which the paragraph's last two sentences describe),
or it could mean in the source literature the previous paragraph just listed.
The second is the intended one, and it is the more useful promise,
but the sentence leaves the reader to guess.

Proposed change:

> Each entry has a one-line intent so you can recognize a pattern by name
> and look it up in the literature that documents it.

An alternative, if you want the sentence to carry the catalog's other job too:

> Each entry has a one-line intent,
> enough to recognize a pattern by name and to look it up in the source that documents it.

I recommend the first.

---

[] Reject

**Second paragraph, the biggest item: the catalog is organized by source, and
chapter 21 has just told the reader that two of those groupings are not
useful.**

Chapter 21's [Pattern Taxonomy](21_The_Pattern_Concept.md#pattern-taxonomy)
says this plainly:

> But I find *Structural* and *Behavioral* to be far less useful distinctions.
> I have not been able to look at a problem and say "clearly,
> you need a structural pattern here," so that classification doesn't lead me
> to a solution ...
> Patterns often resemble each other more in their implementations than the
> *GoF Design Patterns* categories suggest, and that is how this book groups
> them.

Eighteen chapters later the catalog opens with `## Creational (GoF)`,
`## Structural (GoF)`, `## Behavioral (GoF)` and never mentions the
disagreement.
A reader who took chapter 21 seriously arrives here and finds the book using
the classification it criticized, with no explanation.
The honest answer is that a catalog has to follow each source's own
organization so a reader can find a name where the source put it,
and saying so costs one sentence.

There is a second, larger cost that the same sentence cannot fix.
Grouping by source means the catalog answers "what does this name mean?"
but not "which pattern solves my problem?",
which is the question chapter 21 says the GoF categories fail at.
A reader who does not already know that Circuit Breaker exists has no path to
it: they would have to guess that "Distributed and Cloud" is the table to scan.

Three ways forward, increasing in cost.
I recommend the second.

**Option A (one sentence, no structure change).**
Add to the second paragraph, after "Listing a pattern here is not a
recommendation.":

> The tables follow each source's own grouping,
> including the *Creational*/*Structural*/*Behavioral* split that
> [The Pattern Concept](21_The_Pattern_Concept.md#pattern-taxonomy)
> questions, so that a name sits where the source that documents it puts it.

This removes the apparent contradiction and does nothing for problem-first
lookup.

**Option B (recommended): Option A plus a short problem-first index.**
Add one table, near the top, before `## Creational (GoF)`,
keyed by the question a reader actually arrives with.
Something like:

```
## Finding a Pattern by Problem

| If the problem is | Look at |
|-------------------|---------|
| Creating objects without naming their classes | Abstract Factory, Builder, Factory Method, Prototype, Registry, Plugin |
| Making one object stand in for another | Proxy, Decorator, Adapter, Façade, Ambassador, Sidecar |
| Choosing behavior at runtime | Strategy, Command, Chain of Responsibility, State, Visitor, Multiple Dispatch |
| Structuring recursive or tree-shaped data | Composite, Interpreter, Visitor, Blackboard |
| Keeping the number of objects down | Flyweight, Multiton, Object Pool, Singleton |
| Saving and restoring state | Memento, Event Sourcing, Unit of Work, Identity Map |
| Reacting to change | Observer, Publish-Subscribe Channel, Model-View-Controller |
| Coordinating concurrent work | Thread Pool, Producer-Consumer, Future/Promise, Active Object, Reactor |
| Surviving a failing dependency | Circuit Breaker, Retry, Bulkhead, Timeout, Dead Letter Channel |
| Moving data across a boundary | Data Transfer Object, Message Translator, Gateway, Data Mapper |
| Supplying a collaborator from outside | Dependency Injection, Service Locator, Inversion of Control, Strategy |
```

Each cell is names only, not links, so the index stays one screen and does not
duplicate the link maintenance of the tables below it.
The cost is real: eleven more rows to keep in sync when a pattern is added,
and one more place a name can go stale.
It is also the only change that makes the chapter usable by a reader who does
not already know the name they want.

**Option C: keep the source tables but add a "Problem" column to each.**
More precise, much heavier, and it widens every table past comfortable reading
width. I do not recommend it.

---

[] Reject

**Second paragraph: "a number of them are unnecessary in Python" never says
which, and the catalog is the one place a reader would want the list.**

The sentence is the book's central pattern thesis compressed to nine words,
and the catalog is exactly where a reader looking a pattern up would benefit
from knowing that this book argues it dissolves.
Right now that information is spread across chapters 20, 21, 23, 24, 27, 28,
33, and 37, and the catalog carries none of it.

(Applied in this pass and independent of what follows: the sentence now links
to [When a Pattern Dissolves](21_The_Pattern_Concept.md#when-a-pattern-dissolves),
which was the one cross-reference the chapter most obviously needed.
The catalog leaned on chapter 21's entire argument without naming it once.)

Proposal: close the chapter with a short section that names them,
which also fixes the chapter ending on a bare table row.
Draft:

```
## Patterns Python Absorbed

Several entries above are in the catalog because the literature documents
them, not because you need to write them.
Python already supplies the piece they were invented to supply.

| Pattern | What Python supplies instead |
|---------|------------------------------|
| [Iterator](23_Iterators.md#the-pattern-that-disappeared) | The iteration protocol, called for you by `for` |
| [Singleton](24_Singleton.md#a-module-is-already-a-singleton) | A module, imported once and cached |
| [Factory Method](27_Factory.md#the-pythonic-factory-a-dictionary) | A dictionary of classes, since a class is an object |
| [Strategy](28_Function_Objects.md#strategy-choosing-the-algorithm-at-runtime) | A function passed as an argument |
| [Command](28_Function_Objects.md#command-choosing-the-operation-at-runtime) | A function stored in a list |
| [Chain of Responsibility](28_Function_Objects.md#chain-of-responsibility-choosing-the-handler-at-runtime) | A list of functions, tried in order |
| [Visitor](33_Visitor.md#the-pythonic-visitor-singledispatch) | `functools.singledispatch` |
| [Flyweight](35_Flyweight.md#python-uses-flyweights) | Interned strings and cached small integers |
| [Prototype](27_Factory.md#prototype) | `copy.deepcopy()` and `dataclasses.replace()` |

What survives the subtraction is the intent, not the structure.
[The Pattern Concept](21_The_Pattern_Concept.md#when-a-pattern-dissolves)
makes the general argument; each chapter above works one case.
```

Two things to weigh.
This is the closing insight the chapter currently lacks,
and it is the one section of the catalog that is about this book rather than
about the literature, which is a good note to end Part III on.
Against that: it duplicates link targets already in the tables above,
so a renumbering touches both.
Reported rather than applied because a new section changes the chapter's shape
and pacing, and because you may prefer the catalog to stay purely a lookup.

I verified every anchor in the draft table against the current text of each
target chapter, and all nine resolve today.

---

[] Reject

**Behavioral (GoF), the State row: chapter 31 is invisible in this catalog.**

> | [State](26_Surrogate.md#state) | Change an object's behavior when its internal state changes. |

[State Machines](31_State_Machines.md) is a full chapter, the whole of it about
this pattern, and it opens by saying so:

> Recall [*State*](26_Surrogate.md#state) ...
> While *State* allows the client programmer to change the implementation,
> *StateMachine* imposes a structure to automatically change the implementation
> from one object to the next.

Chapter 21 also names `[State Machines](31_State_Machines.md)` as one of the
book's three worked Behavioral patterns, alongside Observer and Visitor,
both of which the catalog links.
As it stands, 31 is one of only two Part III chapters this catalog never
points at.

Recommended fix: add a row to `## Behavioral (GoF)`, after State:

> | [State Machine](31_State_Machines.md) | Drive an object through a fixed set of states from a transition table. |

Alphabetical order puts it right after State, which is also where a reader
would want it.
It is not a GoF pattern, so if you would rather keep that table pure GoF,
the alternative is to put it in `## Foundational Idioms` instead;
I prefer the Behavioral table, because that is where a reader who just read the
State row will look next.

A cheaper alternative that adds no row: change the State intent to
"Change an object's behavior when its internal state changes;
[State Machines](31_State_Machines.md) automates the changes."
I do not recommend this, because it makes the Intent column carry a
cross-reference no other row carries.

---

[] Reject

**Behavioral (GoF): Multiple Dispatching, the book's other missing Part III
chapter.**

[Multiple Dispatching](32_Multiple_Dispatching.md) is a whole chapter,
it names both patterns explicitly
("The solution is *Multiple Dispatching*", "Two unknown types means two
dispatches, which is *double dispatching*"),
and neither name appears anywhere in this catalog.
Double Dispatch is widely documented, and it is the mechanism GoF's Visitor
runs on, so a reader who followed the Visitor row here has a live reason to
want it.

Recommended fix: add to `## Foundational Idioms`, next to Function Object:

> | [Double Dispatch](32_Multiple_Dispatching.md) | Resolve behavior from the runtime types of two objects, through two calls. |

Alternative placement: `## Behavioral (GoF)`, on the grounds that GoF discusses
double dispatch inside Visitor.
I prefer Foundational Idioms, because the table header says (GoF) and
Double Dispatch is not one of the 23.

If you take both this and the State Machine row, the two together close the
gap: every Part III pattern chapter would then be reachable from the catalog.
(37 is a refactoring case study rather than a pattern, so it stays unlinked.)

---

[] Reject

**Concurrency table: the Thread Pool row lands the reader in a section about
the GIL.**

> | [Thread Pool](19_Concurrency.md#the-gil-and-free-threading) | Reuse a fixed set of worker threads across many tasks. |

The target is defensible — `io_threads.py` lives there and the section says
"That release is why a thread pool helps with I/O-bound work" — but the
heading a reader arrives at is "The GIL and Free Threading",
which does not look like an answer to "Thread Pool".
The section that treats the pool as a reusable component is
[One Task, Many Backends](19_Concurrency.md#one-task-many-backends),
where `ThreadPoolExecutor` is one of three interchangeable `Executor`
subclasses and the `submit()`/`map()` interface is explained.

Recommended: point it at `#one-task-many-backends`.
Alternative: leave it, since the GIL section is where a reader learns *when* a
thread pool helps, which is arguably the more useful thing.
This was also noticed independently by the readability pass
(`readability/~39_Pattern_Catalog.md`), which recorded it and left it alone.

(Applied in this pass, and related: the Future/Promise row moved from
`#parallelism` to `#one-task-many-backends`.
`#parallelism` only mentions the `Future` interface in passing while explaining
`ProcessPoolExecutor`; `#one-task-many-backends` is where the book actually
teaches what a Future is, including the `concurrent.futures.Future` versus
`asyncio.Future` distinction and the `TypeError` a reader hits by awaiting the
wrong one.)

---

[] Reject

**Concurrency table: Thread-Specific Storage is covered, thinly.**

> | Thread-Specific Storage | Give each thread its own copy of a value. |

The intro promises that "An unlinked name means the pattern appears only in
this catalog", and chapter 19 does discuss `threading.local` by name:

> The middle line is the reason `ContextVar` rather than `threading.local` is
> the modern answer.
> `threading.local` gives each *thread* its own value,

Two sentences of contrast is thin, and linking it would send a reader to a
section that recommends *against* the pattern.
That is arguably the most useful thing the catalog could tell them.

Recommended: link it to
[Context That Follows the Call Chain](19_Concurrency.md#context-that-follows-the-call-chain).
Alternative: leave it unlinked and accept that the intro's rule means "covers"
rather than "mentions".
Reported rather than applied because it is your line to draw, and drawing it
loosely here invites the same argument for Half-Sync/Half-Async
(`to_thread()` plus an executor queue), Guarded Suspension
(a blocking `Queue.get()`), and Message Channel / Point-to-Point Channel
(chapter 19's queues).
I would link none of those four; they are structural resemblances rather than
the book teaching the pattern.

(Applied in this pass, because it is not a borderline case:
Double-Checked Locking is now linked to
[Tests, Threads, and Locks](24_Singleton.md#tests-threads-and-locks).
Chapter 24 names the pattern, explains the two tests and what each is for,
and recommends against it — a full paragraph, not a mention.
It was the one unlinked row that made the intro's rule flatly untrue.)

---

[] Reject

**Concurrency table onward: only the three GoF tables are in a findable
order.**

Creational, Structural, and Behavioral are alphabetical, which is also GoF's
own order.
Every table after them is not.
Concurrency runs Active Object, Monitor Object, Half-Sync/Half-Async,
Leader/Followers, Thread Pool, Reactor, Proactor, ... , which splits the
Reactor/Proactor pair with Thread Pool between them and puts Future/Promise
twelve rows down.
Enterprise Application is roughly Fowler's book order but strands Service
Layer after Value Object, five rows from the other three domain-logic patterns
it belongs with.
Foundational Idioms has no discernible order at all.

For a name-lookup reference this matters: the reader knows the name and has to
scan.

Recommended: alphabetize the five non-GoF tables, and say so in the intro:

> Within each table, GoF's own order is kept for the classic patterns;
> the rest are alphabetical.

Alternative: keep source order everywhere and drop the alphabetical GoF
tables into GoF's book order too (which is the same order, so nothing moves),
then say the tables follow each source.
That is cheaper and less useful.

Reported rather than applied because reordering rows is a structural change.
Nothing links into these tables, so the move breaks nothing.

---

[] Reject

**Enterprise Application table: Lazy Load and Plugin are borderline
unlinked rows worth a decision.**

Two rows sit next to material the book does cover:

-   `Lazy Load | Defer loading data until it is needed.`
    Fowler's version is database-shaped, but the intent line as written is
    generic, and the book has both
    [Lazy Imports](06_Modules_and_Packages.md#lazy-imports) and
    [Lazy Evaluation with Generators](18_Performance.md#lazy-evaluation-with-generators).
    Meanwhile the Foundational Idioms table's Lazy Initialization row *is*
    linked, so the catalog currently treats two neighbouring lazy patterns
    differently for no stated reason.
-   `Plugin | Choose behavior with classes named at configuration time.`
    Chapter 17's
    [Self-Registration of Subclasses](17_Metaprogramming.md#self-registration-of-subclasses)
    and chapter 27's
    [registry factory](27_Factory.md#the-pythonic-factory-a-dictionary)
    are the same mechanism minus the configuration file.

Recommended: link Lazy Load to
`18_Performance.md#lazy-evaluation-with-generators`, and leave Plugin
unlinked, since Fowler's Plugin specifically means naming the class at
configuration time and the book never does that.
Alternative: leave both unlinked and narrow the Lazy Load intent to
"Defer loading a persisted object until it is needed", which makes the
non-coverage obvious from the text.
I slightly prefer the alternative; it is the more honest of the two.

---

[] Reject

**Distributed and Cloud table: Retry is covered in chapter 47.**

> | Retry | Re-attempt a failed operation, often with backoff. |

Chapter 47 teaches it directly:
`retrying.py` under
[Adding Behavior to an Existing Effect](47_Stateless_in_Practice.md#adding-behavior-to-an-existing-effect),
followed by two subsections,
"Why `retry()` Decorates the Function" and "What Retry Costs the Signature".
That is more coverage than several already-linked rows get.

Recommended:

> | [Retry](47_Stateless_in_Practice.md#adding-behavior-to-an-existing-effect) | Re-attempt a failed operation, often with backoff. |

Reported rather than applied for one reason only: chapter 47 is being edited
in the same sweep as this one, so the heading could move under me.
Verify the anchor with `uv run python tools/heading_links.py` after applying.
The section title as of this review is exactly
`## Adding Behavior to an Existing Effect`.

---

[] Reject

**"Foundational Idioms": the heading uses "idiom" in a sense chapter 21
defines differently.**

Chapter 21's [Pattern Evolution](21_The_Pattern_Concept.md#pattern-evolution)
gives *idiom* a precise, stage-one meaning:

> **Idiom**: how you write code in a particular language to do this particular
> type of thing.

and gives `with open(...)` as the example, "meaningless outside a language that
provides `with`".
Under that definition Monad, Dependency Injection, Null Object, Specification,
Type Object and Double Dispatch are not idioms.
They are stage-four design patterns that happen not to belong to any of the
five sources above.
Only RAII, Pimpl and CRTP fit chapter 21's sense of the word, and those are
C++ idioms, not Python ones.

Recommended: rename the heading to `## Other Patterns and Idioms`,
which is accurate and keeps the table's mixed contents honest.
Alternatives: `## Cross-Cutting Patterns`, or split the table in two
(language-independent patterns, then language-specific idioms),
which is more precise but costs a second table for three rows.

Nothing links to this heading, so the anchor change is free.
Reported rather than applied because renaming a section is your call.

---

[] Reject

**Foundational Idioms: Service Locator and Dependency Injection both point
away from the chapter that treats them together.**

Chapter 46 has a section titled exactly
[Dependency Injection](46_Stateless.md#dependency-injection), which opens

> Dependency injection (DI) has one goal:
> separate a function from the choice of what it uses.

and then builds `DI_CONTAINER` with `register()` and `resolve()`, which is a
Service Locator in Fowler's sense, before arguing for the ability-based
alternative.

Today the catalog sends Dependency Injection to
`11_Testing.md#isolating-tests-from-the-world`
(a section that is mostly `monkeypatch`, with the real injection example one
subsection down at
[Random Numbers](11_Testing.md#random-numbers)),
and leaves Service Locator unlinked.

Recommended: link Service Locator to `46_Stateless.md#dependency-injection`,
and leave the Dependency Injection row pointing at chapter 11,
so the two rows cover the testing motivation and the container machinery
between them.
Alternative: move Dependency Injection to `46_Stateless.md#dependency-injection`
as well, on the grounds that a section with the pattern's exact name is the
better target, and accept that both rows then point at one place.

Reported rather than applied because chapter 46 is being edited in this same
sweep; re-check the anchor before committing.

---

[] Reject

**Foundational Idioms: five more candidate rows, from chapters the catalog
never reaches.**

Chapters 40, 43, 44, 45, 46 and 47 are unlinked from this catalog, and
chapters 11 and 24 contribute one row each.
Each of the following is a documented pattern the book teaches under that
name.
Listed in descending order of how strongly I would argue for them:

1.  `| [Borg (Monostate)](24_Singleton.md#borg-singleton-by-inheritance) | Let every instance share one set of state instead of sharing one instance. |`
    Chapter 24 devotes a subsection to it and attributes it to Alex Martelli.
    Monostate is its usual name in the literature.
    Sits naturally right after Multiton.
2.  `| [Partial Application](40_Functional_Foundations.md#partial-application) | Fix some of a function's arguments and get a function expecting the rest. |`
    Chapter 40 names and defines it.
    Currying is the neighbouring name a reader may search for; the book does
    not use it, so I would not add a second row.
3.  `| [Function Composition](40_Functional_Foundations.md#composing-functions) | Build a function by feeding one function's output into the next. |`
    Chapter 40 names and defines it.
    The Architectural table's Pipes and Filters is the coarse-grained cousin.
4.  `| [Test Stub](11_Testing.md#network-calls) | Stand in for a real collaborator with a canned answer. |`
    Chapter 11: "A stand-in like `fake_urlopen()` is called a *stub*".
    Meszaros' *xUnit Test Patterns* is a sixth source, though, so adding this
    row without adding the source to the intro paragraph is slightly
    inconsistent.
5.  `| [Effect System](44_Effect_Management.md) | Track in a function's type everything it does besides return a value. |`
    Part V's subject.
    The weakest of the five, because an Effect system is a language feature
    rather than a pattern, and the Monad row already covers the neighbouring
    idea.

Recommended: take 1, 2 and 3, skip 4 and 5.
Reported rather than applied because each is a placement decision, and because
2, 3 and 5 point into chapters being edited in this sweep.

---

[] Reject

**Row format: two small consistency items across all eight tables.**

1.  Acronyms are given for four patterns
    (CQRS, RAII, CRTP, Pimpl) and withheld for three that are at least as
    commonly written short:
    Model-View-Controller (MVC), Presentation-Abstraction-Control (PAC),
    and Data Transfer Object (DTO).
    A reader searching for "DTO" finds nothing.
    Proposed: add the parenthesized acronym to those three, matching the
    existing four.

2.  Most Intent cells are imperative verb phrases
    ("Convert one interface into another a client expects").
    Five are noun-phrase definitions instead:
    Message ("A packet of data sent over a channel"),
    Value Object ("A small immutable object compared by value, not identity"),
    CRTP ("A class inherits from a base parameterized by the class itself"),
    and, before this pass, Function Object.
    For Message and Value Object the noun form is arguably right, since the
    pattern names a thing rather than an action.
    Proposed: leave Message and Value Object, and reword CRTP to
    "Parameterize a base class by the subclass that inherits from it."

Both are reported rather than applied because they are consistency judgements
about the book's voice rather than errors.
(Function Object's Intent was changed in this pass on different grounds: the
old text, "An object whose sole purpose is to wrap a single function," is not
what chapter 28 means by the term and is close to backwards in Python, where a
function already is an object.)

---

[] Reject

**End of chapter: it stops on a table row, and there are no exercises.**

The last thing a reader sees is
`| Pointer to Implementation (Pimpl) | Hide a class's implementation ... |`,
and then Part III is over.
Chapter 39 and chapter 41 are the only two chapters in the book with no
Exercises section, and both are reference chapters, so the absence looks
deliberate for 41 and I would not force one here.

The missing conclusion is a different matter, since this chapter closes
Part III as well as itself.
The "Patterns Python Absorbed" section proposed earlier in this file would
serve as that conclusion.
If you would rather not add a table, three sentences would do:

> Most of the names above will never appear in your code, and that is the
> point of having them collected.
> A catalog is for recognizing a name someone else used,
> and for noticing that the problem in front of you already has a worked
> answer.
> It is not a list of things to build.

If you want exercises after all, two that are answerable from this chapter
plus chapter 21:

1.  Pick three unlinked patterns from the tables above.
    For each, decide whether Python supplies the missing piece the pattern was
    invented to supply, and say which language feature does it.
2.  Two rows in the Structural table describe objects that forward calls to
    something behind them.
    Say what distinguishes them, then check your answer against
    [Telling the Wrappers Apart](29_Changing_the_Interface.md#telling-the-wrappers-apart).

---

## Cross-chapter

[] Reject

**`Chapters/01_Introduction.md`, "How the Book Is Organized": the description
of this chapter is inaccurate.**

01 currently says Part III

> ends by refactoring one problem through several designs,
> building a simulation out of the pieces,
> and cataloging the patterns that the literature added after the classic set.

Chapter 39 catalogs the classic set too: its first three tables are all 23 GoF
patterns, and they run before anything the literature added later.
The sentence tells a reader they can skip the catalog if they only want GoF,
which is the opposite of true.

Change I would make in `Chapters/01_Introduction.md`:

> and cataloging the classic patterns together with the ones the literature
> added later.

I did not touch chapter 01, per the scope rules.

---

[] Reject

**`Chapters/21_The_Pattern_Concept.md`: nothing in the book points at the
catalog.**

Chapter 39 is reachable only from the table of contents.
No chapter links to it, which is odd for a reference chapter, and odd
specifically for chapter 21, whose second paragraph is about catalogs:

> Once you know a catalog of patterns, it is tempting to treat it as a
> checklist, and to install patterns as proof of sophistication.

Chapter 21's closing section, "Reading the Chapters Ahead", is the natural
place: it tells the reader what the chapters ahead do, and the last one is the
catalog.

Change I would make in `Chapters/21_The_Pattern_Concept.md`, appended to
"Reading the Chapters Ahead":

> Part III closes with a [Pattern Catalog](39_Pattern_Catalog.md),
> a name-and-intent index of the wider literature,
> with a link to this book's coverage wherever there is one.

An alternative site is the "checklist" sentence above,
which would make the warning and the catalog point at each other.
I prefer the closing section, because a forward link there is the chapter's
existing job.
I did not touch chapter 21, per the scope rules.

---

[] Reject

**MANIFEST, not a proposal. Applied to `Chapters/39_Pattern_Catalog.md` in
this pass:**

-   Intro, paragraph 2: "a number of them are unnecessary in Python" now carries a named link to [When a Pattern Dissolves](21_The_Pattern_Concept.md#when-a-pattern-dissolves); the catalog had leaned on chapter 21's whole argument without naming it once.
-   Creational: Factory Method retargeted from the chapter root to `27_Factory.md#polymorphic-factories`, the section that matches this row's intent line ("so subclasses choose the concrete type") and the only place chapter 27 treats GoF's Factory Method proper.
-   Structural: Composite retargeted from the chapter root to `34_Composite_and_Interpreter.md#the-classic-composite`, matching the Interpreter row, which already anchors into the same two-pattern chapter.
-   Concurrency: Double-Checked Locking linked to `24_Singleton.md#tests-threads-and-locks`; it was the one unlinked row the book genuinely covers, which contradicted the intro's "An unlinked name means the pattern appears only in this catalog."
-   Concurrency: "Future / Promise" renamed to "Future/Promise" (matching Half-Sync/Half-Async and Leader/Followers in the same table) and retargeted from `#parallelism` to `19_Concurrency.md#one-task-many-backends`, where the book actually teaches what a Future is.
-   Foundational Idioms: Inversion of Control retargeted from the chapter root to `25_Template_Method.md#the-fixed-algorithm`, the paragraph that names the pattern and the Hollywood Principle.
-   Foundational Idioms: Function Object's Intent changed from "An object whose sole purpose is to wrap a single function." to "Decouple the choice of function to call from the place that calls it.", which is chapter 28's own definition; the old text described a wrapper, which is backwards in a language where a function already is an object.

Gates run clean on the chapter after these edits: `heading_links.py`,
`banned_phrases.py`, `prose_lint.py`, `spellcheck.py`,
`reflow_prose.py --diff` (0 paragraphs), and
`validate_output.py --tree build/private/39` (no listings in this chapter).
`heading_links.py` over all of `Chapters/` also passes as of this review.
