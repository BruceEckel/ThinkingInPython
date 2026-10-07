# function_facts.py
import ast
from call_names import Scope
from effect_table import PURE, Row
from local_types import (Def, assigned, is_def, is_function,
                         module_scope, parameters)
from record import record
from result import Err, Ok, Result

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
