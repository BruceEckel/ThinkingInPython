# exercise_8.py
def source() -> list[int]:
    print("source() called")
    return [1, 2, 3]

factor = 2
built = [n * factor for n in source()]
#: source() called
print("list created")
#: list created
factor = 10
print(built)
#: [2, 4, 6]
