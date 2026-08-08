# genexp_timing.py
def source() -> list[int]:
    print("source() called")
    return [1, 2, 3]

factor = 2
gen = (n * factor for n in source())
#: source() called
print("generator created")
#: generator created
factor = 10
print(list(gen))
#: [10, 20, 30]
