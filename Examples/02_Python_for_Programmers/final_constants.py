# final_constants.py
# Final marks a name as a constant. Reassigning it is a type error,
# caught by the checker before the program runs.
from typing import Final

MAX_RETRIES: Final = 3
GREETING: Final[str] = "hello"

# MAX_RETRIES = 5  # ty: cannot assign to final name "MAX_RETRIES"

print(MAX_RETRIES, GREETING)
