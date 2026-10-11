"""Pin the recursion limit for calls that forward **kwargs.

Chapter 34 says Python's recursion limit caps how deep a
tree its recursive functions can walk, and its exercise 8
has the reader confirm that `evaluate()`, which forwards
`**env`, raises a `RecursionError` on a deep tree. On
CPython 3.15.0 (rc2 and the final release alike, checked
2026-10-11) a recursive function that forwards `*args` or
`**kwargs`, empty or not, can run past the limit:
`count_down_kw()` below reaches 100,000 frames, while the
same function without them stops at 1000. The chapter's
`evaluate()` forwards `**env` too and still stops, the
difference being two self-calls per frame against this
function's one; the cause is unknown. The prose stays as
written, since the listing it describes behaves as it
says, and this file watches the narrower case.

The second test is an expected failure today. When it
reports XPASS, recheck chapter 34's recursion-limit
paragraph, its exercise 8, and Solutions 34 exercise 8,
then delete the `xfail` marker.
"""
import pytest

# Deep enough to pass a limit near a thousand frames,
# shallow enough that a build ignoring the limit still
# finishes at once.
DEPTH = 3000


def count_down(n: int) -> int:
    return 0 if n == 0 else 1 + count_down(n - 1)


def count_down_kw(n: int, **kw: object) -> int:
    return 0 if n == 0 else 1 + count_down_kw(n - 1, **kw)


def test_plain_recursion_stops_at_the_limit() -> None:
    with pytest.raises(RecursionError):
        count_down(DEPTH)


@pytest.mark.xfail(
    strict=False,
    reason="CPython 3.15.0 lets a recursive call that "
           "forwards **kwargs run past the recursion "
           "limit. On XPASS, recheck chapter 34's "
           "recursion-limit paragraph and exercise 8, and "
           "Solutions 34 exercise 8, then delete this "
           "marker.")
def test_kwargs_recursion_stops_at_the_limit() -> None:
    assert count_down_kw(10, x=1) == 10
    with pytest.raises(RecursionError):
        count_down_kw(DEPTH, x=1)
