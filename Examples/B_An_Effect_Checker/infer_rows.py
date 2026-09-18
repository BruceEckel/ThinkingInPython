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
