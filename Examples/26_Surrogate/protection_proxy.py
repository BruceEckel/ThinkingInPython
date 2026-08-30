# protection_proxy.py
from typing import Any, Final

READ_ONLY: Final[frozenset[str]] = frozenset({"read"})

class Guarded:
    def __init__(self, doc: Document, *,
                 admin: bool) -> None:
        self._doc = doc
        self._admin = admin
    def __getattr__(self, name: str) -> Any:
        if not self._admin and name not in READ_ONLY:
            raise PermissionError(name)
        return getattr(self._doc, name)

class Document:
    def read(self) -> str: return "contents"
    def erase(self) -> None: print("erased")

guest = Guarded(Document(), admin=False)
print(guest.read())
#: contents
try:
    guest.erase()
except PermissionError as e:
    print(type(e).__name__, e)
#: PermissionError erase
Guarded(Document(), admin=True).erase()
#: erased
