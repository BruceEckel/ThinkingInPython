# tstrings.py
from string.templatelib import Template

name = "Alice"
score = 91.5
message: Template = t"{name} scored {score:.0f}%"
print(message.strings)
#: ('', ' scored ', '%')
for piece in message.interpolations:
    print(piece.expression, piece.value,
          repr(piece.format_spec))
#: name Alice ''
#: score 91.5 '.0f'
