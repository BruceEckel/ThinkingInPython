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
This chapter builds each pattern with [exhaustive matching](13_Techniques--Pattern_Matching.md#exhaustive-matching).

![The same shape, two applications: a filesystem tree where a Directory holds File or Directory entries, and an expression tree where Add and Mul hold other expressions](_images/composite_tree)

## The Classic Composite

A file system is the canonical composite.
A directory holds entries, and each entry is a file or another directory.
The payoff is uniformity.

The traditional version puts the operation in a class hierarchy,
hand-written constructors and all:

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
    "root", File("readme.md", 90), src,
    File("data.csv", 1200))
print(root.size(), src.size(), File("lone.txt", 10).size())
#: 1940 650 10
```

`Directory.size()` calls `size()` on each entry without knowing whether the entry is a `File` or another `Directory`.
The same call works on the whole tree, on a subtree, and on a single file.

Adding operations exposes the weakness.
Counting files, finding an entry by name,
and printing the tree each require a new method in every class.
[Visitor](33_Patterns--Visitor.md) exists to solve this problem.

## A Composite of Data Classes

In Python, define the node types as frozen data classes.
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

`Directory` now takes its entries as one tuple rather than as varargs,
because `@dataclass` generates `__init__()` from the field declarations,
and a field is one parameter.
The tuple keeps the tree immutable.
A paragraph below says why a `list` would not do.

`Directory` names `Node` before its definition below,
which works because Python evaluates annotations and `type` aliases lazily
(see [Naming Types: The `type` Statement](08_Foundations--Static_Types.md#the-type-statement)).

`disk_usage()` accepts a lone `File`, a subtree, or the whole tree.
What changed is where operations live.
`disk_usage()` and `walk()` are ordinary functions outside the node classes,
so a new operation is a new function, and the nodes never change.
[Rethinking Objects](20_Patterns--Rethinking_Objects.md#polymorphism-without-inheritance)
explores the same trade: a closed set of types,
with each operation gathered in one place.
The `assert_never()` in each `case _` makes that closed set pay off.
If you add a `Symlink` class to the `Node` union,
every function whose `case _` calls `assert_never()` fails type checking,
because `entry` could be a `Symlink` that no case handles.
The type checker flags each function that still needs a new case,
so you cannot forget one.

`walk()` is a generator, so traversing a composite is lazy.
The `yield from` flattens the recursion into a single stream of paths,
and any consumer of that stream stays decoupled from the tree structure
(see [Iterators](23_Patterns--Iterators.md#delegating-with-yield-from)).

The `entries` field is a tuple of `Node`, so the whole tree is immutable.
A `list` there would not do: `frozen=True` stops rebinding of the field,
not mutation of the object it holds,
which [Rethinking Objects](20_Patterns--Rethinking_Objects.md#the-immutability-solution)
demonstrates.
The demo builds `src` first, then places it inside `root`.
Nothing can modify `src` afterward, so sharing subtrees is safe
(see [Functional Foundations](40_Functional--Foundations.md#immutability)).

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

The classic version is still useful when the set of node types is open.
If plugins or other packages must add new kinds of entries,
a method on a base class lets them do that without touching your code,
but a central `match` needs editing.
The guidance from [Pattern Matching](13_Techniques--Pattern_Matching.md#when-not-to-match)
applies directly.
Match over a closed set, use polymorphism for an open one.

## Interpreter

A tree whose shape follows a grammar is an *abstract syntax tree* (AST).
Python's own compiler builds one of these for every source file,
and `ast.parse()` hands it to you as node objects that `ast.NodeVisitor` walks in the style of [Visitor](33_Patterns--Visitor.md).
Interpreter is Composite applied to language.
Representing each construct as a node type turns evaluation into a tree walk.

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
`Add` and `Mul` hold other expressions, which makes it a composite.

`Operators` is a base class but not a member of `Expr`,
and the split is on purpose.
Every node shares the operator methods,
so those live on a base and arrive by inheritance.
No node shares its meaning, so meaning lives in the walkers,
which need the union to know they have covered every case.
`Expr` is the contract: if you annotate `evaluate()` with `Operators` instead,
`assert_never()` stops working,
because a base class is an open set and any new subclass silently belongs to it.

Every node inherits `__add__()` and `__mul__()`,
and those methods do not compute anything.
They build nodes.
Annotating `self` as `Expr` rather than leaving it implicit lets `Add(self, ...)` type-check.
`Self` would mean "some subclass of `Operators`,"
and the type checker cannot know that every such subclass is in the `Expr` union.
The annotation says so.
Writing `x + 1` produces an `Add`,
so ordinary Python arithmetic notation constructs the AST.
The reflected forms `__radd__()` and `__rmul__()` handle an integer on the left,
and `wrap()` promotes integers to `Num` nodes,
so `2 * x + 1` is a valid sentence in the little language.
Python has parsed it, honoring precedence, before the interpreter runs.

The reflected methods depend on the operator dispatch from [Multiple Dispatching](32_Patterns--Multiple_Dispatching.md#operators-dispatch-twice):
`2 * x` works because `int.__mul__` returns `NotImplemented` and Python turns to `x.__rmul__(2)`.
Unlike that chapter's `Meters`, though,
these reflected methods trust their operand completely.
The type checker rejects `"a" + x` in source it can see,
but at runtime nothing checks: `str.__add__` declines, `Var.__radd__` runs,
and `Add(Num("a"), x)` appears without complaint,
an ill-typed tree instead of an error.
Exercise 6 closes the hole with the declining-`NotImplemented` idiom.

SymPy expressions, Pandas and Polars column arithmetic,
and SQLAlchemy filter conditions all use this technique.
Overloaded operators build an expression tree,
and a library interprets that tree later, symbolically, over a whole column,
or as SQL.

Python's grammar sets the limit of the technique.
You can overload all the arithmetic, bitwise, and comparison operators,
so an expression written with them builds nodes instead of computing.
`and`, `or`, and `not` you cannot: Python asks the operand for a truth value,
then `and` and `or` hand back one of the two objects,
and `not` hands back a `bool`.
`x and y` evaluates to `y`, builds nothing, and reports no error.
An expression language that needs boolean operators borrows `&` and `|` instead,
which is why a Pandas filter reads `(a > 1) & (b > 2)` with parentheses that look unnecessary.
They are not: `&` binds tighter than `>`,
so without them Python parses `1 & b` first.

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

Data classes generate `__eq__()`, so two trees compare by value,
and the demo confirms that the operators build the tree you would assemble by hand.
Printing `expr.left` shows the nesting: the `Add` at the root holds a `Mul`,
which holds a `Num` and a `Var`.
The second `print()` line evaluates that same `expr` twice,
once with `x=3` and once with `x=10`.
Building `2 * x + 1` does not compute a number.
It builds a tree, so `expr` is a value you can hand to `evaluate()` under different variable bindings,
as many times as you like.
An unbound variable raises a `KeyError`, naming the variable.
The `/` makes `e` positional-only
(see [Positional-Only and Keyword-Only Parameters](05_Foundations--Functions.md#positional-only-and-keyword-only-parameters)),
which keeps the parameter name out of the variable namespace so an expression can use `e` as a variable.

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

This is the ability [Visitor](33_Patterns--Visitor.md) fights to provide:
new operations over a fixed hierarchy, defined outside it.
The `match` version needs no `accept()` method and no visitor classes,
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

The patterns read like the algebra they implement.
`(Num(0), other) | (other, Num(0))` says "zero on either side,
keep the other side."
Both alternatives bind `other`, and they must:
every alternative in a `|` must bind the same set of names,
so binding `left` in one and `right` in the other is a `SyntaxError` rather than a runtime surprise
(see [Alternatives and Capture](13_Techniques--Pattern_Matching.md#alternatives-and-capture)).
`(Num(a), Num(b))` captures two constants for folding.
The same syntax does two opposite jobs:
a `Num(0)` on the left of a `case` is a pattern that never calls `Num`,
and the one on the right of a `return` is the constructor.

Matching the pair of simplified children, rather than the original node,
lets the rules compose.
A `case Add(Num(0), other)` at the top of the function would test the tree as the caller wrote it,
and `(0 * y) + x` would keep its zero:
the left child is a `Mul` and only becomes a `Num` once something simplifies it.
Simplifying both children first and matching the results catches the identity the recursion just exposed,
which is how the demo's `((1 * x) + (0 * y))` collapses to `x`.

`frozen=True` blocks every field assignment,
so `simplify()` never edits the input.
It returns a new tree that shares unchanged subtrees with the original:
the `is` guard in each `case _` hands back the node it received when neither child simplified to anything different.

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
Composite is the data: a union of node types, some holding others.
Interpreter is the behavior: recursive functions that give the tree meaning.
Python compresses the pair into frozen data classes, a union,
operator methods that build nodes, and `match` functions that walk them.
One practical limit applies:
every function here recurses once per level of tree,
and Python's recursion limit (roughly a thousand frames)
caps how deep a tree they can walk.
Realistic expressions never approach it.
A machine-generated chain of thousands of nested nodes does,
and the escape is an iterative walk driving an explicit stack of pending nodes.

## A Template Is a Tree {#a-template-is-a-tree}

Python has a composite of its own and supplies no walker for it,
which invites you to write one.
A `t`-string, which [Tour](02_Foundations--Tour.md#t-strings) introduced,
evaluates to a `Template`: a sequence of two node kinds,
the literal `str` pieces the author typed and the `Interpolation` objects holding the values.
Iteration skips the empty literal pieces,
so `t"{a}{b}"` yields two `Interpolation` objects and no strings.
`template.strings` keeps the empty slots when the alternation matters.
The grammar is flat rather than nested,
so the walk is a loop instead of a recursion,
but everything else about it is this chapter's shape.

Iterating a `Template` produces `str | Interpolation`,
a closed union like `Node` with two members,
so an `isinstance` test narrows it as well as a `match` would,
and the `else` branch is the `str` case.
The structure is data, and what it means is whatever a function decides:

```python
# template_query.py
from string.templatelib import Interpolation, Template

def to_query(
    template: Template) -> tuple[str, list[object]]:
    sql: list[str] = []
    values: list[object] = []
    for piece in template:
        if isinstance(piece, Interpolation):
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
```

`to_query()` and `to_shape()` are the same relationship as `evaluate()` and `to_infix()`:
two operations over one structure, which knows neither of them,
and adding a third changes nothing that already exists.

The first one earns its place.
`name` holds an injection attempt,
and it comes out as a value in the parameter list rather than as text in the query.
The reason is structural rather than clever:
`to_query()` receives the literal pieces and the values as separate things,
so it can never confuse them.
Written as an f-string,
the same line would arrive as one finished `str` with the attack already spliced in,
and the only remaining defense would be inspecting the result to guess which characters the program wrote and which a user did.

That is the general argument for handing a consumer the structure instead of the answer.
A finished string has thrown away the distinction on which the safety decision depends.
Textbooks usually present the Interpreter pattern as a way to add operations to a language.
Here it keeps a decision available to whoever should make it.

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
6.  At runtime, `"a" + x` silently builds `Add(Num("a"), x)`,
    an ill-typed tree the type checker rejects in source it can see.
    Rewrite `__radd__()` and `__rmul__()` to return `NotImplemented` for a non-`int` operand
    ([Multiple Dispatching](32_Patterns--Multiple_Dispatching.md#operators-dispatch-twice) shows the idiom),
    and confirm `"a" + x` now raises a `TypeError`.
7.  Write a third walker over `Template` in `template_query.py`, `to_html()`,
    that emits the literal pieces unchanged and replaces `<`, `>`,
    and `&` in every interpolated value with their HTML entities.
    Show that `t"<p>{comment}</p>"` survives a `comment` containing a `<script>` tag.
8.  Build a left-deep expression by folding `+` over a few thousand `Num` nodes,
    and confirm that `evaluate()` raises a `RecursionError`.
    Then write `evaluate_iterative()`,
    which walks the same tree with an explicit stack and no recursion,
    and check that the two agree on a small expression.
    Raising the limit with `sys.setrecursionlimit()` is the other escape.
    Say what it costs.
9.  A plugin package needs to add its own entry types to `filesystem.py` without editing your code.
    Sketch what breaks, then write the version of `disk_usage()` that supports it.
    Which of the two designs would you use for a file system,
    and which for the expression language in `expr.py`?
