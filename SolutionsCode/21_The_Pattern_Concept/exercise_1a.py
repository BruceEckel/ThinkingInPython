# exercise_1a.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Row:
    name: str
    amount: int

def render(rows: list[Row], style: str) -> str:
    match style:
        case "text":
            return "\n".join(f"{r.name}: {r.amount}" for r in rows)
        case "csv":
            return "\n".join(f"{r.name},{r.amount}" for r in rows)
        case _:
            raise ValueError(f"unknown style {style!r}")

rows = [Row("pens", 3), Row("paper", 7)]
print(render(rows, "csv"))
#: pens,3
#: paper,7
