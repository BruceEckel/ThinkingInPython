# tstrings.py
from string.templatelib import Interpolation, Template

name = "Alice"
score = 91.5
message: Template = t"{name} scored {score:.0f}%"
print(message.strings)
#: ('', ' scored ', '%')
print([piece.expression
       for piece in message.interpolations])
#: ['name', 'score']

def shout(template: Template) -> str:
    parts: list[str] = []
    for piece in template:
        if isinstance(piece, Interpolation):
            parts.append(
                format(piece.value, piece.format_spec))
        else:
            parts.append(piece.upper())
    return "".join(parts)

print(shout(message))
#: Alice SCORED 92%

def safe(template: Template) -> str:
    parts: list[str] = []
    for piece in template:
        if isinstance(piece, Interpolation):
            value = str(piece.value)
            if "'" in value:
                raise ValueError(
                    f"unsafe value: {value!r}")
            parts.append(value)
        else:
            parts.append(piece)
    return "".join(parts)

print(safe(t"Hello, {name}"))
#: Hello, Alice
trouble = "Bob'; rm -rf /"
try:
    safe(t"Hello, {trouble}")
except ValueError as e:
    print(e)
#: unsafe value: "Bob'; rm -rf /"
