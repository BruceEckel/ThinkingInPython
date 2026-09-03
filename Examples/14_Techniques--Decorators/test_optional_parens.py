# test_optional_parens.py
from optional_parens import label

def test_bare_decoration() -> None:
    @label
    def greet() -> str:
        return "hi"

    assert greet() == "hi"
    assert greet.__name__ == "greet"

def test_decoration_with_arguments() -> None:
    @label(prefix="TAG")
    def greet() -> str:
        return "hi"

    assert greet() == "hi"
    assert greet.__name__ == "greet"
