# http_status.py
# Literal patterns match exact values.

def describe(status: int) -> str:
    match status:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Server Error"
        case _:  # Default
            return f"Status {status}"

print(describe(200))
print(describe(404))
print(describe(301))
