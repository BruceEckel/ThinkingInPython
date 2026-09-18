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
