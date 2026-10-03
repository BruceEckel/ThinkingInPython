# Composite and Interpreter: Solutions

## 1. `find(entry, name)`

> Add `find(entry, name)` to `filesystem.py`:
> a generator yielding the path of every entry whose name matches.
> A directory can match, and matching should continue into it.

<details>
<summary>Where to look</summary>

[The Classic Composite](../../Chapters/34_Patterns--Composite_and_Interpreter.md#the-classic-composite) and [A Composite of Data Classes](../../Chapters/34_Patterns--Composite_and_Interpreter.md#a-composite-of-data-classes) show `walk()` recursing through a `Directory` with `match`.
Write `find()` in the same shape, with one case per `Node` type and `yield from` for the recursion.
A `Directory` case checks its own name before it descends, and it carries the path prefix down.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from collections.abc import Iterator
from typing import assert_never
from record import record

@record
class File:
    name: str
    size: int

@record
class Directory:
    name: str
    entries: tuple[Node, ...]

type Node = File | Directory

def find(entry: Node, name: str,
         prefix: str = "") -> Iterator[str]:
    ...
```

<details>
<summary>Solution</summary>

If you copy `walk()` and add a name test to the `File` case alone,
`find(root, "main.py")` still works, but `find(root, "src")` returns an empty list.
A `Directory` case that only descends never yields its own path.
The exercise says a directory can match,
so the solution's `Directory` case tests its own name before it descends.

```python
# exercise_1.py
from collections.abc import Iterator
from typing import assert_never
from record import record

@record
class File:
    name: str
    size: int

@record
class Directory:
    name: str
    entries: tuple[Node, ...]

type Node = File | Directory

def find(entry: Node, name: str,
         prefix: str = "") -> Iterator[str]:
    match entry:
        case File(n, _):
            if n == name:
                yield prefix + n
        case Directory(n, entries):
            if n == name:
                yield prefix + n
            for e in entries:
                yield from find(e, name, f"{prefix}{n}/")
        case _:
            assert_never(entry)

src = Directory("src", (
    File("main.py", 400), File("util.py", 250)))
root = Directory("root", (
    File("readme.md", 90), src, File("data.csv", 1200),
    Directory("src", ())))

print(list(find(root, "main.py")))
#: ['root/src/main.py']
print(list(find(root, "src")))
#: ['root/src', 'root/src']
```

**Dispatch on the node type.** `find()` follows `walk()`'s shape: a `match` with one case per
`Node` type, recursing with `yield from` into each `Directory`'s
entries.

**Match a directory, then descend.** A `Directory` can itself match `name`,
where `walk()` only ever yields file paths. Matching also continues
*into* a matched directory rather than stopping there, so a directory
named `"src"` and a file beneath it named `"src"` can both appear in
the results.

The second call shows a simpler duplication: `root`
holds two separate directories named `"src"`, and both come back as
`root/src`, so a path alone does not say which one matched.

</details>
</details>
</details>

## 2. A `Symlink` node

> Add a `Symlink` node to the `Node` union in `filesystem.py`,
> holding a name and a target path,
> and let the type checker report every operation that must change.
> Decide what `disk_usage()` and `walk()` should do with a link.

<details>
<summary>Where to look</summary>

[A Composite of Data Classes](../../Chapters/34_Patterns--Composite_and_Interpreter.md#a-composite-of-data-classes) ends each `match` with `assert_never()`.
Add a `@record` class to the `Node` union and run the type checker: it reports the unhandled type in each operation that lacks a case.
Then decide per operation what a link means, and avoid following the target into a subtree.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from collections.abc import Iterator
from typing import assert_never
from record import record

@record
class File:
    name: str
    size: int

@record
class Directory:
    name: str
    entries: tuple[Node, ...]

@record
class Symlink:
    name: str
    target: str

type Node = File | Directory | Symlink

def disk_usage(entry: Node) -> int:
    ...

def walk(entry: Node, prefix: str = "") -> Iterator[str]:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_2.py
from collections.abc import Iterator
from typing import assert_never
from record import record

@record
class File:
    name: str
    size: int

@record
class Directory:
    name: str
    entries: tuple[Node, ...]

@record
class Symlink:
    name: str
    target: str

type Node = File | Directory | Symlink

def disk_usage(entry: Node) -> int:
    match entry:
        case File(_, size):
            return size
        case Directory(_, entries):
            return sum(disk_usage(e) for e in entries)
        case Symlink():
            # A link contributes no size of its own
            return 0
        case _:
            assert_never(entry)

def walk(entry: Node, prefix: str = "") -> Iterator[str]:
    match entry:
        case File(name, _):
            yield prefix + name
        case Directory(name, entries):
            for e in entries:
                yield from walk(e, f"{prefix}{name}/")
        case Symlink(name, target):
            yield f"{prefix}{name} -> {target}"
        case _:
            assert_never(entry)

tree = Directory("root", (
    File("a.txt", 5), Symlink("shortcut", "/root/a.txt")))
print(disk_usage(tree))
#: 5
print(list(walk(tree)))
#: ['root/a.txt', 'root/shortcut -> /root/a.txt']
```

**Extend the union.** Adding `Symlink` to the union makes every `match` whose `case _` calls
`assert_never()` fail type checking, as the chapter says.
In both `disk_usage()` and `walk()`, the type checker reports that `entry` could
be a `Symlink` that no case handles, until you add the case shown
here. Deciding what a link should do is a judgment call, not
something the type checker picks for you.

**Avoid counting bytes twice.** `disk_usage()` counts a link
as free, since the bytes it references already get counted wherever
the real file lives. Adding the target's size again double-counts those bytes.

**Show a link without following it.** `walk()` reports the link as its own entry, `name -> target`, rather
than following it into the target's subtree, since following it could
loop forever if a link ever pointed back at one of its own ancestors.

</details>
</details>
</details>

## 3. `Neg` and `Div`

> Add `Neg` (negation) and `Div` (division) nodes to `expr.py`,
> along with `__neg__()` and `__truediv__()` operator methods.
> Update `evaluate()`, `to_infix()`, and `simplify()`.
> What should `simplify()` do with division by `Num(0)`?

<details>
<summary>Where to look</summary>

[The Nodes and the `Operators` Base](../../Chapters/34_Patterns--Composite_and_Interpreter.md#the-nodes-and-the-operators-base) explains why node classes inherit their operator methods and why `Expr` is the union that each walker's `assert_never()` checks.
Add both classes to `Expr`, put `__neg__()` and `__truediv__()` on `Operators`, and follow the type checker to every walker.
For `simplify()`, consider what rewrite is safe for `Div` and which input to leave alone.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from typing import assert_never
from record import record

class Operators:
    __slots__ = ()

    def __add__(self: Expr, other: Expr | int) -> Add:
        ...

    def __radd__(self: Expr, other: int) -> Add:
        ...

    def __mul__(self: Expr, other: Expr | int) -> Mul:
        ...

    def __rmul__(self: Expr, other: int) -> Mul:
        ...

    def __neg__(self: Expr) -> Neg:
        ...

    def __truediv__(self: Expr, other: Expr | int) -> Div:
        ...

    def __rtruediv__(self: Expr, other: int) -> Div:
        ...

@record
class Num(Operators):
    value: int

@record
class Var(Operators):
    name: str

@record
class Add(Operators):
    left: Expr
    right: Expr

@record
class Mul(Operators):
    left: Expr
    right: Expr

@record
class Neg(Operators):
    operand: Expr

@record
class Div(Operators):
    left: Expr
    right: Expr

type Expr = Num | Var | Add | Mul | Neg | Div

def wrap(value: Expr | int) -> Expr:
    ...

def evaluate(e: Expr, /, **env: int) -> float:
    ...

def to_infix(e: Expr) -> str:
    ...

def simplify(e: Expr) -> Expr:
    ...
```

<details>
<summary>Solution</summary>

If you write `__truediv__()`, the one division method the exercise names,
`x / 2` builds a `Div`, but `1 / x` raises a `TypeError`.
`int.__truediv__` returns `NotImplemented` for a `Var`, and Python finds no reflected method to try.
The chapter's `Operators` pairs `__add__()` with `__radd__()` and `__mul__()` with `__rmul__()` for that reason,
so the solution adds `__rtruediv__()` as well.

```python
# exercise_3.py
from typing import assert_never
from record import record

class Operators:
    __slots__ = ()

    def __add__(self: Expr, other: Expr | int) -> Add:
        return Add(self, wrap(other))

    def __radd__(self: Expr, other: int) -> Add:
        return Add(Num(other), self)

    def __mul__(self: Expr, other: Expr | int) -> Mul:
        return Mul(self, wrap(other))

    def __rmul__(self: Expr, other: int) -> Mul:
        return Mul(Num(other), self)

    def __neg__(self: Expr) -> Neg:
        return Neg(self)

    def __truediv__(self: Expr, other: Expr | int) -> Div:
        return Div(self, wrap(other))

    def __rtruediv__(self: Expr, other: int) -> Div:
        return Div(Num(other), self)

@record
class Num(Operators):
    value: int

@record
class Var(Operators):
    name: str

@record
class Add(Operators):
    left: Expr
    right: Expr

@record
class Mul(Operators):
    left: Expr
    right: Expr

@record
class Neg(Operators):
    operand: Expr

@record
class Div(Operators):
    left: Expr
    right: Expr

type Expr = Num | Var | Add | Mul | Neg | Div

def wrap(value: Expr | int) -> Expr:
    return Num(value) if isinstance(value, int) else value

def evaluate(e: Expr, /, **env: int) -> float:
    match e:
        case Num(value):
            return value
        case Var(name):
            return env[name]
        case Add(left, right):
            return (evaluate(left, **env)
                    + evaluate(right, **env))
        case Mul(left, right):
            return (evaluate(left, **env)
                    * evaluate(right, **env))
        case Neg(operand):
            return -evaluate(operand, **env)
        case Div(left, right):
            return (evaluate(left, **env)
                    / evaluate(right, **env))
        case _:
            assert_never(e)

def to_infix(e: Expr) -> str:
    match e:
        case Num(value):
            return str(value)
        case Var(name):
            return name
        case Add(left, right):
            return f"({to_infix(left)} + {to_infix(right)})"
        case Mul(left, right):
            return f"({to_infix(left)} * {to_infix(right)})"
        case Neg(operand):
            return f"-{to_infix(operand)}"
        case Div(left, right):
            return f"({to_infix(left)} / {to_infix(right)})"
        case _:
            assert_never(e)

def simplify(e: Expr) -> Expr:
    match e:
        case Num(_) | Var(_):
            return e
        case Add(left, right):
            lhs, rhs = simplify(left), simplify(right)
            match (lhs, rhs):
                case (Num(0), other) | (other, Num(0)):
                    return other
                case (Num(a), Num(b)):
                    return Num(a + b)
                case _:
                    if lhs is left and rhs is right:
                        return e
                    return Add(lhs, rhs)
        case Mul(left, right):
            lhs, rhs = simplify(left), simplify(right)
            match (lhs, rhs):
                case (Num(0), _) | (_, Num(0)):
                    return Num(0)
                case (Num(1), other) | (other, Num(1)):
                    return other
                case (Num(a), Num(b)):
                    return Num(a * b)
                case _:
                    if lhs is left and rhs is right:
                        return e
                    return Mul(lhs, rhs)
        case Neg(operand):
            match simplify(operand):
                case Num(a):
                    return Num(-a)
                case Neg(deeper):
                    return deeper  # Double negation
                case inner if inner is operand:
                    return e
                case inner:
                    return Neg(inner)
        case Div(left, right):
            # Folds nothing, even over Num(0)
            lhs, rhs = simplify(left), simplify(right)
            if lhs is left and rhs is right:
                return e
            return Div(lhs, rhs)
        case _:
            assert_never(e)

x = Var("x")
expr = (2 * x + 1) / -x
print(to_infix(expr))
#: (((2 * x) + 1) / -x)
print(evaluate(expr, x=3))
#: -2.3333333333333335
print(to_infix(simplify(Neg(Neg(x)) + Num(0))))
#: x
```

**Extend each walker by one case per node.** `evaluate()` and `to_infix()` gain one case per new node, and
`evaluate()` now returns a `float`, since `/` produces one.

**Fold negations where possible.** `simplify()` is the interesting one. For `Neg`, a constant operand
folds (`Neg(Num(a))` → `Num(-a)`), and a double negation cancels
(`Neg(Neg(inner))` → `inner`). Every case keeps the chapter's `is`
guard, so an unchanged subtree is still shared.

**Leave division for evaluation.** For `Div`, `simplify()` folds nothing. A quotient of two `int`s is
usually not an `int`, so it does not fit in a `Num`, and division by
`Num(0)` has no value to fold to. Nor should `simplify()` raise the
`ZeroDivisionError` itself. It rewrites a tree without evaluating it,
and a caller can simplify an expression it never evaluates, so an
exception raised in `simplify()` would report an error in a computation that
never runs. Leaving `Div(lhs, Num(0))` in the tree lets `evaluate()`
raise `ZeroDivisionError` when the division runs, and not before.
Python treats `1 / 0` in source the same way: the compiler accepts
it, and the error arrives when the line executes.

</details>
</details>
</details>

## 4. Precedence-aware `to_infix()`

> `to_infix()` parenthesizes every operation.
> Rewrite it to emit only the parentheses that precedence requires,
> so `2 * x + 1` renders as `2 * x + 1` but `(x + 1) * (x + 2)` keeps its parentheses.

<details>
<summary>Where to look</summary>

[New Operations, Same Tree](../../Chapters/34_Patterns--Composite_and_Interpreter.md#new-operations-same-tree) builds `to_infix()` as one more walker over `Expr`.
Give each operator a precedence number and pass the enclosing operator's precedence down the recursion.
A subexpression adds parentheses only when its own precedence is lower than the context it sits in.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from typing import Final, assert_never
from record import record

class Operators:
    __slots__ = ()

    def __add__(self: Expr, other: Expr | int) -> Add:
        ...

    def __radd__(self: Expr, other: int) -> Add:
        ...

    def __mul__(self: Expr, other: Expr | int) -> Mul:
        ...

    def __rmul__(self: Expr, other: int) -> Mul:
        ...

@record
class Num(Operators):
    value: int

@record
class Var(Operators):
    name: str

@record
class Add(Operators):
    left: Expr
    right: Expr

@record
class Mul(Operators):
    left: Expr
    right: Expr

type Expr = Num | Var | Add | Mul

def wrap(value: Expr | int) -> Expr:
    ...

PRECEDENCE: Final[dict[type[Expr], int]] = {
    Add: 1, Mul: 2, Num: 3, Var: 3}

def to_infix(e: Expr, parent_prec: int = 0) -> str:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_4.py
from typing import Final, assert_never
from record import record

class Operators:
    __slots__ = ()

    def __add__(self: Expr, other: Expr | int) -> Add:
        return Add(self, wrap(other))

    def __radd__(self: Expr, other: int) -> Add:
        return Add(Num(other), self)

    def __mul__(self: Expr, other: Expr | int) -> Mul:
        return Mul(self, wrap(other))

    def __rmul__(self: Expr, other: int) -> Mul:
        return Mul(Num(other), self)

@record
class Num(Operators):
    value: int

@record
class Var(Operators):
    name: str

@record
class Add(Operators):
    left: Expr
    right: Expr

@record
class Mul(Operators):
    left: Expr
    right: Expr

type Expr = Num | Var | Add | Mul

def wrap(value: Expr | int) -> Expr:
    return Num(value) if isinstance(value, int) else value

PRECEDENCE: Final[dict[type[Expr], int]] = {
    Add: 1, Mul: 2, Num: 3, Var: 3}

def to_infix(e: Expr, parent_prec: int = 0) -> str:
    match e:
        case Num(value):
            return str(value)
        case Var(name):
            return name
        case Add(left, right):
            prec = PRECEDENCE[Add]
            lhs = to_infix(left, prec)
            rhs = to_infix(right, prec + 1)
            s = f"{lhs} + {rhs}"
        case Mul(left, right):
            prec = PRECEDENCE[Mul]
            lhs = to_infix(left, prec)
            rhs = to_infix(right, prec + 1)
            s = f"{lhs} * {rhs}"
        case _:
            assert_never(e)
    my_prec = PRECEDENCE[type(e)]
    return f"({s})" if my_prec < parent_prec else s

x = Var("x")
print(to_infix(2 * x + 1))
#: 2 * x + 1
print(to_infix((x + 1) * (x + 2)))
#: (x + 1) * (x + 2)
```

**Parenthesize by context.** Each recursive call passes down the precedence its *parent* requires.
A child only gets parentheses when its own operator binds more
loosely than what the parent needs. `Mul`'s children therefore need
parens around a lower-precedence `Add`, while `Add`'s children never
need parens around another `Add`.

**Guard the right operand.** Passing `prec + 1` (rather than
`prec`) for the right operand is a simple, always-safe rule: it can
occasionally print one redundant pair of parentheses around a
right-hand child at the *same* precedence as its parent
(`x + (x + 1)` instead of the fully terse `x + x + 1`), but it never
omits a pair that changes the expression's meaning.

</details>
</details>
</details>

## 5. `derivative(e, name)`

> Write `derivative(e, name)`:
> a function that returns the symbolic derivative of an expression with respect to a variable,
> using the sum rule and the product rule.
> Run its results through `simplify()` and compare.

<details>
<summary>Where to look</summary>

[Simplification Rewrites the Tree](../../Chapters/34_Patterns--Composite_and_Interpreter.md#simplification-rewrites-the-tree) shows a walker that returns a new `Expr` instead of a value.
`derivative()` is another such walker, with one case per node: a `Num` and a `Var` give constants, an `Add` applies the sum rule, and a `Mul` applies the product rule.
The raw result is correct but cluttered, so pass it through `simplify()` to see the difference.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from typing import assert_never
from record import record

class Operators:
    __slots__ = ()

    def __add__(self: Expr, other: Expr | int) -> Add:
        ...

    def __radd__(self: Expr, other: int) -> Add:
        ...

    def __mul__(self: Expr, other: Expr | int) -> Mul:
        ...

    def __rmul__(self: Expr, other: int) -> Mul:
        ...

@record
class Num(Operators):
    value: int

@record
class Var(Operators):
    name: str

@record
class Add(Operators):
    left: Expr
    right: Expr

@record
class Mul(Operators):
    left: Expr
    right: Expr

type Expr = Num | Var | Add | Mul

def wrap(value: Expr | int) -> Expr:
    ...

def to_infix(e: Expr) -> str:
    ...

def simplify(e: Expr) -> Expr:
    ...

def derivative(e: Expr, name: str) -> Expr:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_5.py
from typing import assert_never
from record import record

class Operators:
    __slots__ = ()

    def __add__(self: Expr, other: Expr | int) -> Add:
        return Add(self, wrap(other))

    def __radd__(self: Expr, other: int) -> Add:
        return Add(Num(other), self)

    def __mul__(self: Expr, other: Expr | int) -> Mul:
        return Mul(self, wrap(other))

    def __rmul__(self: Expr, other: int) -> Mul:
        return Mul(Num(other), self)

@record
class Num(Operators):
    value: int

@record
class Var(Operators):
    name: str

@record
class Add(Operators):
    left: Expr
    right: Expr

@record
class Mul(Operators):
    left: Expr
    right: Expr

type Expr = Num | Var | Add | Mul

def wrap(value: Expr | int) -> Expr:
    return Num(value) if isinstance(value, int) else value

def to_infix(e: Expr) -> str:
    match e:
        case Num(value):
            return str(value)
        case Var(name):
            return name
        case Add(left, right):
            return f"({to_infix(left)} + {to_infix(right)})"
        case Mul(left, right):
            return f"({to_infix(left)} * {to_infix(right)})"
        case _:
            assert_never(e)

def simplify(e: Expr) -> Expr:
    match e:
        case Num(_) | Var(_):
            return e
        case Add(left, right):
            lhs, rhs = simplify(left), simplify(right)
            match (lhs, rhs):
                case (Num(0), other) | (other, Num(0)):
                    return other
                case (Num(a), Num(b)):
                    return Num(a + b)
                case _:
                    if lhs is left and rhs is right:
                        return e
                    return Add(lhs, rhs)
        case Mul(left, right):
            lhs, rhs = simplify(left), simplify(right)
            match (lhs, rhs):
                case (Num(0), _) | (_, Num(0)):
                    return Num(0)
                case (Num(1), other) | (other, Num(1)):
                    return other
                case (Num(a), Num(b)):
                    return Num(a * b)
                case _:
                    if lhs is left and rhs is right:
                        return e
                    return Mul(lhs, rhs)
        case _:
            assert_never(e)

def derivative(e: Expr, name: str) -> Expr:
    match e:
        case Num(_):
            return Num(0)
        case Var(n):
            return Num(1) if n == name else Num(0)
        # Sum rule: (f + g)' = f' + g'
        case Add(left, right):
            return Add(derivative(left, name),
                       derivative(right, name))
        # Product rule: (fg)' = f'g + fg'
        case Mul(left, right):
            return Add(Mul(derivative(left, name), right),
                       Mul(left, derivative(right, name)))
        case _:
            assert_never(e)

x = Var("x")
d = derivative(x * x, "x")
print(to_infix(d))
#: ((1 * x) + (x * 1))
print(to_infix(simplify(d)))
#: (x + x)
```

**Differentiate the leaves.** `derivative()` walks the tree like `evaluate()` and
`to_infix()`, one case per node type, but produces another `Expr`
instead of a number or a string. A `Num` never changes, so its
derivative is always `0`. The derivative of `Var(n)` is `1` with
respect to itself and `0` with respect to every other variable.

**Combine the children's derivatives.** `Add`'s case is the sum rule. `Mul`'s case is the product rule, which
keeps both the derivative *and* the original, undifferentiated
subtree on each side, because the rule multiplies one by the other.

Running the raw result through `simplify()` turns `((1 * x) + (x * 1))`
into the much more readable `(x + x)` (reaching `2 * x` takes a further
rule, "combine like terms," that this `simplify()` does not
implement). A full `Expr` that also includes `Neg` and `Div`
(exercise 3's additions) needs a quotient rule for `Div`, which
produces a squared denominator beyond what `simplify()`'s current
rules handle, so this solution leaves that rule for a further
exercise.

</details>
</details>
</details>

## 6. Declining with `NotImplemented`

> At runtime, `"a" + x` silently builds `Add(Num("a"), x)`,
> an ill-typed tree the type checker rejects in source it can see.
> Rewrite all four operator methods to return `NotImplemented` for an operand they cannot use
> ([*Multiple Dispatching*](../../Chapters/32_Patterns--Multiple_Dispatching.md#operators-dispatch-twice) shows the idiom),
> and confirm that `"a" + x` and `x + "a"` both now raise a `TypeError`.

<details>
<summary>Where to look</summary>

[Operators That Build Nodes](../../Chapters/34_Patterns--Composite_and_Interpreter.md#operators-that-build-nodes) defines the four operator methods, and the Multiple Dispatching chapter's [Operators Dispatch Twice](../../Chapters/32_Patterns--Multiple_Dispatching.md#operators-dispatch-twice) shows the idiom.
In each method, test the operand with `isinstance()` and return `NotImplemented` when it is neither an `Expr` nor an `int`.
Python then tries the reflected method on the other operand and, when that declines too, raises the `TypeError` for you.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
from exceptions import expected
from record import record

class Operators:
    __slots__ = ()

    def __add__(self: Expr, other: Expr | int) -> Add:
        ...

    def __radd__(self: Expr, other: int) -> Add:
        ...

    def __mul__(self: Expr, other: Expr | int) -> Mul:
        ...

    def __rmul__(self: Expr, other: int) -> Mul:
        ...

@record
class Num(Operators):
    value: int

@record
class Var(Operators):
    name: str

@record
class Add(Operators):
    left: Expr
    right: Expr

@record
class Mul(Operators):
    left: Expr
    right: Expr

type Expr = Num | Var | Add | Mul

def wrap(value: Expr | int) -> Expr:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_6.py
from exceptions import expected
from record import record

class Operators:
    __slots__ = ()

    def __add__(self: Expr, other: Expr | int) -> Add:
        if isinstance(other, Operators | int):
            return Add(self, wrap(other))
        return NotImplemented

    def __radd__(self: Expr, other: int) -> Add:
        if isinstance(other, int):
            return Add(Num(other), self)
        return NotImplemented

    def __mul__(self: Expr, other: Expr | int) -> Mul:
        if isinstance(other, Operators | int):
            return Mul(self, wrap(other))
        return NotImplemented

    def __rmul__(self: Expr, other: int) -> Mul:
        if isinstance(other, int):
            return Mul(Num(other), self)
        return NotImplemented

@record
class Num(Operators):
    value: int

@record
class Var(Operators):
    name: str

@record
class Add(Operators):
    left: Expr
    right: Expr

@record
class Mul(Operators):
    left: Expr
    right: Expr

type Expr = Num | Var | Add | Mul

def wrap(value: Expr | int) -> Expr:
    return Num(value) if isinstance(value, int) else value

x = Var("x")
print(type(2 * x + 1).__name__, (2 * x + 1).right)
#: Add Num(value=1)
with expected(TypeError):
    "a" + x  # type: ignore
#: [TypeError] can only concatenate str (not "Var") to str
with expected(TypeError):
    x + "a"  # type: ignore
#: [TypeError] unsupported operand type(s) for +: 'Var' and
#: 'str'
```

Before the change, `"a" + x` produces `Add(Num("a"), Var("x"))`: a
`Num` whose `value` is a string, and every walker then mishandles
that `Num`. `str.__add__` declines a `Var`, so Python falls back to
`Var.__radd__("a")`. The old `__radd__()` accepts anything, wrapping
the string in a `Num` without looking at it.

**Hand the decision back to Python.** Returning `NotImplemented` puts the decision back where it belongs.
`__radd__()` now answers only for an `int`, so both sides decline and
Python raises the `TypeError` it raises for any other mismatched pair.
The message comes from `str`, which is the right source: the left
operand is what the caller wrote first, and nothing in this expression
language ever claims to extend `str`.

**Guard the forward direction too.** The forward methods need the same guard for the same reason. Without
it `x + "a"` wraps the string in a `Num` and builds the ill-typed tree
from the other direction, so all four methods decline what they cannot
use. The two messages differ because a different object gets the last
word: `str` reports `"a" + x`, and Python's own fallback reports
`x + "a"`, once both operands have declined.

**Declare the node each method builds.** Each method declares the type it really returns, `Add` or `Mul`,
even though it can also return `NotImplemented`.
[*Multiple Dispatching*](../../Chapters/32_Patterns--Multiple_Dispatching.md#operators-dispatch-twice)
explains the convention: typeshed gives the sentinel a type
inheriting `Any`, so returning it satisfies any declared return type.
The declaration also lets `(2 * x + 1).right` resolve for a caller.

`NotImplemented` closes a runtime hole, not a type-checking one.
The type checker already rejects
`"a" + x` in source it can see, which is why the listing's `"a" + x`
line carries a `# type: ignore` to keep `exercise_6.py` in the build. The runtime hole
is the gap between what the checker sees and what runs. Closing it matters
when a program builds the expression from data the type checker never
sees, the case an interpreter exists to handle.

</details>
</details>
</details>

## 7. A third walker: `to_html()`

> Write a third walker over `Template` in `template_query.py`, `to_html()`,
> that emits the literal pieces unchanged and replaces `<`, `>`,
> and `&` in every interpolated value with their HTML entities.
> Show that `t"<p>{comment}</p>"` survives a `comment` containing a `<script>` tag.

<details>
<summary>Where to look</summary>

[A Template Is a Tree](../../Chapters/34_Patterns--Composite_and_Interpreter.md#a-template-is-a-tree) shows that a `Template` already separates literal strings from `Interpolation` objects.
Loop over the template, copy each string piece unchanged, and pass each interpolation's value through `html.escape()`.
Comparing with an f-string on the same input shows what the structure keeps that a finished string loses.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
from html import escape
from string.templatelib import Interpolation, Template

def to_html(template: Template) -> str:
    ...
```

<details>
<summary>Solution</summary>

If you build the page with an f-string and pass the finished string to `escape()`,
the `<script>` tag comes out escaped, but so do the author's `<p>` tags,
and the output begins `&lt;p&gt;`.
A finished string no longer records which characters the author typed.
The exercise asks for the literal pieces unchanged,
so the solution escapes each interpolation's value and copies each string piece as it is.

```python
# exercise_7.py
from html import escape
from string.templatelib import Interpolation, Template

def to_html(template: Template) -> str:
    parts: list[str] = []
    for piece in template:
        if isinstance(piece, Interpolation):
            parts.append(escape(str(piece.value)))
        else:
            parts.append(piece)
    return "".join(parts)

comment = "<script>steal()</script> & run"
print(to_html(t"<p>{comment}</p>"))
#: <p>&lt;script&gt;steal()&lt;/script&gt; &amp; run</p>
print(f"<p>{comment}</p>")
#: <p><script>steal()</script> & run</p>
```

**Add an operation beside the others.** `to_html()` is the third operation over `Template`, and it changes
nothing about `to_query()` and `to_shape()`, the property the chapter
keeps demonstrating on `Expr`. The whole walker is the same loop with
a different body, because the structure already separates the literal
pieces from the interpolations.

**Escape the interpolated values.** `html.escape()` replaces the characters, so the exercise's
real content is *where* `to_html()` calls it: on the interpolated
values. The `<p>` and `</p>` the author typed pass through untouched,
so the output is valid HTML rather than a document with its own tags
escaped.

The f-string on the last line is the comparison. It produces a
`<script>` tag that a browser runs, and nothing downstream can
intervene, because by the time a function receives that string the
tag and the paragraph markup are the same kind of text. The template
version never loses the distinction, so escaping is a decision the
renderer can still make.

</details>
</details>
</details>

## 8. An iterative walk over a deep tree

> Build a left-deep expression by folding `+` over a few thousand `Num` nodes,
> and confirm that `evaluate()` raises a `RecursionError`.
> Then write `evaluate_iterative()`,
> which walks the same tree with an explicit stack and no recursion,
> and check that the two agree on a small expression.
> Raising the limit with `sys.setrecursionlimit()` also avoids the error.
> Say what it costs.

<details>
<summary>Where to look</summary>

[Evaluation Is a Tree Walk](../../Chapters/34_Patterns--Composite_and_Interpreter.md#evaluation-is-a-tree-walk) shows `evaluate()` recursing once per node, so tree depth becomes call-stack depth.
For `evaluate_iterative()`, keep your own list as a stack of nodes and a second stack of values, and process each node after its children.
For the `sys.setrecursionlimit()` question, consider what the interpreter's own stack must hold at that depth.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
from enum import Enum
from typing import assert_never
from exceptions import expect
from record import record

class Operators:
    __slots__ = ()

    def __add__(self: Expr, other: Expr | int) -> Add:
        ...

    def __radd__(self: Expr, other: int) -> Add:
        ...

    def __mul__(self: Expr, other: Expr | int) -> Mul:
        ...

    def __rmul__(self: Expr, other: int) -> Mul:
        ...

@record
class Num(Operators):
    value: int

@record
class Var(Operators):
    name: str

@record
class Add(Operators):
    left: Expr
    right: Expr

@record
class Mul(Operators):
    left: Expr
    right: Expr

type Expr = Num | Var | Add | Mul

def wrap(value: Expr | int) -> Expr:
    ...

def evaluate(e: Expr, /, **env: int) -> int:
    ...

class Op(Enum):
    ADD = "+"
    MUL = "*"

def evaluate_iterative(e: Expr, /, **env: int) -> int:
    ...
```

<details>
<summary>Solution</summary>

If you push an `Add` or `Mul` node's two children with no marker behind them,
`evaluate_iterative(2 * x + 1, x=3)` returns `1` instead of `7`.
`values` collects the three leaves, and the function returns the last one it reached.
The solution pushes an `Op` beneath each pair of children,
so the combine runs once both values are on `values`.

```python
# exercise_8.py
from enum import Enum
from typing import assert_never
from exceptions import expect
from record import record

class Operators:
    __slots__ = ()

    def __add__(self: Expr, other: Expr | int) -> Add:
        return Add(self, wrap(other))

    def __radd__(self: Expr, other: int) -> Add:
        return Add(Num(other), self)

    def __mul__(self: Expr, other: Expr | int) -> Mul:
        return Mul(self, wrap(other))

    def __rmul__(self: Expr, other: int) -> Mul:
        return Mul(Num(other), self)

@record
class Num(Operators):
    value: int

@record
class Var(Operators):
    name: str

@record
class Add(Operators):
    left: Expr
    right: Expr

@record
class Mul(Operators):
    left: Expr
    right: Expr

type Expr = Num | Var | Add | Mul

def wrap(value: Expr | int) -> Expr:
    return Num(value) if isinstance(value, int) else value

def evaluate(e: Expr, /, **env: int) -> int:
    match e:
        case Num(value):
            return value
        case Var(name):
            return env[name]
        case Add(left, right):
            return (evaluate(left, **env)
                    + evaluate(right, **env))
        case Mul(left, right):
            return (evaluate(left, **env)
                    * evaluate(right, **env))
        case _:
            assert_never(e)

# A pending combine, behind the children it consumes:
class Op(Enum):
    ADD = "+"
    MUL = "*"

def evaluate_iterative(e: Expr, /, **env: int) -> int:
    work: list[Expr | Op] = [e]
    values: list[int] = []
    while work:
        item = work.pop()
        match item:
            case Op.ADD:
                right_value, left_value = (
                    values.pop(), values.pop())
                values.append(left_value + right_value)
            case Op.MUL:
                right_value, left_value = (
                    values.pop(), values.pop())
                values.append(left_value * right_value)
            case Num(value):
                values.append(value)
            case Var(name):
                values.append(env[name])
            case Add(left, right):
                work += [Op.ADD, right, left]
            case Mul(left, right):
                work += [Op.MUL, right, left]
            case _:
                assert_never(item)
    return values.pop()

deep: Expr = Num(0)
for n in range(1, 2001):
    deep = deep + Num(n)

expect(RecursionError, evaluate, deep)
#: [RecursionError] maximum recursion depth exceeded
print(evaluate_iterative(deep))
#: 2001000

x = Var("x")
small = 2 * x + 1
print(evaluate(small, x=3), evaluate_iterative(small, x=3))
#: 7 7
```

The tree is 2000 `Add` nodes deep, and `evaluate()` needs one frame
per level against a limit of 1000, so it fails before reaching the
bottom. Nothing about the expression is unusual. Only its shape is.

**Defer the combine behind its children.** The stack version cannot be a straight translation, and this is where
the exercise bites. Pushing children and popping them in a loop gives
a pre-order walk that visits every node and computes nothing, because
an `Add` can combine its children's values only *after* the children
have produced them. The solution stacks the pending operation behind
its own children: `work += [Op.ADD, right, left]` puts `Op.ADD`
deepest, so it comes off last, by which point the two values it needs
are on `values`.

**Preserve operand order.** Pushing `right` before `left` makes `left` pop
first, and that order matters for the subtraction and division a fuller
language adds.

**Keep the match exhaustive.** `Op` is an enum rather than a string so the `match` stays exhaustive.
`work` holds `Expr | Op`, and every member of both types has its own
case, so `assert_never()` still type-checks. A string marker leaves
`case _` reachable and the guarantee gone.

`sys.setrecursionlimit()` avoids the error for `evaluate()`, and it
costs more than it appears to. A call from one Python function to
another uses no C stack, so with the limit raised to `10**9`,
`evaluate()` walks a million-level tree. Anything that recurses
through C still stops: `repr()` or `hash()` on that same tree raises
a `RecursionError` that reports a stack overflow, whatever the limit
says. Each pending level also holds a frame and a fresh `env` dict,
so memory grows with depth. The limit is global too, so a library
that raises it changes the behavior of code that never asked. The
iterative walk keeps its pending work in one list and changes no
setting that other code can see.

</details>
</details>
</details>

## 9. Reopening the set of node types

> A plugin package needs to add its own entry types to `filesystem.py` without editing your code.
> Sketch what breaks, then write the version of `disk_usage()` that supports the plugin's entry types.
> Which of the two designs,
> a `match` over a union or a method on a base class,
> would you use for a file system,
> and which for the expression language in `expr.py`?

<details>
<summary>Where to look</summary>

[A Composite of Data Classes](../../Chapters/34_Patterns--Composite_and_Interpreter.md#a-composite-of-data-classes) closes `Node` as a union, so every operation is a `match` in your module.
To open the set, move `disk_usage()` onto an abstract base class as an `@abstractmethod`, and let each entry type implement it.
When you choose between the designs, ask who owns the list of node types and who writes new operations.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_9.py
from abc import ABC, abstractmethod
from typing import override
from record import record

class Entry(ABC):
    __slots__ = ()
    name: str

    @abstractmethod
    def disk_usage(self) -> int: ...

@record
class File(Entry):
    name: str
    size: int

    @override
    def disk_usage(self) -> int:
        ...

@record
class Directory(Entry):
    name: str
    entries: tuple[Entry, ...]

    @override
    def disk_usage(self) -> int:
        ...

@record
class Symlink(Entry):
    name: str
    target: str

    @override
    def disk_usage(self) -> int:
        ...
```

<details>
<summary>Solution</summary>

```python
# exercise_9.py
from abc import ABC, abstractmethod
from typing import override
from record import record

class Entry(ABC):
    __slots__ = ()
    name: str

    @abstractmethod
    def disk_usage(self) -> int: ...

@record
class File(Entry):
    name: str
    size: int

    @override
    def disk_usage(self) -> int:
        return self.size

@record
class Directory(Entry):
    name: str
    entries: tuple[Entry, ...]

    @override
    def disk_usage(self) -> int:
        return sum(e.disk_usage() for e in self.entries)

# A plugin package adds a node type, editing nothing above:
@record
class Symlink(Entry):
    name: str
    target: str

    @override
    def disk_usage(self) -> int:
        return 0

src = Directory("src", (
    File("main.py", 400), File("util.py", 250)))
root = Directory("root", (
    File("readme.md", 90), src, Symlink("latest", "src")))
print(root.disk_usage())
#: 740
```

What breaks in the closed version is not subtle. `type Node = File |
Directory` lives in your source, so a plugin cannot extend it. The
type checker does warn the plugin author: `ty` reports a `Symlink`
passed to `disk_usage()`, or placed in a `Directory`'s entries, as
`invalid-argument-type`. The warning leaves the plugin nothing to fix,
because the union it would have to extend is yours. Code the checker
never sees fares worse: its `Symlink` falls through every case to
`assert_never()`, which raises an `AssertionError` at runtime. The plugin's alternatives
are to vendor a patched copy of your module or to persuade you to add
the case. The open design removes that coupling.

**Move the operation onto the classes.** Moving the operation back onto the classes reverses the trade the
chapter spent the first two sections making. Adding `Symlink` now
costs nothing to existing code, while adding a *new operation* costs
a method in every class, including the ones you do not own. The
`@abstractmethod` keeps the plugin honest: Python refuses to
instantiate a subclass that defines no `disk_usage()`.

For a file system, use the open design. Which node types exist is a
fact about the operating system and about whatever the next version
adds, not a decision your code gets to make. Third-party node types
are the normal case.

For `expr.py`, use the closed one. The four node types *are* the
grammar, so a plugin adding a fifth does not extend the language but
defines a different one. Every walker would then be silently wrong
rather than helpfully extended. The `assert_never()` that reads as an
obstacle in the file system reads as the point here: when the grammar
does grow a `Neg`, the type checker hands you the list of walkers to
update.

</details>
</details>
</details>
