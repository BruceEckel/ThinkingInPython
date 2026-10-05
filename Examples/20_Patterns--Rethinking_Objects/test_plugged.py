# test_plugged.py
from plugged import Plugged

def test_defensive_copy_prevents_the_leak() -> None:
    plugged = Plugged([1, 2])
    assert plugged.numbers is not plugged._numbers
    plugged.numbers.append(999)
    assert plugged.numbers == [1, 2]
