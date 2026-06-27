# demo_birth_date.py
from birth_date import BirthDate, Day, Month, Year

print(BirthDate(Month.of(7), Day(8), Year(1957)))
#: BirthDate(month=JULY, day=Day(n=8), year=Year(n=1957))
