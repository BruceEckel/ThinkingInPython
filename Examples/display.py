# display.py
import inspect
from collections.abc import Sequence

def display_object(
    obj: object, dunder: Sequence[str] = (), max_width: int = 65
) -> None:
    """Print a compact, readable view of an object or class.

    Standard dunder members are hidden; name any to keep in `dunder`.
    """
    print(f"=== {type(obj).__name__} ===")
    attributes: list[str] = []
    methods: list[str] = []
    # Read members statically, without triggering dynamic descriptors
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
            val_str = repr(value)
            if len(val_str) > max_width - len(name) - 6:
                val_str = val_str[:max_width - len(name) - 9] + "..."
            attributes.append(f"  • {name}: {val_str}")
    print("[Attributes]")
    print("\n".join(attributes) or "  None")
    print("[Methods]")
    print("\n".join(methods) or "  None")
