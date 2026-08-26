# final.py
from typing import final

@final
class B:
    pass

# ty: cannot inherit from final class "B":
# class C(B): pass
b = B()
print(type(b).__name__)
#: B
