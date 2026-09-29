# exercise_1_upper.py
import tempfile
from pathlib import Path
from typing import override
from exercise_1 import FileFramework, run_file_framework

class Uppercase(FileFramework):
    @override
    def process(self, text: str) -> str:
        return text.upper()

def demo() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "a.txt").write_text("hello\n")
        (root / "b.txt").write_text("world\n")
        inputs = [str(root / "a.txt"), str(root / "b.txt")]

        # Subclassing customization:
        out1 = root / "out1.txt"
        Uppercase().run([*inputs, str(out1)])
        print(repr(out1.read_text()))

        # Function-passing customization:
        out2 = root / "out2.txt"
        run_file_framework([*inputs, str(out2)], str.upper)
        print(repr(out2.read_text()))

demo()
#: 'HELLO\nWORLD\n'
#: 'HELLO\nWORLD\n'
