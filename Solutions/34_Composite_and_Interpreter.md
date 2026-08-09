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
double-counts it. `walk()` reports the link as its own entry,
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
`x + x` (it takes a further simplification rule, "combine like
terms," to reach `2 * x`, which this `simplify()` does not implement).
A full `Expr` that also includes `Neg` and `Div` (exercise 3's
additions) needs a quotient rule for `Div` too, which needs a
squared denominator `simplify()`'s current rules do not yet know how
to render tidily; left for a further exercise, the same way exercise
3 leaves `Div`'s own derivative case unimplemented.

## 6. Declining with `NotImplemented`

```python
# exercise_6.py
from dataclasses import dataclass

class Operators:
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

x = Var("x")
print(type(2 * x + 1).__name__, (2 * x + 1).right)
#: Add Num(value=1)
try:
    "a" + x  # type: ignore
except TypeError as e:
    print(type(e).__name__, e)
#: TypeError can only concatenate str (not "Var") to str
```

Before the change, `"a" + x` produced `Add(Num("a"), Var("x"))`: a
`Num` whose `value` is a string, which every walker then mishandles.
`str.__add__` declines a `Var`, Python falls back to
`Var.__radd__("a")`, and the old version accepted anything, wrapping
the string in a `Num` without looking at it.

Returning `NotImplemented` puts the decision back where it belongs.
`__radd__()` now answers only for an `int`, so both sides decline and
Python raises the `TypeError` it would have raised for any other
mismatched pair. The message comes from `str`, which is right: the
left operand is what the caller wrote first, and nothing in this
expression language ever claimed to extend it.

Each method declares the type it really returns, `Add` or `Mul`,
even though it can also return `NotImplemented`. That is the
convention [Multiple Dispatching](../Chapters/32_Multiple_Dispatching.md#operators-dispatch-twice)
explains: typeshed gives the sentinel a type inheriting `Any`, so
returning it satisfies any declared return type, and the declaration
is what lets `(2 * x + 1).right` resolve for a caller.

Note what this does not fix. `ty` already rejected `"a" + x` in source
it can see, which is why the line above carries a `# type: ignore` to
keep this listing in the build; the runtime hole was the gap between
the two. Closing it matters when the expression is built from data the
checker never sees, which is the case an interpreter is written for.

## 7. A third walker: `to_html()`

```python
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

`to_html()` is the third operation over `Template` and it changes
nothing about the other two, which is the property the chapter keeps
demonstrating on `Expr`. The whole walker is the same loop with a
different body, because the structure already separates the two kinds
of piece.

`html.escape()` does the character replacement, so the exercise's
real content is *where* it gets applied: to the interpolated values.
The `<p>` and `</p>` the author typed pass through untouched, which
is what makes the output valid HTML rather than a document with its
own tags escaped.

The f-string on the last line is the comparison. It produces a
`<script>` tag that a browser will run, and it does so with no way to
intervene, because by the time any function receives that string the
tag and the paragraph markup are the same kind of text. The template
version never loses the distinction, so escaping is a decision the
renderer can still make.

## 8. An iterative walk over a deep tree

```python
# exercise_8.py
from dataclasses import dataclass
from enum import Enum
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

def evaluate(e: Expr, /, **env: int) -> int:
    match e:
        case Num(value):
            return value
        case Var(name):
            return env[name]
        case Add(left, right):
            return evaluate(left, **env) + evaluate(right, **env)
        case Mul(left, right):
            return evaluate(left, **env) * evaluate(right, **env)
        case _:
            assert_never(e)

# A pending combine, stacked behind the children it consumes:
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
                right_value, left_value = values.pop(), values.pop()
                values.append(left_value + right_value)
            case Op.MUL:
                right_value, left_value = values.pop(), values.pop()
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

try:
    evaluate(deep)
except RecursionError as e:
    print(type(e).__name__)
#: RecursionError
print(evaluate_iterative(deep))
#: 2001000

x = Var("x")
small = 2 * x + 1
print(evaluate(small, x=3), evaluate_iterative(small, x=3))
#: 7 7
```

The tree is 2000 `Add` nodes deep, and `evaluate()` needs one frame
per level against a limit of 1000, so it fails before reaching the
bottom. Nothing about the expression is unusual; only its shape is.

The stack version cannot be a straight translation, and this is where
the exercise bites. Pushing children and popping them in a loop gives
a pre-order walk that visits every node and computes nothing, because
`Add` needs both of its results *after* the children have produced
them. The fix is to stack the pending operation behind its own
children: `work += [Op.ADD, right, left]` puts `Op.ADD` deepest, so it
comes off last, by which point the two values it needs are on
`values`. Pushing `right` before `left` makes `left` pop first, which
matters for the subtraction and division a fuller language would add.

`Op` is an enum rather than a string so the `match` stays exhaustive:
`work` holds `Expr | Op`, every member of both is a case, and
`assert_never()` still type-checks. A string marker would leave
`case _` reachable and the guarantee gone.

`sys.setrecursionlimit()` is the other escape, and it is a worse one.
The limit is a guard rather than a budget: it exists because each
Python frame consumes C stack, and raising it past what the thread's
stack can hold turns a catchable `RecursionError` into a segmentation
fault with no traceback. It is also a global setting, so a library
that raises it changes the failure mode of code that never asked. The
iterative walk moves the frames onto the heap, where the only limit
is memory.

## 9. Reopening the set of node types

```python
# exercise_9.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override

class Entry(ABC):
    name: str

    @abstractmethod
    def disk_usage(self) -> int: ...

@dataclass(frozen=True)
class File(Entry):
    name: str
    size: int

    @override
    def disk_usage(self) -> int:
        return self.size

@dataclass(frozen=True)
class Directory(Entry):
    name: str
    entries: tuple[Entry, ...]

    @override
    def disk_usage(self) -> int:
        return sum(e.disk_usage() for e in self.entries)

# A plugin package adds a node type, editing nothing above:
@dataclass(frozen=True)
class Symlink(Entry):
    name: str
    target: str

    @override
    def disk_usage(self) -> int:
        return 0

src = Directory("src", (File("main.py", 400), File("util.py", 250)))
root = Directory("root", (
    File("readme.md", 90), src, Symlink("latest", "src")))
print(root.disk_usage())
#: 740
```

What breaks in the closed version is not subtle. `type Node = File |
Directory` lives in your source, so a plugin cannot extend it, and a
`Symlink` passed to `disk_usage()` falls through every case to
`assert_never()`. The checker cannot warn the plugin author, because
from its side the union is complete: the mismatch only exists at the
call. The plugin's alternatives are to vendor a patched copy of your
module or to persuade you to add the case, which is the coupling the
open design removes.

Moving the operation back onto the classes reverses the trade the
chapter spent the first two sections making. Adding `Symlink` now
costs nothing to existing code, and adding a *new operation* costs a
method in every class, including the ones you do not own. The
`@abstractmethod` is what keeps the plugin honest: a subclass with no
`disk_usage()` cannot be instantiated at all.

For a file system, use the open design. The set of things an entry can
be is a fact about the operating system and about whatever the next
version adds, not a decision your code gets to make, and third-party
node types are the normal case.

For `expr.py`, use the closed one. The four node types *are* the
grammar, so a plugin adding a fifth is not extending the language, it
is defining a different one, and every walker would then be silently
wrong rather than helpfully extended. The `assert_never()` that reads
as an obstacle in the file system reads as the point here: when the
grammar does grow a `Neg`, the checker hands you the list of walkers
to update.
