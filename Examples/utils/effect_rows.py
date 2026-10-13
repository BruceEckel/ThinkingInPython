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
    annotation = hints.get("return")
    return sorted(
        effect.__name__
        for piece in getattr(annotation, "__metadata__", ())
        if isinstance(piece, Performs)
        for effect in piece.effects
    )
