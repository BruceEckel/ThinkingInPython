"""Tests for tools/solution_steps.py (solutions folded into steps)."""
from pathlib import Path

from tools.markdown import Document
from tools.solution_steps import (
    DIAGNOSIS,
    Flat,
    apply,
    shape,
    split_hint,
    steps,
    unwrap,
    wrap,
)


def doc(text: str) -> Document:
    return Document.from_text(text, Path("Solutions/30_Demo/README.md"))


def rendered(text: str) -> str:
    lines, _ = apply(doc(text))
    return "\n".join(lines)


LISTING = """\
# exercise_3.py
from collections.abc import Callable

type Responder[T] = Callable[[T], None]
LIMIT: int = 3

class Broadcaster[T]:
    "Fan-out to callables."
    def __init__(self) -> None:
        self._responders: list[Responder[T]] = []

    def connect(self, responder: Responder[T]) -> None:
        self._responders.append(responder)

    @property
    def count(self) -> int: return len(self._responders)

def helper(n: int) -> int:
    return n + 1

received: list[int] = []
b = Broadcaster[int]()
b.connect(received.append)
print(received)
#: []
"""

SHAPE = """\
from collections.abc import Callable

type Responder[T] = Callable[[T], None]
LIMIT: int = 3

class Broadcaster[T]:
    "Fan-out to callables."
    def __init__(self) -> None:
        ...

    def connect(self, responder: Responder[T]) -> None:
        ...

    @property
    def count(self) -> int: ...

def helper(n: int) -> int:
    ..."""


def test_shape_keeps_declarations_and_elides_bodies() -> None:
    assert "\n".join(shape(LISTING.splitlines()) or []) == SHAPE


def test_shape_drops_the_demonstration_and_its_markers() -> None:
    text = "\n".join(shape(LISTING.splitlines()) or [])
    assert "received" not in text
    assert "#:" not in text


def test_shape_is_none_without_a_body_to_elide() -> None:
    assert shape(["# a.py", "x = 1", "print(x)"]) is None
    assert shape(["# a.py", "class P:", "    def f(self) -> None: ..."]) is None


def test_shape_is_none_for_unparseable_code() -> None:
    assert shape(["# a.py", "def (:"]) is None


def test_a_long_string_constant_is_elided_to_its_name() -> None:
    quote = '"""'
    listing = ["# a.py", "from typing import Final", "",
               "MAZE: Final[str] = " + quote, "###", "#_#", "#.#", "###",
               quote + ".strip()",
               "SHORT: Final[str] = " + quote, "ab", quote,
               "def f() -> None:", "    return None"]
    out = shape(listing) or []
    assert "MAZE: Final[str] = ..." in out
    assert "###" not in out
    assert "SHORT: Final[str] = " + quote in out
    assert out[-2:] == ["def f() -> None:", "    ..."]


def test_an_assignment_a_kept_line_reads_stays() -> None:
    listing = ["# a.py", "import sys", "from typing import Final", "",
               "monitoring = sys.monitoring",
               "TOOL: Final[int] = monitoring.PROFILER_ID",
               "helper = len",
               "def f(n: int) -> int:", "    return helper(n)",
               "count = f(3)", "print(count)"]
    out = shape(listing) or []
    assert "monitoring = sys.monitoring" in out
    assert "helper = len" not in out  # Read only in an elided body.
    assert "count = f(3)" not in out


def test_a_one_line_body_too_wide_for_the_ellipsis_breaks() -> None:
    sig = "def a_function_with_a_much_longer_name(args: int) -> int:"
    assert len(sig) + len(" ...") > 60
    out = shape(["# a.py", sig + " return argument"])
    assert out == [sig, "    ..."]


FLAT = """\
# Demo: Solutions

## 3. Title

> Do the thing.

Hint: Look at the broadcaster section.
Use `connect()`.

The approach.

```python
# exercise_3.py
def f(n: int) -> int:
    return n
```

```python
# test_f.py
from exercise_3 import f

def test_f() -> None:
    assert f(1) == 1
```

Discussion.

## 4. Other

> Do another thing.

Plain answer, no hint.
"""

NESTED = """\
# Demo: Solutions

## 3. Title

> Do the thing.

<details>
<summary>Where to look</summary>

Look at the broadcaster section.
Use `connect()`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
def f(n: int) -> int:
    ...
```

<details>
<summary>Solution</summary>

The approach.

```python
# exercise_3.py
def f(n: int) -> int:
    return n
```

```python
# test_f.py
from exercise_3 import f

def test_f() -> None:
    assert f(1) == 1
```

Discussion.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 4. Other

> Do another thing.

Plain answer, no hint.
"""


def test_a_hint_paragraph_nests_the_section() -> None:
    assert rendered(FLAT) == NESTED


def test_the_nested_form_is_a_fixed_point() -> None:
    assert rendered(NESTED) == NESTED
    _, changed = apply(doc(NESTED))
    assert changed == []


def test_a_section_without_a_hint_is_left_alone() -> None:
    text = FLAT.split("## 3. Title")[0] + NESTED.split("</details>\n\n")[-1]
    assert rendered(text) == text


def test_unwrap_restores_the_flat_form() -> None:
    body = NESTED.split("> Do the thing.\n")[1].split("## 4.")[0]
    flat = unwrap(body.split("\n"))
    assert flat.hint == ["Look at the broadcaster section.",
                         "Use `connect()`."]
    assert flat.rest[0] == "The approach."
    assert flat.rest[-1] == "Discussion."
    assert "The shape of" not in "\n".join(flat.rest)


def test_a_test_listing_gets_no_shape() -> None:
    assert "The shape of test_f.py" not in rendered(FLAT)


def test_no_shape_step_when_no_listing_has_a_body() -> None:
    flat = Flat(["Hint."], ["```python", "# a.py", "x = 1", "```"])
    out = wrap(flat)
    assert "<summary>The shape</summary>" not in out
    assert out.count("<details>") == 2
    assert out[-2:] == ["</details>", "</details>"]


def test_steps_follow_the_ladder() -> None:
    body = NESTED.split("> Do the thing.\n")[1].split("## 4.")[0]
    ladder = steps(unwrap(body.split("\n")))
    assert [s.label for s in ladder] == ["Where to look", "The shape",
                                         "Solution"]
    assert ladder[1].lines[1] == "# The shape of exercise_3.py"
    assert steps(Flat([], ["Answer."])) == [
        type(ladder[0])("Solution", ["Answer."])]


def test_the_solution_step_ends_with_the_diagnosis() -> None:
    lines = rendered(FLAT).split("\n")
    close = lines.index("</details>")
    assert tuple(lines[close - 3:close - 1]) == DIAGNOSIS
    assert lines[close - 1] == ""
    assert rendered(FLAT).count(DIAGNOSIS[0]) == 1


def test_steps_end_the_solution_with_the_diagnosis() -> None:
    body = NESTED.split("> Do the thing.\n")[1].split("## 4.")[0]
    solution = steps(unwrap(body.split("\n")))[-1]
    assert tuple(solution.lines[-2:]) == DIAGNOSIS
    assert solution.lines[-4:-2] == ["Discussion.", ""]


FLAT_DONE = FLAT.replace(
    "Use `connect()`.\n\n",
    "Use `connect()`.\n\nDone when: `test_f.py` passes.\n\n", 1)

NESTED_DONE = NESTED.replace(
    "<details>\n<summary>Solution</summary>",
    "<details>\n<summary>Done when</summary>\n\n"
    "`test_f.py` passes.\n\n"
    "<details>\n<summary>Solution</summary>", 1).replace(
    "</details>\n</details>\n</details>\n",
    "</details>\n</details>\n</details>\n</details>\n", 1)


def test_a_done_when_paragraph_becomes_a_step() -> None:
    assert rendered(FLAT_DONE) == NESTED_DONE


def test_the_done_when_step_nests_between_shape_and_solution() -> None:
    lines = NESTED_DONE.split("\n")
    summaries = [line for line in lines if line.startswith("<summary>")]
    assert summaries == ["<summary>Where to look</summary>",
                         "<summary>The shape</summary>",
                         "<summary>Done when</summary>",
                         "<summary>Solution</summary>"]
    assert lines.count("<details>") == lines.count("</details>") == 4


def test_the_done_when_form_is_a_fixed_point() -> None:
    assert rendered(NESTED_DONE) == NESTED_DONE
    _, changed = apply(doc(NESTED_DONE))
    assert changed == []


def test_unwrap_restores_the_done_when_prefix() -> None:
    body = NESTED_DONE.split("> Do the thing.\n")[1].split("## 4.")[0]
    flat = unwrap(body.split("\n"))
    assert flat.done == ["`test_f.py` passes."]
    assert flat.rest[0] == "The approach."
    assert flat.rest[-1] == "Discussion."
    head = FLAT_DONE.split("> Do the thing.\n")[1].split("The approach.")[0]
    assert "Done when: `test_f.py` passes." in head


def test_steps_put_done_when_before_the_solution() -> None:
    body = NESTED_DONE.split("> Do the thing.\n")[1].split("## 4.")[0]
    ladder = steps(unwrap(body.split("\n")))
    assert [s.label for s in ladder] == ["Where to look", "The shape",
                                         "Done when", "Solution"]
    assert ladder[2].lines == ["`test_f.py` passes."]


def test_no_done_when_step_without_the_paragraph() -> None:
    assert "<summary>Done when</summary>" not in rendered(FLAT)
    body = NESTED.split("> Do the thing.\n")[1].split("## 4.")[0]
    assert unwrap(body.split("\n")).done == []


def test_a_done_when_paragraph_elsewhere_is_prose() -> None:
    text = FLAT.replace("The approach.\n",
                        "The approach.\n\nDone when: it prints.\n", 1)
    out = rendered(text)
    assert "<summary>Done when</summary>" not in out
    assert "Done when: it prints." in out
    assert rendered(out) == out
    flat = split_hint(["Hint: Look.", "", "Rest.", "", "Done when: x."])
    assert flat.done == []
    assert flat.rest == ["Rest.", "", "Done when: x."]


def test_a_done_when_paragraph_without_a_hint_is_prose() -> None:
    flat = split_hint(["Done when: x.", "", "Rest."])
    assert flat.hint == [] and flat.done == []


def test_split_hint_strips_the_prefix() -> None:
    flat = split_hint(["Hint:  Look here.", "", "Rest."])
    assert flat.hint == ["Look here."]
    assert flat.rest == ["Rest."]


def test_apply_reports_the_changed_heading_line() -> None:
    _, changed = apply(doc(FLAT))
    assert changed == [3]
