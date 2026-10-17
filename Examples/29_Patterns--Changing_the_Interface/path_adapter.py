# path_adapter.py
import os
from pathlib import Path
from record import record

@record
class Asset:
    folder: str
    name: str

    def __fspath__(self) -> str:
        return f"{self.folder}/{self.name}"

logo = Asset("images", "logo.svg")
print(isinstance(logo, os.PathLike))
#: True
print(os.path.basename(logo))
#: logo.svg
print(Path(logo).suffix)
#: .svg
