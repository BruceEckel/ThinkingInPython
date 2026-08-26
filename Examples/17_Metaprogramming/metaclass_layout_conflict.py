# metaclass_layout_conflict.py
from typing import Any

try:
    class Singleton(type, dict[type, Any]):  # type: ignore
        pass
except TypeError as e:
    print(e)
#: multiple bases have instance lay-out conflict
