# test_mapping_patterns.py
from mapping_patterns import handle

def test_mapping_patterns() -> None:
    assert handle({"type": "key", "key": "Esc"}) == "Key Esc"
    assert handle({"nope": 1}) == "Not an event: {'nope': 1}"
