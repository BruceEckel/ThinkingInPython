# mapping_patterns.py

def handle(event: dict[str, object]) -> str:
    match event:
        case {"type": "click", "x": x, "y": y}:
            return f"Click at ({x}, {y})"
        case {"type": "key", "key": key}:
            return f"Key {key}"
        case {"type": kind}:
            return f"Other event: {kind}"
        case unknown:
            return f"Unrecognized event: {unknown}"

print(handle({"type": "click", "x": 10, "y": 20}))
#: Click at (10, 20)
print(handle({"type": "key", "key": "Enter"}))
#: Key Enter
print(handle({"type": "scroll", "delta": 3}))
#: Other event: scroll
print(handle({"button": 1}))
#: Unrecognized event: {'button': 1}
