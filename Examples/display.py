# display.py
import inspect
from collections.abc import Sequence
from typing import Final

ALL_DUNDERS = sentinel("ALL_DUNDERS")
REDEFINED_DUNDERS = sentinel("REDEFINED_DUNDERS")
INTERESTING_DUNDERS: Final[tuple[str, ...]] = (
    "__init__", "__repr__", "__eq__", "__hash__",
)

def _annotations(cls: type) -> dict[str, object]:
    # Annotations declared on the class or any of its bases:
    merged: dict[str, object] = {}
    for base in reversed(cls.__mro__):
        merged.update(inspect.get_annotations(base))
    return merged

def _type_name(annotation: object) -> str:
    # A readable name for a type annotation, keeping any [parameters]:
    if isinstance(annotation, type):
        return annotation.__name__
    return str(annotation)

def _redefined(name: str, value: object) -> bool:
    # Restricted to INTERESTING_DUNDERS: every class has __module__,
    # __dict__, and other bookkeeping dunders that always differ from
    # object's, so comparing those would never filter anything out.
    if name not in INTERESTING_DUNDERS:
        return False
    return getattr(object, name, None) is not value

def _show_dunder(
    dunder: Sequence[str] | ALL_DUNDERS | REDEFINED_DUNDERS,
    name: str,
    value: object,
) -> bool:
    if dunder is ALL_DUNDERS:
        return True
    if dunder is REDEFINED_DUNDERS:
        return _redefined(name, value)
    return name in dunder

def _shared(obj: object, name: str) -> bool:
    # A class has no instance-level storage to compare against, so
    # every attribute it shows is class-level storage by construction.
    # For an instance, only a name missing from its own __dict__ is:
    if inspect.isclass(obj):
        return True
    return name not in getattr(obj, "__dict__", {})

def _truncate(text: str, budget: int) -> str:
    # Keep text within budget, marking a cut with an ellipsis:
    if len(text) <= budget:
        return text
    return text[:budget - 3] + "..."

def _format_method(name: str, value: object, max_width: int) -> str:
    try:
        sig = str(inspect.signature(value))
    except (ValueError, TypeError):
        sig = "(...)"
    sig = _truncate(sig, max_width - len(name) - 4)
    return f"  • {name}{sig}"

def _format_attribute(
    obj: object,
    name: str,
    value: object,
    annotations: dict[str, object],
    max_width: int,
) -> str:
    label = name
    if name in annotations:
        label = f"{name}: {_type_name(annotations[name])}"
    tag = " [CV]" if _shared(obj, name) else ""
    budget = max_width - len(label) - len(tag) - 7
    val_str = _truncate(repr(value), budget)
    return f"  • {label} = {val_str}{tag}"

def display_object(
    obj: object,
    dunder: Sequence[str] | ALL_DUNDERS | REDEFINED_DUNDERS = (),
    max_width: int = 65,
    header: bool = False,
    exclude: Sequence[str] = (),
) -> None:
    # For a class, the class itself; for an instance, its class:
    cls = obj if inspect.isclass(obj) else type(obj)
    if header:
        print(f"=== {cls.__name__} ===")
    annotations = _annotations(cls)
    attributes: list[str] = []
    methods: list[str] = []
    # Read members statically, without triggering dynamic descriptors:
    for name, value in inspect.getmembers_static(obj):
        if name in exclude:
            continue
        is_dunder = name.startswith("__") and name.endswith("__")
        if is_dunder and not _show_dunder(dunder, name, value):
            continue  # Skip standard dunder clutter
        if callable(value):
            methods.append(_format_method(name, value, max_width))
        else:
            attributes.append(
                _format_attribute(obj, name, value, annotations, max_width)
            )
    print("[Attributes]")
    print("\n".join(attributes) or "  None")
    print("[Methods]")
    print("\n".join(methods) or "  None")
