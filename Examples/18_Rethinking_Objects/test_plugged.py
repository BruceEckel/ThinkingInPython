# test_plugged.py
from plugged import Plugged

def test_defensive_copy_prevents_the_leak() -> None:
    plugged = Plugged([1, 2])
    plugged.numbers.append(999)  # Mutates only a copy
    assert plugged.numbers == [1, 2]
