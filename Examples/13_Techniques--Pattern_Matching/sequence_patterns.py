# sequence_patterns.py

def summarize(items: list[int]) -> str:
    match items:
        case []:
            return "Empty"
        case [only]:
            return f"One item: {only}"
        case [first, second]:
            return f"Two items: {first}, {second}"
        case [first, *middle, last]:
            return (f"{first} to {last}, "
                    f"{len(middle)} between")
        case _:  # [1]
            return "Unreachable"

print(summarize([]))
#: Empty
print(summarize([5]))
#: One item: 5
print(summarize([3, 4]))
#: Two items: 3, 4
print(summarize([1, 2, 3, 4]))
#: 1 to 4, 2 between
