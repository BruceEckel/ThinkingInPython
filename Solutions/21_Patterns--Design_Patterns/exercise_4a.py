# exercise_4a.py
from record import record

class PdfWriter:
    def pdf(self, text: str) -> str:
        return f"%PDF {text}"

class HtmlWriter:
    def html(self, text: str) -> str:
        return f"<p>{text}</p>"

class MdWriter:
    def markdown(self, text: str) -> str:
        return f"**{text}**"

type AnyWriter = PdfWriter | HtmlWriter | MdWriter

@record
class Report:
    text: str

    def render(self, writer: AnyWriter) -> str:
        match writer:
            case PdfWriter():
                return writer.pdf(self.text)
            case HtmlWriter():
                return writer.html(self.text)
            case MdWriter():
                return writer.markdown(self.text)

def main(kind: str) -> None:
    writer: AnyWriter
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
