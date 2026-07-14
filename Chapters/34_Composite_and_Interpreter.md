# Composite and Interpreter

The *Composite* pattern arranges objects in a tree,
so you can treat a single object and a group of objects uniformly.
The *Interpreter* pattern represents sentences in a small language as trees,
then evaluates them.
*GoF Design Patterns* presents them as separate patterns,
but the second is the first with meaning attached.
In Python both reduce to one technique:
a union of frozen data classes for the nodes,
and recursive functions that `match` on them.
This chapter builds each pattern with [exhaustive matching](13_Pattern_Matching.md#exhaustive-matching).

![The same shape, two applications: a filesystem tree where a Directory holds File or Directory entries, and an expression tree where Add and Mul hold other expressions](_images/composite_tree)

## The Classic Composite

A file system is the canonical composite.
A directory holds entries, and each entry is a file or another directory.
The payoff is uniformity.

The traditional version puts the operation in a class hierarchy:

```python
# filesystem_classic.py
from abc import ABC, abstractmethod
from typing import override

class Node(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def size(self) -> int: ...

class File(Node):
    def __init__(self, name: str, byte_count: int) -> None:
        super().__init__(name)
        self.byte_count = byte_count

    @override
    def size(self) -> int:
        return self.byte_count

class Directory(Node):
    def __init__(self, name: str, *entries: Node) -> None:
        super().__init__(name)
        self.entries = entries

    @override
    def size(self) -> int:
        return sum(e.size() for e in self.entries)

src = Directory(
    "src", File("main.py", 400), File("util.py", 250))
root = Directory(
    "root", File("readme.md", 90), src, File("data.csv", 1200))
print(root.size(), src.size(), File("lone.txt", 10).size())
#: 1940 650 10
```

`Directory.size()` calls `size()` on each entry without knowing whether the entry is a `File` or another `Directory`.
The same call works on the whole tree, on a subtree, and on a single file.

Adding operations exposes the weakness.
Counting files, finding an entry by name,
and printing the tree each require a new method in every class.
[Visitor](33_Visitor.md) exists to solve this problem.

## A Composite of Data Classes

In Python, you can define the node types as frozen data classes.
Name the closed set of alternatives with a union.
Write each operation as a recursive function that matches on the union:

```python
# filesystem.py
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

def disk_usage(entry: Node) -> int:
    match entry:
        case File(_, size):
            return size
        case Directory(_, entries):
            return sum(disk_usage(e) for e in entries)
        case _:
            assert_never(entry)

def walk(entry: Node, prefix: str = "") -> Iterator[str]:
    match entry:
        case File(name, _):
            yield prefix + name
        case Directory(name, entries):
            for e in entries:
                yield from walk(e, f"{prefix}{name}/")
        case _:
            assert_never(entry)

if __name__ == "__main__":
    src = Directory("src", (
        File("main.py", 400), File("util.py", 250)))
    root = Directory("root", (
        File("readme.md", 90), src, File("data.csv", 1200)))
    print(disk_usage(root), disk_usage(src),
          disk_usage(File("lone.txt", 10)))
    for path in walk(root):
        print(path)
#: 1940 650 10
#: root/readme.md
#: root/src/main.py
#: root/src/util.py
#: root/data.csv
```

`disk_usage()` accepts a lone `File`, a subtree, or the whole tree.
What changed is where operations live.
`disk_usage()` and `walk()` are ordinary functions outside the node classes,
so a new operation is a new function, and the nodes never change.
This is the same trade explored in [Rethinking Objects](20_Rethinking_Objects.md#polymorphism-without-inheritance):
a closed set of types, with operations gathered in one place each.
The `assert_never()` in each `case _` makes that closed set pay off.
Add a `Symlink` class to the `Node` union.
Every function whose `case _` calls `assert_never()` now fails type checking,
because `entry` could be a `Symlink` that no case handles.
The checker flags each function that still needs a new case,
so none can be forgotten.

`walk()` is a generator, so a composite is also iterable.
The `yield from` flattens the recursion into a single stream of paths,
and any consumer of that stream stays decoupled from the tree structure
(see [Iterators](23_Iterators.md#delegating-with-yield-from)).

The `entries` field is a tuple of `Node`, so the whole tree is immutable.
The demo builds `src` first, then places it inside `root`.
Nothing can modify `src` afterward, so sharing subtrees is safe
(see [Functional Foundations](40_Functional_Foundations.md#immutability)).

```python
# test_filesystem.py
from typing import Final
import pytest
from filesystem import Directory, File, Node, disk_usage, walk

SUB: Final[Directory] = Directory(
    "sub", (File("b", 2), File("c", 3)))
TREE: Final[Directory] = Directory(
    "top", (File("a", 1), SUB))

@pytest.mark.parametrize("entry, expected", [
    (TREE, 6),
    (SUB, 5),
    (File("solo", 7), 7),
])
def test_disk_usage_is_uniform(entry: Node, expected: int) -> None:
    assert disk_usage(entry) == expected

def test_walk_yields_full_paths() -> None:
    assert list(walk(TREE)) == [
        "top/a", "top/sub/b", "top/sub/c"]

def test_empty_directory() -> None:
    assert disk_usage(Directory("empty", ())) == 0
    assert list(walk(Directory("empty", ()))) == []
```

The classic version is still useful when the set of node types is open.
If plugins or other packages must add new kinds of entries,
a method on a base class lets them do that without touching your code,
while a central `match` would need editing.
The guidance from [Pattern Matching](13_Pattern_Matching.md#when-not-to-match)
applies directly.
Match over a closed set, use polymorphism for an open one.

## Interpreter

A tree whose shape follows a grammar is an *abstract syntax tree* (AST).
*Interpreter* is Composite applied to language.
Represent each construct as a node type, and evaluation becomes a tree walk.

In most languages the pattern has a reputation for heaviness,
because you must write a class per construct and a parser to build the trees.
Python removes both costs.
Data classes make the node declarations nearly free,
and operator overloading lets Python's own parser build the trees.
Here is the complete grammar for a small arithmetic language:

```python
# expr.py
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
```

The four node classes are the grammar.
An expression is a number, a variable, a sum, or a product.
`Add` and `Mul` hold expressions themselves, which is what makes it a composite.

The `Operators` base class is the clever part.
Every node inherits `__add__()` and `__mul__()`,
and those methods do not compute anything.
They build nodes.
Writing `x + 1` on two `Expr` values produces an `Add`,
so ordinary Python arithmetic notation constructs the AST.
The reflected forms `__radd__()` and `__rmul__()` handle a plain integer on the left,
and `wrap()` promotes integers to `Num` nodes,
so `2 * x + 1` is a valid sentence in the little language.
Python has already parsed it, honoring precedence,
before the interpreter ever runs.

This technique is used in SymPy expressions,
Pandas and Polars column arithmetic, and SQLAlchemy filter conditions.
Overloaded operators build an expression tree,
and a library interprets that tree later, symbolically, over a whole column,
or as SQL.

## Evaluation Is a Tree Walk

Evaluation is a recursive `match` function.
Variables need values, supplied here as keyword arguments:

```python
# evaluate.py
from typing import assert_never
from expr import Add, Expr, Mul, Num, Var

def evaluate(e: Expr, **env: int) -> int:
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

if __name__ == "__main__":
    x = Var("x")
    expr = 2 * x + 1
    by_hand = Add(Mul(Num(2), x), Num(1))
    print(expr == by_hand)
    print(evaluate(expr, x=3), evaluate(expr, x=10))
#: True
#: 7 21
```

Data classes generate `__eq__()`, so two trees compare by value,
and the demo confirms that the operators build the tree you would assemble by hand.
The second `print()` line evaluates that same `expr` twice,
once with `x=3` and once with `x=10`.
Building `2 * x + 1` did not compute a number.
It built a tree, so `expr` is a value you can hand to `evaluate()` under different variable bindings,
as many times as you like.
An unbound variable raises `KeyError`, naming the variable.

```python
# test_evaluate.py
import pytest
from evaluate import evaluate
from expr import Add, Mul, Num, Var

def test_literal_and_variable() -> None:
    assert evaluate(Num(42)) == 42
    assert evaluate(Var("x"), x=3) == 3

def test_operators_build_the_tree() -> None:
    x = Var("x")
    assert 2 * x + 1 == Add(Mul(Num(2), x), Num(1))
    assert 1 + x == Add(Num(1), x)
    assert x * x == Mul(x, x)

def test_one_tree_many_environments() -> None:
    area = Var("w") * Var("h")
    assert evaluate(area, w=2, h=3) == 6
    assert evaluate(area, w=10, h=10) == 100

def test_unbound_variable_raises() -> None:
    with pytest.raises(KeyError):
        evaluate(Var("y"), x=1)
```

## New Operations, Same Tree

Evaluation has no privileged status.
Rendering the tree as an infix string is another function, in another file,
and the node classes never hear about it:

```python
# infix.py
from typing import assert_never
from expr import Add, Expr, Mul, Num, Var

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

if __name__ == "__main__":
    x = Var("x")
    print(to_infix(2 * x + 1))
    print(to_infix((x + 1) * (x + 2)))
#: ((2 * x) + 1)
#: ((x + 1) * (x + 2))
```

This is the ability [Visitor](33_Visitor.md) fights to provide:
new operations over a fixed hierarchy, defined outside it.
The `match` version needs no `accept()` hook and no visitor classes,
and unlike `singledispatch` it looks inside the nodes,
binding their fields in the patterns.

## Simplification Rewrites the Tree

An interpreter need not produce a number or a string.
It can produce another tree.
`simplify()` applies algebraic identities.
Adding zero and multiplying by one vanish, multiplying by zero collapses,
and constant subtrees fold into a single `Num`.
Each rule is a nested pattern over a pair of already-simplified children:

```python
# simplify.py
from typing import assert_never
from expr import Add, Expr, Mul, Num, Var

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
        case _:
            assert_never(e)

if __name__ == "__main__":
    from infix import to_infix
    x = Var("x")
    messy = 1 * x + 0 * Var("y") + (Num(2) + 3) * x
    print(to_infix(messy))
    print(to_infix(simplify(messy)))
#: (((1 * x) + (0 * y)) + ((2 + 3) * x))
#: (x + (5 * x))
```

The patterns read like the algebra they implement.
`(Num(0), other) | (other, Num(0))` says "zero on either side,
keep the other side," with the alternatives binding the same name.
`(Num(a), Num(b))` captures two constants for folding.
Because every node is frozen, `simplify()` never edits the input.
It returns a new tree that shares unchanged subtrees with the original.

```python
# test_simplify.py
from typing import Final
import pytest
from expr import Add, Expr, Mul, Num, Var
from simplify import simplify

X: Final[Var] = Var("x")

@pytest.mark.parametrize("expr, expected", [
    (X + 0, X),
    (0 + X, X),
    (1 * X, X),
    (X * 1, X),
])
def test_identity_elements_vanish(
    expr: Expr, expected: Expr,
) -> None:
    assert simplify(expr) == expected

def test_zero_absorbs_multiplication() -> None:
    assert simplify(Var("x") * 0) == Num(0)
    assert simplify(0 * Var("x")) == Num(0)

def test_constant_folding() -> None:
    assert simplify(Num(2) + 3) == Num(5)
    assert simplify(Num(2) * 3 + 4) == Num(10)

def test_rewriting_reaches_every_level() -> None:
    x = Var("x")
    assert simplify((x + 0) * (1 * x)) == Mul(x, x)

def test_already_simple_is_unchanged() -> None:
    x = Var("x")
    assert simplify(2 * x + 1) == Add(Mul(Num(2), x), Num(1))
```

The full shape of the two patterns is now visible.
Composite is the data: a union of node types, some holding others.
Interpreter is the behavior: recursive functions that give the tree meaning.
Python compresses the pair into frozen data classes, a union,
operator methods that build nodes, and `match` functions that walk them.

## Exercises

1.  Add `find(entry, name)` to `filesystem.py`:
    a generator yielding the path of every entry whose name matches.
    A directory can match, and matching should continue into it.
2.  Add a `Symlink` node to the `Node` union in `filesystem.py`,
    holding a name and a target path,
    and let the type checker show you every operation that must change.
    Decide what `disk_usage()` and `walk()` should do with a link.
3.  Add `Neg` (negation) and `Div` (division) nodes to `expr.py`,
    along with `__neg__()` and `__truediv__()` operator methods.
    Update `evaluate()`, `to_infix()`, and `simplify()`.
    What should `simplify()` do with division by `Num(0)`?
4.  `to_infix()` parenthesizes every operation.
    Rewrite it to emit only the parentheses that precedence requires,
    so `2 * x + 1` renders as `2 * x + 1` but `(x + 1) * (x + 2)` keeps its parentheses.
5.  Write `derivative(e, name)`:
    a function that returns the symbolic derivative of an expression with respect to a variable,
    using the sum rule and the product rule.
    Run its results through `simplify()` and compare.
