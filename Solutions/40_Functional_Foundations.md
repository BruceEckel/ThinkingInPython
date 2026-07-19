# Foundations: Solutions

## 1. `deposit()` is impure for the same reason `withdraw()` is

```python
balance = 100

def deposit(amount):
    global balance
    balance += amount
    return balance

print(deposit(30), deposit(30))
#: 130 160
```

Two identical calls, `deposit(30)` and `deposit(30)`, return different
results, `130` then `160`, which is impossible for a pure function:
a pure function must return the same value every time it is called
with the same arguments. `deposit()` reads and mutates `balance`, a
name outside its own scope, so its result depends on how many times it
(or `withdraw()`) has already run. You cannot know what `deposit(30)`
returns without tracking the history of every prior call, which is the
problem the chapter raises for `withdraw()`.

## 2. A `"*"` operator added to the dispatch table

```python
from collections.abc import Callable

def add(a, b):
    return a + b
def sub(a, b):
    return a - b
def mul(a, b):
    return a * b

operations: dict[str, Callable[[int, int], int]] = {
    "+": add,
    "-": sub,
    "*": mul,
}
print(operations["+"](6, 4), operations["-"](6, 4), operations["*"](6, 4))
#: 10 2 24
```

`operations["*"](6, 4)` is called the same way as the other
two entries; nothing about the calling code changes. Supporting a new
operator really was just adding one row to the table, as the chapter
claims.

## 3. A fourth independent closure

```python
def multiplier(factor):
    def multiply(n):
        return n * factor
    return multiply

double = multiplier(2)
triple = multiplier(3)
quadruple = multiplier(4)
print(double(10), triple(10), quadruple(10))
#: 20 30 40
```

Each call to `multiplier()` creates a new `multiply` closure with its
own private `factor`. `quadruple` remembers `4` independently of
`double`'s `2` and `triple`'s `3`, the same way `double` and `triple`
were already independent of each other. Nothing shared between them
could leak, because each closure's `factor` is reachable only through
that particular returned function.

## 4. A three-stage composition

```python
def compose(f, g):
    def composed(x):
        return f(g(x))
    return composed

def increment(n):
    return n + 1
def double(n):
    return n * 2
def square(n):
    return n * n

increment_then_double = compose(double, increment)
increment_then_double_then_square = compose(square, increment_then_double)
print(increment_then_double_then_square(3))
#: 64
```

`increment_then_double_then_square(3)` runs `increment_then_double(3)`
first, which computes `(3 + 1) * 2 = 8`, then feeds that `8` into
`square`, giving `8 * 8 = 64`. `compose()` did not need to change at
all to support a third stage; wrapping one composed function inside
another `compose()` call is enough to extend the pipeline.
