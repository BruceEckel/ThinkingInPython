# metaclass_layout_conflict.py
from typing import Any
from exceptions import ignore

with ignore(TypeError):
    class Singleton(type, dict[type, Any]):  # type: ignore
        pass
#: TypeError('multiple bases have instance lay-out conflict')
