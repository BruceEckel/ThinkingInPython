# test_ch12_leap_year.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from enum import Enum
import pytest

class TypeFailure(ValueError):
    "A value falls outside the type's allowed set."

def check(condition: bool, message: str, detail: str = "") -> None:
    if not condition:
        raise TypeFailure(f"{message} {detail}".rstrip())

@dataclass(frozen=True)
class Day:
    n: int

    def __post_init__(self) -> None:
        check(1 <= self.n <= 31, f"Day({self.n})")

@dataclass(frozen=True)
class Year:
    n: int

    def __post_init__(self) -> None:
        check(1900 < self.n <= date.today().year, f"Year({self.n})")

    def is_leap(self) -> bool:
        return self.n % 4 == 0 and (
            self.n % 100 != 0 or self.n % 400 == 0)

class Month(Enum):
    JANUARY = (1, 31)
    FEBRUARY = (2, 28)
    MARCH = (3, 31)
    APRIL = (4, 30)
    MAY = (5, 31)
    JUNE = (6, 30)
    JULY = (7, 31)
    AUGUST = (8, 31)
    SEPTEMBER = (9, 30)
    OCTOBER = (10, 31)
    NOVEMBER = (11, 30)
    DECEMBER = (12, 31)

    @staticmethod
    def of(month_number: int) -> Month:
        check(1 <= month_number <= 12, f"Month({month_number})")
        return list(Month)[month_number - 1]

    @property
    def max_days(self) -> int:
        return self.value[1]

    def check_day(self, day: Day, year: Year) -> None:
        max_days = self.max_days
        if self is Month.FEBRUARY and year.is_leap():
            max_days = 29
        check(day.n <= max_days, f"{self.name} has no day {day.n}")

@dataclass(frozen=True)
class BirthDate:
    month: Month
    day: Day
    year: Year

    def __post_init__(self) -> None:
        self.month.check_day(self.day, self.year)

def test_feb_29_allowed_in_leap_year() -> None:
    bd = BirthDate(Month.of(2), Day(29), Year(2020))
    assert bd.day.n == 29

def test_feb_29_rejected_in_non_leap_year() -> None:
    with pytest.raises(TypeFailure):
        BirthDate(Month.of(2), Day(29), Year(2021))

def test_feb_30_always_rejected() -> None:
    with pytest.raises(TypeFailure):
        BirthDate(Month.of(2), Day(30), Year(2020))
