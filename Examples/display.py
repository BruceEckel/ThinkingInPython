# display.py
import inspect
from collections.abc import Sequence

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

def display_object(
    obj: object, dunder: Sequence[str] = (), max_width: int = 65
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
        if is_dunder and name not in dunder:
            continue  # Skip standard dunder clutter
        if callable(value):
            try:
                sig = str(inspect.signature(value))
            except (ValueError, TypeError):
                sig = "(...)"
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
