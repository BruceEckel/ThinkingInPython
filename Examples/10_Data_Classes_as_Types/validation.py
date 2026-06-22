# validation.py
class TypeFailure(ValueError):
    "A value falls outside the type's allowed set"

def check(condition: bool, message: str, detail: str = "") -> None:
    if not condition:
        raise TypeFailure(f"{message} {detail}".rstrip())
