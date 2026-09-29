# exercise_1_search.py
import tempfile
from pathlib import Path
from typing import override
from exercise_1 import FileFramework, run_file_framework
from record import record

def found(words: list[str], text: str) -> str:
    present = [w for w in words if w in text.split()]
    return f"{' '.join(present)}\n"

@record
class Search(FileFramework):
    words: list[str]

    @override
    def process(self, text: str) -> str:
        return found(self.words, text)

def demo() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        wordfile = root / "words.txt"
        wordfile.write_text("spam\neggs\nham\n")
        (root / "a.txt").write_text("spam and eggs\n")
        (root / "b.txt").write_text("green eggs and ham\n")
        inputs = [str(root / "a.txt"), str(root / "b.txt")]
        words = wordfile.read_text().split()

        # Subclassing customization:
        out1 = root / "out1.txt"
        Search(words).run([*inputs, str(out1)])
        print(repr(out1.read_text()))

        # Function-passing customization:
        out2 = root / "out2.txt"
        run_file_framework(
            [*inputs, str(out2)],
            lambda text: found(words, text))
        print(repr(out2.read_text()))

demo()
#: 'spam eggs\neggs ham\n'
#: 'spam eggs\neggs ham\n'
