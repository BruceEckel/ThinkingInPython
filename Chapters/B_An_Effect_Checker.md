# An Effect Checker

[Effect Tracking](A_Effect_Tracking.md#what-a-checker-for-the-row-must-do)
lists five problems a checker for `Annotated` rows must solve,
and concludes that solving them all means rebuilding a type checker.
This appendix builds the part that needs no type inference.
The checker here reads source text, resolves the calls it can,
infers a row for every function, and reports each declared row the body exceeds.
It is about 450 lines, and most of its pieces come from earlier chapters:
a `match` over syntax-tree nodes, records for the data,
a `Result` for the one operation that can fail,
and a pure core with its Effects at the edge.
The final listing runs the checker on its own source to confirm that last point.

## The Restriction

The checker resolves a call by its name and by the written type of its receiver.
A call it cannot resolve contributes an Effect named `Unknown` to the caller's row.
The checker treats no unresolved call as pure.
With that rule the tool's reports stay true while the tool stays small.
A row that reads `Unknown` says the checker could not resolve a call, and where.

Name resolution covers more calls than you might expect.
Of the 6,442 calls in this book's chapter listings,
four in five resolve by name alone: a builtin, an imported name,
or a function or class defined in the same file.
The largest remaining group is a method called on a local variable with no annotation,
and [From a Call to a Name](#from-a-call-to-a-name) recovers part of that group.

The checker follows Koka's policy,
from [Effect Tracking](A_Effect_Tracking.md#why-a-native-system-tracks-best).
A function with no written row gets an inferred one.
The checker compares a written row with the function's body,
and the function's callers trust the declaration.
`performs()` with no arguments declares that a function is pure.

## Effect Names and the Table

An Effect is a class with no body,
as `Ask` and `Tell` are in Appendix A. These eight cover the standard library:

```python
# effect_names.py
class Console: ...
class FileSystem: ...
class Network: ...
class Clock: ...
class Random: ...
class Environment: ...
class Process: ...
class Unknown: ...
```

One question decides whether something deserves a name: would a test replace it?
A test replaces the clock, the network, and the file system.
No test replaces `len()`.
A finer vocabulary would make the rows unreadable and the table below unmaintainable.

Appendix A lists three answers to the question of what untracked code performs.
This checker takes the third, a separate declaration,
because the first two are wrong for `print()`.
It writes to the console,
and calling it `Unknown` would put `Unknown` in nearly every row.
The declaration cannot go on the function.
A builtin has no `__annotations__` and no `__dict__` in which to store one,
so `print.__annotations__ = {}` raises an `AttributeError`.
The declarations therefore live in a table:

```python
# effect_table.py
from fnmatch import fnmatchcase
from typing import Final
from effect_names import (
    Clock,
    Console,
    Environment,
    FileSystem,
    Network,
    Process,
    Random,
    Unknown,
)

type Row = frozenset[str]
type Table = dict[str, Row]

def names(*effects: type) -> Row:
    return frozenset(e.__name__ for e in effects)

PURE: Final[Row] = names()
UNKNOWN: Final[Row] = names(Unknown)
STDLIB: Final[Table] = {
    "builtins.print": names(Console),
    "builtins.input": names(Console),
    "builtins.open": names(FileSystem),
    "builtins.eval": UNKNOWN,
    "builtins.exec": UNKNOWN,
    "builtins.*": PURE,
    "pathlib.Path": PURE,
    "pathlib.Path.with_*": PURE,
    "pathlib.Path.*": names(FileSystem),
    "time.time": names(Clock),
    "time.sleep": names(Clock),
    "time.perf_counter": names(Clock),
    "datetime.datetime.now": names(Clock),
    "random.*": names(Random),
    "os.environ.*": names(Environment),
    "os.getenv": names(Environment),
    "os.path.join": PURE,
    "os.*": names(FileSystem),
    "socket.*": names(Network),
    "urllib.request.*": names(Network),
    "subprocess.*": names(Process),
    "ast.*": PURE,
    "fnmatch.*": PURE,
    "itertools.*": PURE,
    "functools.*": PURE,
    "math.*": PURE,
    "typing.*": PURE,
}

def lookup(name: str, table: Table) -> Row:
    for pattern, row in table.items():
        if fnmatchcase(name, pattern):
            return row
    return UNKNOWN
```

A key is an `fnmatch` pattern,
and `lookup()` returns the row of the first pattern that matches.
Because a dictionary keeps insertion order,
a specific name goes above the glob that would otherwise match it.
`"os.path.join"` is pure, and the `"os.*"` below it is `FileSystem`.
Whole modules take one line each, which keeps the table short.
A name that matches nothing is `UNKNOWN`.
Because the table lists pure modules explicitly,
leaving a module out can add an `Unknown` and can never hide an Effect.

The key is the name as a programmer imports it,
because a function's own attributes report its name unreliably.
`os.remove.__module__` is `nt` on Windows and `posix` elsewhere,
`open.__module__` is `_io`,
and `random.random` reports `None` for its module and `Random.random` for its qualified name.
The checker reads source, and in source the name is `os.remove`.

Because `names()` builds a row from classes,
a typing mistake in the table is an error `ty` reports.
A `Row` is a `frozenset[str]` because the checker never imports the code it reads.
In source text, `performs(Ask)` is the name `Ask`.

```python
# test_effect_table.py
import pytest
from effect_table import STDLIB, UNKNOWN, lookup, names

@pytest.mark.parametrize(
    "name, expected",
    [
        ("builtins.print", {"Console"}),
        ("builtins.len", set()),
        ("pathlib.Path.read_text", {"FileSystem"}),
        ("pathlib.Path.with_suffix", set()),
        ("time.time", {"Clock"}),
        ("os.path.join", set()),
        ("os.remove", {"FileSystem"}),
        ("requests.get", {"Unknown"}),
    ],
)
def test_first_matching_pattern_wins(
    name: str, expected: set[str]
) -> None:
    assert lookup(name, STDLIB) == expected

def test_unlisted_name_is_unknown_not_pure() -> None:
    assert lookup("anything.at_all", {}) == UNKNOWN

def test_names_reads_class_names() -> None:
    class Ask: ...
    assert names(Ask) == {"Ask"}
```

## From a Call to a Name

Every call in a syntax tree has a `func` expression,
and this listing turns that expression into a dotted name the table can match:

```python
# call_names.py
import ast
import builtins
from typing import Final
from record import record

UNRESOLVED: Final[str] = "?"
LITERALS: Final[dict[type[ast.expr], str]] = {
    ast.List: "builtins.list",
    ast.ListComp: "builtins.list",
    ast.Dict: "builtins.dict",
    ast.DictComp: "builtins.dict",
    ast.Set: "builtins.set",
    ast.SetComp: "builtins.set",
    ast.Tuple: "builtins.tuple",
    ast.JoinedStr: "builtins.str",
}

def top_of(name: str) -> str:
    return name.split(".")[0]

def imports_of(tree: ast.Module) -> dict[str, str]:
    found: dict[str, str] = {}
    for node in ast.walk(tree):
        match node:
            case ast.Import(names=aliases):
                for a in aliases:
                    top = top_of(a.name)
                    full = a.name if a.asname else top
                    found[a.asname or top] = full
            case ast.ImportFrom(
                module=str(module), names=aliases
            ):
                for a in aliases:
                    full = f"{module}.{a.name}"
                    found[a.asname or a.name] = full
    return found

def dotted(node: ast.expr) -> list[str]:
    match node:
        case ast.Name(id=name):
            return [name]
        case ast.Attribute(value=value, attr=attr):
            head = dotted(value)
            return [*head, attr] if head else []
        case _:
            return []

@record
class Scope:
    module: str
    names: dict[str, str]
    defined: frozenset[str]
    types: dict[str, str]

    def name(self, name: str) -> str:
        if name in self.types:
            return UNRESOLVED
        if name in self.names:
            return self.names[name]
        if name in self.defined:
            return f"{self.module}.{name}"
        if hasattr(builtins, name):
            return f"builtins.{name}"
        return UNRESOLVED

    def annotation(self, node: ast.expr) -> str:
        match node:
            case ast.Subscript(value=value, slice=inner):
                outer = self.annotation(value)
                if outer == "typing.Final":
                    return self.annotation(inner)
                return outer
        match dotted(node):
            case [head, *rest]:
                return ".".join([self.name(head), *rest])
            case _:
                return UNRESOLVED

    def type_of(self, node: ast.expr) -> str:
        match node:
            case ast.Constant(value=str()):
                return "builtins.str"
            case ast.Name(id=name) if name in self.types:
                return self.types[name]
            case ast.Name(id=name):
                return self.name(name)
            case ast.Call(func=func):
                return self.callee(func)
            case _:
                return LITERALS.get(type(node), UNRESOLVED)

    def callee(self, func: ast.expr) -> str:
        match func:
            case ast.Name(id=name):
                return self.name(name)
            case ast.Attribute(value=value, attr=attr):
                if top_of(ast.unparse(func)) in self.names:
                    return self.annotation(func)
                receiver = self.type_of(value)
                if receiver == UNRESOLVED:
                    return UNRESOLVED
                return f"{receiver}.{attr}"
            case _:
                return UNRESOLVED
```

`imports_of()` and `dotted()` are [class patterns](13_Techniques--Pattern_Matching.md#class-patterns)
over `ast` nodes.
[*Composite* and *Interpreter*](34_Patterns--Composite_and_Interpreter.md#interpreter)
notes that the standard library walks these trees with `ast.NodeVisitor`,
in the style of [*Visitor*](33_Patterns--Visitor.md).
The node types are a closed set,
so `match` does the same work with no class to subclass.
`dotted()` is the smallest example.
It is recursive, as the tree is.
`os.path.join` is an `Attribute` whose value is an `Attribute` whose value is a `Name`.

A `Scope` holds the names the checker has collected at one point in a file.
`names` maps a local name to its full one, so `rm` becomes `os.remove`.
`defined` holds the functions and classes the module defines.
`types` maps a variable to the name of its type.
`name()` tries those in the order Python does, then `builtins`.
A name found in `types` is a variable,
and calling a variable calls whatever value it holds at runtime.
The source does not name that value, so `name()` answers `UNRESOLVED`.

`callee()` handles the two shapes a resolvable call takes.
A bare name goes to `name()`.
An attribute is either a path through an import, such as `time.sleep`,
or a method on a receiver.
`type_of()` finds the receiver's type where the source makes it evident:
a string constant, one of the literals in `LITERALS`,
a variable the scope has a type for, or a call,
which takes its callee's name as its type.
`p = Path(name)` therefore gives `p` the type `pathlib.Path`,
and `p.read_text()` becomes `pathlib.Path.read_text`,
which a pattern in the table matches.

`annotation()` reads a written type.
It drops the subscript from `list[str]` and looks through `Final[...]` to the type inside.

```python
# test_call_names.py
import ast
import pytest
from call_names import UNRESOLVED, Scope, imports_of

def test_imports_map_local_names_to_full_names() -> None:
    tree = ast.parse(
        "import os\n"
        "import os.path as p\n"
        "from os import remove as rm\n"
    )
    assert imports_of(tree) == {
        "os": "os",
        "p": "os.path",
        "rm": "os.remove",
    }

def callee(call: str, types: dict[str, str]) -> str:
    names = {"rm": "os.remove", "time": "time"}
    scope = Scope("m", names, frozenset({"local"}), types)
    node = ast.parse(call, mode="eval").body
    assert isinstance(node, ast.Call)
    return scope.callee(node.func)

@pytest.mark.parametrize(
    "call, expected",
    [
        ("rm(x)", "os.remove"),
        ("time.sleep(1)", "time.sleep"),
        ("local()", "m.local"),
        ("print(x)", "builtins.print"),
        ("', '.join(xs)", "builtins.str.join"),
        ("[].append(1)", "builtins.list.append"),
        ("dict.fromkeys(xs)", "builtins.dict.fromkeys"),
        ("p.read_text()", "pathlib.Path.read_text"),
        ("action(x)", UNRESOLVED),
        ("q.anything()", UNRESOLVED),
        ("f()()", UNRESOLVED),
    ],
)
def test_callee(call: str, expected: str) -> None:
    types = {"p": "pathlib.Path", "action": UNRESOLVED}
    assert callee(call, types) == expected
```

The last three cases are the limits.
`action(x)` calls a parameter, `q.anything()` has a receiver of no known type,
and `f()()` calls the result of a call.
Each comes back `UNRESOLVED`.

## Facts About a Function

The checker needs three facts about a function: the row it declares,
the Effects it hides, and the names it calls.
Hiding is this appendix's one addition to Appendix A's notation:

```python
# effect_marks.py
from record import record

@record
class Hides:
    effects: frozenset[type]

def hides(*effects: type) -> Hides:
    return Hides(frozenset(effects))
```

`ask()` in Appendix A declares `Ask` and calls `input()`,
which performs `Console`.
Both are true, and [The Check](#the-check) shows the checker reporting each.
`Annotated[str, performs(Ask), hides(Console)]` states that `ask()` is the boundary where `Console` becomes `Ask`.
The checker removes `Console` from the body's row and checks nothing about the claim,
as `ty` trusts a `cast()`.
`hides()` is the third line of Appendix A's rule, "the Effects f handles,"
in the weakest form you can write without handlers.
The annotation also puts two pieces of metadata in one `Annotated`,
the arrangement PEP 593 exists to allow.
`row()` from Appendix A skips the `Hides` object it does not recognize.

```python
# function_facts.py
import ast
from typing import TypeIs
from call_names import UNRESOLVED, Scope, imports_of
from effect_table import PURE, Row
from record import record
from result import Err, Ok, Result

type Def = ast.FunctionDef | ast.AsyncFunctionDef

@record
class Facts:
    name: str
    declared: Row | None
    hidden: Row
    calls: tuple[str, ...]

def marked(func: Def, marker: str) -> Row | None:
    match func.returns:
        case ast.Subscript(
            value=ast.Name(id="Annotated"),
            slice=ast.Tuple(elts=[_, *extras]),
        ):
            for extra in extras:
                match extra:
                    case ast.Call(
                        func=ast.Name(id=found), args=args
                    ) if found == marker:
                        return frozenset(
                            a.id
                            for a in args
                            if isinstance(a, ast.Name)
                        )
    return None

def assigned(
    body: list[ast.stmt], scope: Scope
) -> dict[str, str]:
    types: dict[str, str] = {}
    nodes = (n for stmt in body for n in ast.walk(stmt))
    for node in nodes:
        match node:
            case ast.AnnAssign(
                target=ast.Name(id=name), annotation=note
            ):
                types[name] = scope.annotation(note)
            case ast.Assign(
                targets=[ast.Name(id=name)], value=value
            ):
                types.setdefault(name, scope.type_of(value))
    return types

def parameters(
    func: Def, scope: Scope, owner: str
) -> dict[str, str]:
    args = func.args
    every = args.posonlyargs + args.args + args.kwonlyargs
    types = {
        arg.arg: scope.annotation(arg.annotation)
        if arg.annotation
        else UNRESOLVED
        for arg in every
    }
    if owner and args.args:
        types[args.args[0].arg] = owner
    return types

def calls_in(
    body: list[ast.stmt], scope: Scope
) -> tuple[str, ...]:
    return tuple(
        scope.callee(node.func)
        for stmt in body
        for node in ast.walk(stmt)
        if isinstance(node, ast.Call)
    )

def function_facts(
    func: Def, base: Scope, owner: str
) -> Facts:
    types = (
        base.types
        | parameters(func, base, owner)
        | assigned(func.body, base)
    )
    scope = Scope(
        base.module, base.names, base.defined, types
    )
    return Facts(
        f"{owner or base.module}.{func.name}",
        marked(func, "performs"),
        marked(func, "hides") or PURE,
        calls_in(func.body, scope),
    )

def is_function(node: ast.stmt) -> TypeIs[Def]:
    kinds = ast.FunctionDef | ast.AsyncFunctionDef
    return isinstance(node, kinds)

def is_def(
    node: ast.stmt,
) -> TypeIs[Def | ast.ClassDef]:
    if isinstance(node, ast.ClassDef):
        return True
    return is_function(node)

def module_scope(module: str, tree: ast.Module) -> Scope:
    defined = frozenset(
        node.name for node in tree.body if is_def(node)
    )
    bare = Scope(module, imports_of(tree), defined, {})
    aliases = {
        node.name.id: bare.annotation(node.value)
        for node in tree.body
        if isinstance(node, ast.TypeAlias)
    }
    named = Scope(module, bare.names | aliases, defined, {})
    top = [node for node in tree.body if not is_def(node)]
    types = assigned(top, named)
    return Scope(module, named.names, defined, types)

def class_facts(
    node: ast.ClassDef, base: Scope
) -> list[Facts]:
    owner = f"{base.module}.{node.name}"
    methods = [
        function_facts(m, base, owner)
        for m in node.body
        if is_function(m)
    ]
    init = f"{owner}.__init__"
    built = tuple(m.name for m in methods if m.name == init)
    return [*methods, Facts(owner, None, PURE, built)]

def facts_of(module: str, tree: ast.Module) -> list[Facts]:
    base = module_scope(module, tree)
    found: list[Facts] = []
    for node in tree.body:
        if is_function(node):
            found.append(function_facts(node, base, ""))
        elif isinstance(node, ast.ClassDef):
            found += class_facts(node, base)
    top = [node for node in tree.body if not is_def(node)]
    name = f"{module}.<module>"
    calls = calls_in(top, base)
    return [*found, Facts(name, None, PURE, calls)]

def read_module(
    module: str, source: str
) -> Result[list[Facts], str]:
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return Err(f"{module}: line {e.lineno}: {e.msg}")
    return Ok(facts_of(module, tree))
```

`marked()` is one nested pattern.
It matches a return annotation of the form `Annotated[T, ...]`,
binds everything after `T` to `extras`,
and returns the argument names of the first call to `marker`.
The guard, `if found == marker`, compares a captured name with a parameter,
which a pattern alone cannot do.
For a function with no such annotation, `marked()` returns `None`,
which means "inferred."
An empty row means "pure," so the two must differ.
`Row | None` is an ordinary optional, with no assertion anywhere to unwrap it.

`parameters()` and `assigned()` fill a scope's `types`: an annotated parameter,
the first parameter of a method (the class), an annotated assignment,
and a plain assignment whose right side has an evident type.
`module_scope()` does the same for a module's top level,
and also reads each `type` statement,
so a parameter annotated `Table` resolves to `builtins.dict`.
Because `is_function()` and `is_def()` return [`TypeIs`](08_Foundations--Static_Types.md#type-narrowing),
a comprehension filtered by one yields nodes whose narrowed type has a `name`.

`facts_of()` records every function, every method under `module.Class.method`,
and each class under its own name.
The class's entry holds a call to its `__init__()` when the class defines one,
so `Log()` performs what `Log.__init__()` performs.
The module's top-level statements become a function named `module.<module>`.
It is never checked, because it is the program's edge,
and its inferred row says what running the file performs.

`read_module()` is the one operation here that can fail.
It returns a `Result` from [Error Handling](42_Functional--Error_Handling.md#a-result-type),
so a parse failure becomes a value the caller must look at.

```python
# test_function_facts.py
from function_facts import Facts, read_module
from result import Err, Ok

SOURCE = '''
from pathlib import Path
from typing import Annotated, Final

type Names = list[str]
LIMIT: Final[dict[str, int]] = {}

class Log:
    def __init__(self) -> None:
        print("open")

    def write(self, text: str) -> None:
        self.flush()

    def flush(self) -> None: ...

def save(
    p: Path, names: Names
) -> Annotated[None, performs(FileSystem), hides(Console)]:
    log = Log()
    log.write(", ".join(names))
    names.sort()
    LIMIT.get("x")
    p.write_text("")
'''

def facts() -> dict[str, Facts]:
    match read_module("m", SOURCE):
        case Ok(found):
            return {f.name: f for f in found}
        case Err(problem):
            raise AssertionError(problem)

def test_every_def_and_the_module_get_facts() -> None:
    assert sorted(facts()) == [
        "m.<module>",
        "m.Log",
        "m.Log.__init__",
        "m.Log.flush",
        "m.Log.write",
        "m.save",
    ]

def test_a_class_calls_its_init() -> None:
    assert facts()["m.Log"].calls == ("m.Log.__init__",)

def test_self_resolves_to_the_class() -> None:
    assert facts()["m.Log.write"].calls == ("m.Log.flush",)

def test_receivers_resolve_five_ways() -> None:
    assert facts()["m.save"].calls == (
        "m.Log",
        "m.Log.write",
        "builtins.str.join",
        "builtins.list.sort",
        "builtins.dict.get",
        "pathlib.Path.write_text",
    )

def test_both_markers_are_read() -> None:
    save = facts()["m.save"]
    assert save.declared == {"FileSystem"}
    assert save.hidden == {"Console"}

def test_a_syntax_error_comes_back_as_a_value() -> None:
    result = read_module("bad", "def f(:\n")
    assert isinstance(result, Err)
    assert result.error.startswith("bad: line 1")
```

`test_receivers_resolve_five_ways()` shows the receiver rules together.
In `save()`, `log` gets its type from a constructor call,
the string by being a constant, `names` through a `type` alias,
`LIMIT` through `Final[...]`, and `p` by its annotation.

## Rows to a Fixed Point

Appendix A's rule is recursive.
A function's row needs its callees' rows, which need theirs.
Two functions that call each other make the recursion circular.
The standard answer is to start every row empty and apply the rule until nothing changes:

```python
# infer_rows.py
from effect_table import Row, Table, lookup
from function_facts import Facts

type Rows = dict[str, Row]

def call_row(call: str, rows: Rows, table: Table) -> Row:
    if call in rows:
        return rows[call]
    return lookup(call, table)

def body_row(facts: Facts, rows: Rows, table: Table) -> Row:
    found = (call_row(c, rows, table) for c in facts.calls)
    return frozenset().union(*found)

def step(
    known: dict[str, Facts], rows: Rows, table: Table
) -> Rows:
    return {
        name: facts.declared
        if facts.declared is not None
        else body_row(facts, rows, table)
        for name, facts in known.items()
    }

def infer(known: dict[str, Facts], table: Table) -> Rows:
    rows: Rows = dict.fromkeys(known, frozenset())
    while (new := step(known, rows, table)) != rows:
        rows = new
    return rows
```

`step()` is a pure function from one set of rows to the next.
A declared row passes through unchanged, which is how callers come to trust it.
An undeclared row becomes the union of what its calls perform.
`infer()` is the loop.
The walrus operator from [Control Flow](04_Foundations--Control_Flow.md)
lets the `while` condition compute the next rows and compare them in one expression.
Each step can add members to a row and cannot remove one,
and the vocabulary is finite, so the loop ends.

```python
# test_infer_rows.py
from effect_table import PURE, STDLIB
from function_facts import Facts
from infer_rows import infer

def known(*facts: Facts) -> dict[str, Facts]:
    return {f.name: f for f in facts}

def test_rows_propagate_up_the_call_chain() -> None:
    rows = infer(
        known(
            Facts("m.a", None, PURE, ("m.b",)),
            Facts("m.b", None, PURE, ("m.c",)),
            Facts("m.c", None, PURE, ("builtins.print",)),
        ),
        STDLIB,
    )
    assert rows["m.a"] == {"Console"}

def test_mutual_recursion_reaches_a_fixed_point() -> None:
    calls = ("m.even", "time.time")
    rows = infer(
        known(
            Facts("m.even", None, PURE, ("m.odd",)),
            Facts("m.odd", None, PURE, calls),
        ),
        STDLIB,
    )
    assert rows["m.even"] == rows["m.odd"] == {"Clock"}

def test_a_declared_row_is_trusted_by_callers() -> None:
    declared = frozenset({"Ask"})
    calls = ("builtins.input",)
    rows = infer(
        known(
            Facts("m.ask", declared, PURE, calls),
            Facts("m.greet", None, PURE, ("m.ask",)),
        ),
        STDLIB,
    )
    assert rows["m.greet"] == {"Ask"}
```

The tests build `Facts` by hand.
Because nothing in `infer_rows.py` reads source text,
testing it requires no source text.

## The Check

```python
# row_check.py
from effect_table import STDLIB, Table
from function_facts import Facts, read_module
from infer_rows import Rows, body_row, infer
from record import record
from result import Err, Ok

@record
class Finding:
    where: str
    problem: str

@record
class Report:
    rows: Rows
    findings: list[Finding]

def undeclared(
    facts: Facts, rows: Rows, table: Table
) -> list[Finding]:
    if facts.declared is None:
        return []
    body = body_row(facts, rows, table) - facts.hidden
    return [
        Finding(facts.name, f"undeclared {effect}")
        for effect in sorted(body - facts.declared)
    ]

def check(
    sources: dict[str, str], table: Table = STDLIB
) -> Report:
    known: dict[str, Facts] = {}
    findings: list[Finding] = []
    for module, source in sources.items():
        match read_module(module, source):
            case Ok(found):
                known |= {f.name: f for f in found}
            case Err(problem):
                findings.append(Finding(module, problem))
    rows = infer(known, table)
    for facts in known.values():
        findings += undeclared(facts, rows, table)
    return Report(rows, findings)
```

`check()` takes source text in a dictionary and a table, and returns a `Report`.
Because it reads no file and prints nothing,
every test of it is a string in and a value out.
The `match` on `read_module()`'s result is where a parse failure becomes a finding,
beside the findings about rows.

Here is the checker on Appendix A's greeting program, with one function added:

```python
# greeting_check.py
from row_check import check

GREETING = '''
from typing import Annotated
from effect_rows import performs

class Ask: ...
class Tell: ...

def ask(prompt: str) -> Annotated[str, performs(Ask)]:
    return input(prompt)

def tell(message: str) -> Annotated[None, performs(Tell)]:
    print(message)

def greet() -> Annotated[None, performs(Ask, Tell)]:
    name: str = ask("What is your name? ")
    tell(f"Hello, {name}!")

def shout(message: str) -> None:
    tell(message.upper())

def quiet() -> Annotated[None, performs()]:
    shout("hi")
'''
report = check({"greeting": GREETING})
for name, row in report.rows.items():
    if row:
        print(name, sorted(row))
#: greeting.ask ['Ask']
#: greeting.tell ['Tell']
#: greeting.greet ['Ask', 'Tell']
#: greeting.shout ['Tell']
for finding in report.findings:
    print(finding.where, finding.problem)
#: greeting.ask undeclared Console
#: greeting.tell undeclared Console
#: greeting.quiet undeclared Tell
```

Appendix A's `row(shout)` read `[]`, because `shout()` declares nothing.
The checker infers `['Tell']` from the call to `tell()`.
`quiet()` declares itself pure and calls `shout()`,
and the checker reports `quiet()`,
two calls away from the `print()` that `tell()` makes.
That is propagation, the thing Appendix A's `tracked_greeting.py` could not do.

[Facts About a Function](#facts-about-a-function)
predicted the first two findings.
`ask()` and `tell()` perform `Console` and say `Ask` and `Tell`.
Adding `hides(Console)` to each clears both findings, as this test file shows:

```python
# test_row_check.py
from row_check import Finding, check

HEAD = "from typing import Annotated\n"

def findings(source: str) -> list[Finding]:
    return check({"m": HEAD + source}).findings

def test_an_undeclared_effect_is_a_finding() -> None:
    source = (
        "def f() -> Annotated[None, performs()]:\n"
        "    print('hi')\n"
    )
    assert findings(source) == [
        Finding("m.f", "undeclared Console")
    ]

def test_a_declared_effect_is_not() -> None:
    source = (
        "def f() -> Annotated[None, performs(Console)]:\n"
        "    print('hi')\n"
    )
    assert findings(source) == []

def test_hides_removes_an_effect_from_the_body() -> None:
    source = (
        "def f() -> Annotated[\n"
        "    None, performs(Tell), hides(Console)\n"
        "]:\n"
        "    print('hi')\n"
    )
    assert findings(source) == []

def test_an_unannotated_function_is_inferred() -> None:
    report = check({"m": "def f():\n    print('hi')\n"})
    assert report.findings == []
    assert report.rows["m.f"] == {"Console"}

def test_an_unresolved_call_is_unknown() -> None:
    source = (
        "def f(action) -> Annotated[None, performs()]:\n"
        "    action()\n"
    )
    assert findings(source) == [
        Finding("m.f", "undeclared Unknown")
    ]

def test_a_broken_module_is_a_finding() -> None:
    report = check({"bad": "def f(:\n"})
    assert [f.where for f in report.findings] == ["bad"]
```

## Effects for Code You Don't Own

The table covers the standard library with patterns.
A third-party library needs the other form, a *stub*:
source text in this appendix's own notation,
passed to `check()` under the library's module name.

```python
# third_party_stub.py
from row_check import check

APP = '''
import requests
from typing import Annotated
from effect_names import Network
from effect_rows import performs

def fetch(url: str) -> Annotated[str, performs(Network)]:
    return requests.get(url).text
'''
STUB = '''
from typing import Annotated
from effect_names import Network
from effect_rows import performs

def get(
    url: str,
) -> Annotated[object, performs(Network)]: ...
'''

def problems(sources: dict[str, str]) -> list[str]:
    return [f.problem for f in check(sources).findings]

print(problems({"app": APP}))
#: ['undeclared Unknown']
print(problems({"app": APP, "requests": STUB}))
#: []
```

Without the stub, `requests.get` matches nothing in the table and reads `Unknown`,
so `fetch()` draws a finding.
With it, `requests.get` is a declared function like any other.
The checker's existing rule covers `requests.get`: callers trust a declared row.
The stub's body is `...`, which calls nothing,
so its body row is empty and stays within its declaration.
Type checkers solved the same problem the same way,
with stub files that declare the types of code they cannot read.

## The Checker Checks Itself

Every function in the checker so far is pure.
This listing is the edge,
the one place the checker reads a file or writes to the console.
Each of its functions declares the row it performs:

```python
# check_files.py
from pathlib import Path
from typing import Annotated
from effect_names import Console, FileSystem
from effect_rows import performs
from row_check import Report, check

def read(
    path: Path,
) -> Annotated[str, performs(FileSystem)]:
    return path.read_text(encoding="utf-8")

def load(
    paths: list[Path],
) -> Annotated[dict[str, str], performs(FileSystem)]:
    return {path.stem: read(path) for path in paths}

def show(
    report: Report,
) -> Annotated[None, performs(Console)]:
    for name in report.rows:
        if row := report.rows[name]:
            print(name, sorted(row))
    for finding in report.findings:
        print("!", finding.where, finding.problem)

FILES = [
    "effect_table.py",
    "call_names.py",
    "function_facts.py",
    "infer_rows.py",
    "row_check.py",
    "check_files.py",
    "../utils/result.py",
]
show(check(load([Path(name) for name in FILES])))
#: check_files.read ['FileSystem']
#: check_files.load ['FileSystem']
#: check_files.show ['Console']
#: check_files.<module> ['Console', 'FileSystem']
#: result.Ok.bind ['Unknown']
```

The demo runs the checker on six of its own source files and on `utils/result.py`,
and prints every nonempty row.
Because the output names no function from `effect_table.py`, `call_names.py`,
`function_facts.py`, `infer_rows.py`, or `row_check.py`,
the checker confirms that its core is pure.
`FileSystem` and `Console` appear in three functions at the edge and in the module that calls them.
[Effect Management](44_Effects--Effect_Management.md#a-program-can-never-be-pure)
calls that arrangement pushing the Effects to the edges,
and here a tool verifies it.

The one `Unknown` is `Ok.bind()`, which calls the function it receives.
That call is the callback problem of [Effect Tracking](A_Effect_Tracking.md#propagate-through-callbacks),
appearing in a class from this book.

Reaching that output took four changes to the checker's own code.
`imports_of()` called `a.name.split(".")` on a loop variable,
which has no written type,
so `top_of()` now takes the name as an annotated parameter.
`body_row()` called `PURE.union()`, a method on an imported constant,
and now calls `frozenset().union()`.
`type_of()` called `self.types.get()`, a method on a record's field,
and now tests `name in self.types` in a pattern's guard.
`load()` called `path.read_text()` inside a comprehension,
and now calls `read(path)`.
Each change is small, and two of them improved the code.
All four are what the tool requires.
You write for it as you write for a type checker,
with types where it needs them.

## What the Checker Resolves, and What It Cannot See

The resolution rules span three listings.
Here, in one place, is what the checker resolves:

- A bare name, through the module's imports, then its own definitions,
  then `builtins`.
- A dotted name whose head is an import, such as `time.sleep` or `requests.get`.
- A method on a receiver whose type is written: an annotated parameter,
  an annotated assignment, the first parameter of a method,
  a module-level constant (through `Final[...]`),
  or a `type` alias defined in the same module.
- A method on a receiver whose type is evident: a string, an f-string, a list,
  dictionary, set, or tuple literal, a list, dictionary, or set comprehension,
  or a local assigned from a call, which takes the callee's name as its type.
- A method called on a class, such as `dict.fromkeys()`.
- A class call, which performs what the class's `__init__()` performs when it defines one.

Every limit below produces `Unknown`,
so each one appears in a row instead of going unreported:

- A call of a parameter, or of a local that holds a function.
- A call of a call's result, as in `dataclass(frozen=True)(cls)`.
- A method on a loop variable, on a name captured by a pattern,
  or on a record's field.
- A receiver annotated with a union,
  or with a `type` alias imported from another module.
- An inherited method, because the checker reads no class hierarchy.

Four limits produce no `Unknown`,
and a production tool would need to remove them.
The checker finds `Annotated` and `performs` by those names,
so a declaration written with `typing.Annotated` or an `as` alias goes unread.
A decorator that wraps a function changes what calling it performs,
and the checker reads the undecorated body.
The first parameter of every method gets the class as its type,
which is wrong for a `staticmethod`.
The checker trusts `hides()` without evidence.

Cleverness removes none of these, because each one is a piece of type inference.
Appendix A's argument holds: past this point you are writing a type checker.
This appendix shows how much tracking needs no type inference.
Name resolution, a table of the standard library,
and a fixed point give every function in a program a row.
They verified the architecture of the program that computes the rows.
