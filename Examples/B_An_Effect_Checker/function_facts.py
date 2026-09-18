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
