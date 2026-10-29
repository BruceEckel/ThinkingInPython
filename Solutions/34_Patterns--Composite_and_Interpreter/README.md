# Composite and Interpreter: Solutions

## 1. `find(entry, name)`

> Add `find(entry, name)` to `filesystem.py`:
> a generator yielding the path of every entry whose name matches.
> A directory can match, and matching should continue into it.

<details>
<summary>Where to look</summary>

[The Classic *Composite*](../../Chapters/34_Patterns--Composite_and_Interpreter.md#the-classic-composite)
and [A *Composite* of Data Classes](../../Chapters/34_Patterns--Composite_and_Interpreter.md#a-composite-of-data-classes)
show `walk()` recursing through a `Directory`,
the classic version through overridden methods and the data-class version through `match`.
Write `find()` in the same shape,
with one case per `Node` type and `yield from` for the recursion.
A `Directory` case checks its name before it descends,
and it carries the path prefix down.

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
type Location = str

def find(entry: Node, name: str,
         prefix: Location = "") -> Iterator[Location]:
    ...
```

<details>
<summary>Done when</summary>

over the chapter's `TREE` from `test_filesystem.py`,
`find(TREE, "sub")` yields `['top/sub']` and `find(TREE, "b")` yields `['top/sub/b']`.
A directory named `"src"` holding a file named `"src"` yields both paths,
`'src'` and then `'src/src'`.

<details>
<summary>Solution</summary>

If you copy `walk()` and add a name test to the `File` case alone,
`find(root, "main.py")` still works, but `list(find(root, "src"))` is `[]`.
The copied `Directory` case descends straight into its children,
so every path it yields lies beneath the directory.
The exercise says a directory can match,
so the solution's `Directory` case tests its name before it descends.

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
type Location = str

def find(entry: Node, name: str,
         prefix: Location = "") -> Iterator[Location]:
    match entry:
        case File(n, _):
            if n == name:
                yield prefix + n
        case Directory(n, entries):
            if n == name:
                yield prefix + n
            for child in entries:
                yield from find(
                    child, name, f"{prefix}{n}/")
        case _:
            assert_never(entry)

src = Directory("src", (
    File("main.py", 400), File("util.py", 250)))
root = Directory("root", (
    File("readme.md", 90), src, File("data.csv", 1200),
    Directory("src", ())))

print(list(find(root, "main.py")))
#: ['root/src/main.py']
print(list(find(root, "src")))  # [1]
#: ['root/src', 'root/src']
```

**Match a directory, then descend.**
A `Directory` can match `name`, where `walk()` yields only file paths.
Matching also continues into a matched directory,
so a directory named `"src"` and a file beneath it named `"src"` can both appear in the results.

The two paths at `[1]` come from two separate directories named `"src"`,
so a path alone does not say which one matched.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[A *Composite* of Data Classes](../../Chapters/34_Patterns--Composite_and_Interpreter.md#a-composite-of-data-classes)
ends each `match` with `assert_never()`.
Add a `@record` class to the `Node` union and run the type checker.
The type checker reports the new type at each operation's `assert_never()` call.
Then decide per operation what a link means.
Treating the link as a leaf keeps each walk to one visit per node.

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
type Location = str

def disk_usage(entry: Node) -> int:
    ...

def walk(
    entry: Node, prefix: Location = ""
) -> Iterator[Location]:
    ...
```

<details>
<summary>Done when</summary>

`uv run ty check` passes on your file,
and deleting the `Symlink` case from either `disk_usage()` or `walk()` brings back a `type-assertion-failure` at that function's `assert_never()`.
Both functions also return normally on a tree holding `Symlink("up", "/root")`,
a link to its root.

<details>
<summary>Solution</summary>

If you follow the link,
resolving `target` to its node and recursing into that node,
`disk_usage(tree)` returns `10`.
`disk_usage()` counts `a.txt` once as a file and again through `shortcut`.
A link to an ancestor, such as `Symlink("up", "/root")`,
makes `disk_usage()` recurse into that ancestor again and again until Python raises a `RecursionError`.
The solution shows the link as its own entry and counts it as zero bytes,
so each operation visits every node once.

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
type Location = str

def disk_usage(entry: Node) -> int:
    match entry:
        case File(_, size):
            return size
        case Directory(_, entries):
            return sum(disk_usage(child)
                       for child in entries)
        case Symlink():
            # A link contributes no size of its own
            return 0
        case _:
            assert_never(entry)

def walk(
    entry: Node, prefix: Location = ""
) -> Iterator[Location]:
    match entry:
        case File(name, _):
            yield prefix + name
        case Directory(name, entries):
            for child in entries:
                yield from walk(child, f"{prefix}{name}/")
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

**Extend the union.**
Once `Symlink` joins the union,
the type checker rejects every `match` whose `case _` calls `assert_never()`.
In both `disk_usage()` and `walk()`,
it reports that `entry` can still be a `Symlink` at the `assert_never()` call.
The `Symlink` case in each function clears that report.
The type checker reports where a case belongs.
You decide what the case does.

**Count each byte once.**
`disk_usage()` counts a link as zero bytes,
since the target file's own entry counts its bytes.
Adding the target's size again double-counts those bytes.

**Stop at the link.**
If `walk()` follows a link back to one of its ancestors,
it re-enters that ancestor until Python raises a `RecursionError`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[The Nodes and the `Operators` Base](../../Chapters/34_Patterns--Composite_and_Interpreter.md#the-nodes-and-the-operators-base)
explains why node classes inherit their operator methods and why `Expr` is the union that each walker's `assert_never()` checks.
Add both classes to `Expr`, put `__neg__()` and `__truediv__()` on `Operators`,
and follow the type checker to every walker.
For `simplify()`, consider what rewrite is safe for `Div` and which input to leave alone.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from collections.abc import Mapping
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

def evaluate(e: Expr, env: Mapping[str, int]) -> float:
    ...

def to_infix(e: Expr) -> str:
    ...

def simplify(e: Expr) -> Expr:
    ...
```

<details>
<summary>Done when</summary>

`uv run ty check` passes,
`evaluate((2 * x + 1) / -x, {"x": 3})` returns `-2.3333333333333335`,
`1 / x` builds a `Div` as `x / 2` does,
and `simplify(Neg(Neg(x)) + Num(0))` renders as `x`.
You can say which function reports division by `Num(0)`, and why there.

<details>
<summary>Solution</summary>

If you write `__truediv__()`, the one division method the exercise names,
`x / 2` builds a `Div`, but `1 / x` raises a `TypeError`.
`int.__truediv__()` returns `NotImplemented` for a `Var`.
Python then looks for the reflected method, `x.__rtruediv__()`,
which is missing.
The chapter's `Operators` pairs `__add__()` with `__radd__()` and `__mul__()` with `__rmul__()` for that reason,
so the solution adds `__rtruediv__()` as well.

```python
# exercise_3.py
from collections.abc import Mapping
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

def evaluate(e: Expr, env: Mapping[str, int]) -> float:
    match e:
        case Num(value):
            return value
        case Var(name):
            return env[name]
        case Add(left, right):
            return (evaluate(left, env)
                    + evaluate(right, env))
        case Mul(left, right):
            return (evaluate(left, env)
                    * evaluate(right, env))
        case Neg(operand):
            return -evaluate(operand, env)
        case Div(left, right):
            return (evaluate(left, env)
                    / evaluate(right, env))
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
print(evaluate(expr, {"x": 3}))
#: -2.3333333333333335
print(to_infix(simplify(Neg(Neg(x)) + Num(0))))
#: x
```

**Add one case per new node.**
`evaluate()` now returns a `float`, since `/` produces one.

**Fold negations where possible.**
The `Neg` case keeps the chapter's `is` test,
so an unchanged subtree stays shared.

**Leave division for evaluation.**
A `Num` holds an `int`, while a quotient of two `int`s is usually a fraction,
so the `Div` stays in the tree with its operands simplified.
Division by `Num(0)` is undefined.

`simplify()` should leave the `ZeroDivisionError` to `evaluate()`.
`simplify()` rewrites a tree.
`evaluate()` computes the tree's value.
A caller can simplify an expression and then discard it,
so an exception raised in `simplify()` could report an error in a division the program throws away.
Leaving `Div(lhs, Num(0))` in the tree lets `evaluate()` raise `ZeroDivisionError` at the moment the division runs.
Python treats `1 / 0` in source the same way.
The compiler accepts it.
Python raises `ZeroDivisionError` when the line executes.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. Precedence-aware `to_infix()`

> `to_infix()` parenthesizes every operation.
> Rewrite it to emit only the parentheses that precedence requires,
> so `2 * x + 1` renders as `2 * x + 1` but `(x + 1) * (x + 2)` keeps its parentheses.

<details>
<summary>Where to look</summary>

[New Operations, Same Tree](../../Chapters/34_Patterns--Composite_and_Interpreter.md#new-operations-same-tree)
builds `to_infix()` as one more walker over `Expr`.
Give each operator a precedence number and pass the enclosing operator's precedence down the recursion.
A subexpression adds parentheses only when its own precedence is lower than the precedence its parent passes down.

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
<summary>Done when</summary>

your `to_infix()` prints `2 * x + 1` and `(x + 1) * (x + 2)` for the exercise's two expressions,
and `2 * (x + 1)` keeps its parentheses while `x * x + 1` gets none.
One redundant pair on a right-hand operand of equal precedence,
as in `x + (x + 1)`, is acceptable.

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

**Parenthesize by context.**
A child gets parentheses only when its own operator binds more loosely than what the parent needs.
A `Mul` therefore parenthesizes an `Add` child,
while an `Add` leaves another `Add` on its left bare.

**Guard the right operand.**
Passing `prec + 1` for the right operand, rather than `prec`,
is simple and always safe.
The rule can print one redundant pair of parentheses around a right-hand child at the same precedence as its parent,
as in `x + (x + 1)` where `x + x + 1` is enough.
It still keeps every pair that the expression's meaning requires.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[Simplification Rewrites the Tree](../../Chapters/34_Patterns--Composite_and_Interpreter.md#simplification-rewrites-the-tree)
shows a walker that returns a new `Expr` instead of a value.
`derivative()` is another such walker, with one case per node:
a `Num` and a `Var` give constants, an `Add` applies the sum rule,
and a `Mul` applies the product rule.
The raw result is correct but cluttered,
so pass it through `simplify()` to see the difference.

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
<summary>Done when</summary>

`to_infix(simplify(derivative(x * x, "x")))` prints `(x + x)`,
while the raw result shows both product-rule terms, `(1 * x)` and `(x * 1)`.
With `simplify()` applied, the derivative of `2 * x + 1` renders as `2`,
and the derivative of `x * x` with respect to `"y"` renders as `0`.

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

**Differentiate the leaves.**
`derivative()` walks the tree like `evaluate()` and `to_infix()`,
one case per node type,
but produces another `Expr` instead of a number or a string.
A `Num` is constant, so its derivative is always `0`.

**Combine the children's derivatives.**
Each of the product rule's two terms multiplies one factor's derivative by the other factor as written,
so the original, undifferentiated subtrees stay in the result.

Reaching `2 * x` takes a further rule, "combine like terms,"
that this `simplify()` does not implement.

Exercise 3 adds `Neg` and `Div` to `Expr`.
Differentiating a `Div` needs the quotient rule,
which produces a squared denominator beyond what `simplify()`'s current rules handle,
so this solution leaves differentiating a `Div` for a further exercise.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. Declining with `NotImplemented`

> At runtime, `"a" + x` silently builds `Add(Num("a"), x)`,
> an ill-typed tree the type checker rejects in source it can see.
> Using the idiom from [*Multiple Dispatching*](../../Chapters/32_Patterns--Multiple_Dispatching.md#operators-dispatch-twice),
> rewrite all four operator methods to return `NotImplemented` for an operand they cannot use.
> Confirm that `"a" + x` and `x + "a"` both now raise a `TypeError`.

<details>
<summary>Where to look</summary>

[Operators That Build Nodes](../../Chapters/34_Patterns--Composite_and_Interpreter.md#operators-that-build-nodes)
explains the four operator methods that `expr.py` defines.
The *Multiple Dispatching* chapter's [Operators Dispatch Twice](../../Chapters/32_Patterns--Multiple_Dispatching.md#operators-dispatch-twice)
shows the idiom.
In each method, test the operand with `isinstance()` and return `NotImplemented` when it is neither an `Expr` nor an `int`.
Python then tries the reflected method on the other operand,
and when that declines too, the expression raises a `TypeError`.

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
<summary>Done when</summary>

`"a" + x` raises a `TypeError` reading `can only concatenate str (not "Var") to str`,
and `x + "a"` raises one reading `unsupported operand type(s) for +: 'Var' and 'str'`.
`2 * x + 1` still builds an `Add` whose `right` is `Num(value=1)`.

<details>
<summary>Solution</summary>

If you guard the reflected methods and leave `__add__()` and `__mul__()` as the chapter writes them,
`"a" + x` raises its `TypeError`, but `x + "a"` succeeds.
`wrap()` passes the string through,
so `x + "a"` returns `Add(left=Var(name='x'), right='a')`,
and the listing's second `expected()` block exits normally and stays silent.
The solution guards all four methods,
since an expression that starts with `x` reaches a forward method first.

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

Before the change, `"a" + x` produces `Add(Num("a"), Var("x"))`.
Python tries `Var.__radd__("a")` first,
because `str` handles `+` as sequence concatenation, which Python tries last.
The old `__radd__()` accepts anything and wraps whatever arrives in a `Num`,
so this `Num` holds a string.
Every walker mishandles that `Num`.

**Hand the decision back to Python.**
Returning `NotImplemented` tells Python to try the next method.
Python then falls back to `str` concatenation, which raises `TypeError`.

The message comes from `str`, which is the right source.
The left operand is what the caller wrote first,
and no method in this expression language accepts a `str`.

**Guard the forward direction too.**
The forward methods need the same guard for the same reason.
The old `__add__()` passes the raw string through `wrap()`,
so `x + "a"` builds the ill-typed tree `Add(Var('x'), 'a')` from the other direction.

The two messages differ because each comes from a different source.
`str` reports `"a" + x`, and Python's own fallback reports `x + "a"`,
once both operands have declined.

**Declare the node each method builds.**
Each method declares the type it really returns, `Add` or `Mul`,
although it can also return `NotImplemented`.
[*Multiple Dispatching*](../../Chapters/32_Patterns--Multiple_Dispatching.md#operators-dispatch-twice)
explains the convention: typeshed gives the sentinel a type inheriting `Any`,
so returning it satisfies any declared return type.
The declaration also lets `(2 * x + 1).right` resolve for a caller.

`NotImplemented` adds a check at runtime, not at type-checking time.
The type checker rejects `"a" + x` and `x + "a"` in the source it checks,
so both lines carry a `# type: ignore` to keep `exercise_6.py` in the build.
The runtime check matters when a program builds the expression from data it reads while running,
after the type checker has finished.
An interpreter exists to handle that case.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[A Template Is a Tree](../../Chapters/34_Patterns--Composite_and_Interpreter.md#a-template-is-a-tree)
shows that a `Template` separates literal strings from `Interpolation` objects.
Loop over the template, copy each string piece unchanged,
and pass each interpolation's value through `html.escape()`.
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
<summary>Done when</summary>

with `comment = "<script>steal()</script> & run"`,
`to_html(t"<p>{comment}</p>")` prints `<p>&lt;script&gt;steal()&lt;/script&gt; &amp; run</p>`.
The author's `<p>` tags come through as typed, and every `<`, `>`,
and `&` from the value becomes an entity.

<details>
<summary>Solution</summary>

If you build the page with an f-string and pass the finished string to `escape()`,
the `<script>` tag comes out escaped, but so do the author's `<p>` tags,
and the output begins `&lt;p&gt;`.
In a finished string,
the characters the author typed and the characters the value supplied look the same.
The exercise asks for the literal pieces as written,
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

**Add an operation beside the others.**
`to_html()` is the third operation over `Template`.
Adding it leaves `to_query()` and `to_shape()` as they were,
in the same way that each walker the chapter adds over `Expr` leaves the earlier walkers as they were.
`to_html()` runs the same `for piece in template` loop as those two walkers with a different body,
because the structure separates the literal pieces from the interpolations.

**Escape the interpolated values.**
`html.escape()` does the replacing,
so the exercise comes down to where `to_html()` calls it:
on the interpolated values.
`html.escape()` replaces the two quote characters, `"` and `'`, as well,
because its `quote` argument defaults to `True`.
The `<p>` and `</p>` the author typed pass through as written,
so the browser sees the author's paragraph with the comment's markup escaped inside it.

The f-string produces a `<script>` tag that a browser runs.
A later function that escapes the tag escapes the paragraph markup with it,
because by the time a function receives that string,
the tag and the paragraph markup are the same kind of text.
The template version keeps the distinction,
so escaping is a decision the renderer can still make.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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
> Name its drawbacks.

<details>
<summary>Where to look</summary>

[Evaluation Is a Tree Walk](../../Chapters/34_Patterns--Composite_and_Interpreter.md#evaluation-is-a-tree-walk)
shows `evaluate()` recursing once per node,
so tree depth becomes call-stack depth.
For `evaluate_iterative()`,
keep your own list as a stack of nodes and a second stack of values,
and process each node after its children.
For the `sys.setrecursionlimit()` question,
consider what the interpreter's own stack must hold at that depth.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
from collections.abc import Mapping
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

def evaluate(e: Expr, env: Mapping[str, int]) -> int:
    ...

class Op(Enum):
    ADD = "+"
    MUL = "*"

def evaluate_iterative(e: Expr,
                       env: Mapping[str, int]) -> int:
    ...
```

<details>
<summary>Done when</summary>

`evaluate()` on a `+` fold of `Num(0)` through `Num(2000)` raises a `RecursionError`,
while your `evaluate_iterative()` returns `2001000` for the same tree and `7` for `2 * x + 1` with `x` at `3`.
You can name at least two drawbacks of raising the limit instead.

<details>
<summary>Solution</summary>

If you push an `Add` or `Mul` node's two children with no marker behind them,
`evaluate_iterative(2 * x + 1, {"x": 3})` returns `1` instead of `7`.
`values` collects the three leaves,
and the function returns the last one it reached.
The solution pushes an `Op` beneath each pair of children,
so the combine runs once both values are on `values`.

```python
# exercise_8.py
from collections.abc import Mapping
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

def evaluate(e: Expr, env: Mapping[str, int]) -> int:
    match e:
        case Num(value):
            return value
        case Var(name):
            return env[name]
        case Add(left, right):
            return (evaluate(left, env)
                    + evaluate(right, env))
        case Mul(left, right):
            return (evaluate(left, env)
                    * evaluate(right, env))
        case _:
            assert_never(e)

# A pending combine, behind the children it consumes:
class Op(Enum):
    ADD = "+"
    MUL = "*"

def evaluate_iterative(e: Expr,
                       env: Mapping[str, int]) -> int:
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

expect(RecursionError, evaluate, deep, {})
#: [RecursionError] maximum recursion depth exceeded
print(evaluate_iterative(deep, {}))
#: 2001000

x = Var("x")
small = 2 * x + 1
print(evaluate(small, {"x": 3}),
      evaluate_iterative(small, {"x": 3}))
#: 7 7
```

The `deep` expression is ordinary apart from its shape.
Its tree is 2000 `Add` nodes deep.
`evaluate()` needs one stack frame per level against a limit of 1000,
so it fails before reaching the bottom.

**Defer the combine behind its children.**
The recursive `evaluate()` combines two values when its two calls return.
A stack version must arrange that moment in its own loop.
A loop that pushes children and pops them gives a pre-order walk.
That walk reaches each `Add` before its children,
but an `Add` combines its children's values after the children have produced them.
The solution stacks the pending operation behind its children.
`work += [Op.ADD, right, left]` puts `Op.ADD` deepest, so it comes off last,
by which point the two values it needs are on `values`.

**Preserve operand order.**
Pushing `right` before `left` makes `left` pop first.
That order matters for the subtraction and division a fuller language adds.

**Keep the match exhaustive.**
`Op` is an enum rather than a string so the `match` stays exhaustive.
`work` holds `Expr | Op`, and every member of both types has its own case,
so `assert_never()` type-checks.
A marker typed `str` leaves `case _` reachable.
The type checker then rejects the `assert_never()` call.

`sys.setrecursionlimit()` avoids the error for `evaluate()`,
but it has three drawbacks.
First, it lifts the limit for Python calls alone.
A call from one Python function to another leaves the C stack at the same depth,
so with the limit raised to `10**9`, `evaluate()` walks a million-level tree.
Anything that recurses through C stops.
`repr()` or `hash()` on that same tree raises a `RecursionError` that reports a stack overflow,
whatever the limit says.
Second, each pending level holds a stack frame, so memory grows with depth.
Third, the limit is global,
so a library that raises it changes the behavior of every other module in the process.
The iterative walk keeps its pending work in one list and leaves every global setting as it was.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 9. Reopening the set of node types

> A plugin package needs to add its own node types to `filesystem.py` without editing your code.
> Sketch what breaks, then write the version of `disk_usage()` that supports the plugin's node types.
> For a file system, would you use a `match` over a union or a method on a base class?
> Which would you use for the expression language in `expr.py`?

<details>
<summary>Where to look</summary>

[A *Composite* of Data Classes](../../Chapters/34_Patterns--Composite_and_Interpreter.md#a-composite-of-data-classes)
closes `Node` as a union, so every operation is a `match` in your module.
To open the set, move `disk_usage()` onto an abstract base class as an `@abstractmethod`,
and let each entry type implement it.
When you choose between the designs,
ask who owns the list of node types and who writes new operations.

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
<summary>Done when</summary>

a node type written below your existing classes, with none of them edited,
adds its share to `disk_usage()` for a directory that holds it,
and `uv run ty check` passes.
For each of `filesystem.py` and `expr.py`,
you can say who owns the list of node types and how that decides your choice.

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
        return sum(entry.disk_usage()
                   for entry in self.entries)

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

The closed version breaks at the union.
`type Node = File | Directory` lives in your source,
so extending it means editing your file.
The type checker does warn the plugin author.
When a plugin passes a `Symlink` to `disk_usage()` or places one in a `Directory`'s entries,
`ty` reports `invalid-argument-type`.
The fix the warning calls for belongs in your file,
because the union it needs to extend is yours.
At runtime, a `Symlink` falls through every case to `assert_never()`,
which raises an `AssertionError`.
The plugin's alternatives are to vendor a patched copy of your module or to persuade you to add the case.
The open design lets a plugin define its node types in its own package.

**Move the operation onto the classes.**
The open design undoes [A *Composite* of Data Classes](../../Chapters/34_Patterns--Composite_and_Interpreter.md#a-composite-of-data-classes),
which moves each operation off the classes and into a `match`.
Adding `Symlink` now leaves existing code as it was,
while adding a new operation takes a method in every class,
including the classes a plugin owns.

**Enforce the contract on plugins.**
Because `disk_usage()` is an `@abstractmethod`,
Python raises a `TypeError` when you instantiate a subclass that leaves it abstract.

For a file system, use the open design.
Which node types exist is a fact about the operating system and about whatever the next version adds,
not a decision your code gets to make.
Third-party node types are the normal case.

For `expr.py`, use the closed one.
The four node types are the grammar,
so a plugin adding a fifth does not extend the language but defines a different one.
Every walker is then silently wrong rather than helpfully extended.
The `assert_never()` that reads as an obstacle in the file system reads as the point here.
When the grammar does grow a `Neg`,
the type checker reports each walker that needs a case for it.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
