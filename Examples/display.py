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

def display_object(
    obj: object,
    dunder: Sequence[str] | ALL_DUNDERS | REDEFINED_DUNDERS = (),
    max_width: int = 65,
) -> None:
    # For a class, the class itself; for an instance, its class:
    cls = obj if inspect.isclass(obj) else type(obj)
    print(f"=== {cls.__name__} ===")
    annotations = _annotations(cls)
    attributes: list[str] = []
    methods: list[str] = []
    # Read members statically, without triggering dynamic descriptors:
    for name, value in inspect.getmembers_static(obj):
        is_dunder = name.startswith("__") and name.endswith("__")
        if dunder is ALL_DUNDERS:
            show_dunder = True
        elif dunder is REDEFINED_DUNDERS:
            show_dunder = _redefined(name, value)
        else:
            show_dunder = name in dunder
        if is_dunder and not show_dunder:
            continue  # Skip standard dunder clutter
        if callable(value):
            try:
                sig = str(inspect.signature(value))
            except (ValueError, TypeError):
                sig = "(...)"
            # Trim the signature to keep the line within max_width:
            sig_budget = max_width - len(name) - 4
            if len(sig) > sig_budget:
                sig = sig[:sig_budget - 3] + "..."
            methods.append(f"  • {name}{sig}")
        else:
            label = name
            if name in annotations:
                label = f"{name}: {_type_name(annotations[name])}"
            val_str = repr(value)
            # Trim the value to keep the line within max_width:
            budget = max_width - len(label) - 7
            if len(val_str) > budget:
                val_str = val_str[:budget - 3] + "..."
            attributes.append(f"  • {label} = {val_str}")
    print("[Attributes]")
    print("\n".join(attributes) or "  None")
    print("[Methods]")
    print("\n".join(methods) or "  None")
