# Composite and Interpreter

The *Composite* pattern arranges objects in a tree,
so you can treat a single object and a group of objects uniformly.
The *Interpreter* pattern represents sentences in a small language as trees,
then evaluates them.
*GoF Design Patterns* presents them as separate patterns,
but *Interpreter* is *Composite* with meaning attached.
In Python both reduce to one technique:
a union of frozen data classes for the nodes,
and recursive functions that `match` on them.
This chapter builds each pattern with [exhaustive matching](13_Techniques--Pattern_Matching.md#exhaustive-matching).

![`disk_usage()` and `walk()` each name both node types, and `Directory` names only the `Node` union](_images/coupling_34)

![One tree shape serves a filesystem and an arithmetic expression](_images/composite_tree)

## The Classic Composite

A file system is the canonical composite.
A directory holds entries, and each entry is a file or another directory.
The point is uniformity: one call serves a file, a directory,
and the whole tree.

The traditional version puts each operation inside the node classes,
under an abstract method on a shared base:

```python
# filesystem_classic.py
from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from typing import override

class Node(ABC):
    name: str

    @abstractmethod
    def disk_usage(self) -> int: ...

    @abstractmethod
    def walk(self, prefix: str = "") -> Iterator[str]: ...

@dataclass(frozen=True)
class File(Node):
    name: str
    size: int

    @override
    def disk_usage(self) -> int:
        return self.size

    @override
    def walk(self, prefix: str = "") -> Iterator[str]:
        yield prefix + self.name

@dataclass(frozen=True)
class Directory(Node):
    name: str
    entries: tuple[Node, ...]

    @override
    def disk_usage(self) -> int:
        return sum(e.disk_usage() for e in self.entries)

    @override
    def walk(self, prefix: str = "") -> Iterator[str]:
        for e in self.entries:
            yield from e.walk(f"{prefix}{self.name}/")

src = Directory("src", (
    File("main.py", 400), File("util.py", 250)))
root = Directory("root", (
    File("readme.md", 90), src, File("data.csv", 1200)))
print(root.disk_usage(), src.disk_usage(),
      File("lone.txt", 10).disk_usage())
#: 1940 650 10
for path in root.walk():
    print(path)
#: root/readme.md
#: root/src/main.py
#: root/src/util.py
#: root/data.csv
```

`Directory.disk_usage()` calls `disk_usage()` on each entry without testing whether the entry is a `File` or another `Directory`.
The demo's first `print()` makes that one call on the whole tree,
on the `src` subtree, and on a lone file.

Adding a node type is one class: a plugin writes it and edits nothing above it.
Adding an *operation* exposes the weakness.
`walk()` needs a method in every class,
and counting files or finding an entry by name each needs another.
[*Visitor*](33_Patterns--Visitor.md) exists to solve this problem.

## A Composite of Data Classes

Now move the operations out of the classes.
The nodes keep their fields, a union names the closed set of alternatives,
and each operation becomes a recursive function that matches on that union.
With no unslotted base class above them,
the nodes become [records](18_Techniques--Performance.md#record):

```python
# filesystem.py
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

`Node` is a *recursive* union.
`Directory` holds a `tuple[Node, ...]`,
so the alias names itself through one of its own members,
and that self-reference makes the tree a tree.
`Directory` mentions `Node` above the [`type` statement](08_Foundations--Static_Types.md#the-type-statement)
that defines it.
That works because Python evaluates annotations and `type` aliases lazily,
the [deferred evaluation](08_Foundations--Static_Types.md#self-and-forward-references).
The alias can therefore sit below the classes it unites,
where it reads as a summary of them rather than as a forward declaration.

Every function over the type repeats its recursion.
`Directory` contains `Node`s,
so `disk_usage()` and `walk()` call themselves on each entry.
Each `match` needs one case per member of the union and no more.

`disk_usage()` still accepts a lone `File`, a subtree, or the whole tree;
what changed from `filesystem_classic.py` is only where the operations live.
`disk_usage()` and `walk()` are ordinary functions outside the node classes,
so a new operation is a new function, and the nodes never change.
In the classic version a new node type is one class and a new operation is a method in every class.
The pairing has a name:
the [*expression problem*](13_Techniques--Pattern_Matching.md#the-expression-problem).
[Rethinking Objects](20_Patterns--Rethinking_Objects.md#polymorphism-without-inheritance)
works out the same split with shapes,
including the `assert_never()` in each `case _`.
Add a `Symlink` to the `Node` union,
and every function whose `case _` calls `assert_never()` fails type checking until it handles one.
Exercise 2 asks you to do that here, and to decide what a link should weigh.

`walk()` is a generator, so traversing a composite is lazy.
The [`yield from`](23_Patterns--Iterators.md#delegating-with-yield-from)
flattens the recursion into a single stream of paths,
and any consumer of that stream stays decoupled from the tree structure.

The `entries` field is a tuple of `Node`, so the whole tree is immutable.
A `list` there would leave the tree mutable.
A record freezes the binding of the field,
and the list it holds keeps its `append()`,
as [Rethinking Objects](20_Patterns--Rethinking_Objects.md#the-immutability-solution)
demonstrates.
With the tuple, sharing a subtree is safe: the demo builds `src` first,
then places it inside `root`, and `src` stays as built.

```python
# test_filesystem.py
from typing import Final
import pytest
from filesystem import (Directory, File, Node,
                        disk_usage, walk)

SUB: Final[Directory] = Directory(
    "sub", (File("b", 2), File("c", 3)))
TREE: Final[Directory] = Directory(
    "top", (File("a", 1), SUB))

@pytest.mark.parametrize("entry, expected", [
    (TREE, 6),
    (SUB, 5),
    (File("solo", 7), 7),
])
def test_disk_usage_is_uniform(entry: Node,
                               expected: int) -> None:
    assert disk_usage(entry) == expected

def test_walk_yields_full_paths() -> None:
    assert list(walk(TREE)) == [
        "top/a", "top/sub/b", "top/sub/c"]

def test_empty_directory() -> None:
    assert disk_usage(Directory("empty", ())) == 0
    assert list(walk(Directory("empty", ()))) == []
```

The classic version wins when the set of node types is open.
If plugins or other packages must add new kinds of entries,
a method on a base class lets them do that in their own code,
but a central `match` needs an edit in yours.
The [guidance on when not to match](13_Techniques--Pattern_Matching.md#when-not-to-match)
applies directly.
Match over a closed set, use polymorphism for an open one.

## Interpreter

A tree whose shape follows a grammar is an *abstract syntax tree* (AST).
Python's own compiler builds one of these for every source file.
`ast.parse()` returns it to you as node objects,
and `ast.NodeVisitor` walks them in the style of [*Visitor*](33_Patterns--Visitor.md).

*Interpreter* is *Composite* applied to language.
Representing each construct as a node type turns evaluation into a tree walk.

In most languages the pattern needs a class per construct and a parser to build the trees.
Python shrinks the classes and removes the parser, for one specific case:
sentences written as Python source in which every operator has at least one node operand.
A data class declares a node in three lines,
and operator overloading lets Python's own parser build the trees.
A GoF *Interpreter* more often parses a rules file, a configuration value,
or a query a user types at runtime; those arrive as text,
and text needs a real parser.
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

### The Nodes and the `Operators` Base

The four node classes are the grammar.
An expression is a number, a variable, a sum, or a product.
`Add` and `Mul` hold other expressions, so the tree is a composite.

`Operators` is a base class but not a member of `Expr`,
and the split is on purpose.
Every node shares the operator methods,
so those live on a base and each node inherits them.
Each node means something different, so meaning lives in the walkers.
Each walker's `assert_never()` needs the union to verify that its `match` covers every member.
`Expr` is the contract.
A base class is an open set that any new subclass silently joins,
so if you annotate `evaluate()` with `Operators` instead,
`assert_never()` stops working.

`Operators` declares no `__slots__`,
so an instance of any subclass carries a `__dict__` whatever its own class declares.
The nodes therefore keep `@dataclass(frozen=True)` instead of becoming [records](18_Techniques--Performance.md#record).

### Operators That Build Nodes

Every node inherits `__add__()` and `__mul__()`,
and those methods compute nothing.
They build nodes.
Annotating `self` as `Expr` lets `Add(self, ...)` type-check.
An implicit `self` means "some subclass of `Operators`,"
and the `Expr` annotation declares to the type checker that `self` is a member of the union.
`ty` accepts a `self` annotation narrower than the class.
Pyright and mypy require the declared type of `self` to be a supertype of its class,
so under either of them the portable form leaves `self` implicit and writes `cast(Expr, self)` at each construction.

Writing `x + 1` produces an `Add`,
so ordinary Python arithmetic notation constructs the AST.
The reflected forms `__radd__()` and `__rmul__()` handle an integer on the left,
and `wrap()` promotes an integer on the right to a `Num` node.
`2 * x + 1` is therefore a valid sentence in the little language.
Python has parsed it, applying its precedence rules,
before the interpreter runs.

The reflected methods depend on the operator dispatch from [*Multiple Dispatching*](32_Patterns--Multiple_Dispatching.md#operators-dispatch-twice).
`2 * x` works because `int.__mul__` returns `NotImplemented` and Python turns to `x.__rmul__(2)`.
Unlike that chapter's `Meters`, though,
these reflected methods accept any operand.
`ty` reports `"a" + x` as `unsupported-operator` in source it checks,
but at runtime `str.__add__` declines, `Var.__radd__` runs,
and the result is `Add(Num("a"), x)`,
an ill-typed tree whose error waits for `evaluate()` to add the `"a"`.
Exercise 6 makes each operator method return `NotImplemented` for an operand it cannot use,
so `"a" + x` raises `TypeError` at the `+`.

SymPy expressions, Polars column arithmetic,
and SQLAlchemy filter conditions all use this technique.
Overloaded operators build an expression tree,
and a library interprets that tree later, symbolically, over a whole column,
or as SQL.

Python's grammar sets the limit of the technique.
You can overload the arithmetic, bitwise, and comparison operators this way,
so an expression written with them builds nodes instead of computing.
`==` is the exception.
`@dataclass` writes its own `__eq__()` onto every node class.
Attribute lookup finds a class's own method before an inherited one,
so that generated `__eq__()` shadows anything `Operators` defines.
`expr.py` leaves `==` alone; the nodes compare by value,
and `evaluate.py`'s demo and its tests rely on that comparison.
When a library's `==` must build a node, as SQLAlchemy's `col == 5` does,
the library sets `eq=False` on the dataclass, giving up structural comparison,
and writes its own `__eq__()`.
This chapter keeps structural comparison;
a class gets either that or an `==` that builds a node, never both.

`and`, `or`, and `not` belong to Python alone.
Python tests the operand's truth value;
then `and` and `or` return one of the two objects, and `not` returns a `bool`.
`x and y` evaluates to `y`, builds nothing, and reports no error.
An expression language that needs boolean operators overloads `&` and `|` instead,
so a Pandas filter reads `(a > 1) & (b > 2)`.
The parentheses change the parse.
`&` binds tighter than `>`, so bare `a > 1 & b > 2` parses `1 & b` first.

## Evaluation Is a Tree Walk

Evaluation is a recursive `match` function.
Variables need values, which the caller supplies as keyword arguments:

```python
# evaluate.py
from typing import assert_never
from expr import Add, Expr, Mul, Num, Var

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

if __name__ == "__main__":
    x = Var("x")
    expr = 2 * x + 1
    by_hand = Add(Mul(Num(2), x), Num(1))
    print(expr == by_hand, expr.left)
    print(evaluate(expr, x=3), evaluate(expr, x=10))
#: True Mul(left=Num(value=2), right=Var(name='x'))
#: 7 21
```

The demo confirms that the operators build the tree you assemble by hand:
data classes generate `__eq__()`,
so `expr == by_hand` compares the two trees by value.
Printing `expr.left` shows the nesting: the `Add` at the root holds a `Mul`,
which holds a `Num` and a `Var`.
The second `print()` line evaluates that same `expr` twice,
once with `x=3` and once with `x=10`.
Building `2 * x + 1` does not compute a number.
It builds a tree, so `expr` is a value you can pass to `evaluate()` under different variable bindings,
as many times as you like.
An unbound variable raises a `KeyError`, naming the variable.

`**env` gives the call site `evaluate(expr, x=3)` rather than `evaluate(expr, {"x": 3})`,
and that convenience has a memory cost.
Each recursive call packs a fresh dict from `**env`,
so at any moment one dict is live per level of recursion,
and the live entries total the tree's depth times the number of bound variables.
The cost matters most on the deep trees this chapter warns about later,
which can run thousands of levels.
`**env` is also why the `/` is there.
The `/` makes `e` [positional-only](05_Foundations--Functions.md#positional-only-and-keyword-only-parameters),
which keeps the parameter name out of the variable namespace,
so an expression can use `e` as a variable: `e=5` lands in `env`,
and `test_e_is_available_as_a_variable()` below confirms that it binds the variable.
A `dict[str, int]` parameter passes the same bindings by reference at every call,
and it would spare both the `/` and this explanation.
This chapter keeps `**env` for the call site.

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

def test_e_is_available_as_a_variable() -> None:
    assert evaluate(Var("e"), e=5) == 5
```

## New Operations, Same Tree

Evaluation has no privileged status.
Rendering the tree as an infix string is another function, in another file,
and the node classes never change:

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

Adding `to_infix()` without editing a node class is the ability [*Visitor*](33_Patterns--Visitor.md)
exists to provide: new operations over a fixed hierarchy, defined outside it.
The `match` version needs no `accept()` method and no visitor classes.
Unlike `singledispatch`, it binds the nodes' fields in the patterns.

## Simplification Rewrites the Tree

An interpreter need not produce a number or a string.
It can produce another tree.
`simplify()` applies algebraic identities.
Adding zero or multiplying by one returns the other operand,
multiplying by zero returns `Num(0)`,
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
                    if lhs is left and rhs is right:
                        # Share the unchanged subtree
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

if __name__ == "__main__":
    from infix import to_infix
    x = Var("x")
    messy = 1 * x + 0 * Var("y") + (Num(2) + 3) * x
    print(to_infix(messy))
    print(to_infix(simplify(messy)))
#: (((1 * x) + (0 * y)) + ((2 + 3) * x))
#: (x + (5 * x))
```

`messy` writes `Num(2) + 3` rather than the plainer `2 + 3` on purpose.
With `2 + 3`, both operands are plain `int`,
so Python adds them to `5` before any node exists.
`simplify()` would receive `5 * x` with the fold already done.
`Num(2)` is already a node,
so `+` dispatches to `Operators.__add__()` and builds an `Add` for `simplify()` to fold back down.
`2 + 3` shows the limit of using the host parser:
an operator builds a node when either operand is one,
and does plain arithmetic otherwise.

The patterns read like the algebra they implement.
`(Num(0), other) | (other, Num(0))` says "zero on either side,
keep the other side."
Both alternatives bind `other`, and they must.
Every [alternative](13_Techniques--Pattern_Matching.md#alternatives-and-capture)
in a `|` must bind the same set of names,
so binding `left` in one and `right` in the other is a `SyntaxError` when the module compiles rather than an unbound name at runtime.
`(Num(a), Num(b))` captures two constants for folding.
The same syntax does two opposite jobs:
`Num(0)` after `case` is a pattern that Python matches without calling `Num`,
and `Num(0)` after `return` is a constructor call.

Matching the pair of simplified children, rather than the original node,
lets the rules compose.
A `case Add(Num(0), other)` at the top of the function tests the tree as the caller wrote it,
so `(0 * y) + x` keeps its zero.
The left child is a `Mul`,
and only becomes a `Num` once something simplifies it.
Simplifying both children first, then matching the results,
applies the rule to the `Num(0)` the recursion just produced.
That order is how the demo's `((1 * x) + (0 * y))` collapses to `x`.

`frozen=True` blocks every field assignment,
so `simplify()` never edits the input.
`simplify()` returns a new tree that shares unchanged subtrees with the original.
The `is` guard in each `case _` returns the node it received when both children simplified to themselves.
The guard tests identity with `is` rather than equality with `==`.
Sharing means the same object, and a data class's `==` compares whole subtrees,
so it would walk each subtree again at every level of the recursion.

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
    assert simplify(2 * x + 1) == Add(Mul(Num(2), x),
                                      Num(1))

def test_unchanged_subtrees_are_shared() -> None:
    keep = Var("w") * Var("h")
    assert simplify(keep + 0 * Var("z")) is keep
```

Three walkers over one set of nodes is the pattern pair in full.
*Composite* is the data: a union of node types, some holding others.
*Interpreter* is the behavior: recursive functions that give the tree meaning.
Python compresses the pair into frozen data classes, a union,
operator methods that build nodes, and `match` functions that walk them.
One practical limit applies.
Every function here recurses once per level of tree,
and Python's recursion limit (roughly a thousand frames)
caps how deep a tree they can walk.
Realistic expressions never approach it.
A machine-generated chain of thousands of nested nodes does.
The alternative is an iterative walk with an explicit stack of pending nodes.

## A Template Is a Tree {#a-template-is-a-tree}

Python has a composite of its own and supplies no walker for it,
so the walker is yours to write.
A [`t`-string](02_Foundations--Tour.md#t-strings) evaluates to a `Template`:
a stream of two node kinds,
the literal `str` pieces the author typed and the `Interpolation` objects holding the values.
Iterating a `Template` is flat.
`for piece in template` yields exactly one level of `str` and `Interpolation` objects,
so the walk itself is a loop rather than a recursion.
An interpolation's value can itself be a `Template`,
built by nesting one `t`-string inside another.
`+` concatenates `t`-strings into one flat `Template`,
as the `query` in the listing below shows,
so nesting is the one way to produce a `Template`-valued interpolation.
A walker that loops over the top level must therefore also recurse into any value that is a `Template`.
Everything else about walking a `Template` is this chapter's shape.

Iterating a `Template` produces `str | Interpolation`,
a closed union like `Node` with two members,
so an `isinstance` test narrows it as well as a `match` does.
The `else` branch is the `str` case.
Iteration skips the empty literal pieces,
so `t"{a}{b}"` yields two `Interpolation` objects and no strings;
`template.strings` keeps the empty slots when the alternation matters.
The structure is data, and its meaning is whatever a function computes from it:

```python
# template_query.py
from string.templatelib import Interpolation, Template

def to_query(
    template: Template) -> tuple[str, list[object]]:
    sql: list[str] = []
    values: list[object] = []
    for piece in template:
        if isinstance(piece, Interpolation):
            if isinstance(piece.value, Template):
                nested_sql, nested_values = (
                    to_query(piece.value))
                sql.append(nested_sql)
                values.extend(nested_values)
            else:
                sql.append("?")
                values.append(piece.value)
        else:
            sql.append(piece)
    return "".join(sql), values

def to_shape(template: Template) -> str:
    parts: list[str] = []
    for piece in template:
        if isinstance(piece, Interpolation):
            parts.append(f"<{piece.expression}>")
        else:
            parts.append(piece)
    return "".join(parts)

name = "Alice'; DROP TABLE users; --"
limit = 18
query = (t"SELECT name FROM users WHERE name={name} "
         + t"AND age>{limit}")
sql, values = to_query(query)
print(sql)
#: SELECT name FROM users WHERE name=? AND age>?
print(values)
#: ["Alice'; DROP TABLE users; --", 18]
print(to_shape(query))
#: SELECT name FROM users WHERE name=<name> AND age><limit>

inner = t"a={limit}"
outer = t"SELECT * FROM t WHERE {inner}"
sql2, values2 = to_query(outer)
print(sql2)
#: SELECT * FROM t WHERE a=?
print(values2)
#: [18]
```

`outer` interpolates `inner`, another `Template`, rather than a plain value.
`to_query()` checks for that case and recurses,
so `inner`'s pieces flatten into the same `sql` string and `values` list.
Every entry in `values2` is then a value a database driver accepts.
Composing `t`-strings this way builds a nested composite;
iterating any one `Template` stays flat.

`to_query()` and `to_shape()` stand in the same relationship as `evaluate()` and `to_infix()`:
two operations over one structure that names neither of them.
Adding a third changes nothing that already exists.

`to_query()` shows what the walk is for.
`name` holds an injection attempt,
and it comes out as a value in the parameter list rather than as text in the query.
The reason is structural rather than clever:
`to_query()` receives the literal pieces and the values separately,
so a value never reaches the `sql` list.
Written as an f-string,
the same line is one finished `str` with the attack already inside it.
The only remaining defense is inspecting the result to guess which characters the program wrote and which a user did.

That separation is the general argument for handing a consumer the structure instead of the answer.
A finished string no longer records which characters the program wrote and which a user did,
and the safety decision depends on that distinction.
Textbooks usually present the *Interpreter* pattern as a way to add operations to a language.
Here it keeps a decision available to whoever should make it.

## Exercises

1.  Add `find(entry, name)` to `filesystem.py`:
    a generator yielding the path of every entry whose name matches.
    A directory can match, and matching should continue into it.
2.  Add a `Symlink` node to the `Node` union in `filesystem.py`,
    holding a name and a target path,
    and let the type checker report every operation that must change.
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
6.  At runtime, `"a" + x` silently builds `Add(Num("a"), x)`,
    an ill-typed tree the type checker rejects in source it can see.
    Rewrite all four operator methods to return `NotImplemented` for an operand they cannot use
    ([*Multiple Dispatching*](32_Patterns--Multiple_Dispatching.md#operators-dispatch-twice) shows the idiom),
    and confirm that `"a" + x` and `x + "a"` both now raise a `TypeError`.
7.  Write a third walker over `Template` in `template_query.py`, `to_html()`,
    that emits the literal pieces unchanged and replaces `<`, `>`,
    and `&` in every interpolated value with their HTML entities.
    Show that `t"<p>{comment}</p>"` survives a `comment` containing a `<script>` tag.
8.  Build a left-deep expression by folding `+` over a few thousand `Num` nodes,
    and confirm that `evaluate()` raises a `RecursionError`.
    Then write `evaluate_iterative()`,
    which walks the same tree with an explicit stack and no recursion,
    and check that the two agree on a small expression.
    Raising the limit with `sys.setrecursionlimit()` is another way out.
    Say what it costs.
9.  A plugin package needs to add its own entry types to `filesystem.py` without editing your code.
    Sketch what breaks, then write the version of `disk_usage()` that supports it.
    Which of the two designs would you use for a file system,
    and which for the expression language in `expr.py`?
