# eafp.py

def careful(text):
    if text.isdigit():
        return int(text)
    return None

def forgiving(text):
    try:
        return int(text)
    except ValueError:
        return None

print(careful("-5"), forgiving("-5"))
#: None -5
try:
    careful("\N{SUPERSCRIPT TWO}")
except ValueError as e:
    print("careful:", e)
#: careful: invalid literal for int() with base 10: '²'
print(forgiving("\N{SUPERSCRIPT TWO}"))
#: None
