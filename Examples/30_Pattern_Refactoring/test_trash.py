# test_trash.py
from pathlib import Path
import pytest
from parse_trash import parse
from trash import Aluminum, Cardboard, Glass, Paper, Trash, sum_value

def test_subclasses_self_register() -> None:
    assert set(Trash.registry) == {
        "Aluminum", "Paper", "Glass", "Cardboard"}

def test_create_builds_by_name() -> None:
    t = Trash.create("Aluminum", 2.0)
    assert isinstance(t, Aluminum)
    assert t.weight == 2.0

def test_per_pound_values() -> None:
    assert Aluminum.value == 1.67
    assert Paper.value == 0.10
    assert Glass.value == 0.23
    assert Cardboard.value == 0.79

def test_sum_value_totals_weight_times_value() -> None:
    items: list[Trash] = [Aluminum(2.0), Paper(5.0)]
    assert sum_value(items) == pytest.approx(3.84)  # 2*1.67 + 5*0.10

def test_parse_reads_and_skips_comments(tmp_path: Path) -> None:
    data = tmp_path / "trash.dat"
    data.write_text("""\
# header
Aluminum:2.0

Glass:3.0
""")
    items = parse(str(data))
    assert [type(t).__name__ for t in items] == ["Aluminum", "Glass"]
    assert items[0].weight == 2.0
    assert items[1].weight == 3.0
