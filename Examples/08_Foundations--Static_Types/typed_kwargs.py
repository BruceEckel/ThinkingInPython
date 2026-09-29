# typed_kwargs.py
from typing import NotRequired, TypedDict, Unpack

class Style(TypedDict):
    width: int
    fill: NotRequired[str]

def label(text: str, **style: Unpack[Style]) -> str:
    fill = style.get("fill", " ")
    return f"[{text.center(style['width'], fill)}]"

print(label("ok", width=6))
#: [  ok  ]
print(label("ok", width=6, fill="*"))
#: [**ok**]
