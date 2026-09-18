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
