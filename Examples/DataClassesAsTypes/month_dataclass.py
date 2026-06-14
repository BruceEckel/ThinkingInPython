# DataClassesAsTypes/month_dataclass.py
# Month can also be a data class instead of an Enum. It works, but it is more
# code for less safety: you have to build and hand around the set of months
# yourself, where the Enum simply is that set.
from dataclasses import dataclass, field
from validation import check


@dataclass(frozen=True)
class Day:
    n: int

    def __post_init__(self) -> None:
        check(1 <= self.n <= 31, f"Day({self.n})")


@dataclass(frozen=True)
class Month:
    name: str
    n: int
    max_days: int

    def __post_init__(self) -> None:
        check(1 <= self.n <= 12, f"Month({self.n})")
        check(self.max_days in (28, 30, 31), f"max_days {self.max_days}")

    def check_day(self, day: Day) -> None:
        check(day.n <= self.max_days, f"{self.name} has no day {day.n}")


def make_months() -> list[Month]:
    return [Month(name, n, days) for n, (name, days) in enumerate([
        ("January", 31), ("February", 28), ("March", 31), ("April", 30),
        ("May", 31), ("June", 30), ("July", 31), ("August", 31),
        ("September", 30), ("October", 31), ("November", 30),
        ("December", 31),
    ], start=1)]


@dataclass(frozen=True)
class Months:
    months: list[Month] = field(default_factory=make_months)

    def of(self, month_number: int) -> Month:
        check(1 <= month_number <= 12, f"Month({month_number})")
        return self.months[month_number - 1]


if __name__ == "__main__":
    months = Months()
    print(months.of(7))
