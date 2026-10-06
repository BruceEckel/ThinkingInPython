"""Pin the recursion limit for calls that forward **kwargs.

Chapter 34 says Python's recursion limit caps how deep a
tree its recursive functions can walk, and its exercise 8
has the reader confirm that `evaluate()`, which forwards
`**env`, raises a `RecursionError` on a deep tree. On
CPython 3.15.0rc2 a recursive function that forwards
`**kwargs` can run past the limit: `count_down_kw()` below
does, while the same function without them stops at it.
That looks like a
release-candidate bug, so the prose stays as written and
this file watches for the fix.

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
    reason="CPython 3.15.0rc2 lets a recursive call that "
           "forwards **kwargs run past the recursion "
           "limit. On XPASS, recheck chapter 34's "
           "recursion-limit paragraph and exercise 8, and "
           "Solutions 34 exercise 8, then delete this "
           "marker.")
def test_kwargs_recursion_stops_at_the_limit() -> None:
    assert count_down_kw(10, x=1) == 10
    with pytest.raises(RecursionError):
        count_down_kw(DEPTH, x=1)
