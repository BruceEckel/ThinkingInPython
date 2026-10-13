# overload_example.py
from typing import overload

@overload
def stringify(value: int) -> str: ...

@overload
def stringify(value: list[int]) -> list[str]: ...

def stringify(value: int | list[int]) -> str | list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    return str(value)

print(stringify(42))
#: 42
print(stringify([1, 2, 3]))
#: ['1', '2', '3']
