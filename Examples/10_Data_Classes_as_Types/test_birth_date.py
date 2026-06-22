# test_birth_date.py
import pytest
from birth_date import BirthDate, Day, Month, Year
from validation import TypeFailure

def test_valid_date() -> None:
    bd = BirthDate(Month.of(7), Day(8), Year(1957))
    assert bd.month is Month.JULY

@pytest.mark.parametrize("month_n, day_n", [
    (2, 31),   # February has 28 days
    (4, 31),   # April has 30
    (9, 31),   # September has 30
])
def test_day_out_of_range_for_month(month_n: int, day_n: int) -> None:
    with pytest.raises(TypeFailure):
        BirthDate(Month.of(month_n), Day(day_n), Year(2020))

@pytest.mark.parametrize("bad", [0, 13])
def test_bad_month_number(bad: int) -> None:
    with pytest.raises(TypeFailure):
        Month.of(bad)
