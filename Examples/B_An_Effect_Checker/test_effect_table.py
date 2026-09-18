# test_effect_table.py
import pytest
from effect_table import STDLIB, UNKNOWN, lookup, names

@pytest.mark.parametrize(
    "name, expected",
    [
        ("builtins.print", {"Console"}),
        ("builtins.len", set()),
        ("pathlib.Path.read_text", {"FileSystem"}),
        ("pathlib.Path.with_suffix", set()),
        ("time.time", {"Clock"}),
        ("os.path.join", set()),
        ("os.remove", {"FileSystem"}),
        ("requests.get", {"Unknown"}),
    ],
)
def test_first_matching_pattern_wins(
    name: str, expected: set[str]
) -> None:
    assert lookup(name, STDLIB) == expected

def test_unlisted_name_is_unknown_not_pure() -> None:
    assert lookup("anything.at_all", {}) == UNKNOWN

def test_names_reads_class_names() -> None:
    class Ask: ...
    assert names(Ask) == {"Ask"}
