# narrowing.py

def shout(text: str | None) -> str:
    if text is not None:
        return text.upper()
    return "(nothing)"

print(shout("hi"))
#: HI
print(shout(None))
#: (nothing)
