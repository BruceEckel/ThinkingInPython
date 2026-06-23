# mapping_patterns.py

def handle(event: dict[str, object]) -> str:
    match event:
        case {"type": "click", "x": x, "y": y}:
            return f"Click at ({x}, {y})"
        case {"type": "key", "key": key}:
            return f"Key {key}"
        case {"type": kind}:
            return f"Other event: {kind}"
        case nonevent:
            return f"Not an event: {nonevent}"

print(handle({"type": "click", "x": 10, "y": 20}))
print(handle({"type": "key", "key": "Enter"}))
print(handle({"type": "scroll", "delta": 3}))
print(handle({"button": 1}))
