# Template Method: Solutions

## 1. A file-processing framework, customized both ways

The framework fixes the shape: read every file but the last, run an
undetermined `process()` step over each one's text, and write the
combined result to the last file.

```python
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
```

Both produce identical output, `'HELLO\nWORLD\n'`, since both express
the exact same `process()` step, an uppercase conversion, through two
different mechanisms for supplying it. The fixed algorithm, "read
every input, transform it, concatenate into the output," lives in
exactly one place either way: the base class's `run()`, or the free
function `run_file_framework()`.

The second customization idea, searching every input file for words
listed in the first, fits the same shape with a different `process()`
step: a version whose `process(text)` checks the text against a
word list (read once, before the loop, from the first input file) and
returns a report of which words it found, rather than transforming the
text itself. Nothing about `FileFramework.run()` or
`run_file_framework()` needs to change to support it; only the step
does, which is the entire point of the pattern.
