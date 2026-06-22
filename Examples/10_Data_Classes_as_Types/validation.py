# validation.py
class TypeFailure(ValueError):
    "Raised when a value falls outside the set its type allows."

def check(condition: bool, message: str, detail: str = "") -> None:
    if not condition:
        raise TypeFailure(f"{message} {detail}".rstrip())
