# value_to_value_lookup.py

STATUS = {200: "OK", 404: "Not Found", 500: "Server Error"}

def describe(status: int) -> str:
    return STATUS.get(status, f"Status {status}")

print(describe(200))
print(describe(301))
