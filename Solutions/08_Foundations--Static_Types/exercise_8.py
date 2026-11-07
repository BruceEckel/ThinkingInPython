# exercise_8.py

def shout(text: str | None) -> str:
    if text:
        return text.upper()
    return "(nothing)"

def shout_strict(text: str | None) -> str:
    if text is not None:
        return text.upper()
    return "(nothing)"

print(shout("hi"))
#: HI
print(shout(None))
#: (nothing)
print(shout(""))  # The empty string is falsy
#: (nothing)
print(repr(shout_strict("")))
#: ''
