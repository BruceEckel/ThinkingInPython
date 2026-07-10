# validation.py
class TypeFailure(ValueError):
    pass

def check(condition: bool, message: str, detail: str = "") -> None:
    if not condition:
        raise TypeFailure(f"{message} {detail}".rstrip())
