# final.py
from typing import final

@final
class B:
    pass

b = B()
print(type(b).__name__)
## B

# A type checker rejects `class C(B): ...`, because it would
# inherit from a final class.
