# final.py
from typing import final

@final
class B:
    pass

b = B()
print(type(b).__name__)
#: B
