# final.py
from typing import final

@final
class B:
    pass

# class C(B): pass  # ty: cannot inherit from final class "B"
b = B()
print(type(b).__name__)
#: B
