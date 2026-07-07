# exercise_1.py
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import final, override

class FileFramework:
    def __init__(self, filenames: list[str]) -> None:
        self.filenames = filenames

    @final
    def run(self) -> None:
        *inputs, output = self.filenames
        pieces = [
            self.process(Path(name).read_text()) for name in inputs]
        Path(output).write_text("".join(pieces))

    def process(self, text: str) -> str:
        raise NotImplementedError

class UppercaseFramework(FileFramework):
    @override
    def process(self, text: str) -> str:
        return text.upper()

def run_file_framework(filenames: list[str],
                        process: Callable[[str], str]) -> None:
    *inputs, output = filenames
    pieces = [process(Path(name).read_text()) for name in inputs]
    Path(output).write_text("".join(pieces))

def demo() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "a.txt").write_text("hello\n")
        (root / "b.txt").write_text("world\n")

        # Subclassing customization:
        UppercaseFramework([
            str(root / "a.txt"), str(root / "b.txt"),
            str(root / "out1.txt"),
        ]).run()
        print(repr((root / "out1.txt").read_text()))

        # Function-passing customization:
        run_file_framework(
            [str(root / "a.txt"), str(root / "b.txt"),
             str(root / "out2.txt")],
            lambda text: text.upper(),
        )
        print(repr((root / "out2.txt").read_text()))

demo()
#: 'HELLO\nWORLD\n'
#: 'HELLO\nWORLD\n'
