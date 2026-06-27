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

A *pure function* computes its result from its arguments alone.
It reads nothing else and changes nothing else.
Given the same arguments, it always returns the same value.
It has no *side effects*: no printing, no file or network access, no mutation of anything outside the function.

Purity is the foundation everything else in this chapter builds on.
A pure function can be tested in isolation, because its behavior is fully determined by what you pass in.
Its result can be cached, because the answer never changes.
You can reason about it the way you reason about an equation:

```python
# pure_functions.py
# Pure: the result depends only on the arguments:
def double(x: int) -> int:
    return x * 2

# Impure: it depends on and mutates outside state:
balance = 100
def withdraw(amount: int) -> int:
    global balance
    balance -= amount
    return balance

print(double(5), double(5))
## 10 10
print(withdraw(30), withdraw(30))
## 70 40
```

`double()` returns the same answer every time.
`withdraw()` does not, because each call changes `balance` and the next call sees the new value.
You cannot understand a single `withdraw()` call without tracking the history of every call before it.

## Immutability

An *immutable* value cannot change after it is created.
Tuples, strings, `frozenset`, and frozen dataclasses are immutable.
Removing shared mutable state is the practical core of the functional style: a value that never changes cannot develop a bug from being changed somewhere you forgot about.

Instead of modifying an object, you build a new one from the old:

```python
# immutability.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

p = Point(1, 2)
try:
    setattr(p, "x", 5)  # A frozen instance rejects assignment
except AttributeError as e:
    print(e)
## cannot assign to field 'x'
# Produce a new value instead of mutating:
moved = Point(p.x + 10, p.y)
print(moved)
## Point(x=11, y=2)
```

The original `p` is untouched.
`moved` is a separate value.
When values never change underneath you, two parts of a program can share one without coordinating, and concurrent code needs no lock to read it.

## Functions as First-Class Objects

A function in Python is an object like any other.
This is what *first-class* means: you can bind a function to a name, store it in a container, pass it as an argument, and return it from another function.
A function value is not special syntax. It is data you can move around.

```python
# first_class.py
def shout(text: str) -> str:
    return text.upper() + "!"

# A function is an object you can bind to another name:
loud = shout
print(loud("hello"))
## HELLO!
# Functions can live in a data structure:
table = {"upper": str.upper, "title": str.title}
print(table["title"]("functional python"))
## Functional Python
```

The dictionary holds functions as values, so a lookup yields a function you can immediately call.
The [Function Objects](27_Function_Objects.md) chapter approaches the same capability from the pattern side.

## Higher-Order Functions

A *higher-order function* takes a function as an argument, returns one, or both.
Three built-ins are the workhorses.
`map()` applies a function to every element of an iterable.
`filter()` keeps the elements for which a function returns true.
`sorted()` accepts a `key` function that decides the ordering:

```python
# higher_order.py
numbers = [1, 2, 3, 4, 5]
# map() applies a function to each element:
squares = list(map(lambda n: n * n, numbers))
print(squares)
## [1, 4, 9, 16, 25]
# filter keeps the elements a predicate accepts:
evens = list(filter(lambda n: n % 2 == 0, numbers))
print(evens)
## [2, 4]
# sorted takes a function as its key argument:
words = ["banana", "pie", "kiwi", "watermelon"]
print(sorted(words, key=len))
## ['pie', 'kiwi', 'banana', 'watermelon']
```

Each call hands a function to another function and lets it do the looping.
Returning a function is the other half of the definition, covered under Closures below.

## Lambdas

A *lambda* is an unnamed function written as a single expression.
It has no statements and no `return`: the expression's value is what it returns.
The examples above already used lambdas as inline arguments, which is where they fit best:

```python
# lambdas.py
# A lambda is an unnamed function written as one expression:
print((lambda n: n * n)(6))
## 36
# Most often a lambda is an inline argument:
pairs = [(3, "c"), (1, "a"), (2, "b")]
pairs.sort(key=lambda pair: pair[0])
print(pairs)
## [(1, 'a'), (2, 'b'), (3, 'c')]
# Binding a lambda to a name works, but a def is clearer:
square = lambda n: n * n
print(square(5))
## 25
```

A lambda is best when the function is small and used right where it is written.
Once you want to give it a name, write a `def` instead.
A named `def` carries a docstring, a readable name in tracebacks, and room to grow.

## Closures

When an inner function refers to a variable from the function that created it, Python keeps that variable alive.
The inner function plus the captured variables is a *closure*.
This is how a function can carry state without a class:

```python
# closures.py
from collections.abc import Callable

def multiplier(factor: int) -> Callable[[int], int]:
    # The inner function captures factor from this scope:
    def multiply(n: int) -> int:
        return n * factor
    return multiply

double = multiplier(2)
triple = multiplier(3)
print(double(10), triple(10))
## 20 30
```

`multiplier()` returns `multiply()`, and each returned function remembers its own `factor`.
`double` and `triple` are the same code with different captured values.
A closure is the functional answer to "an object with one method and some stored data."

## Partial Application

*Partial application* fixes some of a function's arguments and produces a new function that expects the rest.
`functools.partial()` does this without writing a wrapper by hand:

```python
# partial.py
from functools import partial

def power(base: int, exponent: int) -> int:
    return base ** exponent

# Fix the exponent to build new single-argument functions:
square = partial(power, exponent=2)
cube = partial(power, exponent=3)
print(square(5), cube(5))
## 25 125
```

`square` and `cube` are specializations of `power`, each with one argument already supplied.
Partial application turns a general function into the specific one a caller needs, which is handy when a higher-order function wants a single-argument callable.

## Composing Functions

*Composition* builds a new function by feeding one function's output straight into the next.
It lets you assemble behavior from small pieces, the way a pipeline reads as a sequence of steps:

```python
# composing.py
from collections.abc import Callable

def compose(
    f: Callable[[int], int], g: Callable[[int], int]
) -> Callable[[int], int]:
    # Return a function that runs g, then feeds the result to f:
    def composed(x: int) -> int:
        return f(g(x))
    return composed

def increment(n: int) -> int:
    return n + 1
def double(n: int) -> int:
    return n * 2

increment_then_double = compose(double, increment)
print(increment_then_double(10))
## 22
```

`compose(double, increment)` returns a function that increments first, then doubles.
Each piece stays small and pure, and you combine them without touching their internals.

## The `functools` and `itertools` Toolkits

The standard library ships the building blocks of functional Python.
`functools.reduce()` folds a sequence into a single value.
`functools.lru_cache` records a pure function's results so repeated calls are free.
`itertools` provides lazy iterators that produce values on demand:

```python
# toolkits.py
import itertools
from functools import lru_cache, reduce
from operator import add

# reduce() folds a sequence down to a single value:
print(reduce(add, [1, 2, 3, 4]))
## 10
# lru_cache remembers results so repeats are free:
@lru_cache
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)
print(fib(30))
## 832040
# itertools builds lazy iterators:
running = itertools.accumulate([1, 2, 3, 4])
print(list(running))
## [1, 3, 6, 10]
```

`lru_cache` is only correct because `fib()` is pure: caching a function with side effects would skip the effects.
The toolkits reward you for writing pure functions in the first place.

## Recursion

*Recursion* expresses a repeated computation as a function that calls itself.
Each recursive function needs a *base case* that stops the recursion and a *recursive case* that moves toward it:

```python
# recursion.py
import sys

def factorial(n: int) -> int:
    # Base case stops the recursion:
    if n <= 1:
        return 1
    # Recursive case moves toward the base case:
    return n * factorial(n - 1)

print(factorial(5))
## 120
# Python caps how deep recursion can go:
print(sys.getrecursionlimit())
## 1000
```

Recursion suits problems that are naturally self-similar, such as walking a tree.
Python does not optimize tail calls and limits the call stack, so very deep recursion will raise `RecursionError`.
For long flat sequences, a loop or one of the `itertools` tools is the better choice.

## Lazy Evaluation

*Lazy evaluation* computes a value only when it is needed.
A generator is the everyday example: it yields one value at a time instead of building a whole list up front.
Combined with `itertools`, this lets you describe an infinite sequence and take only the part you use:

```python
# lazy.py
from collections.abc import Iterator
from itertools import count, islice

# A generator yields values one at a time, on demand:
def squares() -> Iterator[int]:
    for n in count(1):
        yield n * n

# count() is infinite; islice() pulls only what we ask for:
first_five = list(islice(squares(), 5))
print(first_five)
## [1, 4, 9, 16, 25]
```

`squares()` never finishes on its own, yet the program terminates because `islice()` requests exactly five values.
Nothing beyond those five is ever computed.
The [Performance](17_Performance.md) chapter looks at laziness from the angle of memory and speed.

## Pattern Matching as Destructuring

The `match` statement reads a value apart by its shape rather than by hand.
You describe the structures you expect, and Python binds the pieces for you:

```python
# pattern_matching.py
def describe(value: object) -> str:
    match value:
        case 0:
            return "zero"
        case [x]:
            return f"one item: {x}"
        case [x, y]:
            return f"two items: {x}, {y}"
        case {"name": name}:
            return f"named {name}"
        case _:
            return "something else"

print(describe(0))
## zero
print(describe([42]))
## one item: 42
print(describe([1, 2]))
## two items: 1, 2
print(describe({"name": "Ada"}))
## named Ada
```

Each `case` is a pattern, and a match both tests the shape and pulls out the parts in one step.
The [Pattern Matching](11_Pattern_Matching.md) chapter covers the full syntax.
Here it earns its place as a declarative tool for taking data apart.

## Functional Error Handling

Raising an exception is one way to report failure.
The functional alternative is to return a value that represents the failure, so the caller must handle it in the open instead of through a separate control path:

```python
# functional_errors.py
def safe_divide(a: int, b: int) -> float | None:
    # Return None instead of raising on bad input:
    if b == 0:
        return None
    return a / b

for divisor in (2, 0):
    match safe_divide(10, divisor):
        case None:
            print("undefined")
        case value:
            print(value)
## 5.0
## undefined
```

The return type `float | None` tells the caller, and the type checker, that failure is possible.
A richer version returns a dedicated result object carrying either a value or an error.
The [Functional Error Handling](12_Functional_Error_Handling.md) chapter develops that approach in full.

## Referential Transparency

An expression is *referentially transparent* when you can replace it with its value without changing the program's behavior.
Pure functions give you this property, and it is the precise reason purity matters:

```python
# referential_transparency.py
def add(a: int, b: int) -> int:
    return a + b

# The call add(2, 3) always equals 5, so the call and the
# value 5 are interchangeable everywhere in the program.
x = add(2, 3) + add(2, 3)
y = 5 + 5
print(x, y, x == y)
## 10 10 True
```

Because `add(2, 3)` and `5` are interchangeable, a compiler can cache the call, evaluate it in any order, or skip a repeat.
You can also reason about the code by substitution, the same move you make in algebra.
This is the property that lets parts of a program be checked, and sometimes proved correct, and it connects back to this chapter's opening question about what counts as "what works."

## Declarative Style

*Declarative* code states the result you want.
*Imperative* code spells out each step to produce it.
The functional tools in this chapter push code toward the declarative end:

```python
# declarative.py
numbers = [1, 2, 3, 4, 5, 6]
# Imperative: spell out every step of the how:
result = []
for n in numbers:
    if n % 2 == 0:
        result.append(n * n)
print(result)
## [4, 16, 36]
# Declarative: state the what, as a comprehension:
print([n * n for n in numbers if n % 2 == 0])
## [4, 16, 36]
```

Both produce the same list.
The comprehension says "the squares of the even numbers" and leaves the looping to Python.
This is the broader "functionality" the introduction points toward: describe the result, and let the machine arrange the steps.
The [Comprehensions](15_Comprehensions.md) chapter explores this notation on its own.
