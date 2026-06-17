# http_status.py
# Literal patterns match exact values; the _ wildcard is the default.

def describe(status: int) -> str:
    match status:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Server Error"
        case _:
            return f"status {status}"


print(describe(200))
print(describe(404))
print(describe(301))
