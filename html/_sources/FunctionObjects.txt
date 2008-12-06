
********************************************************************************
Function Objects
********************************************************************************

In *Advanced C++:Programming Styles And Idioms (Addison-Wesley, 1992)*, Jim
Coplien coins the term *functor* which is an object whose sole purpose is to
encapsulate a function (since "functor" has a meaning in mathematics, in this
book I shall use the more explicit term *function object*). The point is to
decouple the choice of function to be called from the site where that function
is called.

This term is mentioned but not used in *Design Patterns*. However, the theme of
the function object is repeated in a number of patterns in that book.

Command: Choosing the Operation at Runtime
=======================================================================

This is the function object in its purest sense: a method that's an object. By
wrapping a method in an object, you can pass it to other methods or objects as a
parameter, to tell them to perform this particular operation in the process of
fulfilling your request::

    # FunctionObjects/CommandPattern.py

    class Command:
        def execute(self): pass

    class Loony(Command):
        def execute(self):
            print("You're a loony.")

    class NewBrain(Command):
        def execute(self):
            print("You might even need a new brain.")

    class Afford(Command):
        def execute(self):
            print("I couldn't afford a whole new brain.")

    # An object that holds commands:
    class Macro:
        def __init__(self):
            self.commands = []
        def add(self, command):
            self.commands.append(command)
        def run(self):
            for c in self.commands:
                c.execute()

    macro = Macro()
    macro.add(Loony())
    macro.add(NewBrain())
    macro.add(Afford())
    macro.run()


The primary point of *Command* is to allow you to hand a desired action to a
method or object. In the above example, this provides a way to queue a set of
actions to be performed collectively. In this case, it allows you to dynamically
create new behavior, something you can normally only do by writing new code but
in the above example could be done by interpreting a script (see the
*Interpreter* pattern if what you need to do gets very complex).

*Design Patterns* says that "Commands are an object-oriented replacement for
callbacks." However, I think that the word "back" is an essential part of the
concept of callbacks. That is, I think a callback actually reaches back to the
creator of the callback. On the other hand, with a *Command* object you
typically just create it and hand it to some method or object, and are not
otherwise connected over time to the *Command* object. That's my take on it,
anyway. Later in this book, I combine a group of design patterns under the
heading of "callbacks."

Strategy: Choosing the Algorithm at Runtime
=======================================================================

*Strategy* appears to be a family of *Command* classes, all inherited from the
same base. But if you look at *Command*, you'll see that it has the same
structure: a hierarchy of function objects. The difference is in the way this
hierarchy is used. As seen in **patternRefactoring:DirList.py**, you use
*Command* to solve a particular problem-in that case, selecting files from a
list. The "thing that stays the same" is the body of the method that's being
called, and the part that varies is isolated in the function object. I would
hazard to say that *Command* provides flexibility while you're writing the
program, whereas *Strategy*\'s flexibility is at run time.

*Strategy* also adds a "Context" which can be a surrogate class that controls
the selection and use of the particular strategy object-just like *State*!
Here's what it looks like::

    # FunctionObjects/StrategyPattern.py

    # The strategy interface:
    class FindMinima:
        # Line is a sequence of points:
        def algorithm(self, line) : pass

    # The various strategies:
    class LeastSquares(FindMinima):
        def algorithm(self, line):
            return [ 1.1, 2.2 ] # Dummy

    class NewtonsMethod(FindMinima):
        def algorithm(self, line):
            return [ 3.3, 4.4 ]  # Dummy

    class Bisection(FindMinima):
        def algorithm(self, line):
            return [ 5.5, 6.6 ] # Dummy

    class ConjugateGradient(FindMinima):
        def algorithm(self, line):
            return [ 3.3, 4.4 ] # Dummy

    # The "Context" controls the strategy:
    class MinimaSolver:
        def __init__(self, strategy):
            self.strategy = strategy

        def minima(self, line):
            return self.strategy.algorithm(line)

        def changeAlgorithm(self, newAlgorithm):
            self.strategy = newAlgorithm

    solver = MinimaSolver(LeastSquares())
    line = [1.0, 2.0, 1.0, 2.0, -1.0, 3.0, 4.0, 5.0, 4.0]
    print(solver.minima(line))
    solver.changeAlgorithm(Bisection())
    print(solver.minima(line))


Note similarity with template method - TM claims distinction that it has more
than one method to call, does things piecewise. However, it's not unlikely that
strategy object would have more than one method call; consider Shalloway's order
fulfullment system with country information in each strategy.

Strategy example from standard Python: **sort( )** takes a second optional
argument that acts as a comparator object; this is a strategy.

.. note:: A better, real world example is numerical integration, shown here:
          http://www.rosettacode.org/wiki/Numerical_Integration#Python

Chain of Responsibility
=======================================================================

*Chain of Responsibility* might be thought of as a dynamic generalization of
recursion using *Strategy* objects. You make a call, and each *Strategy* in a
linked sequence tries to satisfy the call. The process ends when one of the
strategies is successful or the chain ends. In recursion, one method calls
itself over and over until a termination condition is reached; with *Chain of
Responsibility*, a method calls itself, which (by moving down the chain of
*Strategies*) calls a different implementation of the method, etc., until a
termination condition is reached. The termination condition is either the bottom
of the chain is reached (in which case a default object is returned; you may or
may not be able to provide a default result so you must be able to determine the
success or failure of the chain) or one of the *Strategies* is successful.

Instead of calling a single method to satisfy a request, multiple methods in the
chain have a chance to satisfy the request, so it has the flavor of an expert
system. Since the chain is effectively a linked list, it can be dynamically
created, so you could also think of it as a more general, dynamically-built
**switch** statement.

In the GoF, there's a fair amount of Thidiscussion of how to create the chain of
responsibility as a linked list. However, when you look at the pattern it really
shouldn't matter how the chain is maintained; that's an implementation detail.
Since GoF was written before the Standard Template Library (STL) was
incorporated into most C++ compilers, the reason for this is most likely (1)
there was no list and thus they had to create one and (2) data structures are
often taught as a fundamental skill in academia, and the idea that data
structures should be standard tools available with the programming language may
not have occurred to the GoF authors. I maintain that the implementation of
*Chain of Responsibility* as a chain (specifically, a linked list) adds nothing
to the solution and can just as easily be implemented using a standard Python
list, as shown below. Furthermore, you'll see that I've gone to some effort to
separate the chain-management parts of the implementation from the various
*Strategies*, so that the code can be more easily reused.

In **StrategyPattern.py**, above, what you probably want is to automatically
find a solution. *Chain of Responsibility* provides a way to do this by chaining
the *Strategy* objects together and providing a mechanism for them to
automatically recurse through each one in the chain::

    # FunctionObjects/ChainOfResponsibility.py

    # Carry the information into the strategy:
    class Messenger: pass

    # The Result object carries the result data and
    # whether the strategy was successful:
    class Result:
        def __init__(self):
            self.succeeded = 0
        def isSuccessful(self):
            return self.succeeded
        def setSuccessful(self, succeeded):
            self.succeeded = succeeded

    class Strategy:
        def __call__(messenger): pass
        def __str__(self):
            return "Trying " + self.__class__.__name__ \
              + " algorithm"

    # Manage the movement through the chain and
    # find a successful result:
    class ChainLink:
        def __init__(self, chain, strategy):
            self.strategy = strategy
            self.chain = chain
            self.chain.append(self)

        def next(self):
            # Where this link is in the chain:
            location = self.chain.index(self)
            if not self.end():
                return self.chain[location + 1]

        def end(self):
            return (self.chain.index(self) + 1 >=
                    len(self.chain))

        def __call__(self, messenger):
            r = self.strategy(messenger)
            if r.isSuccessful() or self.end(): return r
            return self.next()(messenger)

    # For this example, the Messenger
    # and Result can be the same type:
    class LineData(Result, Messenger):
        def __init__(self, data):
            self.data = data
        def __str__(self): return `self.data`

    class LeastSquares(Strategy):
        def __call__(self, messenger):
            print(self)
            linedata = messenger
            # [ Actual test/calculation here ]
            result = LineData([1.1, 2.2]) # Dummy data
            result.setSuccessful(0)
            return result

    class NewtonsMethod(Strategy):
        def __call__(self, messenger):
            print(self)
            linedata = messenger
            # [ Actual test/calculation here ]
            result = LineData([3.3, 4.4]) # Dummy data
            result.setSuccessful(0)
            return result

    class Bisection(Strategy):
        def __call__(self, messenger):
            print(self)
            linedata = messenger
            # [ Actual test/calculation here ]
            result = LineData([5.5, 6.6]) # Dummy data
            result.setSuccessful(1)
            return result

    class ConjugateGradient(Strategy):
        def __call__(self, messenger):
            print(self)
            linedata = messenger
            # [ Actual test/calculation here ]
            result = LineData([7.7, 8.8]) # Dummy data
            result.setSuccessful(1)
            return result

    solutions = []
    ChainLink(solutions, LeastSquares()),
    ChainLink(solutions, NewtonsMethod()),
    ChainLink(solutions, Bisection()),
    ChainLink(solutions, ConjugateGradient())

    line = LineData([
      1.0, 2.0, 1.0, 2.0, -1.0,
      3.0, 4.0, 5.0, 4.0
    ])

    print(solutions[0](line))


Exercises
=======================================================================

#.  Use *Command* in Chapter 3, Exercise 1.

#.  Implement *Chain of Responsibility* to create an "expert system" that solves
    problems by successively trying one solution after another until one
    matches. You should be able to dynamically add solutions to the expert
    system. The test for solution should just be a string match, but when a
    solution fits, the expert system should return the appropriate type of
    **ProblemSolver** object. What other pattern/patterns show up here?

.. rubric:: Footnotes

.. [#] In Python, all functions are already objects and so the *Command* pattern
       is often redundant.

.. [#] *Design Patterns*, Page 235.


