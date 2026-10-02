# exercise_3.py
from exceptions import expect

def divide(a, b, /, *, label="result"):
    return f"{label}: {a / b}"

print(divide(10, 2, label="half"))
#: half: 5.0

expect(TypeError, divide, 10, 2, "half")  # type: ignore
#: [TypeError] divide() takes 2 positional arguments but 3
#: were given
