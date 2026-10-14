# test_ch12_leap_year.py
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Final
import pytest

@dataclass(eq=False)
class TypeFailure(ValueError):
    subject: str
    reason: str = ""

    def __str__(self) -> str:
        return f"{self.subject} {self.reason}".rstrip()

def check(condition: bool, subject: str,
          reason: str = "") -> None:
    if not condition:
        raise TypeFailure(subject, reason)

@dataclass(frozen=True)
class Day:
    n: int

    def __post_init__(self) -> None:
        check(1 <= self.n <= 31, f"Day({self.n})")

@dataclass(frozen=True)
class Year:
    n: int

    def __post_init__(self) -> None:
        check(1900 < self.n <= date.today().year,
              f"Year({self.n})")

    def is_leap(self) -> bool:
        return self.n % 4 == 0 and (
            self.n % 100 != 0 or self.n % 400 == 0)

DAYS: Final[tuple[int, ...]] = (31, 28, 31, 30, 31, 30,
                                31, 31, 30, 31, 30, 31)

class Month(Enum):
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12

    @property
    def max_days(self) -> int:
        return DAYS[self.value - 1]

    def check_day(self, day: Day, year: Year) -> None:
        max_days = self.max_days
        if self is Month.FEBRUARY and year.is_leap():
            max_days = 29
        check(day.n <= max_days, f"Day({day.n})",
              f"is past the end of {self.name}")

@dataclass(frozen=True)
class BirthDate:
    month: Month
    day: Day
    year: Year

    def __post_init__(self) -> None:
        self.month.check_day(self.day, self.year)

def test_feb_29_allowed_in_leap_year() -> None:
    bd = BirthDate(Month(2), Day(29), Year(2020))
    assert bd.day.n == 29

def test_feb_29_allowed_in_2000() -> None:
    bd = BirthDate(Month(2), Day(29), Year(2000))
    assert bd.day.n == 29

def test_feb_29_rejected_in_non_leap_year() -> None:
    with pytest.raises(TypeFailure):
        BirthDate(Month(2), Day(29), Year(2021))

def test_feb_30_always_rejected() -> None:
    with pytest.raises(TypeFailure):
        BirthDate(Month(2), Day(30), Year(2020))
