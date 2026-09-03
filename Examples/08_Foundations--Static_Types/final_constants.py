# final_constants.py
from typing import Final

MAX_RETRIES: Final = 3
GREETING: Final[str] = "hello"
HISTORY: Final[list[str]] = []

# ty: cannot assign to final name "MAX_RETRIES":
# MAX_RETRIES = 5

HISTORY.append("first")
print(MAX_RETRIES, GREETING, HISTORY)
#: 3 hello ['first']
