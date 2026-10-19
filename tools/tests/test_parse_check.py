"""Tests for tools/parse_check.py, the machinery the parse checks share.

The spaCy half is stubbed: a parser that returns no sentences gives the
right paragraphs with nothing parsed, which is all the plumbing needs.
These tests cover the baseline file, the key form, the stale
computation, the printed report, the survey lines, the `--accept`
refusal, the unavailable-parser path, and the edit-pairs grouping on a
tiny in-memory pairs dict.
"""

import importlib
from collections.abc import Callable
from pathlib import Path
import pytest
from tools import parse_check
from tools.markdown import Document
from tools.parse_check import (
    Pairs,
    apply_baseline,
    build_arg_parser,
    calibrate_edit_pairs,
    edit_pair_sides,
    inside_quotes,
    key,
    load_baseline,
    parse_args,
    print_edit_pairs,
    print_rows,
    print_summary,
    print_survey,
    run,
    run_calibrate,
    skipped,
    write_baseline,
)
from tools.parsed_prose import Paragraph, ParserUnavailable, RawSentence
from tools.report import Finding
from tools.stranded_prepositions import display

HEADER = "# header one\n# header two\n"


def empty(texts: list[str]) -> list[list[RawSentence]]:
    return [[] for _ in texts]


def test_key_normalizes_whitespace() -> None:
    assert key("Chapters/a.md", "x  y\n z") == "Chapters/a.md\tx y z"


def test_baseline_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "base.txt"
    assert load_baseline(path) == set()
    write_baseline({"b\ttwo", "a\tone"}, path, HEADER)
    text = path.read_bytes().decode("utf-8")
    assert text == HEADER + "a\tone\nb\ttwo\n"
    assert b"\r" not in path.read_bytes()
    assert load_baseline(path) == {"a\tone", "b\ttwo"}


def test_load_skips_comments_and_blank_lines(tmp_path: Path) -> None:
    path = tmp_path / "base.txt"
    path.write_text("# c\n\n  \nkeep\tme\n", encoding="utf-8")
    assert load_baseline(path) == {"keep\tme"}


def test_apply_baseline_finds_new_and_stale() -> None:
    found = [("a.md", 3, "old hit"), ("a.md", 9, "fresh hit")]
    baseline = {key("a.md", "old hit"), key("a.md", "gone"),
                key("b.md", "elsewhere")}
    new, stale = apply_baseline(found, baseline, {"a.md"})
    assert new == [("a.md", 9, "fresh hit")]
    assert stale == [key("a.md", "gone")]


def test_print_rows_and_summary(
        capsys: pytest.CaptureFixture[str]) -> None:
    found = [("a.md", 3, "old hit"), ("a.md", 9, "fresh hit")]
    baseline = {key("a.md", "old hit"), key("a.md", "gone")}
    new, stale = apply_baseline(found, baseline, {"a.md"})
    print_rows(found, baseline, stale, show_all=False)
    print_summary(found, new, stale)
    assert capsys.readouterr().out == (
        "NEW      a.md:9: fresh hit\n"
        "stale    a.md: gone\n"
        "1 new, 1 accepted, 1 stale\n")
    print_rows(found, baseline, [], show_all=True)
    print_summary(found, new, [])
    assert capsys.readouterr().out == (
        "accepted a.md:3: old hit\n"
        "NEW      a.md:9: fresh hit\n"
        "1 new, 1 accepted\n")


def test_print_survey(capsys: pytest.CaptureFixture[str]) -> None:
    print_survey([("a.md", 2, "[AND] x")])
    assert capsys.readouterr().out == (
        "survey   a.md:2: [AND] x\n1 survey\n")


def test_inside_quotes_counts_from_start() -> None:
    text = 'say "hi" and "there'
    assert inside_quotes(text, text.index("there"))
    assert not inside_quotes(text, text.index("and"))
    assert not inside_quotes(text, text.index("hi") + 3, 4)


def test_skipped_labels() -> None:
    def para(text: str) -> Paragraph:
        return Paragraph(Path("x.md"), text, [1] * len(text), ())

    assert skipped(para("Hint: look here"))
    assert skipped(para("Done when: it works"))
    assert not skipped(para("A hint: look here"))


def test_parse_args_refuses_accept_with_paths(
        capsys: pytest.CaptureFixture[str]) -> None:
    ap = build_arg_parser("doc", fail_help="fail")
    with pytest.raises(SystemExit) as caught:
        parse_args(ap, ["--accept", "a.md"])
    assert caught.value.code == 2
    assert "give no paths" in capsys.readouterr().err
    assert parse_args(ap, ["--accept"]).accept


def test_survey_tool_parser_has_no_accept() -> None:
    ap = build_arg_parser("doc", baselined=False, fail_help="fail")
    args = parse_args(ap, ["a.md", "--fail"])
    assert args.fail and args.paths == ["a.md"]
    with pytest.raises(SystemExit):
        parse_args(ap, ["--accept"])


def fake_finder(
    path_messages: list[tuple[int, str]],
) -> Callable[[list[Document]], list[Finding]]:
    def find_docs(docs: list[Document]) -> list[Finding]:
        return [Finding(docs[0].path, line, text)
                for line, text in path_messages]

    return find_docs


def test_run_reports_accepts_and_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    prose = tmp_path / "a.md"
    prose.write_text("Some prose.\n", encoding="utf-8")
    base = tmp_path / "base.txt"
    finder = fake_finder([(4, "[X] one"), (2, "[X] two")])
    ap = build_arg_parser("doc", fail_help="fail", survey_help="s")
    args = parse_args(ap, [str(prose), "--fail"])
    assert run("t", args, finder, baseline=base, header=HEADER) == 1
    shown = display(prose)
    assert capsys.readouterr().out == (
        f"NEW      {shown}:2: [X] two\n"
        f"NEW      {shown}:4: [X] one\n"
        "2 new, 0 accepted\n")
    write_baseline({key(shown, "[X] one")}, base, HEADER)
    assert run("t", args, finder, baseline=base, header=HEADER) == 1
    assert "1 new, 1 accepted" in capsys.readouterr().out
    write_baseline({key(shown, "[X] one"), key(shown, "[X] two"),
                    key(shown, "[X] stale")}, base, HEADER)
    assert run("t", args, finder, baseline=base, header=HEADER) == 0
    assert capsys.readouterr().out == (
        f"stale    {shown}: [X] stale\n0 new, 2 accepted, 1 stale\n")


def test_run_accept_rewrites_the_baseline(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    prose = tmp_path / "a.md"
    prose.write_text("Some prose.\n", encoding="utf-8")
    base = tmp_path / "base.txt"
    shown = display(prose)
    write_baseline({key(shown, "[X] stale")}, base, HEADER)
    ap = build_arg_parser("doc", fail_help="fail")
    args = parse_args(ap, [str(prose)])
    args.accept = True
    finder = fake_finder([(1, "[X] fresh")])
    assert run("t", args, finder, baseline=base, header=HEADER) == 0
    assert capsys.readouterr().out == (
        f"Baseline: added 1, dropped 1 stale, in {display(base)}\n")
    assert base.read_text(encoding="utf-8") == (
        HEADER + f"{key(shown, '[X] fresh')}\n")


@pytest.mark.parametrize("survey_last", [False, True])
def test_run_prints_survey_hits_apart(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
    survey_last: bool,
) -> None:
    prose = tmp_path / "a.md"
    prose.write_text("Some prose.\n", encoding="utf-8")
    base = tmp_path / "base.txt"
    finder = fake_finder([(1, "[MAIN] a"), (2, "[SUB] b")])
    ap = build_arg_parser("doc", fail_help="fail", survey_help="s")

    def run_with(extra: list[str]) -> str:
        args = parse_args(ap, [str(prose), *extra])
        code = run("t", args, finder, baseline=base, header=HEADER,
                   is_survey=lambda m: m.startswith("[SUB]"),
                   survey_last=survey_last)
        assert code == 0
        return capsys.readouterr().out

    shown = display(prose)
    quiet = run_with([])
    assert quiet == f"NEW      {shown}:1: [MAIN] a\n1 new, 0 accepted\n"
    loud = run_with(["--survey"])
    row = f"survey   {shown}:2: [SUB] b\n1 survey\n"
    new = f"NEW      {shown}:1: [MAIN] a\n"
    summary = "1 new, 0 accepted\n"
    assert loud == (new + summary + row if survey_last
                    else new + row + summary)


def test_run_reports_an_unavailable_parser(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    prose = tmp_path / "a.md"
    prose.write_text("Some prose.\n", encoding="utf-8")

    def gone(docs: list[Document]) -> list[Finding]:
        raise ParserUnavailable("uv: command not found")

    ap = build_arg_parser("doc", fail_help="fail")
    args = parse_args(ap, [str(prose), "--fail"])
    assert run("name", args, gone, baseline=tmp_path / "b.txt",
               header=HEADER) == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == (
        "name: parser unavailable (uv: command not found); "
        "nothing checked\n")


def test_run_calibrate_survives_a_missing_parser(
        capsys: pytest.CaptureFixture[str]) -> None:
    def gone(parser: parse_check.Parser) -> None:
        raise ParserUnavailable("no network")

    assert run_calibrate("name", gone, empty) == 0
    assert "name: parser unavailable (no network)" in (
        capsys.readouterr().err)


PAIRS: Pairs = {
    "p1": {"before": "old way", "after": "new way", "previous": ""},
    "p2": {"before": "old again", "after": "old still",
           "previous": "Lead sentence."},
    "p3": {"before": "plain", "after": "new thing", "previous": ""},
}


def labels_of(paras: list[Paragraph], skip: int) -> set[str]:
    text = " ".join(p.text for p in paras)
    return {word.upper() for word in ("old", "new") if word in text}


def test_edit_pair_sides_prepends_previous_only_when_asked() -> None:
    seen: list[list[str]] = []

    def spy(texts: list[str]) -> list[list[RawSentence]]:
        seen.append(texts)
        return empty(texts)

    sides = edit_pair_sides(PAIRS, spy, labels_of, previous=False)
    assert seen[0] == ["old way", "new way", "old again", "old still",
                       "plain", "new thing"]
    assert sides["p1.before.md"] == {"OLD"}
    assert sides["p1.after.md"] == {"NEW"}
    seen.clear()
    edit_pair_sides(PAIRS, spy, labels_of, previous=True)
    assert seen[0][:3] == ["x", "old way", "new way"]
    assert "Lead sentence. old again" in seen[0]


def test_print_edit_pairs_groups_by_label(
        capsys: pytest.CaptureFixture[str]) -> None:
    sides = edit_pair_sides(PAIRS, empty, labels_of, previous=False)
    print_edit_pairs(PAIRS, sides, {"OLD": "the old word", "NEW": ""},
                     previous=False, meanings=False, summary=False)
    out = capsys.readouterr().out
    assert out.splitlines()[0] == "== OLD =="
    assert "before only: p1\n  before: old way\n  after:  new way\n" in out
    assert "both: p2\n" in out
    assert "OLD: before-only 1, both 1, after-only 0, of 3 pairs\n" in out
    assert "NEW: before-only 0, both 0, after-only 2, of 3 pairs\n" in out
    assert "after only: p1" in out and "after only: p3" in out


def test_calibrate_edit_pairs_prints_previous_and_summary(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(parse_check, "load_edit_pairs", lambda: PAIRS)
    extra = Document.from_text("old example", Path("calibrate/ex0.md"))
    sides = calibrate_edit_pairs(
        empty, {"OLD": "the old word", "NEW": "the new word"},
        labels_of, previous=True, summary=True, extra_docs=[extra])
    out = capsys.readouterr().out
    assert "== OLD: the old word ==" in out
    assert "  previous: Lead sentence.\n  before:   old again\n" in out
    assert out.rstrip().endswith(
        "Summary (before-only/both/after-only, of 3 pairs): "
        "OLD 1/1/0; NEW 0/0/2")
    assert sides["ex0.md"] == {"OLD"}


@pytest.mark.parametrize("name", parse_check.PROSE_CHECKS)
def test_prose_checks_are_importable_baselined_checks(name: str) -> None:
    module = importlib.import_module(name)
    assert callable(module.main)
    assert isinstance(module.BASELINE, Path)
    assert isinstance(module.HEADER, str)
