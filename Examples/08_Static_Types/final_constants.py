# final_constants.py
from typing import Final

MAX_RETRIES: Final = 3
GREETING: Final[str] = "hello"

# ty: cannot assign to final name "MAX_RETRIES":
# MAX_RETRIES = 5

print(MAX_RETRIES, GREETING)
#: 3 hello
