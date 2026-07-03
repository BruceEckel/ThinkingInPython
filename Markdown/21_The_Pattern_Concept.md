# The Pattern Concept

An important step forward in object-oriented design was the "design patterns" movement,
chronicled in the 1994 book *Design Patterns* by Erich Gamma, Richard Helm, Ralph Johnson, and John Vlissides.
They became known as the "Gang of Four"^[A reference to Chinese politics ... it made sense at the time.].
I will refer to that book as *GoF Design Patterns*, and use *design patterns* for the concept.

*GoF Design Patterns* shows 23 different solutions to particular classes of problems,
along with one or more examples for each, typically in C++ but sometimes in Smalltalk.
A significant portion of those examples provide inspiration for much of the remainder of this book.
I will introduce the basic concepts of design patterns, along with examples.

## What Is a Pattern?

Initially, you can think of a pattern as an especially clever and insightful way of solving a particular class of problems.
It looks like a lot of people have worked out all the angles of a problem and have come up with the most general,
flexible solution.
You may have seen and solved something like it before,
but your solution probably doesn't have the kind of completeness you'll see embodied in a pattern.

Although they're called "design patterns,"
they really aren't tied to the realm of design.
A pattern seems to stand apart from the traditional way of thinking about analysis,
design, and implementation.
Instead, a pattern embodies a complete idea within a program,
and thus it can sometimes appear at the analysis phase or high-level design phase.
This is interesting because a pattern has a direct implementation in code,
so you might not expect it to show up before low-level design or implementation.

The basic concept of a pattern can also be seen as the basic concept of program design:
adding a layer of abstraction.
Whenever you abstract something, you isolate particular details.
One of the most compelling motivations behind this is to *separate things that change from things that stay the same*.
Once you find some part of your program that's likely to change for one reason or another,
you prevent those changes from propagating other changes throughout your code.
Not only does this make the code much cheaper to maintain,
but it is also usually simpler to understand (which results in lowered costs).

Often, the most difficult part of developing an elegant and cheap-to-maintain design is in discovering what I call "the vector of change"
(here, "vector" refers to the maximum gradient and not a container class).
This means finding the most important thing that changes in your system,
which points to your greatest cost.
Once you discover the vector of change,
you have the focal point around which to structure your design.

The goal of design patterns is to isolate changes in your code.
If you look at it this way,
you've already seen some design patterns in this book.
For example, inheritance can be thought of as a design pattern (albeit one implemented by the compiler).
It allows you to express differences in behavior (that's the thing that changes) in objects that all have the same interface (that's what stays the same).
Composition can also be considered a pattern, since it allows you to change,
dynamically or statically, the objects that implement your class,
and thus the way that class works.

Another pattern that appears in *GoF Design Patterns* is the [Iterator](27_Iterators.md),
which has been implicitly available in `for` loops from the beginning of the language,
and was introduced as an explicit feature in Python 2.2.
An iterator allows you to hide the particular implementation of the container as you're stepping through.
You can write generic code that performs an operation on all of the elements in a sequence without regard to the way that sequence is built.
Your generic code can be used with any object that produces an iterator.

## Pattern Evolution

1.  **Idiom**: how we write code in a particular language to do this particular type of thing.
    This could be something as common as the way that you code the process of stepping through an array in C (and not running off the end).
2.  **Specific Design**:
    the solution that we came up with to solve this particular problem.
    This might be a clever design, but it makes no attempt to be general.
3.  **Standard Design**: a way to solve this *kind* of problem.
    A design that has become more general, typically through reuse.
4.  **Design Pattern**: how to solve an entire class of similar problems.
    This usually only appears after applying a standard design a number of times,
    and then seeing a common pattern throughout these applications.

This doesn't say that one is better than another.
It doesn't make sense to try to take every problem solution and generalize it to a design pattern.
That's not a good use of your time, and you can't force the discovery of patterns that way.
They tend to be subtle and appear over time.

## Pattern Taxonomy

*GoF Design Patterns* discusses 23 different patterns,
classified under three purposes (all of which revolve around the particular aspect that can vary).
The three purposes are:

1.  **Creational**: how an object can be created.
    By isolating the details of object creation,
    your code isn't dependent on what types of objects there are and thus doesn't have to be changed when you add a new type of object.
    [Singleton](23_Singleton.md) is classified as a creational pattern,
    and later in this book you'll see examples of [Factories](28_Factory.md).
2.  **Structural**: designing objects to satisfy particular project constraints.
    These work with the way objects are connected with other objects to ensure that changes in the system don't require changes to those connections.
3.  **Behavioral**: objects that handle particular types of actions within a program.
    These encapsulate processes such as interpreting a language, fulfilling a request,
    moving through a sequence (as in an iterator), or implementing an algorithm.
    This book contains multiple examples including [Observer](31_Observer.md),
    [State Machines](26_State_Machines.md), and [Visitor](33_Visitor.md).

I've found the *GoF Design Patterns* classification to be too obscure,
and not always helpful.
Certainly, the *Creational* patterns are fairly straightforward:
how are you going to create your objects?
This is a question you normally need to ask,
and the name brings you right to that group of patterns.
But I find *Structural* and *Behavioral* to be far less useful distinctions.
I have not been able to look at a problem and say "clearly,
you need a structural pattern here,"
so that classification doesn't lead me to a solution (I'll readily admit that I may be missing something here).

I think the patterns themselves use basic principles of organization,
other than (and more fundamental than) those described in *GoF Design Patterns*.
These principles are based on the structure of the implementations,
which is where I have seen great similarities between patterns (more than those expressed in *GoF Design Patterns*).
Although we generally try to avoid implementation in favor of interface,
I have found that it's often easier to think about,
and especially to learn about,
the patterns in terms of these structural principles.
This book attempts to present the patterns based on their structure instead of the categories presented in *GoF Design Patterns*.

I've labored for a while with this problem,
first noting that the underlying structure of some of the *GoF Design Patterns* are similar to each other,
and trying to develop relationships based on that similarity.
I've collected some basic design structures,
to see if there's a way to relate those structures to the various design patterns that appear in well thought-out systems.

Here^[This list includes suggestions by Kevlin Henney, David Scott, and others.] is a list of candidates:

-   **Encapsulation**: self containment and embodying a model of usage
-   **Gathering**
-   **Localization**
-   **Separation**
-   **Hiding**
-   **Guarding**
-   **Connector**
-   **Barrier/fence**
-   **Variation in behavior**
-   **Notification**
-   **Transaction**
-   **Mirror**: "the ability to keep a parallel universe(s) in step with the golden world"
-   **Shadow**: "follows your movement and does something different in a different medium" (May be a variation on [Proxy](25_Surrogate.md#proxy)).

## Design Principles

Design principles are at least as important as design structures,
but for a different reason:
principles ask questions about your proposed design,
to apply tests for quality.
Some of these only apply to OOP.

-   *Principle of least astonishment* (don't be astonishing).
-   *Make common things easy, and rare things possible*.
-   *Consistency*.
    The more random rules you pile onto the programmer,
    rules that have nothing to do with solving the problem at hand,
    the slower the programmer can produce.
    This does not appear to be a linear factor, but an exponential one.
-   *Law of Demeter*: a.k.a.
    "Don't talk to strangers."
    An object should only reference itself, its attributes,
    and the arguments of its methods.
    This may also be a way to say "minimize coupling."
-   *Independence* or *Orthogonality*.
    Express independent ideas independently.
    This complements Separation, Encapsulation and Variation,
    and is part of the Low-Coupling-High-Cohesion message.
-   *Managed Coupling*.
    Simply declaring that we should have "low coupling" in a design is usually too vague;
    coupling happens, and the important issue is to acknowledge it and control it,
    to say "coupling can cause problems" and to compensate for those problems with a well-considered design or pattern.
-   *Subtraction*: a design is finished when you cannot take anything else away^[Generally attributed to Antoine de Saint-Exupéry, from *Wind, Sand and Stars*: "perfection is reached not when there's nothing left to add, but when there's nothing left to remove".].
-   *Simplicity before generality*^[From an email from Kevlin Henney.].
    A common problem we find in frameworks is that they are designed to be general purpose without reference to actual systems.
    This leads to a dizzying array of options that are often unused,
    misused or not useful.
    However, most developers work on specific systems,
    and the quest for generality does not always serve them well.
    The best route to generality is through understanding well-defined specific examples.
    This principle acts as the tie breaker between otherwise equally viable design alternatives.
    The simpler solution may also turn out to be the more general one.
-   *Reflexivity*.
    One abstraction per class, one class per abstraction.
    Might also be called Isomorphism.
-   *Once and once only*:
    Avoid duplication of logic and structure where the duplication is not accidental,
    i.e., where both pieces of code express the same intent for the same reason.
-   *Make things as immutable as possible*, as described in [Data Classes as Types](12_Data_Classes_as_Types.md#immutability).
-   *Make functions pure whenever you can*.

This is a small handful of fundamental ideas that can be held in your head while walking through and analyzing your design.
