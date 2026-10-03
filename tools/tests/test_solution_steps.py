"""Tests for tools/solution_steps.py (solutions folded into steps)."""
from pathlib import Path

from tools.markdown import Document
from tools.solution_steps import (
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


def test_split_hint_strips_the_prefix() -> None:
    flat = split_hint(["Hint:  Look here.", "", "Rest."])
    assert flat.hint == ["Look here."]
    assert flat.rest == ["Rest."]


def test_apply_reports_the_changed_heading_line() -> None:
    _, changed = apply(doc(FLAT))
    assert changed == [3]
