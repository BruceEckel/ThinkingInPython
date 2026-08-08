# The Pattern Concept

An important step forward in object-oriented design was the "design patterns" movement,
carried into the mainstream by the 1994 book *Design Patterns* by Erich Gamma,
Richard Helm, Ralph Johnson, and John Vlissides.
They became known as the "Gang of Four"^[A wry nod to the Chinese political faction of the same name.].
I will refer to that book as *GoF Design Patterns*,
and use *design patterns* for the concept.

*GoF Design Patterns* shows 23 different solutions to particular classes of problems,
along with one or more examples for each,
typically in C++ but sometimes in Smalltalk.
Many of those examples inspired the ones in this part of the book.
This chapter introduces the concepts; one listing makes the point,
and the chapters after it supply the rest of the code.

## What Is a Pattern?

Initially, you can think of a pattern as an especially clever and insightful way of solving a particular class of problems.
Many people have worked out all the angles of a problem and have come up with the most general,
flexible solution.
You may have seen and solved something like it before,
but your solution probably doesn't have the kind of completeness you'll see embodied in a pattern.

That completeness has a failure mode.
Once you know a catalog of patterns, it is tempting to treat it as a checklist,
and to install patterns as proof of sophistication.
A pattern earns its place only when the problem it solves is present.
If nothing varies, you do not need machinery for isolating variation.

Although they're called "design patterns," they aren't tied to design.
Patterns seem to stand apart from the traditional way of thinking about analysis,
design, and implementation.
Instead, a pattern embodies a complete idea within a program.
It can therefore appear at the analysis phase or high-level design phase,
where you are still describing what the system does rather than how it is built.
Because a pattern has a direct implementation in code,
you might expect it to appear no earlier than low-level design.
But it appears at every level,
and you often discover that you need one only once you reach the code.

The basic concept of a pattern is also the basic concept of program design:
adding a layer of abstraction.
Whenever you abstract something, you isolate particular details.
One of the most compelling motivations behind this is to *separate things that change from things that stay the same*.
Once you find a part of your program that's likely to change,
patterns can prevent those changes from causing secondary effects throughout your code.
This makes the code cheaper to maintain and usually simpler to understand.

Often, the most difficult part of developing an elegant and cheap-to-maintain design is discovering what I call "the vector of change"
(here, "vector" means a direction of change, not an array of numbers).
This means finding the most important thing that changes in your system,
which points to your greatest cost.
Once you discover the vector of change,
you have the focal point around which to structure your design.

A vector of change is discovered, not predicted.
Guessing at it up front often builds complexity for flexibility in a direction that doesn't get used.
The second time a requirement shifts the same part of the design,
you have evidence.

The goal of design patterns is to isolate changes in your code.
You have seen some design patterns in this book.
For example, [inheritance](07_Classes.md) can be thought of as a design pattern
(albeit one built into the language).
It allows you to express differences in behavior (that's the thing that changes)
in objects that all have the same interface (that's what stays the same).
[Composition](20_Rethinking_Objects.md#prefer-composition-to-inheritance)
also qualifies as a pattern, since it allows you to change,
dynamically or statically, the objects that implement your class,
and thus the way that class works.

Another pattern that appears in *GoF Design Patterns* is the [Iterator](23_Iterators.md).
An iterator allows you to hide the particular implementation of the container as you're stepping through it.
You can write generic code that performs an operation on all the elements in a sequence without regard to that sequence's construction.
The code works with any object that produces an iterator.

## Pattern Evolution

A pattern arrives in stages, each more general than the last:

1.  **Idiom**: how you write code in a particular language to do this particular type of thing.
    This could be something as common as the way that you code the process of stepping through an array in C
    (and not running off the end).
2.  **Specific Design**:
    the solution that arose to solve this particular problem.
    This might be a clever design, but it makes no attempt to be general.
3.  **Standard Design**: a way to solve every problem of that kind,
    not just the one in front of you.
    A design that has become more general, typically through reuse.
4.  **Design Pattern**: how to solve an entire class of similar problems.
    This usually only appears after applying a standard design a number of times,
    and then seeing a common pattern throughout these applications.

In Python terms: `with open(...)` for guaranteed cleanup is an idiom, stage one,
meaningless outside a language that provides `with`.
A dictionary mapping one program's shape names to its shape classes is a specific design,
stage two.
The same dictionary,
filled by each subclass as it is defined so that adding a type never edits the factory,
is a standard design, stage three ([Factory](27_Factory.md) builds both).
[Template Method](25_Template_Method.md) is a design pattern, stage four:
a shape of solution you could build in any language with polymorphism.

This progression doesn't say that one stage is better than another.
It doesn't make sense to try to take every problem solution and generalize it to a design pattern.
You can't force the discovery of patterns that way.
They tend to be subtle and appear over time.

The ladder runs downward too.
A pattern a language builds in drops back to stage one,
and the programmers who arrive next learn it as syntax rather than as a design.
Stepping through a container is stage one in Python and was stage four in the *GoF Design Patterns* examples.

## When a Pattern Dissolves

A pattern is often a sign of something missing in a language.
Programmers wrote the same scaffolding often enough that it acquired a name.
It exists only because the language does not write it for them.

A pattern meets its missing piece in two ways.
Sometimes a language grows the feature and the pattern dissolves into it^[Peter Norvig made this observation in his 1996 talk "Design Patterns in Dynamic Programming": 16 of the 23 GoF patterns become invisible or simpler in a dynamic language. He counted for Lisp and Dylan, and Python's line falls in a different place. Singleton is one of the seven he leaves standing, but [Singleton](24_Singleton.md)
shows that a Python module already is one.].
Iterator is the clear case.
It was implicit in the `for` loop from the start,
and Python 2.2 made it a protocol the language calls on your behalf.
More often the language had the piece all along,
and the pattern was written for one that didn't.
*Strategy* and *Command* shrink to passing a function,
because a Python function is an object
([Function Objects](28_Function_Objects.md) shows both).
A [Factory](27_Factory.md) becomes a dictionary,
because a class is an object too.
[Singleton](24_Singleton.md) becomes a module,
because Python imports each module once and caches it.

Here is the whole of a *Strategy* in Python:

```python
# strategy_is_a_function.py
from collections.abc import Callable

def apply(nums: list[int], how: Callable[[list[int]], int]) -> int:
    return how(nums)
print(apply([3, 1, 2], max), apply([3, 1, 2], sum))
#: 3 6
```

The classic form declares a `Strategy` interface,
writes one class per algorithm, and adds a context class to hold the chosen one.
The `how` parameter replaces all three.

This is why the chapters ahead keep asking the question [Rethinking Objects](20_Rethinking_Objects.md#guidelines)
posed: how much of each pattern's machinery does Python still need,
and how much of it becomes functions, data, and protocols?

## Pattern Taxonomy

*GoF Design Patterns* discusses 23 different patterns,
classified under three purposes
(all of which revolve around the particular aspect that can vary).
The three purposes are:

1.  **Creational**: how to create an object.
    By isolating the details of object creation,
    your code isn't dependent on what types of objects there are and thus won't change when you add a new type of object.
    [Singleton](24_Singleton.md) counts as a *Creational* pattern,
    and later in this book you'll see [Factory](27_Factory.md)
    methods and factory classes.
2.  **Structural**: designing objects to satisfy particular project constraints.
    How objects connect with other objects to ensure that changes in the system don't require changes to those connections.
    [Surrogate](26_Surrogate.md),
    [Changing the Interface](29_Changing_the_Interface.md),
    [Composite and Interpreter](34_Composite_and_Interpreter.md),
    [Flyweight](35_Flyweight.md),
    and [Decorators](14_Decorators.md#the-decorator-pattern)
    cover the structural patterns in this book.
3.  **Behavioral**: objects that handle particular types of actions within a program.
    These encapsulate processes such as interpreting a language,
    fulfilling a request, moving through a sequence (as in an iterator),
    or implementing an algorithm.
    This book contains multiple examples including [Observer](30_Observer.md),
    [State](26_Surrogate.md#state), and [Visitor](33_Visitor.md),
    though *State* appears beside *Proxy*, for reasons given below.

I've found the *GoF Design Patterns* classification to be too obscure,
and not always helpful.
Certainly, the *Creational* patterns are fairly straightforward.
How will you create objects?
This is a normal question,
and the name brings you right to that group of patterns.
But I find *Structural* and *Behavioral* to be far less useful distinctions.
I have not been able to look at a problem and say "clearly,
you need a structural pattern here,"
so that classification doesn't lead me to a solution
(I'll readily admit that I may be missing something here).

Patterns often resemble each other more in their implementations than the *GoF Design Patterns* categories suggest,
and that is how this book groups them.
[Surrogate](26_Surrogate.md)
treats *Proxy* and *State* as one front-object structure.
[Function Objects](28_Function_Objects.md) treats *Command*, *Strategy*,
and *Chain of Responsibility* as one function-passing structure.
[Composite and Interpreter](34_Composite_and_Interpreter.md)
treats both of its patterns as one recursive-data structure.
When two patterns share a structure, learning one teaches you most of the other,
and the remaining difference is intent.

## Design Principles

Design principles are at least as important as design patterns,
but they do a different job.
A pattern is a shape of solution.
A principle is a test you apply to whatever shape you chose:
a claim you can hold the design up against.
Most hold for any code,
but *Reflexivity* and the *Law of Demeter* assume classes and objects.

-   *Principle of least astonishment* (don't be astonishing).
-   *Make common things easy, and rare things possible*.
-   *Consistency*.
    The more random rules you pile onto the programmer,
    rules that have nothing to do with solving the problem at hand,
    the slower the programmer can produce.
    The cost does not grow one rule at a time; the rules interact.
-   *Law of Demeter*: a.k.a. "Don't talk to strangers."
    A method should talk only to itself, its own attributes, its parameters,
    and objects it creates,
    not to the internals of objects it reached through something else.
    This may also be a way to say "minimize coupling."
-   *Independence* or *Orthogonality*.
    Express independent ideas independently.
    This complements separating what varies from what stays the same,
    and is part of the Low-Coupling-High-Cohesion message:
    few connections between parts, and one subject per part.
    [Rethinking Objects](20_Rethinking_Objects.md#prefer-composition-to-inheritance)
    makes the composition case for it.
-   *Managed Coupling*.
    Simply declaring that a design should have "low coupling" is usually too vague.
    Coupling happens, and the important issue is to acknowledge it and control it,
    to say "coupling can cause problems" and to compensate for those problems with a well-considered design or pattern.
-   *Subtraction*: a design is finished when you cannot take anything else away^[Antoine de Saint-Exupéry, *Wind, Sand and Stars*: "perfection is reached not when there's nothing left to add, but when there's nothing left to remove". The English wording varies by translation.].
-   *Simplicity before generality*^[From an email from Kevlin Henney.].
    A common problem we find in frameworks is that they aim to be general purpose without reference to actual systems.
    This leads to a dizzying array of options that are often unused,
    misused or not useful.
    However, most developers work on specific systems,
    and the quest for generality does not always serve them well.
    The best route to generality is through understanding well-defined specific examples.
    This principle acts as the tie breaker between otherwise equally viable design alternatives.
    The simpler solution may also turn out to be the more general one.
    [Pattern Refactoring](37_Pattern_Refactoring.md#choosing-the-lightest-construct)
    works through a case of this, one requirement at a time.
-   *Reflexivity*.
    One abstraction per class, one class per abstraction.
    Also goes by Isomorphism.
-   *Once and once only*:
    Avoid duplication of logic and structure where the duplication is not accidental,
    i.e., where both pieces of code express the same intent for the same reason.
-   *Make things as immutable as possible*,
    as described in [Data Classes as Types](12_Data_Classes_as_Types.md#immutability).
-   *Make functions pure whenever you can*,
    as described in [Pure Functions](40_Functional_Foundations.md#pure-functions).

This is a small handful of fundamental ideas that you can hold in your head while analyzing a design.

## Reading the Chapters Ahead

Each chapter ahead takes a pattern,
or a family of patterns that share a structure, and asks three questions of it.
What varies and what stays the same?
That names the problem the pattern exists to solve.
How much of the answer does Python supply on its own?
That decides how much is left for you to write.
What remains after you subtract Python's share?
That remainder is worth learning,
and it is usually the intent rather than the structure.

A pattern that subtracts to nothing was not a mistake.
It was the right answer for a language missing the piece Python has.

## Exercises

1.  Pick a program you have written that changed more than once.
    Name its vector of change: the thing that shifted every time.
    Say which part of the design absorbed the change,
    and which parts you edited by hand.
2.  Take a pattern you know from another language and list its parts:
    the classes, the interfaces, and the methods its usual form requires.
    Cross out every part Python supplies without your writing it.
    Describe what is left in one sentence.
3.  Apply *Subtraction* to a design of your own.
    Remove one class, one interface, or one level of inheritance,
    and say what stopped working.
    If nothing did, leave it out.
