# mapping_patterns.py
# A mapping pattern matches the keys it names and binds their values.

def handle(event: dict[str, object]) -> str:
    match event:
        case {"type": "click", "x": x, "y": y}:
            return f"click at ({x}, {y})"
        case {"type": "key", "key": key}:
            return f"key {key}"
        case {"type": kind}:
            return f"other event: {kind}"
        case _:
            return "not an event"

print(handle({"type": "click", "x": 10, "y": 20}))
print(handle({"type": "key", "key": "Enter"}))
print(handle({"type": "scroll", "delta": 3}))
print(handle({"button": 1}))
