# tstrings.py
from string.templatelib import Interpolation, Template

name = "Alice"
score = 91.5
message: Template = t"{name} scored {score:.0f}%"
print(message.strings)
#: ('', ' scored ', '%')
print([piece.expression for piece in message.interpolations])
#: ['name', 'score']

def shout(template: Template) -> str:
    parts: list[str] = []
    for piece in template:
        if isinstance(piece, Interpolation):
            parts.append(format(piece.value, piece.format_spec))
        else:
            parts.append(piece.upper())
    return "".join(parts)

print(shout(message))
#: Alice SCORED 92%
