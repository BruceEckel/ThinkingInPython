# test_parse_trash.py
from pathlib import Path
from parse_trash import parse

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
