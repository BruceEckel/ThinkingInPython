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
