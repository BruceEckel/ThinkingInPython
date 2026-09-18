# utils/effect_rows.py
from collections.abc import Callable
from typing import get_type_hints
from record import record

@record
class Performs:
    effects: frozenset[type]

def performs(*effects: type) -> Performs:
    return Performs(frozenset(effects))

def row(f: Callable[..., object]) -> list[str]:
    hints = get_type_hints(f, include_extras=True)
    result = hints.get("return")
    return sorted(
        effect.__name__
        for extra in getattr(result, "__metadata__", ())
        if isinstance(extra, Performs)
        for effect in extra.effects
    )
