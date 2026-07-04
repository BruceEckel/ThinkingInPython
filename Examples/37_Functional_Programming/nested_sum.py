# nested_sum.py
type Nested = int | list[Nested]

def deep_sum(items: list[Nested]) -> int:
    total = 0
    for item in items:
        if isinstance(item, list):
            total += deep_sum(item)  # Recurse into a sublist
        else:
            total += item  # A plain number
    return total

print(deep_sum([1, [2, [3, 4], 5], 6]))
#: 21
