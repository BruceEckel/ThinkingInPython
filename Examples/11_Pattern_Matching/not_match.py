# not_match.py
# A dict is the right tool for a value-to-value lookup; reserve match
# for patterns that destructure.
STATUS = {200: "OK", 404: "Not Found", 500: "Server Error"}


def describe(status: int) -> str:
    return STATUS.get(status, f"status {status}")


print(describe(200))
print(describe(301))
