# exercise_7.py
from exceptions import expect

def describe(name, /, **facts):
    print(name)
    for key, value in facts.items():
        print(f"{key}={value}")

describe("Bob", role="editor", years=12)
#: Bob
#: role=editor
#: years=12
expect(TypeError, describe, name="Bob")  # type: ignore
#: [TypeError] describe() missing 1 required positional
#: argument: 'name'
