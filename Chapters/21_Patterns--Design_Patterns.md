# Design Patterns

The "design patterns" movement was an important step forward in object-oriented design.
The 1994 book *Design Patterns* by Erich Gamma, Richard Helm, Ralph Johnson,
and John Vlissides carried it into the mainstream.
Its four authors became known as the "Gang of Four"^[A wry nod to the Chinese political faction of the same name.].
I refer to that book as *GoF Design Patterns*,
and use *design patterns* for the concept.

*GoF Design Patterns* shows 23 solutions to particular classes of problems,
along with one or more examples for each,
typically in C++ but sometimes in Smalltalk.
Many of those examples inspired the ones in this part of the book.
This chapter introduces the concepts.
One listing makes the point,
and the chapters that follow supply the rest of the code.

## What Is a Pattern?

Initially, you can think of a pattern as an especially clever and insightful way of solving a particular class of problems.
Many people have worked out all the angles of a problem and have come up with the most general,
flexible solution.
You may have seen and solved something like it before,
but your solution probably lacks the completeness a pattern embodies.

That completeness has a failure mode.
Once you know a catalog of patterns,
that catalog tempts you to treat it as a checklist,
and to install patterns as proof of sophistication.
A pattern earns its place only when you have the problem it solves.
If nothing varies, you do not need machinery for isolating variation.

Although they're called "design patterns," they apply beyond design.
Because a pattern translates directly into code,
you might expect it to appear no earlier than low-level design.
But a pattern embodies a complete idea within a program,
so it can appear at the analysis phase or high-level design phase,
where you are still describing what the system does rather than how to build it.
It appears at every level,
and you often discover that you need one only once you reach the code.

The basic concept of a pattern is also the basic concept of program design:
adding a layer of abstraction.
Whenever you abstract something, you isolate particular details.
One of the most compelling motivations for abstraction is to *separate things that change from things that stay the same*.
Once you find a part of your program that's likely to change,
patterns can prevent those changes from causing secondary effects throughout your code.
That isolation makes the code cheaper to maintain and usually simpler to understand.

Often, the most difficult part of developing an elegant and cheap-to-maintain design is discovering what I call "the vector of change"
(here, "vector" means a direction of change, not an array of numbers).
You look for the most important thing that changes in your system,
because that is where your greatest cost lies.
Once you discover the vector of change,
you have the focal point around which to structure your design.

You discover a vector of change.
You do not predict it.
Guessing at it up front often builds complexity for flexibility in a direction nobody uses.
The second time a requirement shifts the same part of the design,
you have evidence.

Design patterns isolate changes in your code.
You have seen some design patterns in this book.
For example, you can think of [inheritance](07_Foundations--Classes.md)
as a design pattern (albeit one the language builds in).
It lets you express differences in behavior (that's the thing that changes)
in objects that all have the same interface (that's what stays the same).
[Composition](20_Patterns--Rethinking_Objects.md#prefer-composition-to-inheritance)
also qualifies as a pattern, since it lets you change,
dynamically or statically, the objects that implement your class,
and thus the way that class works.

Another pattern that appears in *GoF Design Patterns* is the [Iterator](23_Patterns--Iterators.md).
An iterator lets you hide the particular implementation of the container as you step through it.
You can write generic code that operates on all the elements in a sequence without regard to how that sequence stores them.
The code works with any object that produces an iterator.

## Pattern Evolution

A pattern arrives in stages, each more general than the last:

1.  **Idiom**: how you write code in a particular language to do this particular type of thing.
    This could be something as common as the way you step through an array in C
    (without running off the end).
2.  **Specific Design**:
    the solution that arose to solve this particular problem.
    This might be a clever design, but it doesn't try to be general.
3.  **Standard Design**: a way to solve every problem of that kind,
    not just the one in front of you.
    A design that has become more general, typically through reuse.
4.  **Design Pattern**: how to solve an entire class of similar problems.
    This usually appears only after you apply a standard design several times,
    and then see a common pattern across those uses.

In Python terms: `with open(...)` for guaranteed cleanup is an idiom, stage one,
meaningless outside a language that provides `with`.
A dictionary mapping one program's shape names to its shape classes is a specific design,
stage two.
The same dictionary is a standard design, stage three,
once each subclass fills it at its own definition so that adding a type never edits the factory
([Factory](27_Patterns--Factory.md) builds both).
[Template Method](25_Patterns--Template_Method.md) is a design pattern,
stage four: a shape of solution you could build in any language with polymorphism.

The stages are a history, not a ranking.
Patterns are subtle and appear over time,
so leave a solution at the stage it has reached rather than forcing it toward a design pattern.

The progression runs downward too.
A pattern a language builds in drops back to stage one,
and the programmers who arrive next learn it as syntax rather than as a design.
Stepping through a container is stage one in Python and was stage four in the *GoF Design Patterns* examples.

## When a Pattern Dissolves

A pattern is often a sign of something missing in a language.
Programmers wrote the same scaffolding often enough that it acquired a name,
and the pattern exists because the language leaves that scaffolding for them to write.

A pattern meets its missing piece in two ways.
Sometimes a language grows the feature and the pattern dissolves into it^[Peter Norvig observed this in his 1996 talk "Design Patterns in Dynamic Programming": 16 of the 23 GoF patterns become invisible or simpler in a dynamic language. He counted for Lisp and Dylan, and Python's line falls in a different place. Singleton is one of the seven he leaves standing, but [Singleton](24_Patterns--Singleton.md)
shows that a Python module already is one.].
[Iterator](23_Patterns--Iterators.md#the-pattern-that-disappeared)
is the clear case.
It was implicit in the `for` loop from the start,
and Python 2.2 made it a protocol the language calls on your behalf.
More often the language had the piece all along,
and the pattern came from a language that didn't.
*Strategy* and *Command* shrink to passing a function,
because a Python function is an object
([Function Objects](28_Patterns--Function_Objects.md) shows both).
A [Factory](27_Patterns--Factory.md) becomes a dictionary,
because a class is an object too.
[Singleton](24_Patterns--Singleton.md) becomes a module,
because Python imports each module once and caches it.

Here is the whole of a *Strategy* in Python:

```python
# strategy_is_a_function.py
from collections.abc import Callable

def apply(nums: list[int],
          how: Callable[[list[int]], int]) -> int:
    return how(nums)
print(apply([3, 1, 2], max), apply([3, 1, 2], sum))
#: 3 6
```

The classic form declares a `Strategy` interface,
writes one class per algorithm, and adds a context class to hold the chosen one.
The `how` parameter replaces all three.

That replacement is why the chapters ahead keep asking the question [Rethinking Objects](20_Patterns--Rethinking_Objects.md#guidelines)
posed: how much of each pattern's machinery does Python still need,
and how much of it becomes functions, data, and protocols?

## Pattern Taxonomy

*GoF Design Patterns* discusses 23 patterns and sorts them under three purposes,
each named for the aspect that can vary:

1.  **Creational**: how to create an object.
    Isolate the details of object creation,
    and your code stops depending on which object types exist and stays the same when you add one.
    [Singleton](24_Patterns--Singleton.md) counts as a *Creational* pattern,
    and [Factory](27_Patterns--Factory.md) covers the other four:
    *Factory Method*, *Abstract Factory*, *Prototype*, and *Builder*.
2.  **Structural**: how objects connect to other objects,
    arranged so that changes in the system leave those connections alone.
    [Surrogate](26_Patterns--Surrogate.md),
    [Changing the Interface](29_Patterns--Changing_the_Interface.md),
    [Flyweight](35_Patterns--Flyweight.md),
    [Decorators](14_Techniques--Decorators.md#the-decorator-pattern),
    and the *Composite* half of [Composite and Interpreter](34_Patterns--Composite_and_Interpreter.md)
    cover the structural patterns in this book.
3.  **Behavioral**: objects that handle particular types of actions within a program.
    These encapsulate processes such as interpreting a language,
    fulfilling a request, moving through a sequence (as in an iterator),
    or implementing an algorithm.
    Most of the patterns in this book are behavioral:
    [Iterator](23_Patterns--Iterators.md),
    [Template Method](25_Patterns--Template_Method.md),
    [Function Objects](28_Patterns--Function_Objects.md)
    (*Command*, *Strategy*, and *Chain of Responsibility*),
    [Observer](30_Patterns--Observer.md), [Visitor](33_Patterns--Visitor.md),
    [Memento](36_Patterns--Memento.md),
    [State](26_Patterns--Surrogate.md#state), and *Interpreter*,
    though *State* appears beside *Proxy* and *Interpreter* beside *Composite*,
    for the reason this section ends with.

The catalog above is GoF's.
Patterns from outside it,
like the *Null Object* that [Rethinking Objects](20_Patterns--Rethinking_Objects.md#null-object)
builds, appear in the [Pattern Catalog](39_Patterns--Pattern_Catalog.md).

<!-- The quoted "clearly" below is the vague word this paragraph objects to,
     so House.Weasel flagging it is the rule agreeing with the point. -->
<!-- vale House.Weasel = NO -->
I've found the *GoF Design Patterns* classification too obscure,
and not always helpful.
Certainly, the *Creational* patterns are straightforward.
How will you create objects?
This is a normal question,
and the name brings you right to that group of patterns.
But I find *Structural* and *Behavioral* far less useful distinctions.
I have not been able to look at a problem and say "clearly,
you need a structural pattern here,"
so that classification doesn't lead me to a solution
(I'll readily admit that I may be missing something here).
<!-- vale House.Weasel = YES -->

Patterns often resemble each other more in their implementations than the *GoF Design Patterns* categories suggest,
and this book groups them by that resemblance.
[Surrogate](26_Patterns--Surrogate.md)
treats *Proxy* and *State* as one front-object structure.
[Function Objects](28_Patterns--Function_Objects.md) treats *Command*,
*Strategy*, and *Chain of Responsibility* as one function-passing structure.
[Composite and Interpreter](34_Patterns--Composite_and_Interpreter.md)
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

<!-- Several principles below quote their sources word for word (Saint-Exupery
     in the Subtraction footnote, Kevlin Henney under Simplicity before
     generality), so house style does not govern their wording. -->
<!-- vale write-good.Passive = NO -->
<!-- vale House.WeakVerb = NO -->

-   *Principle of least astonishment* (don't be astonishing).
-   *Make common things easy, and rare things possible*.
-   *Consistency*.
    Every inconsistency in a design is one more arbitrary rule to remember.
    The more random rules you pile onto the programmer,
    rules that have nothing to do with solving the problem at hand,
    the slower the programmer can produce.
    The cost does not grow one rule at a time.
    The rules interact.
-   *Law of Demeter*: a.k.a. "Don't talk to strangers."
    A method should talk only to itself, its own attributes, its parameters,
    and objects it creates,
    not to the internals of objects it reached through something else.
    The Law of Demeter is another way to say "minimize coupling."
-   *Independence* or *Orthogonality*.
    Express independent ideas independently.
    Orthogonality complements separating what varies from what stays the same,
    and is part of the Low-Coupling-High-Cohesion message:
    few connections between parts, and one subject per part.
    [Rethinking Objects](20_Patterns--Rethinking_Objects.md#prefer-composition-to-inheritance)
    argues for composition on those grounds.
-   *Managed Coupling*.
    Simply declaring that a design should have "low coupling" is usually too vague.
    Coupling happens, so acknowledge it and control it:
    say "coupling can cause problems" and compensate for those problems with a well-considered design or pattern.
-   *Subtraction*: a design is complete when you cannot take anything else away^[Antoine de Saint-Exupéry, *Wind, Sand and Stars*: "perfection is reached not when there's nothing left to add, but when there's nothing left to remove". The English wording varies by translation.].
-   *Simplicity before generality*^[From an email from Kevlin Henney.].
    A common problem we find in frameworks is that they aim to be general purpose without reference to actual systems.
    This leads to a dizzying array of options that are often unused,
    misused or not useful.
    However, most developers work on specific systems,
    and the quest for generality does not always serve them well.
    The best route to generality is through understanding well-defined specific examples.
    This principle acts as the tie breaker between otherwise equally viable design alternatives.
    The simpler solution may also turn out to be the more general one.
    [Pattern Refactoring](37_Patterns--Pattern_Refactoring.md#choosing-the-lightest-construct)
    works through a case of this, one requirement at a time.
-   *Reflexivity*.
    One abstraction per class, one class per abstraction.
    Also goes by Isomorphism.
-   *Once and once only*:
    Avoid duplication of logic and structure where the duplication is not accidental,
    i.e., where both pieces of code express the same intent for the same reason.
-   *Make things as immutable as possible*,
    as [Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#immutability)
    describes.
-   *Make functions pure whenever you can*,
    as [Pure Functions](40_Functional--Foundations.md#pure-functions) describes.

<!-- vale write-good.Passive = YES -->
<!-- vale House.WeakVerb = YES -->

You can hold this handful of fundamental ideas in your head while analyzing a design.

## Reading the Chapters Ahead

Each chapter ahead takes a pattern,
or a family of patterns that share a structure, and asks three questions of it.
What varies and what stays the same?
That names the problem the pattern exists to solve.
How much of the answer does Python supply on its own?
That decides how much remains for you to write.
What remains after you subtract Python's share?
That remainder is worth learning,
and it is usually the intent rather than the structure.

A pattern that subtracts to nothing was not a mistake.
It was the right answer for a language missing the piece Python has.

Part III closes with a [Pattern Catalog](39_Patterns--Pattern_Catalog.md),
a name-and-intent index of the wider literature,
with a link to this book's coverage wherever it exists.

## Exercises

1.  Pick a program you have written that changed more than once.
    Name its vector of change: the thing that shifted every time.
    Say which part of the design absorbed the change,
    and which parts you edited by hand.
2.  Take a pattern you know from another language and list its parts:
    the classes, the interfaces, and the methods its usual form requires.
    Cross out every part Python supplies without your writing it.
    Describe what remains in one sentence.
3.  Apply *Subtraction* to a design of your own.
    Remove one class, one interface, or one level of inheritance,
    and say what stopped working.
    If nothing did, leave it out.
