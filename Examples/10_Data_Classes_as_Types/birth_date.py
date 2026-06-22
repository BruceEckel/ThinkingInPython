# birth_date.py
# An Enum is also a type, and is the better choice when the set of
# values is small and fixed. Each Month knows its length and
# validates a Day against it.
from dataclasses import dataclass
from enum import Enum
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
        check(1900 < self.n <= 2026, f"Year({self.n})")

class Month(Enum):
    JANUARY = (1, 31)
    FEBRUARY = (2, 28)   # Leap years are left as an exercise.
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

    def check_day(self, day: Day) -> None:
        check(day.n <= self.max_days,
              f"{self.name} has no day {day.n}")

    def __repr__(self) -> str:
        return self.name

@dataclass(frozen=True)
class BirthDate:
    month: Month
    day: Day
    year: Year

    def __post_init__(self) -> None:
        self.month.check_day(self.day)

if __name__ == "__main__":
    print(BirthDate(Month.of(7), Day(8), Year(1957)))
