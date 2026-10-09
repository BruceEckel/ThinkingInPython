# local_types.py
import ast
from typing import TypeIs
from call_names import UNRESOLVED, Scope, imports_of

type Def = ast.FunctionDef | ast.AsyncFunctionDef

def assigned(
    body: list[ast.stmt], scope: Scope
) -> dict[str, str]:
    types: dict[str, str] = {}
    written: dict[str, str] = {}
    values: dict[ast.AST, str] = {}
    nodes = (n for stmt in body for n in ast.walk(stmt))
    for node in nodes:
        match node:
            case ast.AnnAssign(
                target=ast.Name(id=name), annotation=note
            ):
                written[name] = scope.annotation(note)
            case ast.Assign(targets=[target], value=value):
                values[target] = scope.type_of(value)
            case (
                ast.Name(id=name, ctx=ast.Store())
                | ast.MatchAs(name=str(name))
                | ast.MatchStar(name=str(name))
                | ast.ExceptHandler(name=str(name))
            ):
                found = values.get(node, UNRESOLVED)
                if types.setdefault(name, found) != found:
                    types[name] = UNRESOLVED
    return types | written

def parameters(
    func: Def, scope: Scope, owner: str
) -> dict[str, str]:
    args = func.args
    positional = args.posonlyargs + args.args
    every = positional + args.kwonlyargs
    types = {
        arg.arg: scope.annotation(arg.annotation)
        if arg.annotation
        else UNRESOLVED
        for arg in every
    }
    if owner and positional:
        types[positional[0].arg] = owner
    return types

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
    top = [
        node
        for node in tree.body
        if not is_def(node)
        and not isinstance(node, ast.TypeAlias)
    ]
    types = assigned(top, named)
    return Scope(module, named.names, defined, types)
