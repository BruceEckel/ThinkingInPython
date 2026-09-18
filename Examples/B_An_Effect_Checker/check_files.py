# check_files.py
from pathlib import Path
from typing import Annotated
from effect_names import Console, FileSystem
from effect_rows import performs
from row_check import Report, check

def read(
    path: Path,
) -> Annotated[str, performs(FileSystem)]:
    return path.read_text(encoding="utf-8")

def load(
    paths: list[Path],
) -> Annotated[dict[str, str], performs(FileSystem)]:
    return {path.stem: read(path) for path in paths}

def show(
    report: Report,
) -> Annotated[None, performs(Console)]:
    for name in report.rows:
        if row := report.rows[name]:
            print(name, sorted(row))
    for finding in report.findings:
        print("!", finding.where, finding.problem)

FILES = [
    "effect_table.py",
    "call_names.py",
    "function_facts.py",
    "infer_rows.py",
    "row_check.py",
    "check_files.py",
    "../utils/result.py",
]
show(check(load([Path(name) for name in FILES])))
#: check_files.read ['FileSystem']
#: check_files.load ['FileSystem']
#: check_files.show ['Console']
#: check_files.<module> ['Console', 'FileSystem']
#: result.Ok.bind ['Unknown']
