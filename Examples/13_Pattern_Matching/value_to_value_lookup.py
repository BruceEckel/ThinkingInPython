# value_to_value_lookup.py
from typing import Final

STATUS: Final[dict[int, str]] = {
    200: "OK", 404: "Not Found", 500: "Server Error"}

def describe(status: int) -> str:
    return STATUS.get(status, f"Status {status}")

print(describe(200))
#: OK
print(describe(301))
#: Status 301
