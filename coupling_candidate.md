<!-- Candidate section for Chapters/21_Patterns--Design_Patterns.md,
     between "Pattern Taxonomy" and "Design Principles", so that the
     "Managed Coupling" and "Design the communication" principles have
     a section to point back at. Everything under "Notes on the figures"
     at the end is for choosing among the figures and is not book text.
     The figures are resources/images/coupling_*.svg; the _images/ links
     below resolve once the section is in a chapter. -->

## Coupling

Every pattern in *GoF Design Patterns* answers one question:
what does one part of a program know about another?
Its first chapter lists eight "common causes of redesign"
and names the patterns that address each one.
Six of the eight are a dependence of one part on another:
on a class name, on a specific operation, on a platform,
on an object's representation, on an algorithm,
or on each other, which the list calls *tight coupling*.
The other two, extending by subclassing and being unable to alter a class,
are about what a dependence costs once it exists.
The glossary defines coupling as
"the degree to which software components depend on each other,"
and the chapter's two design principles are both instructions to loosen one particular dependence.
"Program to an interface, not an implementation"
says stop naming concrete classes.
"Favor object composition over class inheritance"
says stop inheriting implementations.
*GoF Design Patterns* has a name for the result, *abstract coupling*:
a class that holds a reference to an abstract class
"refers to a *type* of object, not a concrete object."
Read this way, the catalog is one idea applied twenty-three times.
GoF's own discussion of the behavioral patterns ranks four of them by it:
*Command*, *Observer*, *Mediator*, and *Chain of Responsibility*
each decouple a sender from a receiver, "but with different trade-offs,"
and *Observer* "defines a looser sender-receiver binding than *Command*."

This section makes that measure visible.
Once you can see coupling, the patterns in the chapters ahead stop being twenty-three shapes to memorize
and become a few moves applied to one kind of diagram.

### What One Part Knows About Another

Coupling has degrees.
The question is not whether one part depends on another,
since a program whose parts do not depend on each other does nothing,
but how much of the other part the dependence reaches.

![Six degrees of what one part knows about another, from inheriting its internals down to receiving a value](_images/coupling_ladder)

Each rung is something the dependent part knows.
A subclass knows its parent's internals:
which methods call which, the attributes' names,
what a `super()` call expects to find.
A change to any of that can reach the subclass,
which is why *GoF Design Patterns* says inheritance "breaks encapsulation."
A caller that writes `Circle(2)` knows a name and a constructor signature,
and a caller that writes `isinstance(s, Circle)` knows the name and reads its type.
A caller written against an abstract base class knows a set of method names and signatures,
and every class that joins that set says so in its own `class` line.
A caller written against a `Protocol` knows the same set of names,
but nothing joins;
the type checker matches shapes.
A caller that takes a `Callable` knows one signature.
A caller that takes a value knows the value's type and nothing about who produced it.

The rung a dependence sits on decides how far a change travels.
If you rename a method on a class that other code subclasses,
the subclasses break.
If you rename it on a class that other code reaches through a `Protocol`,
the callers keep working while the protocol keeps its name,
and when the protocol changes too,
the type checker names each place that stopped matching.

Two rungs come free in Python.
An abstract base class is a class you write and every implementer inherits.
A `Protocol` is a class you write and nothing inherits,
and a `Callable` annotation is not a class at all.
That is the mechanism behind
[When a Pattern Dissolves](21_Patterns--Design_Patterns.md#when-a-pattern-dissolves):
a pattern that exists to build the third rung in a language that has only the first two
has nothing left to build in a language that supplies the fourth and fifth.

### A Pattern Moves an Edge

Draw a design as parts and the edges between them,
and let the edge say what the dependent part knows.
A heavy edge names a concrete class.
A thin edge names an interface.
A dashed edge with a hollow head says the part satisfies that interface.
With those three edges alone, six GoF patterns look like this:

![Six patterns drawn only as coupling: which part names a concrete class, which names an interface, and which satisfies one](_images/coupling_gallery)

The red box in each panel is the part the pattern keeps free of change.
Read the heavy edges first, because they are where a change reaches.

*Strategy* has none.
The context names an interface and each algorithm satisfies it,
so adding an algorithm changes nothing that exists.

*Observer* has one, and it points from the observer to the subject.
An observer must know its subject to attach to it.
The subject knows no observer:
"All a subject knows is that it has a list of observers,
each conforming to the simple interface of the abstract `Observer` class."
The heavy edge points at the part that changes least,
which is where a heavy edge belongs.

*Factory Method* does not remove the heavy edge either.
Something must name a class to construct it.
The pattern moves that name out of the client and into a creator,
a part whose whole job is to hold the name
and on which nothing else depends.

*Adapter* moves the heavy edge inside the adapter.
The client sees the target interface,
and the one class that knows the adaptee's real name is the adapter,
so a change to the adaptee reaches one file.

*Decorator* has no heavy edge at all.
A topping satisfies the component interface and also holds one,
so it can wrap a pizza or another topping without naming either.

*Visitor* is the reverse of the others.
The visitor names every concrete element.
The pattern concentrates the heavy edges in one place on purpose:
adding an operation means writing one new visitor and changing nothing else,
while adding an element type means changing every visitor.
[*Visitor*](33_Patterns--Visitor.md) is that trade,
and the diagram shows what you are trading.

Seen this way, the patterns differ less in how much coupling they carry
than in where they put it and which way it points.
A heavy edge is acceptable when it sits in a part that is cheap to change,
or points at a part that rarely changes.
That is the content of the *Managed Coupling* principle below:
coupling you can see and have placed on purpose.

### The Reach of a Change

Coupling matters because of what it does when something changes.
Here is a small design twice.
A `Report` renders itself through a writer,
and `main` assembles the pieces.
On the left, `Report` names each writer class and chooses between them.
On the right, `Report` names a `Writer` protocol.
Then a Markdown writer arrives.

![Adding a writer reaches two parts when Report names each writer, and one when Report names a protocol](_images/coupling_reach)

The shaded parts are the ones whose source changes.
On the left, `Report` gains a branch and `main` gains a case.
On the right, `Report` keeps its source,
because the new writer satisfies the protocol and `Report` named no writer.
`main` still changes, since something must construct the new class.
A registry factory ([Factory](27_Patterns--Factory.md#self-registration))
takes that last change out too,
by letting the new class register itself as its `class` statement runs.

The same two designs as a dependency matrix show the move as a shift in a table:

![The same two designs as dependency matrices: a row is a part, a filled cell is a part it names, and the protocol design confines the filled cells to one column](_images/coupling_matrix)

A row is a part and a filled cell is something it names.
On the left, the concrete names spread across two rows.
On the right, every concrete name sits in one row, `main`'s.
The `Writer` column holds the rest:
one outlined cell where `Report` names the protocol,
and three dashed cells that the type checker fills in and no file writes.
A design's coupling is the pattern of filled cells,
and a pattern moves cells:
usually out of the rows that change often
and into one row you can find.

### The Edge Python Deletes

One more diagram explains why so many of the chapters ahead subtract code as they go.
Take a caller that needs an `area()` from whatever it receives,
and write the same dependence three ways.

![The same dependency written three ways: an ABC needs two edges in source, a Protocol one, and a Callable none outside the caller](_images/coupling_edges)

With an abstract base class, two edges exist in source:
the caller names `Shape`, and `Circle` names `Shape` in its `class` line.
With a `Protocol`, one edge exists in source.
`Circle` does not mention `Shape`,
and the dotted edge is one the type checker draws at check time,
when it compares `Circle`'s members with the protocol's.
With a `Callable`, the interface has no name and no file of its own.
It lives in the caller's signature,
and any function of the right shape satisfies it.

The edge a `Protocol` deletes is the one that in C++ or Java is mandatory:
the implementer must name the interface.
That edge makes an interface a thing on which every implementer depends,
so that renaming it or moving it touches every file that names it.
[Rethinking Objects](20_Patterns--Rethinking_Objects.md#protocols-generalize-composition-adapts)
makes the same point about types "in libraries you cannot edit,"
and this is its general form:
the fewer edges in source, the fewer files a change can reach.

One question serves for every chapter ahead.
Which edge does this pattern move, and where does it put it?

### Exercises (candidates for the chapter's list)

1.  Draw a design of your own with the three kinds of edge.
    Count the heavy ones.
    For each, say whether it points at a part that changes rarely
    or sits in a part that is cheap to change.
    Any heavy edge that does neither is a place a pattern might apply.
2.  Take the `Report` design and add the registry factory.
    Redraw the matrix.
    Which row empties, and what does `main` know now?

## Notes on the figures (not for the book)

Five candidates, all in `resources/images/coupling_*.svg`,
drawn in the existing figure vocabulary
(no width or height on the `viewBox`, JetBrains Mono, the cover palette,
red for the class the figure is about, dashed for a box the listing lacks).
The source that generated them is a scratch script;
the SVGs are the artifact.
I rasterized each one the way the EPUB does and checked for collisions.

1.  **`coupling_ladder`**, six rungs of what one part knows about another.
    This one carries the section's vocabulary,
    so if only one figure survives, it should be this one.
    The pattern placements on the right are debatable
    (*Surrogate* sits at the `Protocol` rung because chapter 26 uses one;
    chapter 27's factories sit at the ABC rung because `Shape(ABC)` does).
2.  **`coupling_gallery`**, six patterns in coupling-only notation.
    This is the "see the patterns as nothing but their coupling" idea.
    Six panels is the most the width allows at a readable size;
    these six show 0, 1-toward-stable, 1-moved, 1-contained, 0, and many.
    It could split into two three-panel figures,
    or become a running motif with one panel per pattern chapter.
3.  **`coupling_reach`**, before and after, with the changed parts shaded.
    The most direct "why care" picture.
4.  **`coupling_matrix`**, the same before and after as a dependency matrix.
    This is the design-structure-matrix view.
    It scales to more parts than the graph does and makes "one column" literal,
    but it is the least familiar notation.
    Figures 3 and 4 say the same thing; the section needs one, not both.
5.  **`coupling_edges`**, nominal versus structural versus callable,
    counting edges in source.
    This is the Python-specific claim and the one no other book makes,
    so it may stay when 3 or 4 goes.

A sixth option not drawn: one gallery panel per chapter,
placed at the top of each pattern chapter,
so the whole part becomes a flip-book of the same diagram.
