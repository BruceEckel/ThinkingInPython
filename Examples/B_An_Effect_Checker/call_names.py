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
