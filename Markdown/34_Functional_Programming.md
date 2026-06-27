# Functional Programming

[[Note: this chapter is currently an experiment which is why I've put it at the end. If I decide to include it, it will probably be placed after "Rethinking Objects"]]

Functional programming is usually introduced as "programming with functions," and functions are indeed a central part of the practice.
But after (slowly) studying it for over ten years, I have started to wonder whether it's actually more about "functionality."
One definition for science is "science is what works."
Science has theories that fit the data, are predictive, and are falsifiable.
If "computer science" is to live up to its name, there should be some ideas and practices that fit that definition, and perhaps even some aspects that are mathematically provable.
This seems to me to be the broader challenge that functional programming takes on, and what I explore in this chapter.
That said, we must still begin with the more traditional explanations of functional programming.

## Pure Functions

[[The foundation: a function whose result depends only on its arguments and that changes nothing outside itself. This is what makes code testable and lets you reason about a piece of it in isolation]]

## Immutability

[[Values that never change after creation: tuples, frozensets, and frozen dataclasses. Removing shared mutable state is the practical core of the functional style]]

## Functions as First-Class Objects

[[You can assign a function to a name, store it in a container, pass it as an argument, and return it. The Function Objects chapter approaches the same idea from the pattern side]]

## Higher-Order Functions

[[Functions that take or return other functions. `map`, `filter`, and the `key` argument to `sorted` are built-in examples]]

## Lambdas

[[Small anonymous functions for the cases where a named `def` would add noise and a comprehension is not clearer]]

## Closures

[[A returned function that remembers the variables from the scope where it was created, carrying state without a class]]

## Partial Application

[[`functools.partial` fixes some arguments of a function and hands back a new function that expects the rest]]

## Composing Functions

[[Building behavior by feeding one function's output straight into the next, so a pipeline reads as a sequence of transformations]]

## The `functools` and `itertools` Toolkits

[[`reduce`, `lru_cache`, and the lazy building blocks (`chain`, `accumulate`, `groupby`) that make functional Python practical]]

## Recursion

[[Expressing a loop as a function that calls itself, plus Python's recursion limit and why iteration is often the better choice]]

## Lazy Evaluation

[[Generators produce values on demand instead of building full lists. The Performance chapter covers this from the cost angle]]

## Pattern Matching as Destructuring

[[`match`/`case` reads data apart declaratively instead of by hand. The Pattern Matching chapter introduces the syntax; here it earns its place as a functional tool]]

## Functional Error Handling

[[Returning a value that represents success or failure rather than raising an exception. The Functional Error Handling chapter develops this in full]]

## Referential Transparency

[[When an expression can be replaced by its value without changing behavior. This is the property that makes equational reasoning, and even proofs, possible, and it connects back to this chapter's opening question about what counts as "what works"]]

## Declarative Style

[[Saying what result you want rather than spelling out each step to reach it. This is the broader "functionality" that the introduction points toward]]
