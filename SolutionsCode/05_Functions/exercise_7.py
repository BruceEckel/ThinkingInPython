# exercise_7.py

def describe(name, /, **facts):
    print(name)
    for key, value in facts.items():
        print(f"{key}={value}")

describe("Bob", role="editor", years=12)
#: Bob
#: role=editor
#: years=12
try:
    describe(name="Bob")  # type: ignore
except TypeError as e:
    print(type(e).__name__)
#: TypeError
