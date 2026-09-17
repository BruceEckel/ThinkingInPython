"""Tests for tools/record_check.py: @record where it fits, nowhere else."""
from pathlib import Path
import pytest
from tools import record_check
from tools.markdown import Document
from tools.record_check import (
    EXCEPTIONS_FILE, Exemption, exemptions, find, unused_exemptions)

REAL_EXEMPTIONS = exemptions  # Bound before the fixture patches it

RECORD_IMPORT = "from record import record\n"


def listing(slug: str, body: str) -> str:
    return f"```python\n# {slug}\n{body}```\n\n"


def doc(tmp_path: Path, text: str,
        name: str = "20_Patterns--Rethinking_Objects.md",
        tree: str = "Chapters") -> Document:
    directory = tmp_path / tree
    directory.mkdir(exist_ok=True)
    path = directory / name
    path.write_text(text, encoding="utf-8")
    return Document.parse(path)


def messages(document: Document) -> list[str]:
    return [f.message for f in find(document)]


@pytest.fixture(autouse=True)
def no_exemptions(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(record_check, "exemptions", lambda: ())


LONG = ("from dataclasses import dataclass\n\n"
        "@dataclass(frozen=True)\nclass Point:\n    x: int\n")


def test_long_form_with_no_base_is_reported(tmp_path: Path) -> None:
    d = doc(tmp_path, listing("point.py", LONG))
    [finding] = find(d)
    assert "Point is @dataclass(frozen=True) and could be @record" \
        in finding.message
    assert finding.line == 5  # The decorator's line in the Markdown


def test_record_is_clean(tmp_path: Path) -> None:
    body = RECORD_IMPORT + "\n@record\nclass Point:\n    x: int\n"
    assert messages(doc(tmp_path, listing("point.py", body))) == []


def test_other_dataclass_options_are_left_alone(tmp_path: Path) -> None:
    body = ("from dataclasses import dataclass\n\n"
            "@dataclass(frozen=True, order=True)\nclass V:\n    n: int\n\n"
            "@dataclass\nclass M:\n    n: int\n")
    assert messages(doc(tmp_path, listing("v.py", body))) == []


def test_chapters_before_18_are_out_of_scope(tmp_path: Path) -> None:
    d = doc(tmp_path, listing("point.py", LONG),
            name="12_Techniques--Data_Classes_as_Types.md")
    assert messages(d) == []


def test_chapter_18_starts_at_the_record_listing(tmp_path: Path) -> None:
    text = (listing("before.py", LONG)
            + listing("utils/record.py", "def record(cls): return cls\n")
            + listing("after.py", LONG.replace("Point", "Later")))
    d = doc(tmp_path, text, name="18_Techniques--Performance.md")
    assert [m.split(":")[0] for m in messages(d)] == ["after.py"]


def test_solutions_18_is_in_scope_from_the_top(tmp_path: Path) -> None:
    d = doc(tmp_path, listing("exercise_1.py", LONG),
            name="18_Techniques--Performance.md", tree="Solutions")
    assert len(messages(d)) == 1


def test_long_form_under_an_unslotted_base_is_clean(tmp_path: Path) -> None:
    body = ("from dataclasses import dataclass\n\n"
            "class Operators:\n    pass\n\n"
            "@dataclass(frozen=True)\nclass Num(Operators):\n    n: int\n")
    assert messages(doc(tmp_path, listing("expr.py", body))) == []


def test_record_under_an_unslotted_base_is_reported(tmp_path: Path) -> None:
    body = (RECORD_IMPORT + "\nclass Operators:\n    pass\n\n"
            "@record\nclass Num(Operators):\n    n: int\n")
    [message] = messages(doc(tmp_path, listing("expr.py", body)))
    assert "its base Operators declares no __slots__" in message


def test_record_under_a_library_ability_is_reported(tmp_path: Path) -> None:
    body = (RECORD_IMPORT + "from stateless import Ability\n\n"
            "@record\nclass Ask(Ability[str]):\n    prompt: str\n")
    [message] = messages(doc(tmp_path, listing("ask.py", body)))
    assert "its base Ability declares no __slots__" in message


def test_a_base_with_empty_slots_lets_the_record_stand(
        tmp_path: Path) -> None:
    body = (RECORD_IMPORT + "from abc import ABC\n\n"
            "class Shape(ABC):\n    __slots__ = ()\n\n"
            "@record\nclass Circle(Shape):\n    r: float\n")
    assert messages(doc(tmp_path, listing("shapes_oo.py", body))) == []


def test_a_record_base_counts_as_slotted(tmp_path: Path) -> None:
    body = ("from dataclasses import dataclass\n" + RECORD_IMPORT
            + "\n@record\nclass Deposit:\n    n: int\n\n"
            "@dataclass(frozen=True)\nclass Big(Deposit):\n    m: int\n")
    [message] = messages(doc(tmp_path, listing("bank.py", body)))
    assert message.startswith("bank.py: Big is @dataclass(frozen=True)")


def test_an_unknown_base_draws_no_finding(tmp_path: Path) -> None:
    body = ("from dataclasses import dataclass\n" + RECORD_IMPORT
            + "from elsewhere import Base\n\n"
            "@dataclass(frozen=True)\nclass A(Base):\n    n: int\n\n"
            "@record\nclass B(Base):\n    n: int\n")
    assert messages(doc(tmp_path, listing("unknown.py", body))) == []


def test_same_name_resolves_within_its_own_listing(tmp_path: Path) -> None:
    slotted = (RECORD_IMPORT + "\nclass Base:\n    __slots__ = ()\n\n"
               "@record\nclass A(Base):\n    n: int\n")
    unslotted = ("from dataclasses import dataclass\n\n"
                 "class Base:\n    pass\n\n"
                 "@dataclass(frozen=True)\nclass B(Base):\n    n: int\n")
    text = listing("one.py", slotted) + listing("two.py", unslotted)
    assert messages(doc(tmp_path, text)) == []


def test_an_unparseable_fragment_is_skipped(tmp_path: Path) -> None:
    text = "```python\n@dataclass(frozen=True)\nclass P:\n    ...\n  x\n```\n"
    assert messages(doc(tmp_path, text)) == []


def test_exemption_by_chapter_name_covers_both_trees(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(record_check, "exemptions", lambda: (
        Exemption("Rethinking_Objects", "point.py", "P*", 1),))
    for tree in ("Chapters", "Solutions"):
        assert messages(doc(tmp_path, listing("point.py", LONG),
                            tree=tree)) == []
    other = doc(tmp_path, listing("point.py", LONG),
                name="21_Patterns--Design_Patterns.md")
    assert len(messages(other)) == 1


def test_an_exemption_that_matches_nothing_is_reported(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(record_check, "exemptions", lambda: (
        Exemption("Rethinking_Objects", "point.py", "Point", 3),
        Exemption("Rethinking_Objects", "gone.py", "*", 4),))
    d = doc(tmp_path, listing("point.py", LONG))
    assert [f.line for f in unused_exemptions([d])] == [4]


def test_the_committed_exceptions_file_parses() -> None:
    entries = REAL_EXEMPTIONS.__wrapped__(EXCEPTIONS_FILE)
    assert entries and all(e.chapter and e.listing for e in entries)
