# exercise_1.py
from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import final

class FileFramework(ABC):
    __slots__ = ()

    @final
    def run(self, filenames: list[str]) -> None:
        *inputs, output = filenames
        pieces = [
            self.process(Path(name).read_text())
            for name in inputs]
        Path(output).write_text("".join(pieces))

    @abstractmethod
    def process(self, text: str) -> str: ...

def run_file_framework(
    filenames: list[str], process: Callable[[str], str]
) -> None:
    *inputs, output = filenames
    pieces = [process(Path(name).read_text())
              for name in inputs]
    Path(output).write_text("".join(pieces))
