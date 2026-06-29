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
#: 10 10
print(withdraw(30), withdraw(30))
#: 70 40
```

`double()` returns the same answer every time.
`withdraw()` does not, because each call changes `balance` and the next call sees the new value.
You cannot understand a single `withdraw()` call without tracking the history of every call before it.

The payoff is trust. A pure function is the most reliable code you can write, because its behavior is fully described by its inputs. You test it with a single assertion and no fixture, since there is nothing to set up or restore. You can call it from many threads at once, because it shares no state to corrupt. A cache can store its results, knowing the answer will never go stale:

```python
# why_pure.py
def slope(rise: int, run: int) -> float:
    return rise / run

# No setup or teardown: assert the result directly:
assert slope(10, 2) == 5.0
assert slope(9, 3) == 3.0
print("ok")
#: ok
```

Every later feature in this chapter is, in part, a way to keep more of your code pure.

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
#: cannot assign to field 'x'
# Produce a new value instead of mutating:
moved = Point(p.x + 10, p.y)
print(moved)
#: Point(x=11, y=2)
```

The original `p` is untouched.
`moved` is a separate value.
When values never change underneath you, two parts of a program can share one without coordinating, and concurrent code needs no lock to read it.

Type annotations can state immutability so a checker enforces it.
`typing.Final` marks a name that must not be rebound.
The read-only collection types in `collections.abc`, such as `Sequence` and `Mapping`, describe a value you only read: they have no `append()` or item assignment, so a checker rejects any attempt to mutate through them:

```python
# immutable_types.py
from collections.abc import Sequence
from typing import Final

# Final marks a name the checker won't let you rebind:
MAX_SIZE: Final = 100

# Sequence is read-only: no append, no item assignment:
def total(values: Sequence[int]) -> int:
    return sum(values)

print(MAX_SIZE, total([1, 2, 3]))
#: 100 6
```

The annotation is a promise the checker keeps for you, even when the value passed in is a mutable `list`.
Writing `MAX_SIZE = 200` later, or `values.append(4)` inside `total()`, is a type error caught before the program runs.

Immutability also unlocks abilities a mutable value lacks. An immutable object can be *hashable*: it can promise a stable hash for its whole life, so it can serve as a dictionary key or a set member. It can also be shared without a defensive copy, because no recipient can change it out from under you. A `list` can do neither:

```python
# hashable.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

# A frozen value is hashable, so it can key a dict:
distances = {Point(0, 0): 0.0, Point(3, 4): 5.0}
print(distances[Point(3, 4)])
#: 5.0
# A list has no stable hash, so it cannot be a key:
try:
    hash([3, 4])
except TypeError as e:
    print(e)
#: unhashable type: 'list'
```

These abilities are why the standard library reaches for tuples and frozen dataclasses whenever a value must be a key, cached, or shared across threads.

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
#: HELLO!
# Functions can live in a data structure:
table = {"upper": str.upper, "title": str.title}
print(table["title"]("functional python"))
#: Functional Python
```

The dictionary holds functions as values, so a lookup yields a function you can immediately call.
The [Function Objects](28_Function_Objects.md) chapter approaches the same capability from the pattern side.

Treating functions as values lets data drive control flow. A dictionary of functions replaces a long `if`/`elif` chain: you select the behavior by looking it up:

```python
# dispatch.py
from collections.abc import Callable

def add(a: int, b: int) -> int:
    return a + b
def sub(a: int, b: int) -> int:
    return a - b

# A table of functions replaces a long if/elif chain:
operations: dict[str, Callable[[int, int], int]] = {
    "+": add,
    "-": sub,
}
print(operations["+"](6, 4), operations["-"](6, 4))
#: 10 2
```

Supporting a new operator means adding a row to the table. The dispatch code never changes. This is the structure behind dispatch tables and the plugin registries that let a program grow without editing its core.

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
#: [1, 4, 9, 16, 25]
# filter keeps the elements a predicate accepts:
evens = list(filter(lambda n: n % 2 == 0, numbers))
print(evens)
#: [2, 4]
# sorted takes a function as its key argument:
words = ["banana", "pie", "kiwi", "watermelon"]
print(sorted(words, key=len))
#: ['pie', 'kiwi', 'banana', 'watermelon']
```

Each call hands a function to another function and lets it do the looping.
Returning a function is the other half of the definition, covered under [Closures](#closures) below.

Higher-order functions provide separation of concerns.
The loop that walks the data is written once, inside `map()`, `filter()`, or `sorted()`,
and you supply only the part that differs from one use to the next.
You stop rewriting the same iteration scaffold,
along with the off-by-one and accumulator-initialization mistakes that scaffold invites.
The idea runs the other direction, too:
a function that takes a function can wrap it with operations like timing, retries, or logging.
This is what a decorator does in [Decorators](14_Decorators.md).

## Lambdas

A *lambda* is an unnamed function written as a single expression.
It has no statements and no `return`: the expression's value is what it returns.
The examples above already used lambdas as inline arguments, which is where they fit best:

```python
# lambdas.py
# A lambda is an unnamed function written as one expression:
print((lambda n: n * n)(6))
#: 36
# Most often a lambda is an inline argument:
pairs = [(3, "c"), (1, "a"), (2, "b")]
pairs.sort(key=lambda pair: pair[0])
print(pairs)
#: [(1, 'a'), (2, 'b'), (3, 'c')]
# Binding a lambda to a name works, but a def is clearer:
square = lambda n: n * n
print(square(5))
#: 25
```

A lambda is best when the function is small and used right where it is written.
Once you want to give it a name, write a `def` instead.
A named `def` carries a docstring, a readable name in tracebacks, and room to grow.

The motivation for a lambda is locality. When a transformation is one short expression, a lambda keeps it at the call site, where the reader already is, instead of sending them to a named function defined elsewhere. `sorted(words, key=lambda w: w.lower())` states the sort order right where the sort happens. Naming that one-liner would cost a line, a name to invent, and a definition to look up, with nothing gained in clarity.

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
#: 20 30
```

`multiplier()` returns `multiply()`, and each returned function remembers its own `factor`.
`double` and `triple` are the same code with different captured values.
A closure is the functional answer to "an object with one method and some stored data."

Closures are compelling when you want behavior configured once and then reused, with its configuration kept private. The captured variable is reachable only through the returned function, so no other code can read or overwrite it. That gives you encapsulation without declaring a class:

```python
# counter.py
from collections.abc import Callable

def make_counter() -> Callable[[], int]:
    count = 0
    def increment() -> int:
        nonlocal count
        count += 1
        return count
    return increment

tally = make_counter()
print(tally(), tally(), tally())
#: 1 2 3
```

Each call to `make_counter()` builds an independent counter with its own hidden `count`. Nothing outside `increment()` can reach that state, so it cannot be corrupted by accident.

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
#: 25 125
```

`square` and `cube` are specializations of `power`, each with one argument already supplied.
Partial application turns a general function into the specific one a caller needs, which is handy when a higher-order function wants a single-argument callable.

Partial application earns its place when an API expects a function of one argument and you have a function of several. Rather than write a throwaway wrapper, you preset the fixed arguments and pass the result straight in. Unlike a lambda, `partial()` keeps the bound arguments as data you can inspect through its `.func` and `.args`, and it binds their values at the moment you build it, which avoids the late-binding surprise a lambda created in a loop can produce.

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
#: 22
```

`compose(double, increment)` returns a function that increments first, then doubles.
Each piece stays small and pure, and you combine them without touching their internals.

Composition is compelling because it scales by addition. Each stage stays small, pure, and testable on its own, and you build larger behavior by naming a new composition rather than writing new logic. Stacking `compose()` calls forms a pipeline that reads as the list of steps it performs. When a requirement changes, you insert or swap a single stage and leave every other one untouched.

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
#: 10
# lru_cache remembers results so repeats are free:
@lru_cache
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)
print(fib(30))
#: 832040
# itertools builds lazy iterators:
running = itertools.accumulate([1, 2, 3, 4])
print(list(running))
#: [1, 3, 6, 10]
```

`lru_cache` is only correct because `fib()` is pure: caching a function with side effects would skip the effects.
The toolkits reward you for writing pure functions in the first place.

The reason to look here before writing your own version is that these tools are already written, already correct, and implemented in C. An accumulation, a grouping, a sliding window, or a memoized cache is one call, not a loop you have to debug. Assembling a solution from vetted parts is faster to write and harder to get wrong, and it keeps the code declarative, naming the operation instead of spelling out its mechanics.

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
#: 120
# Python caps how deep recursion can go:
print(sys.getrecursionlimit())
#: 1000
```

Recursion suits problems that are naturally self-similar, such as walking a tree.
Python does not optimize tail calls and limits the call stack, so very deep recursion will raise `RecursionError`.
For long flat sequences, a loop or one of the `itertools` tools is the better choice.

Recursion is compelling when the data is itself recursive. Code that walks a tree, nested data, or a directory reads most clearly when its shape matches the data's shape. The function handles one node and trusts itself for the rest:

```python
# nested_sum.py
type Nested = int | list[Nested]

def deep_sum(items: list[Nested]) -> int:
    total = 0
    for item in items:
        if isinstance(item, list):
            total += deep_sum(item)  # Recurse into a sublist
        else:
            total += item  # A plain number
    return total

print(deep_sum([1, [2, [3, 4], 5], 6]))
#: 21
```

`deep_sum()` states what to do with one element and delegates the nesting to itself. An iterative version would have to maintain its own stack to remember where it was, reintroducing by hand the bookkeeping recursion gives you for free.

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
#: [1, 4, 9, 16, 25]
```

`squares()` never finishes on its own, yet the program terminates because `islice()` requests exactly five values.
Nothing beyond those five is ever computed.
The [Performance](18_Performance.md) chapter looks at laziness from the angle of memory and speed.

Laziness is compelling at scale. A generator pipeline can process a multi-gigabyte file or a live network stream one item at a time, so memory stays flat no matter how large the source grows. Stages chain together without building intermediate lists between them, and a consumer that stops early, such as `any()` or `next()`, means the upstream work for the items it never reaches is never done at all.

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
#: zero
print(describe([42]))
#: one item: 42
print(describe([1, 2]))
#: two items: 1, 2
print(describe({"name": "Ada"}))
#: named Ada
```

Each `case` is a pattern, and a match both tests the shape and pulls out the parts in one step.
The [Pattern Matching](12_Pattern_Matching.md) chapter covers the full syntax.
Here it earns its place as a declarative tool for taking data apart.

The motivation is that one `match` collapses a stack of `isinstance()` tests, length checks, and key or index lookups into a single readable description of each shape. The test and the extraction happen together, so there is no gap where you have confirmed the shape but not yet pulled out its parts. This pays off most on shaped data, such as parsed JSON, an abstract syntax tree, or the messages of a protocol, where the alternative is a thicket of nested conditionals.

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
#: 5.0
#: undefined
```

The return type `float | None` tells the caller, and the type checker, that failure is possible.
A richer version returns a dedicated result object carrying either a value or an error.
The [Functional Error Handling](13_Functional_Error_Handling.md) chapter develops that approach in full.

Returning failure as a value is compelling because it makes failure visible. The possibility appears in the return type, so the type checker reminds every caller to handle it and a reviewer sees it without reading the body. Control flow stays local, with no exception leaping past intermediate frames to a distant handler. You do pay by handling the failure at each step, but that is the same discipline that stops an unhandled error from escaping unnoticed.

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
#: 10 10 True
```

Because `add(2, 3)` and `5` are interchangeable, a compiler can cache the call, evaluate it in any order, or skip a repeat.
You can also reason about the code by substitution, the same move you make in algebra.
This is the property that lets parts of a program be checked, and sometimes proved correct, and it connects back to this chapter's opening question about what counts as "what works."

This property is also the quiet reason the `lru_cache` from earlier is safe. A memoizer may hand back a stored result only because the call is interchangeable with its value. Every optimization that skips or reuses work, from a cache to a database query planner, is cashing in referential transparency. The more of your program holds this property, the more of it a machine, or a proof, can reason about.

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
#: [4, 16, 36]
# Declarative: state the what, as a comprehension:
print([n * n for n in numbers if n % 2 == 0])
#: [4, 16, 36]
```

Both produce the same list.
The comprehension says "the squares of the even numbers" and leaves the looping to Python.
This is the broader "functionality" the introduction points toward: describe the result, and let the machine arrange the steps.
The [Comprehensions](16_Comprehensions.md) chapter explores this notation on its own.

The compelling part is that declarative code says less and means more. By naming the result instead of the steps, you hand the reader your intent directly, and you give the runtime freedom to choose how to deliver it. That freedom is why a SQL query, a NumPy expression, or a dataframe operation can run on an optimized or parallel engine you never see: you described the what, not a fixed sequence of moves.

## An Assurance Spectrum

The chapter opened by asking whether programming can make the kind of provable claims a science makes. Functional programming's honest answer is not one guarantee but a spectrum. The properties built up here, purity, immutability, and referential transparency, buy assurance at every level. You decide how far up to climb.

1. The cheapest rung is local reasoning. Pure functions and immutable values let you understand one piece at a time, with no hidden state to carry in your head. Most code never needs more.
2. Next is type checking. A type signature is a small theorem, and the function body is its proof. This is the *Curry-Howard correspondence*: types are propositions and programs are their proofs. Running `ty` over the examples in this book discharges that proof for a useful class of mistakes.
3. Above that is *property-based testing*. You state a law the code must obey, then check it against many generated inputs. It does not prove the law. It works to falsify it, which is the falsifiability the chapter's opening called for.
4. At the top is formal proof. Dependently-typed languages such as Lean, Idris, and Rocq prove a program correct for every possible input, checked by machine. This is real, and rare outside specialized work.

The middle rung is the one most worth adopting now. You can write a property check by hand, looping over random inputs and asserting the law. A tool like *Hypothesis* does the same thing with sharper inputs, and shrinks any failure to a minimal counterexample:

```python
# property_check.py
import random

def encode(text: str) -> str:
    # A trivial reversible transform:
    return text[::-1]

def decode(text: str) -> str:
    return text[::-1]

# State a law, then check it on many random inputs the way
# a property-based tool such as Hypothesis would:
alphabet = "abcde"
for _ in range(1000):
    size = random.randint(0, 8)
    sample = "".join(random.choice(alphabet) for _ in range(size))
    assert decode(encode(sample)) == sample
print("1000 random cases passed")
#: 1000 random cases passed
```

The law is "decoding an encoding returns the original," and it holds for every input the loop tries. A property test states what must always be true and lets the machine search for a counterexample, instead of you writing one example at a time.

Hypothesis turns that loop into a declaration. You describe the inputs with a *strategy* and state the law once, as a normal `test_` function. The framework supplies the cases, including awkward ones a handwritten loop would miss, such as the empty string and unusual Unicode:

```python
# test_property.py
from hypothesis import given
from hypothesis import strategies as st

def encode(text: str) -> str:
    return text[::-1]

def decode(text: str) -> str:
    return text[::-1]

@given(st.text())
def test_roundtrip(sample: str) -> None:
    assert decode(encode(sample)) == sample
```

`@given(st.text())` feeds `test_roundtrip()` a stream of generated strings. When a law fails, Hypothesis does not only report the failing input. It shrinks it to the smallest example that still fails, so the bug surfaces as the clearest case rather than a random one. That is the falsification machinery the chapter's opening called for, automated.

Two caveats keep this honest. First, proof is not exclusive to functional code. Hoare logic and tools like Dafny verify imperative programs too. What purity changes is the cost: with no mutable state to track, each step of the reasoning is shorter. Functional programming does not make correctness provable so much as it makes the proof affordable. Second, most functional code stops well below the top rung. Haskell programmers rarely prove a program correct. They lean on types and on reasoning by substitution, and save full proof for the few places that earn it.

So the thread running through this chapter is not that functions are special. It is that purity, immutability, and referential transparency shrink the distance between "I believe this is correct" and "I can show why." Proof is the far end of that distance. The everyday win is everything below it: code you can read, check, and test as statements about what is true. That, more than the presence of functions, is the "functionality" the introduction set out to find.
