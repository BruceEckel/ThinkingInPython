# exercise_4b.py
from typing import Protocol
from record import record

class Writer(Protocol):
    def write(self, text: str) -> str: ...

class PdfWriter:
    def write(self, text: str) -> str:
        return f"%PDF {text}"

class HtmlWriter:
    def write(self, text: str) -> str:
        return f"<p>{text}</p>"

class MdWriter:
    def write(self, text: str) -> str:
        return f"**{text}**"

@record
class Report:
    text: str

    def render(self, writer: Writer) -> str:
        return writer.write(self.text)

def main(kind: str) -> None:
    writer: Writer
    match kind:
        case "pdf":
            writer = PdfWriter()
        case "html":
            writer = HtmlWriter()
        case "md":
            writer = MdWriter()
        case _:
            raise ValueError(f"unknown kind {kind!r}")
    print(Report("Q3 sales").render(writer))

main("pdf")
#: %PDF Q3 sales
main("md")
#: **Q3 sales**
