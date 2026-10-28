# row_check.py
from effect_table import STDLIB, Table
from function_facts import Facts, read_module
from infer_rows import Rows, body_row, infer
from record import record
from result import Err, Ok

type ModuleName = str

@record
class Undeclared:
    where: str
    effect: str

@record
class Unparsed:
    where: str
    message: str

type Finding = Undeclared | Unparsed

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
        Undeclared(facts.name, effect)
        for effect in sorted(body - facts.declared)
    ]

def check(
    sources: dict[ModuleName, str], table: Table = STDLIB
) -> Report:
    known: dict[str, Facts] = {}
    findings: list[Finding] = []
    for module, source in sources.items():
        match read_module(module, source):
            case Ok(found):
                known |= {f.name: f for f in found}
            case Err(problem):
                findings.append(Unparsed(module, problem))
    rows = infer(known, table)
    for facts in known.values():
        findings += undeclared(facts, rows, table)
    return Report(rows, findings)

# row_check.py (continued)
def describe(finding: Finding) -> str:
    match finding:
        case Undeclared(where, effect):
            return f"! {where} undeclared {effect}"
        case Unparsed(where, message):
            return f"! {where} {message}"

def lines(report: Report) -> list[str]:
    rows = [
        f"{name} {sorted(report.rows[name])}"
        for name in report.rows
        if report.rows[name]
    ]
    return rows + [describe(f) for f in report.findings]
