# Composite and Interpreter

> An item can hold more items of its own kind,
> and code must treat one item and a whole group the same way.
> *Composite* builds that tree,
> and *Interpreter* reads one as a sentence and evaluates it.

In *Composite*, each node is a leaf or a group of nodes,
and one call handles both.
In *Interpreter*, the tree is a sentence in a small language,
and evaluating the sentence walks the tree.
*GoF Design Patterns* presents them as separate patterns,
but *Interpreter* is *Composite* with meaning attached.
In Python both reduce to one technique: a union of records for the nodes,
and recursive functions that `match` on them.
Each of those `match` statements is [exhaustive](13_Techniques--Pattern_Matching.md#exhaustive-matching),
so the type checker reports a node kind that no case handles.

## The Classic Composite

A file system is the canonical composite.
A directory holds entries, and each entry is a file or another directory.
The point is uniformity: one call works on a file, a directory,
or the whole tree.

![Each directory adds up what its entries return](_images/composite_tree)

`root.disk_usage()` adds up every file below `root` to get 1940.
The same call on `src` or on a single file returns the size of that subtree or file.

The traditional version puts each operation inside the node classes,
under an abstract method on a shared base:

```python
# filesystem_classic.py
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import override
from record import record

type Location = str

class Node(ABC):
    __slots__ = ()
    name: str

    @abstractmethod
    def disk_usage(self) -> int: ...

    @abstractmethod
    def walk(
        self, prefix: Location = ""
    ) -> Iterator[Location]: ...

@record
class File(Node):
    name: str
    size: int

    @override
    def disk_usage(self) -> int:
        return self.size

    @override
    def walk(
        self, prefix: Location = ""
    ) -> Iterator[Location]:
        yield prefix + self.name

@record
class Directory(Node):
    name: str
    entries: tuple[Node, ...]

    @override
    def disk_usage(self) -> int:
        return sum(entry.disk_usage()
                   for entry in self.entries)

    @override
    def walk(
        self, prefix: Location = ""
    ) -> Iterator[Location]:
        for entry in self.entries:
            yield from entry.walk(f"{prefix}{self.name}/")

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

`Directory.disk_usage()` calls `disk_usage()` on each entry,
whether the entry is a `File` or another `Directory`.

Adding a node type is one class.
A plugin writes it and leaves the classes above it as they are.
Adding an operation exposes the weakness.
`walk()` needs a method in every class,
and counting files or finding an entry by name each needs another.
[*Visitor*](33_Patterns--Visitor.md) exists to solve this problem.

## A Composite of Data Classes

The next version moves the operations out of the classes.
The nodes keep their fields, a union lists the closed set of alternatives,
and each operation becomes a recursive function that matches on that union.
The nodes stay [records](18_Techniques--Performance.md#record),
now with no base class above them:

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
type Location = str

def disk_usage(entry: Node) -> int:
    match entry:
        case File(_, size):
            return size
        case Directory(_, entries):
            return sum(disk_usage(child)
                       for child in entries)
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
        case _:
            assert_never(entry)
```

`Node` is a recursive union.
`Directory` holds a `tuple[Node, ...]`,
so the alias names itself through one of its members.
That self-reference lets a `Directory` hold other directories to any depth.

`Directory` mentions `Node` above the [`type` statement](08_Foundations--Static_Types.md#the-type-statement)
that defines `Node`.
That works because Python evaluates annotations and `type` aliases lazily,
the [deferred evaluation](08_Foundations--Static_Types.md#self-and-forward-references).
The alias can therefore sit below the classes it unites,
where it reads as a summary of them rather than as a forward declaration.

Every function over `Node` repeats the union's recursion.
Because `Directory` contains `Node`s,
`disk_usage()` and `walk()` call themselves on each entry.
Each `match` needs one case per member of the union.

`disk_usage()` still accepts a lone `File`, a subtree, or the whole tree.
Two things differ from `filesystem_classic.py`: where the operations live,
and the closed union that replaces the base class.
`disk_usage()` and `walk()` are ordinary functions outside the node classes,
so a new operation is a new function, and the nodes stay unchanged.
A new node type now touches every function.
If you add a `Symlink` to the `Node` union,
every function whose `case _` calls `assert_never()` fails type checking until it handles `Symlink`
(see exercise 2).
The classic version reverses the two.
A new node type is one class, and a new operation is a method in every class.
The pairing has a name:
the [*expression problem*](13_Techniques--Pattern_Matching.md#the-expression-problem).
[Rethinking Objects](20_Patterns--Rethinking_Objects.md#polymorphism-without-inheritance)
works out the same split with shapes,
including the `assert_never()` in each `case _`.

`walk()` is a generator, so traversing a composite is lazy.
The [`yield from`](22_Patterns--Iterators.md#delegating-with-yield-from)
flattens the recursion into a single stream of paths.
A consumer of that stream receives path strings.
The `match` on `File` and `Directory` stays inside `walk()`.

The `entries` field is a tuple of `Node`, so the whole tree is immutable.
A record freezes the binding of the field, not the object bound to it.
As [Rethinking Objects](20_Patterns--Rethinking_Objects.md#the-immutability-solution)
demonstrates, a list in that field keeps its `append()`,
so a `list` there leaves the tree mutable.
With the tuple, two trees can share a subtree, and neither can change it.

The test file confirms that:

- `disk_usage()` returns the size of the whole tree, a subtree, or a lone file.
- `walk()` yields each file's full path.
- An empty directory has size 0 and yields no paths.

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

`test_filesystem.py` shares a subtree.
It builds `SUB` first, then places it inside `TREE`, and `SUB` stays as built.

The classic version is a better choice when the set of node types is open.
If plugins or other packages must add new node types,
a method on a base class lets them do that in their own code,
but a central `match` needs an edit in yours.
The [guidance on when not to match](13_Techniques--Pattern_Matching.md#when-not-to-match)
applies to node types.

A file and a directory are both a `Path`,
which makes `pathlib` look like a *Composite*.
`pathlib` has the uniform interface.
`name`, `exists()`, and `stat()` work on either kind of entry.
`iterdir()` lists one directory and `rglob()` walks the whole tree.
Both yield a `Path` for each entry, whatever its kind.
`pathlib` lacks the structure.
A `Path` is an immutable value that names a location.
The entries and the tree they form live in the operating system's filesystem.
`iterdir()` asks the OS for the children each time you call it.
The caller must add up any result over that tree, as `disk_usage()` does.
On a directory, `stat().st_size` reports the size of the directory itself rather than the size of its contents,
so you add up the sizes yourself:

```python
total = sum(p.stat().st_size for p in root.rglob("*")
            if p.is_file())
```

`rglob()` supplies the traversal,
and `sum()` supplies the combining step that `disk_usage()` performs for a `Directory`.
The filesystem is the composite, and a `Path` is a handle into it.

## Interpreter

A tree whose shape follows a grammar is an *abstract syntax tree* (AST).
Python's own compiler builds one of these for every source file.
`ast.parse()` returns it to you as node objects,
and `ast.NodeVisitor` walks them in the style of [*Visitor*](33_Patterns--Visitor.md).

*Interpreter* is *Composite* applied to language.
Representing each construct as a node type turns evaluation into a tree walk.

In most languages the pattern needs a class per construct and a parser to build the trees.
Python shrinks the classes and removes the parser.
A record declares a node in three or four lines,
and operator overloading lets Python's own parser build the trees.
Python's parser builds them only for sentences written as Python source in which every operator has at least one node operand.
A GoF *Interpreter* more often parses a rules file, a configuration value,
or a query a user types at runtime.
Those arrive as text, and text needs a real parser.
The complete grammar for a small arithmetic language fits in one module:

```python
# expr.py
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
```

### The Nodes and the `Operators` Base

The four node classes are the grammar.
An expression is a number, a variable, a sum, or a product.
`Add` and `Mul` hold other expressions, so the tree is a composite.

`Operators` is a base class but, on purpose, not a member of `Expr`.
Every node shares the operator methods,
so those live on a base and each node inherits them.
Each node means something different, so meaning lives in the *walkers*,
the recursive functions that `match` on the union.
Each walker's `assert_never()` needs the union to verify that its `match` covers every member,
so `Expr` is the contract.
A base class is an open set, since any module can define a new subclass.
If you annotate `evaluate()` with `Operators` instead,
`assert_never()` fails type checking even with a case for every node.

### Operators That Build Nodes

Every node inherits `__add__()` and `__mul__()`,
which build nodes instead of computing a value.
Annotating `self` as `Expr` lets `Add(self, ...)` type-check.
An implicit `self` means "some subclass of `Operators`."
The `Expr` annotation declares to the type checker that `self` is a member of the union.

`ty` accepts a `self` annotation narrower than the class.
Pyright and mypy require the declared type of `self` to be a supertype of its class.
All three checkers accept a form that leaves `self` implicit and writes `cast(Expr, self)` at each construction.

Writing `x + 1` produces an `Add`,
so ordinary Python arithmetic notation constructs the AST.
The reflected forms `__radd__()` and `__rmul__()` handle an integer on the left,
and `wrap()` promotes an integer on the right to a `Num` node.
`2 * x + 1` is therefore a valid sentence in the little language.
Python has parsed it, applying its precedence rules,
before the interpreter runs.
Compare the tree the operators build with one built from constructor calls:

```python
# build_tree.py
from expr import Add, Mul, Num, Var

x = Var("x")
expr = 2 * x + 1
nested = Add(Mul(Num(2), x), Num(1))
print(expr == nested, type(expr).__name__, expr.left)
#: True Add Mul(left=Num(value=2), right=Var(name='x'))
```

Records generate `__eq__()`,
so `expr == nested` compares the two trees by value.

`build_tree.py` puts the integer on the left of `*` and on the right of `+`.
The test checks the integer on either side of `+`,
and a product with no integer:

```python
# test_expr.py
from expr import Add, Mul, Num, Var

def test_operators_build_the_tree() -> None:
    x = Var("x")
    assert 2 * x + 1 == Add(Mul(Num(2), x), Num(1))
    assert 1 + x == Add(Num(1), x)
    assert x * x == Mul(x, x)
```

The reflected methods depend on the operator dispatch from [*Multiple Dispatching*](32_Patterns--Multiple_Dispatching.md#operators-dispatch-twice).
`2 * x` works because `int.__mul__()` returns `NotImplemented` and Python calls `x.__rmul__(2)`.
Unlike that chapter's `Meters`, though,
these reflected methods accept any operand.
`ty` reports `"a" + x` as `unsupported-operator` in source it checks,
but at runtime `Var.__radd__()` runs before `str` tries to concatenate.
The result is `Add(Num("a"), x)`,
an ill-typed tree that raises a `TypeError` later,
when `evaluate()` adds the `"a"`.
If each operator method returns `NotImplemented` for an operand it cannot use,
`"a" + x` raises a `TypeError` at the `+` (see exercise 6).

SymPy expressions, Polars column arithmetic,
and SQLAlchemy filter conditions all use this technique.
Overloaded operators build an AST, and a library interprets that tree later,
symbolically, over a whole column, or as SQL.

You can overload the arithmetic, bitwise, and comparison operators this way,
so an expression written with them builds nodes instead of computing.
`==` is the exception in `expr.py`,
where it compares nodes instead of building one.
`@record` writes its own `__eq__()` onto every node class.
Attribute lookup finds a class's own method before an inherited one,
so that generated `__eq__()` shadows anything `Operators` defines.

Leaving `==` alone suits `expr.py`.
The nodes compare by value,
and `build_tree.py` and the chapter's tests rely on that comparison.
SQLAlchemy's `col == 5` builds a node,
so its column classes define their own `__eq__()` and give up `==` as a structural comparison.
A data class that builds a node from `==` sets `eq=False`,
so the class keeps the `__eq__()` it inherits.
A class can have structural comparison or an `==` that builds a node,
but not both.
This chapter keeps structural comparison.

Python's grammar sets a harder limit.
`and`, `or`, and `not` have no special methods of their own,
so no class can make them build a node.
Python tests the operand's truth value.
Then `and` and `or` return one of their two operands,
and `not` returns a `bool`.
`x and y` evaluates to `y` and quietly drops `x` from the expression.
An expression language that needs boolean operators overloads `&` and `|`,
so a Pandas filter reads `(a > 1) & (b > 2)`.
The parentheses change the parse.
`&` binds tighter than `>`, so bare `a > 1 & b > 2` parses `1 & b` first.

## Evaluation Is a Tree Walk

Evaluation is a recursive `match` function.
Variables need values,
which the caller supplies in a mapping from each name to its value.
Every recursive call passes that same `env` along:

```python
# evaluate.py
from collections.abc import Mapping
from typing import assert_never
from expr import Add, Expr, Mul, Num, Var

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

if __name__ == "__main__":
    x = Var("x")
    expr = 2 * x + 1
    print(evaluate(expr, {"x": 3}),
          evaluate(expr, {"x": 10}))
#: 7 21
```

Building `2 * x + 1` produces a tree, not a number,
so `expr` is a value you can pass to `evaluate()` under different variable bindings,
as many times as you like.
An unbound variable raises a `KeyError`, naming the variable.

The test file confirms that:

- A `Num` evaluates to its value and a `Var` to its binding.
- One tree evaluates under different bindings.
- An unbound variable raises a `KeyError` that names the variable.

```python
# test_evaluate.py
import pytest
from evaluate import evaluate
from expr import Num, Var

def test_literal_and_variable() -> None:
    assert evaluate(Num(42), {}) == 42
    assert evaluate(Var("x"), {"x": 3}) == 3

def test_one_tree_many_environments() -> None:
    area = Var("w") * Var("h")
    assert evaluate(area, {"w": 2, "h": 3}) == 6
    assert evaluate(area, {"w": 10, "h": 10}) == 100

def test_unbound_variable_raises_key_error() -> None:
    with pytest.raises(KeyError, match="y"):
        evaluate(Var("y"), {"x": 1})
```

## New Operations, Same Tree

Evaluation is one operation among many.
Rendering the tree as an infix string is another function, in another file,
and the node classes stay unchanged:

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

`to_infix()` walks the same tree that `evaluate()` walks,
from the same `2 * x + 1`:

![](_images/composite_story)

Side by side, the two walks share their shape.
Each makes one call per node, leaf or group.
The call for each node returns its result to the call for that node's parent.
Only the value each call returns differs,
an `int` in one walk and a `str` in the other.
The tree holds the structure.
Each walker supplies the meaning, so a new operation is one more walker.

[*Visitor*](33_Patterns--Visitor.md)
exists to add new operations to an existing hierarchy from outside it.
`to_infix()` is one such operation, and every node class stays unchanged.
The `match` version replaces the `accept()` methods and the visitor classes with one function.
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
```

Printing a messy tree before and after `simplify()` shows the rules at work:

```python
# simplify_demo.py
from expr import Num, Var
from infix import to_infix
from simplify import simplify

x = Var("x")
messy = 1 * x + 0 * Var("y") + (Num(2) + 3) * x
print(to_infix(messy))
#: (((1 * x) + (0 * y)) + ((2 + 3) * x))
print(to_infix(simplify(messy)))
#: (x + (5 * x))
```

`messy` writes `Num(2) + 3` rather than the plainer `2 + 3` on purpose.
With `2 + 3`, both operands are plain `int`,
so Python adds them to `5` before any node exists.
`simplify()` receives `5 * x` with the fold already done.
`2 + 3` shows the limit of using the host parser.
An operator builds a node when either operand is a node,
and does plain arithmetic otherwise.
`Num(2)` is a node, so `+` dispatches to `Operators.__add__()` and builds an `Add` for `simplify()` to fold back down.

The patterns read like the algebra they implement.
`(Num(0), other) | (other, Num(0))` says "zero on either side,
keep the other side."
The same syntax does two opposite jobs:
`Num(0)` after `case` is a pattern that tests for a `Num` whose `value` equals 0,
and `Num(0)` after `return` is a constructor call.

Both alternatives of the zero rule bind `other`, and they must.
Every [alternative](13_Techniques--Pattern_Matching.md#alternatives-and-capture)
in a `|` must bind the same set of names.
Binding `left` in one alternative and `right` in the other is a `SyntaxError`,
reported when the module compiles rather than as an unbound name at runtime.

Matching the pair of simplified children, rather than the original node,
lets the rules compose.
A `case Add(Num(0), other)` at the top of the function tests the tree as the caller wrote it.
In `(0 * y) + x`, the left child is still a `Mul` when that case tests it.
The pattern does not match, so the expression keeps its zero.
Simplifying both children first, then matching the results,
applies the rule to the `Num(0)` the recursion just produced.
That order lets the demo's `((1 * x) + (0 * y))` simplify to `x`.

A record freezes every field, so `simplify()` builds its result as a new tree.
That tree shares unchanged subtrees with the original.
The `if` inside each `case _` tests identity with `is` rather than equality with `==`.
Sharing means the same object.
`is` answers with one comparison,
where a record's `==` compares fields and descends into any subtree that changed.

The test file confirms that:

- Adding zero or multiplying by one returns the other operand.
- Multiplying by zero returns `Num(0)`.
- Constant subtrees fold into one `Num`.
- The rules apply at every level of the tree.
- An expression in simplest form comes back as the same object.
- The result shares an unchanged subtree with the input.

```python
# test_simplify.py
from typing import Final
import pytest
from expr import Expr, Mul, Num, Var
from simplify import simplify

X: Final[Var] = Var("x")

@pytest.mark.parametrize("expr, expected", [
    (X + 0, X),
    (0 + X, X),
    (1 * X, X),
    (X * 1, X),
])
def test_identity_returns_other_operand(
    expr: Expr, expected: Expr,
) -> None:
    assert simplify(expr) == expected

def test_multiplying_by_zero_gives_zero() -> None:
    assert simplify(X * 0) == Num(0)
    assert simplify(0 * X) == Num(0)

def test_constant_folding() -> None:
    assert simplify(Num(2) + 3) == Num(5)
    assert simplify(Num(2) * 3 + 4) == Num(10)

def test_rules_compose() -> None:
    assert simplify((X + 0) * (1 * X)) == Mul(X, X)

def test_already_simple_is_unchanged() -> None:
    expr = 2 * X + 1
    assert simplify(expr) is expr

def test_unchanged_subtrees_are_shared() -> None:
    keep = Var("w") * Var("h")
    assert simplify(keep + 0 * Var("z")) is keep
```

Three walkers over one set of nodes is the pattern pair in full.
*Composite* is the data: a union of node types, some holding others.
*Interpreter* is the behavior: recursive functions that give the tree meaning.
Python expresses the pair with records, a union,
operator methods that build nodes, and `match` functions that walk them.

Every function here recurses once per level of tree.
Python's default recursion limit of 1000 stack frames therefore caps how deep a tree these functions can walk.
A hand-written expression nests a few levels deep.
A machine-generated chain of thousands of nested nodes exceeds the limit.
The alternative is an iterative walk with an explicit stack of pending nodes
(see exercise 8).

The walkers also assume that each node appears at one place in the tree.
`expr.py` lets one node appear at several.
After `s = x + 1`, the `Mul` that `s * s` builds holds the same `s` twice,
so `evaluate()` walks `s` twice.
A dependency graph shares nodes as a rule.
Several build targets depend on one library,
so a recursive walk from each target builds that library again.

Such a structure is a *directed acyclic graph*, or DAG, rather than a tree.
Processing a DAG means visiting each node once, after all of its dependencies.
`graphlib.TopologicalSorter`, in the standard library since Python 3.9,
computes that order from a mapping of each node to its dependencies:

```python
# build_order.py
from graphlib import CycleError, TopologicalSorter
from exceptions import expected

type Target = str

deps: dict[Target, tuple[Target, ...]] = {
    "app": ("ui", "db"),
    "ui": ("core",),
    "db": ("core",),
}
print(list(TopologicalSorter(deps).static_order()))
#: ['core', 'ui', 'db', 'app']
deps["core"] = ("app",)
with expected(CycleError):
    list(TopologicalSorter(deps).static_order())
#: [CycleError] ('nodes are in a cycle', ['app', 'core',
#: 'ui', 'app'])
```

`core` appears once, although both `ui` and `db` depend on it.
Pointing `core` back at `app` closes a loop,
and `static_order()` reports the loop as a `CycleError` instead of guessing an order.

A build that runs targets in parallel calls `prepare()` once,
then alternates `get_ready()` and `done()` in place of `static_order()`.
`get_ready()` returns every node whose dependencies have all finished,
so `ui` and `db` come back together after `core` finishes.

## A Template Is a Tree {#a-template-is-a-tree}

Python has a composite of its own.
Its walker is yours to write.
A [`t`-string](02_Foundations--Tour.md#t-strings) evaluates to a `Template`:
a stream of two node kinds,
the literal `str` pieces the author typed and the `Interpolation` objects holding the values.
Iterating over a `Template` is flat.
`for piece in template` yields one level of `str` and `Interpolation` objects,
so the walk is a loop rather than a recursion.
An interpolation's value can be a `Template`,
built by nesting one `t`-string inside another.
`+` instead concatenates `t`-strings into one flat `Template`,
as `query` in `template_query.py` shows.
Nesting, not `+`, produces a `Template`-valued interpolation.
A walker that needs the pieces at every level must therefore also recurse into any value that is a `Template`.
Everything else follows this chapter's walkers: one branch per node kind,
and a recursive call where a node holds more nodes.

Iteration skips the empty literal pieces,
so `t"{a}{b}"` yields two `Interpolation` objects and no strings.
When a walker needs the pieces to alternate,
`template.strings` keeps the empty slots.
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

Iterating over a `Template` produces `str | Interpolation`,
a closed union like `Node` with two members,
so an `isinstance()` test narrows it as well as a `match` does.
The `else` paired with `isinstance(piece, Interpolation)` is the `str` case.

`to_query()` and `to_shape()` stand in the same relationship as `evaluate()` and `to_infix()`:
two operations over one structure that mentions neither of them.
A third operation is one more function,
and neither `Template` nor the two existing functions change.

`to_query()` recurses into the nested `inner`,
so `inner`'s pieces flatten into the same `sql` string and `values` list.
Every entry in `values2` is then a value a database driver accepts.
Composing `t`-strings this way builds a nested composite.
Iterating over any one `Template` stays flat.

`to_query()` uses the walk to keep user values out of the query text.
`name` holds an injection attempt.
`to_query()` receives the literal pieces and the values separately,
so `name` comes out as a value in the parameter list rather than as text in the query.
Written as an f-string,
the same line is one finished `str` with the attack inside it.
Any defense must then inspect that string and guess where the user's text begins.

That separation is the general argument for handing a consumer the structure instead of the answer.
A finished string merges the characters the program wrote with the characters a user supplied.
Any safety decision must then tell the two apart again.
Textbooks usually present the *Interpreter* pattern as a way to evaluate sentences in a small language.
Here *Interpreter* keeps a decision available to whoever should make it.

## Exercises

Try each exercise before opening its [solution](../Solutions/34_Patterns--Composite_and_Interpreter/).

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
    Using the idiom from [*Multiple Dispatching*](32_Patterns--Multiple_Dispatching.md#operators-dispatch-twice),
    rewrite all four operator methods to return `NotImplemented` for an operand they cannot use.
    Confirm that `"a" + x` and `x + "a"` both now raise a `TypeError`.
7.  Write a third walker over `Template` in `template_query.py`, `to_html()`,
    that emits the literal pieces unchanged and replaces `<`, `>`,
    and `&` in every interpolated value with their HTML entities.
    Show that `t"<p>{comment}</p>"` survives a `comment` containing a `<script>` tag.
8.  Build a left-deep expression by folding `+` over a few thousand `Num` nodes,
    and confirm that `evaluate()` raises a `RecursionError`.
    Then write `evaluate_iterative()`,
    which walks the same tree with an explicit stack and no recursion,
    and check that the two agree on a small expression.
    Raising the limit with `sys.setrecursionlimit()` also avoids the error.
    Name its drawbacks.
9.  A plugin package needs to add its own node types to `filesystem.py` without editing your code.
    Sketch what breaks, then write the version of `disk_usage()` that supports the plugin's node types.
    For a file system, would you use a `match` over a union or a method on a base class?
    Which would you use for the expression language in `expr.py`?
