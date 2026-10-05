# test_birth_date.py
import pytest
from birth_date import BirthDate, Day, Month, Year
from validation import TypeFailure

def test_of_finds_the_month() -> None:
    bd = BirthDate(Month.of(7), Day(8), Year(1957))
    assert bd.month is Month.JULY

@pytest.mark.parametrize("month_n, day_n", [
    (2, 31),
    (4, 31),
    (9, 31),
])
def test_day_past_end_of_month(month_n: int,
                               day_n: int) -> None:
    assert Month.of(month_n).max_days < day_n
    with pytest.raises(TypeFailure):
        BirthDate(Month.of(month_n), Day(day_n), Year(2020))

@pytest.mark.parametrize("bad", [0, 13, -1])
def test_month_number_outside_twelve(bad: int) -> None:
    with pytest.raises(TypeFailure):
        Month.of(bad)
