# exercise_10.py
def look_first(text):
    if text.isdigit():
        return int(text)
    return None

for text in (" 42 ", "4_2"):
    print(repr(text), look_first(text), int(text))
#: ' 42 ' None 42
#: '4_2' None 42
