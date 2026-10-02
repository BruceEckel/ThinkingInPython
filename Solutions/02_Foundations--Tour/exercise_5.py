# exercise_5.py
from string.templatelib import Interpolation, Template

name = "Alice"
score = 91.5
message: Template = t"{name} scored {score:.0f}%"

def quoted(template: Template) -> str:
    parts: list[str] = []
    for piece in template:
        if isinstance(piece, Interpolation):
            value = format(piece.value, piece.format_spec)
            parts.append(f"'{value}'")
        else:
            parts.append(piece)
    return "".join(parts)

print(quoted(message))
#: 'Alice' scored '92'%
