# sequence_patterns.py
# Sequence patterns match by length and position; *rest takes the
# remainder.

def summarize(items: list[int]) -> str:
    match items:
        case []:
            return "empty"
        case [only]:
            return f"one item: {only}"
        case [first, second]:
            return f"two items: {first}, {second}"
        case [first, *rest]:
            return f"{first}, then {len(rest)} more"
        case _:
            return "unreachable"

print(summarize([]))
print(summarize([5]))
print(summarize([3, 4]))
print(summarize([1, 2, 3, 4]))
