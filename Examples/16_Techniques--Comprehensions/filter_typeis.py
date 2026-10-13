# filter_typeis.py
from typing import TypeIs
from a_list import a_list

def is_int(e: object) -> TypeIs[int]:
    return isinstance(e, int)

print(list(map(lambda e: e ** 2, filter(is_int, a_list))))
#: [1, 81, 0, 16]
