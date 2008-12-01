
********************************************************************************
The Pattern Concept
********************************************************************************


"Design patterns help you learn from others' successes instead of your own
failures [#]_."

Probably the most important step forward in object-oriented design is the
"design patterns" movement, chronicled in *Design Patterns (ibid)* [#]_. That
book shows 23 different solutions to particular classes of problems. In this
book, the basic concepts of design patterns will be introduced along with
examples. This should whet your appetite to read *Design Patterns* by Gamma, et.
al., a source of what has now become an essential, almost mandatory, vocabulary
for OOP programmers.

The latter part of this book contains an example of the design evolution
process, starting with an initial solution and moving through the logic and
process of evolving the solution to more appropriate designs. The program shown
(a trash sorting simulation) has evolved over time, and you can look at that
evolution as a prototype for the way your own design can start as an adequate
solution to a particular problem and evolve into a flexible approach to a class
of problems.

What is a Pattern?
=======================================================================

Initially, you can think of a pattern as an especially clever and insightful way
of solving a particular class of problems. That is, it looks like a lot of
people have worked out all the angles of a problem and have come up with the
most general, flexible solution for it. The problem could be one you have seen
and solved before, but your solution probably didn't have the kind of
completeness you'll see embodied in a pattern.

Although they're called "design patterns," they really aren't tied to the realm
of design. A pattern seems to stand apart from the traditional way of thinking
about analysis, design, and implementation. Instead, a pattern embodies a
complete idea within a program, and thus it can sometimes appear at the analysis
phase or high-level design phase. This is interesting because a pattern has a
direct implementation in code and so you might not expect it to show up before
low-level design or implementation (and in fact you might not realize that you
need a particular pattern until you get to those phases).

The basic concept of a pattern can also be seen as the basic concept of program
design: adding a layer of abstraction. Whenever you abstract something you're
isolating particular details, and one of the most compelling motivations behind
this is to *separate things that change from things that stay the same*. Another
way to put this is that once you find some part of your program that's likely to
change for one reason or another, you'll want to keep those changes from
propagating other changes throughout your code. Not only does this make the code
much cheaper to maintain, but it also turns out that it is usually simpler to
understand (which results in lowered costs).

Often, the most difficult part of developing an elegant and cheap-to-maintain
design is in discovering what I call "the vector of change." (Here, "vector"
refers to the maximum gradient and not a container class.) This means finding
the most important thing that changes in your system, or put another way,
discovering where your greatest cost is. Once you discover the vector of change,
you have the focal point around which to structure your design.

So the goal of design patterns is to isolate changes in your code. If you look
at it this way, you've been seeing some design patterns already in this book.
For example, inheritance can be thought of as a design pattern (albeit one
implemented by the compiler). It allows you to express differences in behavior
(that's the thing that changes) in objects that all have the same interface
(that's what stays the same). Composition can also be considered a pattern,
since it allows you to change-dynamically or statically-the objects that
implement your class, and thus the way that class works.

Another pattern that appears in *Design Patterns* is the *iterator*, which has
been implicitly available in **for** loops from the beginning of the language,
and was introduced as an explicit feature in Python 2.2. An iterator allows you
to hide the particular implementation of the container as you're stepping
through and selecting the elements one by one. Thus, you can write generic code
that performs an operation on all of the elements in a sequence without regard
to the way that sequence is built. Thus your generic code can be used with any
object that can produce an iterator.

Classifying Patterns
===============================================================================

The *Design Patterns* book discusses 23 different patterns, classified under
three purposes (all of which revolve around the particular aspect that can
vary). The three purposes are:

1.  **Creational**: how an object can be created. This often involves isolating
    the details of object creation so your code isn't dependent on what types of
    objects there are and thus doesn't have to be changed when you add a new type of
    object. The aforementioned *Singleton* is classified as a creational pattern,
    and later in this book you'll see examples of *Factory Method* and *Prototype*.

2.  **Structural**: designing objects to satisfy particular project constraints.
    These work with the way objects are connected with other objects to ensure that
    changes in the system don't require changes to those connections.

3.  **Behavioral**: objects that handle particular types of actions within a
    program. These encapsulate processes that you want to perform, such as
    interpreting a language, fulfilling a request, moving through a sequence (as in
    an iterator), or implementing an algorithm. This book contains examples of the
    *Observer* and the *Visitor* patterns.

The *Design Patterns* book has a section on each of its 23 patterns along with
one or more examples for each, typically in C++ but sometimes in Smalltalk.
(You'll find that this doesn't matter too much since you can easily translate
the concepts from either language into Python.) This book will not repeat all
the patterns shown in *Design Patterns* since that book stands on its own and
should be studied separately. Instead, this book will give some examples that
should provide you with a decent feel for what patterns are about and why they
are so important.

After years of looking at these things, it began to occur to me that the
patterns themselves use basic principles of organization, other than (and more
fundamental than) those described in *Design Patterns*. These principles are
based on the structure of the implementations, which is where I have seen great
similarities between patterns (more than those expressed in *Design Patterns*).
Although we generally try to avoid implementation in favor of interface, I have
found that it's often easier to think about, and especially to learn about, the
patterns in terms of these structural principles. This book will attempt to
present the patterns based on their structure instead of the categories
presented in *Design Patterns*.

Pattern Taxonomy
=======================================================================

One of the events that's occurred with the rise of design patterns is what could
be thought of as the "pollution" of the term - people have begun to use the term
to mean just about anything synonymous with "good." After some pondering, I've
come up with a sort of hierarchy describing a succession of different types of
categories:

#.  **Idiom**: how we write code in a particular language to do this particular
    type of thing. This could be something as common as the way that you code
    the process of stepping through an array in C (and not running off the end).

#.  **Specific Design**: the solution that we came up with to solve this
    particular problem. This might be a clever design, but it makes no attempt
    to be general.

#.  **Standard Design**: a way to solve this *kind* of problem. A design that
    has become more general, typically through reuse.

#.  **Design Pattern**: how to solve an entire class of similar problem. This
    usually only appears after applying a standard design a number of times, and
    then seeing a common pattern throughout these applications.

I feel this helps put things in perspective, and to show where something might
fit. However, it doesn't say that one is better than another. It doesn't make
sense to try to take every problem solution and generalize it to a design
pattern - it's not a good use of your time, and you can't force the discovery of
patterns that way; they tend to be subtle and appear over time.

One could also argue for the inclusion of *Analysis Pattern* and *Architectural
Pattern* in this taxonomy.

Design Structures
=======================================================================

One of the struggles that I've had with design patterns is their classification
- I've often found the GoF approach to be too obscure, and not always very
helpful. Certainly, the *Creational* patterns are fairly straightforward: how
are you going to create your objects? This is a question you normally need to
ask, and the name brings you right to that group of patterns. But I find
*Structural* and *Behavioral* to be far less useful distinctions. I have not
been able to look at a problem and say "clearly, you need a structural pattern
here," so that classification doesn't lead me to a solution (I'll readily admit
that I may be missing something here).

I've labored for awhile with this problem, first noting that the underlying
structure of some of the GoF patterns are similar to each other, and trying to
develop relationships based on that similarity. While this was an interesting
experiment, I don't think it produced much of use in the end because the point
is to solve problems, so a helpful approach will look at the problem to solve
and try to find relationships between the problem and potential solutions.

To that end, I've begun to try to collect basic design structures, and to try to
see if there's a way to relate those structures to the various design patterns
that appear in well thought-out systems. Currently, I'm just trying to make a
list, but eventually I hope to make steps towards connecting these structures
with patterns (or I may come up with a different approach altogether - this is
still in its formative stages).

Here [#]_ is the present list of candidates, only some of which will make it to
the final list. Feel free to suggest others, or possibly relationships with
patterns.

* **Encapsulation**: self containment and embodying a model of usage
* **Gathering**
* **Localization**
* **Separation**
* **Hiding**
* **Guarding**
* **Connector**
* **Barrier/fence**
* **Variation in behavior**
* **Notification**
* **Transaction**
* **Mirror**: "the ability to keep a parallel universe(s) in step with the
    golden world"
* **Shadow**: "follows your movement and does something different in a different
    medium" (May be a variation on Proxy).

Design Principles
=======================================================================

When I put out a call for ideas in my newsletter [#]_, a number of suggestions
came back which turned out to be very useful, but different than the above
classification, and I realized that a list of design principles is at least as
important as design structures, but for a different reason: these allow you to
ask questions about your proposed design, to apply tests for quality.

*   **Principle of least astonishment** (don't be astonishing).

*   **Make common things easy, and rare things possible**

*   **Consistency**. One thing has become very clear to me, especially because of
    Python: the more random rules you pile onto the programmer, rules that have
    nothing to do with solving the problem at hand, the slower the programmer can
    produce. And this does not appear to be a linear factor, but an exponential one.

*   **Law of Demeter**: a.k.a. "Don't talk to strangers." An object should only
    reference itself, its attributes, and the arguments of its methods. This may
    also be a way to say "minimize coupling."

*   **Independence** or **Orthogonality**. Express independent ideas independently.
    This complements Separation, Encapsulation and Variation, and is part of the
    Low-Coupling-High-Cohesion message.

*   **Managed Coupling**. Simply stating that we should have "low coupling" in a
    design is usually too vague - coupling happens, and the important issue is to
    acknowledge it and control it, to say "coupling can cause problems" and to
    compensate for those problems with a well-considered design or pattern.

*   **Subtraction**: a design is finished when you cannot take anything else away
    [#]_.

*   **Simplicity before generality** [#]_. (A variation of *Occam's Razor*, which
    says "the simplest solution is the best"). A common problem we find in
    frameworks is that they are designed to be general purpose without reference to
    actual systems. This leads to a dizzying array of options that are often unused,
    misused or just not useful. However, most developers work on specific systems,
    and the quest for generality does not always serve them well. The best route to
    generality is through understanding well-defined specific examples. So, this
    principle acts as the tie breaker between otherwise equally viable design
    alternatives. Of course, it is entirely possible that the simpler solution is
    the more general one.

*   **Reflexivity** (my suggested term). One abstraction per class, one class per
    abstraction. Might also be called Isomorphism.

*   **Once and once only**: Avoid duplication of logic and structure where the
    duplication is not accidental, ie where both pieces of code express the same
    intent for the same reason.

In the process of brainstorming this idea, I hope to come up with a small
handful of fundamental ideas that can be held in your head while you analyze a
problem. However, other ideas that come from this list may end up being useful
as a checklist while walking through and analyzing your design.

.. rubric:: Footnotes

.. [#] From Mark Johnson.

.. [#] But be warned: the examples are in C++.

.. [#] This list includes suggestions by Kevlin Henney, David Scott, and others.

.. [#] A free email publication. See *www.BruceEckel.com* to subscribe.

.. [#]  This idea is generally attributed to Antoine de St. Exupery from *The
        Little Prince*\: "La perfection est atteinte non quand il ne reste rien à
        ajouter, mais quand il ne reste rien à enlever," or: "perfection is reached not
        when there's nothing left to add, but when there's nothing left to remove".

.. [#] From an email from Kevlin Henney.



