# test_row_check.py
from typing import Final
from row_check import Finding, Undeclared, Unparsed, check

HEAD: Final[str] = "from typing import Annotated\n"

def findings(source: str) -> list[Finding]:
    return check({"m": HEAD + source}).findings

def test_an_undeclared_effect_is_a_finding() -> None:
    source = (
        "def f() -> Annotated[None, performs()]:\n"
        "    print('hi')\n"
    )
    assert findings(source) == [
        Undeclared("m.f", "Console")
    ]

def test_a_declared_effect_is_no_finding() -> None:
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
        Undeclared("m.f", "Unknown")
    ]

def test_a_broken_module_is_a_finding() -> None:
    [finding] = check({"bad": "def f(:\n"}).findings
    assert isinstance(finding, Unparsed)
    assert finding.where == "bad"
