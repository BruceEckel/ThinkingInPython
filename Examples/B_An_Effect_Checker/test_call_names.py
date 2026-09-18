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
