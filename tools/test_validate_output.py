"""Tests for tools/validate_output.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from validate_output import (
    block_slug,
    collect_files,
    decode_output,
    encode_output,
    exec_capture,
    is_marker,
    main,
    parse_chunks,
    process_block,
    process_file,
    process_markdown,
    strip_trailing,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ── is_marker ─────────────────────────────────────────────────────────────────

def test_is_marker_bare() -> None:
    assert is_marker("#:\n")

def test_is_marker_with_content() -> None:
    assert is_marker("#: Hello\n")

def test_is_marker_no_trailing_newline() -> None:
    assert is_marker("#: Hello")

def test_is_marker_bare_no_newline() -> None:
    assert is_marker("#:")

def test_is_marker_space_only_after_hashes() -> None:
    # "#: " with nothing after counts as a marker (empty content line)
    assert is_marker("#: \n")

def test_is_marker_no_space_is_not_marker() -> None:
    # #:content without a separating space is not a marker
    assert not is_marker("#:content\n")

def test_is_marker_indented_not_marker() -> None:
    assert not is_marker("    #: Hello\n")

def test_is_marker_tab_indented_not_marker() -> None:
    assert not is_marker("\t#: Hello\n")

def test_is_marker_single_hash_not_marker() -> None:
    assert not is_marker("# comment\n")

def test_is_marker_regular_code_not_marker() -> None:
    assert not is_marker('print("hello")\n')

def test_is_marker_empty_line_not_marker() -> None:
    assert not is_marker("\n")

def test_is_marker_blank_not_marker() -> None:
    assert not is_marker("   \n")


# ── parse_chunks ──────────────────────────────────────────────────────────────

def test_parse_chunks_empty() -> None:
    assert parse_chunks([]) == []

def test_parse_chunks_code_only() -> None:
    lines = ['print("hi")\n', "x = 1\n"]
    assert parse_chunks(lines) == [("code", [0, 1])]

def test_parse_chunks_output_only() -> None:
    lines = ["#: Hello\n", "#: world\n"]
    assert parse_chunks(lines) == [("output", [0, 1])]

def test_parse_chunks_code_then_output() -> None:
    lines = ['print("hi")\n', "#: hi\n"]
    assert parse_chunks(lines) == [("code", [0]), ("output", [1])]

def test_parse_chunks_output_then_code() -> None:
    lines = ["#: hi\n", 'print("hi")\n']
    assert parse_chunks(lines) == [("output", [0]), ("code", [1])]

def test_parse_chunks_interleaved() -> None:
    lines = [
        'print("a")\n',  # 0
        "#: a\n",        # 1
        'print("b")\n',  # 2
        "#: b\n",        # 3
    ]
    assert parse_chunks(lines) == [
        ("code", [0]),
        ("output", [1]),
        ("code", [2]),
        ("output", [3]),
    ]

def test_parse_chunks_consecutive_markers_grouped() -> None:
    lines = ['print("a")\n', 'print("b")\n', "#: a\n", "#: b\n"]
    assert parse_chunks(lines) == [("code", [0, 1]), ("output", [2, 3])]

def test_parse_chunks_consecutive_code_grouped() -> None:
    lines = ["#: a\n", "x = 1\n", "y = 2\n", "#: done\n"]
    assert parse_chunks(lines) == [
        ("output", [0]),
        ("code", [1, 2]),
        ("output", [3]),
    ]

def test_parse_chunks_indented_hash_is_code() -> None:
    # Indented #: is code, not output
    lines = ["def f():\n", "    #: comment\n", "    pass\n"]
    assert parse_chunks(lines) == [("code", [0, 1, 2])]


# ── decode_output ─────────────────────────────────────────────────────────────

def test_decode_output_single_line() -> None:
    assert decode_output(["#: Hello\n"], [0]) == "Hello\n"

def test_decode_output_bare_marker_is_empty_line() -> None:
    assert decode_output(["#:\n"], [0]) == "\n"

def test_decode_output_multiple_lines() -> None:
    lines = ["#: Hello\n", "#: world\n"]
    assert decode_output(lines, [0, 1]) == "Hello\nworld\n"

def test_decode_output_empty_line_in_middle() -> None:
    lines = ["#: Hello\n", "#:\n", "#: world\n"]
    assert decode_output(lines, [0, 1, 2]) == "Hello\n\nworld\n"

def test_decode_output_empty_indices() -> None:
    assert decode_output([], []) == ""

def test_decode_output_marker_without_newline() -> None:
    assert decode_output(["#: Hello"], [0]) == "Hello\n"

def test_decode_output_content_with_spaces() -> None:
    assert decode_output(["#: hello world\n"], [0]) == "hello world\n"

def test_decode_output_content_with_special_chars() -> None:
    assert decode_output(["#: {'key': 42}\n"], [0]) == "{'key': 42}\n"


# ── encode_output ─────────────────────────────────────────────────────────────

def test_encode_output_single_line() -> None:
    assert encode_output("Hello\n") == ["#: Hello\n"]

def test_encode_output_empty_string() -> None:
    assert encode_output("") == []

def test_encode_output_multiple_lines() -> None:
    assert encode_output("Hello\nworld\n") == ["#: Hello\n", "#: world\n"]

def test_encode_output_empty_line_in_middle() -> None:
    assert encode_output("Hello\n\nworld\n") == [
        "#: Hello\n",
        "#:\n",
        "#: world\n",
    ]

def test_encode_output_bare_newline() -> None:
    assert encode_output("\n") == ["#:\n"]

def test_encode_output_strips_trailing_space() -> None:
    # print(i, end=" ") output: no trailing space in the marker line.
    assert encode_output("0 1 2 \n") == ["#: 0 1 2\n"]

def test_encode_output_preserves_leading_space() -> None:
    assert encode_output("  indented\n") == ["#:   indented\n"]


# ── strip_trailing ────────────────────────────────────────────────────────────

def test_strip_trailing_per_line() -> None:
    assert strip_trailing("a \nb  \n") == "a\nb\n"

def test_strip_trailing_keeps_leading() -> None:
    assert strip_trailing("  a \n") == "  a\n"

def test_strip_trailing_empty() -> None:
    assert strip_trailing("") == ""

def test_encode_output_trailing_blank_line_preserved() -> None:
    # removesuffix('\n') strips exactly one newline, so a trailing
    # blank line in the output (Hello\n\n) is preserved as #:
    assert encode_output("Hello\n\n") == ["#: Hello\n", "#:\n"]


# ── encode / decode round-trip ────────────────────────────────────────────────

@pytest.mark.parametrize("output", [
    "Hello\n",
    "Hello\nworld\n",
    "Hello\n\nworld\n",
    "\n",
    "a\nb\nc\n",
    "{'x': 1}\n",
])
def test_roundtrip(output: str) -> None:
    encoded = encode_output(output)
    indices = list(range(len(encoded)))
    assert decode_output(encoded, indices) == output


# ── exec_capture ──────────────────────────────────────────────────────────────

def test_exec_capture_basic() -> None:
    out, exc = exec_capture('print("hello")', "<test>", {})
    assert out == "hello\n"
    assert exc is None

def test_exec_capture_empty_output() -> None:
    out, exc = exec_capture("x = 1 + 1", "<test>", {})
    assert out == ""
    assert exc is None

def test_exec_capture_multiline_output() -> None:
    out, exc = exec_capture('print("a")\nprint("b")\n', "<test>", {})
    assert out == "a\nb\n"
    assert exc is None

def test_exec_capture_exception_is_returned() -> None:
    out, exc = exec_capture('raise ValueError("oops")', "<test>", {})
    assert isinstance(exc, ValueError)
    assert str(exc) == "oops"

def test_exec_capture_partial_output_before_exception() -> None:
    src = 'print("before")\nraise RuntimeError("boom")'
    out, exc = exec_capture(src, "<test>", {})
    assert out == "before\n"
    assert isinstance(exc, RuntimeError)

def test_exec_capture_restores_stdout_after_exception() -> None:
    original = sys.stdout
    exec_capture("raise ValueError()", "<test>", {})
    assert sys.stdout is original

def test_exec_capture_restores_stdout_on_success() -> None:
    original = sys.stdout
    exec_capture('print("hi")', "<test>", {})
    assert sys.stdout is original

def test_exec_capture_namespace_shared_across_calls() -> None:
    ns: dict = {}
    exec_capture("x = 42", "<test>", ns)
    out, exc = exec_capture("print(x)", "<test>", ns)
    assert out == "42\n"
    assert exc is None

def test_exec_capture_populates_namespace() -> None:
    ns: dict = {}
    exec_capture("y = 'hello'", "<test>", ns)
    assert ns["y"] == "hello"

def test_exec_capture_syntax_error_returned() -> None:
    out, exc = exec_capture("def (", "<test>", {})
    assert isinstance(exc, SyntaxError)


# ── process_file ──────────────────────────────────────────────────────────────

def test_no_markers_returns_none(tmp_path: Path) -> None:
    p = write(tmp_path, "ex.py", 'print("hello")\n')
    assert process_file(p, update=False) is None

def test_blank_file_returns_none(tmp_path: Path) -> None:
    p = write(tmp_path, "ex.py", "\n\n")
    assert process_file(p, update=False) is None

def test_correct_single_marker(tmp_path: Path) -> None:
    p = write(tmp_path, "ex.py", 'print("hello")\n#: hello\n')
    assert process_file(p, update=False) is True

def test_wrong_single_marker(tmp_path: Path) -> None:
    p = write(tmp_path, "ex.py", 'print("hello")\n#: goodbye\n')
    assert process_file(p, update=False) is False

def test_multiple_segments_all_correct(tmp_path: Path) -> None:
    p = write(tmp_path, "ex.py",
              'print("a")\n#: a\nprint("b")\n#: b\n')
    assert process_file(p, update=False) is True

def test_multiple_segments_second_wrong(tmp_path: Path) -> None:
    p = write(tmp_path, "ex.py",
              'print("a")\n#: a\nprint("b")\n#: WRONG\n')
    assert process_file(p, update=False) is False

def test_update_rewrites_wrong_marker(tmp_path: Path) -> None:
    p = write(tmp_path, "ex.py", 'print("hello")\n#: goodbye\n')
    assert process_file(p, update=True) is True
    assert p.read_text(encoding="utf-8") == 'print("hello")\n#: hello\n'

def test_update_does_not_change_correct_file(tmp_path: Path) -> None:
    content = 'print("hello")\n#: hello\n'
    p = write(tmp_path, "ex.py", content)
    process_file(p, update=True)
    assert p.read_text(encoding="utf-8") == content

def test_update_rewrites_all_wrong_segments(tmp_path: Path) -> None:
    p = write(tmp_path, "ex.py",
              'print("a")\n#: X\nprint("b")\n#: Y\n')
    process_file(p, update=True)
    assert p.read_text(encoding="utf-8") == (
        'print("a")\n#: a\nprint("b")\n#: b\n'
    )

def test_exec_error_returns_false(tmp_path: Path) -> None:
    p = write(tmp_path, "ex.py", 'raise ValueError("oops")\n#: x\n')
    assert process_file(p, update=False) is False

def test_exec_error_in_update_leaves_file_unchanged(
    tmp_path: Path,
) -> None:
    content = 'raise ValueError("oops")\n#: x\n'
    p = write(tmp_path, "ex.py", content)
    process_file(p, update=True)
    assert p.read_text(encoding="utf-8") == content

def test_indented_hash_not_treated_as_marker(tmp_path: Path) -> None:
    content = (
        "def foo() -> None:\n"
        "    #: just a comment\n"
        '    print("hi")\n'
        "\n"
        "foo()\n"
        "#: hi\n"
    )
    p = write(tmp_path, "ex.py", content)
    assert process_file(p, update=False) is True

def test_namespace_carries_across_segments(tmp_path: Path) -> None:
    content = (
        "x = 10\n"
        "print(x)\n"
        "#: 10\n"
        "print(x * 2)\n"
        "#: 20\n"
    )
    p = write(tmp_path, "ex.py", content)
    assert process_file(p, update=False) is True

def test_function_defined_then_called(tmp_path: Path) -> None:
    content = (
        "def greet(name: str) -> str:\n"
        '    return f"Hello, {name}!"\n'
        "\n"
        'print(greet("World"))\n'
        "#: Hello, World!\n"
    )
    p = write(tmp_path, "ex.py", content)
    assert process_file(p, update=False) is True

def test_multiline_output_all_markers_required(tmp_path: Path) -> None:
    content = (
        "for i in range(3):\n"
        "    print(i)\n"
        "#: 0\n"
        "#: 1\n"
        "#: 2\n"
    )
    p = write(tmp_path, "ex.py", content)
    assert process_file(p, update=False) is True

def test_empty_output_line_in_middle(tmp_path: Path) -> None:
    content = (
        'print("a")\n'
        "print()\n"
        'print("b")\n'
        "#: a\n"
        "#:\n"
        "#: b\n"
    )
    p = write(tmp_path, "ex.py", content)
    assert process_file(p, update=False) is True

def test_update_expands_single_wrong_marker_to_multiline(
    tmp_path: Path,
) -> None:
    content = "for i in range(3):\n    print(i)\n#: WRONG\n"
    p = write(tmp_path, "ex.py", content)
    process_file(p, update=True)
    assert p.read_text(encoding="utf-8") == (
        "for i in range(3):\n    print(i)\n#: 0\n#: 1\n#: 2\n"
    )

def test_no_output_code_with_marker_is_wrong(tmp_path: Path) -> None:
    # Code that produces no stdout; any #: content is a mismatch
    p = write(tmp_path, "ex.py", "x = 1 + 1\n#: something\n")
    assert process_file(p, update=False) is False

def test_update_removes_marker_when_no_output(tmp_path: Path) -> None:
    # encode_output('') == [] so the #: line disappears
    p = write(tmp_path, "ex.py", "x = 1 + 1\n#: stale\n")
    process_file(p, update=True)
    assert p.read_text(encoding="utf-8") == "x = 1 + 1\n"

def test_output_marker_before_any_code_is_wrong(tmp_path: Path) -> None:
    # #: at the start with no preceding code - actual output is ''
    p = write(tmp_path, "ex.py", "#: something\nprint('hi')\n")
    assert process_file(p, update=False) is False

def test_correct_multipart_with_mixed_output(tmp_path: Path) -> None:
    content = (
        'name = "Alice"\n'
        'print(f"Hello, {name}")\n'
        "#: Hello, Alice\n"
        "print(name.upper())\n"
        "#: ALICE\n"
    )
    p = write(tmp_path, "ex.py", content)
    assert process_file(p, update=False) is True


# ── collect_files ─────────────────────────────────────────────────────────────

def test_collect_files_single_py_file(tmp_path: Path) -> None:
    p = write(tmp_path, "ex.py", "")
    assert collect_files([p]) == [p]

def test_collect_files_non_py_excluded(tmp_path: Path) -> None:
    txt = tmp_path / "readme.txt"
    txt.write_text("hello")
    assert collect_files([txt]) == []

def test_collect_files_directory_finds_py_files(tmp_path: Path) -> None:
    a = write(tmp_path, "a.py", "")
    b = write(tmp_path, "b.py", "")
    assert set(collect_files([tmp_path])) == {a, b}

def test_collect_files_recursive(tmp_path: Path) -> None:
    sub = tmp_path / "sub"
    sub.mkdir()
    a = write(tmp_path, "a.py", "")
    b = write(sub, "b.py", "")
    assert set(collect_files([tmp_path])) == {a, b}

def test_collect_files_directory_excludes_non_py(tmp_path: Path) -> None:
    a = write(tmp_path, "a.py", "")
    (tmp_path / "notes.txt").write_text("x")
    assert collect_files([tmp_path]) == [a]

def test_collect_files_mixed_file_and_dir(tmp_path: Path) -> None:
    a = write(tmp_path, "a.py", "")
    sub = tmp_path / "sub"
    sub.mkdir()
    b = write(sub, "b.py", "")
    assert set(collect_files([a, sub])) == {a, b}

def test_collect_files_empty_list() -> None:
    assert collect_files([]) == []

def test_collect_files_sorted_within_directory(tmp_path: Path) -> None:
    z = write(tmp_path, "z.py", "")
    a = write(tmp_path, "a.py", "")
    result = collect_files([tmp_path])
    assert result == [a, z]


# ── main() ────────────────────────────────────────────────────────────────────

def test_main_check_passes(tmp_path: Path) -> None:
    write(tmp_path, "ex.py", 'print("hi")\n#: hi\n')
    assert main([str(tmp_path)]) == 0

def test_main_check_fails(tmp_path: Path) -> None:
    write(tmp_path, "ex.py", 'print("hi")\n#: bye\n')
    assert main([str(tmp_path)]) == 1

def test_main_no_py_files_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    assert main([str(tmp_path)]) == 1
    assert "No .py or .md files found" in capsys.readouterr().out

def test_main_update_mode_rewrites_and_exits_0(tmp_path: Path) -> None:
    p = write(tmp_path, "ex.py", 'print("hi")\n#: bye\n')
    assert main(["--update", str(p)]) == 0
    assert p.read_text(encoding="utf-8") == 'print("hi")\n#: hi\n'

def test_main_skipped_files_exit_0(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    write(tmp_path, "ex.py", 'print("hi")\n')
    assert main([str(tmp_path)]) == 0
    assert "1 skipped" in capsys.readouterr().out

def test_main_verbose_prints_filenames(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    p = write(tmp_path, "ex.py", 'print("hi")\n#: hi\n')
    main(["-v", str(p)])
    assert "ex.py" in capsys.readouterr().out

def test_main_summary_counts(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    write(tmp_path, "ok.py", 'print("hi")\n#: hi\n')
    write(tmp_path, "bad.py", 'print("hi")\n#: bye\n')
    write(tmp_path, "skip.py", 'print("hi")\n')
    main([str(tmp_path)])
    out = capsys.readouterr().out
    assert "1 ok" in out
    assert "1 failed" in out
    assert "1 skipped" in out

def test_main_exec_error_exits_1(tmp_path: Path) -> None:
    write(tmp_path, "ex.py", "1/0\n#: x\n")
    assert main([str(tmp_path)]) == 1

def test_main_multiple_files_all_pass(tmp_path: Path) -> None:
    write(tmp_path, "a.py", 'print("a")\n#: a\n')
    write(tmp_path, "b.py", 'print("b")\n#: b\n')
    assert main([str(tmp_path)]) == 0

def test_main_multiple_files_one_fails(tmp_path: Path) -> None:
    write(tmp_path, "a.py", 'print("a")\n#: a\n')
    write(tmp_path, "b.py", 'print("b")\n#: WRONG\n')
    assert main([str(tmp_path)]) == 1


# ── block_slug ────────────────────────────────────────────────────────────────

def test_block_slug_simple() -> None:
    assert block_slug(["# trace.py\n", 'print("hi")\n']) == "trace.py"

def test_block_slug_subpath_normalized() -> None:
    assert block_slug(["# mouse/Move.py\n"]) == "mouse/Move.py"

def test_block_slug_none_when_no_path_line() -> None:
    assert block_slug(['print("hi")\n', "#: hi\n"]) is None

def test_block_slug_skips_leading_blank_lines() -> None:
    assert block_slug(["\n", "# a.py\n"]) == "a.py"

def test_block_slug_utils_prefix() -> None:
    assert block_slug(["# utils/display.py\n"]) == "utils/display.py"


# ── collect_files with .md ────────────────────────────────────────────────────

def test_collect_files_single_md_file(tmp_path: Path) -> None:
    p = write(tmp_path, "ch.md", "")
    assert collect_files([p]) == [p]

def test_collect_files_directory_finds_md_and_py(tmp_path: Path) -> None:
    a = write(tmp_path, "a.py", "")
    b = write(tmp_path, "b.md", "")
    assert set(collect_files([tmp_path])) == {a, b}


# ── process_markdown ──────────────────────────────────────────────────────────

def test_markdown_no_python_block_returns_none(tmp_path: Path) -> None:
    p = write(tmp_path, "ch.md", "# Heading\n\nProse here.\n")
    assert process_markdown(p, update=False) is None

def test_markdown_block_without_markers_returns_none(tmp_path: Path) -> None:
    p = write(tmp_path, "ch.md", "```python\nprint('hi')\n```\n")
    assert process_markdown(p, update=False) is None

def test_markdown_correct_marker_passes(tmp_path: Path) -> None:
    p = write(tmp_path, "ch.md", "```python\nprint('hi')\n#: hi\n```\n")
    assert process_markdown(p, update=False) is True

def test_markdown_wrong_marker_fails(tmp_path: Path) -> None:
    p = write(tmp_path, "ch.md", "```python\nprint('hi')\n#: bye\n```\n")
    assert process_markdown(p, update=False) is False

def test_markdown_update_rewrites_marker(tmp_path: Path) -> None:
    p = write(tmp_path, "ch.md", "```python\nprint('hi')\n#: bye\n```\n")
    assert process_markdown(p, update=True) is True
    assert p.read_text(encoding="utf-8") == (
        "```python\nprint('hi')\n#: hi\n```\n"
    )

def test_markdown_update_leaves_surrounding_prose(tmp_path: Path) -> None:
    src = (
        "# Title\n\nIntro.\n\n"
        "```python\nprint('a')\n#: X\n```\n\n"
        "Outro.\n"
    )
    p = write(tmp_path, "ch.md", src)
    process_markdown(p, update=True)
    assert p.read_text(encoding="utf-8") == (
        "# Title\n\nIntro.\n\n"
        "```python\nprint('a')\n#: a\n```\n\n"
        "Outro.\n"
    )

def test_markdown_py_fence_label_handled(tmp_path: Path) -> None:
    p = write(tmp_path, "ch.md", "```py\nprint('hi')\n#: hi\n```\n")
    assert process_markdown(p, update=False) is True

def test_markdown_non_python_fence_ignored(tmp_path: Path) -> None:
    # A #: line inside a non-python block is left alone (not a marker block).
    p = write(tmp_path, "ch.md", "```text\n#: not output\n```\n")
    assert process_markdown(p, update=False) is None

def test_markdown_multiple_blocks_independent(tmp_path: Path) -> None:
    src = (
        "```python\nx = 1\nprint(x)\n#: 1\n```\n\n"
        "```python\nprint('two')\n#: two\n```\n"
    )
    p = write(tmp_path, "ch.md", src)
    # The second block must not see ``x`` from the first.
    bad = src.replace("print('two')", "print(x)")
    pbad = write(tmp_path, "bad.md", bad)
    assert process_markdown(p, update=False) is True
    assert process_markdown(pbad, update=False) is False

def test_markdown_norun_inline_marker_skips(tmp_path: Path) -> None:
    # A block flagged no-run is never executed, so a wrong marker is left as is.
    src = "```python\n# extract: no-run\nwhile True:\n    pass\n#: x\n```\n"
    p = write(tmp_path, "ch.md", src)
    assert process_markdown(p, update=False) is True
    assert p.read_text(encoding="utf-8") == src

def test_markdown_exec_error_fails(tmp_path: Path) -> None:
    p = write(tmp_path, "ch.md", "```python\n1 / 0\n#: x\n```\n")
    assert process_markdown(p, update=False) is False

def test_markdown_trailing_space_marker_has_none(tmp_path: Path) -> None:
    # print(end=" ") output must not leave a trailing space in the marker.
    src = (
        "```python\nfor i in range(3):\n"
        "    print(i, end=' ')\nprint()\n#:\n```\n"
    )
    p = write(tmp_path, "ch.md", src)
    process_markdown(p, update=True)
    text = p.read_text(encoding="utf-8")
    assert "#: 0 1 2\n" in text
    assert "#: 0 1 2 \n" not in text

def test_markdown_clean_marker_with_trailing_output_passes(
    tmp_path: Path,
) -> None:
    # A clean #: marker validates against output that has a trailing space.
    src = (
        "```python\nfor i in range(3):\n"
        "    print(i, end=' ')\nprint()\n#: 0 1 2\n```\n"
    )
    p = write(tmp_path, "ch.md", src)
    assert process_markdown(p, update=False) is True

def test_markdown_block_runs_from_tree_dir(tmp_path: Path) -> None:
    # A block importing a sibling resolves it from build/examples/<chapter>/.
    chapter_dir = tmp_path / "tree" / "ch"
    chapter_dir.mkdir(parents=True)
    (chapter_dir / "helper.py").write_text(
        "VALUE = 42\n", encoding="utf-8"
    )
    src = (
        "```python\n# main.py\n"
        "from helper import VALUE\n"
        "print(VALUE)\n#: 42\n```\n"
    )
    p = write(tmp_path, "ch.md", src)
    assert process_markdown(
        p, update=False, tree=tmp_path / "tree"
    ) is True


# ── process_block ─────────────────────────────────────────────────────────────

def test_process_block_line_offset_in_diagnostics(
    capsys: pytest.CaptureFixture,
) -> None:
    process_block(
        ["print('hi')\n", "#: bye\n"], "<x>",
        update=False, line_offset=10,
    )
    # The #: marker is the second block line (index 1): 1 + 1 + 10 = 12.
    assert "line 12" in capsys.readouterr().out

def test_process_block_returns_new_lines() -> None:
    new_lines, ok, changed = process_block(
        ["print('hi')\n", "#: bye\n"], "<x>", update=True,
    )
    assert ok is True
    assert changed is True
    assert new_lines == ["print('hi')\n", "#: hi\n"]
