# eafp.py

def look_first(text):
    if text.isdigit():
        return int(text)
    return None

def parse_int(text):
    try:
        return int(text)
    except ValueError:
        return None

print(look_first("-5"), parse_int("-5"))
#: None -5
try:
    look_first("\N{SUPERSCRIPT TWO}")
except ValueError as e:
    print("look_first:", e)
#: look_first: invalid literal for int() with base 10: '²'
print(parse_int("\N{SUPERSCRIPT TWO}"))
#: None
