# referential_transparency.py
def add(a: int, b: int) -> int:
    return a + b

x = add(2, 3) + add(2, 3)
y = 5 + 5
print(x, y, x == y)
#: 10 10 True
