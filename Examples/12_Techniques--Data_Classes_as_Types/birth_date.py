# birth_date.py
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Final
from validation import check

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

DAYS: Final[tuple[int, ...]] = (31, 28, 31, 30, 31, 30,
                                31, 31, 30, 31, 30, 31)

class Month(Enum):
    JANUARY = 1
    FEBRUARY = 2  # Leap years are left as an exercise
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

    def check_day(self, day: Day) -> None:
        check(day.n <= self.max_days, f"Day({day.n})",
              f"is past the end of {self.name}")

@dataclass(frozen=True)
class BirthDate:
    month: Month
    day: Day
    year: Year

    def __post_init__(self) -> None:
        self.month.check_day(self.day)
