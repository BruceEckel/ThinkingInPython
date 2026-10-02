# exercise_7.py
from html import escape
from string.templatelib import Interpolation, Template

def to_html(template: Template) -> str:
    parts: list[str] = []
    for piece in template:
        if isinstance(piece, Interpolation):
            parts.append(escape(str(piece.value)))
        else:
            parts.append(piece)
    return "".join(parts)

comment = "<script>steal()</script> & run"
print(to_html(t"<p>{comment}</p>"))
#: <p>&lt;script&gt;steal()&lt;/script&gt; &amp; run</p>
print(f"<p>{comment}</p>")
#: <p><script>steal()</script> & run</p>
