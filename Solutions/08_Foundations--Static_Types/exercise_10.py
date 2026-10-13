# exercise_10.py
from typing import Final

MAX_RETRIES: Final = 3
GREETING: Final[str] = "hello"
HISTORY: Final[tuple[str, ...]] = ("first",)

# ty: tuple has no attribute "append":
# HISTORY.append("second")
# ty: cannot assign to final name "HISTORY":
# HISTORY = HISTORY + ("second",)

print(MAX_RETRIES, GREETING, HISTORY)
#: 3 hello ('first',)
