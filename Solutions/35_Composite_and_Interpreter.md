# Composite and Interpreter: Solutions

## 1. `find(entry, name)`

```python
# exercise_1.py
from collections.abc import Iterator
from dataclasses import dataclass
from typing import assert_never

@dataclass(frozen=True)
class File:
    name: str
    size: int

@dataclass(frozen=True)
class Directory:
    name: str
    entries: tuple[Node, ...]

type Node = File | Directory

def find(entry: Node, name: str, prefix: str = "") -> Iterator[str]:
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

src = Directory("src", (File("main.py", 400), File("util.py", 250)))
root = Directory("root", (
    File("readme.md", 90), src, File("data.csv", 1200),
    Directory("src", ())))

print(list(find(root, "main.py")))
#: ['root/src/main.py']
print(list(find(root, "src")))
#: ['root/src', 'root/src']
```

`find()` follows `walk()`'s shape exactly: a `match` with one case per
`Node` type, recursing with `yield from` into each `Directory`'s
entries. The difference is that a `Directory` can itself match `name`
(unlike `walk()`, which only ever yields file paths), and matching
continues *into* a matched directory rather than stopping there, so a
directory named `"src"` and a file or subdirectory somewhere beneath
it named `"src"` can both appear in the results, as the second call
above shows for two separately-named `"src"` directories in the tree.

## 2. A `Symlink` node

```python
# exercise_2.py
from collections.abc import Iterator
from dataclasses import dataclass
from typing import assert_never

@dataclass(frozen=True)
class File:
    name: str
    size: int

@dataclass(frozen=True)
class Directory:
    name: str
    entries: tuple[Node, ...]

@dataclass(frozen=True)
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
            return 0  # A link contributes no size of its own
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

Adding `Symlink` to the union makes every `match` whose `case _` calls
`assert_never()` fail type checking, exactly as the chapter predicts:
`ty` reports that `entry` (or `e`) could be a `Symlink` that no case
handles, in both `disk_usage()` and `walk()`, until a case is added
for it as shown here. Deciding what a link should do is a judgment
call, not something the type checker picks for you: `disk_usage()`
counts a link as free, since the bytes it references already get
counted wherever the real file lives; adding the target's size again
would double-count it. `walk()` reports the link as its own entry,
`name -> target`, rather than following it into the target's subtree,
since following it could loop forever if a link ever pointed back at
one of its own ancestors.

## 3. `Neg` and `Div`

```python
# exercise_3.py
from __future__ import annotations
from dataclasses import dataclass

class Operators:
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

@dataclass(frozen=True)
class Num(Operators):
    value: int

@dataclass(frozen=True)
class Var(Operators):
    name: str

@dataclass(frozen=True)
class Add(Operators):
    left: Expr
    right: Expr

@dataclass(frozen=True)
class Mul(Operators):
    left: Expr
    right: Expr

@dataclass(frozen=True)
class Neg(Operators):
    operand: Expr

@dataclass(frozen=True)
class Div(Operators):
    left: Expr
    right: Expr

type Expr = Num | Var | Add | Mul | Neg | Div

def wrap(value: Expr | int) -> Expr:
    return Num(value) if isinstance(value, int) else value

def evaluate(e: Expr, **env: int) -> float:
    match e:
        case Num(value):
            return value
        case Var(name):
            return env[name]
        case Add(left, right):
            return evaluate(left, **env) + evaluate(right, **env)
        case Mul(left, right):
            return evaluate(left, **env) * evaluate(right, **env)
        case Neg(operand):
            return -evaluate(operand, **env)
        case Div(left, right):
            return evaluate(left, **env) / evaluate(right, **env)

x = Var("x")
expr = (2 * x + 1) / -x
print(evaluate(expr, x=3))
#: -2.3333333333333335
```

`to_infix()` needs a case for each too (`f"-{to_infix(operand)}"` and
`f"({to_infix(left)} / {to_infix(right)})"`). `simplify()` is the
interesting one: for `Neg`, a constant operand folds
(`Neg(Num(a))` → `Num(-a)`), and a double negation cancels
(`Neg(Neg(inner))` → `inner`). For `Div`, division by `Num(0)` should
*not* fold to anything, not even an error. `simplify()` is a static
rewrite that runs before any variable is bound to a real number; it
cannot know whether a symbolic expression dividing by zero will ever
actually execute with that zero denominator; the division might sit
inside a branch that never runs, or the "zero" might really be a
variable that later never happens to equal zero. The honest move is
to leave `Div(lhs, Num(0))` exactly as it is and let the eventual
`evaluate()` call raise `ZeroDivisionError` if and when it actually
happens, the same way Python itself defers that error to runtime
rather than refusing to parse `1 / x` at all.

## 4. Precedence-aware `to_infix()`

```python
# exercise_4.py
from __future__ import annotations
from dataclasses import dataclass

class Operators:
    def __add__(self: Expr, other: Expr | int) -> Add:
        return Add(self, wrap(other))

    def __radd__(self: Expr, other: int) -> Add:
        return Add(Num(other), self)

    def __mul__(self: Expr, other: Expr | int) -> Mul:
        return Mul(self, wrap(other))

    def __rmul__(self: Expr, other: int) -> Mul:
        return Mul(Num(other), self)

@dataclass(frozen=True)
class Num(Operators):
    value: int

@dataclass(frozen=True)
class Var(Operators):
    name: str

@dataclass(frozen=True)
class Add(Operators):
    left: Expr
    right: Expr

@dataclass(frozen=True)
class Mul(Operators):
    left: Expr
    right: Expr

type Expr = Num | Var | Add | Mul

def wrap(value: Expr | int) -> Expr:
    return Num(value) if isinstance(value, int) else value

PRECEDENCE = {Add: 1, Mul: 2, Num: 3, Var: 3}

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
    my_prec = PRECEDENCE[type(e)]
    return f"({s})" if my_prec < parent_prec else s

x = Var("x")
print(to_infix(2 * x + 1))
#: 2 * x + 1
print(to_infix((x + 1) * (x + 2)))
#: (x + 1) * (x + 2)
```

Each recursive call passes down the precedence its *parent* requires.
A child only gets parenthesized when its own operator binds more
loosely than what the parent needs, exactly `Mul`'s children needing
parens around a lower-precedence `Add`, but `Add`'s children never
needing parens around another `Add`. Passing `prec + 1` (rather than
`prec`) for the right operand is a simple, always-safe rule: it can
occasionally print one redundant pair of parentheses around a
right-hand child at the *same* precedence as its parent (`x + (x +
1)` instead of the fully terse `x + x + 1`), but it never omits a pair
that changes the expression's meaning, which is the property that
actually matters.

## 5. `derivative(e, name)`

```python
# exercise_5.py
from __future__ import annotations
from dataclasses import dataclass
from typing import assert_never

class Operators:
    def __add__(self: Expr, other: Expr | int) -> Add:
        return Add(self, wrap(other))

    def __radd__(self: Expr, other: int) -> Add:
        return Add(Num(other), self)

    def __mul__(self: Expr, other: Expr | int) -> Mul:
        return Mul(self, wrap(other))

    def __rmul__(self: Expr, other: int) -> Mul:
        return Mul(Num(other), self)

@dataclass(frozen=True)
class Num(Operators):
    value: int

@dataclass(frozen=True)
class Var(Operators):
    name: str

@dataclass(frozen=True)
class Add(Operators):
    left: Expr
    right: Expr

@dataclass(frozen=True)
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
            return f"{to_infix(left)} + {to_infix(right)}"
        case Mul(left, right):
            return f"{to_infix(left)} * {to_infix(right)}"

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
                    return Mul(lhs, rhs)

def derivative(e: Expr, name: str) -> Expr:
    match e:
        case Num(_):
            return Num(0)
        case Var(n):
            return Num(1) if n == name else Num(0)
        case Add(left, right):  # Sum rule: (f + g)' = f' + g'
            return Add(derivative(left, name),
                       derivative(right, name))
        case Mul(left, right):  # Product rule: (fg)' = f'g + fg'
            return Add(Mul(derivative(left, name), right),
                       Mul(left, derivative(right, name)))
        case _:
            assert_never(e)

x = Var("x")
d = derivative(x * x, "x")
print(to_infix(d))
#: 1 * x + x * 1
print(to_infix(simplify(d)))
#: x + x
```

`derivative()` walks the tree exactly like `evaluate()` and
`to_infix()`, one case per node type, but produces another `Expr`
instead of a number or a string. A `Num` never changes, so its
derivative is always `0`. `Var(n)` is `1` with respect to itself and
`0` with respect to every other variable. `Add`'s case is the sum
rule; `Mul`'s is the product rule, and it must keep both the
derivative *and* the original, undifferentiated subtree on each side,
because the product rule genuinely needs both. Running the raw result
through `simplify()` turns `1 * x + x * 1` into the much more readable
`x + x` (it would take a further simplification rule, "combine like
terms," to reach `2 * x`, which this `simplify()` does not implement).
A full `Expr` that also includes `Neg` and `Div` (exercise 3's
additions) would need a quotient rule for `Div` too, which needs a
squared denominator `simplify()`'s current rules do not yet know how
to render tidily; left for a further exercise, the same way exercise
3 leaves `Div`'s own derivative case unimplemented.
