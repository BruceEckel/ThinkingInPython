# exercise_3.py
def divide(a, b, /, *, label="result"):
    return f"{label}: {a / b}"

print(divide(10, 2, label="half"))
#: half: 5.0

try:
    divide(10, 2, "half")  # type: ignore
except TypeError as e:
    print("TypeError:", e)
#: TypeError: divide() takes 2 positional arguments but 3 were given
